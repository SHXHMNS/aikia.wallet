import Link from 'next/link';
import { createSupabaseServerClient } from '@/lib/supabase/server';
import DashboardClient from './dashboard-client';
import { platform } from '@/config/platform';

export const dynamic = 'force-dynamic';

type Venue = { id: string; name: string; slug: string; business_type: string; action_label: string; balance_label: string; reward_target: number; reward_name: string; brand_color: string; background_color: string | null; program_logo_url: string | null; hero_image_url: string | null; wallet_program_id: string | null };

function SetupGate({ title, detail }: { title: string; detail: string }) {
  return <main className="readiness-shell"><div className="brand"><span className="brand-mark">{platform.mark}</span><span>{platform.name}</span></div><section className="readiness-card"><span className="eyebrow">OPERATOR PLATFORM · GOOGLE WALLET READY</span><h1>{title}</h1><p>{detail}</p><div className="readiness-actions"><Link className="button primary" href="/demo/index.html">Open the interactive buyer demo ↗</Link><Link className="button secondary" href="/login">Sign in to a live venue ↗</Link></div><div className="readiness-note"><b>Launch sequence</b><span>Use the fictional venue to demo owner controls, staff scanning, member records, coffee actions, tier unlocks, and rewards. Connect a Supabase project and the wallet engine to move from demo to live venue data.</span></div></section><footer className="readiness-footer">DEMO WORKSPACE · NO LIVE CUSTOMER DATA</footer></main>;
}

export default async function HomePage() {
  if (!process.env.NEXT_PUBLIC_SUPABASE_URL || !(process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY)) {
    return <SetupGate title="A wallet experience that fits every venue." detail="The live operator dashboard is ready for its database and wallet engine. You can still run the complete fictional buyer demo now."/>;
  }
  let supabase: Awaited<ReturnType<typeof createSupabaseServerClient>>;
  try { supabase = await createSupabaseServerClient(); }
  catch { return <SetupGate title="Connect the venue platform." detail="Add the Supabase project URL and publishable key to open authenticated owner and staff dashboards."/>; }
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return <SetupGate title="Your venue loyalty program, in one wallet." detail="Owners tune the brand and rewards. Staff scan members and record visits from a focused counter screen."/>;
  const { data: venues, error: venueError } = await supabase.from('venues').select('*').order('created_at').limit(1);
  if (venueError) return <SetupGate title="Apply the wallet database schema." detail="The app is connected to Supabase. Apply each SQL migration in supabase/migrations in number order, then reload this workspace."/>;
  const venue = (venues?.[0] || null) as Venue | null;
  if (!venue) return <DashboardClient userEmail={user.email || ''} role="owner" venue={null} tiers={[]} members={[]} activity={[]} team={[]}/>;
  const { data: team } = await supabase.from('venue_team_members').select('role').eq('venue_id', venue.id).eq('user_id', user.id).single();
  if (!team) return <SetupGate title="This account has no venue access." detail="Ask the venue owner to add this email as an owner, admin, or staff member, then sign in again."/>;
  const role = team.role as 'owner' | 'admin' | 'staff';
  const [{ data: tiers }, { data: members }, { data: activity }, { data: teamRows }] = await Promise.all([
    supabase.from('venue_tiers').select('*').eq('venue_id', venue.id).order('rank'),
    role === 'staff' ? Promise.resolve({ data: [] }) : supabase.from('members').select('id,full_name,public_code,stamp_balance,rewards_available,lifetime_actions,status,current_tier_id').eq('venue_id', venue.id).order('created_at', { ascending: false }).limit(200),
    role === 'staff' ? Promise.resolve({ data: [] }) : supabase.from('ledger_transactions').select('id,event_type,action_units,rewards_delta,created_at,members(full_name)').eq('venue_id', venue.id).order('created_at', { ascending: false }).limit(10),
    role === 'staff' ? Promise.resolve({ data: [] }) : supabase.from('venue_team_members').select('user_id,role').eq('venue_id', venue.id),
  ]);
  const admin = role === 'staff' ? null : (await import('@/lib/supabase/admin')).createSupabaseAdminClient();
  const teamList = admin ? await Promise.all((teamRows || []).map(async row => { const { data } = await admin.auth.admin.getUserById(row.user_id); return { user_id: row.user_id, role: row.role, email: data.user?.email || 'Invited user' }; })) : [];
  return <DashboardClient userEmail={user.email || ''} role={role} venue={venue} tiers={(tiers || []) as never[]} members={(members || []) as never[]} activity={(activity || []) as never[]} team={teamList}/>;
}
