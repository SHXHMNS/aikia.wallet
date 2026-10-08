import 'server-only';

import { passKitPerson, passKitSaveLinks, passKitTierId, passUrlBaseFor, signPassKitToken } from './passkit-core';
import type { IssuedPass, MemberWalletData, PassReference, SaveLinks, VenueLocation, VenueWalletConfig, WalletMessage, WalletProvider } from './types';

// Endpoints follow PassKit's Members & Loyalty API (docs.passkit.io/protocols/member, member.swagger.json).
const DEFAULT_API_BASE = 'https://api.pub1.passkit.io';
type JsonRecord = Record<string, unknown>;

function settings() {
  const apiKey = process.env.PASSKIT_API_KEY?.trim();
  const apiSecret = process.env.PASSKIT_API_SECRET?.trim();
  if (!apiKey || !apiSecret) throw new Error('PassKit is not configured. Set PASSKIT_API_KEY and PASSKIT_API_SECRET.');
  const apiBase = new URL(process.env.PASSKIT_API_BASE_URL?.trim() || DEFAULT_API_BASE);
  if (apiBase.protocol !== 'https:') throw new Error('PASSKIT_API_BASE_URL must use HTTPS.');
  let tierIds: Record<string, string> = {};
  if (process.env.PASSKIT_TIER_IDS) {
    try { tierIds = JSON.parse(process.env.PASSKIT_TIER_IDS) as Record<string, string>; }
    catch { throw new Error('PASSKIT_TIER_IDS must be JSON, for example {"Ink":"ink"}.'); }
  }
  return {
    apiKey, apiSecret, tierIds,
    apiBase: apiBase.origin,
    passBase: passUrlBaseFor(apiBase.origin, process.env.PASSKIT_PASS_URL_BASE),
    defaultProgramId: process.env.PASSKIT_PROGRAM_ID?.trim() || null,
    appleEnabled: process.env.PASSKIT_APPLE_ENABLED === 'true',
  };
}

export class PassKitProvider implements WalletProvider {
  readonly id = 'passkit' as const;

  private config = settings();

  private async request<T extends JsonRecord>(path: string, init?: RequestInit): Promise<T> {
    const response = await fetch(`${this.config.apiBase}/${path}`, {
      ...init,
      cache: 'no-store',
      headers: { authorization: signPassKitToken(this.config.apiKey, this.config.apiSecret), 'content-type': 'application/json', ...init?.headers },
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
    return passKitTierId(tierName, this.config.tierIds);
  }

  saveLinks(passId: string): SaveLinks {
    return passKitSaveLinks(this.config.passBase, passId, this.config.appleEnabled);
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
          person: passKitPerson(member.fullName),
          metaData: this.metaData(member),
        }),
      });
      if (!created.id) throw new Error('PassKit did not return a member ID.');
      passId = created.id;
    }
    return { provider: this.id, providerClassId: programId, providerObjectId: passId, saveLinks: this.saveLinks(passId) };
  }

  /** Applies a change to the pass template of every tier in the venue's program. */
  private async editTierTemplates(venue: VenueWalletConfig, tierNames: string[], edit: (template: Record<string, unknown>) => Record<string, unknown>) {
    const programId = this.programId(venue);
    for (const name of tierNames) {
      let tier: { passTemplateId?: string };
      try { tier = await this.request(`members/tier/${encodeURIComponent(programId)}/${encodeURIComponent(this.tierId(name))}`); } catch { continue; }
      if (!tier.passTemplateId) continue;
      const { template } = await this.request<{ template: Record<string, unknown> }>(`template/data/${tier.passTemplateId}`);
      await this.request('template', { method: 'PUT', body: JSON.stringify(edit(template)) });
    }
  }

  async syncVenueLocations(venue: VenueWalletConfig, locations: VenueLocation[], tierNames: string[]): Promise<void> {
    await this.editTierTemplates(venue, tierNames, template => ({
      ...template,
      locations: locations.slice(0, 10).map((l, position) => ({ name: l.label, lat: l.lat, lon: l.lng, lockScreenMessage: l.lockScreenMessage || `${venue.name} is nearby. Show your card for your stamp.`, position })),
    }));
  }

  /** PassKit: updates the card's "Member news" field for everyone (Apple shows it on the lock screen). */
  async broadcastMessage(venue: VenueWalletConfig, message: WalletMessage, tierNames: string[]): Promise<void> {
    await this.editTierTemplates(venue, tierNames, template => {
      const data = template.data as { dataFields?: { uniqueName: string; defaultValue?: string }[] } | undefined;
      const dataFields = (data?.dataFields || []).map(f => f.uniqueName === 'custom.latest' ? { ...f, defaultValue: `${message.header}: ${message.body}`.slice(0, 300) } : f);
      return { ...template, data: { ...data, dataFields } };
    });
  }

  async messageMember(): Promise<boolean> {
    return false;
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
      body: JSON.stringify({ id: pass.objectId, programId: pass.classId, tierId, operation: 'OPERATION_PATCH', person: passKitPerson(member.fullName), metaData: this.metaData(member) }),
    });
  }
}

export function passkitConfigured() {
  return Boolean(process.env.PASSKIT_API_KEY && process.env.PASSKIT_API_SECRET);
}
