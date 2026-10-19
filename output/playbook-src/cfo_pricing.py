# -*- coding: utf-8 -*-
"""AIKIA.WALLET CFO pricing plan: the cheapest price at which we never go into debt.
Own Google + Apple wallet engines (no PassKit). Costs from launch_cost.py, research checked 19 Oct 2026.
S = published source, E = our estimate."""
import os, math, subprocess
from html import escape as e
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_HTML = os.path.join(HERE, "AIKIA-WALLET-CFO-Pricing.html")
OUT_PDF = os.path.join(HERE, "..", "pdf", "AIKIA-WALLET-CFO-Pricing-Break-Even.pdf")
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

# ---------------- cost base (Rs a month unless stated) ----------------
PLATFORM = 12724          # launch_cost.py: Vercel, Supabase, Apple, weather licence, GitHub Team, GST on imports, CA
OPS = 5000                # E: phone and internet 1,000; travel for sales and onboarding 3,000; admin 1,000
DEV_ONE = 110000          # E: 33 days of build left at a partner rate (Rs 0 if we build it ourselves)
LAUNCH_ONE = 97000        # launch_cost.py upper end: lawyer, GST set-up, trademark, standees, test iPhone
RECOVER_MONTHS = 12       # repay development and launch costs within the first year
RECOVERY = (DEV_ONE + LAUNCH_ONE) / RECOVER_MONTHS

PER_CAFE_SERVE = 100      # E: support time, hosting growth, messages, per cafe a month
ACQUIRE = 1000            # E: standee 400 + visit and travel 600, once per cafe
ACQ_MONTHS = 12
PER_CAFE = PER_CAFE_SERVE + ACQUIRE / ACQ_MONTHS
FEE = 0.01                # E: UPI Autopay collection (no MDR on mandates), gateway platform fee about 1%
CHURN = 0.03              # monthly, low end of the 3 to 7% SMB benchmark

FIXED_Y1 = PLATFORM + OPS + RECOVERY
FIXED_LATER = PLATFORM + OPS
STIPEND = 50000           # optional: Rs 25,000 a month each for two founders

def net(p): return p * (1 - FEE) - PER_CAFE
def need(p, fixed):
    n = net(p)
    return math.ceil(fixed / n) if n > 0 else None

PRICES = [299, 399, 499, 599, 699, 799, 999]

# ---------------- cash simulation ----------------
def simulate(price, new_per_month, months=24, setup=0, fixed_recovery=False, stipend=0, upfront=DEV_ONE + LAUNCH_ONE):
    """Month-by-month cash. Development and launch are paid upfront (month 0); no recovery line, the cash low point is the money needed."""
    cash = -upfront; cafes = 0.0; low = cash; low_m = 0; be_m = None; rows = []
    for m in range(1, months + 1):
        lost = cafes * CHURN
        cafes = cafes - lost + new_per_month
        income = cafes * price * (1 - FEE) + new_per_month * setup
        cost = PLATFORM + OPS + stipend + cafes * PER_CAFE_SERVE + new_per_month * ACQUIRE
        cash += income - cost
        if income >= cost and be_m is None: be_m = m
        if cash < low: low, low_m = cash, m
        rows.append(dict(m=m, cafes=cafes, income=income, cost=cost, cash=cash))
    payback = next((r["m"] for r in rows if r["cash"] >= 0), None)
    return dict(rows=rows, low=low, low_m=low_m, be_m=be_m, payback=payback)

PLAN = dict(price=499, plus=799, mix_plus=0.3)
BLEND = PLAN["price"] * (1 - PLAN["mix_plus"]) + PLAN["plus"] * PLAN["mix_plus"]
SIM_SLOW = simulate(BLEND, 8)
SIM_BASE = simulate(BLEND, 12)
SIM_FAST = simulate(BLEND, 20)

# ---------------- HTML ----------------
H = []; A = H.append
A('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>AIKIA.WALLET CFO pricing</title><style>%s</style></head><body>' % css)

n499y1, n499 = need(499, FIXED_Y1), need(499, FIXED_LATER)
nbl, nbly1 = need(BLEND, FIXED_LATER), need(BLEND, FIXED_Y1)
A('''<section class="cover"><div class="band"><div class="ring"></div><div class="ring2"></div>
<div class="kicker">AIKIA.WALLET &nbsp;/&nbsp; CFO PRICING PLAN</div>
<h1 style="max-width:66%%">The cheapest price<br>that keeps us<br>out of debt.</h1>
<p style="max-width:62%%">Every cost counted: platform, data, management, sales, development and launch. Then the lowest monthly price at which the cafes pay for all of it, and how many cafes that takes. Own Google and Apple wallet engines, no PassKit. October 2026.</p></div>
<div><div class="grid3" style="margin-bottom:5mm">
<div class="card pink"><div class="stat">Rs 499<small>A MONTH, Basic plan (Rs 4,999 a year). Rs 17 a day: less than one cup of coffee. 85%% below Reelo's Growth plan.</small></div></div>
<div class="card pink"><div class="stat">%d cafes<small>TO BREAK EVEN every month on running costs (30%% on the Rs 799 Plus plan). %d cafes to also repay development and launch within 12 months.</small></div></div>
<div class="card pink"><div class="stat">%s<small>CASH TO HAVE IN HAND before launch, so we never borrow: the lowest point at 12 new cafes a month.</small></div></div>
</div>
<div class="callout ok"><b>The decision.</b> Basic Rs 499 a month (or Rs 4,999 a year), Plus Rs 799 a month (or Rs 7,999 a year), no setup fee for the first 50 founding cafes. Prices before GST. Break-even at about %d cafes; all money back by month %s at 12 new cafes a month.</div>
<div class="callout red"><b>Why not cheaper.</b> At Rs 299 we would need %d cafes just to cover running costs. For a brand nobody knows yet, that is a year of selling before we stop losing money. Rs 499 is cheap enough to feel like no risk and still reachable.</div>
</div></section>''' % (nbl, nbly1, rs(-SIM_BASE["low"]), nbl, SIM_BASE["payback"], need(299, FIXED_LATER)))

# 1. Market
A('''<section class="sec"><div class="kicker">1 &nbsp;/&nbsp; THE MARKET PRICE</div><h2>What cafes pay today</h2>
<table><tr><th>Option</th><th>What it is</th><th class="n">Price</th><th class="c">Src</th></tr>
<tr><td><b>Reelo Growth</b></td><td>The best-known cafe loyalty and CRM tool in India</td><td class="n">Rs 3,250 a month per outlet (Rs 39,000 a year + GST)</td><td class="c">S</td></tr>
<tr><td><b>Reelo Forever Free</b></td><td>Basic SMS and email campaigns, customer insights</td><td class="n">Rs 0</td><td class="c">S</td></tr>
<tr><td><b>Petpooja POS</b></td><td>Billing software; loyalty and wallet are add-ons priced on request</td><td class="n">about Rs 10,000 to 12,000 a year base</td><td class="c">S</td></tr>
<tr><td><b>Paper stamp cards</b></td><td>Printed cards and a rubber stamp</td><td class="n">Rs 1,000 to 3,000 a year</td><td class="c">E</td></tr>
<tr><td><b>AIKIA.WALLET Basic (proposed)</b></td><td>Google and Apple Wallet card, stamps, tiers, offers, geofencing, no app download</td><td class="n"><b>Rs 499 a month</b></td><td class="c">-</td></tr></table>
<div class="callout"><b>Where we stand.</b> At Rs 499 we are about 85%% below Reelo's paid plan and cost about the same as a year of paper stamp cards, yet the card lives in the customer's phone wallet. Reelo's free plan is the real competitor at the bottom: our answer is the wallet card itself, which no free tool gives.</div>
<p class="small">India has about 5,339 branded coffee-shop outlets (World Coffee Portal, 2025) and independent outlets are about 76%% of the cafes-and-bars market (Mordor Intelligence). A city-by-city count of independent cafes in Vadodara, Ahmedabad and Surat is NOT DOCUMENTED; we need it before planning beyond 100 cafes.</p>
</section>''')

# 2. Cost base
A('''<section class="sec"><div class="kicker">2 &nbsp;/&nbsp; EVERY COST</div><h2>What the cafes have to pay for</h2>
<table><tr><th>Cost</th><th>What it covers</th><th class="c">Src</th><th class="n">Rs a month</th></tr>
<tr><td><b>Platform</b></td><td>Hosting, database and ledger with backups, Apple Developer, weather licence, GitHub, GST on imported software, CA</td><td class="c">S/E</td><td class="n">%s</td></tr>
<tr><td><b>Management and operations</b></td><td>Phone and internet, travel for sales and onboarding, admin</td><td class="c">E</td><td class="n">%s</td></tr>
<tr><td><b>Development and launch, repaid in 12 months</b></td><td>%s build left (partner rate) + %s launch costs, spread over 12 months</td><td class="c">E</td><td class="n">%s</td></tr>
<tr><td colspan="3"><b>Fixed cost a month, year 1</b></td><td class="n"><b>%s</b></td></tr>
<tr><td colspan="3"><b>Fixed cost a month, from year 2</b> (development repaid)</td><td class="n"><b>%s</b></td></tr></table>
<table><tr><th>Cost per cafe</th><th>What it covers</th><th class="c">Src</th><th class="n">Rs a month</th></tr>
<tr><td>Serving</td><td>Support calls, hosting growth, card messages</td><td class="c">E</td><td class="n">%s</td></tr>
<tr><td>Winning the cafe</td><td>Standee and onboarding visit (Rs 1,000 once), spread over 12 months</td><td class="c">E</td><td class="n">%s</td></tr>
<tr><td>Collecting the fee</td><td>UPI Autopay mandate: no MDR; gateway platform fee about 1%%</td><td class="c">S/E</td><td class="n">1%% of price</td></tr>
<tr><td colspan="3"><b>Per cafe a month</b></td><td class="n"><b>%s + 1%%</b></td></tr></table>
<div class="callout warn"><b>What is not in here.</b> Founder salaries (shown separately in section 4), office rent, paid ads, WhatsApp messages and the credit legal opinion. If we build the remaining work ourselves with Claude, development is Rs 0 and year-1 break-even drops sharply.</div>
</section>''' % (rs(PLATFORM), rs(OPS), rs(DEV_ONE), rs(LAUNCH_ONE), rs(RECOVERY), rs(FIXED_Y1), rs(FIXED_LATER), rs(PER_CAFE_SERVE), rs(ACQUIRE / ACQ_MONTHS), rs(PER_CAFE)))

# 3. Price ladder
lad = "".join('<tr%s><td>Rs %s</td><td class="n">Rs %s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td></tr>' % (
    ' style="background:#fff0f7"' if p == 499 else "", "{:,}".format(p), "{:,}".format(p * 10 + 9 if p * 10 < 10000 else p * 10), rs(net(p)), need(p, FIXED_LATER), need(p, FIXED_Y1), need(p, FIXED_LATER + STIPEND)) for p in PRICES)
A('''<section class="sec"><div class="kicker">3 &nbsp;/&nbsp; THE PRICE LADDER</div><h2>Cafes needed at each price</h2>
<p class="lede">Each cafe leaves us its price minus the 1%% collection fee and %s of its own cost. That remainder has to cover the fixed bill.</p>
<table><tr><th>A month</th><th class="n">A year</th><th class="n">Left per cafe</th><th class="n">Break-even, running costs</th><th class="n">Also repay dev + launch in 12 months</th><th class="n">Also pay founders Rs 25,000 each</th></tr>%s</table>
<h3>Reading the ladder</h3>
<ul><li><b>Rs 299</b> is the cheapest price that covers anything, but needs %d cafes before we stop losing money. Too slow for a new brand.</li>
<li><b>Rs 499</b> is the sweet spot: Rs 17 a day for the cafe, and %d cafes to cover running costs.</li>
<li><b>Rs 999 and up</b> breaks even faster, but loses the "too cheap to say no" message we need without references.</li>
<li><b>Every price below about Rs %d loses money on each cafe</b>, whatever the number of cafes.</li></ul>
</section>''' % (rs(PER_CAFE), lad, need(299, FIXED_LATER), need(499, FIXED_LATER), math.ceil(PER_CAFE / (1 - FEE))))

# 4. Plans
A('''<section class="sec"><div class="kicker">4 &nbsp;/&nbsp; THE OFFER</div><h2>Two cheap plans, one clear choice</h2>
<table><tr><th>Plan</th><th>Includes</th><th class="n">Monthly</th><th class="n">Yearly (2 months free)</th></tr>
<tr><td><b>Basic</b></td><td>Google and Apple Wallet card with the cafe's brand, stamps and free-reward rule, 3 tiers, staff scanner, offers and campaign messages, geofencing, owner dashboard, unlimited customers</td><td class="n">Rs 499</td><td class="n">Rs 4,999</td></tr>
<tr><td><b>Plus</b></td><td>Everything in Basic, plus prepaid credit with scan-and-charge, Send-a-gift, weather-mood messages and the monthly money report</td><td class="n">Rs 799</td><td class="n">Rs 7,999</td></tr></table>
<ul><li><b>No setup fee for the first 50 founding cafes</b>; Rs 999 setup after that.</li>
<li><b>30-day free trial</b>, no card needed. Billing by UPI Autopay so renewals never need a reminder.</li>
<li><b>Prices before GST.</b> Below Rs 20 lakh a year of turnover a service business usually doesn't need GST registration; ask the CA whether to register from day one (it lets us claim back GST on imported software).</li>
<li><b>Founding price lock:</b> the first 50 cafes keep their price for 2 years. That is the trust-builder we can afford.</li></ul>
<div class="callout ok"><b>Blended price.</b> If 30%% of cafes take Plus, the average is %s a month. Break-even on running costs: <b>%d cafes</b>. Repay development and launch within 12 months as well: <b>%d cafes</b>.</div>
<div class="callout warn"><b>Credit on Plus.</b> Prepaid credit with real money waits for the lawyer's written opinion. Until then Plus sells on gifts, weather messages and the report, and credit is switched on per cafe once cleared.</div>
</section>''' % (rs(BLEND), nbl, nbly1))

# 5. Cash plan
def sim_table(s):
    keep = [1, 2, 3, 4, 6, 8, 10, 12, 18, 24]
    return "".join('<tr><td>Month %d</td><td class="n">%d</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td></tr>' % (r["m"], round(r["cafes"]), rs(r["income"]), rs(r["cost"]), rs(r["cash"])) for r in s["rows"] if r["m"] in keep)
A('''<section class="sec"><div class="kicker">5 &nbsp;/&nbsp; CASH PLAN</div><h2>Month by month, so we never borrow</h2>
<p class="lede">Development and launch are paid upfront (%s). Then each month: income from active cafes, running costs, and %d%% of cafes leaving (the low end of the 3 to 7%% small-business benchmark). Blended price %s.</p>
<table><tr><th>New cafes a month</th><th class="n">Monthly break-even reached</th><th class="n">Lowest cash point</th><th class="n">All money back</th></tr>
<tr><td>8 (slow)</td><td class="n">month %s</td><td class="n">%s</td><td class="n">month %s</td></tr>
<tr><td><b>12 (plan)</b></td><td class="n"><b>month %s</b></td><td class="n"><b>%s</b></td><td class="n"><b>month %s</b></td></tr>
<tr><td>20 (strong)</td><td class="n">month %s</td><td class="n">%s</td><td class="n">month %s</td></tr></table>
<p class="small">Monthly break-even in the cash plan comes later than the 45 cafes in section 4 because each month also pays Rs 12,000 to win 12 new cafes. Stop adding cafes and 45 is enough.</p>
<h3>The plan, 12 new cafes a month</h3>
<table><tr><th>Month</th><th class="n">Active cafes</th><th class="n">Income</th><th class="n">Costs</th><th class="n">Cash position</th></tr>%s</table>
<div class="callout red"><b>Money to keep in hand: %s.</b> That is the deepest point of the plan. With it we never borrow. If we build the remaining work ourselves (Rs 0 development) it falls to about %s.</div>
</section>''' % (rs(DEV_ONE + LAUNCH_ONE), int(CHURN * 100), rs(BLEND),
    SIM_SLOW["be_m"], rs(-SIM_SLOW["low"]), SIM_SLOW["payback"] or "24+", SIM_BASE["be_m"], rs(-SIM_BASE["low"]), SIM_BASE["payback"] or "24+", SIM_FAST["be_m"], rs(-SIM_FAST["low"]), SIM_FAST["payback"] or "24+",
    sim_table(SIM_BASE), rs(-SIM_BASE["low"]), rs(-simulate(BLEND, 12, upfront=LAUNCH_ONE)["low"])))

# 6. Sales targets and rules
A('''<section class="sec"><div class="kicker">6 &nbsp;/&nbsp; HOW WE GET THERE</div><h2>Sales targets and money rules</h2>
<table><tr><th>Target</th><th class="n">Cafes</th><th>What it takes</th></tr>
<tr><td>Weekly</td><td class="n">3</td><td>About 15 cafe visits a week with the live demo (1 in 5 signs)</td></tr>
<tr><td>Month 3</td><td class="n">about 34</td><td>Vadodara cafes and bakeries; the first case study</td></tr>
<tr><td>Month 4 to 5</td><td class="n">%d</td><td>Monthly break-even on running costs</td></tr>
<tr><td>Month 12</td><td class="n">about %d</td><td>Expand to Ahmedabad and Surat, and to sweet shops, salons and gyms at the same price</td></tr></table>
<h3>Rules from the finance desk</h3>
<ol><li><b>Sell yearly first.</b> Offer Rs 4,999 a year with two months free. Ten yearly cafes bring Rs 50,000 on day one, which funds the launch without borrowing.</li>
<li><b>Never go below Rs %d a month.</b> Below that, each cafe costs more than it pays.</li>
<li><b>No discounts on top of the founding offer.</b> The price is already the discount.</li>
<li><b>Keep 3 months of running cost (%s) in the bank</b> at all times.</li>
<li><b>Watch two numbers every month:</b> cafes leaving (keep under 3%%) and new cafes (keep at or above 12).</li>
<li><b>Raise prices only for new cafes</b>, once we have 3 case studies and 50+ cafes. Founding cafes keep theirs.</li>
<li><b>Build the remaining work ourselves</b> where we can: every Rs 1 lakh saved on development is about 20 fewer cafes needed in year one.</li></ol>
<h3>Sources (checked 19 Oct 2026)</h3>
<ul class="srclist small">
<li>Reelo pricing, Growth Rs 3,250 a month per outlet and Forever Free: reelo.io/pricing; techjockey.com/detail/reelocrm</li>
<li>Petpooja price estimates: dineopen.com/blog/petpooja-pricing-plans-2026; techjockey.com/detail/petpooja-pos</li>
<li>Cafe market: worldcoffeeportal.com Project Cafe India 2025 (5,339 branded outlets); mordorintelligence.com India cafes and bars market</li>
<li>UPI Autopay mandates and MDR: razorpay.com/blog/upi-mdr-for-merchants-in-payment-gateway-explained</li>
<li>SMB churn 3 to 7%% a month: kalungi.com/blog/saas-churn-rate-benchmarks; velaris.io</li>
<li>Platform costs: AIKIA.WALLET Launch Costing (own wallet), October 2026</li></ul>
</section>''' % (nbl, round(SIM_BASE["rows"][11]["cafes"]), math.ceil(PER_CAFE / (1 - FEE)), rs(3 * FIXED_LATER)))

A('</body></html>')
open(OUT_HTML, "w", encoding="utf-8").write("".join(H))
r = subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--print-to-pdf=" + os.path.abspath(OUT_PDF), "file:///" + OUT_HTML.replace("\\", "/")], capture_output=True, text=True, timeout=180)
print("pdf", os.path.exists(OUT_PDF), r.returncode)
print("fixed y1", round(FIXED_Y1), "later", round(FIXED_LATER), "per cafe", round(PER_CAFE), "blend", BLEND)
print("ladder", [(p, need(p, FIXED_LATER), need(p, FIXED_Y1), need(p, FIXED_LATER + STIPEND)) for p in PRICES])
print("blend need", nbl, nbly1)
for n, s in (("slow", SIM_SLOW), ("base", SIM_BASE), ("fast", SIM_FAST)): print(n, s["be_m"], round(s["low"]), s["low_m"], s["payback"])
print([(r["m"], round(r["cafes"]), round(r["cash"])) for r in SIM_BASE["rows"]][:14])
