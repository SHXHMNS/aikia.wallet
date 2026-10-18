import { NextResponse } from 'next/server';
import { getVenueRole } from '@/lib/server/venue-access';
import { refreshVenueMood, sendMoodNow, type Mood } from '@/lib/server/engagement';

export const runtime = 'nodejs';
type Context = { params: Promise<{ venueId: string }> };
const MOODS: Mood[] = ['rain', 'hot', 'cold', 'clear'];

async function ownerAccess(venueId: string) {
  const access = await getVenueRole(venueId);
  if (!access) return { error: NextResponse.json({ error: 'Venue access required.' }, { status: 401 }) };
  if (access.role === 'staff') return { error: NextResponse.json({ error: 'Owner or admin access required.' }, { status: 403 }) };
  return { access };
}

export async function GET(_r: Request, { params }: Context) {
  const { venueId } = await params; const { access, error } = await ownerAccess(venueId); if (error) return error;
  const { data } = await access.supabase.from('venues').select('nearby_moods,nearby_mood_today,nearby_mood_updated_at').eq('id', venueId).single();
  return NextResponse.json({ moods: data?.nearby_moods, today: data?.nearby_mood_today, updatedAt: data?.nearby_mood_updated_at });
}

/** Saves the four weather messages and whether they replace the nearby (geofence) text. */
export async function PUT(request: Request, { params }: Context) {
  const { venueId } = await params; const { access, error } = await ownerAccess(venueId); if (error) return error;
  const input = await request.json().catch(() => ({})) as Record<string, unknown>;
  const moods: Record<string, unknown> = { enabled: input.enabled === true };
  for (const m of MOODS) {
    const text = typeof input[m] === 'string' ? (input[m] as string).trim() : '';
    if (!text || text.length > 120) return NextResponse.json({ error: 'Each weather message needs 1 to 120 characters.' }, { status: 400 });
    moods[m] = text;
  }
  const { error: updateError } = await access.supabase.from('venues').update({ nearby_moods: moods }).eq('id', venueId);
  if (updateError) return NextResponse.json({ error: updateError.message }, { status: 400 });
  if (!moods.enabled) return NextResponse.json({ saved: true });
  try { return NextResponse.json({ saved: true, ...(await refreshVenueMood(venueId)) }); }
  catch (e) { return NextResponse.json({ saved: true, walletSyncMessage: e instanceof Error ? e.message : 'Could not check the weather.' }); }
}

/** action "check": today's weather and the message the cards now show. action "send": also notify every card now. */
export async function POST(request: Request, { params }: Context) {
  const { venueId } = await params; const { error } = await ownerAccess(venueId); if (error) return error;
  const input = await request.json().catch(() => ({})) as { action?: unknown };
  try { return NextResponse.json(input.action === 'send' ? await sendMoodNow(venueId) : await refreshVenueMood(venueId)); }
  catch (e) { return NextResponse.json({ error: e instanceof Error ? e.message : 'Weather check failed.' }, { status: 400 }); }
}
