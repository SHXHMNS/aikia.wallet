import { NextResponse } from 'next/server';
import { getVenueRole } from '@/lib/server/venue-access';

type Context = { params: Promise<{ venueId: string; campaignId: string }> };

export async function PATCH(request: Request, { params }: Context) {
  const { venueId, campaignId } = await params; const access = await getVenueRole(venueId);
  if (!access || access.role === 'staff') return NextResponse.json({ error: 'Owner or admin access required.' }, { status: 403 });
  const b = await request.json().catch(() => ({})) as { active?: unknown };
  const { error } = await access.supabase.from('campaigns').update({ active: b.active === true }).eq('id', campaignId).eq('venue_id', venueId);
  if (error) return NextResponse.json({ error: error.message }, { status: 400 });
  return NextResponse.json({ ok: true });
}

export async function DELETE(_r: Request, { params }: Context) {
  const { venueId, campaignId } = await params; const access = await getVenueRole(venueId);
  if (!access || access.role === 'staff') return NextResponse.json({ error: 'Owner or admin access required.' }, { status: 403 });
  const { error } = await access.supabase.from('campaigns').delete().eq('id', campaignId).eq('venue_id', venueId);
  if (error) return NextResponse.json({ error: error.message }, { status: 400 });
  return NextResponse.json({ ok: true });
}
