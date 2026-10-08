import { NextResponse } from 'next/server';
import { syncVenueLocations } from '@/lib/server/engagement';
import { getVenueRole } from '@/lib/server/venue-access';

export const runtime = 'nodejs';
type Context = { params: Promise<{ venueId: string }> };

async function ownerAccess(venueId: string) {
  const access = await getVenueRole(venueId);
  if (!access) return { error: NextResponse.json({ error: 'Venue access required.' }, { status: 401 }) };
  if (access.role === 'staff') return { error: NextResponse.json({ error: 'Owner or admin access required.' }, { status: 403 }) };
  return { access };
}

export async function GET(_r: Request, { params }: Context) {
  const { venueId } = await params; const { access, error } = await ownerAccess(venueId); if (error) return error;
  const { data } = await access.supabase.from('venue_locations').select('id,label,lat,lng,lock_screen_message').eq('venue_id', venueId).order('created_at');
  return NextResponse.json({ locations: data || [] });
}

/** Replaces the venue's locations (max 10) and pushes them to the wallet cards. */
export async function PUT(request: Request, { params }: Context) {
  const { venueId } = await params; const { access, error } = await ownerAccess(venueId); if (error) return error;
  let input: { locations?: unknown };
  try { input = await request.json(); } catch { return NextResponse.json({ error: 'Expected JSON.' }, { status: 400 }); }
  if (!Array.isArray(input.locations) || input.locations.length > 10) return NextResponse.json({ error: 'Add up to 10 locations.' }, { status: 400 });
  const rows = input.locations.map(item => {
    const l = item as Record<string, unknown>;
    return { venue_id: venueId, label: String(l.label || '').trim().slice(0, 60), lat: Number(l.lat), lng: Number(l.lng), lock_screen_message: typeof l.lockScreenMessage === 'string' && l.lockScreenMessage.trim() ? l.lockScreenMessage.trim().slice(0, 120) : null };
  });
  if (rows.some(r => !r.label || !Number.isFinite(r.lat) || !Number.isFinite(r.lng) || Math.abs(r.lat) > 90 || Math.abs(r.lng) > 180)) return NextResponse.json({ error: 'Each location needs a name and valid coordinates.' }, { status: 400 });
  const { error: delError } = await access.supabase.from('venue_locations').delete().eq('venue_id', venueId);
  if (delError) return NextResponse.json({ error: delError.message }, { status: 400 });
  if (rows.length) { const { error: insError } = await access.supabase.from('venue_locations').insert(rows); if (insError) return NextResponse.json({ error: insError.message }, { status: 400 }); }
  try { await syncVenueLocations(venueId); return NextResponse.json({ saved: rows.length, walletSynced: true }); }
  catch (e) { return NextResponse.json({ saved: rows.length, walletSynced: false, walletSyncMessage: e instanceof Error ? e.message : 'Wallet sync failed.' }); }
}
