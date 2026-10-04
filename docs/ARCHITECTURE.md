# AIKIA.WALLET architecture

## Product surfaces

### Buyer demo

`demo-service/` is a complete presentation flow backed by fictional records in browser `localStorage`. The Owner dashboard edits venue identity, card color, reward rules, and a configurable Ink / Chrome / Pink membership ladder. The Staff dashboard has member lookup, browser QR scanning where available, purchase recording, tier upgrades, reward availability, and redemption. It deliberately makes no claim of live wallet issuance or cloud persistence.

### Authenticated operator application

`software/` is the app intended for connected venue accounts. Supabase Auth authenticates users. A venue membership role chooses the dashboard surface:

- **Owner/admin:** program settings, brand and theme, tiers and benefits, team invitations, member book and reporting.
- **Staff/manager:** venue-scoped member lookup, QR scan, qualifying-action recording and reward redemption.

### Customer enrollment

Each venue can share `/join/<venue-slug>`. The public page collects a member name and consent, creates a venue-scoped member record, and returns a Google Wallet save link when the issuer is configured. A server-only HMAC fingerprint and Supabase function impose a small per-venue signup limit. The privacy and program-terms pages are starter copy and must be replaced with venue-approved information before live enrollment.

## Domain model

- A **venue** owns business type, theme, qualifying-action label, wallet balance label, reward target, reward name, member records and tier rules.
- A **qualifying action** is the repeat behavior that moves the member forward. A café can count coffees; another venue can count purchases, visits, treatments or bookings.
- **Tiers** are ordered by lifetime qualifying actions. The venue can change their names, thresholds, colors and exclusive benefits.
- **Members** carry an opaque random scan token, a public member code, reward progress, earned rewards and a current tier.
- **Ledger transactions** record actions and redemptions. The database operation is atomic and idempotent so a retried request cannot award the same action twice.
- **Wallet passes** store the provider mapping. A Google Wallet class represents the venue theme and each Loyalty Object represents one member.

## Wallet provider boundary

`software/src/lib/wallet/types.ts` defines the provider-neutral contract. `google.ts` is the active Google Wallet Loyalty Class/Object integration. `apple.ts` is intentionally an unimplemented adapter seam; it can be added without changing venue, member, tier, or ledger concepts.

Google's class controls the shared venue card design. Per-member points, tier name, exclusive benefits and action history are sent to the member object. Google Wallet applies the class's color to all cards in a venue. The demo can preview different tier colors, while live Google passes currently use the venue-wide class color.

## Security boundaries

- Route handlers verify the authenticated Supabase user and venue role. Sensitive provider calls and service-role database operations stay server-side.
- Supabase RLS scopes venue data. Staff cannot directly edit member balances or the ledger; authorized route handlers call restricted database functions.
- Scan tokens are random and contain no phone number or other member PII. Member lookup is restricted to an authenticated venue team member.
- Public enrollment records the consent time and notice version. Its rate limit stores a short-lived HMAC of the network address rather than the address itself; it is an initial pilot control, not a substitute for managed bot protection.
- Purchase writes and reward redemptions are transactional, audited and idempotent. Google Wallet synchronization happens after the canonical ledger update and failures are recorded.
- The buyer demo is fictional, local-only sample data. Never enter real customer details into it.

## Current integration prerequisites

1. Supabase project URL and publishable/anon key.
2. Server-only Supabase service-role key.
3. Google Wallet Issuer ID and service-account JSON with issuer Developer access.
4. Public HTTPS program logo and canonical app origin.
5. Authorized Google Wallet test accounts; publishing access before general availability.

Apple Wallet certificates, identifiers and signing remain a later provider integration phase.
