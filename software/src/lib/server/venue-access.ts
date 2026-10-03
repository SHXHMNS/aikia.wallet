import 'server-only';
import { createSupabaseServerClient } from '@/lib/supabase/server';

export type VenueRole = 'owner' | 'admin' | 'staff';

export async function getVenueRole(venueId: string): Promise<{ supabase: Awaited<ReturnType<typeof createSupabaseServerClient>>; userId: string; role: VenueRole } | null> {
  const supabase = await createSupabaseServerClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return null;
  const { data: teamMember, error } = await supabase
    .from('venue_team_members')
    .select('role')
    .eq('venue_id', venueId)
    .eq('user_id', user.id)
    .maybeSingle();
  if (error || !teamMember) return null;
  return { supabase, userId: user.id, role: teamMember.role as VenueRole };
}
