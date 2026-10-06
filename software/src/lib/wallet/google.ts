import 'server-only';

import { GoogleAuth } from 'google-auth-library';
import { createSign } from 'node:crypto';
import { platform } from '@/config/platform';
import { googleCardLayout, googleTextModules, tierArtSlug } from './google-card';
import type { IssuedPass, MemberWalletData, PassReference, VenueWalletConfig, WalletProvider } from './types';

const API_ROOT = 'https://walletobjects.googleapis.com/walletobjects/v1';
const WALLET_SCOPE = 'https://www.googleapis.com/auth/wallet_object.issuer';
type JsonRecord = Record<string, unknown>;

function settings() {
  const issuerId = process.env.GOOGLE_WALLET_ISSUER_ID?.trim();
  const serviceJson = process.env.GOOGLE_WALLET_SERVICE_ACCOUNT_JSON;
  const appUrl = process.env.NEXT_PUBLIC_APP_URL;
  if (!issuerId || !serviceJson || !appUrl) {
    throw new Error('Google Wallet is not configured. Set GOOGLE_WALLET_ISSUER_ID, GOOGLE_WALLET_SERVICE_ACCOUNT_JSON and NEXT_PUBLIC_APP_URL.');
  }
  const credentials = JSON.parse(serviceJson) as { client_email?: string; private_key?: string };
  if (!credentials.client_email || !credentials.private_key) {
    throw new Error('The Google service-account JSON must contain client_email and private_key.');
  }
  // Card artwork is served by this app from public/brand unless a venue supplies its own HTTPS images.
  const brandBase = `${new URL(appUrl).origin}/brand`;
  const fallbackLogo = process.env.GOOGLE_WALLET_PROGRAM_LOGO_URL || `${brandBase}/aikia-wallet-program-logo.png`;
  if (new URL(fallbackLogo).protocol !== 'https:') throw new Error('Google Wallet program logo URL must use HTTPS.');
  return { issuerId, credentials: credentials as { client_email: string; private_key: string }, appUrl, fallbackLogo, brandBase };
}

function safeSuffix(value: string) {
  const suffix = value.replace(/[^A-Za-z0-9._-]/g, '-');
  if (!suffix || suffix.length > 64) throw new Error('Invalid Google Wallet identifier suffix.');
  return suffix;
}

function localized(language: string, value: string) {
  return { defaultValue: { language, value } };
}

function image(uri: string, description: string) {
  if (new URL(uri).protocol !== 'https:') throw new Error('Google Wallet images must use HTTPS.');
  return { sourceUri: { uri }, contentDescription: localized('en-US', description) };
}

export class GoogleWalletProvider implements WalletProvider {
  readonly id = 'google' as const;

  private config = settings();
  private auth = new GoogleAuth({ credentials: JSON.parse(process.env.GOOGLE_WALLET_SERVICE_ACCOUNT_JSON!), scopes: [WALLET_SCOPE] });

  private async request<T extends JsonRecord>(path: string, init?: RequestInit): Promise<T> {
    const client = await this.auth.getClient();
    const token = await client.getAccessToken();
    if (!token.token) throw new Error('Google Wallet authentication did not return an access token.');
    const response = await fetch(`${API_ROOT}/${path}`, {
      ...init,
      cache: 'no-store',
      headers: { authorization: `Bearer ${token.token}`, 'content-type': 'application/json', ...init?.headers },
    });
    if (!response.ok) {
      const body = await response.text();
      throw new Error(`Google Wallet API ${response.status}: ${body.slice(0, 700)}`);
    }
    return response.status === 204 ? ({} as T) : (await response.json()) as T;
  }

  classId(venue: VenueWalletConfig) {
    return `${this.config.issuerId}.aikia_${safeSuffix(venue.id)}`;
  }

  objectId(member: MemberWalletData) {
    return `${this.config.issuerId}.member_${safeSuffix(member.id)}`;
  }

  /** Tier banner: the venue's own artwork if set, otherwise the AIKIA aurora art for that tier. */
  private heroFor(venue: VenueWalletConfig | null, tierName: string) {
    if (venue?.heroImageUrl) return venue.heroImageUrl;
    return `${this.config.brandBase}/card-hero-${tierArtSlug(tierName)}.png`;
  }

  private classBody(venue: VenueWalletConfig): JsonRecord {
    const id = this.classId(venue);
    return {
      id,
      issuerName: platform.name,
      localizedIssuerName: localized('en-US', platform.name),
      programName: venue.name,
      localizedProgramName: localized('en-US', venue.name),
      programLogo: image(venue.programLogoUrl || this.config.fallbackLogo, `${venue.name} logo`),
      heroImage: image(this.heroFor(venue, 'Ink'), `${venue.name} membership card`),
      hexBackgroundColor: venue.brandColor,
      accountNameLabel: 'MEMBER',
      accountIdLabel: 'MEMBER CODE',
      classTemplateInfo: googleCardLayout,
      multipleDevicesAndHoldersAllowedStatus: 'ONE_USER_ALL_DEVICES',
    };
  }

  async ensureVenueClass(venue: VenueWalletConfig): Promise<string> {
    const id = this.classId(venue);
    const body = this.classBody(venue);
    try {
      await this.request(`loyaltyClass/${encodeURIComponent(id)}`);
      // Google requires class updates to be re-submitted for review.
      await this.request(`loyaltyClass/${encodeURIComponent(id)}`, { method: 'PATCH', body: JSON.stringify({ ...body, reviewStatus: 'UNDER_REVIEW' }) });
      return id;
    } catch (error) {
      if (!(error instanceof Error) || !error.message.startsWith('Google Wallet API 404:')) throw error;
    }
    try {
      await this.request('loyaltyClass', { method: 'POST', body: JSON.stringify({ ...body, reviewStatus: 'UNDER_REVIEW' }) });
    } catch (error) {
      // A concurrent setup may have created the deterministic class ID first.
      if (!(error instanceof Error) || !error.message.startsWith('Google Wallet API 409:')) throw error;
    }
    return id;
  }

  private memberFields(member: MemberWalletData, venue: VenueWalletConfig | null) {
    return {
      accountName: member.fullName.slice(0, 40),
      accountId: member.publicCode.slice(0, 20),
      barcode: { type: 'QR_CODE', value: member.scanToken, alternateText: member.publicCode },
      loyaltyPoints: { label: member.balanceLabel.slice(0, 9), balance: { int: member.stampBalance } },
      textModulesData: googleTextModules(member),
      heroImage: image(this.heroFor(venue, member.tierName), `${member.tierName} member card`),
    };
  }

  private async ensureObject(venue: VenueWalletConfig, venueClassId: string, member: MemberWalletData) {
    const id = this.objectId(member);
    try {
      await this.request(`loyaltyObject/${encodeURIComponent(id)}`);
      await this.request(`loyaltyObject/${encodeURIComponent(id)}`, { method: 'PATCH', body: JSON.stringify(this.memberFields(member, venue)) });
      return id;
    } catch (error) {
      if (!(error instanceof Error) || !error.message.startsWith('Google Wallet API 404:')) throw error;
    }
    try {
      await this.request('loyaltyObject', { method: 'POST', body: JSON.stringify({ id, classId: venueClassId, state: 'ACTIVE', ...this.memberFields(member, venue) }) });
    } catch (error) {
      if (!(error instanceof Error) || !error.message.startsWith('Google Wallet API 409:')) throw error;
    }
    return id;
  }

  private signSaveJwt(objectId: string) {
    const { credentials, appUrl } = this.config;
    const header = Buffer.from(JSON.stringify({ alg: 'RS256', typ: 'JWT' })).toString('base64url');
    const payload = Buffer.from(JSON.stringify({
      iss: credentials.client_email,
      aud: 'google',
      origins: [new URL(appUrl).origin],
      typ: 'savetowallet',
      payload: { loyaltyObjects: [{ id: objectId }] },
    })).toString('base64url');
    const unsigned = `${header}.${payload}`;
    const signer = createSign('RSA-SHA256');
    signer.update(unsigned);
    signer.end();
    return `${unsigned}.${signer.sign(credentials.private_key).toString('base64url')}`;
  }

  async issueMemberPass(venue: VenueWalletConfig, member: MemberWalletData): Promise<IssuedPass> {
    const providerClassId = await this.ensureVenueClass(venue);
    const providerObjectId = await this.ensureObject(venue, providerClassId, member);
    const jwt = this.signSaveJwt(providerObjectId);
    return { provider: this.id, providerClassId, providerObjectId, saveLinks: { google: `https://pay.google.com/gp/v/save/${jwt}` } };
  }

  async updateMember(member: MemberWalletData, pass: PassReference): Promise<void> {
    if (!Number.isInteger(member.stampBalance) || member.stampBalance < 0) throw new Error('Wallet stamp balance must be a non-negative integer.');
    const { heroImage, loyaltyPoints, textModulesData } = this.memberFields(member, null);
    await this.request(`loyaltyObject/${encodeURIComponent(pass.objectId)}`, {
      method: 'PATCH',
      body: JSON.stringify({ loyaltyPoints, textModulesData, heroImage }),
    });
  }
}

export function googleWalletConfigured() {
  return Boolean(process.env.GOOGLE_WALLET_ISSUER_ID && process.env.GOOGLE_WALLET_SERVICE_ACCOUNT_JSON && process.env.NEXT_PUBLIC_APP_URL);
}
