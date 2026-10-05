// Applies AIKIA branding to a PassKit membership program's Google Wallet designs.
// Usage (from software/): node --env-file=.env.local scripts/passkit-brand.mjs [--dry-run]
// Needs PASSKIT_API_KEY, PASSKIT_API_SECRET, PASSKIT_API_BASE_URL and PASSKIT_PROGRAM_ID.
// Only Google-facing parts (background, label/text colours, logo, hero) are changed; Apple images are left as they are.
import { createHmac } from 'node:crypto';
import { readFileSync } from 'node:fs';

const { PASSKIT_API_KEY: key, PASSKIT_API_SECRET: secret, PASSKIT_API_BASE_URL: base = 'https://api.pub1.passkit.io', PASSKIT_PROGRAM_ID: programId } = process.env;
if (!key || !secret || !programId) throw new Error('Set PASSKIT_API_KEY, PASSKIT_API_SECRET and PASSKIT_PROGRAM_ID.');
const dryRun = process.argv.includes('--dry-run');

const programName = 'AIKIA Members Club';
const cardName = 'Members Club';
const organizationName = 'AIKIA';
// Tier ID → AIKIA brand palette (tokens.json) and its hero banner in public/brand.
const tiers = {
  ink: { backgroundColor: '#A98BFF', labelColor: '#FF3D9A', textColor: '#14111F', hero: 'card-hero-ink.png', richHero: 'card-rich-ink.png' },
  chrome: { backgroundColor: '#7FE7F2', labelColor: '#A98BFF', textColor: '#14111F', hero: 'card-hero-chrome.png', richHero: 'card-rich-chrome.png' },
  pink: { backgroundColor: '#FF3D9A', labelColor: '#14111F', textColor: '#14111F', hero: 'card-hero-pink.png', richHero: 'card-rich-pink.png' },
  membership: { backgroundColor: '#A98BFF', labelColor: '#FF3D9A', textColor: '#14111F', hero: 'card-hero-ink.png', richHero: 'card-rich-ink.png' },
};
// Template fields that loyalty cards don't use (they showed as "missing: universal.expiryDate" / "empty value").
const removedFields = new Set(['universal.expiryDate', 'meta.notification']);

// Card copy, replacing the template's sample text. Keyed by PassKit data field uniqueName.
const fieldCopy = {
  'members.member.points': { label: 'Stamps', apple: 'You now have %@ stamps.' },
  'members.program.name': { defaultValue: programName },
  'custom.latest': { label: 'MEMBER NEWS', defaultValue: 'Welcome to the club. Show this card at the counter on every visit.' },
  'universal.info': { label: 'HOW TO USE', defaultValue: 'Show the QR code at the counter on every visit. Each qualifying visit adds a stamp; collect enough to unlock your reward and move up from Ink to Chrome to Pink.', apple: 'AIKIA Members Club update: %@' },
};
// Extra Google Wallet text fields our app fills in from the member's metaData (see src/lib/wallet/passkit.ts).
const addedFields = [
  { uniqueName: 'meta.rewardsAvailable', label: 'REWARDS READY', dataType: 'TEXT', defaultValue: '0', priority: 2 },
  { uniqueName: 'meta.tierBenefits', label: 'YOUR BENEFITS', dataType: 'TEXT_LONG', defaultValue: 'Collect stamps to unlock member benefits.', priority: 3 },
];
const textModule = name => ({ firstValue: { fields: [{ fieldPath: `object.textModulesData['${name.replace('.', '-')}']` }] } });
// Google card layout: name + stamps, tier + rewards ready on the front; member ID, how to use and benefits on the back.
const googleLayout = {
  detailsTemplateOverride: { detailsItemInfos: [{ item: { firstValue: { fields: [{ fieldPath: 'object.accountId' }] } } }, { item: textModule('universal.info') }, { item: textModule('meta.tierBenefits') }] },
  cardTemplateOverride: { cardRowTemplateInfos: [
    { threeItems: { startItem: textModule('person.forename'), middleItem: textModule('person.surname'), endItem: { firstValue: { fields: [{ fieldPath: 'object.loyaltyPoints.balance' }] } } } },
    { twoItems: { startItem: { firstValue: { fields: [{ fieldPath: 'class.localizedRewardsTier' }] } }, endItem: textModule('meta.rewardsAvailable') } },
  ] },
};

const enrolmentDescription = 'Enter your name to get your AIKIA membership card. Save it to your wallet and show it on every visit.';

function applyCopy(data) {
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

const b64url = value => Buffer.from(value).toString('base64url');
function token() {
  const now = Math.floor(Date.now() / 1000);
  const unsigned = `${b64url(JSON.stringify({ alg: 'HS256', typ: 'JWT' }))}.${b64url(JSON.stringify({ uid: key, iat: now, exp: now + 60 }))}`;
  return `${unsigned}.${createHmac('sha256', secret).update(unsigned).digest('base64url')}`;
}
async function pk(path, init = {}) {
  const response = await fetch(`${base}/${path}`, { ...init, headers: { authorization: token(), 'content-type': 'application/json' } });
  const text = await response.text();
  if (!response.ok) throw new Error(`PassKit ${init.method || 'GET'} ${path} → ${response.status}: ${text.slice(0, 400)}`);
  return text ? JSON.parse(text) : {};
}
const image = file => readFileSync(new URL(`../public/brand/${file}`, import.meta.url)).toString('base64');

const program = await pk(`members/program/${programId}`);
// Loyalty members join with just a name, so the program must not demand a profile photo.
if (program.name !== programName || program.profileImageSettings !== 'PROFILE_IMAGE_NONE') {
  console.log(`Program: "${program.name}" → "${programName}", profile image ${program.profileImageSettings} → PROFILE_IMAGE_NONE`);
  if (!dryRun) await pk('members/program', { method: 'PUT', body: JSON.stringify({ ...program, name: programName, profileImageSettings: 'PROFILE_IMAGE_NONE' }) });
}

const logo = image('aikia-wallet-program-logo.png');
for (const [tierId, look] of Object.entries(tiers)) {
  let tier;
  try { tier = await pk(`members/tier/${programId}/${tierId}`); } catch { console.log(`Tier ${tierId}: not found, skipped`); continue; }
  const { template } = await pk(`template/data/${tier.passTemplateId}`);
  console.log(`Tier ${tierId}: template ${tier.passTemplateId}, background ${template.colors?.backgroundColor} → ${look.backgroundColor}`);
  if (dryRun) continue;
  const uploaded = await pk('images', { method: 'POST', body: JSON.stringify({ name: `aikia-${tierId}`, imageData: { logo, hero: image(look.hero), richHero: image(look.richHero) } }) });
  await pk('template', {
    method: 'PUT',
    body: JSON.stringify({
      ...template,
      name: cardName,
      organizationName,
      data: applyCopy(template.data),
      googlePaySettings: { ...template.googlePaySettings, classTemplateInfo: JSON.stringify(googleLayout) },
      colors: { ...template.colors, backgroundColor: look.backgroundColor, labelColor: look.labelColor, textColor: look.textColor },
      imageIds: { ...template.imageIds, logo: uploaded.logo || template.imageIds.logo, hero: uploaded.hero || template.imageIds.hero, richHero: uploaded.richHero || template.imageIds.richHero },
    }),
  });
  console.log(`  updated (logo ${uploaded.logo}, hero ${uploaded.hero}, richHero ${uploaded.richHero})`);
}
console.log(dryRun ? 'Dry run only, nothing changed.' : 'Done.');
