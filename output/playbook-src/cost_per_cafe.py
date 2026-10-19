# -*- coding: utf-8 -*-
"""AIKIA.WALLET: what it costs US to serve ONE cafe, per month and per year. Cost price only, no selling price.
Own Google + Apple wallet engines (no PassKit). Same figures as the Launch Costing, checked 19 Oct 2026.
S = published source, E = our estimate."""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_HTML = os.path.join(HERE, "AIKIA-WALLET-Cost-Per-Cafe.html")
OUT_PDF = os.path.join(HERE, "..", "pdf", "AIKIA-WALLET-Cost-Per-Cafe.pdf")
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
css = open(os.path.join(HERE, "style.css"), encoding="utf-8").read()
FX = 96.0

def rs(x):
    n = str(int(round(abs(x))))
    if len(n) > 3:
        head, tail = n[:-3], n[-3:]; parts = []
        while len(head) > 2: parts.insert(0, head[-2:]); head = head[:-2]
        if head: parts.insert(0, head)
        n = ",".join(parts) + "," + tail
    return ("-Rs " if x < 0 else "Rs ") + n

# Shared running costs: needed to serve any cafe at all (Rs a month)
SHARED = [
    ("Hosting", "Vercel Pro, 1 seat: app, join page, staff scanner, owner dashboard, guest pages, scheduled jobs", "US$20 a month", "S", 20 * FX),
    ("Database and ledger", "Supabase Pro: members, ledger, credit, gifts, logins, daily backups kept 7 days", "US$25 a month", "S", 25 * FX),
    ("Apple Wallet", "Apple Developer Program: our pass certificate and iPhone card updates", "US$99 a year", "S", 99 / 12 * FX),
    ("Weather data", "Open-Meteo commercial licence for weather-mood messages", "US$29 a month (confirm)", "S", 29 * FX),
    ("Code security", "GitHub Team, 2 users: protected code and reviews", "about US$4 a user a month", "S", 8 * FX),
    ("GST on imported software", "18% on the five services above (claimable once GST-registered)", "18%", "S", 90.25 * FX * 0.18),
    ("Accounts and GST filing", "Chartered accountant retainer", "monthly", "E", 2500),
    ("Phone and internet", "Business phone and data for support and sales", "monthly", "E", 1000),
    ("Travel", "Visits for onboarding, support and sales", "monthly", "E", 3000),
    ("Admin", "Printing, stationery, bank charges, small tools", "monthly", "E", 1000),
]
FREE = [
    ("Google Wallet API and console", "Android cards, updates, messages, nearby alerts"),
    ("Apple push notifications", "Tells iPhones to refresh the card"),
    ("Email (Resend free tier)", "Login links and alerts, up to 3,000 a month"),
    ("Automation (GitHub Actions)", "Tests, nightly backup, health checks"),
    ("Off-site backup (Cloudflare R2)", "Nightly encrypted database copy, up to 10 GB"),
    ("DNS and protection (Cloudflare)", "Domain records, DDoS shield"),
    ("Password manager (Bitwarden, 2 users)", "Keys and passwords vault"),
    ("Domain", "wallet.aikia.world sub-domain"),
]
# One-time costs to start the service (Rs)
ONE = [
    ("Development left before launch", "Apple engine, own Google engine switch, automation, security, testing (33 days at a partner rate; Rs 0 if built in-house)", "E", 110000),
    ("Lawyer", "Cafe agreement, privacy notice (DPDP Act), programme terms", "E", 60000),
    ("GST registration", "CA set-up fee", "E", 5000),
    ("Trademark", "aikia.wallet, 1 class, e-filing government fee", "S", 4500),
    ("Test iPhone", "Second-hand, if no one in the team has one", "E", 25000),
]
# Direct costs for each cafe
DIRECT_ONCE = [
    ("QR standee and counter poster", "Printed and laminated", "E", 400),
    ("Onboarding visit", "Travel and time to set up the venue, tiers and staff (about 2 hours)", "E", 600),
]
DIRECT_MONTH = [
    ("Support", "Calls, changes to offers, staff questions (about 1 hour a month of time and calls)", "E", 60),
    ("Hosting growth", "Extra database rows, traffic and card updates for 100 to 200 customers", "E", 20),
    ("Card messages and alerts", "Google and Apple card updates and push (free); our alert emails", "E", 0),
    ("Replacement standee and small extras", "Worn posters, reprints", "E", 20),
]

shared_m = sum(x[4] for x in SHARED)
one_total = sum(x[3] for x in ONE)
one_m_y1 = one_total / 12
d_once = sum(x[3] for x in DIRECT_ONCE)
d_m = sum(x[3] for x in DIRECT_MONTH)

def per_cafe(n, year):
    shared = shared_m / n
    one = one_m_y1 / n if year == 1 else 0
    direct = d_m + (d_once / 12 if year == 1 else 0)
    return shared, one, direct, shared + one + direct

H = []; X = H.append
X('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>AIKIA.WALLET cost per cafe</title><style>%s</style></head><body>' % css)

s1, o1, d1, t1 = per_cafe(1, 1); s1b, _, d1b, t1b = per_cafe(1, 2)
s5, o5, d5, t5 = per_cafe(5, 1); _, _, _, t5b = per_cafe(5, 2)
_, _, _, t100 = per_cafe(100, 1); _, _, _, t100b = per_cafe(100, 2)
X('''<section class="cover"><div class="band"><div class="ring"></div><div class="ring2"></div>
<div class="kicker">AIKIA.WALLET &nbsp;/&nbsp; COST PER CAFE</div>
<h1 style="max-width:70%%">What one cafe<br>costs us to serve.</h1>
<p style="max-width:62%%">Cost price only, no selling price. Every item we need to run the service and look after a cafe, per month and per year. Own Google and Apple wallet, no PassKit. Prices checked 19 October 2026 at Rs 96 to the US dollar.</p></div>
<div><div class="grid3" style="margin-bottom:5mm">
<div class="card pink"><div class="stat">%s<small>A MONTH per cafe if we serve 5 cafes (year 1, including start-up costs). %s a year.</small></div></div>
<div class="card pink"><div class="stat">%s<small>A MONTH per cafe at 5 cafes from year 2 (start-up costs repaid). %s a year.</small></div></div>
<div class="card pink"><div class="stat">%s<small>A MONTH: the cafe's own direct cost (support, hosting growth, extras). The rest is its share of shared costs.</small></div></div>
</div>
<div class="callout warn"><b>Why the number depends on how many cafes we have.</b> Most of the cost is shared: hosting, database, Apple, accounts and travel cost the same whether we serve 1 cafe or 50. A cafe's cost is its direct cost plus its share of the shared bill. Section 3 shows it for 1 to 100 cafes.</div>
<div class="callout"><b>Not included.</b> Founders' salaries and time, office rent, paid advertising, WhatsApp or SMS messages, a penetration test (about Rs 1 to 1.5 lakh once, past 10 cafes) and the lawyer's opinion on prepaid credit (Rs 50,000 to 1 lakh, only before real-money credit).</div>
</div></section>''' % (rs(t5), rs(t5 * 12), rs(t5b), rs(t5b * 12), rs(d_m)))

rows = "".join('<tr><td><b>%s</b><br><span class="small">%s</span></td><td>%s</td><td class="c">%s</td><td class="n">%s</td><td class="n">%s</td></tr>' % (a, b, c, f, rs(v), rs(v * 12)) for a, b, c, f, v in SHARED)
X('''<section class="sec"><div class="kicker">1 &nbsp;/&nbsp; SHARED RUNNING COSTS</div><h2>What we pay to run the service at all</h2>
<table><tr><th>Item</th><th>Basis</th><th class="c">Src</th><th class="n">A month</th><th class="n">A year</th></tr>%s
<tr><td colspan="3"><b>Shared running cost</b></td><td class="n"><b>%s</b></td><td class="n"><b>%s</b></td></tr></table>
<h3>Needed but free at our size</h3>
<table><tr><th>Item</th><th>What it does</th><th class="n">Cost</th></tr>%s</table>
</section>''' % (rows, rs(shared_m), rs(shared_m * 12), "".join('<tr><td><b>%s</b></td><td>%s</td><td class="n">Rs 0</td></tr>' % f for f in FREE)))

one_rows = "".join('<tr><td><b>%s</b><br><span class="small">%s</span></td><td class="c">%s</td><td class="n">%s</td><td class="n">%s</td></tr>' % (a, b, f, rs(v), rs(v / 12)) for a, b, f, v in ONE)
dir_once = "".join('<tr><td><b>%s</b><br><span class="small">%s</span></td><td class="c">%s</td><td class="n">%s</td><td class="n">%s</td></tr>' % (a, b, f, rs(v), rs(v / 12)) for a, b, f, v in DIRECT_ONCE)
dir_m = "".join('<tr><td><b>%s</b><br><span class="small">%s</span></td><td class="c">%s</td><td class="n">%s</td><td class="n">%s</td></tr>' % (a, b, f, rs(v), rs(v * 12)) for a, b, f, v in DIRECT_MONTH)
X('''<section class="sec"><div class="kicker">2 &nbsp;/&nbsp; ONE-TIME AND DIRECT COSTS</div><h2>Start-up costs and the cost of each cafe</h2>
<h3>One-time, to start the service (spread over the first 12 months)</h3>
<table><tr><th>Item</th><th class="c">Src</th><th class="n">Once</th><th class="n">A month in year 1</th></tr>%s
<tr><td colspan="2"><b>Total</b></td><td class="n"><b>%s</b></td><td class="n"><b>%s</b></td></tr></table>
<h3>Each cafe, once (spread over its first 12 months)</h3>
<table><tr><th>Item</th><th class="c">Src</th><th class="n">Once</th><th class="n">A month in year 1</th></tr>%s</table>
<h3>Each cafe, every month</h3>
<table><tr><th>Item</th><th class="c">Src</th><th class="n">A month</th><th class="n">A year</th></tr>%s
<tr><td colspan="2"><b>Direct cost of one cafe</b></td><td class="n"><b>%s</b></td><td class="n"><b>%s</b></td></tr></table>
<div class="callout"><b>Customers don't add cost.</b> Google and Apple charge nothing per card, so a cafe with 100 or 200 customers costs us the same. A cafe's ledger for a year is a few MB.</div>
</section>''' % (one_rows, rs(one_total), rs(one_m_y1), dir_once, dir_m, rs(d_m), rs(d_m * 12)))

def tbl(year):
    out = ""
    for n in (1, 3, 5, 10, 25, 50, 100):
        s, o, d, t = per_cafe(n, year)
        out += '<tr%s><td class="n">%d</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n"><b>%s</b></td><td class="n"><b>%s</b></td></tr>' % (' style="background:#fff0f7"' if n == 5 else "", n, rs(s), rs(o), rs(d), rs(t), rs(t * 12))
    return out
X('''<section class="sec"><div class="kicker">3 &nbsp;/&nbsp; COST OF ONE CAFE</div><h2>Per cafe, per month and per year</h2>
<h3>Year 1 (start-up costs spread over 12 months)</h3>
<table><tr><th class="n">Cafes we serve</th><th class="n">Share of running costs</th><th class="n">Share of start-up costs</th><th class="n">Direct cost</th><th class="n">Cost of one cafe a month</th><th class="n">A year</th></tr>%s</table>
<h3>Year 2 onward (start-up costs repaid)</h3>
<table><tr><th class="n">Cafes we serve</th><th class="n">Share of running costs</th><th class="n">Share of start-up costs</th><th class="n">Direct cost</th><th class="n">Cost of one cafe a month</th><th class="n">A year</th></tr>%s</table>
<div class="callout warn"><b>If we serve just one cafe</b>, that cafe carries everything: %s a month (%s a year) in year 1, and %s a month (%s a year) after. With 100 cafes the same service costs %s a month per cafe in year 1 and %s from year 2.</div>
<h3>Sources and notes</h3>
<ul class="srclist small"><li>Vercel, Supabase, Apple, Open-Meteo, GitHub prices and the Rs 96 rate: AIKIA.WALLET Launch Costing (own wallet), sources listed there, checked 19 Oct 2026.</li>
<li>GST on imported software is a real cost until we are GST-registered; after registration it is claimed back (about Rs 1,560 a month less).</li>
<li>Estimates (E) are planning figures to be replaced with real numbers after the first 3 months.</li></ul>
</section>''' % (tbl(1), tbl(2), rs(t1), rs(t1 * 12), rs(t1b), rs(t1b * 12), rs(t100), rs(t100b)))

X('</body></html>')
open(OUT_HTML, "w", encoding="utf-8").write("".join(H))
r = subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--print-to-pdf=" + os.path.abspath(OUT_PDF), "file:///" + OUT_HTML.replace("\\", "/")], capture_output=True, text=True, timeout=180)
print("pdf", os.path.exists(OUT_PDF), r.returncode, "shared", round(shared_m), "one", one_total, "direct", d_m, d_once)
for n in (1, 5, 100): print(n, [round(x) for x in per_cafe(n, 1)], [round(x) for x in per_cafe(n, 2)])
