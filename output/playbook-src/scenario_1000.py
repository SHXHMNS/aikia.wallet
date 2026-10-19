# -*- coding: utf-8 -*-
"""AIKIA.WALLET pricing scenario C: one fixed price, Rs 1,000 a month or Rs 12,000 a year, all features, no negotiation.
Same cost base as the CFO plan (own Google + Apple wallet, no PassKit). Research checked 19 Oct 2026.
S = published source, E = our estimate."""
import os, math, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_HTML = os.path.join(HERE, "AIKIA-WALLET-Scenario-1000.html")
OUT_PDF = os.path.join(HERE, "..", "pdf", "AIKIA-WALLET-Pricing-Fixed-1000.pdf")
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

# ---------------- cost base (same as CFO plan) ----------------
PLATFORM = 12724; OPS = 5000
IMPORT_GST = 1560          # GST paid on imported software inside PLATFORM; claimable once GST-registered
DEV_ONE = 110000; LAUNCH_ONE = 97000; UPFRONT = DEV_ONE + LAUNCH_ONE; RECOVERY = UPFRONT / 12
SERVE = 100; ACQUIRE = 1000; PER_CAFE = SERVE + ACQUIRE / 12
FEE = 0.01; CHURN = 0.03; TAX = 0.2517
FIXED_Y1 = PLATFORM + OPS + RECOVERY; FIXED = PLATFORM + OPS
def step_cost(c): return (0 if c <= 150 else 21000) + (0 if c <= 300 else 15000)

PRICE = 1000; YEAR = 12000
GST_THRESHOLD_CAFES = math.ceil(2000000 / YEAR)

# GST cases: what we keep per Rs 1,000 and the fixed cost
CASES = {
    "nogst": dict(label="Not GST-registered (under Rs 20 lakh a year)", keep=1000.0, fixed=FIXED, fixed_y1=FIXED_Y1, cafe_pays=1000),
    "plus": dict(label="Registered, Rs 1,000 + 18% GST (cafe pays Rs 1,180)", keep=1000.0, fixed=FIXED - IMPORT_GST, fixed_y1=FIXED_Y1 - IMPORT_GST, cafe_pays=1180),
    "incl": dict(label="Registered, Rs 1,000 including GST", keep=1000 / 1.18, fixed=FIXED - IMPORT_GST, fixed_y1=FIXED_Y1 - IMPORT_GST, cafe_pays=1000),
}
def net(keep): return keep * (1 - FEE) - PER_CAFE
def need(keep, fixed): return math.ceil(fixed / net(keep))
def profit(keep, fixed, c): return c * net(keep) - fixed - step_cost(c)
def cafes_for(keep, fixed, target):
    n = 1
    while profit(keep, fixed, n) < target: n += 1
    return n

# ---------------- cash with monthly and yearly payers ----------------
def simulate(keep, fixed, new, yearly_share=0.4, months=36, upfront=UPFRONT):
    monthly = 0.0; cohorts = []   # yearly cohorts: (start month, cafes)
    cash = -upfront; rows = []; low = cash; be = pay = None
    yr_keep = keep * 12
    for m in range(1, months + 1):
        monthly = monthly * (1 - CHURN) + new * (1 - yearly_share)
        cohorts.append([m, new * yearly_share])
        income = monthly * keep * (1 - FEE)
        for c in cohorts:
            if (m - c[0]) % 12 == 0:
                if m != c[0]: c[1] *= (1 - CHURN) ** 12   # some yearly cafes don't renew
                income += c[1] * yr_keep * (1 - FEE)
        active = monthly + sum(c[1] for c in cohorts)
        cost = fixed + active * SERVE + new * ACQUIRE + step_cost(active)
        cash += income - cost
        earned = active * keep * (1 - FEE)   # what the month's service is worth, however it was paid
        if be is None and earned >= cost: be = m
        if pay is None and cash >= 0: pay = m
        low = min(low, cash)
        rows.append(dict(m=m, cafes=active, income=income, cost=cost, cash=cash))
    yr = lambda y: sum(r["income"] - r["cost"] for r in rows[(y - 1) * 12:y * 12])
    return dict(rows=rows, low=low, be=be, pay=pay, y1=yr(1) - upfront, y2=yr(2), y3=yr(3))

C = CASES["plus"]   # decided 19 Oct 2026: Rs 1,000 a month plus GST, GST-registered from day one
S_MAIN = simulate(C["keep"], C["fixed"], 9)
S_MONTHLY = simulate(C["keep"], C["fixed"], 9, yearly_share=0.0)
SENS = {n: simulate(C["keep"], C["fixed"], n) for n in (6, 9, 12, 15)}

# comparison with earlier scenarios (blended prices, same cost base)
CMP = [("A: Rs 499 / Rs 799 (30% Plus)", 589.0, 12), ("B: Rs 899 / Rs 1,199 (30% Plus)", 989.0, 9), ("C: Rs 1,000 flat, all features", 1000.0, 9)]

H = []; X = H.append
X('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>AIKIA.WALLET fixed Rs 1,000</title><style>%s</style></head><body>' % css)

X('''<section class="cover"><div class="band"><div class="ring"></div><div class="ring2"></div>
<div class="kicker">AIKIA.WALLET &nbsp;/&nbsp; PRICING SCENARIO C</div>
<h1 style="max-width:70%%">Rs 1,000 + GST.<br>One price,<br>no haggling.</h1>
<p style="max-width:62%%">One fixed price for every cafe: Rs 1,000 a month or Rs 12,000 a year, plus 18%% GST, every feature included, no discounts. What it costs, how many cafes break even, the profit at each size, a 3-year cash plan, and the GST decision that changes the numbers. Own Google and Apple wallet, no PassKit. October 2026.</p></div>
<div><div class="grid3" style="margin-bottom:5mm">
<div class="card pink"><div class="stat">%d cafes<small>TO BREAK EVEN every month on running costs. %d cafes to also repay development and launch in year 1.</small></div></div>
<div class="card pink"><div class="stat">%s<small>PROFIT A MONTH before tax with 100 cafes. %d cafes make Rs 1 lakh a month.</small></div></div>
<div class="card pink"><div class="stat">month %s<small>EVERY RUPEE BACK at 9 new cafes a month, with 4 in 10 cafes paying yearly. Cash to keep in hand: %s.</small></div></div>
</div>
<div class="callout ok"><b>Finance desk verdict.</b> Rs 1,000 flat is the best of the three plans for us: the highest money per cafe, the fewest cafes to break even, nothing to negotiate and nothing to explain. It is still 69%% below Reelo. Two conditions: GST registration done before the first invoice, and the yearly plan offered first.</div>
<div class="callout warn"><b>Plus GST, registered from day one.</b> The cafe pays Rs 1,180 a month (Rs 14,160 a year); we keep the full Rs 1,000 and claim back the GST on our own imported software. GST-registered cafes claim the Rs 180 back. Cafes on the composition scheme or not registered can't, so for them the real price is Rs 1,180. (For reference: unregistered we would need %d cafes; quoting Rs 1,000 including GST would push it to %d.)</div>
</div></section>''' % (need(C["keep"], C["fixed"]), need(C["keep"], C["fixed_y1"]), rs(profit(C["keep"], C["fixed"], 100)), cafes_for(C["keep"], C["fixed"], 100000), S_MAIN["pay"], rs(-S_MAIN["low"]), need(1000, FIXED), need(CASES["incl"]["keep"], CASES["incl"]["fixed"])))

# 1. Research
X('''<section class="sec"><div class="kicker">1 &nbsp;/&nbsp; RESEARCH</div><h2>Is one fixed Rs 1,000 price right for India?</h2>
<table><tr><th>Finding</th><th>What it means for us</th><th class="c">Src</th></tr>
<tr><td><b>One flat plan is easy to explain, sell and forecast</b>, but gives up upsell revenue. Companies that moved from tiers to one plan did it for higher conversion.</td><td>Right for launch: one sentence pitch, one invoice, one price on the poster. Add-ons can come later.</td><td class="c">S</td></tr>
<tr><td><b>Indian small businesses compare against the cheapest option</b> and usually ask for special pricing.</td><td>A written fixed price with a public "same price for everyone" rule ends the haggle. The answer to a discount request is the yearly plan, not a lower price.</td><td class="c">S</td></tr>
<tr><td><b>Cutting price too far breaks unit economics</b>: one Indian SaaS at Rs 299 got more sign-ups but lost money and moved back to tiers.</td><td>Rs 1,000 keeps about Rs 807 per cafe after costs, the healthiest of our three options.</td><td class="c">S</td></tr>
<tr><td><b>Rs 999-style "charm" prices lift consumer sales</b>; no evidence was found for business buyers.</td><td>For a cafe owner, "Rs 1,000 a month" and "Rs 12,000 a year" are cleaner and signal a fixed, honest price.</td><td class="c">S</td></tr>
<tr><td><b>Competitors:</b> Reelo Rs 3,250 a month; DotPe about Rs 2,000; global wallet-loyalty tools US$19 to 49 (Rs 1,800 to 4,700).</td><td>Rs 1,000 is 69%% below Reelo and below every wallet-loyalty tool found.</td><td class="c">S</td></tr>
<tr><td><b>GST on software is 18%%</b>; service businesses register above Rs 20 lakh a year of turnover.</td><td>We register from day one and bill Rs 1,000 + 18%% GST. See section 3.</td><td class="c">S</td></tr></table>
<div class="callout"><b>Positioning line.</b> "Rs 1,000 a month plus GST. About Rs 33 a day. Less than one cappuccino. Same price for every cafe, every feature included." No Indian survey of what cafes will pay for this category was found; the first 20 pitches are the test.</div>
</section>''')

# 2. What the cafe gets + cost
X('''<section class="sec"><div class="kicker">2 &nbsp;/&nbsp; THE OFFER AND THE COST</div><h2>Everything for Rs 1,000</h2>
<table><tr><th>Included for every cafe</th></tr>
<tr><td>Google Wallet and Apple Wallet card in the cafe's brand; Ink, Chrome and Pink metallic tiers</td></tr>
<tr><td>Stamps and free-reward rule, tiers by visits or by spend, unlimited customers</td></tr>
<tr><td>Staff scanner with one-step scan-and-charge; owner dashboard; team logins</td></tr>
<tr><td>Prepaid credit and top-up packs (once the lawyer clears real-money credit), pay codes, Send-a-gift</td></tr>
<tr><td>Offers, scheduled and win-back campaigns, weather-mood messages, geofencing (up to 10 locations)</td></tr>
<tr><td>Monthly report: visits, members, credit loaded and spent; QR standee; onboarding and staff training</td></tr></table>
<table><tr><th>Our cost</th><th class="n">Rs a month</th></tr>
<tr><td>Platform: hosting, database and backups, Apple, weather licence, GitHub, GST on imports, CA</td><td class="n">%s</td></tr>
<tr><td>Management and operations (E)</td><td class="n">%s</td></tr>
<tr><td>Development %s + launch %s, repaid over 12 months (E)</td><td class="n">%s</td></tr>
<tr><td><b>Fixed a month, year 1 / from year 2</b></td><td class="n"><b>%s / %s</b></td></tr>
<tr><td>Per cafe: support and hosting, winning the cafe (Rs 1,000 once over 12 months), 1%% collection fee (E)</td><td class="n">%s + 1%%</td></tr>
<tr><td><b>What each cafe leaves us</b> (Rs 1,000; the GST goes to the government)</td><td class="n"><b>%s</b></td></tr></table>
</section>''' % (rs(PLATFORM), rs(OPS), rs(DEV_ONE), rs(LAUNCH_ONE), rs(RECOVERY), rs(FIXED_Y1), rs(FIXED), rs(PER_CAFE), rs(net(1000))))

# 3. GST cases
g = "".join('<tr><td>%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%d</td><td class="n">%d</td><td class="n">%s</td></tr>' % (
    v["label"], rs(v["cafe_pays"]), rs(v["keep"]), rs(net(v["keep"])), need(v["keep"], v["fixed"]), need(v["keep"], v["fixed_y1"]), rs(profit(v["keep"], v["fixed"], 100))) for v in CASES.values())
X('''<section class="sec"><div class="kicker">3 &nbsp;/&nbsp; THE GST DECISION</div><h2>Why "Rs 1,000 + GST" is the right way to bill</h2>
<table><tr><th>How we bill</th><th class="n">Cafe pays</th><th class="n">We keep</th><th class="n">Left after cafe costs</th><th class="n">Break-even cafes</th><th class="n">Year 1 incl. dev</th><th class="n">Profit at 100 cafes</th></tr>%s</table>
<ul><li><b>Our choice: registered, "Rs 1,000 + GST"</b> (the middle row). We keep the full Rs 1,000, give every cafe a proper GST invoice, and claim back the GST on our imported software (about %s a month).</li>
<li><b>The cafe pays Rs 1,180 a month or Rs 14,160 a year.</b> GST-registered cafes claim the Rs 180 back as input credit. Small cafes on the composition scheme, or not registered, can't, so for them the price is really Rs 1,180. Say it upfront.</li>
<li><b>Never let it slip to "Rs 1,000 including GST":</b> that quietly cuts %s from every cafe every month.</li>
<li>Below Rs 20 lakh a year (about %d cafes) registration is voluntary. Registering from day one is the cleaner, more trusted choice; it needs monthly GST returns, which the CA retainer already covers.</li></ul>
<div class="callout warn"><b>Ask the CA.</b> GST registration before the first invoice, the invoice format, the place-of-supply rules if we sell outside Gujarat, and whether cafes will want a GST invoice. These figures are a briefing, not tax advice.</div>
</section>''' % (g, rs(IMPORT_GST), rs(1000 - 1000 / 1.18), GST_THRESHOLD_CAFES))

# 4. Profit ladder
rows = ""
for n in (22, 25, 50, 75, 100, 150, 166, 200, 300):
    k = CASES["plus"]
    rev = n * k["keep"] * (1 - FEE); pbt = profit(k["keep"], k["fixed"], n); pat = pbt * (1 - TAX) if pbt > 0 else pbt
    rows += '<tr><td class="n">%d</td><td class="n">%s</td><td class="n">%s</td><td class="n"><b>%s</b></td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td></tr>' % (n, rs(rev), rs(rev - pbt), rs(pbt), rs(pbt * 12), rs(pat), rs(max(pat, 0) / 2))
X('''<section class="sec"><div class="kicker">4 &nbsp;/&nbsp; PROFIT</div><h2>What Rs 1,000 earns at each size</h2>
<p class="lede">Steady month from year 2. Billing Rs 1,000 + GST; income below is what we keep (GST goes to the government), before company tax at 25.17%%.</p>
<table><tr><th class="n">Cafes</th><th class="n">Income a month</th><th class="n">Costs a month</th><th class="n">Profit before tax</th><th class="n">A year</th><th class="n">After tax a month</th><th class="n">Per founder a month</th></tr>%s</table>
<ul><li><b>Break-even at %d cafes.</b> Each cafe after that adds about %s a month.</li>
<li><b>100 cafes</b>: about %s a month before tax, about %s per founder after tax.</li>
<li><b>Rs 1 lakh profit a month</b> at about %d cafes.</li></ul>
</section>''' % (rows, need(1000, C["fixed"]), rs(net(1000)), rs(profit(1000, C["fixed"], 100)), rs(profit(1000, C["fixed"], 100) * (1 - TAX) / 2), cafes_for(1000, C["fixed"], 100000)))

# 5. Cash plan
sens = "".join('<tr><td>%d a month</td><td class="n">month %s</td><td class="n">%s</td><td class="n">month %s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td></tr>' % (n, s["be"], rs(-s["low"]), s["pay"] or "36+", lakh(s["y1"]), lakh(s["y2"]), lakh(s["y3"])) for n, s in SENS.items())
plan = "".join('<tr><td>Month %d</td><td class="n">%d</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td></tr>' % (r["m"], round(r["cafes"]), rs(r["income"]), rs(r["cost"]), rs(r["cash"])) for r in S_MAIN["rows"] if r["m"] in (1, 2, 3, 4, 6, 9, 12, 13, 18, 24, 36))
X('''<section class="sec"><div class="kicker">5 &nbsp;/&nbsp; CASH PLAN</div><h2>3 years, with 4 in 10 cafes paying yearly</h2>
<p class="lede">Monthly break-even is measured on earned income (Rs 1,000 a month per active cafe, however they paid); cash is shown separately. Development and launch paid upfront (%s). 40%% of cafes pay Rs 12,000 upfront for the year; the rest pay Rs 1,000 a month. 3%% of monthly cafes leave each month; the same rate applies to yearly renewals. Billed Rs 1,000 + GST; the GST collected goes to the government and is not counted.</p>
<table><tr><th>New cafes a month</th><th class="n">Monthly break-even</th><th class="n">Cash to keep in hand</th><th class="n">All money back</th><th class="n">Year 1 (after upfront)</th><th class="n">Year 2</th><th class="n">Year 3</th></tr>%s</table>
<h3>The plan: 9 new cafes a month</h3>
<table><tr><th>Month</th><th class="n">Active cafes</th><th class="n">Money in</th><th class="n">Costs</th><th class="n">Cash position</th></tr>%s</table>
<div class="callout ok"><b>Why yearly matters.</b> If every cafe paid monthly instead, the cash low point would be %s and all money back by month %s. Yearly payers bring the money forward; push the yearly plan first.</div>
<div class="callout red"><b>Money to keep in hand: %s</b>, which is just the upfront development and launch: with 4 in 10 cafes paying yearly, cash never dips below it. Add 3 months of running cost as a reserve. If we build the remaining work ourselves (Rs 0 development) it falls by Rs 1.1 lakh.</div>
</section>''' % (rs(UPFRONT), sens, plan, rs(-S_MONTHLY["low"]), S_MONTHLY["pay"], rs(-S_MAIN["low"])))

# 6. Comparison + rules
cmp_rows = ""
for name, p, sales in CMP:
    fx, fy = FIXED - IMPORT_GST, FIXED_Y1 - IMPORT_GST
    s = simulate(p, fx, sales, yearly_share=0.0)
    cmp_rows += '<tr><td>%s</td><td class="n">%s</td><td class="n">%d</td><td class="n">%d</td><td class="n">%s</td><td class="n">%s</td><td class="n">month %s</td></tr>' % (name, rs(net(p)), need(p, fx), need(p, fy), rs(profit(p, fx, 100)), rs(-s["low"]), s["pay"])
X('''<section class="sec"><div class="kicker">6 &nbsp;/&nbsp; COMPARISON AND RULES</div><h2>Rs 1,000 against the earlier plans</h2>
<table><tr><th>Plan</th><th class="n">Left per cafe</th><th class="n">Break-even cafes</th><th class="n">Year 1 incl. dev</th><th class="n">Profit at 100 cafes</th><th class="n">Cash in hand</th><th class="n">Money back</th></tr>%s</table>
<p class="small">All three compared on monthly billing only, each priced plus GST, so they are like for like. Scenario C with 40%% yearly payers does better, as section 5 shows.</p>
<h3>Rules for a fixed price</h3>
<ol><li><b>One price, written everywhere:</b> "Rs 1,000 a month + GST" on the poster, website, proposal and invoice. "Same price for every cafe."</li>
<li><b>No discounts, ever.</b> If a cafe asks, the only answer is the yearly plan and the 30-day free trial.</li>
<li><b>Yearly first:</b> Rs 12,000 + GST (Rs 14,160) upfront by UPI or bank transfer. Monthly Rs 1,180 by UPI Autopay.</li>
<li><b>30-day free trial</b> with the card live; the trial does the convincing, not the price.</li>
<li><b>Price lock for the first 50 cafes</b> for 2 years. This is a promise, not a discount, and costs us nothing now.</li>
<li><b>Same money rules:</b> 3 months of running cost in the bank (%s), churn under 3%%, at least 9 new cafes a month.</li>
<li><b>Review after 3 months:</b> if fewer than 1 in 8 pitched cafes sign, test the Rs 899 / Rs 1,199 plan on new cafes; never cut existing ones.</li></ol>
<h3>Sources (checked 19 Oct 2026)</h3>
<ul class="srclist small">
<li>Flat-rate pricing trade-offs: zuora.com/glossary/flat-rate-pricing; slidebean.com SaaS startups pricing pages; cashfree.com/blog/saas-billing-models-explained</li>
<li>Indian SaaS pricing: upgrowth.in/saas-pricing-packaging-strategy-india-gtm; inc42.com/buzz/pricing-saas-product</li>
<li>Charm pricing: exchange4media.com, the psychology of pricing (Rs 999 vs Rs 1,000); pricepush.app glossary</li>
<li>GST 18%% on SaaS and Rs 20 lakh services threshold: trykintsugi.com/sales-tax-guides/apac/india; incorpx.io/blog/saas-business-gst-guide-india</li>
<li>Competitors: reelo.io/pricing; codingclave.com/blog/best-restaurant-pos-software-india-2026; loyaltypass.co small-business guide</li>
<li>Company tax 25.17%%: setindiabiz.com/blog/corporate-tax-private-limited-company. Churn: kalungi.com/blog/saas-churn-rate-benchmarks</li></ul>
</section>''' % (cmp_rows, rs(3 * C["fixed"])))

X('</body></html>')
open(OUT_HTML, "w", encoding="utf-8").write("".join(H))
r = subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--print-to-pdf=" + os.path.abspath(OUT_PDF), "file:///" + OUT_HTML.replace("\\", "/")], capture_output=True, text=True, timeout=180)
print("pdf", os.path.exists(OUT_PDF), r.returncode)
for k, v in CASES.items(): print(k, round(v["keep"]), round(net(v["keep"])), need(v["keep"], v["fixed"]), need(v["keep"], v["fixed_y1"]), round(profit(v["keep"], v["fixed"], 100)))
print("1L", cafes_for(1000, FIXED, 100000), "gst cafes", GST_THRESHOLD_CAFES)
print("main", S_MAIN["be"], round(S_MAIN["low"]), S_MAIN["pay"], round(S_MAIN["y1"]), round(S_MAIN["y2"]), round(S_MAIN["y3"]))
print("monthly", S_MONTHLY["be"], round(S_MONTHLY["low"]), S_MONTHLY["pay"])
for n, s in SENS.items(): print("sens", n, s["be"], round(s["low"]), s["pay"])
