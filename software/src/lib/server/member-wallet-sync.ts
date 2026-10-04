import 'server-only';
import { createSupabaseAdminClient } from '@/lib/supabase/admin';
import { activeProviderIds, enabledProviderIds, getWalletProvider, providerConfigured } from '@/lib/wallet/provider';
import type { MemberWalletData, SaveLinks, VenueWalletConfig, WalletProviderId } from '@/lib/wallet/types';

type VenueRow = { id: string; name: string; slug: string; brand_color: string; background_color: string | null; program_logo_url: string | null; hero_image_url: string | null; balance_label: string; action_label: string; wallet_program_id?: string | null };
type MemberRow = { id: string; venue_id: string; full_name: string; public_code: string; scan_token: string; stamp_balance: number; rewards_available: number; lifetime_actions: number; current_tier_id: string };
type TierRow = { name: string; benefits: string[] | null } | null;

export function venueWalletConfig(v: VenueRow): VenueWalletConfig {
  return { id: v.id, name: v.name, slug: v.slug, brandColor: v.brand_color, backgroundColor: v.background_color, programLogoUrl: v.program_logo_url, heroImageUrl: v.hero_image_url, balanceLabel: v.balance_label, actionLabel: v.action_label, walletProgramId: v.wallet_program_id };
}

function memberWalletData(member: MemberRow, venue: Pick<VenueRow, 'balance_label'> | null, tier: TierRow): MemberWalletData {
  return {
    id: member.id, venueId: member.venue_id, fullName: member.full_name, publicCode: member.public_code,
    scanToken: member.scan_token, stampBalance: member.stamp_balance, balanceLabel: venue?.balance_label || 'STAMPS',
    rewardsAvailable: member.rewards_available, lifetimeActions: member.lifetime_actions,
    tierName: tier?.name || 'Member', tierBenefits: tier?.benefits || [],
  };
}

const errorText = (error: unknown, fallback: string) => error instanceof Error ? error.message : fallback;

/** Issues (or re-issues) the member's card on every active wallet provider and records it in `wallet_passes`. */
export async function issueMemberWallets(memberId: string): Promise<{ saveLinks: SaveLinks; walletSyncMessage: string | null }> {
  const providers = activeProviderIds();
  if (!providers.length) return { saveLinks: {}, walletSyncMessage: 'Wallet cards are not configured yet. The member is saved; their card can be issued once the wallet engine is connected.' };
  const admin = createSupabaseAdminClient();
  const { data: member, error } = await admin.from('members').select('*').eq('id', memberId).single();
  if (error || !member) return { saveLinks: {}, walletSyncMessage: 'Member saved, but it could not be reloaded to issue a wallet card.' };
  const [{ data: venue }, { data: tier }] = await Promise.all([
    admin.from('venues').select('*').eq('id', member.venue_id).single(),
    admin.from('venue_tiers').select('name,benefits').eq('id', member.current_tier_id).single(),
  ]);
  if (!venue) return { saveLinks: {}, walletSyncMessage: 'Member saved, but the venue could not be loaded to issue a wallet card.' };
  const saveLinks: SaveLinks = {};
  const failures: string[] = [];
  for (const id of providers) {
    try {
      const issued = await getWalletProvider(id).issueMemberPass(venueWalletConfig(venue), memberWalletData(member, venue, tier));
      const { error: passError } = await admin.from('wallet_passes').upsert({ member_id: member.id, venue_id: venue.id, provider: id, provider_class_id: issued.providerClassId, provider_object_id: issued.providerObjectId, last_synced_at: new Date().toISOString(), sync_error: null, updated_at: new Date().toISOString() }, { onConflict: 'member_id,provider' });
      if (passError) throw passError;
      Object.assign(saveLinks, issued.saveLinks);
    } catch (issueError) {
      failures.push(errorText(issueError, `${id} card could not be issued.`));
    }
  }
  return { saveLinks, walletSyncMessage: failures.length ? failures.join(' ') : null };
}

/** Pushes the ledger-derived balance and tier to every card the member holds. The ledger stays authoritative. */
export async function syncMemberWallet(memberId: string) {
  const admin = createSupabaseAdminClient();
  const { data: passes } = await admin.from('wallet_passes').select('*').eq('member_id', memberId);
  const enabled = new Set(enabledProviderIds());
  const syncable = (passes || []).filter(pass => enabled.has(pass.provider as WalletProviderId) && providerConfigured(pass.provider as WalletProviderId));
  if (!syncable.length) return { walletSynced: false, hasWalletPass: Boolean(passes?.length) };
  const { data: member, error } = await admin.from('members').select('*').eq('id', memberId).single();
  if (error || !member) return { walletSynced: false, hasWalletPass: true, walletSyncMessage: 'Action saved; member details could not be reloaded for pass sync.' };
  const [{ data: venue }, { data: tier }] = await Promise.all([
    admin.from('venues').select('balance_label').eq('id', member.venue_id).single(),
    admin.from('venue_tiers').select('name,benefits').eq('id', member.current_tier_id).single(),
  ]);
  const walletMember = memberWalletData(member, venue, tier);
  const failures: string[] = [];
  for (const pass of syncable) {
    const now = new Date().toISOString();
    try {
      await getWalletProvider(pass.provider as WalletProviderId).updateMember(walletMember, { classId: pass.provider_class_id, objectId: pass.provider_object_id });
      const { error: updateError } = await admin.from('wallet_passes').update({ last_synced_at: now, sync_error: null, updated_at: now }).eq('member_id', memberId).eq('provider', pass.provider);
      if (updateError) throw updateError;
    } catch (syncError) {
      const message = errorText(syncError, 'Wallet synchronization failed.');
      failures.push(message);
      await admin.from('wallet_passes').update({ sync_error: message, updated_at: now }).eq('member_id', memberId).eq('provider', pass.provider);
    }
  }
  return failures.length
    ? { walletSynced: false, hasWalletPass: true, walletSyncMessage: failures.join(' ') }
    : { walletSynced: true, hasWalletPass: true };
}

export const redeemSync = syncMemberWallet;
