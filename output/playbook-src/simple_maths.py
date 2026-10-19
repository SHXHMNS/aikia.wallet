# -*- coding: utf-8 -*-
"""AIKIA.WALLET business maths, made simple. Software, system and security costs only
(founders build everything, devices owned, lawyer/CA/travel/physical work excluded as instructed 19 Oct 2026).
Price Rs 1,500 + GST a cafe a month. Prices checked 19 Oct 2026 at Rs 96 to the US dollar."""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_HTML = os.path.join(HERE, "AIKIA-WALLET-Business-Maths.html")
OUT_PDF = os.path.join(HERE, "..", "pdf", "AIKIA-WALLET-Business-Maths-Simple.pdf")
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

SOFTWARE = [
    ("Vercel Pro", "Runs the website, dashboards, staff scanner, guest pages", 20 * FX),
    ("Supabase Pro", "Database, ledger, logins, daily backups", 25 * FX),
    ("Apple Developer", "Apple Wallet cards (US$99 a year)", 99 / 12 * FX),
    ("Open-Meteo commercial", "Weather data for weather-mood messages", 29 * FX),
    ("GitHub Team (2 users)", "Keeps our code private and protected", 8 * FX),
]
FREE = ["Google Wallet API", "Apple push updates", "Email (Resend free)", "Automation and backups (GitHub Actions, Cloudflare R2)", "Security shield and DNS (Cloudflare)", "Password manager (Bitwarden, 2 users)"]
BILL = sum(x[2] for x in SOFTWARE)            # GST on these is claimed back because we are GST-registered
PRICE = 1500
KEEP = PRICE * 0.99                           # about 1% goes to the payment gateway
STEP_AT, STEP = 150, 6000                     # bigger database past ~150 cafes (E)
def profit(n): return n * KEEP - BILL - (STEP if n > STEP_AT else 0)
BREAK_EVEN = next(n for n in range(1, 500) if profit(n) >= 0)
ONE_LAKH = next(n for n in range(1, 500) if profit(n) >= 100000)

NEW, CHURN = 8, 0.03                          # 2 new cafes a week; 3 in 100 leave each month
months = []; n = 0.0
for m in range(1, 25):
    n = n * (1 - CHURN) + NEW
    months.append((m, n, n * KEEP, BILL, profit(n)))
LAKH_MONTH = next(m for m, c, i, b, p in months if p >= 100000)

def chart():
    W, Ht, L, B = 900, 300, 60, 40
    mx = max(p for *_, p in months[:18])
    s = ['<svg class="chart" viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg">' % (W, Ht)]
    s.append('<text x="10" y="18" font-size="13" font-weight="700" fill="#15131c">Profit each month after the software bill (8 new cafes a month)</text>')
    bw = (W - L - 20) / 18
    yz = Ht - B
    for i, (m, c, inc, bill, p) in enumerate(months[:18]):
        h = (p / mx) * (Ht - B - 50)
        x = L + i * bw + 4
        s.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" fill="%s"/>' % (x, yz - h, bw - 8, h, "#e6007a" if p >= 100000 else "#2b5fb3"))
        s.append('<text x="%.1f" y="%d" font-size="9" text-anchor="middle" fill="#6f6b7a">M%d</text>' % (x + (bw - 8) / 2, Ht - 22, m))
        if m in (1, 3, 6, 9, 12, 18): s.append('<text x="%.1f" y="%.1f" font-size="8.5" text-anchor="middle" fill="#15131c">%.0fk</text>' % (x + (bw - 8) / 2, yz - h - 4, p / 1000))
    s.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#9b97a8"/>' % (L, yz, W - 10, yz))
    y1l = yz - (100000 / mx) * (Ht - B - 50)
    s.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="#e6007a" stroke-dasharray="4 3"/><text x="%d" y="%.1f" font-size="9" fill="#e6007a">Rs 1 lakh a month</text>' % (L, y1l, W - 10, y1l, L + 2, y1l - 4))
    s.append('</svg>')
    return "".join(s)

H = []; X = H.append
X('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>AIKIA.WALLET business maths</title><style>%s</style></head><body>' % css)
X('''<section class="cover"><div class="band"><div class="ring"></div><div class="ring2"></div>
<div class="kicker">AIKIA.WALLET &nbsp;/&nbsp; THE MATHS, MADE SIMPLE</div>
<h1 style="max-width:70%%">Three numbers<br>run this business.</h1>
<p style="max-width:62%%">We build everything ourselves and already own the phones and laptops. So the only real cost is the online software. This page shows why we can't go bankrupt, how many cafes we need, and when the money becomes good. Price: Rs 1,500 a month + GST per cafe.</p></div>
<div><div class="grid3" style="margin-bottom:5mm">
<div class="card pink"><div class="stat">%s<small>NUMBER 1: OUR MONTHLY BILL. All the software, system and security. The same for 1 cafe or 150.</small></div></div>
<div class="card pink"><div class="stat">%s<small>NUMBER 2: WHAT WE KEEP FROM EACH CAFE a month (Rs 1,500 minus about 1%% payment fee; the GST goes to the government).</small></div></div>
<div class="card pink"><div class="stat">%d cafes<small>NUMBER 3: BREAK-EVEN. Bill divided by what each cafe pays us. From cafe %d, every cafe is profit.</small></div></div>
</div>
<div class="callout ok"><b>The whole business in one line.</b> Profit a month = (number of cafes x %s) minus %s. That's it.</div>
<div class="callout"><b>Why we can't go bankrupt.</b> Our worst case is zero cafes for a whole year. That costs %s a year: the software bill. Keep that amount aside and nothing else can sink us. There is no rent, no salary bill and no loan in this model.</div>
</div></section>''' % (rs(BILL), rs(KEEP), BREAK_EVEN, BREAK_EVEN, rs(KEEP), rs(BILL), rs(BILL * 12)))

rows = "".join('<tr><td><b>%s</b></td><td>%s</td><td class="n">%s</td><td class="n">%s</td></tr>' % (a, b, rs(v), rs(v * 12)) for a, b, v in SOFTWARE)
X('''<section class="sec"><div class="kicker">1 &nbsp;/&nbsp; NUMBER 1: THE BILL</div><h2>Everything we pay every month</h2>
<table><tr><th>Software</th><th>What it does</th><th class="n">A month</th><th class="n">A year</th></tr>%s
<tr><td colspan="2"><b>Total bill</b></td><td class="n"><b>%s</b></td><td class="n"><b>%s</b></td></tr></table>
<p><b>Free, and enough for us:</b> %s.</p>
<div class="callout"><b>Customers cost nothing.</b> Google and Apple charge nothing per wallet card. A cafe with 100 customers and a cafe with 500 cost us the same. More cafes don't raise the bill until about 150 cafes, when the database needs an upgrade (about %s more a month).</div>
<div class="callout warn"><b>Left out, as you asked:</b> development (we build it), phones and laptops (we own them), lawyer and CA fees, travel and physical work. GST on the software is left out too, because as a GST-registered business we claim it back.</div>
<h3>Even cheaper while we have no paying cafe</h3>
<p>Until the first cafe pays, we can demo on the free Vercel and Supabase plans and pay only Apple (about %s a month). Switch to the paid plans the day the first cafe pays.</p>
</section>''' % (rows, rs(BILL), rs(BILL * 12), ", ".join(FREE), rs(STEP), rs(99 / 12 * FX)))

ladder = "".join('<tr%s><td class="n">%d</td><td class="n">%s</td><td class="n">%s</td><td class="n"><b>%s</b></td><td class="n">%s</td><td class="n">%s</td></tr>' % (
    ' style="background:#fff0f7"' if n in (BREAK_EVEN, ONE_LAKH) else "", n, rs(n * KEEP), rs(BILL + (STEP if n > STEP_AT else 0)), rs(profit(n)), rs(profit(n) * 12), rs(max(profit(n), 0) / 2))
    for n in sorted({1, 3, BREAK_EVEN, 10, 25, 50, ONE_LAKH, 100, 150, 200}))
X('''<section class="sec"><div class="kicker">2 &nbsp;/&nbsp; THE MATHS</div><h2>How many cafes, how much money</h2>
<p class="lede">Every row uses the same sum: cafes x %s, minus the bill.</p>
<table><tr><th class="n">Cafes</th><th class="n">Money in a month</th><th class="n">Software bill</th><th class="n">Profit a month</th><th class="n">Profit a year</th><th class="n">Each founder a month</th></tr>%s</table>
<h3>Read it like this</h3>
<ul><li><b>Cafes 1 to %d</b> pay the software bill.</li>
<li><b>Every cafe after that</b> puts about %s a month in our pocket, and about %s a year.</li>
<li><b>%d cafes</b> = about Rs 1 lakh a month profit (Rs 50,000 each for two founders).</li>
<li><b>100 cafes</b> = about %s a month. <b>200 cafes</b> = about %s a month.</li></ul>
<div class="callout warn"><b>Before tax.</b> If the founders take this as salary, it is a company cost and the company pays little or no tax on it; personal tax at Rs 6 lakh a year each is likely nil under the new regime. Confirm with your CA.</div>
</section>''' % (rs(KEEP), ladder, BREAK_EVEN, rs(KEEP), rs(KEEP * 12), ONE_LAKH, rs(profit(100)), rs(profit(200))))

mrows = "".join('<tr><td>Month %d</td><td class="n">%d</td><td class="n">%s</td><td class="n">%s</td><td class="n"><b>%s</b></td></tr>' % (m, round(c), rs(i), rs(b), rs(p)) for m, c, i, b, p in months if m in (1, 2, 3, 4, 6, 9, LAKH_MONTH, 12, 18, 24))
total12 = sum(p for *_, p in months[:12])
X('''<section class="sec"><div class="kicker">3 &nbsp;/&nbsp; AFTER LAUNCH</div><h2>When the money becomes good</h2>
<p class="lede">If we sign 2 cafes a week (8 a month) and 3 in every 100 cafes leave each month:</p>
%s
<table><tr><th>Month</th><th class="n">Cafes</th><th class="n">Money in</th><th class="n">Software bill</th><th class="n">Profit</th></tr>%s</table>
<ul><li><b>Month 1:</b> already above the bill with %d cafes.</li>
<li><b>Month %d:</b> profit passes Rs 1 lakh a month.</li>
<li><b>First 12 months together:</b> about %s profit.</li></ul>
<div class="callout ok"><b>The only job: sell 2 cafes a week and keep them happy.</b> Faster selling moves every date earlier; at 1 cafe a week the Rs 1 lakh month comes later (about month %s), but we still never lose money after cafe %d.</div>
</section>''' % (chart(), mrows, round(months[0][1]), LAKH_MONTH, rs(total12),
    next((m for m, c, *_ in [(mm, cc) for mm, cc in [(k + 1, 4 * (1 - 0.97 ** (k + 1)) / 0.03) for k in range(60)]] if profit(c) >= 100000), "36+"), BREAK_EVEN))

X('''<section class="sec"><div class="kicker">4 &nbsp;/&nbsp; THE RULES</div><h2>Five rules so we never go into loss</h2>
<ol><li><b>Keep %s in the bank</b> before launch: one full year of the software bill. With it, even zero sales can't hurt us.</li>
<li><b>Get %d paying cafes first.</b> Until then, stay on free plans for demos.</li>
<li><b>One price, no discounts:</b> Rs 1,500 + GST a month, or Rs 18,000 + GST a year.</li>
<li><b>Ask for yearly payment first.</b> One yearly cafe pays the software bill for about 2 months.</li>
<li><b>Watch one number every month: cafes.</b> If it goes up, profit goes up. If cafes leave, find out why that same week.</li></ol>
<div class="callout"><b>Check the bill every 6 months.</b> Prices are in US dollars; if the rupee weakens by Rs 5, the bill rises by about %s a month. Still tiny next to what %d cafes bring in.</div>
<p class="small">Sources: Vercel Pro US$20, Supabase Pro US$25, Apple US$99 a year, Open-Meteo US$29, GitHub Team about US$4 a user: AIKIA.WALLET Launch Costing (sources listed there), checked 19 Oct 2026. Selling speed and leaving rate are planning estimates.</p>
</section>''' % (rs(BILL * 12), BREAK_EVEN, rs(sum(x[2] for x in SOFTWARE) / FX * 5), ONE_LAKH))

X('</body></html>')
open(OUT_HTML, "w", encoding="utf-8").write("".join(H))
r = subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--print-to-pdf=" + os.path.abspath(OUT_PDF), "file:///" + OUT_HTML.replace("\\", "/")], capture_output=True, text=True, timeout=180)
print("pdf", os.path.exists(OUT_PDF), r.returncode, "bill", round(BILL), "keep", KEEP, "be", BREAK_EVEN, "1L", ONE_LAKH, "lakh month", LAKH_MONTH, "12m", round(total12))
print([(m, round(c), round(p)) for m, c, i, b, p in months[:13]])
