#!/usr/bin/env python3
"""Ingest curated public-domain paintings into Supabase.

Resolves each seed against the live Met / Art Institute APIs (by search),
verifies the work is public domain + has an image, then upserts paintings,
artists, hotspots and tags. Idempotent: safe to re-run.

Usage:
    python ingest.py            # import everything in seed_data.SEEDS
    python ingest.py --dry-run  # resolve + print, but write nothing

Env (see .env.example):
    SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
"""
from __future__ import annotations

import os
import re
import sys
import time
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

from seed_data import SEEDS

MET_BASE = "https://collectionapi.metmuseum.org/public/collection/v1"
AIC_BASE = "https://api.artic.edu/api/v1"
AIC_IIIF = "https://www.artic.edu/iiif/2"
WIKI_API = "https://commons.wikimedia.org/w/api.php"

# Display/zoom widths sourced from Wikimedia Commons (hotlink-friendly CDN).
# NOTE: very large "Google Art Project" scans only render at fixed bucket sizes,
# so we always use the exact thumb URL the API returns for a requested width
# (never rewrite the width ourselves).
WIKI_DISPLAY_W = 1600   # inline image on the page + share card
WIKI_ZOOM_W = 4096      # high-res single image for the deep-zoom viewer
WIKI_THUMB_W = 600      # gallery card

HTTP = requests.Session()
HTTP.headers.update({"User-Agent": "paintings-explained-ingest/1.0 (contact: site owner)"})


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def slugify(text: str) -> str:
    text = (text or "").lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "untitled"


def first_year(*values) -> int | None:
    for v in values:
        if v is None:
            continue
        m = re.search(r"\b(\d{3,4})\b", str(v))
        if m:
            return int(m.group(1))
    return None


def get_json(url: str, **kwargs) -> dict:
    for attempt in range(5):
        try:
            r = HTTP.get(url, timeout=30, **kwargs)
            if r.status_code == 429:  # rate limited — back off harder
                raise requests.HTTPError("429 Too Many Requests")
            r.raise_for_status()
            return r.json()
        except Exception as exc:  # noqa: BLE001
            if attempt == 4:
                raise
            wait = 3 * (attempt + 1)
            time.sleep(wait)
            print(f"    retry in {wait}s ({exc})")
    return {}


def wiki_get(params: dict) -> dict:
    """Throttled Wikimedia API call (unauthenticated clients are rate-limited)."""
    time.sleep(1.0)
    return get_json(WIKI_API, params=params)


# --------------------------------------------------------------------------- #
# museum resolvers -> normalized dict
# --------------------------------------------------------------------------- #
def resolve_met(query: str, artist_match: str) -> dict | None:
    data = get_json(f"{MET_BASE}/search", params={"q": query, "hasImages": "true"})
    for oid in (data.get("objectIDs") or [])[:30]:
        obj = get_json(f"{MET_BASE}/objects/{oid}")
        if not obj.get("isPublicDomain") or not obj.get("primaryImage"):
            continue
        if artist_match.lower() not in (obj.get("artistDisplayName") or "").lower():
            continue
        return {
            "title": obj.get("title") or query,
            "artist_name": obj.get("artistDisplayName") or "Unknown artist",
            "year": obj.get("objectDate"),
            "year_sort": first_year(obj.get("objectBeginDate"), obj.get("objectDate")),
            "museum": obj.get("repository") or "The Metropolitan Museum of Art",
            "medium": obj.get("medium"),
            "image_url": obj.get("primaryImage"),
            "iiif_url": None,  # Met serves a single high-res JPEG (OpenSeadragon "image" mode)
            "thumb_url": obj.get("primaryImageSmall") or obj.get("primaryImage"),
            "width": None,
            "height": None,
            "object_id": str(obj.get("objectID")),
            "credit": obj.get("creditLine"),
        }
    return None


def resolve_artic(query: str, artist_match: str) -> dict | None:
    fields = ",".join([
        "id", "title", "artist_title", "date_display", "date_start",
        "medium_display", "is_public_domain", "image_id", "credit_line", "thumbnail",
    ])
    data = get_json(f"{AIC_BASE}/artworks/search", params={"q": query, "fields": fields, "limit": 30})
    for art in data.get("data", []):
        if not art.get("is_public_domain") or not art.get("image_id"):
            continue
        if artist_match.lower() not in (art.get("artist_title") or "").lower():
            continue
        image_id = art["image_id"]
        thumb = art.get("thumbnail") or {}
        return {
            "title": art.get("title") or query,
            "artist_name": art.get("artist_title") or "Unknown artist",
            "year": art.get("date_display"),
            "year_sort": first_year(art.get("date_start"), art.get("date_display")),
            "museum": "Art Institute of Chicago",
            "medium": art.get("medium_display"),
            "image_url": f"{AIC_IIIF}/{image_id}/full/1686,/0/default.jpg",
            "iiif_url": f"{AIC_IIIF}/{image_id}/info.json",  # tiled deep zoom
            "thumb_url": f"{AIC_IIIF}/{image_id}/full/600,/0/default.jpg",
            "width": thumb.get("width"),
            "height": thumb.get("height"),
            "object_id": str(art["id"]),
            "credit": art.get("credit_line"),
        }
    return None


RESOLVERS = {"met": resolve_met, "artic": resolve_artic}


def wiki_thumburl(title: str, width: int) -> str | None:
    """Ask the API for a renderable thumb of `title` at (about) `width`.

    For large images MediaWiki clamps to the nearest renderable bucket and
    returns that URL — which is guaranteed to render (unlike an arbitrary width).
    """
    params = {
        "action": "query", "format": "json", "titles": title,
        "prop": "imageinfo", "iiprop": "url|size", "iiurlwidth": str(width),
    }
    data = wiki_get(params)
    pages = list(((data.get("query") or {}).get("pages") or {}).values())
    if not pages:
        return None
    ii = (pages[0].get("imageinfo") or [None])[0]
    if not ii:
        return None
    return ii.get("thumburl") or ii.get("url")


def resolve_wikimedia(query: str) -> dict | None:
    """Find a high-res public-domain scan on Wikimedia Commons.

    Wikimedia's image CDN (upload.wikimedia.org) is hotlink-friendly and not
    behind a bot challenge, unlike the Art Institute's IIIF endpoint.
    """
    params = {
        "action": "query", "format": "json", "generator": "search",
        "gsrnamespace": "6", "gsrlimit": "5", "gsrsearch": query,
        "prop": "imageinfo", "iiprop": "url|size",
    }
    data = wiki_get(params)
    pages = list(((data.get("query") or {}).get("pages") or {}).values())
    pages.sort(key=lambda p: p.get("index", 99))  # keep search relevance order
    for p in pages:
        ii = (p.get("imageinfo") or [None])[0]
        if not ii:
            continue
        title = p.get("title", "")
        display = wiki_thumburl(title, WIKI_DISPLAY_W)
        if not display:
            continue
        return {
            "title": title,
            "display": display,
            "zoom": wiki_thumburl(title, WIKI_ZOOM_W) or display,
            "thumb": wiki_thumburl(title, WIKI_THUMB_W) or display,
            "width": ii.get("width"),
            "height": ii.get("height"),
        }
    return None


# --------------------------------------------------------------------------- #
# Supabase writes
# --------------------------------------------------------------------------- #
def upsert_artist(sb, name: str) -> str:
    slug = slugify(name)
    sb.table("artists").upsert({"slug": slug, "name": name}, on_conflict="slug").execute()
    return sb.table("artists").select("id").eq("slug", slug).single().execute().data["id"]


def upsert_tag(sb, slug: str) -> str:
    slug = slugify(slug)
    name = slug.replace("-", " ").title()
    sb.table("tags").upsert({"slug": slug, "name": name}, on_conflict="slug").execute()
    return sb.table("tags").select("id").eq("slug", slug).single().execute().data["id"]


def import_seed(sb, seed: dict, dry_run: bool) -> bool:
    resolver = RESOLVERS[seed["source"]]
    print(f"  resolving {seed['source']}: '{seed['query']}' …")
    norm = resolver(seed["query"], seed["artist_match"])
    if not norm:
        print(f"  ✗ SKIPPED — no public-domain match for '{seed['query']}'")
        return False
    print(f"  ✓ matched: {norm['title']} — {norm['artist_name']} ({norm['year']})")

    # Prefer a Wikimedia Commons scan for the image (reliable hotlinking +
    # huge resolution for deep zoom). Keep the museum's authoritative metadata.
    wiki_query = seed.get("wikimedia") or f"{norm['title']} {seed['artist_match']}"
    wiki = resolve_wikimedia(wiki_query)
    if wiki:
        norm["image_url"] = wiki["display"]
        norm["thumb_url"] = wiki["thumb"]
        norm["iiif_url"] = wiki["zoom"]  # high-res single image for OpenSeadragon
        norm["width"] = wiki["width"]
        norm["height"] = wiki["height"]
        norm["credit"] = ((norm.get("credit") or "").strip()
                          + " · image via Wikimedia Commons").lstrip(" ·")
        print(f"    image ← Wikimedia: {wiki['title']} ({wiki['width']}×{wiki['height']})")
    else:
        print("    image ← museum (no Wikimedia match)")

    if dry_run:
        return True

    artist_id = upsert_artist(sb, norm["artist_name"])
    row = {
        "slug": seed["slug"],
        "title": norm["title"],
        "artist_id": artist_id,
        "year": norm["year"],
        "year_sort": norm["year_sort"],
        "movement": seed.get("movement"),
        "museum": norm["museum"],
        "medium": norm["medium"],
        "image_url": norm["image_url"],
        "iiif_url": norm["iiif_url"],
        "thumb_url": norm["thumb_url"],
        "width": norm["width"],
        "height": norm["height"],
        "source": seed["source"],
        "object_id": norm["object_id"],
        "license": "CC0",
        "credit": norm["credit"],
        "summary": seed.get("summary"),
        "why_watch": seed.get("why_watch"),
        "body": seed.get("body"),
        "featured": seed.get("featured", False),
        "published": True,
        "published_at": datetime.now(timezone.utc).isoformat(),
    }
    sb.table("paintings").upsert(row, on_conflict="source,object_id").execute()
    pid = (
        sb.table("paintings").select("id")
        .eq("source", seed["source"]).eq("object_id", norm["object_id"])
        .single().execute().data["id"]
    )

    # hotspots — replace wholesale so re-runs stay clean
    sb.table("hotspots").delete().eq("painting_id", pid).execute()
    for i, h in enumerate(seed.get("hotspots", [])):
        sb.table("hotspots").insert({
            "painting_id": pid, "x": h["x"], "y": h["y"],
            "title": h["title"], "detail": h["detail"], "ordinal": i,
        }).execute()

    # tags
    for tag_slug in seed.get("tags", []):
        tid = upsert_tag(sb, tag_slug)
        sb.table("painting_tags").upsert(
            {"painting_id": pid, "tag_id": tid}, on_conflict="painting_id,tag_id"
        ).execute()

    print(f"  → saved as /paintings/{seed['slug']} "
          f"({len(seed.get('hotspots', []))} hotspots, {len(seed.get('tags', []))} tags)")
    return True


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    load_dotenv()

    sb = None
    if not dry_run:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        if not url or not key:
            print("ERROR: set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env "
                  "(copy .env.example). Or run with --dry-run.")
            return 1
        from supabase import create_client
        sb = create_client(url, key)

    print(f"Ingesting {len(SEEDS)} seed paintings"
          f"{' (DRY RUN — no writes)' if dry_run else ''}\n")
    ok = 0
    for seed in SEEDS:
        try:
            if import_seed(sb, seed, dry_run):
                ok += 1
        except Exception as exc:  # noqa: BLE001
            print(f"  ✗ ERROR on '{seed['query']}': {exc}")
        print()

    print(f"Done: {ok}/{len(SEEDS)} imported.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
