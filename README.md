# Paintings Explained

A website that showcases famous **public-domain paintings** and the **hidden
details** inside them — zoom in, tap the markers, and discover why people stare
at these masterpieces for hours.

- **Content** lives in a **Supabase (Postgres)** database.
- A **Python script** pulls public-domain art (CC0) from the **Met** and **Art
  Institute of Chicago** APIs into the database.
- The **website** (Astro) reads from the database and updates near-instantly.
- Hosting is **free** (Vercel).

```
paintings-explained/
├── db/migrations/     SQL to set up the database (run once in Supabase)
├── ingest/            Python script that imports paintings from museum APIs
└── web/               The Astro website
```

---

## One-time setup

### 1. Create the database (Supabase — free)

1. Go to <https://supabase.com> → **New project**. Pick a name and a strong
   database password. Wait ~2 minutes for it to provision.
2. Open **SQL Editor** (left sidebar) → **New query**.
3. Paste the contents of [`db/migrations/001_schema.sql`](db/migrations/001_schema.sql),
   click **Run**. Then do the same with
   [`db/migrations/002_rls.sql`](db/migrations/002_rls.sql).
4. Open **Project Settings → API** and copy three things:
   - **Project URL**
   - **anon public** key (safe for the website)
   - **service_role** key (secret — only for the import script)

### 2. Import the starter paintings (Python)

```bash
cd ingest
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
cp .env.example .env          # then paste your Project URL + service_role key
./.venv/bin/python ingest.py  # imports ~9 public-domain paintings
```

Re-running is safe — it updates existing rows instead of duplicating them.
Use `python ingest.py --dry-run` to preview without writing.

### 3. Run the website locally

```bash
cd web
npm install
cp .env.example .env           # paste your Project URL + anon key
npm run dev                    # open http://localhost:4321
```

### 4. Deploy free (Vercel)

1. Push this folder to a GitHub repo.
2. Go to <https://vercel.com> → **Add New Project** → import the repo.
3. Set **Root Directory** to `web`.
4. Add Environment Variables: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, and
   `SITE_URL` (your `*.vercel.app` URL, editable later).
5. Deploy. Done — you have a live URL.

---

## Adding & editing paintings (no code)

Two ways, use either:

- **Bulk:** add a new entry to `ingest/seed_data.py` (copy an existing block,
  change the `query`/`artist_match`/text) and re-run the import script.
- **By hand:** in Supabase, open **Table Editor → paintings** and add or edit a
  row. To make it appear on the site, set **`published` = true**. Add rows in
  **hotspots** (with the `painting_id`) to place the clickable markers — `x` and
  `y` are percentages across/down the image (0–100).

Tips:
- `featured = true` shows a painting on the home page.
- `summary` is the one-line hook; `why_watch` is the "stare for hours"
  paragraph; `body` is the full explanation (supports Markdown).
- Only **public-domain (CC0)** works should be added — the import script
  enforces this automatically.

---

## How the pieces fit

| Piece | Tech | Notes |
|-------|------|-------|
| Database | Supabase Postgres | Source of truth; Row Level Security = public can only read published rows |
| Import | Python (`requests`, `supabase`) | Resolves works by search, verifies CC0, upserts |
| Website | Astro (SSR) + OpenSeadragon | Deep zoom + hidden-detail hotspots; CDN-cached |
| Hosting | Vercel (free) | Auto-redeploys on every Git push |

See [`db/`](db/), [`ingest/`](ingest/), and [`web/`](web/) for details.
