import type { WalletProvider } from './types';

/** Reserved provider seam. Apple Wallet APIs will be implemented in this adapter later. */
export class AppleWalletProvider implements WalletProvider {
  readonly id = 'apple' as const;

  private unavailable(): never {
    throw new Error('Apple Wallet provider is not implemented yet. Google Wallet is the active provider.');
  }

  async ensureVenueClass(_venue: Parameters<WalletProvider['ensureVenueClass']>[0]): Promise<string> { return this.unavailable(); }
  async issueMemberPass(_venue: Parameters<WalletProvider['issueMemberPass']>[0], _member: Parameters<WalletProvider['issueMemberPass']>[1]): ReturnType<WalletProvider['issueMemberPass']> { return this.unavailable(); }
  async updateMember(_member: Parameters<WalletProvider['updateMember']>[0], _providerObjectId: string): Promise<void> { return this.unavailable(); }
}
