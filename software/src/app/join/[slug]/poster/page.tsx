import { notFound } from 'next/navigation';
import QRCode from 'qrcode';
import { platform } from '@/config/platform';
import { createSupabaseAdminClient } from '@/lib/supabase/admin';

export const dynamic = 'force-dynamic';
type Context = { params: Promise<{ slug: string }> };

/** Printable counter poster: venue name, reward rule and a QR code to the join page. */
export default async function Poster({ params }: Context) {
  const { slug } = await params;
  const { data: v } = await createSupabaseAdminClient().from('venues').select('name,slug,reward_target,reward_name,action_label,brand_color').eq('slug', slug).maybeSingle();
  if (!v) notFound();
  const url = `${process.env.NEXT_PUBLIC_APP_URL || ''}/join/${v.slug}`;
  const svg = await QRCode.toString(url, { type: 'svg', margin: 1, color: { dark: '#14111F', light: '#FFFFFF' } });
  return <main className="poster" style={{ ['--venue' as string]: v.brand_color }}>
    <section className="poster-card">
      <span className="eyebrow">MEMBERS CLUB</span>
      <h1>{v.name}</h1>
      <p className="poster-rule">{v.reward_target} {v.action_label}s = <b>{v.reward_name}</b></p>
      <div className="poster-qr" dangerouslySetInnerHTML={{ __html: svg }}/>
      <p className="poster-cta">Scan with your camera · Join free · Save to Google Wallet</p>
      <small>No app needed · Powered by {platform.name}</small>
    </section>
    <p className="poster-print">Print this page (⌘P) and place it at the counter.</p>
  </main>;
}
