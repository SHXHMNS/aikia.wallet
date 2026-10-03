import 'server-only';

import { GoogleAuth } from 'google-auth-library';
import { createSign } from 'node:crypto';
import type { IssuedPass, MemberWalletData, VenueWalletConfig, WalletProvider } from './types';

const API_ROOT = 'https://walletobjects.googleapis.com/walletobjects/v1';
const WALLET_SCOPE = 'https://www.googleapis.com/auth/wallet_object.issuer';
type JsonRecord = Record<string, unknown>;

function settings() {
  const issuerId = process.env.GOOGLE_WALLET_ISSUER_ID?.trim();
  const serviceJson = process.env.GOOGLE_WALLET_SERVICE_ACCOUNT_JSON;
  const appUrl = process.env.NEXT_PUBLIC_APP_URL;
  const fallbackLogo = process.env.GOOGLE_WALLET_PROGRAM_LOGO_URL;
  if (!issuerId || !serviceJson || !appUrl || !fallbackLogo) {
    throw new Error('Google Wallet is not configured. Set issuer, service-account JSON, app URL and a public HTTPS logo URL.');
  }
  const credentials = JSON.parse(serviceJson) as { client_email?: string; private_key?: string };
  if (!credentials.client_email || !credentials.private_key) {
    throw new Error('The Google service-account JSON must contain client_email and private_key.');
  }
  const logo = new URL(fallbackLogo);
  if (logo.protocol !== 'https:') throw new Error('Google Wallet program logo URL must use HTTPS.');
  return { issuerId, credentials: credentials as { client_email: string; private_key: string }, appUrl, fallbackLogo };
}

function safeSuffix(value: string) {
  const suffix = value.replace(/[^A-Za-z0-9._-]/g, '-');
  if (!suffix || suffix.length > 64) throw new Error('Invalid Google Wallet identifier suffix.');
  return suffix;
}

function localized(language: string, value: string) {
  return { defaultValue: { language, value } };
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

  async ensureVenueClass(venue: VenueWalletConfig): Promise<string> {
    const id = this.classId(venue);
    const logoUrl = venue.programLogoUrl || this.config.fallbackLogo;
    if (new URL(logoUrl).protocol !== 'https:') throw new Error('Google Wallet program logo URL must use HTTPS.');
    const body: JsonRecord = {
      id,
      issuerName: 'AIKIA.WALLET',
      programName: venue.name,
      programLogo: {
        sourceUri: { uri: logoUrl },
        contentDescription: localized('en-US', `${venue.name} logo`),
      },
      hexBackgroundColor: venue.brandColor,
      localizedIssuerName: localized('en-US', 'AIKIA.WALLET'),
      localizedProgramName: localized('en-US', venue.name),
      accountNameLabel: 'MEMBER',
      accountIdLabel: 'MEMBER ID',
      rewardsTierLabel: 'STATUS',
    };
    if (venue.heroImageUrl) {
      if (new URL(venue.heroImageUrl).protocol !== 'https:') throw new Error('Google Wallet hero image URL must use HTTPS.');
      body.heroImage = { sourceUri: { uri: venue.heroImageUrl }, contentDescription: localized('en-US', `${venue.name} venue artwork`) };
    }
    try {
      await this.request(`loyaltyClass/${encodeURIComponent(id)}`);
      await this.request(`loyaltyClass/${encodeURIComponent(id)}`, { method: 'PATCH', body: JSON.stringify(body) });
      return id;
    } catch (error) {
      if (!(error instanceof Error) || !error.message.startsWith('Google Wallet API 404:')) throw error;
    }
    body.reviewStatus = 'UNDER_REVIEW';
    try {
      await this.request('loyaltyClass', { method: 'POST', body: JSON.stringify(body) });
    } catch (error) {
      // A concurrent setup may have created the deterministic class ID first.
      if (!(error instanceof Error) || !error.message.startsWith('Google Wallet API 409:')) throw error;
    }
    return id;
  }

  private async ensureObject(venueClassId: string, member: MemberWalletData) {
    const id = this.objectId(member);
    try {
      await this.request(`loyaltyObject/${encodeURIComponent(id)}`);
      await this.request(`loyaltyObject/${encodeURIComponent(id)}`, {
        method: 'PATCH',
        body: JSON.stringify({
          accountName: member.fullName.slice(0, 20),
          accountId: member.publicCode.slice(0, 20),
          barcode: { type: 'QR_CODE', value: member.scanToken, alternateText: member.publicCode },
          loyaltyPoints: { label: member.balanceLabel.slice(0, 9), balance: { int: member.stampBalance } },
          textModulesData: this.memberModules(member),
        }),
      });
      return id;
    } catch (error) {
      if (!(error instanceof Error) || !error.message.startsWith('Google Wallet API 404:')) throw error;
    }
    const body = {
      id,
      classId: venueClassId,
      state: 'ACTIVE',
      accountName: member.fullName.slice(0, 20),
      accountId: member.publicCode.slice(0, 20),
      barcode: { type: 'QR_CODE', value: member.scanToken, alternateText: member.publicCode },
      loyaltyPoints: { label: member.balanceLabel.slice(0, 9), balance: { int: member.stampBalance } },
      textModulesData: this.memberModules(member),
    };
    try {
      await this.request('loyaltyObject', { method: 'POST', body: JSON.stringify(body) });
    } catch (error) {
      if (!(error instanceof Error) || !error.message.startsWith('Google Wallet API 409:')) throw error;
    }
    return id;
  }

  private signSaveJwt(objectId: string) {
    const { credentials, appUrl } = this.config;
    const origin = new URL(appUrl).hostname;
    const header = Buffer.from(JSON.stringify({ alg: 'RS256', typ: 'JWT' })).toString('base64url');
    const payload = Buffer.from(JSON.stringify({
      iss: credentials.client_email,
      aud: 'google',
      origins: [origin],
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
    const providerObjectId = await this.ensureObject(providerClassId, member);
    const jwt = this.signSaveJwt(providerObjectId);
    return { provider: this.id, providerClassId, providerObjectId, saveUrl: `https://pay.google.com/gp/v/save/${jwt}` };
  }

  private memberModules(member: MemberWalletData) {
    const benefits = member.tierBenefits.length ? member.tierBenefits.join(' · ') : 'Keep collecting coffees to unlock member benefits.';
    return [
      { id: 'member_tier', header: 'REWARDS TIER', body: member.tierName.slice(0, 500) },
      { id: 'tier_benefits', header: 'TIER BENEFITS', body: benefits.slice(0, 500) },
      { id: 'rewards_available', header: 'REWARDS READY', body: `${member.rewardsAvailable}` },
      { id: 'member_progress', header: 'LIFETIME ACTIONS', body: `${member.lifetimeActions}` },
    ];
  }

  async updateMember(member: MemberWalletData, providerObjectId: string): Promise<void> {
    if (!Number.isInteger(member.stampBalance) || member.stampBalance < 0) throw new Error('Wallet stamp balance must be a non-negative integer.');
    await this.request(`loyaltyObject/${encodeURIComponent(providerObjectId)}`, {
      method: 'PATCH',
      body: JSON.stringify({
        loyaltyPoints: { label: member.balanceLabel.slice(0, 9), balance: { int: member.stampBalance } },
        textModulesData: this.memberModules(member),
      }),
    });
  }
}

export function googleWalletConfigured() {
  return Boolean(
    process.env.GOOGLE_WALLET_ISSUER_ID &&
    process.env.GOOGLE_WALLET_SERVICE_ACCOUNT_JSON &&
    process.env.GOOGLE_WALLET_PROGRAM_LOGO_URL &&
    process.env.NEXT_PUBLIC_APP_URL,
  );
}
