import { NextResponse } from 'next/server';
import { getPlatformAdmin } from '@/lib/server/platform-access';
import { issueMemberWallets } from '@/lib/server/member-wallet-sync';
import { createSupabaseAdminClient } from '@/lib/supabase/admin';
import { activeProviderIds } from '@/lib/wallet/provider';

export const runtime = 'nodejs';
export const maxDuration = 60;

/**
 * AIKIA team only: issues a card on the currently active wallet engine for every active member
 * that does not have one yet (used when moving from PassKit to our own Google engine).
 * Members re-save their card from the returned link, the staff scanner, or by reopening the join page.
 */
export async function POST() {
  if (!(await getPlatformAdmin())) return NextResponse.json({ error: 'Platform admin access required.' }, { status: 403 });
  const providers = activeProviderIds();
  if (!providers.length) return NextResponse.json({ error: 'No wallet engine is configured.' }, { status: 503 });
  const admin = createSupabaseAdminClient();
  const [{ data: members }, { data: passes }] = await Promise.all([
    admin.from('members').select('id,public_code,full_name').eq('status', 'active').order('created_at').limit(500),
    admin.from('wallet_passes').select('member_id,provider').in('provider', providers),
  ]);
  const done = new Set((passes || []).map(pass => pass.member_id as string));
  const results = [];
  for (const member of (members || []).filter(m => !done.has(m.id))) {
    const { saveLinks, walletSyncMessage } = await issueMemberWallets(member.id);
    results.push({ code: member.public_code, name: member.full_name, google: saveLinks.google || null, error: walletSyncMessage });
  }
  return NextResponse.json({ engine: providers, migrated: results.filter(r => r.google).length, failed: results.filter(r => !r.google).length, results });
}
