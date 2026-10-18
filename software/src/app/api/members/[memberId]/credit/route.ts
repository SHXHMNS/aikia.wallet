import { NextResponse } from 'next/server';
import { randomUUID } from 'node:crypto';
import { createSupabaseServerClient } from '@/lib/supabase/server';
import { createSupabaseAdminClient } from '@/lib/supabase/admin';
import { syncMemberWallet } from '@/lib/server/member-wallet-sync';

export const runtime = 'nodejs';
type Context = { params: Promise<{ memberId: string }> };

/**
 * Staff counter: `load` records a top-up the guest paid to the venue (cash / UPI / card), `spend` pays a bill from credit.
 * The SQL functions check the venue role, limits, pay code and idempotency; the ledger stays authoritative.
 */
export async function POST(request: Request, { params }: Context) {
  const { memberId } = await params;
  const supabase = await createSupabaseServerClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: 'Sign in first.' }, { status: 401 });
  let input: Record<string, unknown>;
  try { input = await request.json(); } catch { return NextResponse.json({ error: 'Expected JSON.' }, { status: 400 }); }
  const action = input.action;
  const amount = Number(input.amount);
  const idempotencyKey = typeof input.idempotencyKey === 'string' && input.idempotencyKey.length >= 8 && input.idempotencyKey.length <= 100 ? input.idempotencyKey : randomUUID();
  if (!Number.isFinite(amount) || amount < 1 || amount > 50000) return NextResponse.json({ error: 'Enter an amount between ₹1 and ₹50,000.' }, { status: 400 });
  const paise = Math.round(amount * 100);

  let result: unknown; let visit: unknown = null;
  if (action === 'load') {
    const method = typeof input.method === 'string' ? input.method : 'upi';
    const ref = typeof input.paymentRef === 'string' ? input.paymentRef.slice(0, 80) : null;
    const { data, error } = await supabase.rpc('credit_load', { p_member_id: memberId, p_pay_paise: paise, p_method: method, p_payment_ref: ref, p_idempotency_key: idempotencyKey });
    if (error) return NextResponse.json({ error: error.message }, { status: 400 });
    result = data;
  } else if (action === 'spend') {
    const payCode = typeof input.payCode === 'string' && /^\d{6}$/.test(input.payCode) ? input.payCode : null;
    const { data, error } = await supabase.rpc('credit_spend', { p_member_id: memberId, p_amount_paise: paise, p_idempotency_key: idempotencyKey, p_pay_code: payCode, p_note: null });
    if (error) return NextResponse.json({ error: error.message }, { status: 400 });
    result = data;
    // Paying from credit also counts as a visit with this bill amount (stamps, spend tiers).
    if (input.recordVisit !== false && !(data as { duplicate?: boolean }).duplicate) {
      const { data: v } = await supabase.rpc('record_qualifying_action', { p_member_id: memberId, p_action_units: 1, p_idempotency_key: `${idempotencyKey}-visit`.slice(0, 120), p_note: 'Paid from credit', p_amount_paise: paise });
      visit = v;
    }
  } else {
    return NextResponse.json({ error: 'Unknown credit action.' }, { status: 400 });
  }

  const { data: member } = await createSupabaseAdminClient().from('members').select('stamp_balance,rewards_available,lifetime_actions,lifetime_spend_paise,credit_paid_paise,credit_bonus_paise').eq('id', memberId).single();
  const sync = await syncMemberWallet(memberId);
  return NextResponse.json({
    credit: result, visit,
    member: member ? { stampBalance: member.stamp_balance, rewardsAvailable: member.rewards_available, lifetimeActions: member.lifetime_actions, lifetimeSpendPaise: member.lifetime_spend_paise, creditPaidPaise: member.credit_paid_paise, creditBonusPaise: member.credit_bonus_paise, ...((visit as { tier_name?: string } | null)?.tier_name ? { tier: (visit as { tier_name: string }).tier_name } : {}) } : null,
    ...sync,
  });
}
