-- Venue credit (closed-loop: spendable only at the issuing venue, no cash-out, no person-to-person money transfer),
-- rotating single-use pay codes, "Send a coffee" gift vouchers, and weather-mood nearby messages.
-- Money is integer paise. Credit has two buckets: paid (what the guest paid) and bonus (the venue's top-up extra).
-- Spending uses paid credit first, then bonus.

-- ── Venue settings ──────────────────────────────────────────────────────────
alter table public.venues
  add column if not exists credit_enabled boolean not null default false,
  -- Top-up packs in rupees, e.g. pay 2000 → get 2300.
  add column if not exists credit_packs jsonb not null default '[{"pay":500,"get":550},{"pay":1000,"get":1125},{"pay":2000,"get":2300}]'::jsonb
    check (jsonb_typeof(credit_packs) = 'array' and jsonb_array_length(credit_packs) <= 6),
  -- A scan alone may pay up to this; above it the guest's live pay code is required.
  add column if not exists tapless_limit_paise bigint not null default 30000 check (tapless_limit_paise between 0 and 10000000),
  add column if not exists daily_spend_cap_paise bigint not null default 500000 check (daily_spend_cap_paise between 100 and 100000000),
  add column if not exists gift_daily_limit integer not null default 2 check (gift_daily_limit between 0 and 10),
  add column if not exists gift_valid_days integer not null default 30 check (gift_valid_days between 1 and 365),
  -- Nearby (geofence) message that changes with today's weather at the venue.
  add column if not exists nearby_moods jsonb not null default '{"enabled":false,"rain":"It’s raining ☔ Come in, grab a hot coffee. Your card is ready.","hot":"Hot one today ☀️ Cool down with an iced coffee, a few steps away.","cold":"Chilly out 🧣 A warm cup is waiting for you nearby.","clear":"You’re close by ☕ Your usual is a few steps away."}'::jsonb
    check (jsonb_typeof(nearby_moods) = 'object'),
  add column if not exists nearby_mood_today text,
  add column if not exists nearby_mood_updated_at timestamptz;

-- ── Member balances and private link ────────────────────────────────────────
alter table public.members
  -- Secret for the guest's private "My card" page (pay code, gifts). Never placed in the card barcode.
  add column if not exists access_token text not null default encode(gen_random_bytes(24), 'hex'),
  add column if not exists credit_paid_paise bigint not null default 0 check (credit_paid_paise >= 0),
  add column if not exists credit_bonus_paise bigint not null default 0 check (credit_bonus_paise >= 0);
create unique index if not exists members_access_token_idx on public.members(access_token);

-- ── Credit ledger (append-only) ─────────────────────────────────────────────
create table if not exists public.credit_transactions (
  id uuid primary key default gen_random_uuid(),
  venue_id uuid not null references public.venues(id) on delete cascade,
  member_id uuid not null,
  actor_user_id uuid references auth.users(id),
  kind text not null check (kind in ('load', 'spend', 'reversal', 'gift_out', 'gift_return', 'adjust')),
  paid_delta_paise bigint not null default 0,
  bonus_delta_paise bigint not null default 0,
  amount_paise bigint not null default 0 check (amount_paise >= 0),
  payment_method text check (payment_method is null or payment_method in ('cash', 'upi', 'card', 'online')),
  payment_ref text check (payment_ref is null or char_length(payment_ref) <= 80),
  verified_by_code boolean not null default false,
  reverses_id uuid unique references public.credit_transactions(id),
  gift_id uuid,
  idempotency_key text not null check (char_length(idempotency_key) between 8 and 120),
  note text check (note is null or char_length(note) <= 200),
  created_at timestamptz not null default now(),
  unique (venue_id, idempotency_key),
  foreign key (venue_id, member_id) references public.members(venue_id, id) on delete cascade
);
create index if not exists credit_tx_member_idx on public.credit_transactions(member_id, created_at desc);
create index if not exists credit_tx_venue_idx on public.credit_transactions(venue_id, created_at desc);

-- ── Rotating single-use pay codes (shown on the guest's private page) ───────
create table if not exists public.pay_codes (
  id uuid primary key default gen_random_uuid(),
  member_id uuid not null references public.members(id) on delete cascade,
  code text not null check (code ~ '^[0-9]{6}$'),
  expires_at timestamptz not null,
  used_at timestamptz,
  created_at timestamptz not null default now()
);
create index if not exists pay_codes_member_idx on public.pay_codes(member_id, expires_at desc);

-- ── Gift menu and vouchers ("Send a coffee") ────────────────────────────────
create table if not exists public.gift_items (
  id uuid primary key default gen_random_uuid(),
  venue_id uuid not null references public.venues(id) on delete cascade,
  name text not null check (char_length(name) between 1 and 60),
  credit_cost_paise bigint not null check (credit_cost_paise between 100 and 10000000),
  active boolean not null default true,
  sort integer not null default 0,
  created_at timestamptz not null default now()
);
create index if not exists gift_items_venue_idx on public.gift_items(venue_id, sort);

create table if not exists public.gifts (
  id uuid primary key default gen_random_uuid(),
  venue_id uuid not null references public.venues(id) on delete cascade,
  sender_member_id uuid not null references public.members(id) on delete cascade,
  token text not null unique default encode(gen_random_bytes(16), 'hex'),
  item_name text not null check (char_length(item_name) between 1 and 80),
  quantity integer not null check (quantity between 1 and 2),
  source text not null check (source in ('credit', 'reward')),
  cost_paid_paise bigint not null default 0,
  cost_bonus_paise bigint not null default 0,
  recipient_name text check (recipient_name is null or char_length(recipient_name) <= 60),
  message text check (message is null or char_length(message) <= 140),
  status text not null default 'active' check (status in ('active', 'redeemed', 'cancelled', 'expired')),
  expires_at timestamptz not null,
  redeemed_at timestamptz,
  redeemed_by uuid references auth.users(id),
  created_at timestamptz not null default now()
);
create index if not exists gifts_sender_idx on public.gifts(sender_member_id, created_at desc);
create index if not exists gifts_venue_idx on public.gifts(venue_id, created_at desc);

alter table public.credit_transactions enable row level security;
alter table public.pay_codes enable row level security;
alter table public.gift_items enable row level security;
alter table public.gifts enable row level security;
revoke all on table public.pay_codes from anon, authenticated;

create policy credit_tx_read on public.credit_transactions for select to authenticated using (public.has_venue_role(venue_id, array['owner','admin']));
create policy gift_items_read on public.gift_items for select to authenticated using (public.has_venue_role(venue_id));
create policy gift_items_manage on public.gift_items for all to authenticated using (public.has_venue_role(venue_id, array['owner','admin'])) with check (public.has_venue_role(venue_id, array['owner','admin']));
create policy gifts_read on public.gifts for select to authenticated using (public.has_venue_role(venue_id, array['owner','admin']));

-- IST calendar day start, for daily caps.
create or replace function public.ist_day_start(p_at timestamptz default now())
returns timestamptz language sql immutable as $$
  select (date_trunc('day', p_at at time zone 'Asia/Kolkata')) at time zone 'Asia/Kolkata';
$$;

create or replace function public.credit_result(m public.members, p_tx uuid, p_duplicate boolean, p_extra jsonb default '{}'::jsonb)
returns jsonb language sql stable as $$
  select jsonb_build_object('member_id', m.id, 'credit_paid_paise', m.credit_paid_paise, 'credit_bonus_paise', m.credit_bonus_paise,
    'credit_balance_paise', m.credit_paid_paise + m.credit_bonus_paise, 'transaction_id', p_tx, 'duplicate', p_duplicate) || p_extra;
$$;

-- Staff record a top-up the guest paid to the venue (cash / UPI / card into the venue's own account).
-- The bonus is computed here from the venue's packs, never trusted from the browser.
create or replace function public.credit_load(p_member_id uuid, p_pay_paise bigint, p_method text, p_payment_ref text, p_idempotency_key text)
returns jsonb language plpgsql security definer set search_path = public, auth as $$
declare m public.members%rowtype; v public.venues%rowtype; v_existing public.credit_transactions%rowtype; v_bonus bigint := 0; v_tx uuid; pack jsonb;
begin
  if p_pay_paise < 100 or p_pay_paise > 5000000 then raise exception 'Top-up must be between ₹1 and ₹50,000'; end if;
  if p_method not in ('cash', 'upi', 'card', 'online') then raise exception 'Choose how the guest paid'; end if;
  select * into m from public.members where id = p_member_id for update;
  if not found then raise exception 'Member not found'; end if;
  if not public.has_venue_role(m.venue_id, array['owner','admin','staff']) then raise exception 'Venue staff access required'; end if;
  select * into v_existing from public.credit_transactions where venue_id = m.venue_id and idempotency_key = p_idempotency_key;
  if found then
    if v_existing.member_id <> m.id then raise exception 'This idempotency key belongs to another member'; end if;
    return public.credit_result(m, v_existing.id, true);
  end if;
  select * into v from public.venues where id = m.venue_id;
  if not v.credit_enabled then raise exception 'Credit is not switched on for this venue'; end if;
  if m.status <> 'active' then raise exception 'Member is not active'; end if;
  for pack in select * from jsonb_array_elements(v.credit_packs) loop
    if ((pack->>'pay')::numeric * 100)::bigint = p_pay_paise then v_bonus := greatest(((pack->>'get')::numeric * 100)::bigint - p_pay_paise, 0); end if;
  end loop;
  insert into public.credit_transactions(venue_id, member_id, actor_user_id, kind, paid_delta_paise, bonus_delta_paise, amount_paise, payment_method, payment_ref, idempotency_key)
  values (m.venue_id, m.id, auth.uid(), 'load', p_pay_paise, v_bonus, p_pay_paise, p_method, nullif(trim(p_payment_ref), ''), p_idempotency_key) returning id into v_tx;
  update public.members set credit_paid_paise = credit_paid_paise + p_pay_paise, credit_bonus_paise = credit_bonus_paise + v_bonus where id = m.id returning * into m;
  return public.credit_result(m, v_tx, false, jsonb_build_object('bonus_paise', v_bonus));
end;
$$;
revoke all on function public.credit_load(uuid, bigint, text, text, text) from public;
grant execute on function public.credit_load(uuid, bigint, text, text, text) to authenticated;

-- Staff deduct the bill from the guest's credit. Above the venue's tap-less limit the guest's live pay code is required.
create or replace function public.credit_spend(p_member_id uuid, p_amount_paise bigint, p_idempotency_key text, p_pay_code text default null, p_note text default null)
returns jsonb language plpgsql security definer set search_path = public, auth as $$
declare m public.members%rowtype; v public.venues%rowtype; v_existing public.credit_transactions%rowtype; v_code public.pay_codes%rowtype;
        v_today bigint; v_paid bigint; v_bonus bigint; v_tx uuid; v_verified boolean := false;
begin
  if p_amount_paise < 100 or p_amount_paise > 5000000 then raise exception 'Bill must be between ₹1 and ₹50,000'; end if;
  select * into m from public.members where id = p_member_id for update;
  if not found then raise exception 'Member not found'; end if;
  if not public.has_venue_role(m.venue_id, array['owner','admin','staff']) then raise exception 'Venue staff access required'; end if;
  select * into v_existing from public.credit_transactions where venue_id = m.venue_id and idempotency_key = p_idempotency_key;
  if found then
    if v_existing.member_id <> m.id or v_existing.kind <> 'spend' then raise exception 'This idempotency key has already been used'; end if;
    return public.credit_result(m, v_existing.id, true, jsonb_build_object('amount_paise', v_existing.amount_paise));
  end if;
  select * into v from public.venues where id = m.venue_id;
  if not v.credit_enabled then raise exception 'Credit is not switched on for this venue'; end if;
  if m.status <> 'active' then raise exception 'Member is not active'; end if;
  if p_pay_code is not null then
    select * into v_code from public.pay_codes where member_id = m.id and code = p_pay_code and used_at is null and expires_at > now()
      order by created_at desc limit 1 for update;
    if not found then raise exception 'That pay code has expired or was already used. Ask the guest to refresh it.'; end if;
    update public.pay_codes set used_at = now() where id = v_code.id;
    v_verified := true;
  end if;
  if p_amount_paise > v.tapless_limit_paise and not v_verified then
    raise exception 'Bills over ₹% need the guest''s live pay code. Ask them to open "My card" and show the Pay QR.', (v.tapless_limit_paise / 100);
  end if;
  select coalesce(sum(amount_paise), 0) into v_today from public.credit_transactions
    where member_id = m.id and kind = 'spend' and created_at >= public.ist_day_start()
      and not exists (select 1 from public.credit_transactions r where r.reverses_id = credit_transactions.id);
  if v_today + p_amount_paise > v.daily_spend_cap_paise then raise exception 'This would pass the daily credit limit of ₹%', (v.daily_spend_cap_paise / 100); end if;
  if m.credit_paid_paise + m.credit_bonus_paise < p_amount_paise then
    raise exception 'Not enough credit. Balance is ₹%; collect ₹% by cash or UPI, or charge less from credit.',
      round((m.credit_paid_paise + m.credit_bonus_paise) / 100.0, 2), round((p_amount_paise - m.credit_paid_paise - m.credit_bonus_paise) / 100.0, 2);
  end if;
  v_paid := least(m.credit_paid_paise, p_amount_paise);
  v_bonus := p_amount_paise - v_paid;
  insert into public.credit_transactions(venue_id, member_id, actor_user_id, kind, paid_delta_paise, bonus_delta_paise, amount_paise, verified_by_code, idempotency_key, note)
  values (m.venue_id, m.id, auth.uid(), 'spend', -v_paid, -v_bonus, p_amount_paise, v_verified, p_idempotency_key, p_note) returning id into v_tx;
  update public.members set credit_paid_paise = credit_paid_paise - v_paid, credit_bonus_paise = credit_bonus_paise - v_bonus where id = m.id returning * into m;
  return public.credit_result(m, v_tx, false, jsonb_build_object('amount_paise', p_amount_paise, 'verified_by_code', v_verified));
end;
$$;
revoke all on function public.credit_spend(uuid, bigint, text, text, text) from public;
grant execute on function public.credit_spend(uuid, bigint, text, text, text) to authenticated;

-- Owner/admin undo a wrong spend or top-up. Writes a new, opposite entry; the original stays in the ledger.
create or replace function public.credit_reverse(p_transaction_id uuid, p_idempotency_key text, p_note text default null)
returns jsonb language plpgsql security definer set search_path = public, auth as $$
declare t public.credit_transactions%rowtype; m public.members%rowtype; v_tx uuid;
begin
  select * into t from public.credit_transactions where id = p_transaction_id;
  if not found then raise exception 'Transaction not found'; end if;
  if not public.has_venue_role(t.venue_id, array['owner','admin']) then raise exception 'Only the owner or an admin can reverse credit'; end if;
  if t.kind not in ('load', 'spend') then raise exception 'Only top-ups and payments can be reversed'; end if;
  if exists (select 1 from public.credit_transactions where reverses_id = t.id) then raise exception 'This transaction was already reversed'; end if;
  select * into m from public.members where id = t.member_id for update;
  if m.credit_paid_paise - t.paid_delta_paise < 0 or m.credit_bonus_paise - t.bonus_delta_paise < 0 then
    raise exception 'The guest has already spent this credit, so the top-up cannot be reversed in full';
  end if;
  insert into public.credit_transactions(venue_id, member_id, actor_user_id, kind, paid_delta_paise, bonus_delta_paise, amount_paise, reverses_id, idempotency_key, note)
  values (t.venue_id, t.member_id, auth.uid(), 'reversal', -t.paid_delta_paise, -t.bonus_delta_paise, t.amount_paise, t.id, p_idempotency_key, p_note) returning id into v_tx;
  update public.members set credit_paid_paise = credit_paid_paise - t.paid_delta_paise, credit_bonus_paise = credit_bonus_paise - t.bonus_delta_paise where id = m.id returning * into m;
  return public.credit_result(m, v_tx, false);
end;
$$;
revoke all on function public.credit_reverse(uuid, text, text) from public;
grant execute on function public.credit_reverse(uuid, text, text) to authenticated;

-- Guest's private page asks for a fresh pay code (server-only; the page is authorised by the member access token).
create or replace function public.issue_pay_code(p_access_token text)
returns jsonb language plpgsql security definer set search_path = public as $$
declare m public.members%rowtype; v_code text; v_exp timestamptz := now() + interval '45 seconds';
begin
  select * into m from public.members where access_token = p_access_token;
  if not found or m.status <> 'active' then raise exception 'Card not found'; end if;
  delete from public.pay_codes where member_id = m.id and (expires_at < now() - interval '1 day');
  v_code := lpad((floor(random() * 1000000))::int::text, 6, '0');
  insert into public.pay_codes(member_id, code, expires_at) values (m.id, v_code, v_exp);
  return jsonb_build_object('code', v_code, 'expires_at', v_exp, 'public_code', m.public_code);
end;
$$;
revoke all on function public.issue_pay_code(text) from public, anon, authenticated;
grant execute on function public.issue_pay_code(text) to service_role;

-- Guest sends a gift voucher to a friend: 1–2 items, this venue only, paid from their own credit or one earned reward.
-- No money moves between people; the friend receives an item voucher redeemable once at this venue.
create or replace function public.gift_create(p_access_token text, p_item_id uuid, p_quantity integer, p_source text, p_recipient_name text, p_message text)
returns jsonb language plpgsql security definer set search_path = public as $$
declare m public.members%rowtype; v public.venues%rowtype; it public.gift_items%rowtype; v_sent integer; v_cost bigint := 0; v_paid bigint := 0; v_bonus bigint := 0;
        v_name text; g public.gifts%rowtype;
begin
  if p_quantity not between 1 and 2 then raise exception 'You can send one or two items'; end if;
  select * into m from public.members where access_token = p_access_token for update;
  if not found or m.status <> 'active' then raise exception 'Card not found'; end if;
  select * into v from public.venues where id = m.venue_id;
  select count(*) into v_sent from public.gifts where sender_member_id = m.id and created_at >= public.ist_day_start() and status <> 'cancelled';
  if v_sent >= v.gift_daily_limit then raise exception 'You have reached today''s gift limit (%)', v.gift_daily_limit; end if;
  if p_source = 'reward' then
    if p_quantity <> 1 then raise exception 'A reward can be gifted one at a time'; end if;
    if m.rewards_available < 1 then raise exception 'You have no reward ready to gift yet'; end if;
    v_name := v.reward_name;
    update public.members set rewards_available = rewards_available - 1 where id = m.id;
  elsif p_source = 'credit' then
    if not v.credit_enabled then raise exception 'Credit is not switched on at this venue'; end if;
    select * into it from public.gift_items where id = p_item_id and venue_id = m.venue_id and active;
    if not found then raise exception 'That item is not available to gift'; end if;
    v_name := it.name; v_cost := it.credit_cost_paise * p_quantity;
    if m.credit_paid_paise + m.credit_bonus_paise < v_cost then raise exception 'Not enough credit for this gift'; end if;
    v_paid := least(m.credit_paid_paise, v_cost); v_bonus := v_cost - v_paid;
    update public.members set credit_paid_paise = credit_paid_paise - v_paid, credit_bonus_paise = credit_bonus_paise - v_bonus where id = m.id;
  else raise exception 'Choose how to pay for the gift'; end if;
  insert into public.gifts(venue_id, sender_member_id, item_name, quantity, source, cost_paid_paise, cost_bonus_paise, recipient_name, message, expires_at)
  values (m.venue_id, m.id, v_name, p_quantity, p_source, v_paid, v_bonus, nullif(trim(p_recipient_name), ''), nullif(trim(p_message), ''), now() + make_interval(days => v.gift_valid_days))
  returning * into g;
  if p_source = 'credit' then
    insert into public.credit_transactions(venue_id, member_id, kind, paid_delta_paise, bonus_delta_paise, amount_paise, gift_id, idempotency_key, note)
    values (m.venue_id, m.id, 'gift_out', -v_paid, -v_bonus, v_cost, g.id, 'gift-' || g.id, p_quantity || ' × ' || v_name);
  else
    insert into public.ledger_transactions(venue_id, member_id, event_type, action_units, stamp_delta, rewards_delta, idempotency_key, note)
    values (m.venue_id, m.id, 'redemption', 0, 0, -1, 'gift-' || g.id, 'Gifted to a friend');
  end if;
  return jsonb_build_object('gift_id', g.id, 'token', g.token, 'item_name', g.item_name, 'quantity', g.quantity, 'expires_at', g.expires_at);
end;
$$;
revoke all on function public.gift_create(text, uuid, integer, text, text, text) from public, anon, authenticated;
grant execute on function public.gift_create(text, uuid, integer, text, text, text) to service_role;

-- Returns an unused gift to the sender (sender cancels, or the voucher expires).
create or replace function public.gift_return(p_gift_id uuid, p_status text)
returns void language plpgsql security definer set search_path = public as $$
declare g public.gifts%rowtype;
begin
  if p_status not in ('cancelled', 'expired') then raise exception 'Invalid gift status'; end if;
  select * into g from public.gifts where id = p_gift_id for update;
  if not found or g.status <> 'active' then raise exception 'This gift is no longer active'; end if;
  update public.gifts set status = p_status where id = g.id;
  if g.source = 'credit' then
    update public.members set credit_paid_paise = credit_paid_paise + g.cost_paid_paise, credit_bonus_paise = credit_bonus_paise + g.cost_bonus_paise where id = g.sender_member_id;
    insert into public.credit_transactions(venue_id, member_id, kind, paid_delta_paise, bonus_delta_paise, amount_paise, gift_id, idempotency_key, note)
    values (g.venue_id, g.sender_member_id, 'gift_return', g.cost_paid_paise, g.cost_bonus_paise, g.cost_paid_paise + g.cost_bonus_paise, g.id, 'gift-return-' || g.id, 'Gift ' || p_status);
  else
    update public.members set rewards_available = rewards_available + 1 where id = g.sender_member_id;
    insert into public.ledger_transactions(venue_id, member_id, event_type, action_units, stamp_delta, rewards_delta, idempotency_key, note)
    values (g.venue_id, g.sender_member_id, 'adjustment', 0, 0, 1, 'gift-return-' || g.id, 'Gift ' || p_status || ', reward returned');
  end if;
end;
$$;
revoke all on function public.gift_return(uuid, text) from public, anon, authenticated;
grant execute on function public.gift_return(uuid, text) to service_role;

create or replace function public.gift_cancel(p_access_token text, p_gift_id uuid)
returns void language plpgsql security definer set search_path = public as $$
begin
  if not exists (select 1 from public.gifts g join public.members m on m.id = g.sender_member_id where g.id = p_gift_id and m.access_token = p_access_token) then
    raise exception 'Gift not found';
  end if;
  perform public.gift_return(p_gift_id, 'cancelled');
end;
$$;
revoke all on function public.gift_cancel(text, uuid) from public, anon, authenticated;
grant execute on function public.gift_cancel(text, uuid) to service_role;

-- Daily job: expired, unused gifts go back to the sender.
create or replace function public.expire_gifts()
returns integer language plpgsql security definer set search_path = public as $$
declare g record; n integer := 0;
begin
  for g in select id from public.gifts where status = 'active' and expires_at < now() loop
    perform public.gift_return(g.id, 'expired'); n := n + 1;
  end loop;
  return n;
end;
$$;
revoke all on function public.expire_gifts() from public, anon, authenticated;
grant execute on function public.expire_gifts() to service_role;

-- Staff redeem a friend's gift voucher at the counter (one time only, this venue only).
create or replace function public.gift_redeem(p_venue_id uuid, p_token text)
returns jsonb language plpgsql security definer set search_path = public, auth as $$
declare g public.gifts%rowtype; v_sender text;
begin
  if not public.has_venue_role(p_venue_id, array['owner','admin','staff']) then raise exception 'Venue staff access required'; end if;
  select * into g from public.gifts where token = p_token for update;
  if not found or g.venue_id <> p_venue_id then raise exception 'This gift voucher is not valid at this venue'; end if;
  if g.status = 'redeemed' then raise exception 'This gift was already used on %', to_char(g.redeemed_at at time zone 'Asia/Kolkata', 'DD Mon, HH24:MI'); end if;
  if g.status <> 'active' or g.expires_at < now() then raise exception 'This gift voucher has expired or was cancelled'; end if;
  update public.gifts set status = 'redeemed', redeemed_at = now(), redeemed_by = auth.uid() where id = g.id;
  select full_name into v_sender from public.members where id = g.sender_member_id;
  return jsonb_build_object('item_name', g.item_name, 'quantity', g.quantity, 'from', split_part(v_sender, ' ', 1), 'recipient_name', g.recipient_name, 'message', g.message);
end;
$$;
revoke all on function public.gift_redeem(uuid, text) from public;
grant execute on function public.gift_redeem(uuid, text) to authenticated;
