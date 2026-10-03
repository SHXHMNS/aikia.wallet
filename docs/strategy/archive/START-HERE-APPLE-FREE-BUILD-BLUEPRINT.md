# AIKIA.WALLET: Apple-free build blueprint

**Purpose:** create a credible, usable demonstration of the AIKIA.WALLET service before Apple Developer Program enrollment. Apple Wallet issuance is a later integration step, not a blocker for building the venue, guest, staff and owner experience.

**Route:** use the newer PassKit-first decision: AIKIA owns the join experience, staff scanner, owner dashboard, venue configuration and member ledger; PassKit is the planned wallet-pass engine. Do not start with a direct Apple pass engine. Keep the wallet provider behind an adapter so PassKit can be connected after account setup.

## What we can build now

1. **Venue configuration:** a venue name, brand color, reward rule, opening details and a join link/QR concept.
2. **Guest join:** a short form, explicit marketing consent, and a branded digital-card preview. The preview is a web card, not an Apple or Google Wallet pass.
3. **Member record:** stable member ID, venue ID, join time, consent state and sample card code.
4. **Staff flow:** find a demo member, apply a stamp, show reward progress and record who performed the action.
5. **Owner dashboard:** sample members, visit/reward activity and a campaign preview. Campaign preview must not send real messages.
6. **Ledger rules:** represent stamps and reversals as appended transactions; calculate the displayed total from transactions instead of directly overwriting a balance.
7. **Demo operations:** clearly label sample data, support a reset, and prevent the demo from being mistaken for a live service.

## Build phases

### Phase 0 - Apple-free service demo (start now)

- Build the responsive venue dashboard, guest join flow, digital-card preview and staff reward flow.
- Use fictional seed data and browser-local persistence only. Do not enter real guest contact details.
- Make the pass-provider boundary explicit: `createPass`, `updatePass`, `getAddToWalletLink` are not implemented in this phase.
- Demonstrate the service value and staff workflow without claiming an installable wallet pass, real notification, cross-device sync or production security.

**Done when:** a venue owner can understand the offer, a test guest can join, staff can apply a test stamp, and the owner can see the updated sample activity on the same browser.

### Phase 1 - Production foundation (can proceed before Apple)

- Create the Next.js + TypeScript application and Supabase project; set up separate development and production environments.
- Model `venues`, `profiles`, `venue_members`, `ledger_transactions`, `rewards`, `campaigns`, `staff_members` and `audit_events`.
- Require `venue_id` on venue-owned records. Enforce venue boundaries with Supabase Row Level Security and server-side authorization.
- Add real staff/owner login, server validation, rate limits, idempotency keys, append-only ledger writes, backups and audit attribution.
- Build the production join page, scanner, owner dashboard and venue-admin flow around APIs, not browser storage.
- Keep all provider keys server-side; add no real guest data until access controls, consent and data handling have been reviewed.

**Done when:** two test venues cannot read one another's member data; duplicate requests do not double-stamp; restore and member deletion procedures are documented; demo flows work from separate devices.

### Phase 2 - Wallet provider setup (start PassKit work; Apple enrollment is a dependency)

- Create the company PassKit account and confirm its current pricing, API access, Apple certificate requirements, Google Wallet route, branded links, data location, export path, test environment and migration options.
- Reserve permanent identifiers only after the company account and ownership are confirmed.
- Draft a `WalletProvider` interface and a fake provider for development. Keep PassKit credentials in server secrets.
- Prepare pass artwork, venue fields, update messages, QR payload format and device test matrix.
- Wait for Apple Developer Program approval before creating the live Apple Pass Type ID/certificate or issuing production Apple passes.

**Done when:** a PassKit sandbox/test project can issue and update a test card on supported devices, while the AIKIA join page, scanner and dashboard remain the only venue/staff surfaces.

### Phase 3 - Apple and Google wallet integration (after Apple enrollment)

- Enroll using the company Apple account; confirm whether the company needs organization enrollment/D-U-N-S verification or can begin as an individual account.
- Create the production Pass Type ID under the company account and generate the certificate/CSR through the approved PassKit flow.
- Store certificates and API credentials in the production secret manager; never commit them to source control or send them in chat.
- Connect the PassKit adapter; implement Apple add/update and device registration flows; verify Google issuance through the confirmed provider route.
- Test install, scan, stamp, reward, offer update, device removal, lost-phone recovery and certificate-renewal procedures on real test devices.
- Enable a limited pilot only after privacy terms, venue contract, data isolation, support, backup, restore, monitoring and manual fallback are in place.

## Data and event rules

- A member belongs to exactly one venue unless a future cross-venue Circle feature is deliberately designed and consented to.
- Every stamp, redemption, correction or reversal is a new ledger event. Never silently edit prior reward history.
- Each staff action carries `venue_id`, `member_id`, `actor_id`, timestamp and a unique request ID.
- Check reward eligibility and write the ledger event in one database transaction.
- Keep consent state, consent-copy version and timestamp. Honor opt-outs and deletion requests under the approved retention policy.
- A wallet barcode should carry an opaque, signed token, not a sequential member number or phone number.

## Apple-free work that does not need the enrollment

- Brand system and card layouts; service copy and venue onboarding forms.
- Owner, staff and guest screens; sample join, scan, stamp, reward and campaign-preview flows.
- Database schema design, local development environment, account setup for hosting and Supabase, server authorization and venue-isolation rules.
- PassKit evaluation questions, provider adapter, test fixture data, deployment pipeline, monitoring plan and support playbook.
- Legal/accounting review of consent, privacy notice, venue data terms, prepaid balance handling, GST, invoicing and cancellation.

## Explicitly out of the first demo

Production Apple/Google pass issuance; real push/lock-screen delivery; Halo geofencing; prepaid cash balances; POS integration; automated SMS/WhatsApp; cross-venue Circle; production analytics claims. These are not needed to demonstrate the core service and each has extra technical, legal, provider or operational requirements.

## Commercial and launch safeguards

- Treat existing tier prices and the Founding 10 terms as proposed drafts until a founder approves them.
- Do not promise incremental visits, profit, notification reach, a fixed location radius or guaranteed return. Establish a baseline and report observed results.
- Do not use real customer data in the local demo. Browser storage is not encrypted, shared across devices, backed up, access-controlled or venue-isolated.
- The demo QR/card code is illustrative and must not be accepted as a production credential.
- Confirm India privacy, consumer, telecom, prepaid balance and GST obligations with qualified counsel/accounting support before the relevant features go live.

## Immediate sequence

1. Run `demo-service/index.html` using the local server instructions in `demo-service/README.md`.
2. Walk through owner dashboard, guest join, demo card and staff stamp with fictional data.
3. Pick one pilot café, one reward rule and one metric; prepare a written pilot scope and draft consent language.
4. Set up company-owned Supabase/Vercel environments and implement the secure production data model.
5. Start the PassKit account and provider due-diligence questions while the Apple enrollment is in process.
6. After Apple approval, connect certificates and wallet issuance behind the provider adapter, then test end to end.

**Current milestone:** Apple-free demo foundation. **Not a production wallet service yet.**
