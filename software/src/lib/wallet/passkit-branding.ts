import 'server-only';
import { signPassKitToken } from './passkit-core';

// Applies the AIKIA card design to the PassKit membership program's Google Wallet designs:
// metallic Ink / Chrome / Pink art (made in Canva, files in public/brand), colours, card copy and the
// extra fields our app fills in (credit balance and the member's private "My card" link).
// Apple designs are left alone until the Apple certificate is uploaded to PassKit.

const programName = 'AIKIA Members Club';
const cardName = 'Members Club';
const organizationName = 'AIKIA';

/** Tier ID → metallic card colours and its artwork in public/brand. */
const tiers: Record<string, { backgroundColor: string; labelColor: string; textColor: string; hero: string; richHero: string }> = {
  ink: { backgroundColor: '#14111F', labelColor: '#B9BDC9', textColor: '#ECEEF5', hero: 'card-hero-ink.png', richHero: 'card-rich-ink.png' },
  chrome: { backgroundColor: '#C9CEDB', labelColor: '#3A3646', textColor: '#14111F', hero: 'card-hero-chrome.png', richHero: 'card-rich-chrome.png' },
  pink: { backgroundColor: '#DF215F', labelColor: '#FFE3EE', textColor: '#FFFFFF', hero: 'card-hero-pink.png', richHero: 'card-rich-pink.png' },
  membership: { backgroundColor: '#14111F', labelColor: '#B9BDC9', textColor: '#ECEEF5', hero: 'card-hero-ink.png', richHero: 'card-rich-ink.png' },
};
// Template fields that loyalty cards don't use (they showed as "missing: universal.expiryDate" / "empty value").
const removedFields = new Set(['universal.expiryDate', 'meta.notification']);

type Field = { uniqueName: string; label?: string; defaultValue?: string; appleWalletFieldRenderOptions?: Record<string, unknown>; [key: string]: unknown };
type TemplateData = { dataFields?: Field[]; dataCollectionPageSettings?: Record<string, unknown>; [key: string]: unknown };

const fieldCopy: Record<string, { label?: string; defaultValue?: string; apple?: string }> = {
  'members.member.points': { label: 'Stamps', apple: 'You now have %@ stamps.' },
  'members.program.name': { defaultValue: programName },
  'custom.latest': { label: 'MEMBER NEWS', defaultValue: 'Welcome to the club. Show this card at the counter on every visit.' },
  'universal.info': { label: 'HOW TO USE', defaultValue: 'Show the QR code at the counter on every visit. Each qualifying visit adds a stamp; collect enough to unlock your reward and move up from Ink to Chrome to Pink.', apple: 'AIKIA Members Club update: %@' },
};
// Extra Google Wallet text fields our app fills in from the member's metaData (see passkit.ts).
const addedFields = [
  { uniqueName: 'meta.myCardUrl', label: 'PAY, TOP UP, SEND A GIFT', dataType: 'TEXT_LONG', defaultValue: 'Ask the team for your card link.', priority: 1 },
  { uniqueName: 'meta.rewardsAvailable', label: 'REWARDS READY', dataType: 'TEXT', defaultValue: '0', priority: 2 },
  { uniqueName: 'meta.tierBenefits', label: 'YOUR BENEFITS', dataType: 'TEXT_LONG', defaultValue: 'Collect stamps to unlock member benefits.', priority: 3 },
  { uniqueName: 'meta.creditBalance', label: 'CREDIT', dataType: 'TEXT', defaultValue: 'Not offered', priority: 4 },
];
const textModule = (name: string) => ({ firstValue: { fields: [{ fieldPath: `object.textModulesData['${name.replace('.', '-')}']` }] } });
// Front: name + stamps, tier + rewards ready, credit. Back: member ID, My card link, how to use, benefits.
const googleLayout = {
  detailsTemplateOverride: { detailsItemInfos: [{ item: { firstValue: { fields: [{ fieldPath: 'object.accountId' }] } } }, { item: textModule('meta.myCardUrl') }, { item: textModule('universal.info') }, { item: textModule('meta.tierBenefits') }] },
  cardTemplateOverride: { cardRowTemplateInfos: [
    { threeItems: { startItem: textModule('person.forename'), middleItem: textModule('person.surname'), endItem: { firstValue: { fields: [{ fieldPath: 'object.loyaltyPoints.balance' }] } } } },
    { twoItems: { startItem: { firstValue: { fields: [{ fieldPath: 'class.localizedRewardsTier' }] } }, endItem: textModule('meta.rewardsAvailable') } },
    { oneItem: { item: textModule('meta.creditBalance') } },
  ] },
};
const enrolmentDescription = 'Enter your name to get your AIKIA membership card. Save it to your wallet and show it on every visit.';

function applyCopy(data: TemplateData | undefined) {
  if (!data) return data;
  const dataFields = (data.dataFields || []).filter(field => !removedFields.has(field.uniqueName)).map(field => {
    const copy = fieldCopy[field.uniqueName];
    if (!copy) return field;
    const next = { ...field };
    if (copy.label) next.label = copy.label;
    if (copy.defaultValue !== undefined) next.defaultValue = copy.defaultValue;
    if (copy.apple && next.appleWalletFieldRenderOptions) next.appleWalletFieldRenderOptions = { ...next.appleWalletFieldRenderOptions, changeMessage: copy.apple };
    return next;
  });
  const base = data.dataFields?.find(field => field.uniqueName === 'universal.info');
  for (const added of addedFields) {
    if (!base || dataFields.some(field => field.uniqueName === added.uniqueName)) continue;
    dataFields.push({ ...base, uniqueName: added.uniqueName, fieldType: 'META', label: added.label, dataType: added.dataType, defaultValue: added.defaultValue, userCanSetValue: false, usage: ['USAGE_GOOGLE_PAY'], googlePayFieldRenderOptions: { googlePayPosition: 'GOOGLE_PAY_TEXT_MODULE', textModulePriority: added.priority } });
  }
  const dataCollectionPageSettings = data.dataCollectionPageSettings ? { ...data.dataCollectionPageSettings, description: enrolmentDescription } : data.dataCollectionPageSettings;
  return { ...data, dataFields, dataCollectionPageSettings };
}

/** Runs the branding against PassKit. Images are read from the deployed app's /brand folder. */
export async function applyPassKitBranding(appUrl: string) {
  const key = process.env.PASSKIT_API_KEY?.trim(); const secret = process.env.PASSKIT_API_SECRET?.trim();
  const base = new URL(process.env.PASSKIT_API_BASE_URL?.trim() || 'https://api.pub1.passkit.io').origin;
  const programId = process.env.PASSKIT_PROGRAM_ID?.trim();
  if (!key || !secret || !programId) throw new Error('PassKit is not configured (PASSKIT_API_KEY, PASSKIT_API_SECRET, PASSKIT_PROGRAM_ID).');
  async function pk<T = Record<string, unknown>>(path: string, init: RequestInit = {}): Promise<T> {
    const response = await fetch(`${base}/${path}`, { ...init, cache: 'no-store', headers: { authorization: signPassKitToken(key!, secret!), 'content-type': 'application/json' } });
    const text = await response.text();
    if (!response.ok) throw new Error(`PassKit ${init.method || 'GET'} ${path} → ${response.status}: ${text.slice(0, 300)}`);
    return (text ? JSON.parse(text) : {}) as T;
  }
  async function image(file: string) {
    const response = await fetch(`${appUrl.replace(/\/$/, '')}/brand/${file}`, { cache: 'no-store' });
    if (!response.ok) throw new Error(`Card image ${file} could not be loaded (${response.status}).`);
    return Buffer.from(await response.arrayBuffer()).toString('base64');
  }
  const log: string[] = [];
  const program = await pk<{ name?: string; profileImageSettings?: string }>(`members/program/${programId}`);
  if (program.name !== programName || program.profileImageSettings !== 'PROFILE_IMAGE_NONE') {
    await pk('members/program', { method: 'PUT', body: JSON.stringify({ ...program, name: programName, profileImageSettings: 'PROFILE_IMAGE_NONE' }) });
    log.push(`Program renamed to ${programName}`);
  }
  const logo = await image('aikia-wallet-program-logo.png');
  for (const [tierId, look] of Object.entries(tiers)) {
    let tier: { passTemplateId?: string };
    try { tier = await pk(`members/tier/${programId}/${tierId}`); } catch { log.push(`Tier ${tierId}: not in this program, skipped`); continue; }
    if (!tier.passTemplateId) continue;
    const { template } = await pk<{ template: Record<string, unknown> & { data?: TemplateData; googlePaySettings?: Record<string, unknown>; colors?: Record<string, unknown>; imageIds?: Record<string, string> } }>(`template/data/${tier.passTemplateId}`);
    const uploaded = await pk<{ logo?: string; hero?: string; richHero?: string }>('images', { method: 'POST', body: JSON.stringify({ name: `aikia-metal-${tierId}`, imageData: { logo, hero: await image(look.hero), richHero: await image(look.richHero) } }) });
    await pk('template', {
      method: 'PUT',
      body: JSON.stringify({
        ...template, name: cardName, organizationName, data: applyCopy(template.data),
        googlePaySettings: { ...template.googlePaySettings, classTemplateInfo: JSON.stringify(googleLayout) },
        colors: { ...template.colors, backgroundColor: look.backgroundColor, labelColor: look.labelColor, textColor: look.textColor },
        imageIds: { ...template.imageIds, logo: uploaded.logo || template.imageIds?.logo, hero: uploaded.hero || template.imageIds?.hero, richHero: uploaded.richHero || template.imageIds?.richHero },
      }),
    });
    log.push(`Tier ${tierId}: metallic design applied`);
  }
  return log;
}
