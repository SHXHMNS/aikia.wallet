import type { Metadata } from 'next';
import { notFound } from 'next/navigation';
import Link from 'next/link';
import QRCode from 'qrcode';
import { createSupabaseAdminClient } from '@/lib/supabase/admin';

export const dynamic = 'force-dynamic';
export const metadata: Metadata = { title: 'A gift for you', robots: { index: false, follow: false } };

const STATE: Record<string, string> = { redeemed: 'This gift has been used. Enjoy!', cancelled: 'The sender took this gift back.', expired: 'This gift has expired.' };

/** The friend's voucher: a one-time QR the venue team scans. It carries no money and works only at this venue. */
export default async function GiftPage({ params }: { params: Promise<{ token: string }> }) {
  const { token } = await params;
  if (!/^[0-9a-f]{32}$/.test(token)) notFound();
  let admin;
  try { admin = createSupabaseAdminClient(); } catch { notFound(); }
  const { data: gift } = await admin.from('gifts').select('item_name,quantity,status,recipient_name,message,expires_at,venue_id,sender_member_id').eq('token', token).maybeSingle();
  if (!gift) notFound();
  const [{ data: venue }, { data: sender }] = await Promise.all([
    admin.from('venues').select('name,slug').eq('id', gift.venue_id).single(),
    admin.from('members').select('full_name').eq('id', gift.sender_member_id).single(),
  ]);
  const status = gift.status === 'active' && new Date(gift.expires_at) < new Date() ? 'expired' : gift.status;
  const from = (sender?.full_name || 'A friend').split(/\s+/)[0];
  const qr = status === 'active' ? await QRCode.toDataURL(`AKGIFT.${token}`, { margin: 1, width: 520, color: { dark: '#14111F', light: '#FFFFFF' } }) : null;
  const until = new Date(gift.expires_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'Asia/Kolkata' });

  return <main className="me-shell gift-shell">
    <header className="me-top"><span>{venue?.name}</span><small>Gift voucher</small></header>
    <section className="gift-hero">
      <p>{gift.recipient_name ? `${gift.recipient_name}, ` : ''}{from} sent you</p>
      <h1>{gift.quantity} × {gift.item_name}</h1>
      {gift.message && <blockquote>“{gift.message}”</blockquote>}
    </section>
    {qr ? <section className="me-block gift-qr">
      <img src={qr} alt="Gift voucher QR code" width={260} height={260}/>
      <p>Show this at the counter of <b>{venue?.name}</b>. It works once, until {until}.</p>
    </section> : <section className="me-block"><p>{STATE[status] || 'This gift is no longer available.'}</p></section>}
    {venue && <section className="me-block"><h2>Not a member yet?</h2><p>Join {venue.name}&apos;s club free and collect rewards on every visit.</p><Link className="me-secondary" href={`/join/${venue.slug}`}>Join the club</Link></section>}
    <footer className="me-foot">No payment needed. This voucher has no cash value. Powered by aikia.wallet.</footer>
  </main>;
}
