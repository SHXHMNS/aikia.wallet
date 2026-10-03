import { NextResponse } from 'next/server';
import { getVenueRole } from '@/lib/server/venue-access';
import { createSupabaseAdminClient } from '@/lib/supabase/admin';

type Context = { params: Promise<{ venueId: string }> };

export async function POST(request: Request, { params }: Context) {
  const { venueId } = await params;
  const access = await getVenueRole(venueId);
  if (!access) return NextResponse.json({ error: 'Venue access required.' }, { status: 401 });
  if (access.role !== 'owner' && access.role !== 'admin') return NextResponse.json({ error: 'Owner access is required to invite team members.' }, { status: 403 });
  let input: { email?: unknown };
  try { input = await request.json(); } catch { return NextResponse.json({ error: 'Expected JSON.' }, { status: 400 }); }
  const email = typeof input.email === 'string' ? input.email.trim().toLowerCase() : '';
  if (email.length > 254 || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return NextResponse.json({ error: 'Enter a valid staff email address.' }, { status: 400 });
  const { data: existing } = await access.supabase.from('venue_team_members').select('user_id').eq('venue_id', venueId);
  const admin = createSupabaseAdminClient();
  const redirectTo = `${process.env.NEXT_PUBLIC_APP_URL || new URL(request.url).origin}/auth/callback?next=/`;
  const { data, error } = await admin.auth.admin.inviteUserByEmail(email, { redirectTo });
  if (error || !data.user) return NextResponse.json({ error: error?.message || 'Supabase did not create an invitation.' }, { status: 400 });
  if (existing?.some(member => member.user_id === data.user.id)) return NextResponse.json({ error: 'This person already belongs to the venue.' }, { status: 409 });
  const { error: insertError } = await admin.from('venue_team_members').insert({ venue_id: venueId, user_id: data.user.id, role: 'staff' });
  if (insertError) return NextResponse.json({ error: `The invitation was sent but team access could not be saved: ${insertError.message}` }, { status: 500 });
  return NextResponse.json({ invited: { email, role: 'staff' } }, { status: 201 });
}
