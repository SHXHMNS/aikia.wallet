import { NextResponse } from 'next/server';
import { sendCampaign, type Campaign } from '@/lib/server/engagement';
import { getVenueRole } from '@/lib/server/venue-access';

export const runtime = 'nodejs';
export const maxDuration = 60;
type Context = { params: Promise<{ venueId: string; campaignId: string }> };

export async function POST(_r: Request, { params }: Context) {
  const { venueId, campaignId } = await params; const access = await getVenueRole(venueId);
  if (!access || access.role === 'staff') return NextResponse.json({ error: 'Owner or admin access required.' }, { status: 403 });
  const { data: campaign } = await access.supabase.from('campaigns').select('*').eq('id', campaignId).eq('venue_id', venueId).maybeSingle();
  if (!campaign) return NextResponse.json({ error: 'Campaign not found.' }, { status: 404 });
  return NextResponse.json(await sendCampaign(campaign as Campaign, 'manual'));
}
