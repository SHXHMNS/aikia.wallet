import 'server-only';
import { createSupabaseServerClient } from '@/lib/supabase/server';

/** AIKIA's own team: signed-in users whose verified email is listed in PLATFORM_ADMIN_EMAILS. Separate from venue roles. */
export async function getPlatformAdmin() {
  const allowed = (process.env.PLATFORM_ADMIN_EMAILS || '').split(',').map(email => email.trim().toLowerCase()).filter(Boolean);
  if (!allowed.length) return null;
  const supabase = await createSupabaseServerClient();
  const { data: { user } } = await supabase.auth.getUser();
  const email = user?.email?.toLowerCase();
  if (!user || !email || !user.email_confirmed_at || !allowed.includes(email)) return null;
  return { userId: user.id, email };
}
