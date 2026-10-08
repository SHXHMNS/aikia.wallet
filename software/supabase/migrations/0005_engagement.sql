-- Engagement: venue locations (geofenced lock-screen / nearby alerts), current offer, and automated campaigns.

alter table public.venues add column if not exists current_offer text check (current_offer is null or char_length(current_offer) <= 200);

create table if not exists public.venue_locations (
  id uuid primary key default gen_random_uuid(),
  venue_id uuid not null references public.venues(id) on delete cascade,
  label text not null check (char_length(label) between 1 and 60),
  lat double precision not null check (lat between -90 and 90),
  lng double precision not null check (lng between -180 and 180),
  lock_screen_message text check (lock_screen_message is null or char_length(lock_screen_message) <= 120),
  created_at timestamptz not null default now()
);
create index if not exists venue_locations_venue_idx on public.venue_locations(venue_id);

create table if not exists public.campaigns (
  id uuid primary key default gen_random_uuid(),
  venue_id uuid not null references public.venues(id) on delete cascade,
  name text not null check (char_length(name) between 1 and 60),
  kind text not null check (kind in ('broadcast', 'daily', 'weather_rain', 'weather_hot', 'winback')),
  header text not null check (char_length(header) between 1 and 60),
  body text not null check (char_length(body) between 1 and 300),
  weekdays integer[] not null default '{0,1,2,3,4,5,6}',
  winback_days integer not null default 14 check (winback_days between 3 and 365),
  active boolean not null default true,
  last_sent_at timestamptz,
  created_at timestamptz not null default now()
);
create index if not exists campaigns_venue_idx on public.campaigns(venue_id);

create table if not exists public.campaign_sends (
  id uuid primary key default gen_random_uuid(),
  campaign_id uuid references public.campaigns(id) on delete set null,
  venue_id uuid not null references public.venues(id) on delete cascade,
  trigger text not null check (trigger in ('manual', 'scheduled')),
  audience integer not null default 0,
  status text not null check (status in ('sent', 'skipped', 'failed')),
  detail text,
  sent_at timestamptz not null default now()
);
create index if not exists campaign_sends_venue_idx on public.campaign_sends(venue_id, sent_at desc);

alter table public.venue_locations enable row level security;
alter table public.campaigns enable row level security;
alter table public.campaign_sends enable row level security;

create policy venue_locations_read on public.venue_locations for select to authenticated using (public.has_venue_role(venue_id, array['owner','admin']));
create policy venue_locations_manage on public.venue_locations for all to authenticated using (public.has_venue_role(venue_id, array['owner','admin'])) with check (public.has_venue_role(venue_id, array['owner','admin']));
create policy campaigns_read on public.campaigns for select to authenticated using (public.has_venue_role(venue_id, array['owner','admin']));
create policy campaigns_manage on public.campaigns for all to authenticated using (public.has_venue_role(venue_id, array['owner','admin'])) with check (public.has_venue_role(venue_id, array['owner','admin']));
create policy campaign_sends_read on public.campaign_sends for select to authenticated using (public.has_venue_role(venue_id, array['owner','admin']));
