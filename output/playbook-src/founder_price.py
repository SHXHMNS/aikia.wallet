# -*- coding: utf-8 -*-
"""AIKIA.WALLET: the price at which the two founders take at least Rs 1 lakh a month from year 2,
while staying affordable for cafes. Fixed price + GST, GST-registered, own Google + Apple wallet engines.
Same cost base as the earlier plans. Research checked 19 Oct 2026. S = published source, E = our estimate."""
import os, math, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_HTML = os.path.join(HERE, "AIKIA-WALLET-Founder-Price.html")
OUT_PDF = os.path.join(HERE, "..", "pdf", "AIKIA-WALLET-Price-For-Founder-Income.pdf")
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

# ---------------- cost base (registered for GST: import GST claimed back) ----------------
PLATFORM = 12724 - 1560; OPS = 5000
FIXED = PLATFORM + OPS                     # Rs 16,164 a month
UPFRONT = 110000 + 97000                   # development (partner rate, E) + launch
SERVE = 100; ACQUIRE = 1000; PER_CAFE = SERVE + ACQUIRE / 12
FEE = 0.01; CHURN = 0.03
def step(c): return (0 if c <= 150 else 21000) + (0 if c <= 300 else 15000)
def net(p): return p * (1 - FEE) - PER_CAFE

TARGETS = {"combined": 100000, "each": 200000}   # founders' pay a month, paid as salary (a company cost)
def need(p, target):
    n = 1
    while n * net(p) - FIXED - step(n) - target < 0: n += 1
    return n

PRICES = [999, 1000, 1299, 1500, 1799, 2000, 2499]
REC = 1500

def simulate(price, new, salary_from=13, salary=100000, yearly_share=0.4, months=36):
    monthly = 0.0; cohorts = []; cash = -UPFRONT; rows = []; low = cash
    for m in range(1, months + 1):
        monthly = monthly * (1 - CHURN) + new * (1 - yearly_share)
        cohorts.append([m, new * yearly_share])
        income = monthly * price * (1 - FEE)
        for c in cohorts:
            if (m - c[0]) % 12 == 0:
                if m != c[0]: c[1] *= (1 - CHURN) ** 12
                income += c[1] * price * 12 * (1 - FEE)
        active = monthly + sum(c[1] for c in cohorts)
        pay = salary if m >= salary_from else 0
        cost = FIXED + active * SERVE + new * ACQUIRE + step(active) + pay
        earned = active * price * (1 - FEE)
        cash += income - cost
        low = min(low, cash)
        rows.append(dict(m=m, cafes=active, income=income, earned=earned, cost=cost, pay=pay, cash=cash, surplus=earned - cost))
    return dict(rows=rows, low=low)

S = {n: simulate(REC, n) for n in (6, 8, 9, 12)}
S_EACH = {n: simulate(2000, n, salary=200000) for n in (9, 12, 15)}

H = []; X = H.append
X('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>AIKIA.WALLET founder price</title><style>%s</style></head><body>' % css)

n1 = need(REC, TARGETS["combined"]); n2 = need(REC, TARGETS["each"])
m12 = S[9]["rows"][11]["cafes"]
X('''<section class="cover"><div class="band"><div class="ring"></div><div class="ring2"></div>
<div class="kicker">AIKIA.WALLET &nbsp;/&nbsp; FOUNDER INCOME PRICE</div>
<h1 style="max-width:70%%">Rs 1,500 + GST.<br>Rs 1 lakh a month<br>to the founders.</h1>
<p style="max-width:62%%">The fixed price at which the two founders take at least Rs 1 lakh a month from year 2, every cost is covered, and a cafe owner still finds it easy to say yes. Own Google and Apple wallet, no PassKit. October 2026.</p></div>
<div><div class="grid3" style="margin-bottom:5mm">
<div class="card pink"><div class="stat">Rs 1,500<small>A MONTH + GST (Rs 18,000 + GST a year). Rs 50 a day. One price for every cafe, every feature.</small></div></div>
<div class="card pink"><div class="stat">%d cafes<small>PAY EVERY COST AND Rs 1 LAKH A MONTH to the founders (Rs 50,000 each). Selling 9 a month, we reach about %d by month 12.</small></div></div>
<div class="card pink"><div class="stat">8 visits<small>A MONTH PAY FOR IT. At a Rs 200 bill, 8 extra repeat visits a month (one every 4 days) cover the cafe's Rs 1,500.</small></div></div>
</div>
<div class="callout ok"><b>Finance desk verdict.</b> Rs 1,500 + GST is the price. It is about half of Reelo's Rs 3,250, under 1%% of a small cafe's monthly sales, and gives the two founders Rs 1 lakh a month from month 13 at about %d cafes. For Rs 1 lakh EACH, the price is Rs 2,000 + GST at about %d cafes, or Rs 1,500 at %d cafes.</div>
<div class="callout warn"><b>How to read this.</b> Planning numbers, not quotes. Founders' pay is treated as salary, a company cost, so it is paid before profit. Year 1 founders take nothing and the business repays development and launch. Cafe revenue and loyalty effects come from industry blogs and vendor data, not audited studies.</div>
</div></section>''' % (n1, round(m12), n1, need(2000, TARGETS["each"]), n2))

# 1. What a cafe can afford
X('''<section class="sec"><div class="kicker">1 &nbsp;/&nbsp; WHAT A CAFE CAN AFFORD</div><h2>Not costly, not cheap: the cafe owner's view</h2>
<table><tr><th>Fact</th><th>Figure</th><th class="c">Src</th></tr>
<tr><td>Small neighbourhood cafe, monthly sales</td><td>about Rs 2 to 5 lakh (smaller cafes lower; busy specialty cafes higher)</td><td class="c">S</td></tr>
<tr><td>Tier-2 cafe break-even sales</td><td>about Rs 80,000 to 2 lakh (secondary location), Rs 1.5 to 3.5 lakh (prime)</td><td class="c">S</td></tr>
<tr><td>Net profit margin, small cafe</td><td>about 5 to 12%%</td><td class="c">S</td></tr>
<tr><td>Marketing spend, restaurants</td><td>about 3 to 6%% of sales (5 to 10%% when new)</td><td class="c">S</td></tr>
<tr><td>Average cappuccino price in India</td><td>about Rs 214; tier-2 bills often Rs 100 to 200</td><td class="c">S</td></tr>
<tr><td>Loyalty effect (vendor data)</td><td>chance a guest returns rises from about 7%% to about 30%% once enrolled</td><td class="c">S</td></tr></table>
<table><tr><th>Price + GST a month</th><th class="n">Per day</th><th class="n">Share of Rs 3 lakh sales</th><th class="n">Share of a 4%% marketing budget</th><th class="n">Extra Rs 200 visits to pay for it</th><th class="n">vs Reelo Rs 3,250</th></tr>%s</table>
<div class="callout ok"><b>Where Rs 1,500 lands.</b> Rs 50 a day, half of one percent of a Rs 3 lakh cafe's sales, about one-eighth of a normal marketing budget, and paid back by 8 extra visits a month. That is the line between "cheap" and "costly" for a cafe owner: it is a real business tool, priced like one cup of coffee a day.</div>
</section>''' % "".join('<tr%s><td>Rs %s</td><td class="n">Rs %d</td><td class="n">%.2f%%</td><td class="n">%d%%</td><td class="n">%d</td><td class="n">%d%% less</td></tr>' % (
    ' style="background:#fff0f7"' if p == REC else "", "{:,}".format(p), round(p / 30), p / 300000 * 100, round(p / 12000 * 100), math.ceil(p / 200), round((1 - p / 3250) * 100)) for p in PRICES))

# 2. Price ladder for founder income
lad = "".join('<tr%s><td>Rs %s</td><td class="n">Rs %s</td><td class="n">%s</td><td class="n">%d</td><td class="n">%d</td><td class="n">%d</td></tr>' % (
    ' style="background:#fff0f7"' if p == REC else "", "{:,}".format(p), "{:,}".format(p * 12), rs(net(p)), need(p, 0), need(p, TARGETS["combined"]), need(p, TARGETS["each"])) for p in PRICES)
X('''<section class="sec"><div class="kicker">2 &nbsp;/&nbsp; THE PRICE LADDER</div><h2>Cafes needed for the founders' Rs 1 lakh</h2>
<p class="lede">Fixed costs %s a month (GST-registered, development already repaid in year 1). Each cafe costs about %s a month to serve and win, plus a 1%% collection fee. Founders' pay is a salary the company pays.</p>
<table><tr><th>Price + GST a month</th><th class="n">A year + GST</th><th class="n">Left per cafe</th><th class="n">Just break even</th><th class="n">Rs 1 lakh total (Rs 50k each)</th><th class="n">Rs 1 lakh each (Rs 2 lakh)</th></tr>%s</table>
<h3>Reading the ladder</h3>
<ul><li><b>At Rs 1,000</b> the founders' Rs 1 lakh needs %d cafes: more than a new brand reaches in 12 months at our selling speed.</li>
<li><b>At Rs 1,500</b> it needs %d cafes, which 9 new cafes a month reaches by about month 11 or 12.</li>
<li><b>At Rs 2,000</b> it needs %d cafes, but the price starts to feel "costly" against a Rs 2 to 5 lakh cafe, and sign-ups slow.</li>
<li>Above 150 cafes the costs step up (database upgrade and a part-time support person, about Rs 21,000 a month), which is why the Rs 1 lakh-each column jumps.</li></ul>
</section>''' % (rs(FIXED), rs(PER_CAFE), lad, need(1000, TARGETS["combined"]), n1, need(2000, TARGETS["combined"])))

# 3. Cash plan with salaries from month 13
sens = "".join('<tr><td>%d a month</td><td class="n">%d</td><td class="n">%d</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td></tr>' % (
    n, round(s["rows"][11]["cafes"]), round(s["rows"][23]["cafes"]), rs(s["rows"][12]["surplus"]), rs(-s["low"]), rs(s["rows"][35]["cash"])) for n, s in S.items())
plan = "".join('<tr><td>Month %d</td><td class="n">%d</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td></tr>' % (
    r["m"], round(r["cafes"]), rs(r["income"]), rs(r["pay"]), rs(r["cost"]), rs(r["cash"])) for r in S[9]["rows"] if r["m"] in (1, 3, 6, 9, 12, 13, 15, 18, 24, 30, 36))
X('''<section class="sec"><div class="kicker">3 &nbsp;/&nbsp; CASH PLAN</div><h2>Rs 1,500: founders paid Rs 1 lakh a month from month 13</h2>
<p class="lede">Development and launch paid upfront (%s). Founders take nothing in year 1, then Rs 1 lakh a month in total from month 13. 4 in 10 cafes pay the year upfront; 3%% of cafes leave each month.</p>
<table><tr><th>New cafes a month</th><th class="n">Cafes at month 12</th><th class="n">Cafes at month 24</th><th class="n">Surplus in month 13 after founder pay</th><th class="n">Cash to keep in hand</th><th class="n">Bank at month 36</th></tr>%s</table>
<h3>The plan: 9 new cafes a month</h3>
<table><tr><th>Month</th><th class="n">Active cafes</th><th class="n">Money in</th><th class="n">Founder pay</th><th class="n">All costs</th><th class="n">Cash position</th></tr>%s</table>
<div class="callout ok"><b>What the founders get.</b> From month 13: Rs 50,000 each, every month, after every cost, with the company still adding cash. At 8 new cafes a month it still just clears. At 6 a month it does not: start founder pay at Rs 70,000 in total and lift it to Rs 1 lakh once the business passes %d cafes.</div>
</section>''' % (rs(UPFRONT), sens, plan, n1))

# 4. Rs 1 lakh each
se = "".join('<tr><td>%d a month</td><td class="n">%d</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td></tr>' % (
    n, round(s["rows"][11]["cafes"]), rs(s["rows"][12]["surplus"]), rs(-s["low"]), rs(s["rows"][35]["cash"])) for n, s in S_EACH.items())
X('''<section class="sec"><div class="kicker">4 &nbsp;/&nbsp; IF IT MEANS Rs 1 LAKH EACH</div><h2>Rs 2 lakh a month to the two founders</h2>
<table><tr><th>Option</th><th class="n">Cafes needed</th><th>What it takes</th></tr>
<tr><td>Rs 1,500 + GST</td><td class="n">%d</td><td>About 17 to 18 new cafes a month in year 1; needs a sales helper or partner channel</td></tr>
<tr><td>Rs 2,000 + GST</td><td class="n">%d</td><td>About 12 new cafes a month; price is still 38%% below Reelo but feels premium to small cafes</td></tr>
<tr><td>Rs 1,500 now, Rs 2,000 for new cafes from month 13</td><td class="n">about 140 to 160</td><td>Founding cafes keep Rs 1,500; reach Rs 2 lakh in year 2 as the mix shifts</td></tr></table>
<h3>Rs 2,000 + GST with Rs 2 lakh founder pay from month 13</h3>
<table><tr><th>New cafes a month</th><th class="n">Cafes at month 12</th><th class="n">Surplus in month 13 after founder pay</th><th class="n">Cash to keep in hand</th><th class="n">Bank at month 36</th></tr>%s</table>
<div class="callout warn"><b>Personal tax.</b> Paid as salary, Rs 6 to 12 lakh a year per founder is likely to fall within the rebate under the new personal tax regime; confirm with the CA. Salary is a company cost, so it also lowers company tax.</div>
</section>''' % (n2, need(2000, TARGETS["each"]), se))

# 5. Recommendation
X('''<section class="sec"><div class="kicker">5 &nbsp;/&nbsp; RECOMMENDATION</div><h2>The price and how to hold it</h2>
<table><tr><th>Item</th><th>Decision</th></tr>
<tr><td><b>Price</b></td><td>Rs 1,500 a month + GST (cafe pays Rs 1,770); Rs 18,000 a year + GST (Rs 21,240). One price, every feature, every cafe.</td></tr>
<tr><td><b>No negotiation</b></td><td>The same price is printed on the poster, website, proposal and invoice. The only "offer" is the 30-day free trial.</td></tr>
<tr><td><b>Founding promise</b></td><td>The first 50 cafes keep Rs 1,500 for 2 years, even if the price rises for new cafes.</td></tr>
<tr><td><b>Founder pay</b></td><td>Nothing in year 1. From month 13: Rs 1 lakh a month in total once active cafes pass %d; Rs 70,000 until then.</td></tr>
<tr><td><b>Sales target</b></td><td>9 new cafes a month (about 2 a week); 1 in 6 cafes pitched.</td></tr>
<tr><td><b>Money rules</b></td><td>Keep %s in hand before launch plus 3 months of costs as reserve; churn under 3%%; review the price after 6 months with real numbers.</td></tr></table>
<h3>The pitch in one line</h3>
<p class="lede">"Rs 50 a day, less than a coffee. Your card sits in every customer's phone, brings them back, and pays for itself with 8 extra visits a month."</p>
<h3>Why not Rs 1,000 or Rs 2,000</h3>
<ul><li><b>Rs 1,000</b> is easy to sell but needs %d cafes to pay the founders Rs 1 lakh. At 9 a month that is not reached in year 2's first months, so the founders would wait.</li>
<li><b>Rs 2,000</b> reaches the founders' goal fastest but sits at the edge of what a Rs 2 lakh cafe will spend on one tool, so sign-ups slow and churn rises.</li>
<li><b>Rs 1,500</b> keeps the founders' goal reachable on a normal selling pace and stays at about half the market leader's price.</li></ul>
<h3>Sources (checked 19 Oct 2026)</h3>
<ul class="srclist small">
<li>Cafe revenue and margins: restaurantindia.in cafe business in India; blog.petpooja.com cafe business model revenue and profit; thecoffeecana.com tier 2 and 3 cafe profitability; trufflenation.com how to start a cafe in India</li>
<li>Marketing budgets: lightspeedhq.com restaurant marketing budget; get.chownow.com restaurant marketing budget; restaurantindia.in marketing budget survey</li>
<li>Loyalty return rates: pos.toasttab.com/blog/data/restaurant-loyalty-program-return-rate (vendor data)</li>
<li>Cappuccino price: World Coffee Portal, Project Cafe India 2025</li>
<li>Competitor price: reelo.io/pricing. Costs: AIKIA.WALLET Launch Costing and pricing scenarios, October 2026</li></ul>
</section>''' % (n1, rs(UPFRONT), need(1000, TARGETS["combined"])))

X('</body></html>')
open(OUT_HTML, "w", encoding="utf-8").write("".join(H))
r = subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--print-to-pdf=" + os.path.abspath(OUT_PDF), "file:///" + OUT_HTML.replace("\\", "/")], capture_output=True, text=True, timeout=180)
print("pdf", os.path.exists(OUT_PDF), r.returncode)
print("ladder", [(p, need(p, 0), need(p, 100000), need(p, 200000)) for p in PRICES])
for n, s in S.items(): print("1500", n, round(s["rows"][11]["cafes"]), round(s["rows"][12]["surplus"]), round(s["low"]), round(s["rows"][35]["cash"]))
for n, s in S_EACH.items(): print("2000each", n, round(s["rows"][11]["cafes"]), round(s["rows"][12]["surplus"]), round(s["low"]), round(s["rows"][35]["cash"]))
