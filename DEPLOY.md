# Deploying Paintings Explained (free, on Vercel)

You'll run these in **your own Terminal** (Node is already installed and on your
PATH). Two paths — **A is the fastest**. Either gives a free public URL.

Content updates (adding/editing paintings in Supabase) never need a redeploy —
only *code* changes do.

---

## Path A — Vercel CLI (fastest, no GitHub needed)

Open Terminal and run:

```bash
cd ~/Documents/paintings-explained/web
npm install -g vercel        # installs the Vercel command
vercel login                 # pick "Continue with Email/GitHub", confirm in browser
vercel                       # first run: answer the prompts (see below), then it deploys
```

When `vercel` asks:
- *Set up and deploy?* → **Y**
- *Which scope?* → your account
- *Link to existing project?* → **N**
- *Project name?* → press Enter (or type `paintings-explained`)
- *In which directory is your code located?* → **`./`** (you're already in `web/`)
- It auto-detects **Astro** — accept the defaults.

Then add your two environment variables (the site reads the database with these):

```bash
vercel env add SUPABASE_URL            # paste your https://...supabase.co URL, choose Production
vercel env add SUPABASE_ANON_KEY       # paste your anon key, choose Production
```

Deploy to production:

```bash
vercel --prod
```

It prints your live URL (e.g. `https://paintings-explained.vercel.app`). Done! 🎉

> Tip: set `SITE_URL` too (`vercel env add SITE_URL`) to your live URL, so share
> cards and the sitemap use the right address. Then run `vercel --prod` again.

---

## Path B — GitHub + Vercel dashboard (auto-redeploys on every code change)

1. Create an empty repo on <https://github.com/new> (e.g. `paintings-explained`).
2. In Terminal:
   ```bash
   cd ~/Documents/paintings-explained
   git branch -M main
   git remote add origin https://github.com/<you>/paintings-explained.git
   git push -u origin main
   ```
3. Go to <https://vercel.com> → **Add New… → Project** → import the repo.
4. **Root Directory:** set to **`web`**.
5. **Environment Variables:** add `SUPABASE_URL`, `SUPABASE_ANON_KEY`, and
   `SITE_URL` (your future `*.vercel.app` URL).
6. **Deploy.** Every future `git push` auto-redeploys.

---

## After deploying

- **Custom domain (optional):** Vercel → Project → Settings → Domains. Then set
  `SITE_URL` to it and redeploy.
- **Add paintings:** Supabase **Table Editor → paintings** (set `published = true`),
  or add to `ingest/seed_data.py` and re-run the importer. No redeploy needed.
- **Newsletter:** set `NEWSLETTER_ACTION` env var to your provider's form URL
  (e.g. Buttondown) to make the signup live.
