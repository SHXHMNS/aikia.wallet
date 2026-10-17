# -*- coding: utf-8 -*-
import os, subprocess
from html import escape as e
import data as D
import budget_model as M

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_HTML = os.path.join(HERE, "AIKIA-WALLET-Budget-Plan.html")
OUT_PDF = os.path.join(HERE, "..", "pdf", "AIKIA-WALLET-Budget-Plan-India.pdf")
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
css = open(os.path.join(HERE, "style.css"), encoding="utf-8").read()
R = lambda x: D.inr(x, True)
RF = lambda x: D.inr(round(x, -2) if abs(x) >= 1000 else x)

LEAN = M.lean()
A3 = M.scope_A(types=M.SCOPE_A_TYPES3)
A2 = M.scope_A(types=M.SCOPE_A_TYPES2)
B = M.scope_B()
A3m, Bm = M.scope_A(rate=M.RATE_MARKET), M.scope_B(rate=M.RATE_MARKET)
sharedA, sharedB = M.shared_totals()
LA, LB = M.loaded(M.RATE_PARTNER), M.loaded(M.RATE_MARKET)
fundA = M.round_up(A3["peak"], 100000); fundB = M.round_up(B["peak"], 500000)

# ------------------------------------------------------------------ charts
def split_chart():
    items = [("Lean start (cafes only)", dict(build=LEAN["opt"], one=LEAN["one"], run=LEAN["monthly"] * 12, comm=0, cont=LEAN["year_cont"] - LEAN["year"])),
             ("Standard: 3 business types, 12 months", A3["total"]), ("Full programme: 29 types, 24 months", B["total"])]
    cats = [("build", "Product build", "#e6007a"), ("one", "One-time legal, security, brand", "#2b5fb3"), ("run", "Running the business", "#0f8b8d"),
            ("comm", "Partner commissions", "#b7791f"), ("cont", "Contingency", "#9b97a8")]
    W, H = 1000, 270
    mx = max(sum(d[k] for k, _, _ in cats) for _, d in items)
    s = ['<svg class="chart" viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg">' % (W, H)]
    s.append('<text x="10" y="20" font-size="13" font-weight="700" fill="#15131c" font-family="Bahnschrift, Segoe UI">Chart B1. Where the money goes</text>')
    y = 44
    for name, d in items:
        s.append('<text x="10" y="%d" font-size="10.5" font-weight="600" fill="#15131c">%s</text>' % (y + 11, e(name)))
        x = 250
        tot = sum(d[k] for k, _, _ in cats)
        for k, lbl, col in cats:
            w = 640.0 * d[k] / mx
            if w > 0.5:
                s.append('<rect x="%.1f" y="%d" width="%.1f" height="22" fill="%s"/>' % (x, y, w, col))
            x += w
        s.append('<text x="%.1f" y="%d" font-size="10.5" font-weight="700" fill="#15131c">%s</text>' % (x + 8, y + 15, e(R(tot))))
        y += 40
    lx = 10
    for k, lbl, col in cats:
        s.append('<rect x="%d" y="%d" width="10" height="10" fill="%s"/><text x="%d" y="%d" font-size="9.4" fill="#3b3846">%s</text>' % (lx, H - 38, col, lx + 15, H - 29, e(lbl)))
        lx += 20 + len(lbl) * 5.6
    s.append('<text x="10" y="%d" font-size="9" fill="#6f6b7a">Totals include 15%% contingency. Founders\' own pay and venue-funded messaging are not included.</text>' % (H - 10))
    s.append('</svg>')
    return "".join(s)

def cash_chart(sc, title, qn):
    W, H = 1000, 300
    rows, cum = sc["rows"], sc["cum"]
    top = max(max(r["cost"] for r in rows), max(r["rev"] for r in rows))
    lo = min(0, min(cum)); hi = top
    x0, x1, y0, y1 = 70, 970, 50, 240
    def Y(v): return y1 - (v - lo) / (hi - lo) * (y1 - y0)
    s = ['<svg class="chart" viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg">' % (W, H)]
    s.append('<text x="10" y="20" font-size="13" font-weight="700" fill="#15131c" font-family="Bahnschrift, Segoe UI">%s</text>' % e(title))
    zero = Y(0)
    s.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="#b9b6c4"/>' % (x0, zero, x1, zero))
    n = len(rows); bw = (x1 - x0) / n
    for i, r in enumerate(rows):
        bx = x0 + i * bw
        s.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#e6007a" opacity=".85"/>' % (bx + bw * .12, Y(r["cost"]), bw * .3, zero - Y(r["cost"])))
        s.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#0f8b8d" opacity=".85"/>' % (bx + bw * .46, Y(r["rev"]), bw * .3, max(zero - Y(r["rev"]), 0.5)))
        s.append('<text x="%.1f" y="%d" font-size="9.6" fill="#3b3846" text-anchor="middle">Q%d</text>' % (bx + bw / 2, y1 + 40, i + 1))
    pts = " ".join("%.1f,%.1f" % (x0 + (i + .5) * bw, Y(c)) for i, c in enumerate(cum))
    s.append('<polyline points="%s" fill="none" stroke="#15131c" stroke-width="2.4"/>' % pts)
    for i, c in enumerate(cum):
        s.append('<circle cx="%.1f" cy="%.1f" r="3.4" fill="#15131c"/>' % (x0 + (i + .5) * bw, Y(c)))
        if i in (n // 2 - 1, n - 1) or n <= 4:
            s.append('<text x="%.1f" y="%.1f" font-size="9.2" font-weight="700" fill="#15131c" text-anchor="middle">%s</text>' % (x0 + (i + .5) * bw, Y(c) + 15, e(R(c))))
    s.append('<rect x="70" y="%d" width="10" height="10" fill="#e6007a"/><text x="85" y="%d" font-size="9.4" fill="#3b3846">Cost in the quarter</text>' % (H - 22, H - 13))
    s.append('<rect x="215" y="%d" width="10" height="10" fill="#0f8b8d"/><text x="230" y="%d" font-size="9.4" fill="#3b3846">Revenue (illustrative)</text>' % (H - 22, H - 13))
    s.append('<line x1="370" y1="%d" x2="392" y2="%d" stroke="#15131c" stroke-width="2.4"/><text x="398" y="%d" font-size="9.4" fill="#3b3846">Cumulative cash (below the line = money you must have put in)</text>' % (H - 17, H - 17, H - 13))
    s.append('</svg>')
    return "".join(s)

# ------------------------------------------------------------------ tables
def quarter_table(sc, n):
    rows = sc["rows"]
    out = ['<table><thead><tr><th style="width:%d%%">Line</th>' % (30 if n == 8 else 34) + "".join('<th class="n">Q%d</th>' % (i + 1) for i in range(n)) + '<th class="n">Total</th></tr></thead><tbody>']
    def line(lbl, key, bold=False):
        vals = [r[key] for r in rows]
        tag = ("<b>%s</b>" if bold else "%s")
        return '<tr><td>%s</td>%s<td class="n">%s</td></tr>' % (tag % e(lbl), "".join('<td class="n">%s</td>' % tag % R(v) for v in vals), tag % R(sum(vals)))
    out.append(line("Product build (partner team)", "build"))
    out.append(line("One-time legal, security, brand, launch", "one"))
    out.append(line("Running costs (cloud, tools, people, sales, upkeep)", "run"))
    out.append(line("Partner commissions on revenue", "comm"))
    out.append(line("Contingency (15%)", "cont"))
    out.append(line("Total cost", "cost", True))
    out.append(line("Revenue (illustrative)", "rev"))
    net = [r["rev"] - r["cost"] for r in rows]
    out.append('<tr><td><b>Net for the quarter</b></td>%s<td class="n"><b>%s</b></td></tr>' % ("".join('<td class="n">%s</td>' % R(v) for v in net), R(sum(net))))
    out.append('<tr><td><b>Cumulative cash</b></td>%s<td class="n"></td></tr>' % "".join('<td class="n"><b>%s</b></td>' % R(c) for c in sc["cum"]))
    out.append('<tr><td>Paying venues at quarter end (illustrative)</td>%s<td class="n"></td></tr>' % "".join('<td class="n">%d</td>' % round(r["venues"]) for r in rows))
    out.append('</tbody></table>')
    return "".join(out)

def shared_table(which):
    idx = 1 if which == "A" else 2
    ld = LA
    out = ['<table><thead><tr><th>Shared platform work package</th><th class="n">Person-months</th><th class="n">Cost at partner rate</th></tr></thead><tbody>']
    for x in M.SHARED:
        pm = x[idx]
        if pm:
            out.append('<tr><td>%s</td><td class="n">%.1f</td><td class="n">%s</td></tr>' % (e(x[0]), pm, R(pm * ld)))
    tot = sum(x[idx] for x in M.SHARED)
    out.append('<tr><td><b>Total shared platform work</b></td><td class="n"><b>%.1f</b></td><td class="n"><b>%s</b></td></tr></tbody></table>' % (tot, R(tot * ld)))
    return "".join(out)

def oneoff_table(extra=False, tcost=0):
    items = list(M.ONE_A) + (list(M.ONE_B_EXTRA) if extra else [])
    out = ['<table><thead><tr><th>One-time item</th><th class="n">Estimate</th></tr></thead><tbody>']
    for t, v in items:
        out.append('<tr><td>%s</td><td class="n">%s</td></tr>' % (e(t), D.inr(v)))
    out.append('<tr><td>Per-business-type launch items (legal review, sales kit, training, pilot support, security review)</td><td class="n">%s</td></tr>' % D.inr(tcost))
    out.append('<tr><td><b>Total before contingency</b></td><td class="n"><b>%s</b></td></tr></tbody></table>' % D.inr(sum(v for _, v in items) + tcost))
    return "".join(out)

def type_rows(names, with_cluster=False):
    out = ['<table><thead><tr><th style="width:34%">Business type</th><th class="n">Build (person-months)</th><th class="n">Build cost</th><th class="n">Legal and security</th><th class="n">Sales kit, training, pilot</th><th class="n">Total</th></tr></thead><tbody>']
    ts = 0
    for n in names:
        c = M.type_cost(n)
        out.append('<tr><td>%s</td><td class="n">%.1f</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n"><b>%s</b></td></tr>' % (e(M.short(n)), c["pm"], R(c["eng"]), R(c["legal"] + c["sec"]), R(c["sales"] + c["train"] + c["pilot"]), R(c["total"])))
        ts += c["total"]
    out.append('<tr><td><b>Subtotal</b></td><td></td><td></td><td></td><td></td><td class="n"><b>%s</b></td></tr></tbody></table>' % R(ts))
    return "".join(out), ts

def all_types_html():
    out, grand, pm = [], 0, 0
    for ci, (cname, why, rows) in enumerate(D.CLUSTERS, 1):
        names = [r[0] for r in rows]
        t, ts = type_rows(names)
        grand += ts
        out.append('<div class="cluster-h"><span class="no">%d</span><h3>%s</h3></div>%s' % (ci, e(cname), t))
    return "".join(out), grand

def archetype_table():
    rows = D.archetype_rows()
    out = ['<table><thead><tr><th>Example customer</th><th class="n">Price / month</th><th class="n">Our cost to serve</th><th class="n">Gross margin</th></tr></thead><tbody>']
    for r in rows:
        out.append('<tr><td>%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%d%%</td></tr>' % (e(r["label"]), D.inr(r["price"]), D.inr(round(r["platform_cost"], -1)), round(r["gm"] * 100)))
    out.append('</tbody></table>')
    return "".join(out)

def sens_table():
    cases = [("Base case (partner rate, plan as stated)", {}),
             ("Development at market rate instead of partner rate", dict(rate=M.RATE_MARKET)),
             ("Revenue one quarter late", dict(delay=1)),
             ("Half as many venues as planned", dict(vmult=.5)),
             ("Market rate and half the venues together", dict(rate=M.RATE_MARKET, vmult=.5))]
    out = ['<table><thead><tr><th>What if</th><th class="n">Standard (3 types, 12 months): money to put in</th><th class="n">Full programme (24 months): money to put in</th></tr></thead><tbody>']
    for lbl, kw in cases:
        a = M.scope_A(**kw); b = M.scope_B(**kw)
        out.append('<tr><td>%s</td><td class="n">%s</td><td class="n">%s</td></tr>' % (e(lbl), R(a["peak"]), R(b["peak"])))
    out.append('</tbody></table>')
    return "".join(out)

def tranche_table(sc, step, labels):
    rows = sc["rows"]; out = ['<table><thead><tr><th>Tranche</th><th class="n">Net cash needed</th><th>Release when</th></tr></thead><tbody>']
    prev_cum = 0.0
    for i in range(0, len(rows), step):
        cum = sc["cum"][min(i + step, len(rows)) - 1]
        out.append('<tr><td><b>%s</b></td><td class="n">%s</td><td>%s</td></tr>' % (labels[i // step][0], R(max(0, prev_cum - cum)), e(labels[i // step][1])))
        prev_cum = min(prev_cum, cum)
    out.append('</tbody></table>')
    return "".join(out)

types_html, types_grand = all_types_html()
tcA = sum(M.type_cost(t)["other"] for t in M.SCOPE_A_TYPES3)
tcB = sum(M.type_cost(t[2])["other"] for t in M.all_type_names())
SECBUDGET = sum(M.type_cost(t[2])["sec"] for t in M.all_type_names())

html = []
A = html.append
A('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>AIKIA.WALLET Budget Plan India</title><style>%s</style></head><body>' % css)

# ---------------------------------------------------------------- cover + headline
A('''<section class="cover"><div class="band"><div class="ring"></div><div class="ring2"></div>
<div class="kicker">AIKIA.WALLET &nbsp;/&nbsp; BUDGET PLAN</div>
<h1>Where the money goes,<br>and how much.</h1>
<p>A full budget for starting with two or three business types, and for the whole programme of 29 business types. Built for a founder with a trusted development partner. October 2026.</p></div>
<div>
<div class="grid3" style="margin-bottom:5mm">
<div class="card pink"><div class="stat">%s<small>LEAN START: cafes only, no new build, founders sell. Year one including 15%% contingency.</small></div></div>
<div class="card pink"><div class="stat">%s<small>STANDARD: three business types, a proper product build with your partner team, 12 months. Money to put in before it carries itself.</small></div></div>
<div class="card pink"><div class="stat">%s<small>FULL PROGRAMME: all 29 business types, 24 months. Money to put in, with founders unpaid.</small></div></div>
</div>
<div class="callout warn"><b>How to read this.</b> Every figure is a planning estimate from published rates and stated assumptions, not a quote. Revenue lines are illustrations to show the cash need, not forecasts. The development rate for your partner company is an assumption you must replace with their real quote. Legal items are for briefing a lawyer and a CA.</div>
<h3>What is inside</h3>
<div class="toc"><div><b>1</b><span>Assumptions and how the model works</span></div><div><b>2</b><span>The eight places money is needed</span></div><div><b>3</b><span>Lean start: cafes only</span></div><div><b>4</b><span>Standard: three business types</span></div><div><b>5</b><span>Full programme: 29 business types</span></div><div><b>6</b><span>Cost to launch each business type</span></div><div><b>7</b><span>Working with your development partner</span></div><div><b>8</b><span>What if things go slower</span></div><div><b>9</b><span>Costs people forget</span></div><div><b>10</b><span>Control, tranches, and what to cut</span></div></div>
</div></section>''' % (R(LEAN["year_cont"]), R(fundA), R(fundB)))

# ---------------------------------------------------------------- assumptions
A('''<section class="sec"><div class="kicker">1 / ASSUMPTIONS</div><h2>How the model works</h2>
<p class="lede">The model adds up four things: building the product, launching it legally and safely, running the company, and selling. It then lays them over 4 quarters (Standard) or 8 quarters (Full) and compares them with an illustrative revenue line.</p>
<table><thead><tr><th>Assumption</th><th>Value used</th><th>Why, and how to change it</th></tr></thead><tbody>
<tr><td>Development partner rate</td><td>%s per engineering person-month (partner), %s (market)</td><td>ASSUMED. Your 20-year partner may quote less or more. Replace with their real rate card.</td></tr>
<tr><td>Uplift for design, testing, project management</td><td>x%.2f on engineering cost</td><td>So a partner person-month costs %s fully loaded (market: %s).</td></tr>
<tr><td>Existing code already built</td><td>Core, cafe preset, Google engine, tiers, geofencing, campaigns</td><td>Only remaining work is costed. Confirm with a code review by your partner before signing.</td></tr>
<tr><td>Contingency</td><td>15%%</td><td>Applied to build, one-time and running costs.</td></tr>
<tr><td>Partner and reseller commission</td><td>15%% of first-year revenue</td><td>Paid only on revenue that arrives.</td></tr>
<tr><td>Dollar rate</td><td>Rs 90 per US$</td><td>Supabase, Vercel, Apple are priced in dollars.</td></tr>
<tr><td>Running-cost lines</td><td>From the Founder Playbook (pilot and growth stage tables)</td><td>Cloud, tools, communications set-up, security, legal and accounts retainer.</td></tr>
<tr><td>Illustrative venues (Standard)</td><td>3, 8, 15, 25 at quarter end; Rs 1,800 a month each</td><td>Shows the cash need; actual numbers come from the pilots.</td></tr>
<tr><td>Illustrative venues (Full)</td><td>3, 10, 25, 60, 120, 200, 300, 400; Rs 1,800 rising to Rs 3,500</td><td>Includes some chains and institutions in later quarters.</td></tr>
<tr><td>Not included</td><td>Founders' own pay; venue-funded messaging; income tax</td><td>See section 9 for founders' pay options.</td></tr>
</tbody></table>
<div class="callout"><b>The one number to get first.</b> Ask your partner company for a written estimate in person-months for the work packages in this plan. That single quote moves the build line more than any other figure here.</div>
</section>''' % (D.inr(M.RATE_PARTNER), D.inr(M.RATE_MARKET), M.LOAD, R(LA), R(LB)))

# ---------------------------------------------------------------- 8 places
A('<section class="sec"><div class="kicker">2 / WHERE MONEY IS NEEDED</div><h2>The eight places money is needed</h2>' + split_chart() + '''
<table><thead><tr><th style="width:4%">#</th><th style="width:22%">Bucket</th><th>What it pays for</th><th style="width:16%">When</th></tr></thead><tbody>
<tr><td>1</td><td><b>Product build</b></td><td>Billing, rules engine, scanner upgrades, integrations, messaging, analytics, security fixes, localisation, and the modules each business type needs. Done by your partner team.</td><td>Months 1 to 6 (Standard); months 1 to 21 (Full)</td></tr>
<tr><td>2</td><td><b>Legal and compliance</b></td><td>Company and GST, agreements, data-processing terms, privacy notice, written view on points versus prepaid rules, trademark, higher-risk sector reviews (clinics, bars, schools, jewellers).</td><td>Before the first paying venue; more per new sector</td></tr>
<tr><td>3</td><td><b>Security</b></td><td>Penetration tests, cyber insurance, log archive, later ISO 27001 or SOC 2 for chains and institutions.</td><td>Before scale; yearly</td></tr>
<tr><td>4</td><td><b>Cloud and tools</b></td><td>Database, hosting, monitoring, support desk, design and project tools, WhatsApp and SMS accounts.</td><td>Every month</td></tr>
<tr><td>5</td><td><b>People</b></td><td>Support and customer success, sales, a product and operations head, part-time finance and compliance, upkeep retainer with the partner team.</td><td>From Q2 (Standard); ramps from Q3 (Full)</td></tr>
<tr><td>6</td><td><b>Sales and marketing</b></td><td>Demo days, printed kits, videos, local events, partner commissions.</td><td>Every month, rising</td></tr>
<tr><td>7</td><td><b>Launch per business type</b></td><td>A preset, sales kit, training video, pilot support and a legal check for each type you enter.</td><td>When you start each type</td></tr>
<tr><td>8</td><td><b>Contingency and reserves</b></td><td>15% on everything, plus the hidden items in section 9.</td><td>Held back</td></tr>
</tbody></table></section>''')

# ---------------------------------------------------------------- lean
A('<section class="sec"><div class="kicker">3 / LEAN START</div><h2>Cafes only, no new build</h2><p class="lede">The least you can spend to run three real cafes on the product that already exists, with you and me doing the work.</p>')
A('<h3>One-time</h3><table><thead><tr><th>Item</th><th class="n">Cost</th></tr></thead><tbody>' + "".join('<tr><td>%s</td><td class="n">%s</td></tr>' % (e(t), D.inr(v)) for t, v in M.LEAN_ONE) + '<tr><td><b>One-time total</b></td><td class="n"><b>%s</b></td></tr></tbody></table>' % D.inr(LEAN["one"]))
A('<h3>Every month</h3><table><thead><tr><th>Item</th><th class="n">Cost</th></tr></thead><tbody>' + "".join('<tr><td>%s</td><td class="n">%s</td></tr>' % (e(t), D.inr(v)) for t, v in M.LEAN_MONTHLY) + '<tr><td><b>Monthly total</b></td><td class="n"><b>%s</b></td></tr></tbody></table>' % D.inr(LEAN["monthly"]))
A('<h3>Optional help</h3><table><tbody>' + "".join('<tr><td>%s</td><td class="n">%s</td></tr>' % (e(t), D.inr(v)) for t, v in M.LEAN_BUILD) + '</tbody></table>')
A('''<div class="grid3">
<div class="card pink"><div class="stat">%s<small>year one, with the optional developer month and 15%% contingency</small></div></div>
<div class="card soft"><div class="stat">%s<small>without the optional developer month: %s</small></div></div>
<div class="card soft"><div class="stat">0<small>new platform features. Uses the cafe preset, tiers, QR poster and Google card already built.</small></div></div></div>''' % (R(LEAN["year_cont"]), R((LEAN["year"] - LEAN["opt"]) * 1.15), "one-time plus 12 months"))
A('''<h3>What this does not buy</h3>
<ul><li>Apple Wallet, paid WhatsApp or SMS, phone-number verification (so fake numbers are possible), billing, POS integration, a penetration test or cyber insurance.</li>
<li>Any support staff. You and I answer the three cafes yourselves.</li>
<li>More than about 3 to 5 venues. Beyond that, support time and the missing features start to cost more than the lean budget saves.</li></ul>
<div class="callout"><b>Use it to answer one question:</b> do repeat visits go up in a cafe after 60 days? If yes, move to Standard. If not, you have spent about %s learning that.</div></section>''' % R(LEAN["year_cont"] * 0.5))

# ---------------------------------------------------------------- standard
A('<section class="sec"><div class="kicker">4 / STANDARD: THREE BUSINESS TYPES</div><h2>Cafes, sweets and bakeries, salons</h2><p class="lede">A proper product for these three types, built with your partner team and run for 12 months. Salons are included because they bring appointments and venue-run packs. Dropping salons saves about %s.</p>' % R(A3["total"]["cost"] - A2["total"]["cost"]))
A('<h3>Product build</h3>')
A(shared_table("A"))
A('<p class="small">Plus the business-type items in the next table. Total build: %s shared + %s for the three types = <b>%s</b>, over about 6 months.</p>' % (R(A3["build_shared"]), R(A3["build_types"]), R(A3["build_total"])))
t, ts = type_rows(M.SCOPE_A_TYPES3)
A('<h3>The three business types</h3>' + t)
A('''<h3>Monthly running costs in this stage</h3>
<table><thead><tr><th>Line</th><th class="n">Per month</th></tr></thead><tbody>
<tr><td>Cloud, tools, communications set-up, security, legal and accounts retainer</td><td class="n">%s</td></tr>
<tr><td>Part-time support and customer success (from Q2)</td><td class="n">%s</td></tr>
<tr><td>Sales and marketing</td><td class="n">%s</td></tr>
<tr><td>Upkeep retainer with the partner team (from Q3, half a person-month)</td><td class="n">%s</td></tr>
</tbody></table>''' % (D.inr(sum(M.INFRA_PILOT.values())), D.inr(45000), D.inr(30000), R(0.5 * LA)))
A('</section>')
A('<section class="sec"><div class="kicker">4 / STANDARD (CONTINUED)</div><h2>One-time costs, then twelve months quarter by quarter</h2>')
A(oneoff_table(False, tcA))
A(quarter_table(A3, 4))
A(cash_chart(A3, "Chart B2. Standard: cost, revenue and cumulative cash by quarter", 4))
A('''<div class="callout"><b>Reading it.</b> You need about <b>%s</b> in hand before the plan carries itself, rounded to <b>%s</b>. Most of it is the build and the team that supports and sells. The venues in this stage pay for only a small part of it. That is normal for a software product: the build is paid once, then sold many times.</div>
</section>''' % (R(A3["peak"]), R(fundA)))

# ---------------------------------------------------------------- full
A('<section class="sec"><div class="kicker">5 / FULL PROGRAMME: 29 BUSINESS TYPES</div><h2>Everything, over 24 months</h2><p class="lede">All business types from the playbook, in waves, with a growing team. The shared platform work is larger because chains, institutions and enterprise buyers need more.</p>')
A('<h3>Shared platform build</h3>' + shared_table("B"))
A('<p class="small">Shared build: <b>%s</b>. Business-type build and launch: <b>%s</b> (next pages). Total build: <b>%s</b>.</p>' % (R(B["build_shared"]), R(B["build_types"]), R(B["build_total"])))
A('</section>')
A('<section class="sec"><div class="kicker">5 / FULL PROGRAMME (CONTINUED)</div><h2>One-time costs, the wave order and the team</h2>' + oneoff_table(True, tcB))
A('''<h3>Wave order</h3><table><thead><tr><th>Wave</th><th>Business types</th><th>Quarters</th><th>Why in this order</th></tr></thead><tbody>
<tr><td><span class="tag t1">Wave 1</span></td><td>Cafes, QSR chains, sweets and bakeries, ice cream and dessert, salons, turfs and courts</td><td>Q1 to Q4</td><td>Fast sales cycle, simple rules, many already have a POS or booking tool.</td></tr>
<tr><td><span class="tag t2">Wave 2</span></td><td>Clothing, sarees, footwear, mobile shops, fine dining, gyms, car wash, laundry, hotels, gaming, coaching, specialty shops</td><td>Q3 to Q6</td><td>Need family accounts, occasions, check-in and booking links.</td></tr>
<tr><td><span class="tag t3">Wave 3</span></td><td>Supermarkets, electronics, kiranas, pharmacies, clinics, jewellery, schools, colleges, malls, channel loyalty, clubs</td><td>Q5 to Q8</td><td>Need integrations, security evidence, sector legal review or minors' data design.</td></tr>
</tbody></table>
<div class="callout warn"><b>Do not start Wave 3 types until Wave 1 pays for itself in support time.</b> Schools, clinics, jewellers and coalitions each need a legal opinion first. The costs here are for that opinion and for building, not for the sale.</div>''')
A('''<h3>Team and run-rate in the last quarter</h3>
<table><thead><tr><th>Line</th><th class="n">Per month, Q5 to Q8</th></tr></thead><tbody>
<tr><td>Cloud, tools, communications, security, legal and accounts (growth stage)</td><td class="n">%s</td></tr>
<tr><td>Support and customer success (about four people)</td><td class="n">%s</td></tr>
<tr><td>Sales team (about three people)</td><td class="n">%s</td></tr>
<tr><td>Product and operations head</td><td class="n">%s</td></tr>
<tr><td>Finance and compliance (part-time)</td><td class="n">%s</td></tr>
<tr><td>Marketing and partner events</td><td class="n">%s</td></tr>
</tbody></table>''' % (D.inr(sum(M.INFRA_GROWTH.values())), D.inr(180000), D.inr(180000), D.inr(120000), D.inr(60000), D.inr(150000)))
A('</section>')
A('<section class="sec"><div class="kicker">5 / FULL PROGRAMME (CONTINUED)</div><h2>Twenty-four months, quarter by quarter</h2>')
A(quarter_table(B, 8))
A(cash_chart(B, "Chart B3. Full programme: cost, revenue and cumulative cash by quarter", 8))
A('''<div class="callout"><b>Reading it.</b> You need about <b>%s</b> of funding at the deepest point, rounded to <b>%s</b>, with founders unpaid and revenue as illustrated. The run rate in the last quarter is about <b>%s a month</b> against revenue of about <b>%s a month</b>. That gap is the reason to stage-gate the spend (section 10).</div>
</section>''' % (R(B["peak"]), R(fundB), R(B["rows"][-1]["cost"] / 3), R(B["rows"][-1]["rev"] / 3)))
#TEAMCUT

# ---------------------------------------------------------------- per type
A('<section class="sec"><div class="kicker">6 / PER BUSINESS TYPE</div><h2>Cost to launch each business type</h2><p class="lede">What it costs to enter each type once the shared platform exists: a preset, any extra build and integration, a legal check, a sales kit, a training video, pilot support and (for chains and institutions) a security review. Build cost is at the partner rate.</p>')
A(types_html)
A('<p class="small"><b>All 29 types: %s</b> (before contingency). Of this, legal and security reviews are about %s; the rest is build and launch work.</p></section>' % (R(types_grand), R(sum(M.type_cost(t[2])["legal"] + M.type_cost(t[2])["sec"] for t in M.all_type_names()))))

# ---------------------------------------------------------------- cost to serve
A('<section class="sec"><div class="kicker">6 / PER CUSTOMER</div><h2>What each kind of customer costs us every month</h2><p class="lede">Separate from the launch cost above: the ongoing cost of serving one customer, against a suggested price. From the Founder Playbook model (messaging, hosting share, support hours).</p>')
A(archetype_table())
A('''<p class="small">Marketing messages are passed on at cost plus 30%. The platform cost excludes the venue's own marketing messages and any integration support, which is billed as setup.</p>
<h3>Rule of thumb for pricing</h3>
<ul><li>A venue must pay at least 3x its monthly cost to serve, or support time will erase the margin.</li>
<li>Small venues only work if onboarding is self-serve. Spending a person-day on a Rs 1,499 plan loses money for the first year.</li>
<li>Chains and institutions should pay setup fees that cover their integration and security work.</li></ul></section>''')

# ---------------------------------------------------------------- partner
A('''<section class="sec"><div class="kicker">7 / DEVELOPMENT PARTNER</div><h2>Working with your development company</h2>
<p class="lede">A 20-year relationship helps, but the product, the code and the customer data are the company's most valuable assets, so the paper must be as clear as with a stranger.</p>
<h3>Suggested payment structure (fixed-scope packages)</h3>
<table><thead><tr><th>Milestone</th><th class="n">Share of package</th><th>Condition</th></tr></thead><tbody>
<tr><td>Start</td><td class="n">15%</td><td>Signed scope, person-month estimate, schedule, IP assignment, NDA</td></tr>
<tr><td>Design and architecture sign-off</td><td class="n">20%</td><td>Written design for the package reviewed by you or an independent reviewer</td></tr>
<tr><td>Working beta in a pilot venue</td><td class="n">30%</td><td>Demo on a real phone and counter, with test results</td></tr>
<tr><td>Production acceptance</td><td class="n">25%</td><td>Acceptance tests pass; security fixes closed; documentation delivered</td></tr>
<tr><td>Warranty holdback</td><td class="n">10%</td><td>Paid 60 days after go-live if no serious defects</td></tr>
</tbody></table>
<p class="small">Alternative: time-and-materials with a monthly cap, weekly demos and a written burn report. Use this for the exploratory work (integrations) and fixed-scope for the well-defined work (billing, rules, scanner).</p>
<div class="grid2">
<div class="card"><h4>Put in the contract</h4><ul><li>All code and designs assigned to the company; code lives in the company's own GitHub organisation from day one</li>
<li>No partner-owned libraries without an open licence; list of third-party components</li><li>Security duties: no secrets in code, access by named people, breach notice within hours</li>
<li>Data ownership: member data belongs to the venue; partner is a sub-processor with a data-processing agreement</li><li>Support terms after go-live: response times, upkeep retainer, warranty</li>
<li>Non-solicit and confidentiality; key-person cover so one engineer leaving does not stop delivery</li></ul></div>
<div class="card"><h4>Controls on your side</h4><ul><li>One internal owner who accepts or rejects each package</li><li>Weekly demo; monthly budget review against this plan</li>
<li>Independent code review once per quarter (a few person-days, about Rs 40,000 to 80,000)</li><li>Change requests priced in person-months before work starts</li>
<li>Keep the build and deployment accounts in the company's name, not the partner's</li><li>Do not pre-pay beyond the milestone table</li></ul></div></div>
<div class="callout warn"><b>If the partner offers equity or revenue share instead of cash:</b> treat it as a separate legal decision with its own lawyer. It lowers early cash but gives a third party a claim on the company, and it changes who decides the roadmap.</div>
</section>''')

# ---------------------------------------------------------------- sensitivity
A('<section class="sec"><div class="kicker">8 / WHAT IF IT GOES SLOWER</div><h2>Sensitivity: how the money needed changes</h2>' + sens_table() + '''
<p class="small">"Money to put in" is the deepest point of cumulative cash. It rises when development costs more or revenue arrives later.</p>
<h3>Levers that matter most</h3>
<table><thead><tr><th>Lever</th><th>Effect</th></tr></thead><tbody>
<tr><td>Development rate</td><td>Standard build is %s at partner rate and %s at market rate, a difference of %s. For the full programme the difference is %s.</td></tr>
<tr><td>Build only what a paying customer asked for</td><td>Wave 3 and the enterprise modules can wait. Cutting the full programme to Waves 1 and 2 lowers the build line by roughly a third.</td></tr>
<tr><td>Self-serve onboarding</td><td>Cuts support cost and lets the same team serve many more small venues.</td></tr>
<tr><td>Price</td><td>Raising the average from Rs 1,800 to Rs 2,500 changes revenue by 39%% for the same venues.</td></tr>
<tr><td>Partner-led sales</td><td>Commissions cost 15%% of revenue but replace a sales hire you would pay for regardless of results.</td></tr>
<tr><td>Founders' pay</td><td>Not included. Two founders at Rs 60,000 each add Rs 14.4 lakh a year.</td></tr>
</tbody></table></section>''' % (R(A3["build_total"]), R(A3m["build_total"]), R(A3m["build_total"] - A3["build_total"]), R(Bm["build_total"] - B["build_total"])))

# ---------------------------------------------------------------- missed
A('''<section class="sec"><div class="kicker">9 / COSTS PEOPLE FORGET</div><h2>What you and I might miss</h2>
<table><thead><tr><th style="width:25%">Item</th><th style="width:20%">Rough size</th><th>Why it appears</th></tr></thead><tbody>
<tr><td><b>Founders' own pay</b></td><td>Rs 1.2 lakh a month for two at Rs 60,000</td><td>Not in the plan. Without it, founders fund the plan with their time.</td></tr>
<tr><td><b>Scope growth on fixed-price work</b></td><td>10 to 20% of build</td><td>Requirements change once real cafes use it. Held partly in the contingency.</td></tr>
<tr><td><b>Statutory audit, ROC filings, tax returns</b></td><td>Rs 40,000 to 80,000 a year (estimate)</td><td>A private limited company must file every year.</td></tr>
<tr><td><b>GST cash timing</b></td><td>18% collected, paid later</td><td>Output GST is a pass-through, but late payment attracts interest. Keep it in a separate account.</td></tr>
<tr><td><b>Employer costs on staff</b></td><td>About 13 to 15% on pay for PF, ESI, gratuity where applicable (confirm with CA)</td><td>Support, sales and finance monthly figures in this plan are treated as loaded; check.</td></tr>
<tr><td><b>Recruitment and equipment</b></td><td>Included in Full programme</td><td>About 8% of annual pay per hire; laptops and phones.</td></tr>
<tr><td><b>Payment gateway fees on our own subscriptions</b></td><td>About 2% of revenue (estimate)</td><td>Small, but it adds up at scale. UPI autopay is often cheaper than cards.</td></tr>
<tr><td><b>Free months and pilot discounts</b></td><td>2 months free x pilot venues</td><td>Pilot support is costed; the foregone revenue is not.</td></tr>
<tr><td><b>Churn and bad debt</b></td><td>3 to 5% of revenue (assumption)</td><td>Small venues close or stop paying.</td></tr>
<tr><td><b>Dollar and platform price changes</b></td><td>3 to 8% a year</td><td>Cloud, Apple and tool prices are in dollars; Meta changes WhatsApp rates up to four times a year.</td></tr>
<tr><td><b>Data-breach reserve</b></td><td>Rs 5 to 10 lakh set aside</td><td>Insurance has a deductible; legal, forensics and notices come first.</td></tr>
<tr><td><b>Legal disputes reserve</b></td><td>Rs 2 to 5 lakh</td><td>Points disputes, venue exits, partner disagreements.</td></tr>
<tr><td><b>Office or co-working</b></td><td>Rs 0 to 1.5 lakh a month</td><td>Not in the plan; remote work assumed.</td></tr>
<tr><td><b>Travel and installation visits</b></td><td>Rs 30,000 to 60,000 a month at scale</td><td>Installing and training at venues in person.</td></tr>
<tr><td><b>Translation and local-language support</b></td><td>Part of localisation build; plus content refresh</td><td>Regional language help videos and cheat sheets per sector.</td></tr>
<tr><td><b>Source-code escrow and documentation</b></td><td>A few person-days per package</td><td>So the product can survive a change of partner.</td></tr>
<tr><td><b>Insurance renewals</b></td><td>Yearly</td><td>Cyber and professional indemnity renew every year.</td></tr>
<tr><td><b>Wallet-platform risk</b></td><td>Cost of rebuilding an engine</td><td>Google, Apple or PassKit can change terms. Keep the adapter design.</td></tr>
<tr><td><b>Key-person risk</b></td><td>One senior engineer at the partner</td><td>Negotiate a named backup and written documentation.</td></tr>
<tr><td><b>Founder time</b></td><td>The largest hidden cost</td><td>Sales, pilots, support and partner management take full days.</td></tr>
</tbody></table></section>''')

# ---------------------------------------------------------------- control
A('<section class="sec"><div class="kicker">10 / CONTROL</div><h2>Release the money in tranches</h2><p class="lede">Do not commit the whole amount at once. Tie each tranche to a result that proves the next one is safe.</p>')
A('<h3>Standard (3 types, 12 months)</h3>' + tranche_table(A3, 2, [("Tranche 1 (Q1 to Q2)", "Legal base done; build packages accepted; first 3 pilot venues live"), ("Tranche 2 (Q3 to Q4)", "Repeat visits up in at least 2 of 3 pilot types; 10+ venues willing to pay; support under about 1 hour per venue a month")]))
A('<h3>Full programme (24 months)</h3>' + tranche_table(B, 2, [("Tranche 1 (Q1 to Q2)", "Same as Standard Tranche 1"), ("Tranche 2 (Q3 to Q4)", "25+ paying venues; billing and messaging live; integrations wave 1 working"), ("Tranche 3 (Q5 to Q6)", "100+ paying venues; support time stable; first chain or institution signed; penetration test clean"), ("Tranche 4 (Q7 to Q8)", "Partner channel producing leads; unit economics proven; legal opinions in hand for each Wave 3 type")]))
A('''<h3>If money is short: what to cut first</h3>
<table><thead><tr><th>Order</th><th>Cut or delay</th><th>Saves (approx.)</th></tr></thead><tbody>
<tr><td>1</td><td>Wave 3 business types and enterprise modules</td><td>About one third of the full build</td></tr>
<tr><td>2</td><td>Education module and coalition / channel products</td><td>%s of build, plus legal reviews</td></tr>
<tr><td>3</td><td>ISO 27001 or SOC 2 audit</td><td>Rs 4 lakh</td></tr>
<tr><td>4</td><td>Sales hires: use partner commissions instead</td><td>Rs 1.8 lakh a month at full size</td></tr>
<tr><td>5</td><td>Apple Wallet (use web card for iPhone)</td><td>Rs 8,700 a year plus about %s</td></tr>
<tr><td>6</td><td>Paid WhatsApp and SMS (use free links)</td><td>The messaging build and registrations</td></tr>
</tbody></table>
<h3>Never cut</h3>
<ul><li>Consent, privacy notice and venue data-processing agreement</li><li>A penetration test before the first large customer</li><li>The ledger, backups and a tested restore</li><li>The written view on points versus prepaid rules before any venue-run pack</li><li>IP assignment and company-owned code and accounts</li></ul>
<h3>Decisions for the founders</h3>
<ol><li>Start with Lean, Standard, or both in sequence (recommended: Lean for 60 days, then Standard if the repeat-visit test passes)</li><li>The partner company's real rate and the written estimate for the packages</li><li>Which three business types, and the three pilot venues</li><li>Where the %s comes from (savings, investors, agency profits, partner equity) and who signs the budget each month</li><li>Whether founders take pay, and from when</li></ol></section>''' % (R((2.5 + 1.5) * LA + 250000), R(1.0 * LA), R(fundA)))

A('<section class="sec"><div class="kicker">NOTES</div><h2>Where the numbers come from</h2><p class="small">Unit costs and prices (WhatsApp rates, SMS, DLT, Apple fee, Supabase and Vercel, salaries, incorporation) come from the sources listed in the Founder Playbook, which are third-party pages and should be re-checked before spending. The partner rate, uplift, commission, venue counts, prices and the reserves in section 9 are our assumptions. The model is in <code>output/playbook-src/budget_model.py</code>; change a value there and rebuild with <code>python budget_build.py</code> to refresh every table and chart.</p><p class="small">Standard and Full budgets include a 15% contingency. Revenue is illustrative. This document is a planning tool, not financial or legal advice; confirm tax and legal points with a chartered accountant and a lawyer.</p></section></body></html>')

open(OUT_HTML, "w", encoding="utf-8").write("".join(html))
os.makedirs(os.path.dirname(OUT_PDF), exist_ok=True)
r = subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--print-to-pdf=" + os.path.abspath(OUT_PDF), "file:///" + OUT_HTML.replace("\\", "/")], capture_output=True, text=True, timeout=180)
print("rc", r.returncode, os.path.getsize(OUT_PDF))
print("lean", R(LEAN["year_cont"]), "A", R(A3["peak"]), R(fundA), "B", R(B["peak"]), R(fundB))
