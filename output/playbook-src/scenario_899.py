# -*- coding: utf-8 -*-
"""AIKIA.WALLET pricing scenario B: Basic Rs 899 and Plus Rs 1,199 a month, against scenario A (Rs 499 / Rs 799).
Same cost base as cfo_pricing.py (own Google + Apple wallet, no PassKit). Research checked 19 Oct 2026.
S = published source, E = our estimate."""
import os, math, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_HTML = os.path.join(HERE, "AIKIA-WALLET-Scenario-899.html")
OUT_PDF = os.path.join(HERE, "..", "pdf", "AIKIA-WALLET-Pricing-Scenario-899-1199.pdf")
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
css = open(os.path.join(HERE, "style.css"), encoding="utf-8").read()

def rs(x):
    n = str(int(round(abs(x))))
    if len(n) > 3:
        head, tail = n[:-3], n[-3:]; parts = []
        while len(head) > 2: parts.insert(0, head[-2:]); head = head[:-2]
        if head: parts.insert(0, head)
        n = ",".join(parts) + "," + tail
    return ("-Rs " if x < 0 else "Rs ") + n

def lakh(x): return ("-" if x < 0 else "") + "Rs %.2f lakh" % (abs(x) / 1e5)

# ---------------- shared cost base (same as the CFO plan) ----------------
PLATFORM = 12724; OPS = 5000
DEV_ONE = 110000; LAUNCH_ONE = 97000; UPFRONT = DEV_ONE + LAUNCH_ONE
RECOVERY = UPFRONT / 12
SERVE = 100; ACQUIRE = 1000; PER_CAFE = SERVE + ACQUIRE / 12
FEE = 0.01; CHURN = 0.03; TAX = 0.2517
FIXED_Y1 = PLATFORM + OPS + RECOVERY
FIXED = PLATFORM + OPS
# Above 150 cafes: Supabase compute step-up and a part-time support person (E)
def step_cost(cafes): return (0 if cafes <= 150 else 15000 + 6000) + (0 if cafes <= 300 else 15000)

MIX_PLUS = 0.30
A = dict(name="A", basic=499, plus=799, sales=12)
B = dict(name="B", basic=899, plus=1199, sales=9)
for s in (A, B): s["blend"] = s["basic"] * (1 - MIX_PLUS) + s["plus"] * MIX_PLUS

def net(p): return p * (1 - FEE) - PER_CAFE
def need(p, fixed): return math.ceil(fixed / net(p))
def profit_month(p, cafes): return cafes * net(p) - FIXED - step_cost(cafes)
def cafes_for_profit(p, target):
    n = 1
    while profit_month(p, n) < target: n += 1
    return n

def simulate(price, new, months=36, upfront=UPFRONT):
    cash = -upfront; cafes = 0.0; rows = []; low = cash; be = None; pay = None; cum_profit = 0
    for m in range(1, months + 1):
        cafes = cafes * (1 - CHURN) + new
        income = cafes * price * (1 - FEE)
        cost = PLATFORM + OPS + cafes * SERVE + new * ACQUIRE + step_cost(cafes)
        cash += income - cost
        if be is None and income >= cost: be = m
        if pay is None and cash >= 0: pay = m
        low = min(low, cash)
        rows.append(dict(m=m, cafes=cafes, income=income, cost=cost, cash=cash))
    yr = lambda y: sum(r["income"] - r["cost"] for r in rows[(y - 1) * 12:y * 12])
    return dict(rows=rows, low=low, be=be, pay=pay, y1=yr(1) - upfront, y2=yr(2), y3=yr(3))

SA, SB = simulate(A["blend"], A["sales"]), simulate(B["blend"], B["sales"])
SB_SAME = simulate(B["blend"], 12)
SENS = {n: simulate(B["blend"], n) for n in (6, 9, 12, 15)}

H = []; X = H.append
X('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>AIKIA.WALLET pricing scenario 899</title><style>%s</style></head><body>' % css)

bB, bA = need(B["blend"], FIXED), need(A["blend"], FIXED)
X('''<section class="cover"><div class="band"><div class="ring"></div><div class="ring2"></div>
<div class="kicker">AIKIA.WALLET &nbsp;/&nbsp; PRICING SCENARIO B</div>
<h1 style="max-width:66%%">Rs 899 and Rs 1,199:<br>break-even and profit.</h1>
<p style="max-width:62%%">Basic at Rs 899 a month and Plus at Rs 1,199 a month, set against the Rs 499 / Rs 799 plan. Every cost counted, cafes needed to break even, profit at 50, 100 and 200 cafes, and a 3-year cash plan. Own Google and Apple wallet, no PassKit. October 2026.</p></div>
<div><div class="grid3" style="margin-bottom:5mm">
<div class="card pink"><div class="stat">%d cafes<small>TO BREAK EVEN every month on running costs (Rs 499 plan: %d). %d cafes to also repay development and launch in year 1.</small></div></div>
<div class="card pink"><div class="stat">%s<small>PROFIT A MONTH before tax with 100 cafes (Rs 499 plan: %s).</small></div></div>
<div class="card pink"><div class="stat">month %s<small>EVERY RUPEE BACK, even selling 25%% slower (9 new cafes a month). Rs 499 plan: month %s.</small></div></div>
</div>
<div class="callout ok"><b>Finance desk verdict.</b> Rs 899 / Rs 1,199 is the stronger business: it breaks even with half the cafes, needs less cash in hand and earns about twice the profit per cafe. It still sits far below every Indian competitor we found. The risk is a slower yes from cafes, so it needs a strong founding offer.</div>
<div class="callout warn"><b>How to read this.</b> Planning numbers, not quotes. The average price assumes 30%% of cafes take Plus. Scenario B assumes cafes sign up 25%% slower than at Rs 499 (9 a month instead of 12). Prices are before GST; cafes pay 18%% GST on top if we are registered.</div>
</div></section>''' % (bB, bA, need(B["blend"], FIXED_Y1), rs(profit_month(B["blend"], 100)), rs(profit_month(A["blend"], 100)), SB["pay"], SA["pay"]))

# 1. Research
X('''<section class="sec"><div class="kicker">1 &nbsp;/&nbsp; RESEARCH</div><h2>Where Rs 899 and Rs 1,199 sit in the market</h2>
<table><tr><th>Product</th><th>What it is</th><th class="n">Price a month</th><th class="c">Src</th></tr>
<tr><td>Reelo Growth (India)</td><td>Cafe loyalty and CRM, the main Indian rival</td><td class="n">Rs 3,250 per outlet</td><td class="c">S</td></tr>
<tr><td>DotPe paid tier (India)</td><td>Ordering and restaurant software</td><td class="n">about Rs 2,000</td><td class="c">S</td></tr>
<tr><td>Petpooja POS (India)</td><td>Billing; loyalty is an add-on</td><td class="n">about Rs 3,000 to 5,000 basic (estimates)</td><td class="c">S</td></tr>
<tr><td>Wallet-pass loyalty tools, global</td><td>What independent shops typically spend</td><td class="n">US$19 to 49 (about Rs 1,800 to 4,700)</td><td class="c">S</td></tr>
<tr><td>CHCKN</td><td>Wallet loyalty, up to 500 cards</td><td class="n">US$25 (about Rs 2,400)</td><td class="c">S</td></tr>
<tr><td>FaveCard Pro</td><td>Wallet loyalty</td><td class="n">US$19 (about Rs 1,800)</td><td class="c">S</td></tr>
<tr><td><b>AIKIA.WALLET Basic / Plus (scenario B)</b></td><td>Google and Apple Wallet card, tiers, offers, geofencing; Plus adds credit, gifts, weather</td><td class="n"><b>Rs 899 / Rs 1,199</b></td><td class="c">-</td></tr></table>
<h3>What the research says about Indian buyers</h3>
<ul><li><b>Indian businesses pay 50 to 70%% less</b> than US and EU customers for the same software, and traditional small businesses are the most price-sensitive.</li>
<li><b>Negotiation is expected.</b> Practitioners plan for a 20 to 30%% discount request and set the list price above the target. Rs 899 leaves room to "give" a founding discount and still land near Rs 629 to 719.</li>
<li><b>They pay for immediate, visible value.</b> A card in the customer's phone wallet and repeat visits the owner can count are easier to justify than a dashboard.</li></ul>
<div class="callout"><b>Position.</b> Even at Rs 899 we are about 72%% below Reelo, at the bottom of the global wallet-loyalty range, and the only option with Google and Apple Wallet cards built in. No formal Indian willingness-to-pay survey for this category was found; our first 20 sales calls are the real test.</div>
</section>''')

# 2. Cost base
X('''<section class="sec"><div class="kicker">2 &nbsp;/&nbsp; WHAT IT COSTS</div><h2>The cost base, the same in both scenarios</h2>
<table><tr><th>Cost</th><th class="n">Rs a month</th></tr>
<tr><td>Platform: hosting, database and backups, Apple, weather licence, GitHub, GST on imports, CA</td><td class="n">%s</td></tr>
<tr><td>Management and operations: phone, internet, travel for sales, admin (E)</td><td class="n">%s</td></tr>
<tr><td>Development %s + launch %s, repaid over 12 months (E)</td><td class="n">%s</td></tr>
<tr><td><b>Fixed a month, year 1</b></td><td class="n"><b>%s</b></td></tr>
<tr><td><b>Fixed a month, from year 2</b></td><td class="n"><b>%s</b></td></tr>
<tr><td>Per cafe: support and hosting %s + winning the cafe (Rs 1,000 once, over 12 months) + 1%% collection fee (E)</td><td class="n">%s + 1%%</td></tr>
<tr><td>Step costs past 150 cafes: database upgrade + part-time support person (E); past 300 a second support person</td><td class="n">Rs 21,000 / Rs 36,000</td></tr></table>
<div class="callout warn"><b>Not included.</b> Founder salaries (shown in section 4 as what profit can pay), office rent, paid ads, WhatsApp messages, the credit legal opinion and income tax (shown separately at 25.17%%).</div>
</section>''' % (rs(PLATFORM), rs(OPS), rs(DEV_ONE), rs(LAUNCH_ONE), rs(RECOVERY), rs(FIXED_Y1), rs(FIXED), rs(SERVE), rs(PER_CAFE)))

# 3. Side by side
def cmp_row(label, a, b): return '<tr><td>%s</td><td class="n">%s</td><td class="n"><b>%s</b></td></tr>' % (label, a, b)
X('''<section class="sec"><div class="kicker">3 &nbsp;/&nbsp; SIDE BY SIDE</div><h2>Rs 499 / Rs 799 against Rs 899 / Rs 1,199</h2>
<table><tr><th>Measure</th><th class="n">Scenario A: Rs 499 / Rs 799</th><th class="n">Scenario B: Rs 899 / Rs 1,199</th></tr>
%s%s%s%s%s%s%s%s%s%s%s%s%s</table>
<div class="callout ok"><b>Even if B sells 25%% slower</b> it needs less cash, pays everything back sooner and makes more by year 3. If B sells as fast as A (12 a month), all money is back by month %s and year-3 surplus is %s.</div>
</section>''' % (
    cmp_row("Average price a month (30% on Plus)", rs(A["blend"]), rs(B["blend"])),
    cmp_row("Yearly prices (2 months free)", "Rs 4,999 / Rs 7,999", "Rs 8,999 / Rs 11,999"),
    cmp_row("What each cafe leaves us a month", rs(net(A["blend"])), rs(net(B["blend"]))),
    cmp_row("Cafes to break even on running costs", str(bA), str(bB)),
    cmp_row("Cafes to also repay dev + launch in year 1", str(need(A["blend"], FIXED_Y1)), str(need(B["blend"], FIXED_Y1))),
    cmp_row("New cafes a month assumed", str(A["sales"]), str(B["sales"])),
    cmp_row("Monthly break-even reached", "month %d" % SA["be"], "month %d" % SB["be"]),
    cmp_row("Cash to keep in hand (lowest point)", rs(-SA["low"]), rs(-SB["low"])),
    cmp_row("All money back", "month %d" % SA["pay"], "month %d" % SB["pay"]),
    cmp_row("Profit a month at 50 cafes, before tax", rs(profit_month(A["blend"], 50)), rs(profit_month(B["blend"], 50))),
    cmp_row("Profit a month at 100 cafes, before tax", rs(profit_month(A["blend"], 100)), rs(profit_month(B["blend"], 100))),
    cmp_row("Profit a month at 200 cafes, before tax", rs(profit_month(A["blend"], 200)), rs(profit_month(B["blend"], 200))),
    cmp_row("Cafes for Rs 1 lakh profit a month", str(cafes_for_profit(A["blend"], 100000)), str(cafes_for_profit(B["blend"], 100000))),
    SB_SAME["pay"], rs(SB_SAME["y3"])))

# 4. Profit ladder
lad_rows = ""
for n in (23, 25, 50, 75, 100, 150, 200, 300):
    rev = n * B["blend"] * (1 - FEE); pbt = profit_month(B["blend"], n); pat = pbt * (1 - TAX) if pbt > 0 else pbt
    lad_rows += '<tr><td class="n">%d</td><td class="n">%s</td><td class="n">%s</td><td class="n"><b>%s</b></td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td></tr>' % (
        n, rs(rev), rs(rev - pbt), rs(pbt), rs(pbt * 12), rs(pat), rs(max(pat, 0) / 2))
X('''<section class="sec"><div class="kicker">4 &nbsp;/&nbsp; PROFIT</div><h2>What scenario B earns at each size</h2>
<p class="lede">Steady month from year 2 (development repaid). Average price %s. Tax at 25.17%% (company rate under the 22%% regime).</p>
<table><tr><th class="n">Cafes</th><th class="n">Income a month</th><th class="n">Costs a month</th><th class="n">Profit before tax</th><th class="n">A year</th><th class="n">After tax a month</th><th class="n">Per founder a month</th></tr>%s</table>
<ul><li><b>Break-even at %d cafes.</b> From cafe %d onward each cafe adds about %s a month.</li>
<li><b>100 cafes</b> pay each founder about %s a month after company tax.</li>
<li><b>Above 150 cafes</b> a database upgrade and a part-time support person come in (about Rs 21,000 a month), which the extra cafes cover many times over.</li></ul>
</section>''' % (rs(B["blend"]), lad_rows, bB, bB + 1, rs(net(B["blend"])), rs(profit_month(B["blend"], 100) * (1 - TAX) / 2)))

# 5. Cash plan
def cash_rows(s):
    return "".join('<tr><td>Month %d</td><td class="n">%d</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td></tr>' % (r["m"], round(r["cafes"]), rs(r["income"]), rs(r["cost"]), rs(r["cash"])) for r in s["rows"] if r["m"] in (1, 2, 3, 4, 6, 9, 12, 18, 24, 36))
sens = "".join('<tr><td>%d a month</td><td class="n">month %s</td><td class="n">%s</td><td class="n">month %s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td></tr>' % (
    n, s["be"], rs(-s["low"]), s["pay"] or "36+", lakh(s["y1"]), lakh(s["y2"]), lakh(s["y3"])) for n, s in SENS.items())
X('''<section class="sec"><div class="kicker">5 &nbsp;/&nbsp; CASH PLAN</div><h2>3 years, month by month, scenario B</h2>
<p class="lede">Development and launch paid upfront (%s). %d%% of cafes leave each month. Each new cafe costs Rs 1,000 to win.</p>
<table><tr><th>New cafes a month</th><th class="n">Monthly break-even</th><th class="n">Cash to keep in hand</th><th class="n">All money back</th><th class="n">Year 1 (after upfront)</th><th class="n">Year 2</th><th class="n">Year 3</th></tr>%s</table>
<h3>The plan: 9 new cafes a month</h3>
<table><tr><th>Month</th><th class="n">Active cafes</th><th class="n">Income</th><th class="n">Costs</th><th class="n">Cash position</th></tr>%s</table>
<div class="callout red"><b>Money to keep in hand: %s.</b> With it we never borrow, even at 9 new cafes a month. If we build the remaining work ourselves (Rs 0 development), it falls by Rs 1.1 lakh.</div>
</section>''' % (rs(UPFRONT), int(CHURN * 100), sens, cash_rows(SB), rs(-SB["low"])))

# 6. Recommendation
X('''<section class="sec"><div class="kicker">6 &nbsp;/&nbsp; RECOMMENDATION</div><h2>How to sell Rs 899 so cafes still say yes</h2>
<table><tr><th>Plan</th><th class="n">List a month</th><th class="n">Yearly (2 months free)</th><th class="n">Founding offer, first 50 cafes</th></tr>
<tr><td><b>Basic</b>: wallet card, stamps, tiers, offers, geofencing, staff scanner, unlimited customers</td><td class="n">Rs 899</td><td class="n">Rs 8,999</td><td class="n">Rs 6,999 for the first year</td></tr>
<tr><td><b>Plus</b>: Basic + credit and scan-and-charge, Send-a-gift, weather messages, money report</td><td class="n">Rs 1,199</td><td class="n">Rs 11,999</td><td class="n">Rs 8,999 for the first year</td></tr></table>
<ol><li><b>Lead with the yearly price.</b> "Rs 8,999 a year, Rs 25 a day" is easier than "Rs 899 a month", and brings cash in on day one.</li>
<li><b>The founding offer is the negotiation room.</b> Indian buyers expect 20 to 30%% off; the founding price gives exactly that once, in writing, for the first 50 cafes only.</li>
<li><b>30-day free trial</b> with the card live in the cafe's customers' phones. The trial does the selling.</li>
<li><b>Show the maths to the owner:</b> 2 extra repeat visits a day at Rs 150 pays for Basic in 3 days.</li>
<li><b>Keep Rs 499 in the pocket.</b> If fewer than 1 in 8 pitched cafes sign after 2 months, switch new cafes to the Rs 499 plan (section 3 shows it still works).</li>
<li><b>Never go below the founding price</b> (Rs 6,999 a year, about Rs 583 a month, on Basic), and never give it after the first 50 cafes.</li>
<li><b>Same money rules as before:</b> 3 months of running cost in the bank, churn under 3%%, at least 9 new cafes a month.</li></ol>
<div class="callout"><b>Founding offer check.</b> If all 50 founding cafes pay the founding yearly prices (average about Rs 7,599 a year, about Rs 633 a month), break-even rises to about %d cafes during the founding year. The cafes after 50 pay list price.</div>
<h3>Sources (checked 19 Oct 2026)</h3>
<ul class="srclist small">
<li>Reelo pricing: reelo.io/pricing; techjockey.com/detail/reelocrm</li>
<li>DotPe and Petpooja estimates: codingclave.com/blog/best-restaurant-pos-software-india-2026; dineopen.com/blog/petpooja-pricing-plans-2026</li>
<li>Wallet-pass loyalty prices: loyaltypass.co/blog/guide/loyalty-app-for-small-business; favecard.co/en/blog/loyalty-app-for-small-business; chckn.app magazine (2026 guide)</li>
<li>Indian SaaS pricing and negotiation: upgrowth.in/saas-pricing-packaging-strategy-india-gtm; echai.ventures pricing and packaging; pn.ispirt.in</li>
<li>Company tax 22%% regime, 25.17%% effective: setindiabiz.com/blog/corporate-tax-private-limited-company</li>
<li>SMB churn 3 to 7%% a month: kalungi.com/blog/saas-churn-rate-benchmarks</li>
<li>Cost base: AIKIA.WALLET Launch Costing and CFO Pricing Plan, October 2026</li></ul>
</section>''' % need((0.7 * 6999 + 0.3 * 8999) / 12, FIXED))

X('</body></html>')
open(OUT_HTML, "w", encoding="utf-8").write("".join(H))
r = subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--print-to-pdf=" + os.path.abspath(OUT_PDF), "file:///" + OUT_HTML.replace("\\", "/")], capture_output=True, text=True, timeout=180)
print("pdf", os.path.exists(OUT_PDF), r.returncode)
print("blend", A["blend"], B["blend"], "net", round(net(A["blend"])), round(net(B["blend"])))
print("need", bA, bB, need(A["blend"], FIXED_Y1), need(B["blend"], FIXED_Y1))
for n in (50, 100, 200): print(n, round(profit_month(A["blend"], n)), round(profit_month(B["blend"], n)))
print("1L", cafes_for_profit(A["blend"], 100000), cafes_for_profit(B["blend"], 100000))
for k, s in (("A", SA), ("B", SB), ("Bsame", SB_SAME)): print(k, s["be"], round(s["low"]), s["pay"], round(s["y1"]), round(s["y2"]), round(s["y3"]))
for n, s in SENS.items(): print("sens", n, s["be"], round(s["low"]), s["pay"])
print("founding need", need(633, FIXED))
