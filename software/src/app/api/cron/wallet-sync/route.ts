import { timingSafeEqual } from 'node:crypto';
import { NextResponse } from 'next/server';
import { syncMemberWallet } from '@/lib/server/member-wallet-sync';
import { createSupabaseAdminClient } from '@/lib/supabase/admin';

export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

function authorized(request: Request) {
  const secret = process.env.CRON_SECRET;
  if (!secret) return false;
  const given = Buffer.from(request.headers.get('authorization') || '');
  const expected = Buffer.from(`Bearer ${secret}`);
  return given.length === expected.length && timingSafeEqual(given, expected);
}

/** Vercel Cron retries wallet cards whose last update failed. The ledger stays authoritative; this only re-pushes it. */
export async function GET(request: Request) {
  if (!authorized(request)) return NextResponse.json({ error: 'Unauthorized.' }, { status: 401 });
  const admin = createSupabaseAdminClient();
  const { data: failed, error } = await admin.from('wallet_passes').select('member_id').not('sync_error', 'is', null).order('updated_at').limit(100);
  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  const memberIds = [...new Set((failed || []).map(row => row.member_id as string))];
  let repaired = 0;
  for (const memberId of memberIds) {
    const result = await syncMemberWallet(memberId);
    if (result.walletSynced) repaired += 1;
  }
  return NextResponse.json({ checked: memberIds.length, repaired });
}
