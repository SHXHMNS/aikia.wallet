# AIKIA.WALLET — build blueprint (the real app)

This is the active, step-by-step plan for taking `software/` from code on a laptop to a live product. It replaces every file in `docs/strategy/archive/`.

**Ground rules**

- **We build on PassKit first.** PassKit (passkit.com) is a rented "pass engine": it creates, signs and updates the wallet cards. Everything a venue, staff member or guest touches stays **ours**: the join page, staff scanner, owner/admin dashboards, tiers and the Supabase ledger (the record of truth).
- **The engine can be swapped.** All wallet calls go through one adapter in `software/src/lib/wallet/`. Today the engine is `passkit`. Later, one setting (`WALLET_ENGINE=direct`) moves us to our own engine (the direct Google Wallet API code that already exists, plus an Apple adapter). Dashboards, members, tiers and the ledger do not change.
- **Google Wallet now, Apple when the account arrives.** PassKit issues Google Wallet cards without a Google developer account. Apple cards need a certificate from **your own** Apple Developer account, which PassKit then uses. Once it's uploaded, the same members get both buttons.
- The product starts from a **demo base**: one demo venue with a sample program (café preset: Ink / Chrome / Pink tiers). Everything a buyer sees, from names and colours to the action, reward, tiers and logo, comes from configuration. Re-branding the whole thing for AIKIA or any client is a config change, not a code rewrite.
- Secrets (Supabase secret key, Google JSON key, later the Apple `.p12`) live only in `.env.local` on your Mac and in Vercel's environment variables. Never commit, paste in chat or screenshot them.

> Screens in Supabase, Google and Vercel change their labels now and then. If a button name doesn't match exactly, look for the closest match in the same menu.

---

## ⭐ Only your part is left: credentials (updated 5 Oct 2026)

Everything else is built, deployed and connected. **Live app: https://aikia-wallet.vercel.app.** Its home page lists, with ✓ / •, every setting that is still missing.

Paste each value in **two places**: Vercel → project **aikia-wallet** → Settings → **Environment Variables** → **Add Environment Variable** (type **Secret**), and your Mac's `software/.env.local` (open it with `open -e ~/Desktop/aikia.wallet/software/.env.local`).

| Name | Where you get it |
|---|---|
| `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` | Supabase → project → Project Settings → **API Keys** → Publishable key |
| `SUPABASE_SECRET_KEY` | Same page → **Secret key** (create one if none) |
| `JOIN_RATE_LIMIT_SECRET` | Already in your `.env.local`. Copy the same value into Vercel. |
| `CRON_SECRET` | Already in your `.env.local`. Copy the same value into Vercel. |
| `PLATFORM_ADMIN_EMAILS` | The email you sign in with, to open `/platform` |
| `PASSKIT_API_KEY`, `PASSKIT_API_SECRET` | After you create the PassKit account: Developer Tools → REST credentials |
| `PASSKIT_PROGRAM_ID` | PassKit → your program's settings |

After adding them in Vercel: **Deployments → ⋯ → Redeploy**. Then open the live app, sign in with your email and create your first venue.

Already done for you: Supabase migrations 0001–0003; Supabase login Site URL and redirect URLs; Vercel project (root `software`) with `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_APP_URL`, `WALLET_ENGINE` and `PASSKIT_API_BASE_URL`; auto-deploy on every push; GitHub CI (type check, tests, build).

---

## Where you are now (5 Oct 2026)

| Step | Status |
|---|---|
| Supabase project created, SQL migrations run | ✅ you did this |
| GitHub repo `SHXHMNS/aikia.wallet` | ✅ exists, local `main` matches GitHub |
| Google Wallet issuer account | ✅ you did this (used later for the own-engine switch, Phase 11) |
| PassKit account (45-day free trial) | ⬜ Phase 5 |
| `software/.env.local` | ✅ created (Supabase URL + random secrets); your keys still to paste |
| App running on your Mac against Supabase | ⬜ Phase 3 |
| App live on Vercel | ✅ https://aikia-wallet.vercel.app, deploys on every push |
| PassKit adapter in the app | ✅ built (Phase 7.0), waiting for PassKit keys |
| First real card saved on an Android phone | ⬜ Phase 6 |
| Re-brandable base + engine switch | ✅ platform config, engine switch and business presets built |
| Apple Wallet (through PassKit) | ⬜ Phase 9, after the Apple Developer account |
| Public launch | ⬜ Phase 10 |
| Optional: move to our own engine | ⬜ Phase 11, around 25+ venues |

---

## Phase 1 — Prepare your Mac (10 min)

1. Open **Terminal** (⌘ Space, type `Terminal`, Enter).
2. Check Node.js: run `node -v`. You need **v20 or newer** (v22 LTS is ideal). If it's missing or older, go to <https://nodejs.org>, click **LTS**, download the macOS installer, run it, then close and reopen Terminal.
3. Check git: run `git -v`. If macOS offers to install the Command Line Tools, click **Install**.
4. Go to the app folder and install its packages:
   ```bash
   cd ~/Desktop/aikia.wallet/software
   ```
   ```bash
   npm install
   ```
   Some "warn" lines are fine. An "ERR!" line is not, so send it to Claude.

---

## Phase 2 — Supabase: confirm the database and collect keys (15 min)

### 2.1 Confirm both migrations ran
1. Go to <https://supabase.com/dashboard> and click your project.
2. In the left sidebar, click **SQL Editor**, then **+ New query**.
3. Paste this and click **Run**:
   ```sql
   select table_name from information_schema.tables
   where table_schema = 'public' order by table_name;
   ```
4. You should see `ledger_transactions`, `members`, `venue_team_members`, `venue_tiers`, `venues` and `wallet_passes`, **plus** the sign-up rate-limit table from migration `0002`.
   - If the `0002` table is missing: open `software/supabase/migrations/0002_public_customer_join.sql` on your Mac, copy all of it, paste it into a new query and click **Run**.
   - Never re-run `0001` on a database that already has these tables.

### 2.2 Turn on email sign-in and set the redirect URLs
The app signs people in with a **magic link** (an email login link, no password).
1. Click **Authentication** in the sidebar, then **Sign In / Providers**. Make sure **Email** is enabled.
2. Click **Authentication → URL Configuration**:
   - **Site URL:** `http://localhost:3000` (you'll change this to the Vercel URL in Phase 4).
   - **Redirect URLs:** click **Add URL** and add `http://localhost:3000/auth/callback`.
   - Click **Save**.
3. Supabase's built-in email sender only allows a few emails per hour, which is fine for testing. Before inviting real staff, set up your own sender (Phase 10).

### 2.2b Run migration 0003
Open `software/supabase/migrations/0003_wallet_engines.sql`, paste it into **SQL Editor → + New query** and click **Run**. It lets one member hold a card per wallet and adds the per-venue PassKit program ID.

### 2.3 Copy the three values the app needs
1. Click the **Connect** button at the top of the project (or **Project Settings → Data API**). Copy the **Project URL** (`https://xxxx.supabase.co`).
2. Go to **Project Settings → API Keys**:
   - **Publishable key** (starts `sb_publishable_`). This one is safe in the browser.
   - **Secret key** (starts `sb_secret_`). If none exists, click **+ New secret key** and name it `aikia-wallet-server`. **Server only, never share it.**
   - If you only see the older "anon" / "service_role" keys, those work too. The app accepts both naming styles.

---

## Phase 3 — Run the real app on your Mac (15 min)

### 3.1 Create `.env.local`
```bash
cd ~/Desktop/aikia.wallet/software
```
```bash
cp .env.example .env.local
```
```bash
open -e .env.local
```
TextEdit opens. Fill in:

```
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_SUPABASE_URL=<Project URL from 2.3>
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=<sb_publishable_…>
SUPABASE_SECRET_KEY=<sb_secret_…>
JOIN_RATE_LIMIT_SECRET=<see below>
WALLET_PROVIDER=google              ← becomes WALLET_ENGINE=passkit in Phase 7
(leave every GOOGLE_WALLET_… and PASSKIT_… line empty for now)
```
To get a random `JOIN_RATE_LIMIT_SECRET`, run this and paste the output:
```bash
openssl rand -base64 32
```
Save with ⌘S and close TextEdit. `.env.local` is already in `.gitignore`, so it will never be pushed.

### 3.2 Start it
```bash
npm run dev
```
1. Open <http://localhost:3000/api/health>. You want `"databaseConfigured": true` and `"customerJoinRateLimitConfigured": true`. The wallet engine shows "not configured" for now.
2. Open <http://localhost:3000>. Enter your email and click the magic link that arrives. Use the same browser.
3. You'll see **"Set up your first venue."** Enter a name such as `Demo Café` and a URL name such as `demo-cafe`, then click **Create owner workspace**. This is your **demo base**.
4. Click through **Overview → Members → Staff scanner → Brand & tiers → Team access**. This is the owner/admin dashboard.
5. **Test the staff dashboard:** under **Team access**, invite a second email you own. Open that invite in a private window (⇧⌘N). You should see **only** the Staff counter.
6. **Test customer sign-up:** under **Members**, click **Copy customer sign-up link** and open it. Join as a guest, then find that member in the staff scanner and click **Record 1 …**.

If any step fails, copy the red text from the page or Terminal and send it to Claude.

---

## Phase 4 — Put it online with Vercel (20 min)

Wallet cards need a public `https://` address for logos, links and PassKit's update callbacks, so deploy before wiring in the engine.

1. Go to <https://vercel.com>, click **Sign Up**, then **Continue with GitHub**, and approve access.
2. Click **Add New… → Project**.
3. Under **Import Git Repository**, find `SHXHMNS/aikia.wallet` and click **Import**. If it isn't listed, click **Adjust GitHub App Permissions**, give Vercel access to that repo, and come back.
4. On the configure screen:
   - **Root Directory:** click **Edit**, choose **`software`**, click **Continue**. *This matters most: the app is in a subfolder.*
   - **Framework Preset:** Next.js (auto-detected).
   - Open **Environment Variables**, then paste every line from your `.env.local` (Vercel accepts a whole `.env` paste) **except** set `NEXT_PUBLIC_APP_URL` to a placeholder for now.
5. Click **Deploy** and wait about 2 minutes. You get a URL like `https://aikia-wallet-xxxx.vercel.app`.
6. Set the real URL:
   - Vercel → your project → **Settings → Environment Variables**. Set `NEXT_PUBLIC_APP_URL` = `https://aikia-wallet-xxxx.vercel.app` and click **Save**.
   - Vercel → **Deployments**, click **⋯** on the latest deployment, then **Redeploy**.
7. Tell Supabase about the live URL: **Authentication → URL Configuration**:
   - **Site URL:** `https://aikia-wallet-xxxx.vercel.app`
   - **Redirect URLs:** add `https://aikia-wallet-xxxx.vercel.app/auth/callback`. Keep the localhost one for development.
8. Open `https://aikia-wallet-xxxx.vercel.app/api/health` and check it matches what you saw locally.
9. From now on, every `git push` to `main` redeploys automatically.

*(Later, Phase 10: point `wallet.aikia.world` at it under Vercel → Settings → Domains.)*

---

## Phase 5 — PassKit: account, card design, API keys (about 2 hours)

> Button names come from PassKit's help pages. If one differs, use the closest match in the same menu.

### 5.1 Create the account
1. Go to <https://passkit.com> and start the **free trial** (45 days) with your company email (for example `connect@aikia.world`).
2. Confirm the email PassKit sends, then log in at <https://app.passkit.com>.

### 5.2 Create the demo program (the "base")
1. In the portal, create a **new project**, choosing the **Membership / Loyalty** type. Name it `aikia demo`.
2. It starts as a **draft** (PassKit's test mode). Draft cards are **deleted after 48 hours** and a new account can issue only a few, so drafts are for checking the design, not for meetings.

### 5.3 Design the card (Google design first)
1. Open **Design**. There is an **Apple** design and a **Google** design; do Google now and Apple in Phase 9.
2. Upload the AIKIA logo (PNG, transparent) and a wide banner image.
3. Colours: background **Ink `#14111F`**, text **Frost `#ECEEF5`**, labels **Hyper Pink `#FF3D9A`**.
4. Card name: `Your Café` (each venue's real name replaces it later, from our dashboard).
5. Barcode: **QR code**.
6. Fields: **Member name**, **Points** (label it `Stamps`), **Tier**, **Offer** (one text for everyone, start with `Welcome to the club`). On the back: hours, address and `Powered by aikia.wallet`.

**Barcode:** keep PassKit's default barcode content (the pass/member ID). Our staff scanner recognises it.

### 5.4 Create the three tiers
Add the tiers **Ink** (the starting tier), **Chrome** and **Pink**, each with its own colours. Give each tier the **ID** `ink`, `chrome` and `pink` (our tier name in lowercase). Our dashboard stays in charge and tells PassKit when a member moves up. If you must use other IDs, set `PASSKIT_TIER_IDS`, for example `{"Ink":"base"}`.

### 5.5 Test the draft on Android
1. Open the project's sign-up / distribution link on an Android phone, fill it in and tap **Add to Google Wallet**.
2. Check the logo, colours and every field. Fix and repeat.
3. We won't use PassKit's own sign-up page or its PassReader scanner app for real venues, because **our** join page and staff scanner replace them. They're only for this check.

### 5.6 Get the API credentials (for our app)
1. Go to **Developer Tools**: <https://app.passkit.com/app/account/developer-tools>.
2. Click **GET REST Credentials** (it may be named slightly differently). Note the **API key**, **API secret** and the **API region / base URL** shown for your account.
3. Copy the **Program ID** and each **Tier ID** from the project's settings.
4. Put them into `.env.local` and into Vercel → Settings → Environment Variables. Never paste them in chat:
   ```
   WALLET_ENGINE=passkit
   PASSKIT_API_BASE_URL=<the region URL from Developer Tools>
   PASSKIT_API_KEY=<key>
   PASSKIT_API_SECRET=<secret>
   PASSKIT_PROGRAM_ID=<program id>
   ```
   Tier IDs get mapped to our tiers from the dashboard (Phase 7), so they don't go in env.
5. Redeploy on Vercel.

### 5.7 Going live (needs Apple)
PassKit's **Launch** step asks you to choose an **Apple certificate**. Until the Apple Developer account exists (Phase 9), you build and demo with **draft** cards (re-added every 48 hours). **Ask PassKit support in writing** whether a project can go live for Google Wallet only, before the Apple certificate. Also ask whether reselling under the AIKIA brand is allowed on your plan.

## Phase 6 — First real pass, end to end (20 min)

You need an Android phone with Google Wallet. This needs the PassKit adapter from Phase 7.0 in the deployed app.

1. On the live URL, sign in as owner and open **Members**, then copy the customer sign-up link.
2. On the Android phone, open that link in Chrome. Enter a name, tick consent and submit, then tap **Save to Google Wallet** and **Save**.
3. On your laptop, sign in as the **staff** account and go to the **Staff scanner**. Click **Open QR camera** and scan the QR on the phone's wallet card (or type its member code). Click **Record 1 …**.
4. Within seconds the card in Google Wallet should show the new balance. Repeat until the reward unlocks, then click **Redeem**.
   Our ledger is updated first, then the app tells PassKit the new points/tier, and PassKit updates the card.
5. Things to check: what happens if you scan twice quickly (only one action should be recorded), what a removed member's card does, and the card's look after you change the colour under **Brand & tiers**.

**When this works, the core product is real.** Everything after this is making it re-brandable, adding Apple, and getting it launch-ready.

---

## Phase 7 — Build work: PassKit adapter, re-brandable base, engine switch (Claude builds this in the code)

These are code changes in `software/`. Each one is a separate commit you can review.

### 7.0 PassKit adapter ✅ built
- New `src/lib/wallet/passkit.ts` implementing the existing `WalletProvider` contract: create or update the program and tiers, enrol a member, push points/tier changes, and return the member's **Google** (later also **Apple**) save link.
- Exact PassKit endpoints and the JWT signing are taken from docs.passkit.io and PassKit's Postman collection, never guessed.
- Members enrol through **our** `/join/<venue>` page. PassKit never shows a venue or guest its own screens.

### 7.1 Platform brand config ✅ built (`src/config/platform.ts`, `NEXT_PUBLIC_PLATFORM_*`)
- Add `src/config/platform.ts`: the product name, logo, colours, support email, legal entity and default locale, read from env vars (`PLATFORM_NAME`, `PLATFORM_LOGO_URL`, `PLATFORM_PRIMARY_COLOR`, …) with AIKIA as the default.
- Replace every hard-coded `AIKIA.WALLET` / colour in the dashboard, login, join, privacy and terms pages with that config.
- **Result:** a new white-label deployment means a new Vercel project plus different env values. No code edits.

### 7.2 Venue presets ✅ built (`src/config/presets.ts`)
- Add `src/config/presets.ts` with café, restaurant, salon, fitness, retail, hotel and entertainment presets. Each sets the action label, balance label, reward target, reward name, tier names/thresholds/benefits and colours.
- The "Set up your first venue" screen gets a **Business type** picker that applies a preset. Owners can still edit everything afterwards in **Brand & tiers**.
- The demo base becomes "the café preset plus demo sample data", switchable to any other preset.

### 7.3 The engine switch ✅ built (`WALLET_ENGINE`, migration `0003_wallet_engines.sql`)
- `WALLET_ENGINE=passkit` (today) or `direct` (later). With `direct`, wallets are chosen by `WALLET_PROVIDERS=google` and later `google,apple`, using the existing `google.ts` and a future `apple.ts`.
- **Migration `0003`:** `wallet_passes` records the **engine** and the **wallet** (google/apple) for each card, with one row per member per wallet. Today the table allows only one pass per member, which would block Google and Apple together. The `provider` check must also allow `passkit`.
- `member-wallet-sync.ts` updates **every** card a member holds through whichever engine issued it, instead of hard-coding `'google'`.
- The join page and member screen show **Add to Google Wallet** and, once enabled, **Add to Apple Wallet**.
- `/api/health` reports the engine and each wallet's status.
- **Switching engines later** = issue new cards on the new engine (members re-add once; a one-off migration script plus a "re-add your card" link), then turn the old engine off. Our member records and ledger stay the same throughout.

### 7.4 Reliability ✅ built
- A retry job (Vercel Cron, **daily** on the free Hobby plan) re-syncs passes where `sync_error` is set. It needs `CRON_SECRET`.
- ✅ Done: `proxy.ts` moved to `src/proxy.ts`, so the security headers and session refresh are now active. Confirm The app uses `src/`, so it may need to move to `src/proxy.ts`. Check that the `Content-Security-Policy` response header is present on the live site.

### 7.5 Dashboard gaps ✅ built (admin/staff invites, remove member, `/platform` console via `PLATFORM_ADMIN_EMAILS`)
- Invite as **admin** or **staff** (today invites always create staff).
- Remove a team member; owner-only actions (transfer ownership, delete venue).
- **AIKIA super-admin console:** `/platform` shows all venues, member counts and sync errors to emails listed in `PLATFORM_ADMIN_EMAILS`. This is separate from venue roles.

### 7.6 Quality gates ✅ built (`.github/workflows/ci.yml`, `npm test`)
- A GitHub Action on every push: `npm ci`, a type check and `npm run build`. Vercel only deploys green builds.
- Basic tests for the ledger rules (stamp, reward unlock, redeem, idempotency) and the role checks.

---

## Phase 8 — Make the demo-service match the real product

`demo-service/` is the sales demo you show buyers. Once 7.1–7.2 land, it should load the **same presets** (café, salon, gym …) and brand config, so the demo and the real app never drift apart. It keeps using fictional, browser-only data.

---

## Phase 9 — Apple Wallet (when you have the Apple Developer account)

### 9.1 Join Apple
1. Go to <https://developer.apple.com/programs/enroll/> and enrol (US$99 per year). Enrolling as an individual is fastest; an organisation needs a D-U-N-S number. Approval takes 1 to 2 days, sometimes longer.

### 9.2 Connect Apple to PassKit (about 20 minutes)
1. In PassKit, open **Certificates** and click **ADD CERTIFICATE**. A file called `cert.certSigningRequest` downloads.
2. At <https://developer.apple.com/account>, go to **Certificates, IDs & Profiles → Identifiers → +**, choose **Pass Type IDs** and click **Continue**. Description: `aikia wallet`. Identifier: `pass.world.aikia.wallet`. Click **Register**. **This identifier can never change** without every guest re-adding their card.
3. Open the new Pass Type ID and click **Create Certificate**. Upload the `cert.certSigningRequest` from step 1, click **Continue**, then download `pass.cer`.
4. Back in PassKit → **Certificates → ADD CERTIFICATE → I ALREADY HAVE A CSR**, then drag in `pass.cer`.
5. In PassKit **Design → Apple Design**, build the Apple card to match the Google one. For lock-screen messages, set the Stamps field's message to `You now have %@ stamps`.
6. **Launch** the project with that certificate. The live project starts empty, so add your test cards again.

### 9.3 Code
Nothing new in the app except turning on the Apple button. PassKit returns the Apple link for the same member. Both wallets now run side by side, with no changes to venues, tiers, the ledger or dashboards.

### 9.4 Test
Use an iPhone: join, tap **Add to Apple Wallet**, scan, and check that the lock-screen message and balance update.

*(If we later move to our own engine, Phase 11 reuses the same Pass Type ID with a certificate we hold ourselves.)*

## Phase 10 — Launch-ready checklist

1. **PassKit live:** the project is launched (Phase 9.2), a payment method is on file, and the plan covers your card volume. Get written confirmation that white-label resale is allowed.
2. **Domain:** in Vercel → Settings → **Domains**, add `wallet.aikia.world` and create the DNS record Vercel shows at your domain registrar. Then update `NEXT_PUBLIC_APP_URL` and the Supabase URL Configuration to the new domain.
3. **Email sender:** create an account at <https://resend.com> and verify `aikia.world`. In Supabase → **Authentication → Emails → SMTP Settings**, enter Resend's SMTP details. Customise the magic-link and invite email templates.
4. **Legal:** replace the starter `/privacy` and `/terms` text with real terms for each venue (name, contact, retention period). In India, review this against the DPDP Act with a lawyer.
5. **Backups:** upgrade the Supabase plan if you need point-in-time recovery before real customers.
6. **Monitoring:** use error tracking (for example Sentry) and Vercel's logs. Get alerts when `sync_error` rows build up.
7. **Abuse protection:** add managed bot protection (for example Cloudflare Turnstile) to the public join page.
8. **Security review** before the first paying venue.
9. **Pilot:** run one real venue for 2–4 weeks, fix what staff struggle with, then sell.

---

## Phase 11 — Optional: move to our own engine (around 25+ venues, or when PassKit costs or limits hurt)

The direct Google Wallet code (`src/lib/wallet/google.ts`) already exists, and your Google Wallet issuer account is ready for it.
1. **Google:** in <https://console.cloud.google.com>, create a project, enable the **Google Wallet API**, then go to **IAM & Admin → Service Accounts → Create**. Under **Keys → Add key → JSON**, download the key and keep it outside the repo. In <https://pay.google.com/business/console>, under **Users**, invite the service-account email as **Developer**. Set `GOOGLE_WALLET_ISSUER_ID`, `GOOGLE_WALLET_SERVICE_ACCOUNT_JSON` (one line) and `GOOGLE_WALLET_PROGRAM_LOGO_URL` in Vercel. Then complete the business profile and **request publishing access**.
2. **Apple:** create a certificate for the same `pass.world.aikia.wallet` on your Mac (Keychain Access → Certificate Assistant → Request a Certificate…), export it as `.p12` and download Apple's WWDR G4 certificate. Claude builds `apple.ts`: `.pkpass` signing, Apple's pass web service routes and APNs updates.
3. Set `WALLET_ENGINE=direct` and `WALLET_PROVIDERS=google,apple`, run the card re-issue script, send members the "re-add your card" link, then cancel PassKit.

---

## How we work from here

- Do the clicks in Phases 1–5 in order. Phase 6 runs once Claude's PassKit adapter (7.0) is deployed. Stop at the first failure and send Claude the exact error text (never the keys).
- In parallel, Claude builds Phase 7 in the repo, PassKit adapter first, in small commits you can review and push.
- Apple (Phase 9) starts the day the developer account is approved.
