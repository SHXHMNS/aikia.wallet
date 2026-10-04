import { NextResponse } from 'next/server';
import { getVenueRole } from '@/lib/server/venue-access';
import { createSupabaseAdminClient } from '@/lib/supabase/admin';

type Context = { params: Promise<{ venueId: string }> };

export async function GET(request: Request, { params }: Context) {
  const { venueId } = await params;
  const access = await getVenueRole(venueId);
  if (!access) return NextResponse.json({ error: 'Venue access required.' }, { status: 401 });
  const code = new URL(request.url).searchParams.get('code')?.trim();
  if (!code || code.length > 100 || !/^[A-Za-z0-9._-]+$/.test(code)) return NextResponse.json({ error: 'Enter a valid member code or pass QR value.' }, { status: 400 });
  const admin = createSupabaseAdminClient();
  const columns = 'id,venue_id,full_name,public_code,scan_token,stamp_balance,rewards_available,lifetime_actions,current_tier_id,status';
  let { data: member, error } = await admin.from('members').select(columns)
    .eq('venue_id', venueId).or(`public_code.eq.${code},scan_token.eq.${code}`).maybeSingle();
  if (!error && !member) {
    // PassKit cards carry PassKit's member ID in the QR code by default.
    const { data: pass } = await admin.from('wallet_passes').select('member_id').eq('venue_id', venueId).eq('provider_object_id', code).maybeSingle();
    if (pass) ({ data: member, error } = await admin.from('members').select(columns).eq('venue_id', venueId).eq('id', pass.member_id).maybeSingle());
  }
  if (error || !member) return NextResponse.json({ error: 'No member found for that code.' }, { status: 404 });
  const [{ data: tier }, { data: venue }] = await Promise.all([
    admin.from('venue_tiers').select('name,benefits,min_lifetime_actions').eq('id', member.current_tier_id).single(),
    admin.from('venues').select('action_label,balance_label,reward_target,reward_name').eq('id', venueId).single(),
  ]);
  return NextResponse.json({ member: { id: member.id, fullName: member.full_name, publicCode: member.public_code, stampBalance: member.stamp_balance, rewardsAvailable: member.rewards_available, lifetimeActions: member.lifetime_actions, status: member.status, tier: tier?.name || 'Member', tierBenefits: tier?.benefits || [], tierMinimum: tier?.min_lifetime_actions || 0 }, program: venue });
}
