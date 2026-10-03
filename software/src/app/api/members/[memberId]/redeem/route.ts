import { randomUUID } from 'node:crypto';
import { NextResponse } from 'next/server';
import { createSupabaseServerClient } from '@/lib/supabase/server';
import { redeemSync } from '@/lib/server/member-wallet-sync';

type Context = { params: Promise<{ memberId: string }> };

export async function POST(request: Request, { params }: Context) {
  const { memberId } = await params;
  const supabase = await createSupabaseServerClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: 'Sign in first.' }, { status: 401 });
  let input: { idempotencyKey?: unknown };
  try { input = await request.json(); } catch { return NextResponse.json({ error: 'Expected JSON.' }, { status: 400 }); }
  const idempotencyKey = typeof input.idempotencyKey === 'string' ? input.idempotencyKey : `redeem-${randomUUID()}`;
  if (idempotencyKey.length < 8 || idempotencyKey.length > 120 || !/^[A-Za-z0-9._:-]+$/.test(idempotencyKey)) return NextResponse.json({ error: 'Redemption request key is invalid.' }, { status: 400 });
  const { data: redemption, error } = await supabase.rpc('redeem_member_reward', { p_member_id: memberId, p_idempotency_key: idempotencyKey });
  if (error) return NextResponse.json({ error: error.message }, { status: 400 });
  const sync = await redeemSync(memberId);
  return NextResponse.json({ redemption, ...sync });
}
