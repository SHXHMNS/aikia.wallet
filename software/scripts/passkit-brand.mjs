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
  ink: { backgroundColor: '#14111F', labelColor: '#FF3D9A', textColor: '#ECEEF5', hero: 'card-hero-ink.png' },
  chrome: { backgroundColor: '#252038', labelColor: '#A98BFF', textColor: '#ECEEF5', hero: 'card-hero-chrome.png' },
  pink: { backgroundColor: '#FF3D9A', labelColor: '#14111F', textColor: '#14111F', hero: 'card-hero-pink.png' },
  membership: { backgroundColor: '#14111F', labelColor: '#FF3D9A', textColor: '#ECEEF5', hero: 'card-hero-ink.png' },
};

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
if (program.name !== programName) {
  console.log(`Program: "${program.name}" → "${programName}"`);
  if (!dryRun) await pk('members/program', { method: 'PUT', body: JSON.stringify({ ...program, name: programName }) });
}

const logo = image('aikia-wallet-program-logo.png');
for (const [tierId, look] of Object.entries(tiers)) {
  let tier;
  try { tier = await pk(`members/tier/${programId}/${tierId}`); } catch { console.log(`Tier ${tierId}: not found, skipped`); continue; }
  const { template } = await pk(`template/data/${tier.passTemplateId}`);
  console.log(`Tier ${tierId}: template ${tier.passTemplateId}, background ${template.colors?.backgroundColor} → ${look.backgroundColor}`);
  if (dryRun) continue;
  const uploaded = await pk('images', { method: 'POST', body: JSON.stringify({ name: `aikia-${tierId}`, imageData: { logo, hero: image(look.hero) } }) });
  await pk('template', {
    method: 'PUT',
    body: JSON.stringify({
      ...template,
      name: cardName,
      organizationName,
      colors: { ...template.colors, backgroundColor: look.backgroundColor, labelColor: look.labelColor, textColor: look.textColor },
      imageIds: { ...template.imageIds, logo: uploaded.logo || template.imageIds.logo, hero: uploaded.hero || template.imageIds.hero },
    }),
  });
  console.log(`  updated (logo ${uploaded.logo}, hero ${uploaded.hero})`);
}
console.log(dryRun ? 'Dry run only, nothing changed.' : 'Done.');
