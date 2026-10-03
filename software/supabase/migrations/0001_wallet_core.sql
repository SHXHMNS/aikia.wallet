create extension if not exists pgcrypto;

create table public.venues (
  id uuid primary key default gen_random_uuid(),
  name text not null check (char_length(name) between 2 and 80),
  slug text not null unique check (slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
  business_type text not null default 'cafe' check (business_type in ('cafe','restaurant','retail','salon','fitness','hotel','entertainment','other')),
  action_label text not null default 'coffee purchase' check (char_length(action_label) between 2 and 24),
  balance_label text not null default 'STAMPS' check (char_length(balance_label) between 2 and 9),
  reward_target integer not null default 9 check (reward_target between 1 and 1000),
  reward_name text not null default 'Free coffee' check (char_length(reward_name) between 1 and 80),
  brand_color text not null default '#171421' check (brand_color ~ '^#[0-9A-Fa-f]{6}$'),
  background_color text check (background_color is null or background_color ~ '^#[0-9A-Fa-f]{6}$'),
  program_logo_url text,
  hero_image_url text,
  created_at timestamptz not null default now()
);

create table public.venue_team_members (
  venue_id uuid not null references public.venues(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  role text not null check (role in ('owner', 'admin', 'staff')),
  created_at timestamptz not null default now(),
  primary key (venue_id, user_id)
);

create table public.venue_tiers (
  id uuid primary key default gen_random_uuid(),
  venue_id uuid not null references public.venues(id) on delete cascade,
  rank integer not null check (rank >= 0),
  name text not null check (char_length(name) between 1 and 32),
  min_lifetime_actions integer not null check (min_lifetime_actions >= 0),
  benefits jsonb not null default '[]'::jsonb check (jsonb_typeof(benefits) = 'array'),
  accent_color text not null default '#171421' check (accent_color ~ '^#[0-9A-Fa-f]{6}$'),
  created_at timestamptz not null default now(),
  unique (venue_id, rank),
  unique (venue_id, name),
  unique (venue_id, min_lifetime_actions),
  unique (venue_id, id)
);

create table public.members (
  id uuid primary key default gen_random_uuid(),
  venue_id uuid not null references public.venues(id) on delete cascade,
  full_name text not null check (char_length(full_name) between 1 and 120),
  public_code text not null,
  scan_token text not null unique default encode(gen_random_bytes(24), 'hex'),
  stamp_balance integer not null default 0 check (stamp_balance >= 0),
  rewards_available integer not null default 0 check (rewards_available >= 0),
  lifetime_actions integer not null default 0 check (lifetime_actions >= 0),
  current_tier_id uuid,
  status text not null default 'active' check (status in ('active', 'suspended')),
  created_at timestamptz not null default now(),
  unique (venue_id, public_code),
  unique (venue_id, id),
  foreign key (venue_id, current_tier_id) references public.venue_tiers(venue_id, id) deferrable initially deferred
);

create table public.ledger_transactions (
  id uuid primary key default gen_random_uuid(),
  venue_id uuid not null references public.venues(id) on delete cascade,
  member_id uuid not null,
  actor_user_id uuid references auth.users(id),
  event_type text not null check (event_type in ('qualifying_action', 'redemption', 'adjustment')),
  action_units integer not null default 0 check (action_units >= 0),
  stamp_delta integer not null,
  rewards_delta integer not null default 0,
  idempotency_key text not null check (char_length(idempotency_key) between 8 and 120),
  note text,
  created_at timestamptz not null default now(),
  unique (venue_id, idempotency_key),
  foreign key (venue_id, member_id) references public.members(venue_id, id) on delete cascade
);

create table public.wallet_passes (
  member_id uuid primary key,
  venue_id uuid not null references public.venues(id) on delete cascade,
  provider text not null check (provider in ('google', 'apple')),
  provider_class_id text not null,
  provider_object_id text not null unique,
  last_synced_at timestamptz,
  sync_error text,
  updated_at timestamptz not null default now(),
  foreign key (venue_id, member_id) references public.members(venue_id, id) on delete cascade
);

create index ledger_member_created_idx on public.ledger_transactions(member_id, created_at desc);
create index members_venue_created_idx on public.members(venue_id, created_at desc);
create index team_user_idx on public.venue_team_members(user_id, venue_id);

create function public.has_venue_role(p_venue_id uuid, p_roles text[] default array['owner','admin','staff'])
returns boolean language sql stable security definer set search_path = public, auth as $$
  select exists (
    select 1 from public.venue_team_members tm
    where tm.venue_id = p_venue_id and tm.user_id = auth.uid() and tm.role = any(p_roles)
  );
$$;
revoke all on function public.has_venue_role(uuid, text[]) from public;
grant execute on function public.has_venue_role(uuid, text[]) to authenticated;

alter table public.venues enable row level security;
alter table public.venue_team_members enable row level security;
alter table public.venue_tiers enable row level security;
alter table public.members enable row level security;
alter table public.ledger_transactions enable row level security;
alter table public.wallet_passes enable row level security;

create policy venue_read on public.venues for select to authenticated using (public.has_venue_role(id));
create policy venue_update on public.venues for update to authenticated using (public.has_venue_role(id, array['owner','admin'])) with check (public.has_venue_role(id, array['owner','admin']));
create policy team_read on public.venue_team_members for select to authenticated using (user_id = auth.uid() or public.has_venue_role(venue_id, array['owner','admin']));
create policy tier_read on public.venue_tiers for select to authenticated using (public.has_venue_role(venue_id));
create policy tier_manage on public.venue_tiers for all to authenticated using (public.has_venue_role(venue_id, array['owner','admin'])) with check (public.has_venue_role(venue_id, array['owner','admin']));
create policy member_read on public.members for select to authenticated using (public.has_venue_role(venue_id, array['owner','admin']));
create policy ledger_read on public.ledger_transactions for select to authenticated using (public.has_venue_role(venue_id, array['owner','admin']));
create policy pass_read on public.wallet_passes for select to authenticated using (public.has_venue_role(venue_id, array['owner','admin']));

create function public.create_venue(p_name text, p_slug text)
returns uuid language plpgsql security definer set search_path = public, auth as $$
declare v_id uuid;
begin
  if auth.uid() is null then raise exception 'Authentication required'; end if;
  insert into public.venues(name, slug) values (trim(p_name), lower(trim(p_slug))) returning id into v_id;
  insert into public.venue_team_members(venue_id, user_id, role) values (v_id, auth.uid(), 'owner');
  insert into public.venue_tiers(venue_id, rank, name, min_lifetime_actions, benefits, accent_color) values
    (v_id, 0, 'Ink', 0, '["Collect a stamp with every coffee"]', '#171421'),
    (v_id, 1, 'Chrome', 15, '["A complimentary size upgrade", "Members-only seasonal menu"]', '#A98BFF'),
    (v_id, 2, 'Pink', 40, '["A complimentary coffee", "First access to new drinks", "Invitations to member events"]', '#FF3D9A');
  return v_id;
end;
$$;
revoke all on function public.create_venue(text, text) from public;
grant execute on function public.create_venue(text, text) to authenticated;

create function public.replace_venue_tiers(p_venue_id uuid, p_tiers jsonb)
returns void language plpgsql security definer set search_path = public, auth as $$
begin
  if not public.has_venue_role(p_venue_id, array['owner','admin']) then raise exception 'Venue admin access required'; end if;
  if jsonb_typeof(p_tiers) <> 'array' or jsonb_array_length(p_tiers) < 1 or jsonb_array_length(p_tiers) > 8 then
    raise exception 'Provide between one and eight tiers';
  end if;
  if (select count(*) from jsonb_array_elements(p_tiers) t where coalesce((t->>'min_lifetime_actions')::integer, -1) = 0) <> 1 then
    raise exception 'Exactly one entry tier must start at zero';
  end if;
  delete from public.venue_tiers where venue_id = p_venue_id;
  insert into public.venue_tiers(venue_id, rank, name, min_lifetime_actions, benefits, accent_color)
  select p_venue_id, (t->>'rank')::integer, trim(t->>'name'), (t->>'min_lifetime_actions')::integer,
         coalesce(t->'benefits', '[]'::jsonb), coalesce(t->>'accent_color', '#171421')
  from jsonb_array_elements(p_tiers) t;
  update public.members m set current_tier_id = (
    select vt.id from public.venue_tiers vt where vt.venue_id = p_venue_id and vt.min_lifetime_actions <= m.lifetime_actions
    order by vt.min_lifetime_actions desc limit 1
  ) where m.venue_id = p_venue_id;
end;
$$;
revoke all on function public.replace_venue_tiers(uuid, jsonb) from public;
grant execute on function public.replace_venue_tiers(uuid, jsonb) to authenticated;

create function public.record_qualifying_action(p_member_id uuid, p_action_units integer, p_idempotency_key text, p_note text default null)
returns jsonb language plpgsql security definer set search_path = public, auth as $$
declare m public.members%rowtype; v_tier public.venue_tiers%rowtype; v_existing public.ledger_transactions%rowtype;
        v_target integer; v_new_rewards integer; v_new_balance integer;
begin
  if p_action_units < 1 or p_action_units > 100 then raise exception 'Action units must be between 1 and 100'; end if;
  select * into m from public.members where id = p_member_id for update;
  if not found then raise exception 'Member not found'; end if;
  if not public.has_venue_role(m.venue_id, array['owner','admin','staff']) then raise exception 'Venue staff access required'; end if;
  select * into v_existing from public.ledger_transactions where venue_id = m.venue_id and idempotency_key = p_idempotency_key;
  if found then
    if v_existing.member_id <> p_member_id then raise exception 'This idempotency key belongs to another member'; end if;
    select * into v_tier from public.venue_tiers where id = m.current_tier_id;
    return jsonb_build_object('member_id', m.id, 'stamp_balance', m.stamp_balance, 'rewards_available', m.rewards_available, 'lifetime_actions', m.lifetime_actions, 'tier_id', m.current_tier_id, 'tier_name', v_tier.name, 'duplicate', true);
  end if;
  if m.status <> 'active' then raise exception 'Member is not active'; end if;
  select reward_target into v_target from public.venues where id = m.venue_id;
  v_new_rewards := (m.stamp_balance + p_action_units) / v_target;
  v_new_balance := (m.stamp_balance + p_action_units) % v_target;
  insert into public.ledger_transactions(venue_id, member_id, actor_user_id, event_type, action_units, stamp_delta, rewards_delta, idempotency_key, note)
  values (m.venue_id, m.id, auth.uid(), 'qualifying_action', p_action_units, p_action_units, v_new_rewards, p_idempotency_key, p_note);
  update public.members set stamp_balance = v_new_balance, rewards_available = rewards_available + v_new_rewards,
    lifetime_actions = lifetime_actions + p_action_units where id = m.id returning * into m;
  select * into v_tier from public.venue_tiers where venue_id = m.venue_id and min_lifetime_actions <= m.lifetime_actions order by min_lifetime_actions desc limit 1;
  update public.members set current_tier_id = v_tier.id where id = m.id;
  return jsonb_build_object('member_id', m.id, 'stamp_balance', m.stamp_balance, 'rewards_available', m.rewards_available, 'lifetime_actions', m.lifetime_actions, 'tier_id', v_tier.id, 'tier_name', v_tier.name, 'duplicate', false);
end;
$$;
revoke all on function public.record_qualifying_action(uuid, integer, text, text) from public;
grant execute on function public.record_qualifying_action(uuid, integer, text, text) to authenticated;

create function public.redeem_member_reward(p_member_id uuid, p_idempotency_key text)
returns jsonb language plpgsql security definer set search_path = public, auth as $$
declare m public.members%rowtype; v_existing public.ledger_transactions%rowtype;
begin
  select * into m from public.members where id = p_member_id for update;
  if not found then raise exception 'Member not found'; end if;
  if not public.has_venue_role(m.venue_id, array['owner','admin','staff']) then raise exception 'Venue staff access required'; end if;
  select * into v_existing from public.ledger_transactions where venue_id = m.venue_id and idempotency_key = p_idempotency_key;
  if found then
    if v_existing.member_id <> p_member_id or v_existing.event_type <> 'redemption' then raise exception 'This idempotency key has already been used'; end if;
    return jsonb_build_object('member_id', m.id, 'rewards_available', m.rewards_available, 'duplicate', true);
  end if;
  if m.rewards_available < 1 then raise exception 'No reward is available to redeem'; end if;
  insert into public.ledger_transactions(venue_id, member_id, actor_user_id, event_type, action_units, stamp_delta, rewards_delta, idempotency_key)
  values (m.venue_id, m.id, auth.uid(), 'redemption', 0, 0, -1, p_idempotency_key);
  update public.members set rewards_available = rewards_available - 1 where id = m.id returning * into m;
  return jsonb_build_object('member_id', m.id, 'rewards_available', m.rewards_available, 'duplicate', false);
end;
$$;
revoke all on function public.redeem_member_reward(uuid, text) from public;
grant execute on function public.redeem_member_reward(uuid, text) to authenticated;
