/** `passkit` is a hosted engine that issues Google (and later Apple) cards; `google` / `apple` are our own direct adapters. */
export type WalletProviderId = 'google' | 'apple' | 'passkit';
/** The wallet app a customer saves the card into. */
export type WalletApp = 'google' | 'apple';
export type WalletEngine = 'passkit' | 'direct';

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
  /** Engine-side program reference, e.g. the PassKit program ID for this venue. */
  walletProgramId?: string | null;
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

export type SaveLinks = Partial<Record<WalletApp, string>>;

export type IssuedPass = {
  provider: WalletProviderId;
  providerClassId: string;
  providerObjectId: string;
  saveLinks: SaveLinks;
};

/** Identifiers stored in `wallet_passes` for an issued card. */
export type PassReference = { classId: string; objectId: string };

export interface WalletProvider {
  readonly id: WalletProviderId;
  ensureVenueClass(venue: VenueWalletConfig): Promise<string>;
  issueMemberPass(venue: VenueWalletConfig, member: MemberWalletData): Promise<IssuedPass>;
  updateMember(member: MemberWalletData, pass: PassReference): Promise<void>;
}
