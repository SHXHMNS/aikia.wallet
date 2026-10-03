import { randomBytes } from 'node:crypto';
import { NextResponse } from 'next/server';
import { getVenueRole } from '@/lib/server/venue-access';
import { createSupabaseAdminClient } from '@/lib/supabase/admin';
import { googleWalletConfigured } from '@/lib/wallet/google';
import { getWalletProvider } from '@/lib/wallet/provider';
import type { MemberWalletData, VenueWalletConfig } from '@/lib/wallet/types';

type Context = { params: Promise<{ venueId: string }> };
type VenueRow = { id: string; name: string; slug: string; brand_color: string; background_color: string | null; program_logo_url: string | null; hero_image_url: string | null; balance_label: string; action_label: string };
const venueConfig = (v: VenueRow): VenueWalletConfig => ({ id: v.id, name: v.name, slug: v.slug, brandColor: v.brand_color, backgroundColor: v.background_color, programLogoUrl: v.program_logo_url, heroImageUrl: v.hero_image_url, balanceLabel: v.balance_label, actionLabel: v.action_label });

export async function POST(request: Request, { params }: Context) {
  const { venueId } = await params;
  const access = await getVenueRole(venueId);
  if (!access) return NextResponse.json({ error: 'Venue access required.' }, { status: 401 });
  let input: { fullName?: unknown };
  try { input = await request.json(); } catch { return NextResponse.json({ error: 'Expected JSON.' }, { status: 400 }); }
  const fullName = typeof input.fullName === 'string' ? input.fullName.trim() : '';
  if (!fullName || fullName.length > 120) return NextResponse.json({ error: 'Member name must be 1–120 characters.' }, { status: 400 });
  const [{ data: venue, error: venueError }, { data: entryTier, error: tierError }] = await Promise.all([
    access.supabase.from('venues').select('*').eq('id', venueId).single(),
    access.supabase.from('venue_tiers').select('id').eq('venue_id', venueId).eq('min_lifetime_actions', 0).single(),
  ]);
  if (venueError || tierError || !venue || !entryTier) return NextResponse.json({ error: 'Venue or entry tier is not configured.' }, { status: 400 });
  const publicCode = `A${randomBytes(4).toString('hex').toUpperCase()}`;
  const admin = createSupabaseAdminClient();
  const { data: member, error } = await admin.from('members').insert({ venue_id: venueId, full_name: fullName, public_code: publicCode, current_tier_id: entryTier.id }).select('*').single();
  if (error) return NextResponse.json({ error: error.message }, { status: 400 });
  let saveUrl: string | null = null;
  let walletSyncMessage: string | null = null;
  if (googleWalletConfigured()) {
    const { data: tier } = await access.supabase.from('venue_tiers').select('*').eq('id', entryTier.id).single();
    const memberData: MemberWalletData = { id: member.id, venueId, fullName: member.full_name, publicCode: member.public_code, scanToken: member.scan_token, stampBalance: member.stamp_balance, balanceLabel: venue.balance_label, rewardsAvailable: member.rewards_available, lifetimeActions: member.lifetime_actions, tierName: tier?.name || 'Member', tierBenefits: tier?.benefits || [] };
    try {
      const provider = getWalletProvider('google');
      const issued = await provider.issueMemberPass(venueConfig(venue), memberData);
      const { error: passError } = await admin.from('wallet_passes').upsert({ member_id: member.id, venue_id: venueId, provider: 'google', provider_class_id: issued.providerClassId, provider_object_id: issued.providerObjectId, last_synced_at: new Date().toISOString(), sync_error: null }, { onConflict: 'member_id' });
      if (passError) throw passError;
      saveUrl = issued.saveUrl;
    } catch (issueError) { walletSyncMessage = issueError instanceof Error ? issueError.message : 'Google Wallet pass could not be issued.'; }
  } else walletSyncMessage = 'Google Wallet issuer credentials are not configured yet. The member record is saved; pass issuance can be enabled later.';
  return NextResponse.json({ member: { id: member.id, fullName: member.full_name, publicCode: member.public_code, stampBalance: member.stamp_balance, lifetimeActions: member.lifetime_actions }, saveUrl, walletSyncMessage }, { status: 201 });
}
