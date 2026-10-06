import { NextResponse } from 'next/server';
import { randomUUID } from 'node:crypto';
import { createSupabaseServerClient } from '@/lib/supabase/server';
import { createSupabaseAdminClient } from '@/lib/supabase/admin';
import { syncMemberWallet } from '@/lib/server/member-wallet-sync';

type Context = { params: Promise<{ memberId: string }> };

export async function POST(request: Request, { params }: Context) {
  const { memberId } = await params;
  const supabase = await createSupabaseServerClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: 'Sign in first.' }, { status: 401 });
  let input: { units?: unknown; idempotencyKey?: unknown; note?: unknown; amount?: unknown };
  try { input = await request.json(); } catch { return NextResponse.json({ error: 'Expected JSON.' }, { status: 400 }); }
  const units = Number(input.units ?? 1);
  const idempotencyKey = typeof input.idempotencyKey === 'string' ? input.idempotencyKey : randomUUID();
  const note = typeof input.note === 'string' ? input.note.slice(0, 200) : null;
  if (!Number.isInteger(units) || units < 1 || units > 100 || idempotencyKey.length < 8 || idempotencyKey.length > 120) return NextResponse.json({ error: 'Action details are invalid.' }, { status: 400 });
  const amount = input.amount === null || input.amount === undefined || input.amount === '' ? null : Number(input.amount);
  if (amount !== null && (!Number.isFinite(amount) || amount < 0 || amount > 1_000_000_000)) return NextResponse.json({ error: 'Enter a valid bill amount.' }, { status: 400 });
  const { data: action, error } = await supabase.rpc('record_qualifying_action', { p_member_id: memberId, p_action_units: units, p_idempotency_key: idempotencyKey, p_note: note, p_amount_paise: amount === null ? null : Math.round(amount * 100) });
  if (error) return NextResponse.json({ error: error.message }, { status: 400 });
  const admin = createSupabaseAdminClient();
  const [{ data: member }, { data: membership }] = await Promise.all([
    admin.from('members').select('id,full_name,stamp_balance,rewards_available,lifetime_actions,lifetime_spend_paise,current_tier_id').eq('id', memberId).single(),
    admin.from('members').select('venue_id').eq('id', memberId).single(),
  ]);
  const { data: relation } = membership ? await admin.from('venues').select('name,action_label,reward_target,reward_name').eq('id', membership.venue_id).single() : { data: null };
  const sync = await syncMemberWallet(memberId);
  return NextResponse.json({
    action,
    member: member ? { id: member.id, fullName: member.full_name, stampBalance: member.stamp_balance, rewardsAvailable: member.rewards_available, lifetimeActions: member.lifetime_actions, lifetimeSpendPaise: member.lifetime_spend_paise, ...((action as { tier_name?: string } | null)?.tier_name ? { tier: (action as { tier_name: string }).tier_name } : {}) } : null,
    program: relation ? { venue: relation.name, actionLabel: relation.action_label, rewardTarget: relation.reward_target, rewardName: relation.reward_name } : null,
    ...sync,
  });
}
