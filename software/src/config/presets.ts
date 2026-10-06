/**
 * Starting programs per business type. A new venue picks one; the owner can change every value
 * afterwards in Brand & tiers. Tier names stay Ink / Chrome / Pink so wallet card designs carry over.
 */
export type BusinessType = 'cafe' | 'restaurant' | 'retail' | 'salon' | 'fitness' | 'hotel' | 'entertainment' | 'other';

export type VenuePreset = {
  label: string;
  actionLabel: string;
  balanceLabel: string;
  rewardTarget: number;
  rewardName: string;
  brandColor: string;
  tiers: { name: string; minLifetimeActions: number; minLifetimeSpend: number; benefits: string[]; accentColor: string }[];
};

// Spend thresholds (₹) apply when a venue chooses spend-based tiers; default ₹20,000 → Chrome, ₹1,00,000 → Pink.
const ladder = (entry: string[], mid: string[], top: string[], midAt: number, topAt: number, midSpend = 20000, topSpend = 100000) => [
  { name: 'Ink', minLifetimeActions: 0, minLifetimeSpend: 0, benefits: entry, accentColor: '#171421' },
  { name: 'Chrome', minLifetimeActions: midAt, minLifetimeSpend: midSpend, benefits: mid, accentColor: '#A98BFF' },
  { name: 'Pink', minLifetimeActions: topAt, minLifetimeSpend: topSpend, benefits: top, accentColor: '#FF3D9A' },
];

export const venuePresets: Record<BusinessType, VenuePreset> = {
  cafe: {
    label: 'Café', actionLabel: 'coffee purchase', balanceLabel: 'STAMPS', rewardTarget: 9, rewardName: 'Free coffee', brandColor: '#171421',
    tiers: ladder(['Collect a stamp with every coffee'], ['A complimentary size upgrade', 'Members-only seasonal menu'], ['A complimentary coffee', 'First access to new drinks', 'Invitations to member events'], 15, 40),
  },
  restaurant: {
    label: 'Restaurant', actionLabel: 'dine-in visit', balanceLabel: 'VISITS', rewardTarget: 8, rewardName: 'Free dessert', brandColor: '#2B1D1A',
    tiers: ladder(['Collect a visit with every meal'], ['Priority reservations', 'Chef’s tasting previews'], ['A complimentary starter every visit', 'Members-only dinners'], 10, 30),
  },
  retail: {
    label: 'Retail store', actionLabel: 'purchase', balanceLabel: 'POINTS', rewardTarget: 10, rewardName: '10% off your next order', brandColor: '#1B2230',
    tiers: ladder(['Collect a point with every purchase'], ['Early access to sales', 'Free gift wrapping'], ['Members-only drops', 'Birthday gift', 'Free alterations'], 12, 35),
  },
  salon: {
    label: 'Salon & spa', actionLabel: 'treatment', balanceLabel: 'VISITS', rewardTarget: 6, rewardName: 'Free blow-dry', brandColor: '#2A1830',
    tiers: ladder(['Collect a visit with every treatment'], ['Priority booking', 'Complimentary hair mask'], ['A free treatment upgrade each visit', 'Birthday pampering'], 8, 24),
  },
  fitness: {
    label: 'Gym & fitness', actionLabel: 'class check-in', balanceLabel: 'CLASSES', rewardTarget: 10, rewardName: 'Free class', brandColor: '#10221C',
    tiers: ladder(['Collect a check-in with every class'], ['Bring a friend free monthly', 'Free towel service'], ['One free personal-training session', 'Members-only events'], 20, 60),
  },
  hotel: {
    label: 'Hotel', actionLabel: 'night stayed', balanceLabel: 'NIGHTS', rewardTarget: 10, rewardName: 'Free night', brandColor: '#1A2033',
    tiers: ladder(['Collect a night with every stay'], ['Late checkout', 'Welcome drink'], ['Room upgrade when available', 'Breakfast included'], 10, 30),
  },
  entertainment: {
    label: 'Entertainment', actionLabel: 'ticketed visit', balanceLabel: 'VISITS', rewardTarget: 6, rewardName: 'Free entry', brandColor: '#1E1530',
    tiers: ladder(['Collect a visit with every ticket'], ['Skip-the-line entry', 'Member pricing on snacks'], ['Free guest pass monthly', 'Invitations to premieres'], 8, 25),
  },
  other: {
    label: 'Other business', actionLabel: 'qualifying visit', balanceLabel: 'STAMPS', rewardTarget: 9, rewardName: 'Member reward', brandColor: '#171421',
    tiers: ladder(['Collect a stamp with every visit'], ['Members-only offers'], ['A complimentary reward', 'Invitations to member events'], 15, 40),
  },
};

export function isBusinessType(value: unknown): value is BusinessType {
  return typeof value === 'string' && value in venuePresets;
}
