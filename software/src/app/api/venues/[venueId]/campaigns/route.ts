import { NextResponse } from 'next/server';
import { getVenueRole } from '@/lib/server/venue-access';

type Context = { params: Promise<{ venueId: string }> };
const kinds = ['broadcast', 'daily', 'weather_rain', 'weather_hot', 'winback'];

function campaignInput(b: Record<string, unknown>) {
  const name = String(b.name || '').trim(); const header = String(b.header || '').trim(); const body = String(b.body || '').trim();
  const kind = kinds.includes(String(b.kind)) ? String(b.kind) : null;
  const weekdays = Array.isArray(b.weekdays) ? [...new Set(b.weekdays.map(Number).filter(d => Number.isInteger(d) && d >= 0 && d <= 6))] : [0, 1, 2, 3, 4, 5, 6];
  const winbackDays = Number(b.winbackDays ?? 14);
  if (!kind || !name || name.length > 60 || !header || header.length > 60 || !body || body.length > 300 || !weekdays.length || !Number.isInteger(winbackDays) || winbackDays < 3 || winbackDays > 365) return null;
  return { name, kind, header, body, weekdays, winback_days: winbackDays };
}

export async function GET(_r: Request, { params }: Context) {
  const { venueId } = await params; const access = await getVenueRole(venueId);
  if (!access || access.role === 'staff') return NextResponse.json({ error: 'Owner or admin access required.' }, { status: 403 });
  const [{ data: campaigns }, { data: sends }] = await Promise.all([
    access.supabase.from('campaigns').select('*').eq('venue_id', venueId).order('created_at', { ascending: false }),
    access.supabase.from('campaign_sends').select('campaign_id,trigger,audience,status,detail,sent_at').eq('venue_id', venueId).order('sent_at', { ascending: false }).limit(20),
  ]);
  return NextResponse.json({ campaigns: campaigns || [], sends: sends || [] });
}

export async function POST(request: Request, { params }: Context) {
  const { venueId } = await params; const access = await getVenueRole(venueId);
  if (!access || access.role === 'staff') return NextResponse.json({ error: 'Owner or admin access required.' }, { status: 403 });
  let b: Record<string, unknown>; try { b = await request.json(); } catch { return NextResponse.json({ error: 'Expected JSON.' }, { status: 400 }); }
  const values = campaignInput(b);
  if (!values) return NextResponse.json({ error: 'Give the campaign a name, a type, a title (60) and a message (300).' }, { status: 400 });
  const { data, error } = await access.supabase.from('campaigns').insert({ ...values, venue_id: venueId }).select('*').single();
  if (error) return NextResponse.json({ error: error.message }, { status: 400 });
  return NextResponse.json({ campaign: data }, { status: 201 });
}
