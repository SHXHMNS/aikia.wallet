# Go live: credit, gifts, weather moods, metallic cards (18 Oct 2026)

Everything below is built and tested on the computer (type check, 17 unit tests, production build). It is **not live yet**: it needs your one database step and a deploy. Do the steps in order.

## What was added

| Feature | Where you see it |
|---|---|
| **Metallic cards** (Ink black, Chrome silver, Pink), designed in Canva, small `aikia.wallet` branding. The card changes colour when the tier changes. | Wallet card; art in `software/public/brand/`, Canva designs: Ink https://canva.link/gx4u4xnl4nnx2hu · Chrome https://canva.link/11rztekwj124utp · Pink https://canva.link/t1vgg1a5nn24h1d |
| **Prepaid credit**: guest pays the café (UPI/cash/card), gets bonus credit (e.g. pay ₹2,000, get ₹2,300). | Staff scanner → Credit → *Record top-up* |
| **Scan to pay**: staff scan the card and take the bill from credit. Small bills (default up to ₹300) need only the scan; bigger bills need the guest's live **Pay QR**, which changes every 45 seconds and works once (screenshots useless). Daily limit per guest. Paying also adds the visit/stamp. | Staff scanner; guest's *My card* page |
| **Send a gift ("send a coffee")**: guest sends 1 or 2 items from their credit, or their free reward, to a friend. Friend gets a link with a one-time QR; staff scan it and hand over the item. Max gifts per day; unused gifts expire and go back to the sender. Never money. | Guest *My card* page → *Send a gift*; friend's `/gift/...` page |
| **My card page**: private page per guest (balances, Pay QR, top-up packs, gifts). Linked from the back of the wallet card and shown after joining. | `/me/<private link>` |
| **Weather-mood geofencing**: each morning the app checks the weather at the café and changes the nearby (geofence) message: rain → "It's raining ☔ Come in, grab a hot coffee", hot, cool, clear. *Send to all cards now* for demos. | Offers & alerts → Weather mood messages |
| **Credit & gifts settings + money report** (loaded, spent, gifted, owed to guests), reverse a wrong payment/top-up. | Owner dashboard → *Credit & gifts* |
| **Apply card design** button (pushes the metallic design to PassKit and refreshes all cards). | `/platform` |

## Step 1: run the database update (you, 3 minutes)

I'm not allowed to change your live database myself, so this click is yours.

1. Open https://supabase.com/dashboard and click the **aikia.wallet** project.
2. Left sidebar → **SQL Editor** → **+ New query**.
3. On this PC open `Desktop\RECOVERED-PROJECTS\aikia.wallet\software\supabase\migrations\0006_credit_gifts_moods.sql` (right-click → Open with → Notepad), press **Ctrl+A**, **Ctrl+C**.
4. Paste into the SQL editor (**Ctrl+V**) and click **Run**. You should see "Success. No rows returned".
   - If it asks to confirm a "destructive operation", that's because of the `alter table` lines; click **Run this query**.
   - If you get any red error, copy the text and send it to me.

## Step 2: deploy (tell me "deploy")

The code is committed on branch `feat/credit-gifts-moods`. Once Step 1 is done, say **deploy** and I'll merge it to `main`; Vercel then publishes it in about 2 minutes. (Don't deploy before Step 1: the live app would look for the new columns and fail.)

## Step 3: switch the new things on (you, 10 minutes, on the live site)

1. **Card design:** sign in at https://aikia-wallet.vercel.app/platform → **Apply card design** → OK. Wait for "Tier ink/chrome/pink: metallic design applied". Every card updates.
2. **Credit:** dashboard → **Credit & gifts** → Credit: **On**. Check the packs (₹500→550, ₹1,000→1,125, ₹2,000→2,300), the scan-only limit (₹300) and daily limit (₹5,000). Add gift items, for example *Cappuccino ₹180*, *Cold coffee ₹220*. **Save**.
3. **Weather moods:** **Offers & alerts** → make sure the café location is saved (paste the Google Maps link) → Weather messages: **On** → edit the four messages if you like → **Save weather messages** → **Check today**.

## Step 4: the 5-minute café demo

Use two phones: yours (staff) and a second one (guest).

1. Guest scans the counter QR poster (`/join/<venue>/poster`), types a name, taps **Add to Google Wallet**, then **Open my card**.
2. Staff: **Staff scanner** → scan the card → **Top up** → ₹2,000 pack → UPI → **Record top-up**. Guest's card shows ₹2,300.
3. Small bill: type ₹180 → **Pay ₹180 from credit**. Card updates, stamp added.
4. Big bill: type ₹650. Guest taps **Show pay code**; staff scan that QR → pay. Show that a screenshot of the code fails the second time.
5. Gift: guest → **Send a gift** → Cappuccino → **Send gift** → share on WhatsApp to a friend. Staff scan the friend's gift QR → "Hand over 1 × Cappuccino".
6. Weather: **Offers & alerts** → **Send to all cards now**. The guest's phone shows the rain/heat message.
7. Owner: **Credit & gifts** shows loaded / spent / owed.

## Free cards while you wait for Google and Apple

You're on PassKit, so cards work today **without** Google business verification or Apple. Notes:
- My notes from 8 Oct say a payment method was added on PassKit and the 5-card draft limit was lifted. **Check** in PassKit (app.passkit.com → your program) that the project is not a 48-hour "draft"; if it still is, cards disappear after 48 hours, so re-add before each meeting.
- The PassKit free trial started about 5 Oct (45 days, ends around **19 Nov**). Check your plan in PassKit → Billing.
- Keep demo cards to 5–6 test members (you, your partner, a test phone).

## Google business profile (to use our own Google engine later)

Not needed for PassKit cards. Needed before we switch `WALLET_ENGINE=direct` (our own engine, cheaper at scale).
1. Go to https://pay.google.com/business/console and sign in as **connect@aikia.world** (account 2, `/u/1`).
2. **Business profile**: fill in legal business name, address in Vadodara, website `https://aikia.world`, contact email and phone. Save. If it asks for a **payments profile** verification, upload the documents it asks for (PAN / GST / address proof). Google reviews this in a few days.
3. **Google Wallet API** → your issuer → complete the 3 publishing steps, then **Request publishing access**. Until approved, only test users you add can save cards from our own engine.
4. Tell me when it says approved; I'll switch the engine and run *Issue missing cards*.

## Apple Wallet (space is ready)

The app already shows **Add to Apple Wallet** as soon as Apple is switched on. Steps when you're ready:
1. Enrol at https://developer.apple.com/programs/enroll/ (US$99/year; individual is fastest).
2. In PassKit → **Certificates → ADD CERTIFICATE** → download `cert.certSigningRequest`.
3. Apple Developer → Certificates, IDs & Profiles → Identifiers → **+** → **Pass Type IDs** → identifier `pass.world.aikia.wallet` (never change it) → **Create Certificate** → upload the CSR → download `pass.cer`.
4. PassKit → Certificates → **I ALREADY HAVE A CSR** → upload `pass.cer`. In PassKit Design → Apple, match the Google card.
5. Vercel → aikia-wallet → Settings → Environment Variables → add `PASSKIT_APPLE_ENABLED` = `true` → Redeploy. Done: both buttons appear, same members.

## Before taking real money for credit

The credit feature is built as a closed loop (one café only, no cash-out, gifts are items not money, daily caps). That is the shape the RBI has so far treated as outside prepaid-wallet licensing, but the RBI's April 2026 draft may change it. **Get a lawyer's written opinion before any café takes real top-ups**, and ask your CA about GST on top-ups. Demos and pilots without real money are fine. The Credit & gifts screen shows this reminder.

## Not done yet

- Online top-up (guest pays on their phone via the café's Razorpay/UPI link): needs the café's payment account. Today top-ups are paid at the counter and recorded by staff.
- The browser-only sales demo (`/demo`) does not show credit and gifts yet.
- Live end-to-end test with a real phone after deploy (Step 4).
