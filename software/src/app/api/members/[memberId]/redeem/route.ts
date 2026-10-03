import { randomUUID } from 'node:crypto';
import { NextResponse } from 'next/server';
import { createSupabaseServerClient } from '@/lib/supabase/server';
import { redeemSync } from '@/lib/server/member-wallet-sync';

type Context = { params: Promise<{ memberId: string }> };

export async function POST(_request: Request, { params }: Context) {
  const { memberId } = await params;
  const supabase = await createSupabaseServerClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: 'Sign in first.' }, { status: 401 });
  const { data: redemption, error } = await supabase.rpc('redeem_member_reward', { p_member_id: memberId, p_idempotency_key: `redeem-${randomUUID()}` });
  if (error) return NextResponse.json({ error: error.message }, { status: 400 });
  const sync = await redeemSync(supabase, memberId);
  return NextResponse.json({ redemption, ...sync });
}
