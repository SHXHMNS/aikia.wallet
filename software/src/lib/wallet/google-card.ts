// Pure Google Wallet card helpers (no server-only import) so they can be unit-tested with node --test.

type WalletMemberCard = { fullName: string; tierName: string; tierBenefits: string[]; rewardsAvailable: number };

const field = (fieldPath: string) => ({ firstValue: { fields: [{ fieldPath }] } });
const module = (id: string) => field(`object.textModulesData['${id}']`);

/** Front: first name · last name · stamps, then tier · rewards ready. Back: member code, how to use, benefits. */
export const googleCardLayout = {
  cardTemplateOverride: {
    cardRowTemplateInfos: [
      { threeItems: { startItem: module('first-name'), middleItem: module('last-name'), endItem: field('object.loyaltyPoints.balance') } },
      { twoItems: { startItem: module('member-tier'), endItem: module('rewards-ready') } },
    ],
  },
  detailsTemplateOverride: {
    detailsItemInfos: [{ item: field('object.accountId') }, { item: module('how-to-use') }, { item: module('tier-benefits') }],
  },
};

export function googleTextModules(member: WalletMemberCard) {
  const parts = member.fullName.trim().split(/\s+/).filter(Boolean);
  const first = parts.shift() || member.fullName.trim();
  return [
    { id: 'first-name', header: 'FIRST NAME', body: first.slice(0, 60) },
    { id: 'last-name', header: 'LAST NAME', body: (parts.join(' ') || ' ').slice(0, 60) },
    { id: 'member-tier', header: 'TIER', body: member.tierName.slice(0, 40) },
    { id: 'rewards-ready', header: 'REWARDS READY', body: String(member.rewardsAvailable) },
    { id: 'how-to-use', header: 'HOW TO USE', body: 'Show the QR code at the counter on every visit. Each qualifying visit adds a stamp; collect enough to unlock your reward and move up the tiers.' },
    { id: 'tier-benefits', header: 'YOUR BENEFITS', body: (member.tierBenefits.join(' · ') || 'Collect stamps to unlock member benefits.').slice(0, 500) },
  ];
}

/** AIKIA aurora artwork exists for ink / chrome / pink; any other tier name uses the entry (ink) art. */
export function tierArtSlug(tierName: string) {
  const slug = tierName.trim().toLowerCase();
  return slug === 'chrome' || slug === 'pink' ? slug : 'ink';
}
