import 'server-only';

import { createHmac } from 'node:crypto';
import type { IssuedPass, MemberWalletData, PassReference, SaveLinks, VenueWalletConfig, WalletProvider } from './types';

// Endpoints follow PassKit's Members & Loyalty API (docs.passkit.io/protocols/member, member.swagger.json).
const DEFAULT_API_BASE = 'https://api.pub1.passkit.io';
type JsonRecord = Record<string, unknown>;

function settings() {
  const apiKey = process.env.PASSKIT_API_KEY?.trim();
  const apiSecret = process.env.PASSKIT_API_SECRET?.trim();
  if (!apiKey || !apiSecret) throw new Error('PassKit is not configured. Set PASSKIT_API_KEY and PASSKIT_API_SECRET.');
  const apiBase = new URL(process.env.PASSKIT_API_BASE_URL?.trim() || DEFAULT_API_BASE);
  if (apiBase.protocol !== 'https:') throw new Error('PASSKIT_API_BASE_URL must use HTTPS.');
  // api.pub1.passkit.io (EU) serves passes from pub1.pskt.io; api.pub2 (USA) from pub2.pskt.io.
  const region = apiBase.hostname.match(/^api\.(pub\d+)\./)?.[1] || 'pub1';
  const passBase = new URL(process.env.PASSKIT_PASS_URL_BASE?.trim() || `https://${region}.pskt.io/`);
  let tierIds: Record<string, string> = {};
  if (process.env.PASSKIT_TIER_IDS) {
    try { tierIds = JSON.parse(process.env.PASSKIT_TIER_IDS) as Record<string, string>; }
    catch { throw new Error('PASSKIT_TIER_IDS must be JSON, for example {"Ink":"ink"}.'); }
  }
  return {
    apiKey, apiSecret, tierIds,
    apiBase: apiBase.origin,
    passBase: passBase.toString().endsWith('/') ? passBase.toString() : `${passBase}/`,
    defaultProgramId: process.env.PASSKIT_PROGRAM_ID?.trim() || null,
    appleEnabled: process.env.PASSKIT_APPLE_ENABLED === 'true',
  };
}

function base64url(value: string | Buffer) {
  return Buffer.from(value).toString('base64url');
}

/** Short-lived HS256 JWT: `uid` is the API key, signed with the API secret. */
function signToken(apiKey: string, apiSecret: string) {
  const now = Math.floor(Date.now() / 1000);
  const unsigned = `${base64url(JSON.stringify({ alg: 'HS256', typ: 'JWT' }))}.${base64url(JSON.stringify({ uid: apiKey, iat: now, exp: now + 60 }))}`;
  return `${unsigned}.${createHmac('sha256', apiSecret).update(unsigned).digest('base64url')}`;
}

function slug(value: string) {
  return value.trim().toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

export class PassKitProvider implements WalletProvider {
  readonly id = 'passkit' as const;

  private config = settings();

  private async request<T extends JsonRecord>(path: string, init?: RequestInit): Promise<T> {
    const response = await fetch(`${this.config.apiBase}/${path}`, {
      ...init,
      cache: 'no-store',
      headers: { authorization: signToken(this.config.apiKey, this.config.apiSecret), 'content-type': 'application/json', ...init?.headers },
    });
    if (!response.ok) {
      const body = await response.text();
      throw new Error(`PassKit API ${response.status}: ${body.slice(0, 700)}`);
    }
    const text = await response.text();
    return (text ? JSON.parse(text) : {}) as T;
  }

  programId(venue: VenueWalletConfig) {
    const id = venue.walletProgramId?.trim() || this.config.defaultProgramId;
    if (!id) throw new Error('No PassKit program is linked to this venue. Add its PassKit program ID in Brand & tiers, or set PASSKIT_PROGRAM_ID.');
    return id;
  }

  /** PassKit tier IDs default to the slug of our tier name ("Ink" → "ink"); PASSKIT_TIER_IDS can override. */
  tierId(tierName: string) {
    return this.config.tierIds[tierName] || slug(tierName);
  }

  saveLinks(passId: string): SaveLinks {
    const url = `${this.config.passBase}${encodeURIComponent(passId)}`;
    return this.config.appleEnabled ? { google: `${url}.gpay`, apple: `${url}.pkpass` } : { google: `${url}.gpay` };
  }

  /** Confirms the venue's program exists. Card design and tiers are managed in the PassKit portal. */
  async ensureVenueClass(venue: VenueWalletConfig): Promise<string> {
    const id = this.programId(venue);
    await this.request(`members/program/${encodeURIComponent(id)}`);
    return id;
  }

  private metaData(member: MemberWalletData) {
    return {
      memberCode: member.publicCode,
      tierName: member.tierName,
      tierBenefits: member.tierBenefits.join(' · ') || 'Keep collecting to unlock member benefits.',
      rewardsAvailable: String(member.rewardsAvailable),
      lifetimeActions: String(member.lifetimeActions),
      balanceLabel: member.balanceLabel,
    };
  }

  private async findByExternalId(programId: string, externalId: string) {
    try {
      const found = await this.request<{ id?: string }>(`members/member/externalId/${encodeURIComponent(programId)}/${encodeURIComponent(externalId)}`);
      return found.id || null;
    } catch (error) {
      if (error instanceof Error && error.message.startsWith('PassKit API 404:')) return null;
      throw error;
    }
  }

  async issueMemberPass(venue: VenueWalletConfig, member: MemberWalletData): Promise<IssuedPass> {
    const programId = this.programId(venue);
    // externalId is our member UUID, so a retried issue finds the existing PassKit member instead of duplicating it.
    let passId = await this.findByExternalId(programId, member.id);
    if (passId) {
      await this.updateMember(member, { classId: programId, objectId: passId });
    } else {
      const created = await this.request<{ id?: string }>('members/member', {
        method: 'POST',
        body: JSON.stringify({
          programId,
          tierId: this.tierId(member.tierName),
          externalId: member.id,
          points: member.stampBalance,
          person: { displayName: member.fullName.slice(0, 120) },
          metaData: this.metaData(member),
        }),
      });
      if (!created.id) throw new Error('PassKit did not return a member ID.');
      passId = created.id;
    }
    return { provider: this.id, providerClassId: programId, providerObjectId: passId, saveLinks: this.saveLinks(passId) };
  }

  async updateMember(member: MemberWalletData, pass: PassReference): Promise<void> {
    if (!Number.isInteger(member.stampBalance) || member.stampBalance < 0) throw new Error('Wallet stamp balance must be a non-negative integer.');
    const tierId = this.tierId(member.tierName);
    // Points go through points/set because a PATCH update ignores a zero balance after redemption.
    await this.request('members/member/points/set', {
      method: 'PUT',
      body: JSON.stringify({ id: pass.objectId, points: member.stampBalance, resetPoints: member.stampBalance === 0, tierId }),
    });
    await this.request('members/member', {
      method: 'PUT',
      body: JSON.stringify({ id: pass.objectId, programId: pass.classId, tierId, operation: 'OPERATION_PATCH', metaData: this.metaData(member) }),
    });
  }
}

export function passkitConfigured() {
  return Boolean(process.env.PASSKIT_API_KEY && process.env.PASSKIT_API_SECRET);
}
