import { NextResponse } from 'next/server';
import { getVenueRole } from '@/lib/server/venue-access';

export const runtime = 'nodejs';
type Context = { params: Promise<{ venueId: string }> };

/** Staff scan a friend's gift voucher QR and hand over the item. One use only, this venue only. */
export async function POST(request: Request, { params }: Context) {
  const { venueId } = await params;
  const access = await getVenueRole(venueId);
  if (!access) return NextResponse.json({ error: 'Venue access required.' }, { status: 401 });
  const input = await request.json().catch(() => ({})) as { token?: unknown };
  const token = typeof input.token === 'string' ? input.token.trim().toLowerCase() : '';
  if (!/^[0-9a-f]{32}$/.test(token)) return NextResponse.json({ error: 'That is not a gift voucher code.' }, { status: 400 });
  const { data, error } = await access.supabase.rpc('gift_redeem', { p_venue_id: venueId, p_token: token });
  if (error) return NextResponse.json({ error: error.message }, { status: 400 });
  return NextResponse.json({ gift: data });
}
