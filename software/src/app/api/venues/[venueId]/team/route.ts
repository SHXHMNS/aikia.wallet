import { NextResponse } from 'next/server';
import { getVenueRole } from '@/lib/server/venue-access';
import { createSupabaseAdminClient } from '@/lib/supabase/admin';

type Context = { params: Promise<{ venueId: string }> };

export async function POST(request: Request, { params }: Context) {
  const { venueId } = await params;
  const access = await getVenueRole(venueId);
  if (!access) return NextResponse.json({ error: 'Venue access required.' }, { status: 401 });
  if (access.role !== 'owner' && access.role !== 'admin') return NextResponse.json({ error: 'Owner access is required to invite team members.' }, { status: 403 });
  let input: { email?: unknown; role?: unknown };
  try { input = await request.json(); } catch { return NextResponse.json({ error: 'Expected JSON.' }, { status: 400 }); }
  const email = typeof input.email === 'string' ? input.email.trim().toLowerCase() : '';
  const role = input.role === 'admin' ? 'admin' : 'staff';
  if (role === 'admin' && access.role !== 'owner') return NextResponse.json({ error: 'Only the venue owner can add admins.' }, { status: 403 });
  if (email.length > 254 || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return NextResponse.json({ error: 'Enter a valid staff email address.' }, { status: 400 });
  const { data: existing } = await access.supabase.from('venue_team_members').select('user_id').eq('venue_id', venueId);
  const admin = createSupabaseAdminClient();
  const redirectTo = `${process.env.NEXT_PUBLIC_APP_URL || new URL(request.url).origin}/auth/callback?next=/`;
  const { data, error } = await admin.auth.admin.inviteUserByEmail(email, { redirectTo });
  if (error || !data.user) return NextResponse.json({ error: error?.message || 'Supabase did not create an invitation.' }, { status: 400 });
  if (existing?.some(member => member.user_id === data.user.id)) return NextResponse.json({ error: 'This person already belongs to the venue.' }, { status: 409 });
  const { error: insertError } = await admin.from('venue_team_members').insert({ venue_id: venueId, user_id: data.user.id, role });
  if (insertError) return NextResponse.json({ error: `The invitation was sent but team access could not be saved: ${insertError.message}` }, { status: 500 });
  return NextResponse.json({ invited: { email, role, userId: data.user.id } }, { status: 201 });
}

/** Removes a person's access to this venue. Owners can remove admins and staff; admins can remove staff. */
export async function DELETE(request: Request, { params }: Context) {
  const { venueId } = await params;
  const access = await getVenueRole(venueId);
  if (!access) return NextResponse.json({ error: 'Venue access required.' }, { status: 401 });
  if (access.role !== 'owner' && access.role !== 'admin') return NextResponse.json({ error: 'Owner or admin access required.' }, { status: 403 });
  const userId = new URL(request.url).searchParams.get('userId') || '';
  if (!/^[0-9a-f-]{36}$/i.test(userId)) return NextResponse.json({ error: 'Choose a team member to remove.' }, { status: 400 });
  if (userId === access.userId) return NextResponse.json({ error: 'You cannot remove yourself.' }, { status: 400 });
  const admin = createSupabaseAdminClient();
  const { data: target } = await admin.from('venue_team_members').select('role').eq('venue_id', venueId).eq('user_id', userId).maybeSingle();
  if (!target) return NextResponse.json({ error: 'That person is not on this venue team.' }, { status: 404 });
  if (target.role === 'owner') return NextResponse.json({ error: 'The venue owner cannot be removed.' }, { status: 403 });
  if (target.role === 'admin' && access.role !== 'owner') return NextResponse.json({ error: 'Only the venue owner can remove an admin.' }, { status: 403 });
  const { error } = await admin.from('venue_team_members').delete().eq('venue_id', venueId).eq('user_id', userId);
  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json({ removed: userId });
}
