import 'server-only';
import { walletEngine } from '@/lib/wallet/provider';

export type SetupItem = { key: string; ready: boolean; where: string; required: boolean };

/** Which settings are present (never their values), with where each one comes from. */
export function setupStatus(): SetupItem[] {
  const has = (name: string) => Boolean(process.env[name]?.trim());
  const items: SetupItem[] = [
    { key: 'NEXT_PUBLIC_SUPABASE_URL', ready: has('NEXT_PUBLIC_SUPABASE_URL'), where: 'Supabase → Connect → Project URL', required: true },
    { key: 'NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY', ready: has('NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY') || has('NEXT_PUBLIC_SUPABASE_ANON_KEY'), where: 'Supabase → Project Settings → API Keys → Publishable key', required: true },
    { key: 'SUPABASE_SECRET_KEY', ready: has('SUPABASE_SECRET_KEY') || has('SUPABASE_SERVICE_ROLE_KEY'), where: 'Supabase → Project Settings → API Keys → Secret key', required: true },
    { key: 'NEXT_PUBLIC_APP_URL', ready: has('NEXT_PUBLIC_APP_URL'), where: 'The public address of this app', required: true },
    { key: 'JOIN_RATE_LIMIT_SECRET', ready: has('JOIN_RATE_LIMIT_SECRET'), where: 'Any long random text (Terminal: openssl rand -base64 32)', required: true },
    { key: 'CRON_SECRET', ready: has('CRON_SECRET'), where: 'Any long random text; protects the daily card-sync retry', required: false },
    { key: 'PLATFORM_ADMIN_EMAILS', ready: has('PLATFORM_ADMIN_EMAILS'), where: 'Your own email(s), comma-separated, to open /platform', required: false },
  ];
  if (walletEngine() === 'passkit') {
    items.push(
      { key: 'PASSKIT_API_KEY', ready: has('PASSKIT_API_KEY'), where: 'PassKit → Developer Tools → REST credentials', required: true },
      { key: 'PASSKIT_API_SECRET', ready: has('PASSKIT_API_SECRET'), where: 'PassKit → Developer Tools → REST credentials', required: true },
      { key: 'PASSKIT_PROGRAM_ID', ready: has('PASSKIT_PROGRAM_ID'), where: 'PassKit → your program → settings (or set per venue in Brand & tiers)', required: false },
    );
  } else {
    items.push(
      { key: 'GOOGLE_WALLET_ISSUER_ID', ready: has('GOOGLE_WALLET_ISSUER_ID'), where: 'Google Pay & Wallet Console → Google Wallet API', required: true },
      { key: 'GOOGLE_WALLET_SERVICE_ACCOUNT_JSON', ready: has('GOOGLE_WALLET_SERVICE_ACCOUNT_JSON'), where: 'Google Cloud → service account → JSON key (one line)', required: true },
      { key: 'GOOGLE_WALLET_PROGRAM_LOGO_URL', ready: has('GOOGLE_WALLET_PROGRAM_LOGO_URL'), where: '<app address>/brand/aikia-wallet-program-logo.png', required: true },
    );
  }
  return items;
}
