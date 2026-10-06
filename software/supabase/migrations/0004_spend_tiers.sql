-- Spend-based tiers: each venue chooses whether tiers unlock by lifetime visits/actions or lifetime spend.
-- Money is stored as integer paise (₹1 = 100 paise) to avoid rounding errors.

alter table public.venues add column if not exists tier_basis text not null default 'actions'
  check (tier_basis in ('actions', 'spend'));

alter table public.members add column if not exists lifetime_spend_paise bigint not null default 0
  check (lifetime_spend_paise >= 0);

alter table public.venue_tiers add column if not exists min_lifetime_spend_paise bigint not null default 0
  check (min_lifetime_spend_paise >= 0);

alter table public.ledger_transactions add column if not exists amount_paise bigint
  check (amount_paise is null or (amount_paise >= 0 and amount_paise <= 100000000000));

-- Picks the member's tier from the venue's chosen basis.
create or replace function public.tier_for_member(p_venue_id uuid, p_lifetime_actions integer, p_lifetime_spend_paise bigint)
returns uuid language sql stable security definer set search_path = public as $$
  select vt.id from public.venue_tiers vt
  join public.venues v on v.id = vt.venue_id
  where vt.venue_id = p_venue_id
    and case when v.tier_basis = 'spend' then vt.min_lifetime_spend_paise <= p_lifetime_spend_paise
             else vt.min_lifetime_actions <= p_lifetime_actions end
  order by case when v.tier_basis = 'spend' then vt.min_lifetime_spend_paise else vt.min_lifetime_actions end desc
  limit 1;
$$;
revoke all on function public.tier_for_member(uuid, integer, bigint) from public;

-- Re-evaluates every member's tier after the owner changes tier rules or the tier basis.
create or replace function public.recompute_member_tiers(p_venue_id uuid)
returns void language plpgsql security definer set search_path = public, auth as $$
begin
  if not public.has_venue_role(p_venue_id, array['owner','admin']) then raise exception 'Venue admin access required'; end if;
  update public.members m set current_tier_id = public.tier_for_member(p_venue_id, m.lifetime_actions, m.lifetime_spend_paise)
  where m.venue_id = p_venue_id;
end;
$$;
revoke all on function public.recompute_member_tiers(uuid) from public;
grant execute on function public.recompute_member_tiers(uuid) to authenticated;

create or replace function public.replace_venue_tiers(p_venue_id uuid, p_tiers jsonb)
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
  insert into public.venue_tiers(venue_id, rank, name, min_lifetime_actions, min_lifetime_spend_paise, benefits, accent_color)
  select p_venue_id, (t->>'rank')::integer, trim(t->>'name'), (t->>'min_lifetime_actions')::integer,
         greatest(coalesce((t->>'min_lifetime_spend_paise')::bigint, 0), 0),
         coalesce(t->'benefits', '[]'::jsonb), coalesce(t->>'accent_color', '#171421')
  from jsonb_array_elements(p_tiers) t;
  update public.members m set current_tier_id = public.tier_for_member(p_venue_id, m.lifetime_actions, m.lifetime_spend_paise)
  where m.venue_id = p_venue_id;
end;
$$;

-- Records one qualifying visit/purchase. p_amount_paise is the bill amount; it is required when the venue's tiers are spend-based.
drop function if exists public.record_qualifying_action(uuid, integer, text, text);
create function public.record_qualifying_action(p_member_id uuid, p_action_units integer, p_idempotency_key text, p_note text default null, p_amount_paise bigint default null)
returns jsonb language plpgsql security definer set search_path = public, auth as $$
declare m public.members%rowtype; v_tier public.venue_tiers%rowtype; v_existing public.ledger_transactions%rowtype;
        v_target integer; v_basis text; v_new_rewards integer; v_new_balance integer;
begin
  if p_action_units < 1 or p_action_units > 100 then raise exception 'Action units must be between 1 and 100'; end if;
  if p_amount_paise is not null and (p_amount_paise < 0 or p_amount_paise > 100000000000) then raise exception 'Bill amount is out of range'; end if;
  select * into m from public.members where id = p_member_id for update;
  if not found then raise exception 'Member not found'; end if;
  if not public.has_venue_role(m.venue_id, array['owner','admin','staff']) then raise exception 'Venue staff access required'; end if;
  select * into v_existing from public.ledger_transactions where venue_id = m.venue_id and idempotency_key = p_idempotency_key;
  if found then
    if v_existing.member_id <> p_member_id then raise exception 'This idempotency key belongs to another member'; end if;
    select * into v_tier from public.venue_tiers where id = m.current_tier_id;
    return jsonb_build_object('member_id', m.id, 'stamp_balance', m.stamp_balance, 'rewards_available', m.rewards_available, 'lifetime_actions', m.lifetime_actions, 'lifetime_spend_paise', m.lifetime_spend_paise, 'tier_id', m.current_tier_id, 'tier_name', v_tier.name, 'duplicate', true);
  end if;
  if m.status <> 'active' then raise exception 'Member is not active'; end if;
  select reward_target, tier_basis into v_target, v_basis from public.venues where id = m.venue_id;
  if v_basis = 'spend' and p_amount_paise is null then raise exception 'Enter the bill amount for this visit'; end if;
  v_new_rewards := (m.stamp_balance + p_action_units) / v_target;
  v_new_balance := (m.stamp_balance + p_action_units) % v_target;
  insert into public.ledger_transactions(venue_id, member_id, actor_user_id, event_type, action_units, stamp_delta, rewards_delta, idempotency_key, note, amount_paise)
  values (m.venue_id, m.id, auth.uid(), 'qualifying_action', p_action_units, p_action_units, v_new_rewards, p_idempotency_key, p_note, p_amount_paise);
  update public.members set stamp_balance = v_new_balance, rewards_available = rewards_available + v_new_rewards,
    lifetime_actions = lifetime_actions + p_action_units, lifetime_spend_paise = lifetime_spend_paise + coalesce(p_amount_paise, 0)
  where id = m.id returning * into m;
  select * into v_tier from public.venue_tiers where id = public.tier_for_member(m.venue_id, m.lifetime_actions, m.lifetime_spend_paise);
  update public.members set current_tier_id = v_tier.id where id = m.id;
  return jsonb_build_object('member_id', m.id, 'stamp_balance', m.stamp_balance, 'rewards_available', m.rewards_available, 'lifetime_actions', m.lifetime_actions, 'lifetime_spend_paise', m.lifetime_spend_paise, 'tier_id', v_tier.id, 'tier_name', v_tier.name, 'duplicate', false);
end;
$$;
revoke all on function public.record_qualifying_action(uuid, integer, text, text, bigint) from public;
grant execute on function public.record_qualifying_action(uuid, integer, text, text, bigint) to authenticated;
