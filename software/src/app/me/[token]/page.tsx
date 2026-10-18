import type { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { loadMemberCard } from '@/lib/server/member-card';
import MeClient from './me-client';

export const dynamic = 'force-dynamic';
export const metadata: Metadata = { title: 'My card', robots: { index: false, follow: false } };

/** The guest's private page, opened from the link on their wallet card. The link itself is the key. */
export default async function MyCardPage({ params }: { params: Promise<{ token: string }> }) {
  const { token } = await params;
  let card;
  try { card = await loadMemberCard(token); } catch { notFound(); }
  if (!card) notFound();
  return <MeClient token={token} initial={card}/>;
}
