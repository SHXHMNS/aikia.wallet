import Link from 'next/link';
import { notFound } from 'next/navigation';
import { platform } from '@/config/platform';
import { getPlatformAdmin } from '@/lib/server/platform-access';
import { createSupabaseAdminClient } from '@/lib/supabase/admin';
import { walletStatus } from '@/lib/wallet/provider';
import MigrateButton from './migrate-button';
import NewVenueForm from './new-venue-form';

export const dynamic = 'force-dynamic';
export const metadata = { title: `Platform | ${platform.name}` };

type VenueRow = { id: string; name: string; slug: string; business_type: string; wallet_program_id: string | null; created_at: string };

export default async function PlatformPage() {
  const operator = await getPlatformAdmin();
  if (!operator) notFound();
  const admin = createSupabaseAdminClient();
  const [{ data: venues }, { data: members }, { data: team }, { data: passes }] = await Promise.all([
    admin.from('venues').select('id,name,slug,business_type,wallet_program_id,created_at').order('created_at', { ascending: false }),
    admin.from('members').select('venue_id'),
    admin.from('venue_team_members').select('venue_id'),
    admin.from('wallet_passes').select('venue_id,sync_error'),
  ]);
  const count = (rows: { venue_id: string }[] | null, venueId: string) => (rows || []).filter(row => row.venue_id === venueId).length;
  const failing = (venueId: string) => (passes || []).filter(row => row.venue_id === venueId && row.sync_error).length;
  const wallet = walletStatus();
  const rows = (venues || []) as VenueRow[];
  return <main className="console-main platform-shell">
    <header className="console-top"><div><span className="eyebrow">{platform.shortName} PLATFORM</span><h1>All venues</h1></div><span className="live-provider">ENGINE · {wallet.engine.toUpperCase()} · {Object.entries(wallet.providers).map(([id, state]) => `${id} ${state.replace('_', ' ')}`).join(' · ')}</span></header>
    <div className="metric-row platform-metrics">
      <article><span>Venues</span><strong>{rows.length}</strong></article>
      <article><span>Members</span><strong>{members?.length || 0}</strong></article>
      <article><span>Wallet cards</span><strong>{passes?.length || 0}</strong></article>
      <article><span>Cards failing sync</span><strong>{(passes || []).filter(row => row.sync_error).length}</strong></article>
    </div>
    <section className="console-panel platform-table">
      <div className="member-table">
        <div className="member-line header"><span>VENUE</span><span>TYPE</span><span>MEMBERS · TEAM</span><span>WALLET</span></div>
        {rows.map(venue => <div className="member-line" key={venue.id}>
          <span><b>{venue.name}</b><small><Link href={`/join/${venue.slug}`}>/join/{venue.slug}</Link> · <Link href={`/join/${venue.slug}/poster`}>poster</Link> · since {new Date(venue.created_at).toLocaleDateString('en-IN')}</small></span>
          <code>{venue.business_type}</code>
          <span>{count(members, venue.id)} members · {count(team, venue.id)} team</span>
          <span>{venue.wallet_program_id || 'default program'}{failing(venue.id) ? <small>{failing(venue.id)} card(s) failing sync</small> : <small>all cards in sync</small>}</span>
        </div>)}
        {!rows.length && <p>No venues yet.</p>}
      </div>
    </section>
    <section className="console-panel platform-table"><span className="eyebrow">NEW VENUE</span><h2>Set up a venue in one step</h2><p>Creates the venue, its reward rule and Ink / Chrome / Pink tiers, invites the owner, and gives you the join link and QR poster.</p><NewVenueForm/></section>
    <section className="console-panel platform-table"><span className="eyebrow">WALLET ENGINE</span><h2>Issue cards on the active engine</h2><p>Creates a card on the current engine for every member who does not have one yet, and lists their save links.</p><MigrateButton/></section>
    <footer className="console-footer"><span>Signed in as {operator.email}</span><Link href="/">Back to venue console</Link></footer>
  </main>;
}
