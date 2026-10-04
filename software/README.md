# AIKIA.WALLET software

Development workspace for the AIKIA.WALLET venue platform. Google Wallet loyalty cards are the active integration; Apple Wallet is reserved for a later provider implementation. The app now contains a complete controlled-pilot workflow, but it still needs the owner's service accounts, a deployment, live Wallet approval and operational launch checks.

## Stack

- Next.js App Router + TypeScript
- Supabase Postgres/Auth with row-level security
- Google Wallet REST API (`LoyaltyClass` + `LoyaltyObject`)
- Server-side Google service-account authentication and signed Add to Google Wallet JWTs

## Configuration

Copy `.env.example` to `.env.local` and set the values through the secret manager used by the deployment. Never commit `.env.local` or the Google JSON key.

Required before the app can read/write persistent data:

- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`
- `SUPABASE_SECRET_KEY` (server only; never send it to the browser or commit it)

The legacy `NEXT_PUBLIC_SUPABASE_ANON_KEY` and `SUPABASE_SERVICE_ROLE_KEY` names remain accepted for existing local projects, but new Supabase projects should use publishable and secret keys.

The built-in AIKIA Wallet mark for a first Google Wallet class is `public/brand/aikia-wallet-program-logo.png`. Once the app has a public HTTPS Vercel URL, the logo URL is `<app-origin>/brand/aikia-wallet-program-logo.png`. Replace it with the venue's approved artwork before customer launch.

Required before Google Wallet API calls can succeed:

- `GOOGLE_WALLET_ISSUER_ID`
- `GOOGLE_WALLET_SERVICE_ACCOUNT_JSON` (the complete service-account JSON as one environment value)
- `GOOGLE_WALLET_PROGRAM_LOGO_URL` (a public HTTPS logo URL)
- `NEXT_PUBLIC_APP_URL` (the canonical HTTPS app origin used in Save-to-Wallet JWT claims)
- `JOIN_RATE_LIMIT_SECRET` (random server-only secret used to create short-lived HMAC fingerprints for public customer sign-up limits)

## Google Wallet issuer setup

1. Create a Google Wallet API Issuer account in Google Pay & Wallet Console.
2. Enable the Google Wallet REST API in its Google Cloud project.
3. Create a service account and JSON key; add its email to the Wallet Issuer as a Developer.
4. Keep the key server-side. Do not upload it to the repository.
5. Create a Loyalty Class and a test Loyalty Object from the authenticated API routes.
6. Add authorized test Google accounts. New Issuers start in demo mode; passes are limited to admins, developers and test accounts until publishing access is granted.
7. Complete the business profile and request publishing access from the Wallet console before serving general customers.

Google's current onboarding, service-account and publishing requirements are linked in `docs/GOOGLE-WALLET-SETUP.md`.

## Database

Apply every file in `supabase/migrations/` to a new Supabase project in number order. `0001` creates tenant-scoped venue/team/member records, reward tiers, an append-only ledger, provider bindings and RLS policies. `0002` adds recorded customer consent and the public sign-up flow's database rate limit. If the database already has `0001`, apply `0002` only.

## Run

```sh
npm install
npm run dev
```

Open `http://localhost:3000`. The home screen and health endpoint describe which environment values are missing. Authenticated operator routes live under `/api/venues/...` and `/api/members/...`.

## Current limits

- Real pass issuance requires the Issuer account, service account access, program logo, app origin and authorized Google test account.
- Demo-mode Google passes are not available to all customers until publishing access is granted.
- Customers can join from `/join/<venue-slug>` and receive a Google Wallet save link when issuance is configured. The owner dashboard shows the venue sign-up link. The form collects only a name and loyalty-program consent; it does not collect phone numbers or payment details.
- The public join flow requires the private `JOIN_RATE_LIMIT_SECRET`. It rate-limits sign-ups per venue and hashed visitor address, and removes old rate-limit rows as new customers join. Add a hosted abuse-control service before a wide public launch.
- The privacy page is starter copy. Replace it with each venue's approved legal name, contact information, retention period and privacy terms before inviting customers.
- Guest OTP/SMS, member self-service, message delivery, venue billing, POS integration and Apple Wallet are not included. Production still needs queued retry for failed Wallet syncs, monitored backups, alerts and an independent security/privacy review.
- A Google Wallet object update can fail after the canonical ledger write. The ledger remains authoritative; the application must report/retry provider synchronization rather than silently changing the ledger.

## Workspace map

- `src/lib/wallet/`: provider-neutral contract and Google implementation; future Apple adapter boundary.
- `src/lib/supabase/`: server and browser Supabase clients.
- `src/app/api/`: authenticated Google Wallet and member-operation endpoints.
- `supabase/migrations/`: database schema and row-level security.
- `docs/`: setup and integration notes.
