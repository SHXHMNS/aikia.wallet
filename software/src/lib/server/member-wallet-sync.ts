import 'server-only';
import { createSupabaseAdminClient } from '@/lib/supabase/admin';
import { getWalletProvider } from '@/lib/wallet/provider';
import { googleWalletConfigured } from '@/lib/wallet/google';
import type { MemberWalletData } from '@/lib/wallet/types';

export async function syncMemberWallet(memberId: string) {
  const admin = createSupabaseAdminClient();
  const { data: pass } = await admin.from('wallet_passes').select('*').eq('member_id', memberId).maybeSingle();
  if (!pass || pass.provider !== 'google' || !googleWalletConfigured()) return { walletSynced: false, hasWalletPass: Boolean(pass) };
  const { data: member, error } = await admin.from('members').select('*').eq('id', memberId).single();
  if (error || !member) return { walletSynced: false, hasWalletPass: true, walletSyncMessage: 'Action saved; member details could not be reloaded for pass sync.' };
  const [{ data: venue }, { data: tier }] = await Promise.all([
    admin.from('venues').select('balance_label').eq('id', member.venue_id).single(),
    admin.from('venue_tiers').select('name,benefits').eq('id', member.current_tier_id).single(),
  ]);
  const walletMember: MemberWalletData = {
    id: member.id, venueId: member.venue_id, fullName: member.full_name, publicCode: member.public_code,
    scanToken: member.scan_token, stampBalance: member.stamp_balance, balanceLabel: venue?.balance_label || 'STAMPS',
    rewardsAvailable: member.rewards_available, lifetimeActions: member.lifetime_actions,
    tierName: tier?.name || 'Member', tierBenefits: tier?.benefits || [],
  };
  try {
    await getWalletProvider('google').updateMember(walletMember, pass.provider_object_id);
    const { error: updateError } = await admin.from('wallet_passes').update({ last_synced_at: new Date().toISOString(), sync_error: null, updated_at: new Date().toISOString() }).eq('member_id', memberId);
    if (updateError) throw updateError;
    return { walletSynced: true, hasWalletPass: true };
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Google Wallet synchronization failed.';
    await admin.from('wallet_passes').update({ sync_error: message, updated_at: new Date().toISOString() }).eq('member_id', memberId);
    return { walletSynced: false, hasWalletPass: true, walletSyncMessage: message };
  }
}

export const redeemSync = syncMemberWallet;
