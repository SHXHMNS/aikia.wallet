import { createHmac, randomBytes } from 'node:crypto';
import { NextResponse } from 'next/server';
import { createSupabaseAdminClient } from '@/lib/supabase/admin';
import { googleWalletConfigured } from '@/lib/wallet/google';
import { getWalletProvider } from '@/lib/wallet/provider';
import type { MemberWalletData, VenueWalletConfig } from '@/lib/wallet/types';

export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';
type Context = { params: Promise<{ slug: string }> };

export async function POST(request: Request, { params }: Context) {
  const { slug } = await params;
  let input: { fullName?: unknown; consent?: unknown };
  try { input = await request.json(); } catch { return NextResponse.json({ error: 'Enter your name and agree to the membership terms.' }, { status: 400 }); }
  const fullName = typeof input.fullName === 'string' ? input.fullName.trim() : '';
  if (!fullName || fullName.length > 120 || input.consent !== true) return NextResponse.json({ error: 'Enter your name and agree to the membership terms.' }, { status: 400 });
  const rateSecret = process.env.JOIN_RATE_LIMIT_SECRET;
  const ip = request.headers.get('x-forwarded-for')?.split(',')[0]?.trim() || (process.env.NODE_ENV !== 'production' ? 'local-development' : '');
  if (!rateSecret || !ip) return NextResponse.json({ error: 'Membership sign-up is temporarily unavailable. Please ask the venue team.' }, { status: 503 });

  const admin = createSupabaseAdminClient();
  const { data: venue } = await admin.from('venues').select('*').eq('slug', slug).maybeSingle();
  if (!venue) return NextResponse.json({ error: 'This loyalty program is not available.' }, { status: 404 });
  const fingerprint = createHmac('sha256', rateSecret).update(ip).digest('hex');
  const { data: allowed, error: limitError } = await admin.rpc('consume_public_join_attempt', {
    p_venue_id: venue.id, p_fingerprint: fingerprint, p_limit: 5, p_window_seconds: 600,
  });
  if (limitError) return NextResponse.json({ error: 'Membership sign-up is temporarily unavailable. Please ask the venue team.' }, { status: 503 });
  if (!allowed) return NextResponse.json({ error: 'Too many sign-up attempts. Please wait a few minutes or ask the venue team.' }, { status: 429 });

  const { data: tier } = await admin.from('venue_tiers').select('*').eq('venue_id', venue.id).eq('min_lifetime_actions', 0).maybeSingle();
  if (!tier) return NextResponse.json({ error: 'This venue has not finished setting up its rewards.' }, { status: 503 });
  const publicCode = `A${randomBytes(5).toString('hex').toUpperCase()}`;
  const { data: member, error: memberError } = await admin.from('members').insert({
    venue_id: venue.id, full_name: fullName, public_code: publicCode, current_tier_id: tier.id,
    consented_at: new Date().toISOString(), consent_version: 'venue-loyalty-v1',
  }).select('*').single();
  if (memberError || !member) return NextResponse.json({ error: 'Your membership could not be created. Please try once more or ask the venue team.' }, { status: 503 });

  let saveUrl: string | null = null;
  let walletSyncMessage: string | null = null;
  if (googleWalletConfigured()) {
    const venueConfig: VenueWalletConfig = { id: venue.id, name: venue.name, slug: venue.slug, brandColor: venue.brand_color, backgroundColor: venue.background_color, programLogoUrl: venue.program_logo_url, heroImageUrl: venue.hero_image_url, balanceLabel: venue.balance_label, actionLabel: venue.action_label };
    const memberData: MemberWalletData = { id: member.id, venueId: venue.id, fullName: member.full_name, publicCode: member.public_code, scanToken: member.scan_token, stampBalance: member.stamp_balance, balanceLabel: venue.balance_label, rewardsAvailable: member.rewards_available, lifetimeActions: member.lifetime_actions, tierName: tier.name, tierBenefits: tier.benefits || [] };
    try {
      const issued = await getWalletProvider('google').issueMemberPass(venueConfig, memberData);
      const { error: passError } = await admin.from('wallet_passes').upsert({ member_id: member.id, venue_id: venue.id, provider: 'google', provider_class_id: issued.providerClassId, provider_object_id: issued.providerObjectId, last_synced_at: new Date().toISOString(), sync_error: null }, { onConflict: 'member_id' });
      if (passError) throw passError;
      saveUrl = issued.saveUrl;
    } catch { walletSyncMessage = 'Your membership is ready. The Google Wallet pass is not available yet; please ask the venue team.'; }
  } else walletSyncMessage = 'Your membership is ready. The venue is finishing Google Wallet setup; please ask the team for help adding the pass.';
  return NextResponse.json({ member: { publicCode: member.public_code, saveUrl, walletSyncMessage } }, { status: 201 });
}
