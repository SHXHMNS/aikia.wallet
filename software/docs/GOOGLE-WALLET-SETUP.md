# Google Wallet setup for AIKIA.WALLET

This software targets Google **Loyalty Classes and Loyalty Objects**. Classes hold shared venue/program design; one object is issued per loyalty member. The Google Wallet API creates a Save-to-Wallet URL from an RS256-signed JWT.

## Accounts and access

1. Create an Issuer account in Google Pay & Wallet Console under the company identity and record its Issuer ID.
2. Create/select the Google Cloud project and enable the Google Wallet REST API.
3. Create a service account, download one JSON key to a secure place, and invite that service-account email as a Developer on the Issuer account.
4. Store the JSON as the server-only `GOOGLE_WALLET_SERVICE_ACCOUNT_JSON` secret. Do not place the key in the repository or browser bundle.
5. Complete the Issuer business profile and publishing-access process before onboarding general customers. Demo mode is for issuer admins/developers and explicitly added test accounts.

## App configuration

- `GOOGLE_WALLET_ISSUER_ID`: numeric issuer ID from the Wallet console.
- `GOOGLE_WALLET_SERVICE_ACCOUNT_JSON`: complete service-account JSON.
- `GOOGLE_WALLET_PROGRAM_LOGO_URL`: publicly reachable HTTPS logo for initial class creation.
- `NEXT_PUBLIC_APP_URL`: canonical app origin included in signed Add-to-Wallet claims.
- Supabase keys from the project dashboard.

## Pass lifecycle in this codebase

1. An authenticated venue owner creates a deterministic `LoyaltyClass` for that venue.
2. An owner/staff member can create a member, or the customer can join at `/join/<venue-slug>`. When the issuer is configured, the server creates/updates that member's `LoyaltyObject` with an opaque barcode token and current ledger balance.
3. The server signs a Save-to-Wallet JWT and returns the Google URL to the owner or customer. The customer must open it while signed in to a Google identity. A new issuer still limits passes to authorized users until publishing access is granted.
4. A stamp action writes to the AIKIA append-only ledger first. The Google object balance is then patched from that ledger-derived balance.

The AIKIA ledger remains the record of truth. Google Wallet displays the current balance but does not authorize a stamp or redemption by itself. Public join additionally needs migration `0002_public_customer_join.sql` and the server-only `JOIN_RATE_LIMIT_SECRET`.

## Test and go-live sequence

- Create a class and object; ensure identifiers are stable and unique.
- Add issuer admins/developers or test users, and issue passes to them.
- Test save, duplicate saves, class/object updates, barcode scan, balance update, revoked member, recovery and failure/retry handling.
- Confirm Google Wallet Business Console lists the expected account, program and review state.
- Request publishing access in the Wallet console after the business profile and required class are present. Public issuance stays off until Google grants that access.

Official references:

- [Loyalty card setup and issuer onboarding](https://developers.google.com/wallet/retail/loyalty-cards/getting-started/issuer-onboarding)
- [REST API authentication credentials](https://developers.google.com/wallet/retail/loyalty-cards/getting-started/auth/rest)
- [Create Loyalty Classes and Objects](https://developers.google.com/wallet/retail/loyalty-cards/use-cases/create)
- [Request publishing access](https://developers.google.com/wallet/retail/loyalty-cards/test-and-go-live/request-publishing-access)
