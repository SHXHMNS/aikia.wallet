import { notFound } from 'next/navigation';
import { createSupabaseAdminClient } from '@/lib/supabase/admin';
import JoinClient from './join-client';

export const dynamic = 'force-dynamic';

export default async function JoinPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  let admin;
  try { admin = createSupabaseAdminClient(); } catch { notFound(); }
  const { data: venue } = await admin.from('venues')
    .select('id,name,slug,brand_color,background_color,action_label,balance_label,reward_target,reward_name')
    .eq('slug', slug).maybeSingle();
  if (!venue) notFound();
  return <JoinClient venue={venue}/>;
}
