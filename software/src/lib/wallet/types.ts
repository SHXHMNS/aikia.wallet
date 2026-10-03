export type WalletProviderId = 'google' | 'apple';

export type VenueWalletConfig = {
  id: string;
  name: string;
  slug: string;
  brandColor: string;
  backgroundColor?: string | null;
  programLogoUrl?: string | null;
  heroImageUrl?: string | null;
  balanceLabel?: string | null;
  actionLabel?: string | null;
};

export type MemberWalletData = {
  id: string;
  venueId: string;
  fullName: string;
  publicCode: string;
  scanToken: string;
  stampBalance: number;
  balanceLabel: string;
  rewardsAvailable: number;
  lifetimeActions: number;
  tierName: string;
  tierBenefits: string[];
};

export type IssuedPass = {
  provider: WalletProviderId;
  providerClassId: string;
  providerObjectId: string;
  saveUrl: string;
};

export interface WalletProvider {
  readonly id: WalletProviderId;
  ensureVenueClass(venue: VenueWalletConfig): Promise<string>;
  issueMemberPass(venue: VenueWalletConfig, member: MemberWalletData): Promise<IssuedPass>;
  updateMember(member: MemberWalletData, providerObjectId: string): Promise<void>;
}
