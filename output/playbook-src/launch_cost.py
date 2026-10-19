# -*- coding: utf-8 -*-
"""AIKIA.WALLET launch costing on OUR OWN wallet engines (Google Wallet API + Apple Wallet), no PassKit.
3 to 5 cafes with 100 to 200 customers each, every feature on: cards, tiers, credit, scan-and-charge, gifts,
geofencing, weather-mood and campaign messages. Running cost, break-even price, data storage, automation,
security and the build that is left. Prices checked 19 Oct 2026. S = published price found online, E = our estimate."""
import os, math, subprocess
from html import escape as e

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_HTML = os.path.join(HERE, "AIKIA-WALLET-Launch-Costing.html")
OUT_PDF = os.path.join(HERE, "..", "pdf", "AIKIA-WALLET-Launch-Costing-Own-Wallet.pdf")
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
css = open(os.path.join(HERE, "style.css"), encoding="utf-8").read()

FX = 96.0        # Rs per US$, mid-October 2026 (mid-market about 96.5)
GST = 0.18       # on imported software services
GATEWAY = 0.0236 # card payment fee on what cafes pay us (about 2% + GST); UPI is free

def rs(x):
    n = str(int(round(abs(x))))
    if len(n) > 3:
        head, tail = n[:-3], n[-3:]
        parts = []
        while len(head) > 2: parts.insert(0, head[-2:]); head = head[:-2]
        if head: parts.insert(0, head)
        n = ",".join(parts) + "," + tail
    return ("-Rs " if x < 0 else "Rs ") + n

# (item, what it does for us, price basis, flag, US$ a month)
PAID_USD = [
    ("Vercel Pro, 1 seat", "Runs the app and the scheduled jobs: join page, staff scanner, owner dashboard, guest pages, Apple pass web service. Hobby (free) is non-commercial only.", "US$20 a month, usage credit included", "S", 20.0),
    ("Supabase Pro", "The database and ledger, logins, daily backups kept 7 days. Never pauses (the free plan pauses after 7 idle days).", "US$25 a month", "S", 25.0),
    ("Apple Developer Program", "Our own Apple Wallet pass certificate and push updates to iPhones.", "US$99 a year, shown per month", "S", 99.0 / 12),
    ("Weather data, commercial (Open-Meteo Standard)", "Weather-mood messages. The free API is for non-commercial use.", "US$29 a month per Open-Meteo's own announcement; confirm", "S", 29.0),
    ("GitHub Team, 2 users", "Protected main branch and required reviews on our private code (not enforced on the free plan for private repositories).", "about US$4 a user a month; confirm on github.com/pricing", "S", 8.0),
]
PAID_RS = [
    ("Chartered accountant", "GST registration, monthly GST returns, invoices to cafes.", "monthly retainer", "E", 2500),
]
FREE = [
    ("Google Wallet API and Google Pay & Wallet Console", "Issue and update Android cards, messages, nearby alerts.", "Free, no per-card fee found", "S"),
    ("Apple push notifications (APNs)", "Tells iPhones to fetch the updated card.", "Free with the developer account", "S"),
    ("Login-link and alert email (Resend free)", "3,000 emails a month, 100 a day. Enough for 5 cafes' teams and our alerts.", "Free", "S"),
    ("GitHub Actions", "Tests on every change, nightly backup, health checks every 10 minutes.", "Free minutes cover this", "E"),
    ("Cloudflare R2 (off-site backup copy)", "A second, encrypted copy of the database every night, kept 30 days.", "Free up to 10 GB", "E"),
    ("Cloudflare DNS and protection", "Domain records, DDoS shield, basic firewall in front of the app.", "Free plan", "E"),
    ("Password manager (Bitwarden, 2 users)", "All keys and passwords in one shared vault, never in chat or code.", "Free for 2 users", "E"),
    ("Domain", "wallet.aikia.world, a sub-domain of the agency's domain.", "Rs 0 extra", "E"),
]

USD = sum(x[4] for x in PAID_USD)
FIXED = USD * FX * (1 + GST) + sum(x[4] for x in PAID_RS)
PER_CUSTOMER = 0.0   # Google and Apple charge nothing per card; hosting stays inside the plans at this size

def month_cost(cafes, per_cafe): return FIXED + PER_CUSTOMER * cafes * per_cafe
def breakeven_price(cafes): return FIXED / cafes / (1 - GATEWAY)
def cafes_needed(price): return math.ceil(FIXED / (price * (1 - GATEWAY)))

# One-time
ONE = [
    ("Lawyer: cafe agreement, privacy notice (DPDP Act), programme terms", 25000, 60000, "E"),
    ("CA: GST registration and set-up", 2000, 5000, "E"),
    ("Trademark filing for aikia.wallet, 1 class, e-filing (government fee)", 4500, 4500, "S"),
    ("QR standee and counter poster, 5 cafes", 1500, 2500, "E"),
    ("Test iPhone (second-hand) if no one in the team has one", 0, 25000, "E"),
]
ONE_CREDIT = ("Lawyer: written opinion on venue-only prepaid credit (before real money)", 50000, 100000, "E")
one_lo = sum(x[1] for x in ONE); one_hi = sum(x[2] for x in ONE)

# Build left before launch (days)
DEV = [
    ("Apple Wallet engine: build and sign passes, Apple's update web service, push to iPhones", 12, True),
    ("Switch to our Google engine (already built), finish publishing approval, move cards", 3, True),
    ("Geofence and weather on own engines: Apple lock-screen text, Google nearby + message", 2, True),
    ("Notification budget: never more than 3 messages a card a day on Google", 1, True),
    ("Remove PassKit from settings and code paths", 1, True),
    ("Automation: nightly off-site backup, health checks, alert emails", 2, True),
    ("Staging copy and safe database-change workflow", 2, True),
    ("Security review and fixes", 5, True),
    ("Own email sender and domain", 1, True),
    ("Testing on real Android and iPhone at a cafe counter", 4, True),
    ("Online top-up through the cafe's own Razorpay / UPI account (optional)", 15, False),
]
core_days = sum(d for _, d, c in DEV if c); all_days = sum(d for _, d, _ in DEV)
RATE_PM = 70000

# ---------------- HTML ----------------
H = []; A = H.append
A('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>AIKIA.WALLET launch costing</title><style>%s</style></head><body>' % css)

be3, be5 = breakeven_price(3), breakeven_price(5)
A('''<section class="cover"><div class="band"><div class="ring"></div><div class="ring2"></div>
<div class="kicker">AIKIA.WALLET &nbsp;/&nbsp; LAUNCH COSTING</div>
<h1>Our own wallet,<br>at break-even.</h1>
<p style="max-width:62%%">Launch on our own Google Wallet and Apple Wallet engines, with no PassKit, and every feature on. What it costs to run, what to charge so 3 to 5 cafes cover it, where the data lives, what runs by itself and how it stays secure. Prices checked 19 October 2026 at Rs %d to the US dollar.</p></div>
<div><div class="grid3" style="margin-bottom:5mm">
<div class="card pink"><div class="stat">%s<small>A MONTH to run everything, all features, for 3 or 5 cafes. %s a year.</small></div></div>
<div class="card pink"><div class="stat">%s<small>A MONTH per cafe to break even with 5 cafes. With 3 cafes: %s.</small></div></div>
<div class="card pink"><div class="stat">Rs 0<small>PER CUSTOMER. Google and Apple charge nothing per card, so 100 or 200 customers cost the same.</small></div></div>
</div>
<div class="callout ok"><b>The answer.</b> Charge <b>Rs 2,999 a month</b> per cafe (or Rs 29,999 a year) plus a one-time <b>Rs 4,999 setup</b>. 5 cafes cover every running cost from the first month. With 3 cafes, charge Rs 4,499 a month or accept a gap of about %s a month until cafe 5 joins.</div>
<div class="callout warn"><b>How to read this.</b> Planning numbers, not quotes. S = price found in a published source (re-check on the vendor page before paying). E = our estimate. Founder time and salaries are not costed. PassKit is used only for demos until launch and is left out.</div>
</div></section>''' % (FX, rs(FIXED), rs(FIXED * 12), rs(be5), rs(be3), rs(FIXED - 3 * 2999 * (1 - GATEWAY))))

# 1. Running cost
rows = "".join('<tr><td><b>%s</b><br><span class="small">%s</span></td><td>%s</td><td class="c">%s</td><td class="n">%s</td></tr>' % (e(n), e(w), e(b), f, rs(u * FX)) for n, w, b, f, u in PAID_USD)
rows += '<tr><td colspan="3">GST at 18%% on the imported services (US$%.2f a month)</td><td class="n">%s</td></tr>' % (USD, rs(USD * FX * GST))
rows += "".join('<tr><td><b>%s</b><br><span class="small">%s</span></td><td>%s</td><td class="c">%s</td><td class="n">%s</td></tr>' % (e(n), e(w), e(b), f, rs(r)) for n, w, b, f, r in PAID_RS)
A('''<section class="sec"><div class="kicker">1 &nbsp;/&nbsp; RUNNING COST</div><h2>Everything we pay every month</h2>
<p class="lede">Every feature is included: wallet cards, tiers, scan-and-charge, credit, gifts, geofencing, weather-mood and campaign messages, the ledger and backups. None of it grows with the number of customers at this size.</p>
<table><tr><th>Service and what it does</th><th>Price basis</th><th class="c">Src</th><th class="n">Rs a month</th></tr>%s
<tr><td colspan="3"><b>Total a month</b></td><td class="n"><b>%s</b></td></tr>
<tr><td colspan="3"><b>Total a year</b></td><td class="n"><b>%s</b></td></tr></table>
<h3>Free at this size, and safe for business use</h3>
<table><tr><th>Service</th><th>What it does</th><th>Cost</th></tr>%s</table>
</section>''' % (rows, rs(FIXED), rs(FIXED * 12), "".join('<tr><td><b>%s</b></td><td class="small">%s</td><td>%s</td></tr>' % (e(n), e(w), e(c)) for n, w, c, _ in FREE)))

# 2. Per cafe and 3 to 5 cafes
sc = [(c, p) for c in (3, 4, 5) for p in (100, 200)]
A('''<section class="sec"><div class="kicker">2 &nbsp;/&nbsp; PER CAFE</div><h2>Cost per cafe, for 3 to 5 cafes</h2>
<table><tr><th>Cafes x customers</th><th class="n">Customers</th><th class="n">Running cost a month</th><th class="n">A year</th><th class="n">Per cafe a month</th><th class="n">Per customer a month</th></tr>%s</table>
<h3>What each feature costs us</h3>
<table><tr><th>Feature</th><th>What it runs on</th><th class="n">Extra cost</th></tr>
<tr><td>Google Wallet cards, updates, tier colours</td><td>Google Wallet API</td><td class="n">Rs 0</td></tr>
<tr><td>Apple Wallet cards and updates</td><td>Our pass certificate + Apple push</td><td class="n">in the Apple fee</td></tr>
<tr><td>Geofencing (up to 10 locations a cafe)</td><td>Apple: our text on the lock screen. Google: nearby alert in Google's own words</td><td class="n">Rs 0</td></tr>
<tr><td>Weather-mood messages</td><td>Daily weather check + card message</td><td class="n">in the weather licence</td></tr>
<tr><td>Campaigns, offers, win-back messages</td><td>Card messages (Google: up to 3 a card a day)</td><td class="n">Rs 0</td></tr>
<tr><td>Credit, scan-and-charge, pay codes, gifts</td><td>Our ledger in Supabase</td><td class="n">Rs 0</td></tr>
<tr><td>Ledger, members, history, backups</td><td>Supabase Pro + nightly off-site copy</td><td class="n">in Supabase</td></tr>
<tr><td>Optional later: WhatsApp messages</td><td>WhatsApp provider (not part of launch)</td><td class="n">about Rs 0.12 a utility message</td></tr></table>
<h3>Costs that come per cafe, outside software</h3>
<table><tr><th>Item</th><th>When</th><th class="n">Cost</th></tr>
<tr><td>QR standee and counter poster</td><td>Once</td><td class="n">Rs 300 to 500</td></tr>
<tr><td>Payment fee when a cafe pays us by card (UPI is free)</td><td>Each payment</td><td class="n">about 2.36%%</td></tr>
<tr><td>Onboarding visit and staff training (about 2 hours)</td><td>Once</td><td class="n">founder time</td></tr></table>
</section>''' % "".join('<tr><td>%d x %d</td><td class="n">%d</td><td class="n">%s</td><td class="n">%s</td><td class="n"><b>%s</b></td><td class="n">Rs %.0f</td></tr>' % (c, p, c * p, rs(month_cost(c, p)), rs(month_cost(c, p) * 12), rs(month_cost(c, p) / c), month_cost(c, p) / (c * p)) for c, p in sc))

# 3. Break-even
prices = [1999, 2499, 2999, 3999, 4499]
A('''<section class="sec"><div class="kicker">3 &nbsp;/&nbsp; BREAK-EVEN PRICE</div><h2>What to charge so we are never in loss</h2>
<p class="lede">Break-even here means the cafes' fees cover every running cost each month, after the card-payment fee. Founders are unpaid.</p>
<table><tr><th>Cafes</th><th class="n">Break-even price per cafe a month</th><th class="n">Rounded price</th><th class="n">A year, paid upfront</th></tr>
<tr><td>3</td><td class="n">%s</td><td class="n">Rs 4,499</td><td class="n">Rs 44,999</td></tr>
<tr><td>4</td><td class="n">%s</td><td class="n">Rs 3,499</td><td class="n">Rs 34,999</td></tr>
<tr><td>5</td><td class="n">%s</td><td class="n">Rs 2,999</td><td class="n">Rs 29,999</td></tr></table>
<table><tr><th>If we charge</th><th class="n">Cafes needed to break even</th><th class="n">Surplus with 5 cafes a month</th></tr>%s</table>
<h3>Our recommendation</h3>
<ul><li><b>Rs 2,999 a month per cafe</b> (Rs 29,999 a year upfront, two months free), all features included. That is about Rs 100 a day for the cafe.</li>
<li><b>Rs 4,999 one-time setup</b> per cafe: card design, tiers, staff training, standee. Every 5 paid setups (%s) cover most of the one-time legal and set-up costs.</li>
<li><b>Founding-cafe offer for the first 3:</b> setup free, Rs 2,999 a month, in return for a case study. The gap of about %s a month closes when cafe 5 joins.</li>
<li>Above 5 cafes everything is surplus: each new cafe adds about %s a month after fees, because running cost doesn't grow at this size.</li></ul>
</section>''' % (rs(breakeven_price(3)), rs(breakeven_price(4)), rs(breakeven_price(5)),
    "".join('<tr><td>Rs %s a month</td><td class="n">%d</td><td class="n">%s</td></tr>' % ("{:,}".format(p), cafes_needed(p), rs(5 * p * (1 - GATEWAY) - FIXED)) for p in prices),
    rs(5 * 4999), rs(FIXED - 3 * 2999 * (1 - GATEWAY)), rs(2999 * (1 - GATEWAY))))

# 4. Data
A('''<section class="sec"><div class="kicker">4 &nbsp;/&nbsp; DATA</div><h2>Where the data lives and what we keep</h2>
<table><tr><th>What</th><th>Where</th><th>Why</th></tr>
<tr><td><b>Members, tiers, ledger, credit, gifts, campaigns, team</b></td><td>Supabase Postgres (choose the Mumbai region)</td><td>One database with row-level security: each cafe sees only its own rows. The ledger is append-only, so every stamp, payment and refund stays on record.</td></tr>
<tr><td><b>Card artwork and logos</b></td><td>In the app's code (public/brand), served by Vercel</td><td>Fast, versioned, no extra storage cost.</td></tr>
<tr><td><b>Keys and certificates</b> (Google service account, Apple pass certificate, database keys)</td><td>Vercel encrypted settings (type Secret) and the Bitwarden vault</td><td>Never in code, chat, email or screenshots.</td></tr>
<tr><td><b>Backups</b></td><td>Supabase daily backup (7 days) + our nightly encrypted copy in Cloudflare R2 (30 days)</td><td>Two places, two companies. A restore is tested once a month.</td></tr>
<tr><td><b>Code</b></td><td>Private GitHub repository SHXHMNS/aikia.wallet</td><td>Every change reviewed and tested before it goes live.</td></tr></table>
<h3>What we store about a guest, and what we don't</h3>
<table><tr><th>Stored</th><th>Never stored</th></tr>
<tr><td>Name, consent date, member code, visits, stamps, tier, credit balance, gift history</td><td>Phone number in the card or its QR, card or bank details, UPI IDs, location history</td></tr></table>
<div class="callout"><b>Size.</b> 5 cafes x 200 customers = 1,000 members. A year of visits, payments and gifts is a few MB. Supabase Pro holds this many times over; data is not a cost until thousands of cafes.</div>
<div class="callout warn"><b>DPDP Act.</b> Guests consent on the join page. On request, a cafe owner or we delete a member and their card. Keep the privacy notice and a deletion log; the lawyer drafts both.</div>
</section>''')

# 5. Automation
A('''<section class="sec"><div class="kicker">5 &nbsp;/&nbsp; AUTOMATION</div><h2>What runs by itself, so nothing waits on us</h2>
<table><tr><th>Job</th><th>When</th><th>Runs on</th><th>If it fails</th></tr>
<tr><td>Test, type-check and build every code change</td><td>Every push</td><td>GitHub Actions</td><td>Change is blocked from going live</td></tr>
<tr><td>Deploy: preview first, then live</td><td>On merge to main</td><td>Vercel</td><td>One-click roll back to the last good version</td></tr>
<tr><td>Database changes (new columns, tables)</td><td>With the code change, after approval</td><td>Supabase migration step in the workflow</td><td>Applied to the staging copy first; the live app never runs ahead of its database</td></tr>
<tr><td>Retry wallet cards that failed to update</td><td>Daily (more often on Vercel Pro)</td><td>Vercel Cron</td><td>Alert email if any card stays out of sync</td></tr>
<tr><td>Weather check and mood messages; scheduled and win-back campaigns</td><td>Every morning, 9 am</td><td>Vercel Cron</td><td>Logged in "Recent sends"; never more than 3 Google messages a card a day</td></tr>
<tr><td>Expire unused gifts and return them to the sender</td><td>Daily</td><td>Vercel Cron</td><td>Logged</td></tr>
<tr><td>Off-site encrypted database backup</td><td>Nightly</td><td>GitHub Actions to Cloudflare R2</td><td>Alert email</td></tr>
<tr><td>Health check of the app, database and wallet engines</td><td>Every 10 minutes</td><td>GitHub Actions</td><td>Alert email to both founders</td></tr>
<tr><td>Dependency and security updates</td><td>Weekly</td><td>GitHub Dependabot</td><td>Pull request to review</td></tr>
<tr><td>Monthly cafe report: visits, members, credit loaded and spent</td><td>1st of the month</td><td>Vercel Cron + email</td><td>Logged</td></tr></table>
<h3>How we avoid lag and breakdowns</h3>
<ul><li><b>The counter never waits on Google or Apple.</b> The ledger is saved first. The wallet card updates right after, and if Google or Apple is slow, the daily retry finishes the job.</li>
<li><b>No double charges.</b> Every scan carries a one-time key, so a double tap or a weak network can't charge twice.</li>
<li><b>Fast for India.</b> Database in Mumbai; app served from Vercel's edge network.</li>
<li><b>Safe changes.</b> Staging first, automatic tests, preview link, then live. Roll back in one click.</li>
<li><b>Room to grow.</b> Vercel Pro and Supabase Pro comfortably carry 5 to 50 cafes before any upgrade.</li></ul>
</section>''')

# 6. Security
A('''<section class="sec"><div class="kicker">6 &nbsp;/&nbsp; SECURITY</div><h2>How the code, website and servers stay safe</h2>
<table><tr><th>Area</th><th>What we do</th><th class="n">Cost</th></tr>
<tr><td>Accounts</td><td>Two-step login on Google, Apple, Vercel, Supabase, GitHub, Cloudflare and the domain registrar. Only the two founders are owners.</td><td class="n">Rs 0</td></tr>
<tr><td>Keys and certificates</td><td>Stored only as Vercel Secrets and in Bitwarden. Google key and Apple certificate rotated once a year. Never in code or chat.</td><td class="n">Rs 0</td></tr>
<tr><td>Code</td><td>Private repository, protected main branch, review before merge, Dependabot alerts, no secrets in the repository.</td><td class="n">GitHub Team</td></tr>
<tr><td>Database</td><td>Row-level security per cafe; staff can scan but not see the member list; owner-only reversals; append-only ledger.</td><td class="n">Rs 0</td></tr>
<tr><td>App</td><td>HTTPS only, security headers and content policy, rate limits on sign-up, single-use pay codes, scan-only limit and daily cap on credit.</td><td class="n">Rs 0</td></tr>
<tr><td>Network</td><td>Vercel's built-in DDoS protection; Cloudflare in front of the domain.</td><td class="n">Rs 0</td></tr>
<tr><td>Backups</td><td>Two copies in two companies, encrypted, restore tested monthly.</td><td class="n">Rs 0</td></tr>
<tr><td>Outside test (later)</td><td>Professional penetration test once we pass about 10 cafes or before any chain.</td><td class="n">about Rs 1 to 1.5 lakh, once (E)</td></tr></table>
<div class="callout red"><b>Before the first real customer.</b> Turn on two-step login everywhere (Vercel asked for it on 18 October and it was skipped), mark every Vercel setting as Secret, and delete the old Google key file from Downloads.</div>
</section>''')

# 7. One-time + build
one_rows = "".join('<tr><td>%s</td><td class="c">%s</td><td class="n">%s</td></tr>' % (e(n), f, rs(lo) if lo == hi else "%s to %s" % (rs(lo), rs(hi))) for n, lo, hi, f in ONE)
dev_rows = "".join('<tr><td>%s</td><td class="c">%s</td><td class="n">%d days</td></tr>' % (e(n), "Before launch" if c else "Later", d) for n, d, c in DEV)
A('''<section class="sec"><div class="kicker">7 &nbsp;/&nbsp; ONE-TIME AND BUILD</div><h2>What we pay once, and the build that is left</h2>
<table><tr><th>One-time item</th><th class="c">Src</th><th class="n">Cost</th></tr>%s
<tr><td><b>Total before launch</b></td><td></td><td class="n"><b>%s to %s</b></td></tr>
<tr><td>%s</td><td class="c">E</td><td class="n">%s to %s</td></tr></table>
<h3>Build left before launch on our own engines</h3>
<table><tr><th>Work</th><th class="c">When</th><th class="n">Effort</th></tr>%s</table>
<table><tr><th>Who builds it</th><th class="n">Before launch (%d days)</th><th class="n">With online top-up (%d days)</th></tr>
<tr><td>Us, with Claude</td><td class="n">Rs 0 extra cash</td><td class="n">Rs 0 extra cash</td></tr>
<tr><td>Partner company at about Rs 70,000 a person-month (assumption; ask them to quote)</td><td class="n">%s</td><td class="n">%s</td></tr></table>
</section>''' % (one_rows, rs(one_lo), rs(one_hi), e(ONE_CREDIT[0]), rs(ONE_CREDIT[1]), rs(ONE_CREDIT[2]), dev_rows, core_days, all_days, rs(core_days / 21 * RATE_PM), rs(all_days / 21 * RATE_PM)))

# 8. Budget + roadmap
y1_lo = FIXED * 12 + one_lo; y1_hi = FIXED * 12 * 1.15 + one_hi
A('''<section class="sec"><div class="kicker">8 &nbsp;/&nbsp; BUDGET AND ROADMAP</div><h2>The money to keep aside, and the order of work</h2>
<table><tr><th>Budget line</th><th class="n">Amount</th></tr>
<tr><td>Running cost, a month</td><td class="n">%s</td></tr>
<tr><td>Running cost, a year</td><td class="n">%s</td></tr>
<tr><td>One-time before launch</td><td class="n">%s to %s</td></tr>
<tr><td>Contingency 15%% on running cost</td><td class="n">%s</td></tr>
<tr><td><b>Year one to keep aside (before any cafe pays)</b></td><td class="n"><b>%s to %s</b></td></tr>
<tr><td>Year one income at 5 cafes x Rs 2,999 a month + Rs 4,999 setup, after card fees</td><td class="n">%s</td></tr></table>
<table><tr><th>When</th><th>What we do</th><th class="n">Monthly cost</th></tr>
<tr><td><b>Weeks 0 to 2</b></td><td>Enrol in Apple Developer. Finish the Google business profile and request publishing access. Lawyer drafts agreement and privacy notice. CA registers GST. Keep demoing on PassKit's free draft cards.</td><td class="n">about %s</td></tr>
<tr><td><b>Weeks 2 to 5</b></td><td>Build the Apple engine, switch to our Google engine, automation, security review, test on real phones. Sign 3 founding cafes.</td><td class="n">about %s</td></tr>
<tr><td><b>Week 5</b></td><td>Launch: Vercel Pro, Supabase Pro, GitHub Team, weather licence on. Cancel PassKit. Onboard the first 3 cafes.</td><td class="n">%s</td></tr>
<tr><td><b>Months 2 to 3</b></td><td>Cafes 4 and 5 at Rs 2,999 a month. Break-even reached.</td><td class="n">%s</td></tr>
<tr><td><b>Months 4 to 6</b></td><td>Fix pricing with real data, 2 case studies, then 10 to 25 cafes. Penetration test past 10 cafes.</td><td class="n">%s</td></tr></table>
<h3>Sources (checked 19 Oct 2026)</h3>
<ul class="srclist small">
<li>Google Wallet push and nearby notifications, 3 a card a day: developers.google.com/wallet/retail/loyalty-cards/use-cases/trigger-push-notifications</li>
<li>Vercel Pro US$20 a seat, Hobby non-commercial: makerkit.dev/blog/saas/vercel-cost; community.vercel.com</li>
<li>Supabase Pro US$25, daily backups 7 days, PITR US$100 extra: supabase.com/pricing; jetadmin.io Supabase pricing guide 2026</li>
<li>Open-Meteo commercial plans: openmeteo.substack.com/p/api-subscriptions-for-commercial</li>
<li>Resend free tier: resend.com/docs/knowledge-base/what-is-resend-pricing</li>
<li>GitHub plans (protected branches on private repositories need Team): docs.github.com, About GitHub's plans; github.com/pricing</li>
<li>Apple Developer Program US$99 a year: developer.apple.com/programs</li>
<li>Rupee rate about 96.5 per US$: pluang.com, mid-October 2026</li></ul>
</section>''' % (rs(FIXED), rs(FIXED * 12), rs(one_lo), rs(one_hi), rs(FIXED * 12 * 0.15), rs(y1_lo), rs(y1_hi),
    rs((5 * 2999 * 12 + 5 * 4999) * (1 - GATEWAY)),
    rs(99.0 / 12 * FX * (1 + GST)), rs(99.0 / 12 * FX * (1 + GST)), rs(FIXED), rs(FIXED), rs(FIXED)))

A('</body></html>')
open(OUT_HTML, "w", encoding="utf-8").write("".join(H))
r = subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--print-to-pdf=" + os.path.abspath(OUT_PDF), "file:///" + OUT_HTML.replace("\\", "/")], capture_output=True, text=True, timeout=180)
print("pdf", os.path.exists(OUT_PDF), r.returncode)
print("fixed", round(FIXED), "year", round(FIXED * 12), "be3", round(breakeven_price(3)), "be4", round(breakeven_price(4)), "be5", round(breakeven_price(5)))
print("needed", [(p, cafes_needed(p)) for p in prices], "one", one_lo, one_hi, "dev", core_days, all_days, "y1", round(y1_lo), round(y1_hi))
