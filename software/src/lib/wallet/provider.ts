import 'server-only';
import { AppleWalletProvider } from './apple';
import { GoogleWalletProvider } from './google';
import type { WalletProvider, WalletProviderId } from './types';

export function getWalletProvider(id = (process.env.WALLET_PROVIDER || 'google') as WalletProviderId): WalletProvider {
  if (id === 'google') return new GoogleWalletProvider();
  if (id === 'apple') return new AppleWalletProvider();
  throw new Error(`Unsupported wallet provider: ${id}`);
}
