import { createHmac } from 'node:crypto';

// Pure PassKit helpers (no server-only import) so they can be unit-tested with node --test.

function base64url(value: string | Buffer) {
  return Buffer.from(value).toString('base64url');
}

/** Short-lived HS256 JWT: `uid` is the API key, signed with the API secret. */
export function signPassKitToken(apiKey: string, apiSecret: string, now = Math.floor(Date.now() / 1000)) {
  const unsigned = `${base64url(JSON.stringify({ alg: 'HS256', typ: 'JWT' }))}.${base64url(JSON.stringify({ uid: apiKey, iat: now, exp: now + 60 }))}`;
  return `${unsigned}.${createHmac('sha256', apiSecret).update(unsigned).digest('base64url')}`;
}

/** api.pub1.passkit.io (EU) serves passes from pub1.pskt.io; api.pub2 (USA) from pub2.pskt.io. */
export function passUrlBaseFor(apiBase: string, override?: string | null) {
  const region = new URL(apiBase).hostname.match(/^api\.(pub\d+)\./)?.[1] || 'pub1';
  const base = new URL(override?.trim() || `https://${region}.pskt.io/`).toString();
  return base.endsWith('/') ? base : `${base}/`;
}

/** Direct "add to wallet" links: `.gpay` opens Google Wallet, `.pkpass` opens Apple Wallet. */
export function passKitSaveLinks(passBase: string, passId: string, appleEnabled: boolean) {
  const url = `${passBase}${encodeURIComponent(passId)}`;
  return appleEnabled ? { google: `${url}.gpay`, apple: `${url}.pkpass` } : { google: `${url}.gpay` };
}

/** PassKit tier IDs default to the slug of our tier name ("Ink" → "ink"); an override map can replace them. */
export function passKitTierId(tierName: string, overrides: Record<string, string> = {}) {
  return overrides[tierName] || tierName.trim().toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}
