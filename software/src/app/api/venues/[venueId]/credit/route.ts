import { NextResponse } from 'next/server';
import { getVenueRole } from '@/lib/server/venue-access';
import { createSupabaseAdminClient } from '@/lib/supabase/admin';

export const runtime = 'nodejs';
type Context = { params: Promise<{ venueId: string }> };
type Pack = { pay: number; get: number };

async function ownerAccess(venueId: string) {
  const access = await getVenueRole(venueId);
  if (!access) return { error: NextResponse.json({ error: 'Venue access required.' }, { status: 401 }) };
  if (access.role === 'staff') return { error: NextResponse.json({ error: 'Owner or admin access required.' }, { status: 403 }) };
  return { access };
}

/** Credit & gifts settings, the gift menu and the money report (loaded, spent, outstanding). */
export async function GET(_r: Request, { params }: Context) {
  const { venueId } = await params; const { access, error } = await ownerAccess(venueId); if (error) return error;
  const admin = createSupabaseAdminClient();
  const [{ data: venue }, { data: items }, { data: tx }, { data: members }, { data: gifts }] = await Promise.all([
    access.supabase.from('venues').select('credit_enabled,credit_packs,tapless_limit_paise,daily_spend_cap_paise,gift_daily_limit,gift_valid_days').eq('id', venueId).single(),
    access.supabase.from('gift_items').select('id,name,credit_cost_paise,active,sort').eq('venue_id', venueId).eq('active', true).order('sort'),
    admin.from('credit_transactions').select('id,kind,paid_delta_paise,bonus_delta_paise,amount_paise,payment_method,payment_ref,verified_by_code,reverses_id,note,created_at,members(full_name,public_code)').eq('venue_id', venueId).order('created_at', { ascending: false }).limit(40),
    admin.from('members').select('credit_paid_paise,credit_bonus_paise').eq('venue_id', venueId),
    admin.from('gifts').select('id,item_name,quantity,source,status,recipient_name,created_at,redeemed_at,members:sender_member_id(full_name)').eq('venue_id', venueId).order('created_at', { ascending: false }).limit(20),
  ]);
  const reversed = new Set((tx || []).map(t => t.reverses_id).filter(Boolean));
  const outstanding = (members || []).reduce((acc, m) => ({ paid: acc.paid + (m.credit_paid_paise || 0), bonus: acc.bonus + (m.credit_bonus_paise || 0) }), { paid: 0, bonus: 0 });
  // Totals over all time, from the ledger itself.
  const { data: all } = await admin.from('credit_transactions').select('kind,amount_paise,id,reverses_id').eq('venue_id', venueId);
  const allReversed = new Set((all || []).map(t => t.reverses_id).filter(Boolean));
  const sum = (kind: string) => (all || []).filter(t => t.kind === kind && !allReversed.has(t.id)).reduce((n, t) => n + Number(t.amount_paise), 0);
  return NextResponse.json({
    settings: venue, giftItems: items || [], gifts: gifts || [],
    transactions: (tx || []).map(t => ({ ...t, reversed: reversed.has(t.id) })),
    report: { loadedPaise: sum('load'), spentPaise: sum('spend'), giftedPaise: sum('gift_out') - sum('gift_return'), outstandingPaidPaise: outstanding.paid, outstandingBonusPaise: outstanding.bonus },
  });
}

export async function PUT(request: Request, { params }: Context) {
  const { venueId } = await params; const { access, error } = await ownerAccess(venueId); if (error) return error;
  let input: Record<string, unknown>;
  try { input = await request.json(); } catch { return NextResponse.json({ error: 'Expected JSON.' }, { status: 400 }); }
  const packs = Array.isArray(input.packs) ? (input.packs as Pack[]).map(p => ({ pay: Math.round(Number(p.pay)), get: Math.round(Number(p.get)) })) : [];
  if (packs.length > 6 || packs.some(p => !(p.pay >= 1 && p.pay <= 50000 && p.get >= p.pay && p.get <= p.pay * 1.5))) {
    return NextResponse.json({ error: 'Each top-up pack needs a price of ₹1 to ₹50,000 and a value between the price and 1.5 times the price.' }, { status: 400 });
  }
  const num = (v: unknown, min: number, max: number, label: string) => { const n = Number(v); if (!Number.isFinite(n) || n < min || n > max) throw new Error(`${label} must be between ${min} and ${max}.`); return n; };
  let patch;
  try {
    patch = {
      credit_enabled: input.creditEnabled === true,
      credit_packs: packs,
      tapless_limit_paise: Math.round(num(input.taplessLimit, 0, 100000, 'Scan-only limit (₹)') * 100),
      daily_spend_cap_paise: Math.round(num(input.dailyCap, 1, 1000000, 'Daily limit (₹)') * 100),
      gift_daily_limit: Math.round(num(input.giftDailyLimit, 0, 10, 'Gifts per day')),
      gift_valid_days: Math.round(num(input.giftValidDays, 1, 365, 'Gift validity (days)')),
    };
  } catch (e) { return NextResponse.json({ error: e instanceof Error ? e.message : 'Invalid settings.' }, { status: 400 }); }
  const { error: updateError } = await access.supabase.from('venues').update(patch).eq('id', venueId);
  if (updateError) return NextResponse.json({ error: updateError.message }, { status: 400 });

  if (Array.isArray(input.giftItems)) {
    const items = (input.giftItems as { name?: unknown; price?: unknown }[]).slice(0, 12).map((it, sort) => ({ venue_id: venueId, name: String(it.name || '').trim().slice(0, 60), credit_cost_paise: Math.round(Number(it.price) * 100), active: true, sort }));
    if (items.some(it => !it.name || !(it.credit_cost_paise >= 100 && it.credit_cost_paise <= 10000000))) return NextResponse.json({ error: 'Each gift item needs a name and a price.' }, { status: 400 });
    // Old items are switched off rather than deleted, so past gifts keep their history.
    await access.supabase.from('gift_items').update({ active: false }).eq('venue_id', venueId);
    if (items.length) { const { error: insError } = await access.supabase.from('gift_items').insert(items); if (insError) return NextResponse.json({ error: insError.message }, { status: 400 }); }
  }
  return NextResponse.json({ saved: true });
}
