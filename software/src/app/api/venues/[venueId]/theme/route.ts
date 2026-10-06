import { NextResponse } from 'next/server';
import { getVenueRole } from '@/lib/server/venue-access';
import { venueWalletConfig } from '@/lib/server/member-wallet-sync';
import { activeProviderIds, getWalletProvider } from '@/lib/wallet/provider';

type Context = { params: Promise<{ venueId: string }> };
const hex = /^#[0-9a-fA-F]{6}$/;
function optionalHttps(value: unknown) {
  if (value === null || value === '') return null;
  if (typeof value !== 'string') throw new Error('Image URLs must be strings.');
  const url = new URL(value);
  if (url.protocol !== 'https:') throw new Error('Logo and hero artwork must use HTTPS.');
  return url.toString();
}

export async function PATCH(request: Request, { params }: Context) {
  const { venueId } = await params;
  const access = await getVenueRole(venueId);
  if (!access) return NextResponse.json({ error: 'Venue access required.' }, { status: 401 });
  if (access.role === 'staff') return NextResponse.json({ error: 'Owner or admin access required.' }, { status: 403 });
  let body: Record<string, unknown>;
  try { body = await request.json(); } catch { return NextResponse.json({ error: 'Expected JSON.' }, { status: 400 }); }
  if (typeof body.name !== 'string' || body.name.trim().length < 2 || body.name.trim().length > 80) return NextResponse.json({ error: 'Venue name must be 2–80 characters.' }, { status: 400 });
  if (typeof body.brandColor !== 'string' || !hex.test(body.brandColor)) return NextResponse.json({ error: 'Choose a valid six-digit hex card color.' }, { status: 400 });
  if (body.backgroundColor !== null && body.backgroundColor !== undefined && (typeof body.backgroundColor !== 'string' || !hex.test(body.backgroundColor))) return NextResponse.json({ error: 'Choose a valid six-digit hex dashboard color.' }, { status: 400 });
  let logoUrl: string | null; let heroUrl: string | null;
  try { logoUrl = optionalHttps(body.programLogoUrl); heroUrl = optionalHttps(body.heroImageUrl); }
  catch (error) { return NextResponse.json({ error: error instanceof Error ? error.message : 'Invalid image URL.' }, { status: 400 }); }
  const businessTypes = ['cafe','restaurant','retail','salon','fitness','hotel','entertainment','other'];
  const businessType = typeof body.businessType === 'string' && businessTypes.includes(body.businessType) ? body.businessType : 'cafe';
  const actionLabel = typeof body.actionLabel === 'string' && body.actionLabel.trim().length >= 2 && body.actionLabel.trim().length <= 24 ? body.actionLabel.trim() : 'coffee purchase';
  const balanceLabel = typeof body.balanceLabel === 'string' && body.balanceLabel.trim().length >= 2 && body.balanceLabel.trim().length <= 9 ? body.balanceLabel.trim().toUpperCase() : 'STAMPS';
  const rewardTarget = Number(body.rewardTarget ?? 9);
  const rewardName = typeof body.rewardName === 'string' && body.rewardName.trim().length > 0 && body.rewardName.trim().length <= 80 ? body.rewardName.trim() : 'Member reward';
  if (!Number.isInteger(rewardTarget) || rewardTarget < 1 || rewardTarget > 1000) return NextResponse.json({ error: 'Reward target must be a whole number between 1 and 1000.' }, { status: 400 });
  const walletProgramId = typeof body.walletProgramId === 'string' && body.walletProgramId.trim() ? body.walletProgramId.trim() : null;
  if (walletProgramId && !/^[A-Za-z0-9_-]{1,64}$/.test(walletProgramId)) return NextResponse.json({ error: 'The wallet program ID can only contain letters, numbers, dashes and underscores.' }, { status: 400 });
  const values = {
    name: body.name.trim(), brand_color: body.brandColor, background_color: body.backgroundColor || null,
    program_logo_url: logoUrl, hero_image_url: heroUrl, business_type: businessType,
    action_label: actionLabel, balance_label: balanceLabel, reward_target: rewardTarget, reward_name: rewardName,
    wallet_program_id: walletProgramId,
    tier_basis: body.tierBasis === 'spend' ? 'spend' : 'actions',
  };
  const { data: venue, error } = await access.supabase.from('venues').update(values).eq('id', venueId).select('id,name,slug,business_type,action_label,balance_label,reward_target,reward_name,brand_color,background_color,program_logo_url,hero_image_url,wallet_program_id,tier_basis').single();
  if (error) return NextResponse.json({ error: error.message }, { status: 400 });
  // Tier basis may have changed: re-evaluate every member's tier.
  const { error: recomputeError } = await access.supabase.rpc('recompute_member_tiers', { p_venue_id: venueId });
  if (recomputeError) return NextResponse.json({ error: recomputeError.message }, { status: 400 });
  const providers = activeProviderIds();
  let walletSynced = providers.length > 0; let walletSyncMessage: string | undefined;
  for (const id of providers) {
    try { await getWalletProvider(id).ensureVenueClass(venueWalletConfig(venue)); }
    catch (syncError) { walletSynced = false; walletSyncMessage = syncError instanceof Error ? syncError.message : 'Wallet program sync failed.'; }
  }
  return NextResponse.json({ venue, walletSynced, walletSyncMessage });
}
