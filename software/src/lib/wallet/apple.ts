import type { IssuedPass, MemberWalletData, PassReference, VenueLocation, VenueWalletConfig, WalletMessage, WalletProvider } from './types';

/** Reserved direct-engine seam. While on PassKit, Apple cards come from PassKit once the Apple certificate is uploaded there. */
export class AppleWalletProvider implements WalletProvider {
  readonly id = 'apple' as const;

  private unavailable(): never {
    throw new Error('The direct Apple Wallet adapter is not implemented yet.');
  }

  async ensureVenueClass(_venue: VenueWalletConfig): Promise<string> { return this.unavailable(); }
  async issueMemberPass(_venue: VenueWalletConfig, _member: MemberWalletData): Promise<IssuedPass> { return this.unavailable(); }
  async updateMember(_member: MemberWalletData, _pass: PassReference): Promise<void> { return this.unavailable(); }
  async syncVenueLocations(_venue: VenueWalletConfig, _locations: VenueLocation[], _tiers: string[]): Promise<void> { return this.unavailable(); }
  async broadcastMessage(_venue: VenueWalletConfig, _message: WalletMessage, _tiers: string[]): Promise<void> { return this.unavailable(); }
  async messageMember(_pass: PassReference, _message: WalletMessage): Promise<boolean> { return this.unavailable(); }
}

export function appleWalletConfigured() {
  return false;
}
