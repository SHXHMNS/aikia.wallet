import 'server-only';
import { AppleWalletProvider, appleWalletConfigured } from './apple';
import { GoogleWalletProvider, googleWalletConfigured } from './google';
import { PassKitProvider, passkitConfigured } from './passkit';
import type { WalletEngine, WalletProvider, WalletProviderId } from './types';

/**
 * WALLET_ENGINE=passkit (default): PassKit issues the cards.
 * WALLET_ENGINE=direct: our own adapters, listed in WALLET_PROVIDERS (e.g. "google" or "google,apple").
 */
export function walletEngine(): WalletEngine {
  const engine = process.env.WALLET_ENGINE?.trim();
  if (engine === 'passkit' || engine === 'direct') return engine;
  if (engine) throw new Error(`Unsupported WALLET_ENGINE: ${engine}`);
  // Older deployments only set WALLET_PROVIDER=google.
  return process.env.WALLET_PROVIDER ? 'direct' : 'passkit';
}

export function enabledProviderIds(): WalletProviderId[] {
  if (walletEngine() === 'passkit') return ['passkit'];
  const list = (process.env.WALLET_PROVIDERS || process.env.WALLET_PROVIDER || 'google').split(',').map(id => id.trim()).filter(Boolean);
  return list.filter((id): id is WalletProviderId => id === 'google' || id === 'apple');
}

export function providerConfigured(id: WalletProviderId) {
  if (id === 'passkit') return passkitConfigured();
  if (id === 'google') return googleWalletConfigured();
  return appleWalletConfigured();
}

export function getWalletProvider(id: WalletProviderId): WalletProvider {
  if (id === 'passkit') return new PassKitProvider();
  if (id === 'google') return new GoogleWalletProvider();
  if (id === 'apple') return new AppleWalletProvider();
  throw new Error(`Unsupported wallet provider: ${id}`);
}

/** Providers that are both enabled by the engine setting and have credentials. */
export function activeProviderIds() {
  return enabledProviderIds().filter(providerConfigured);
}

export function walletStatus() {
  return {
    engine: walletEngine(),
    providers: Object.fromEntries(enabledProviderIds().map(id => [id, providerConfigured(id) ? 'configured' : 'missing_credentials'])),
    // Engines with credentials that are not switched on yet (ready for WALLET_ENGINE / WALLET_PROVIDERS).
    standby: (['passkit', 'google', 'apple'] as WalletProviderId[]).filter(id => !enabledProviderIds().includes(id) && providerConfigured(id)),
  };
}
