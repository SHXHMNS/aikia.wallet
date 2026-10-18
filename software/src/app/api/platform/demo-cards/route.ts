import { NextResponse } from 'next/server';
import { getPlatformAdmin } from '@/lib/server/platform-access';
import { createSupabaseAdminClient } from '@/lib/supabase/admin';
import { getWalletProvider, providerConfigured } from '@/lib/wallet/provider';
import type { WalletProviderId } from '@/lib/wallet/types';

export const runtime = 'nodejs';
export const maxDuration = 60;

/** AIKIA team only: every member across venues with their cards, so test cards can be cleaned up before demos. */
export async function GET() {
  if (!(await getPlatformAdmin())) return NextResponse.json({ error: 'Platform admin access required.' }, { status: 403 });
  const admin = createSupabaseAdminClient();
  const [{ data: members }, { data: passes }, { data: venues }] = await Promise.all([
    admin.from('members').select('id,venue_id,full_name,public_code,created_at').order('created_at', { ascending: false }).limit(300),
    admin.from('wallet_passes').select('member_id,provider'),
    admin.from('venues').select('id,name'),
  ]);
  const venueName = new Map((venues || []).map(v => [v.id as string, v.name as string]));
  return NextResponse.json({ members: (members || []).map(m => ({
    id: m.id, name: m.full_name, code: m.public_code, venue: venueName.get(m.venue_id) || '', createdAt: m.created_at,
    cards: (passes || []).filter(p => p.member_id === m.id).map(p => p.provider),
  })) });
}

/**
 * Deletes every member except the ones in `keep`: their wallet cards are removed from the engine
 * (PassKit deletes the card; Google marks it inactive), then the member and their history are deleted.
 * Needs confirm: "DELETE" so it cannot run by accident.
 */
export async function POST(request: Request) {
  if (!(await getPlatformAdmin())) return NextResponse.json({ error: 'Platform admin access required.' }, { status: 403 });
  const input = await request.json().catch(() => ({})) as { keep?: unknown; confirm?: unknown };
  const keep = Array.isArray(input.keep) ? input.keep.filter((id): id is string => typeof id === 'string' && /^[0-9a-f-]{36}$/i.test(id)) : [];
  if (input.confirm !== 'DELETE') return NextResponse.json({ error: 'Type DELETE to confirm.' }, { status: 400 });
  if (!keep.length) return NextResponse.json({ error: 'Choose at least one card to keep.' }, { status: 400 });
  const admin = createSupabaseAdminClient();
  const { data: members } = await admin.from('members').select('id,full_name').not('id', 'in', `(${keep.join(',')})`).limit(300);
  const results: { name: string; removed: boolean; error?: string }[] = [];
  for (const member of members || []) {
    const { data: passes } = await admin.from('wallet_passes').select('provider,provider_class_id,provider_object_id').eq('member_id', member.id);
    try {
      for (const pass of passes || []) {
        const id = pass.provider as WalletProviderId;
        if (providerConfigured(id)) await getWalletProvider(id).removePass({ classId: pass.provider_class_id, objectId: pass.provider_object_id });
      }
      const { error } = await admin.from('members').delete().eq('id', member.id);
      if (error) throw error;
      results.push({ name: member.full_name, removed: true });
    } catch (error) {
      results.push({ name: member.full_name, removed: false, error: error instanceof Error ? error.message.slice(0, 200) : 'Failed.' });
    }
  }
  return NextResponse.json({ removed: results.filter(r => r.removed).length, failed: results.filter(r => !r.removed).length, results });
}
