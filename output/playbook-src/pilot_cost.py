# -*- coding: utf-8 -*-
"""AIKIA.WALLET pilot costing: 3 to 5 cafes with 100 to 200 customers each.
Running costs per month and per year, cost per cafe, one-time costs, break-even pricing and a roadmap.
Prices checked 19 Oct 2026. S = published price found online (re-check on the vendor page), E = our estimate."""
import os, subprocess
from html import escape as e

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_HTML = os.path.join(HERE, "AIKIA-WALLET-Pilot-Costing.html")
OUT_PDF = os.path.join(HERE, "..", "pdf", "AIKIA-WALLET-Pilot-Costing-3-to-5-Cafes.pdf")
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
css = open(os.path.join(HERE, "style.css"), encoding="utf-8").read()

FX = 96.0          # Rs per US$ (mid-market about 96.5 in mid-Oct 2026; banks and cards charge a little more)
GST = 0.18         # GST on imported software services (charged by the vendor, or reverse charge once GST-registered)

def rs(x):
    s = "{:,.0f}".format(round(x))
    # Indian grouping
    n = str(int(round(abs(x))))
    if len(n) > 3:
        head, tail = n[:-3], n[-3:]
        parts = []
        while len(head) > 2: parts.insert(0, head[-2:]); head = head[:-2]
        if head: parts.insert(0, head)
        s = ",".join(parts) + "," + tail
    else:
        s = n
    return ("-Rs " if x < 0 else "Rs ") + s

# ---------------- monthly platform costs (same whether 1 or 5 cafes) ----------------
# (item, what it does, price basis, flag, US$ per month or None, Rs per month if priced in rupees, foreign?)
FIXED = [
    ("PassKit, platform fee (1 user)", "Issues and updates the Google (and later Apple) wallet cards. Includes the first 250 cards.", "US$39.50 a month", "S", 39.50, None),
    ("Vercel Pro (1 seat)", "Hosts the app: join page, staff scanner, owner dashboard, guest pages. The free Hobby plan is for non-commercial use only.", "US$20 a seat a month, usage credit included", "S", 20.0, None),
    ("Supabase Pro", "Database, ledger, logins and backups. The free plan pauses after 7 days without activity, which is not safe for paying cafes.", "US$25 a month, US$10 compute credit included", "S", 25.0, None),
    ("Apple Developer Program", "Needed to make cards permanent on PassKit (the certificate) and for iPhone cards.", "US$99 a year, shown per month", "S", 99.0 / 12, None),
    ("Weather data, commercial licence (Open-Meteo Standard)", "Weather-mood messages. The free Open-Meteo API is for non-commercial use.", "US$29 a month in Open-Meteo's own announcement; confirm on its pricing page", "S", 29.0, None),
]
LOCAL = [
    ("Chartered accountant (GST and books)", "GST registration, monthly returns, invoices to cafes.", "monthly retainer", "E", 2500),
]
FREE = [
    ("Login-link email (Resend free tier)", "3,000 emails a month, 100 a day. Enough for 5 cafes' owners and staff.", "Rs 0 (US$20 a month only past the free limits)", "S"),
    ("Google Wallet API", "Used later by our own engine. No per-card fee found.", "Rs 0", "S"),
    ("Code hosting (GitHub), error alerts (free tiers)", "Source code, automatic checks, crash alerts.", "Rs 0 at this size", "E"),
    ("Domain", "A sub-domain of aikia.world (for example wallet.aikia.world). aikia.world is already paid for by the agency.", "Rs 0 extra", "E"),
    ("Staff devices", "Staff use their own phone or the cafe's tablet to scan.", "Rs 0", "E"),
]

# ---------------- per-customer cost ----------------
PK_FREE_CARDS = 250
PK_PER_CARD = 0.045          # US$ a stored card a month, cards 251 to 2,500
PK_CARD_RS = PK_PER_CARD * FX * (1 + GST)   # about Rs 5.10 a card a month incl. GST

def fixed_month(engine="passkit"):
    usd = sum(x[4] for x in FIXED if engine == "passkit" or not x[0].startswith("PassKit"))
    foreign = usd * FX * (1 + GST)
    local = sum(x[4] for x in LOCAL)
    return foreign + local

def cards_cost(members, engine="passkit"):
    if engine != "passkit": return 0.0
    return max(0, members - PK_FREE_CARDS) * PK_CARD_RS

def scenario(cafes, per_cafe, engine="passkit"):
    members = cafes * per_cafe
    f = fixed_month(engine); v = cards_cost(members, engine)
    m = f + v
    return dict(cafes=cafes, per_cafe=per_cafe, members=members, fixed=f, cards=v, month=m, year=m * 12, per_cafe_month=m / cafes, per_member=m / members)

SCEN = [scenario(c, p) for c in (3, 5) for p in (100, 150, 200)]
OWN = [scenario(c, p, "own") for c in (3, 5) for p in (100, 150, 200)]
S3, S5 = scenario(3, 150), scenario(5, 150)
O5 = scenario(5, 150, "own")

# ---------------- one-time costs ----------------
ONE = [
    ("Lawyer: cafe agreement, privacy notice (DPDP Act), programme terms", 25000, 60000, "E", "Before the first paying cafe"),
    ("CA: GST registration and set-up", 2000, 5000, "E", "Before invoicing cafes"),
    ("Trademark filing for aikia.wallet (1 class, e-filing, individual or small business)", 4500, 4500, "S", "Government fee; agent fees extra if used"),
    ("QR standee and counter poster, per cafe x 5", 1500, 2500, "E", "Rs 300 to 500 per cafe"),
    ("Lawyer: written opinion on venue-only prepaid credit", 50000, 100000, "E", "Only before cafes take real money as credit"),
]
ONE_CORE = ONE[:4]
one_lo = sum(x[1] for x in ONE_CORE); one_hi = sum(x[2] for x in ONE_CORE)
one_lo_all = sum(x[1] for x in ONE); one_hi_all = sum(x[2] for x in ONE)

# ---------------- development still to do ----------------
RATE_PM = 70000   # partner person-month (ASSUMPTION carried from the Budget Plan; ask the partner to quote)
DEV = [
    ("Own email sender and custom domain for the app", 1, True),
    ("Monitoring, uptime alerts, backup restore test", 2, True),
    ("Security review and fixes before real customers", 5, True),
    ("Testing on real Android phones at a cafe counter", 3, True),
    ("Apple Wallet switch-on and test (after the certificate)", 2, True),
    ("Sales demo (browser demo) updated with credit and gifts", 3, False),
    ("Online top-up through the cafe's own Razorpay / UPI account", 15, False),
    ("Own Google Wallet engine switch-over and card migration", 3, False),
]
dev_core_days = sum(d for _, d, core in DEV if core)
dev_all_days = sum(d for _, d, _ in DEV)
pm = lambda days: days / 21.0

# ---------------- break-even ----------------
def breakeven(price_month, engine="passkit", per_cafe=150):
    var = per_cafe * PK_CARD_RS if engine == "passkit" else 0  # each extra cafe's cards, once the free 250 are used up
    margin = price_month * (1 - 0.0236) - var    # 2.36% gateway on card payments; UPI is free
    if margin <= 0: return None
    import math
    return math.ceil(fixed_month(engine) / margin)

PRICES = [417, 999, 1499, 1999, 2999]

# ---------------- HTML ----------------
H = []
A = H.append
A('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>AIKIA.WALLET pilot costing</title><style>%s</style></head><body>' % css)

A('''<section class="cover"><div class="band"><div class="ring"></div><div class="ring2"></div>
<div class="kicker">AIKIA.WALLET &nbsp;/&nbsp; PILOT COSTING</div>
<h1>What 3 to 5 cafes<br>cost us to run.</h1>
<p style="max-width:62%%">Monthly and yearly running costs for 3 to 5 cafes with 100 to 200 customers each, the cost per cafe, one-time costs, the development still to do, break-even pricing and a roadmap. Prices checked 19 October 2026 at Rs %d to the US dollar, plus 18%% GST on imported software.</p></div>
<div><div class="grid3" style="margin-bottom:5mm">
<div class="card pink"><div class="stat">%s<small>A MONTH to run 3 cafes with 150 customers each (450 cards), all-in.</small></div></div>
<div class="card pink"><div class="stat">%s<small>A MONTH to run 5 cafes with 150 customers each (750 cards). That is %s a cafe.</small></div></div>
<div class="card pink"><div class="stat">%s<small>A YEAR for 5 cafes, plus %s to %s one-time to start.</small></div></div>
</div>
<div class="callout red"><b>The big finding.</b> At this size most of the cost is fixed platform fees, not customers. PassKit also charges about %s a customer card every month after the first 250. At our earlier Starter price of Rs 4,999 a year (Rs 417 a month) a cafe never covers its own cost. Pilot pricing must be closer to Rs 1,500 to Rs 2,000 a month, or we move to our own Google Wallet engine early.</div>
<div class="callout warn"><b>How to read this.</b> Figures are planning numbers, not quotes. S = price found in a published source (re-check on the vendor page before paying). E = our estimate. Founder time is not costed. Development is shown separately because most of the product is already built.</div>
</div></section>''' % (FX, rs(S3["month"]), rs(S5["month"]), rs(S5["per_cafe_month"]), rs(S5["year"]), rs(one_lo), rs(one_hi), rs(PK_CARD_RS)))

# Section 1: monthly running costs
rows = "".join('<tr><td><b>%s</b><br><span class="small">%s</span></td><td>%s</td><td class="c">%s</td><td class="n">%s</td></tr>' % (e(n), e(w), e(b), f, rs(u * FX)) for n, w, b, f, u, _ in FIXED)
rows += "".join('<tr><td><b>%s</b><br><span class="small">%s</span></td><td>%s</td><td class="c">%s</td><td class="n">%s</td></tr>' % (e(n), e(w), e(b), f, rs(r)) for n, w, b, f, r in LOCAL)
usd_total = sum(x[4] for x in FIXED)
A('''<section class="sec"><div class="kicker">1 &nbsp;/&nbsp; MONTHLY RUNNING COSTS</div><h2>The fixed bill: the same for 1 cafe or 5</h2>
<p class="lede">These are the services that keep the product online for every cafe. They don't grow with the number of cafes until well past 5.</p>
<table><tr><th>Service and why</th><th>Price basis</th><th class="c">Src</th><th class="n">Rs a month</th></tr>%s
<tr><td colspan="3">GST at 18%% on the imported services (US$%.2f a month)</td><td class="n">%s</td></tr>
<tr><td colspan="3"><b>Fixed total a month</b></td><td class="n"><b>%s</b></td></tr></table>
<h3>Free at this size</h3><table><tr><th>Service</th><th>Why it's enough</th><th>Cost</th></tr>%s</table>
<div class="callout"><b>Customer cards.</b> PassKit includes 250 stored cards. After that each card costs US$0.045 a month (cards 251 to 2,500), about %s with GST, every month the card exists, used or not. Cards of customers who leave should be deleted so they stop costing.</div>
</section>''' % (rows, usd_total, rs(usd_total * FX * GST), rs(fixed_month()),
    "".join('<tr><td><b>%s</b></td><td class="small">%s</td><td>%s</td></tr>' % (e(n), e(w), e(c)) for n, w, c, _ in FREE), rs(PK_CARD_RS)))

# Section 2: scenarios
def scen_rows(lst):
    return "".join('<tr><td>%d cafes x %d</td><td class="n">%d</td><td class="n">%s</td><td class="n">%s</td><td class="n"><b>%s</b></td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td></tr>' % (
        s["cafes"], s["per_cafe"], s["members"], rs(s["fixed"]), rs(s["cards"]), rs(s["month"]), rs(s["year"]), rs(s["per_cafe_month"]), "Rs %.0f" % s["per_member"]) for s in lst)
A('''<section class="sec"><div class="kicker">2 &nbsp;/&nbsp; 3 TO 5 CAFES</div><h2>Monthly and yearly, by number of cafes and customers</h2>
<h3>On PassKit (today's set-up)</h3>
<table><tr><th>Cafes x customers</th><th class="n">Cards</th><th class="n">Fixed</th><th class="n">Cards fee</th><th class="n">A month</th><th class="n">A year</th><th class="n">Per cafe a month</th><th class="n">Per customer a month</th></tr>%s</table>
<h3>On our own Google Wallet engine (after Google approves publishing)</h3>
<p>No PassKit fee and no per-card fee. The Apple Developer fee is kept for iPhone cards later.</p>
<table><tr><th>Cafes x customers</th><th class="n">Cards</th><th class="n">Fixed</th><th class="n">Cards fee</th><th class="n">A month</th><th class="n">A year</th><th class="n">Per cafe a month</th><th class="n">Per customer a month</th></tr>%s</table>
<div class="callout ok"><b>What the switch saves.</b> For 5 cafes with 150 customers each, our own engine costs %s a month instead of %s: about %s a year less. The code for it is already built and was tested on 6 October; it is waiting for Google's publishing approval.</div>
</section>''' % (scen_rows(SCEN), scen_rows(OWN), rs(O5["month"]), rs(S5["month"]), rs((S5["month"] - O5["month"]) * 12)))

# Section 3: cost for ONE cafe
one_cafe = scenario(1, 150)
A('''<section class="sec"><div class="kicker">3 &nbsp;/&nbsp; ONE CAFE</div><h2>The cost of one cafe, to set its price</h2>
<p class="lede">A cafe's true cost is its share of the fixed bill plus its customers' cards. The share falls as more cafes join.</p>
<table><tr><th>Number of cafes sharing the fixed bill</th><th class="n">Fixed share a month</th><th class="n">Its 150 cards (past the free 250)</th><th class="n">Cost of one cafe a month</th><th class="n">A year</th></tr>%s</table>
<h3>What we spend on each cafe besides software</h3>
<table><tr><th>Item</th><th>When</th><th class="n">Cost</th></tr>
<tr><td>QR standee and counter poster</td><td>Once, at onboarding</td><td class="n">Rs 300 to 500</td></tr>
<tr><td>Onboarding visit: set up venue, tiers, staff, train the counter (about 2 hours)</td><td>Once</td><td class="n">Founder time</td></tr>
<tr><td>Payment fee when the cafe pays us by card (about 2%% plus GST); UPI is free</td><td>Each payment</td><td class="n">about 2.36%%</td></tr>
<tr><td>Support calls and changes to offers</td><td>Monthly</td><td class="n">Founder time</td></tr></table>
<div class="callout warn"><b>Data and the ledger.</b> 5 cafes with 200 customers each is about 1,000 members. A year of visits is still only tens of thousands of ledger lines, a few MB. Supabase Pro covers this many times over, with daily backups. Data use is not a cost driver until thousands of cafes.</div>
</section>''' % "".join('<tr><td>%d cafe%s</td><td class="n">%s</td><td class="n">%s</td><td class="n"><b>%s</b></td><td class="n">%s</td></tr>' % (
    n, "" if n == 1 else "s", rs(fixed_month() / n), rs(PK_CARD_RS * 150 if n * 150 > PK_FREE_CARDS else 0), rs(fixed_month() / n + (PK_CARD_RS * 150 if n * 150 > PK_FREE_CARDS else 0)), rs((fixed_month() / n + (PK_CARD_RS * 150 if n * 150 > PK_FREE_CARDS else 0)) * 12)) for n in (1, 3, 5, 10, 25)))

# Section 4: pricing and break-even
be_rows = "".join('<tr><td>Rs %s a month%s</td><td class="n">%s</td><td class="n">%s</td></tr>' % (
    "{:,}".format(p), " (Rs 4,999 a year)" if p == 417 else "", (str(breakeven(p)) + " cafes") if breakeven(p) else "never", (str(breakeven(p, "own")) + " cafes") if breakeven(p, "own") else "never") for p in PRICES)
rev5 = 5 * 1499
A('''<section class="sec"><div class="kicker">4 &nbsp;/&nbsp; PRICING</div><h2>How many cafes cover the bill</h2>
<p class="lede">Cafes needed before the monthly bill is covered, at different monthly prices (150 customers a cafe, after a 2.36%% card-payment fee).</p>
<table><tr><th>Price per cafe</th><th class="n">On PassKit</th><th class="n">On our own Google engine</th></tr>%s</table>
<h3>What this means for the pilot</h3>
<ul><li><b>The pilot runs at a loss, and that is normal.</b> With 5 cafes at Rs 1,499 a month we collect %s and spend about %s: a gap of about %s a month. That gap is the price of proof.</li>
<li><b>Charge a one-time setup fee.</b> Rs 2,999 to Rs 4,999 per cafe covers the standee, the onboarding visit and part of the legal set-up.</li>
<li><b>Suggested pilot offer:</b> setup Rs 2,999, then Rs 1,499 a month (or Rs 14,999 a year paid upfront), with credit and gifts as a Growth add-on once the lawyer approves.</li>
<li><b>Move to our own Google engine as soon as Google approves.</b> It removes the biggest fixed fee and the per-card fee, so about 8 to 10 cafes at Rs 1,499 cover the bill.</li></ul>
<div class="callout red"><b>Re-price the old plans.</b> The earlier Rs 4,999-a-year Starter plan does not cover cost at any number of cafes on PassKit. Keep it only for the own-engine set-up and only at 25+ cafes.</div>
</section>''' % (be_rows, rs(rev5), rs(S5["month"]), rs(S5["month"] - rev5)))

# Section 5: one-time + development
one_rows = "".join('<tr><td>%s</td><td>%s</td><td class="c">%s</td><td class="n">%s</td></tr>' % (e(n), e(w), f, rs(lo) if lo == hi else "%s to %s" % (rs(lo), rs(hi))) for n, lo, hi, f, w in ONE)
dev_rows = "".join('<tr><td>%s</td><td class="c">%s</td><td class="n">%d days</td></tr>' % (e(n), "Before pilot" if core else "Later", d) for n, d, core in DEV)
A('''<section class="sec"><div class="kicker">5 &nbsp;/&nbsp; ONE-TIME COSTS AND DEVELOPMENT</div><h2>What to pay once, and the build that is left</h2>
<table><tr><th>One-time item</th><th>When</th><th class="c">Src</th><th class="n">Cost</th></tr>%s
<tr><td colspan="3"><b>Before the first paying cafe</b> (first four lines)</td><td class="n"><b>%s to %s</b></td></tr>
<tr><td colspan="3"><b>Including the credit legal opinion</b></td><td class="n"><b>%s to %s</b></td></tr></table>
<h3>Development still to do</h3>
<p>The product for 3 to 5 cafes is already built and live: cards, join page, staff scanner, scan-and-charge, tiers, offers, weather messages, credit and gifts. What is left:</p>
<table><tr><th>Work</th><th class="c">When</th><th class="n">Effort</th></tr>%s</table>
<table><tr><th>Who builds it</th><th class="n">Before pilot (%d days)</th><th class="n">Everything (%d days)</th></tr>
<tr><td>Us, with Claude (what we did so far)</td><td class="n">Rs 0 extra cash</td><td class="n">Rs 0 extra cash</td></tr>
<tr><td>Partner company at about Rs 70,000 a person-month (assumption; ask them to quote)</td><td class="n">%s</td><td class="n">%s</td></tr></table>
</section>''' % (one_rows, rs(one_lo), rs(one_hi), rs(one_lo_all), rs(one_hi_all), dev_rows, dev_core_days, dev_all_days, rs(pm(dev_core_days) * RATE_PM), rs(pm(dev_all_days) * RATE_PM)))

# Section 6: budget summary
def yr(s): return s["year"]
A('''<section class="sec"><div class="kicker">6 &nbsp;/&nbsp; BUDGET</div><h2>Monthly and yearly budget to keep aside</h2>
<table><tr><th>Budget line</th><th class="n">3 cafes, 150 each</th><th class="n">5 cafes, 150 each</th><th class="n">5 cafes, 200 each</th></tr>
<tr><td>Running cost a month (PassKit)</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td></tr>
<tr><td>Running cost a year (PassKit)</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td></tr>
<tr><td>One-time start (without credit opinion), upper end</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td></tr>
<tr><td>Contingency 15%% on the year</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td></tr>
<tr><td><b>Year one total to keep aside</b></td><td class="n"><b>%s</b></td><td class="n"><b>%s</b></td><td class="n"><b>%s</b></td></tr>
<tr><td>Same, if we move to our own Google engine from month 3</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td></tr></table>
<div class="callout"><b>Cheapest safe start.</b> While cafes are on free trial, the bill can stay near %s a month: PassKit plus Apple only, on the free Vercel and Supabase plans. Switch Vercel and Supabase to paid the day the first cafe pays, because the free plans don't allow commercial use or may pause.</div>
</section>''' % tuple(
    [rs(scenario(*c)["month"]) for c in ((3, 150), (5, 150), (5, 200))] +
    [rs(scenario(*c)["year"]) for c in ((3, 150), (5, 150), (5, 200))] +
    [rs(one_hi)] * 3 +
    [rs(scenario(*c)["year"] * 0.15) for c in ((3, 150), (5, 150), (5, 200))] +
    [rs(scenario(*c)["year"] * 1.15 + one_hi) for c in ((3, 150), (5, 150), (5, 200))] +
    [rs((scenario(*c)["month"] * 2 + scenario(c[0], c[1], "own")["month"] * 10) * 1.15 + one_hi) for c in ((3, 150), (5, 150), (5, 200))] +
    [rs((39.5 + 99.0 / 12) * FX * (1 + GST))]))

# Section 7: roadmap
A('''<section class="sec"><div class="kicker">7 &nbsp;/&nbsp; ROADMAP</div><h2>From demo to 5 paying cafes</h2>
<table><tr><th>When</th><th>Goal</th><th>What we do</th><th class="n">Monthly cost</th></tr>
<tr><td><b>Weeks 0 to 2</b></td><td>Demos and first yes</td><td>Show the live demo in 10 to 15 Vadodara cafes. Sign 3 pilot cafes. Lawyer drafts the cafe agreement and privacy notice. CA registers GST.</td><td class="n">about %s</td></tr>
<tr><td><b>Weeks 2 to 4</b></td><td>Cards that last</td><td>Enrol in Apple Developer and upload the certificate to PassKit, so cards stop expiring after 48 hours. Finish the Google business profile and ask Google for publishing access. Own email sender.</td><td class="n">about %s</td></tr>
<tr><td><b>Weeks 4 to 8</b></td><td>3 cafes live</td><td>Switch Vercel and Supabase to paid. Onboard 3 cafes: tiers, staff, standee, 2-hour training. Weekly check-in, fix what the counter staff report.</td><td class="n">%s</td></tr>
<tr><td><b>Months 3 to 4</b></td><td>5 cafes, own engine</td><td>Add 2 more cafes. When Google approves, switch to our own Google engine and re-issue cards. Credit only after the lawyer's written opinion.</td><td class="n">%s to %s</td></tr>
<tr><td><b>Months 5 to 6</b></td><td>Price and proof</td><td>Measure repeat visits per cafe, fix the price, write 2 case studies, then sell to 10 to 25 cafes.</td><td class="n">%s and up</td></tr></table>
<h3>Risks that change the cost</h3>
<ul><li><b>PassKit draft mode.</b> Until the Apple certificate is uploaded, cards are deleted after about 48 hours. Do not onboard real customers before this.</li>
<li><b>Nearby (geofence) messages.</b> On PassKit, location alerts work on Apple Wallet only. On Android, weather offers still reach guests as card messages, but not as "you are near the cafe" alerts.</li>
<li><b>Dollar rate.</b> Most costs are in US dollars. Every Rs 5 move in the rate changes the fixed bill by about %s a month.</li>
<li><b>Cards that are never deleted.</b> PassKit bills every stored card. Clean up members who leave, every month.</li></ul>
<h3>Sources (checked 19 Oct 2026)</h3>
<ul class="srclist small">
<li>PassKit pricing model: help.passkit.com/en/articles/3133669-the-passkit-pricing-model (platform fee, card tiers, Apple certificate, location alerts Apple only)</li>
<li>Vercel Pro US$20 a seat and Hobby non-commercial: makerkit.dev/blog/saas/vercel-cost; community.vercel.com (commercial use needs Pro)</li>
<li>Supabase Pro US$25 and free-plan pausing: jetadmin.io/blog/supabase-pricing-2026-guide-to-plans-limits-and-real-world-costs</li>
<li>Open-Meteo commercial plans: openmeteo.substack.com/p/api-subscriptions-for-commercial; open-meteo.com/en/pricing</li>
<li>Resend free tier and Pro: resend.com/docs/knowledge-base/what-is-resend-pricing</li>
<li>Rupee rate about 96.5 per US$: pluang.com currency converter, mid-October 2026</li>
<li>Card payment fee about 2%% plus GST, UPI free: AIKIA.WALLET Budget Plan (October 2026)</li></ul>
</section>''' % (rs((39.5 + 99.0 / 12) * FX * (1 + GST)), rs((39.5 + 99.0 / 12) * FX * (1 + GST)), rs(S3["month"]), rs(O5["month"]), rs(S5["month"]), rs(O5["month"]), rs(usd_total * 5 * (1 + GST))))

A('</body></html>')
open(OUT_HTML, "w", encoding="utf-8").write("".join(H))
r = subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--print-to-pdf=" + os.path.abspath(OUT_PDF), "file:///" + OUT_HTML.replace("\\", "/")], capture_output=True, text=True, timeout=180)
print("pdf", os.path.exists(OUT_PDF), r.returncode)
for s in SCEN + OWN: print(s["cafes"], s["per_cafe"], round(s["month"]), round(s["per_cafe_month"]), round(s["year"]))
print("fixed", round(fixed_month()), "own", round(fixed_month("own")), "card", round(PK_CARD_RS, 2), "one", one_lo, one_hi, "dev", dev_core_days, dev_all_days)
print("breakeven", [(p, breakeven(p), breakeven(p, "own")) for p in PRICES])
