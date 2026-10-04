# AIKIA.WALLET repository notes

- The active product lives in `software/`; `demo-service/` is a browser-only buyer prototype and must never be used to store actual member data.
- Preserve the original product direction: venue-branded wallet membership, repeat-purchase rewards, configurable lifetime tiers and exclusive benefits.
- The owner/admin workspace manages venue branding, program rules, tiers and staff invitations. Staff/managers get the restricted member-scanner workflow.
- Model qualifying actions generically so the software can serve cafés, retail, hospitality, salons, fitness, entertainment and other venues.
- Wallet engine: build on **PassKit first** (Google Wallet cards now, Apple once the owner's Apple certificate is uploaded to PassKit). Keep all wallet behavior behind the provider contract in `software/src/lib/wallet/` so the engine can be switched to our own direct Google/Apple adapters by config. Active plan: `docs/BUILD-BLUEPRINT.md`.
- Do not put secrets, real member data, service-account JSON, or Supabase service-role keys in Git, browser code, logs, screenshots, or chat.
- Enforce authorization in route handlers and Supabase row-level security. Never treat the role switch in the local demo as production authentication.
- The append-only ledger is authoritative. Google Wallet is a synchronized display of the venue's membership data.
- Documents under `docs/strategy/archive/` are background only; `docs/BUILD-BLUEPRINT.md` is the active plan. Verify PassKit API paths against docs.passkit.io, never guess them.
- Keep modules named and scoped so Claude Code and other agents can navigate the project without hidden setup.
