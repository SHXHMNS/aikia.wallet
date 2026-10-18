import { NextResponse } from 'next/server';
import { createSupabaseServerClient } from '@/lib/supabase/server';
import { syncMemberWallet } from '@/lib/server/member-wallet-sync';

export const runtime = 'nodejs';
type Context = { params: Promise<{ transactionId: string }> };

/** Owner/admin undo of a wrong payment or top-up. The SQL function enforces the role and one reversal per entry. */
export async function POST(request: Request, { params }: Context) {
  const { transactionId } = await params;
  const supabase = await createSupabaseServerClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: 'Sign in first.' }, { status: 401 });
  const input = await request.json().catch(() => ({})) as { note?: unknown };
  const { data, error } = await supabase.rpc('credit_reverse', { p_transaction_id: transactionId, p_idempotency_key: `reverse-${transactionId}`, p_note: typeof input.note === 'string' ? input.note.slice(0, 200) : null });
  if (error) return NextResponse.json({ error: error.message }, { status: 400 });
  const sync = await syncMemberWallet((data as { member_id: string }).member_id);
  return NextResponse.json({ credit: data, ...sync });
}
