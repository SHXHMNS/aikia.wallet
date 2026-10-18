import { NextResponse } from 'next/server';
import { createSupabaseAdminClient } from '@/lib/supabase/admin';
import { validAccessToken } from '@/lib/server/member-card';
import { syncMemberWallet } from '@/lib/server/member-wallet-sync';

export const runtime = 'nodejs';
type Context = { params: Promise<{ token: string }> };

async function memberId(token: string) {
  const { data } = await createSupabaseAdminClient().from('members').select('id').eq('access_token', token).maybeSingle();
  return data?.id as string | undefined;
}

/** "Send a coffee": the guest turns their own credit (or one earned reward) into a one-time item voucher for a friend. */
export async function POST(request: Request, { params }: Context) {
  const { token } = await params;
  if (!validAccessToken(token)) return NextResponse.json({ error: 'This card link is not valid.' }, { status: 404 });
  const input = await request.json().catch(() => ({})) as Record<string, unknown>;
  const source = input.source === 'reward' ? 'reward' : 'credit';
  const itemId = typeof input.itemId === 'string' && /^[0-9a-f-]{36}$/i.test(input.itemId) ? input.itemId : null;
  if (source === 'credit' && !itemId) return NextResponse.json({ error: 'Choose what to send.' }, { status: 400 });
  const { data, error } = await createSupabaseAdminClient().rpc('gift_create', {
    p_access_token: token, p_item_id: itemId, p_quantity: Number(input.quantity) === 2 ? 2 : 1, p_source: source,
    p_recipient_name: typeof input.recipientName === 'string' ? input.recipientName.slice(0, 60) : null,
    p_message: typeof input.message === 'string' ? input.message.slice(0, 140) : null,
  });
  if (error) return NextResponse.json({ error: error.message }, { status: 400 });
  const id = await memberId(token); if (id) await syncMemberWallet(id);
  return NextResponse.json({ gift: data }, { status: 201 });
}

/** The sender takes back a gift the friend has not used yet; credit or the reward returns to their card. */
export async function DELETE(request: Request, { params }: Context) {
  const { token } = await params;
  const giftId = new URL(request.url).searchParams.get('id') || '';
  if (!validAccessToken(token) || !/^[0-9a-f-]{36}$/i.test(giftId)) return NextResponse.json({ error: 'Gift not found.' }, { status: 404 });
  const { error } = await createSupabaseAdminClient().rpc('gift_cancel', { p_access_token: token, p_gift_id: giftId });
  if (error) return NextResponse.json({ error: error.message }, { status: 400 });
  const id = await memberId(token); if (id) await syncMemberWallet(id);
  return NextResponse.json({ cancelled: true });
}
