import type { APIRoute } from 'astro';

type RiskDecision = 'allow' | 'review' | 'block';

const API_BASE_BY_REGION: Record<string, string> = {
  us: 'https://api.fpjs.io/v4',
  eu: 'https://eu.api.fpjs.io/v4',
  ap: 'https://ap.api.fpjs.io/v4',
};

function resolveApiBase(): string {
  const explicit = import.meta.env.FINGERPRINT_SERVER_API_BASE_URL?.trim();
  if (explicit) return explicit.replace(/\/$/, '');
  const region = (import.meta.env.PUBLIC_FINGERPRINT_REGION || 'us').toLowerCase();
  return API_BASE_BY_REGION[region] || API_BASE_BY_REGION.us;
}

function asNumber(value: unknown): number | null {
  if (typeof value === 'number' && Number.isFinite(value)) return value;
  if (
    value &&
    typeof value === 'object' &&
    'score' in value &&
    typeof (value as { score?: unknown }).score === 'number'
  ) {
    return (value as { score: number }).score;
  }
  return null;
}

function asBoolean(value: unknown): boolean | null {
  if (typeof value === 'boolean') return value;
  return null;
}

function evaluateRisk(event: Record<string, unknown>) {
  const reasons: string[] = [];
  let decision: RiskDecision = 'allow';

  const bot = String(event.bot || '').toLowerCase();
  const suspectScore = asNumber(event.suspect_score);
  const tampering = asBoolean(event.tampering);
  const tamperingConfidence = String(event.tampering_confidence || '').toLowerCase();
  const proxy = asBoolean(event.proxy);
  const proxyConfidence = String(event.proxy_confidence || '').toLowerCase();
  const vpn = asBoolean(event.vpn);
  const incognito = asBoolean(event.incognito);
  const ipBlocklist =
    event.ip_blocklist && typeof event.ip_blocklist === 'object'
      ? (event.ip_blocklist as Record<string, unknown>)
      : null;
  const attackSource = asBoolean(ipBlocklist?.attack_source);
  const torNode = asBoolean(ipBlocklist?.tor_node);

  if (bot === 'bad') {
    decision = 'block';
    reasons.push('bot_detected');
  }

  if ((attackSource || torNode) && decision !== 'block') {
    decision = 'block';
    reasons.push('ip_blocklist');
  }

  if (tampering === true && ['medium', 'high'].includes(tamperingConfidence) && decision !== 'block') {
    decision = 'block';
    reasons.push('tampering_high_confidence');
  }

  if (suspectScore !== null && suspectScore >= 90 && decision !== 'block') {
    decision = 'block';
    reasons.push('suspect_score_high');
  } else if (suspectScore !== null && suspectScore >= 70 && decision === 'allow') {
    decision = 'review';
    reasons.push('suspect_score_elevated');
  }

  if (proxy === true && proxyConfidence === 'high' && decision === 'allow') {
    decision = 'review';
    reasons.push('high_confidence_proxy');
  }

  if (vpn === true && decision === 'allow') {
    decision = 'review';
    reasons.push('vpn_detected');
  }

  if (incognito === true && decision === 'allow') {
    decision = 'review';
    reasons.push('incognito_mode');
  }

  return {
    decision,
    reasons,
    summary: {
      bot: bot || null,
      suspectScore,
      tampering,
      proxy,
      vpn,
      incognito,
      attackSource,
      torNode,
    },
  };
}

export const POST: APIRoute = async ({ request }) => {
  try {
    const secretKey = import.meta.env.FINGERPRINT_SECRET_API_KEY;
    if (!secretKey) {
      return new Response(
        JSON.stringify({
          decision: 'allow',
          reasons: ['missing_server_api_key'],
          summary: null,
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } },
      );
    }

    const body = (await request.json()) as { requestId?: string };
    const requestId = (body.requestId || '').trim();
    if (!requestId) {
      return new Response(JSON.stringify({ error: 'requestId is required' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    const apiBase = resolveApiBase();
    const apiResponse = await fetch(`${apiBase}/events/${encodeURIComponent(requestId)}`, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${secretKey}`,
        Accept: 'application/json',
      },
    });

    if (!apiResponse.ok) {
      const text = await apiResponse.text();
      return new Response(
        JSON.stringify({
          error: 'fingerprint_server_api_error',
          status: apiResponse.status,
          detail: text.slice(0, 400),
        }),
        { status: 502, headers: { 'Content-Type': 'application/json' } },
      );
    }

    const event = (await apiResponse.json()) as Record<string, unknown>;
    const evaluation = evaluateRisk(event);
    return new Response(
      JSON.stringify({
        ...evaluation,
        eventId: event.event_id || requestId,
      }),
      { status: 200, headers: { 'Content-Type': 'application/json' } },
    );
  } catch (error) {
    return new Response(
      JSON.stringify({
        error: 'fingerprint_risk_evaluation_failed',
        detail: error instanceof Error ? error.message : 'unknown',
      }),
      { status: 500, headers: { 'Content-Type': 'application/json' } },
    );
  }
};
