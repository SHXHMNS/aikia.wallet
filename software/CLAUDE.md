# AIKIA.WALLET software workspace

This is the software workspace. The sibling `../demo-service/` is a browser-only buyer prototype; do not treat its localStorage data or QR art as production logic.

## Product and provider rules

- Google Wallet loyalty cards are the active provider. Use Google's **Loyalty Class/Object** API, not Generic passes.
- Keep provider-specific work behind `src/lib/wallet/WalletProvider`. Future Apple Wallet support belongs in a separate adapter and must not leak Apple-specific assumptions into the ledger or venue/member model.
- Never put Google service-account JSON, private keys, Supabase service-role keys or other secrets in browser code, committed files, screenshots or chat. Only `.env.example` is safe to commit.
- Google demo Issuers can only issue to authorized test users until Google grants publishing access. Treat live public issuance as a separate launch gate.
- Stamp balance is derived from append-only `ledger_transactions`. A correction is a new compensating transaction. Every stamp request uses an idempotency key.
- Every venue-owned row has `venue_id`; rely on database RLS as well as server-side role checks. Never trust a client-supplied venue scope by itself.
- Do not store phone numbers or other member PII inside Google object IDs or barcodes. Use opaque random identifiers.
- Only an authenticated venue owner/admin may create a Google Wallet class. Only authorized venue staff may issue a member pass or record a stamp.

## Current stage

The current software slice includes an authenticated Supabase operator app, owner and staff experiences, public customer enrollment with consent, venue-scoped schema/RLS, generic reward and tier rules, an append-only activity ledger and a Google Wallet class/object adapter. This is a controlled-pilot foundation, not a public launch. It has not been verified against a configured Supabase project or Google Wallet issuer. Keep secrets in `.env.local` for local work and the deployment provider's secret manager in hosted environments.

## Working agreements

- Keep the project easy for Claude Code and other coding agents to navigate; prefer clear modules and short setup instructions.
- Use the App Router and TypeScript. Provider integrations are server-only.
- Do not claim a route is operational until it has been exercised against a configured test Issuer and database.
- Run package scripts only when the user asks for verification or when a workflow explicitly requires them. Record configuration blockers clearly.
