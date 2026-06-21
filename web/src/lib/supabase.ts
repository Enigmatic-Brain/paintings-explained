import { createClient } from '@supabase/supabase-js';

const url = import.meta.env.SUPABASE_URL;
const anonKey = import.meta.env.SUPABASE_ANON_KEY;

if (!url || !anonKey) {
  // Fail loudly in dev so a missing .env is obvious rather than mysterious.
  throw new Error(
    'Missing SUPABASE_URL / SUPABASE_ANON_KEY. Copy web/.env.example to web/.env and fill them in.',
  );
}

// Read-only, server-side client. The anon key + RLS (public read of published
// rows) means this can never write or read unpublished content.
export const supabase = createClient(url, anonKey, {
  auth: { persistSession: false, autoRefreshToken: false },
});
