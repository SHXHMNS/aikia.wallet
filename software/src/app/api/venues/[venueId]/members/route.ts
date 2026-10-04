import { randomBytes } from 'node:crypto';
import { NextResponse } from 'next/server';
import { getVenueRole } from '@/lib/server/venue-access';
import { createSupabaseAdminClient } from '@/lib/supabase/admin';
import { issueMemberWallets } from '@/lib/server/member-wallet-sync';

type Context = { params: Promise<{ venueId: string }> };
export async function POST(request: Request, { params }: Context) {
  const { venueId } = await params;
  const access = await getVenueRole(venueId);
  if (!access) return NextResponse.json({ error: 'Venue access required.' }, { status: 401 });
  let input: { fullName?: unknown };
  try { input = await request.json(); } catch { return NextResponse.json({ error: 'Expected JSON.' }, { status: 400 }); }
  const fullName = typeof input.fullName === 'string' ? input.fullName.trim() : '';
  if (!fullName || fullName.length > 120) return NextResponse.json({ error: 'Member name must be 1–120 characters.' }, { status: 400 });
  const [{ data: venue, error: venueError }, { data: entryTier, error: tierError }] = await Promise.all([
    access.supabase.from('venues').select('*').eq('id', venueId).single(),
    access.supabase.from('venue_tiers').select('id').eq('venue_id', venueId).eq('min_lifetime_actions', 0).single(),
  ]);
  if (venueError || tierError || !venue || !entryTier) return NextResponse.json({ error: 'Venue or entry tier is not configured.' }, { status: 400 });
  const publicCode = `A${randomBytes(4).toString('hex').toUpperCase()}`;
  const admin = createSupabaseAdminClient();
  const { data: member, error } = await admin.from('members').insert({ venue_id: venueId, full_name: fullName, public_code: publicCode, current_tier_id: entryTier.id }).select('*').single();
  if (error) return NextResponse.json({ error: error.message }, { status: 400 });
  const { saveLinks, walletSyncMessage } = await issueMemberWallets(member.id);
  return NextResponse.json({ member: { id: member.id, fullName: member.full_name, publicCode: member.public_code, stampBalance: member.stamp_balance, lifetimeActions: member.lifetime_actions }, saveLinks, walletSyncMessage }, { status: 201 });
}
