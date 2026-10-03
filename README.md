# AIKIA.WALLET

AIKIA.WALLET is a configurable digital loyalty platform for cafés and other venues. Members carry a venue-branded loyalty card in Google Wallet, earn progress from repeat visits or purchases, move through configurable tiers, and unlock venue-defined benefits. Apple Wallet is planned behind the same provider boundary.

## Project map

- [`software/`](software/README.md) — Next.js operator platform, authenticated owner and staff dashboards, Google Wallet integration, Supabase schema and API routes.
- [`demo-service/`](demo-service/README.md) — self-contained, fictional buyer demo with owner and staff workspaces, editable branding and tiers, guest join, member lookup, purchase/reward flow, and browser-local sample data.
- [`docs/sales/`](docs/sales/) — buyer pitch and sales playbook in HTML and PDF.
- [`docs/strategy/archive/`](docs/strategy/archive/) — earlier product, PassKit, and launch blueprints retained as history. The current implementation is Google Wallet first; do not follow old PassKit steps as the active integration plan.
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — current domain model, roles, provider seam and security approach.
- [`marketing/`](marketing/) — launch film, source composition, and prior campaign files.

## Run the buyer demo

The demo requires no account or wallet credentials. It uses fictional sample data stored only in the current browser profile.

```sh
python3 -m http.server 4173 --directory demo-service
```

Open [http://localhost:4173](http://localhost:4173). Use the dashboard switcher to move between the **Owner dashboard** and the focused **Staff dashboard**. The owner workspace controls the venue identity, reward target and Ink / Chrome / Pink tier ladder. The staff workspace looks up a sample member, records qualifying purchases, unlocks rewards and records redemptions. The camera reader can read QR codes in supported browsers; the member-code field remains available for the sample flow.

The demo is a sales prototype. It does not process real members, issue real Wallet passes, send messages, or provide account security or cloud persistence.

## Run the authenticated software

See [`software/README.md`](software/README.md) for setup. The live operator app needs a Supabase project and, for real passes, a Google Wallet Issuer, service-account credentials and public HTTPS artwork. Apple Wallet is not active yet.

```sh
cd software
cp .env.example .env.local
npm install
npm run dev
```

Apply `software/supabase/migrations/0001_wallet_core.sql` to a development Supabase project before using the live dashboard. Keep all real keys in `.env.local` or the deployment secret manager. Never commit credentials or real customer data.

## Development status

The buyer demo is ready for venue presentations using sample data. The authenticated Google-first software and database/API foundation are under active development and still need connection to the owner's Supabase and Google Wallet accounts, venue onboarding, operational hardening and a live deployment before customer use. Google demo issuers are limited to authorized test users until publishing access is granted.

The database and loyalty rules use generic qualifying actions, balances, rewards and tiers. A café uses coffee purchases as its first preset; retail, hospitality, fitness, salons and other eligible venues can set their own qualifying action, balance label, reward rule, brand theme and tier benefits.

## Security posture

The implementation uses server-side secrets, authenticated owner/staff roles, venue-scoped row-level security, opaque scan tokens, an append-only activity ledger, idempotent purchase recording and a separate staff scanner view. These controls reduce risk; no software can promise zero breaches. A production launch still needs independent security review, privacy/legal review, rate limiting, monitored backups, operational alerting and incident-response procedures.
