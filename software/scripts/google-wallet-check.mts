// Checks the direct Google Wallet engine end to end without touching the database:
// authenticates, creates/updates the venue's LoyaltyClass, issues a test LoyaltyObject and prints a save link.
// Usage (from software/): npx tsx --conditions=react-server --env-file=.env.local scripts/google-wallet-check.mts <venue-slug>
import { createClient } from '@supabase/supabase-js';
import { GoogleWalletProvider } from '../src/lib/wallet/google.ts';

const slug = process.argv[2] || '1331';
const admin = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, process.env.SUPABASE_SECRET_KEY!, { auth: { persistSession: false } });
const { data: v, error } = await admin.from('venues').select('*').eq('slug', slug).single();
if (error || !v) throw new Error(`Venue ${slug} not found`);
const provider = new GoogleWalletProvider();
const venue = { id: v.id, name: v.name, slug: v.slug, brandColor: v.brand_color, backgroundColor: v.background_color, programLogoUrl: v.program_logo_url, heroImageUrl: v.hero_image_url, balanceLabel: v.balance_label, actionLabel: v.action_label };
const classId = await provider.ensureVenueClass(venue);
console.log('class ok:', classId);
const issued = await provider.issueMemberPass(venue, {
  id: 'google-check-test', venueId: v.id, fullName: 'AIKIA Test Member', publicCode: 'ATEST0001', scanToken: 'google-check-test-token',
  stampBalance: 3, balanceLabel: v.balance_label || 'STAMPS', rewardsAvailable: 0, lifetimeActions: 3, tierName: 'Ink', tierBenefits: ['Collect a stamp with every coffee'],
});
console.log('object ok:', issued.providerObjectId);
console.log('SAVE LINK:', issued.saveLinks.google);
