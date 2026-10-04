-- Public customer enrolment for the venue-branded join link.
-- The API uses the server-only Supabase secret key; browser roles get no access.
alter table public.members
  add column if not exists consented_at timestamptz,
  add column if not exists consent_version text;

create table if not exists public.public_join_limits (
  venue_id uuid not null references public.venues(id) on delete cascade,
  visitor_fingerprint text not null check (visitor_fingerprint ~ '^[0-9a-f]{64}$'),
  window_started_at timestamptz not null default now(),
  request_count integer not null default 0 check (request_count >= 0),
  primary key (venue_id, visitor_fingerprint)
);

alter table public.public_join_limits enable row level security;
revoke all on table public.public_join_limits from anon, authenticated;
grant all on table public.public_join_limits to service_role;

create or replace function public.consume_public_join_attempt(
  p_venue_id uuid,
  p_fingerprint text,
  p_limit integer default 5,
  p_window_seconds integer default 600
)
returns boolean
language plpgsql
security definer
set search_path = public
as $$
declare v_count integer;
begin
  if p_fingerprint !~ '^[0-9a-f]{64}$' or p_limit < 1 or p_limit > 20 or p_window_seconds < 60 or p_window_seconds > 3600 then
    raise exception 'Invalid rate limit request';
  end if;
  delete from public.public_join_limits where venue_id = p_venue_id and window_started_at < now() - interval '24 hours';
  insert into public.public_join_limits(venue_id, visitor_fingerprint, window_started_at, request_count)
  values (p_venue_id, p_fingerprint, now(), 1)
  on conflict (venue_id, visitor_fingerprint) do update
    set request_count = case
          when public.public_join_limits.window_started_at < now() - make_interval(secs => p_window_seconds) then 1
          else public.public_join_limits.request_count + 1
        end,
        window_started_at = case
          when public.public_join_limits.window_started_at < now() - make_interval(secs => p_window_seconds) then now()
          else public.public_join_limits.window_started_at
        end
  returning request_count into v_count;
  return v_count <= p_limit;
end;
$$;
revoke all on function public.consume_public_join_attempt(uuid, text, integer, integer) from public, anon, authenticated;
grant execute on function public.consume_public_join_attempt(uuid, text, integer, integer) to service_role;

-- Keep the table bounded. A daily scheduled cleanup can be added after launch.
create index if not exists public_join_limits_window_idx on public.public_join_limits(window_started_at);
