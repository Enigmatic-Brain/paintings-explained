-- Row Level Security: the browser (anon key) may READ published content only.
-- The ingestion script uses the service-role key, which BYPASSES RLS, so it can
-- still insert/update freely. Run this AFTER 001_schema.sql.

alter table artists              enable row level security;
alter table paintings            enable row level security;
alter table hotspots             enable row level security;
alter table tags                 enable row level security;
alter table painting_tags        enable row level security;
alter table collections          enable row level security;
alter table collection_paintings enable row level security;

-- Drop existing policies so this file is re-runnable
drop policy if exists "public read artists"              on artists;
drop policy if exists "public read paintings"            on paintings;
drop policy if exists "public read hotspots"             on hotspots;
drop policy if exists "public read tags"                 on tags;
drop policy if exists "public read painting_tags"        on painting_tags;
drop policy if exists "public read collections"          on collections;
drop policy if exists "public read collection_paintings" on collection_paintings;

-- Public READ policies (apply to anon + authenticated roles)
create policy "public read paintings" on paintings
  for select using (published = true);

create policy "public read artists" on artists
  for select using (true);

create policy "public read hotspots" on hotspots
  for select using (
    exists (select 1 from paintings p where p.id = hotspots.painting_id and p.published)
  );

create policy "public read tags" on tags
  for select using (true);

create policy "public read painting_tags" on painting_tags
  for select using (
    exists (select 1 from paintings p where p.id = painting_tags.painting_id and p.published)
  );

create policy "public read collections" on collections
  for select using (published = true);

create policy "public read collection_paintings" on collection_paintings
  for select using (
    exists (select 1 from collections c where c.id = collection_paintings.collection_id and c.published)
  );

-- Note: no INSERT/UPDATE/DELETE policies are defined, so anonymous/browser
-- clients cannot write. View-count increments (Phase 2) will go through a
-- SECURITY DEFINER RPC rather than a broad write policy.
