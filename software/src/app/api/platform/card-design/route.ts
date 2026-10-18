import { NextResponse } from 'next/server';
import { getPlatformAdmin } from '@/lib/server/platform-access';
import { syncMemberWallet } from '@/lib/server/member-wallet-sync';
import { createSupabaseAdminClient } from '@/lib/supabase/admin';
import { applyPassKitBranding } from '@/lib/wallet/passkit-branding';

export const runtime = 'nodejs';
export const maxDuration = 60;

/**
 * AIKIA team only: pushes the current card design (metallic tier art, colours, copy, credit and My card fields)
 * to PassKit, then refreshes every member's card so the new fields fill in.
 */
export async function POST(request: Request) {
  if (!(await getPlatformAdmin())) return NextResponse.json({ error: 'Platform admin access required.' }, { status: 403 });
  const appUrl = process.env.NEXT_PUBLIC_APP_URL || new URL(request.url).origin;
  let log: string[];
  try { log = await applyPassKitBranding(appUrl); }
  catch (error) { return NextResponse.json({ error: error instanceof Error ? error.message : 'Card design update failed.' }, { status: 502 }); }
  const { data: passes } = await createSupabaseAdminClient().from('wallet_passes').select('member_id').eq('provider', 'passkit').limit(200);
  let refreshed = 0;
  for (const memberId of new Set((passes || []).map(p => p.member_id as string))) if ((await syncMemberWallet(memberId)).walletSynced) refreshed += 1;
  return NextResponse.json({ log, refreshed });
}
