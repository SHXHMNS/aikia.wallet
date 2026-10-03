# AIKIA.WALLET repository notes

- The active product lives in `software/`; `demo-service/` is a browser-only buyer prototype and must never be used to store actual member data.
- Preserve the original product direction: venue-branded wallet membership, repeat-purchase rewards, configurable lifetime tiers and exclusive benefits.
- The owner/admin workspace manages venue branding, program rules, tiers and staff invitations. Staff/managers get the restricted member-scanner workflow.
- Model qualifying actions generically so the software can serve cafés, retail, hospitality, salons, fitness, entertainment and other venues.
- Google Wallet is the current pass provider. Keep all wallet behavior behind the provider contract so Apple Wallet can be added in a separate adapter later.
- Do not put secrets, real member data, service-account JSON, or Supabase service-role keys in Git, browser code, logs, screenshots, or chat.
- Enforce authorization in route handlers and Supabase row-level security. Never treat the role switch in the local demo as production authentication.
- The append-only ledger is authoritative. Google Wallet is a synchronized display of the venue's membership data.
- Older PassKit documents under `docs/strategy/archive/` are historical only and must not override the current Google-first direction.
- Keep modules named and scoped so Claude Code and other agents can navigate the project without hidden setup.
