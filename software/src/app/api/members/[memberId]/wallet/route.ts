import { NextResponse } from 'next/server';
import { issueMemberWallets } from '@/lib/server/member-wallet-sync';
import { getVenueRole } from '@/lib/server/venue-access';
import { createSupabaseAdminClient } from '@/lib/supabase/admin';

export const runtime = 'nodejs';
type Context = { params: Promise<{ memberId: string }> };

/** Issues (or re-issues) a member's wallet card and returns the save links. Any venue team member may do this at the counter. */
export async function POST(_request: Request, { params }: Context) {
  const { memberId } = await params;
  if (!/^[0-9a-f-]{36}$/i.test(memberId)) return NextResponse.json({ error: 'Unknown member.' }, { status: 400 });
  const { data: member } = await createSupabaseAdminClient().from('members').select('venue_id,status').eq('id', memberId).maybeSingle();
  if (!member) return NextResponse.json({ error: 'Unknown member.' }, { status: 404 });
  const access = await getVenueRole(member.venue_id);
  if (!access) return NextResponse.json({ error: 'Venue access required.' }, { status: 401 });
  if (member.status !== 'active') return NextResponse.json({ error: 'This membership is not active.' }, { status: 409 });
  const { saveLinks, walletSyncMessage } = await issueMemberWallets(memberId);
  if (!saveLinks.google && !saveLinks.apple) return NextResponse.json({ error: walletSyncMessage || 'The wallet card could not be issued.' }, { status: 502 });
  return NextResponse.json({ saveLinks, walletSyncMessage });
}
