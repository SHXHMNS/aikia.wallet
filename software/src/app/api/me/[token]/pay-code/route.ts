import { NextResponse } from 'next/server';
import { createSupabaseAdminClient } from '@/lib/supabase/admin';
import { validAccessToken } from '@/lib/server/member-card';

export const runtime = 'nodejs';
type Context = { params: Promise<{ token: string }> };

/**
 * A fresh single-use pay code, valid 45 seconds. The page shows it as a QR ("AKPAY.<member code>.<code>").
 * A screenshot is useless once it expires or has been used once.
 */
export async function POST(_r: Request, { params }: Context) {
  const { token } = await params;
  if (!validAccessToken(token)) return NextResponse.json({ error: 'This card link is not valid.' }, { status: 404 });
  const { data, error } = await createSupabaseAdminClient().rpc('issue_pay_code', { p_access_token: token });
  if (error) return NextResponse.json({ error: 'This card link is not valid.' }, { status: 404 });
  const { code, expires_at, public_code } = data as { code: string; expires_at: string; public_code: string };
  return NextResponse.json({ code, expiresAt: expires_at, qrValue: `AKPAY.${public_code}.${code}` }, { headers: { 'cache-control': 'no-store' } });
}
