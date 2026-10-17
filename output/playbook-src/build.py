# -*- coding: utf-8 -*-
import os, subprocess, sys
from html import escape as e
import data as D
import charts as C

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_HTML = os.path.join(HERE, "AIKIA-WALLET-Founder-Playbook.html")
OUT_PDF = os.path.join(HERE, "..", "pdf", "AIKIA-WALLET-Founder-Playbook-India.pdf")
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
css = open(os.path.join(HERE, "style.css"), encoding="utf-8").read()
R = lambda x, s=True: D.inr(x, s)

def wave_tag(w):
    return {1: '<span class="tag t1">Wave 1</span>', 2: '<span class="tag t2">Wave 2</span>', 3: '<span class="tag t3">Wave 3</span>'}[w]

# ---------------------------------------------------------------- business type tables
def cluster_html():
    out = []
    for i, (name, why, rows) in enumerate(D.CLUSTERS, 1):
        out.append('<div class="cluster"><div class="cluster-h"><span class="no">%d</span><h3>%s</h3><span class="why">%s</span></div>' % (i, e(name), e(why)))
        out.append('<table><thead><tr><th style="width:21%">Business type</th><th style="width:13%">What counts</th><th style="width:25%">Reward ideas</th><th style="width:19%">Standout modules</th><th style="width:16%">Watch-outs</th><th style="width:6%">When</th></tr></thead><tbody>')
        for (t, count, rew, mod, watch, w) in rows:
            out.append('<tr><td><b>%s</b></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (e(t), e(count), e(rew), e(mod), e(watch), wave_tag(w)))
        out.append('</tbody></table></div>')
    return "".join(out)

def matrix_html():
    out = ['<table class="matrix"><thead><tr><th>Business type</th>']
    for m in D.MODULES:
        out.append('<th><span>%s</span></th>' % e(m))
    out.append('</tr></thead><tbody>')
    for name, vals in D.MATRIX:
        if vals is None:
            out.append('<tr><td class="grp" colspan="%d">%s</td></tr>' % (len(D.MODULES) + 1, e(name)))
            continue
        out.append('<tr><td>%s</td>' % e(name))
        for v in vals:
            out.append('<td>%s</td>' % ({2: '<span class="dot full"></span>', 1: '<span class="dot half"></span>', 0: ""}[v]))
        out.append('</tr>')
    out.append('</tbody></table>')
    return "".join(out)

def archetype_html():
    rows = D.archetype_rows()
    out = ['<table><thead><tr><th>Example customer</th><th class="n">Active members</th><th class="n">Suggested price / month</th><th class="n">Our cost to serve / month</th><th class="n">Gross margin</th><th class="n">Marketing messages we pass on (billed at cost +30%)</th></tr></thead><tbody>']
    for r in rows:
        out.append('<tr><td><b>%s</b></td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%d%%</td><td class="n">%s</td></tr>' % (
            e(r["label"]), "{:,}".format(r["members"]), D.inr(r["price"]), D.inr(round(r["platform_cost"], -1)), round(r["gm"] * 100), D.inr(round(r["mkt_bill"], -1))))
    out.append('</tbody></table>')
    return "".join(out)

def backlog_html():
    pm, cost = D.backlog_total()
    out = ['<table><thead><tr><th>Work package still to build</th><th class="n">Person-months</th></tr></thead><tbody>']
    for t, p in D.BACKLOG:
        out.append('<tr><td>%s</td><td class="n">%.1f</td></tr>' % (e(t), p))
    out.append('<tr><td><b>Total engineering effort</b></td><td class="n"><b>%.1f</b></td></tr></tbody></table>' % pm)
    return "".join(out), pm, cost

def delivery_html():
    opts, pm, dev_cost = D.delivery_options()
    out = ['<table><thead><tr><th>Delivery option</th><th>Team</th><th class="n">Months</th><th class="n">Build cost (range)</th><th>Note</th></tr></thead><tbody>']
    for o in opts:
        lo, hi = o["build"] * 0.8, o["build"] * 1.25
        out.append('<tr><td><b>%s</b></td><td>%s</td><td class="n">%d</td><td class="n">%s to %s</td><td>%s</td></tr>' % (e(o["name"]), e(o["team"]), o["months"], R(lo), R(hi), e(o["note"])))
    out.append('</tbody></table>')
    return "".join(out), opts

def stage_html():
    rows = D.stage_rows()
    out = ['<table><thead><tr><th>Cost line (per month)</th>']
    for r in rows:
        out.append('<th class="n">%s<br><span style="font-weight:400">%s</span></th>' % (r["name"], e(r["desc"])))
    out.append('</tr></thead><tbody>')
    lines = [("Cloud: database, hosting, storage, bandwidth", "cloud"), ("Tools: support desk, CRM, analytics, design, project tools", "tool"),
             ("Communication set-up and gateway minimums", "comms"), ("Security: scans, monitoring, log archive (averaged)", "sec"),
             ("Legal, accounting, compliance retainer", "legal"), ("People: team salaries incl. overhead", "team")]
    for lbl, k in lines:
        out.append('<tr><td>%s</td>' % e(lbl))
        for r in rows:
            out.append('<td class="n">%s</td>' % R(r[k]))
        out.append('</tr>')
    out.append('<tr><td><b>Total monthly run cost</b></td>')
    for r in rows:
        out.append('<td class="n"><b>%s</b></td>' % R(r["total"]))
    out.append('</tr><tr><td>Assumed average revenue per venue per month</td>')
    for r in rows:
        out.append('<td class="n">%s</td>' % D.inr(r["arpa"]))
    out.append('</tr><tr><td><b>Paying venues needed to break even</b> (at 70% contribution margin)</td>')
    for r in rows:
        out.append('<td class="n"><b>{:,}</b></td>'.format(round(r["breakeven"])))
    out.append('</tr><tr><td>Recurring revenue at the top of the stage (monthly)</td>')
    for r in rows:
        out.append('<td class="n">%s</td>' % R(r["rev"]))
    out.append('</tr></tbody></table>')
    return "".join(out), rows

backlog_tbl, PM, DEVCOST = backlog_html()
delivery_tbl, OPTS = delivery_html()
stage_tbl, STAGE = stage_html()
B_OPT = OPTS[1]

SOURCES = [
 ("RBI draft Master Direction on PPIs, 2026 (Nasscom summary)", "https://community.nasscom.in/communities/public-policy/key-highlights-rbi-draft-master-direction-prepaid-payment-instruments"),
 ("RBI Master Direction on PPIs (Trilegal note, 2021 framework)", "https://trilegal.com/knowledge_repository/new-master-directions-on-prepaid-payment-instruments/"),
 ("RBI draft PPI directions, 2026 (Lexology)", "https://www.lexology.com/library/detail.aspx?g=741da40c-2952-4c9b-8f94-886e57b874ec"),
 ("RBI Master Directions page", "https://www.rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=11142"),
 ("RBI Payment Aggregator Directions 2025 (Outlook Business)", "https://www.outlookbusiness.com/news/rbi-issues-new-master-directions-for-payment-aggregators-rules-take-effect-immediately"),
 ("DPDP Rules 2025 timeline (TCSA)", "https://www.tcsa.in/resources/dpdp-rules-2025-implementation-roadmap"),
 ("DPDP Rules 2025 explained", "https://dpdpactindia.in/dpdp-rules/"),
 ("DPDP Act timeline 2025-2027", "https://www.dpdpactindia.com/timeline.html"),
 ("GST on vouchers (Lakshmikumaran & Sridharan)", "https://lakshmisri.com/insights/articles/treatment-of-vouchers-under-gst-law"),
 ("GST on vouchers and gift cards (Taxmann)", "https://www.taxmann.com/post/blog/opinion-understanding-gst-implications-on-vouchers-gift-cards-in-india/"),
 ("India loyalty programs market (ResearchAndMarkets via BusinessWire)", "https://www.businesswire.com/news/home/20250213552919/en/India-Loyalty-Programs-Market-Intelligence-2025-Cross-Industry-and-Cross-Brand-Loyalty-Partnerships-Competitive-Landscape-Data-Analytics-for-Personalization---Future-Growth-Dynamics-to-2029---ResearchAndMarkets.com"),
 ("India loyalty management software market (MarketsandMarkets)", "https://www.marketsandmarkets.com/Market-Reports/geography/loyalty-management-market/India"),
 ("India loyalty programme market (Future Market Insights)", "https://www.futuremarketinsights.com/reports/india-loyalty-program-market"),
 ("Channel loyalty report 2025 (Almonds.ai)", "https://content.almonds.ai/wp-content/uploads/2025/02/19060337/Channel-Loyalty-Report-2025.pdf"),
 ("UDISE+ 2024-25 analysis", "https://educationforallinindia.com/trends-in-school-education-in-india-an-analysis-based-on-udise-2024-25-data/"),
 ("AISHE higher-education network (Free Press Journal)", "https://www.freepressjournal.in/analysis/the-aishe-report-institutional-network-of-higher-education"),
 ("Food services sector size (India Retailing, NRAI)", "https://www.indiaretailing.com/2024/07/10/food-services-sector-set-to-reach-rs-7-76-lakh-crore"),
 ("Salon industry overview (Lakme Salon)", "https://www.lakmesalon.in/pages/industry-overview"),
 ("Kirana store estimates (Inc42)", "https://inc42.com/?p=155952"),
 ("WhatsApp Business API pricing India 2026 (Monty Mobile)", "https://montymobile.com/blogs/whatsapp-business-api-pricing-in-india-inr-rates-gst-and-the-2026-currency-migration-deadline"),
 ("WhatsApp API pricing update (Authkey)", "https://authkey.io/blogs/?p=1840"),
 ("DLT registration (Infobip)", "https://www.infobip.com/docs/essentials/asia-registration/dlt-registration"),
 ("A2P SMS pricing India (Message Central)", "https://www.messagecentral.com/en-in/blog/a2p-sms-pricing-india"),
 ("PassKit pricing", "https://passkit.com/pricing/video/"),
 ("Google Wallet loyalty FAQ", "https://developers.google.com/wallet/retail/loyalty-cards/resources/faq"),
 ("Push notification limits in Google Wallet (Notificare)", "https://notificare.com/blog/2024/06/21/push-notifications-in-google-wallet/"),
 ("Apple Developer Program fee, India (Apple forums)", "https://developer.apple.com/forums/thread/746357"),
 ("Supabase pricing 2026 (Makerkit)", "https://makerkit.dev/blog/md/saas/supabase-pricing"),
 ("CERT-In directions overview (PSA Legal)", "https://psalegal.com/new-cert-in-directions-overview-and-implications/"),
 ("Company registration costs 2026 (Taxaj)", "https://www.taxaj.com/learn/company-registration-fees-india/"),
 ("Full stack developer pay India 2026 (Weekday)", "https://www.weekday.works/post/full-stack-developer-salary-in-india-2026"),
 ("Loyalty software for Indian retail (commmerce.com)", "https://commmerce.com/blog/top-loyalty-program-platforms-indian-retail/"),
 ("AIKIA internal: Vertical Expansion Blueprint (Oct 2026)", "output/pdf/AIKIA-WALLET-Vertical-Expansion-Blueprint.pdf"),
]

html = []
A = html.append
A('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>AIKIA.WALLET Founder Playbook India</title><style>%s</style></head><body>' % css)

# ================================================================ COVER
A('''<section class="cover"><div class="band"><div class="ring"></div><div class="ring2"></div>
<div class="kicker">AIKIA.WALLET &nbsp;/&nbsp; FOUNDER PLAYBOOK</div>
<h1>One membership card<br>for every Indian business.</h1>
<p>Where it fits, what each business type gets, how the system works, what the law requires when money is involved, and what it costs to build, launch and run. Prepared for the founders. October 2026.</p></div>
<div>
<h3 style="margin-bottom:2mm">Questions this document answers</h3>
<div class="grid2" style="margin-bottom:5mm">
<div class="card"><h4>Where does it fit?</h4><p class="small" style="color:#3b3846">25+ business types across food, fashion, electronics, grocery, health, services, hospitality, education and channel loyalty, with the features each one gets.</p></div>
<div class="card"><h4>How does it work?</h4><p class="small" style="color:#3b3846">An end-to-end flow chart, a system map, and a customisation grid showing what changes for each business type.</p></div>
<div class="card"><h4>What does the law need?</h4><p class="small" style="color:#3b3846">Company and tax, RBI rules on stored money, data protection (DPDP), messaging, consumer and security duties, and the order to do them in.</p></div>
<div class="card"><h4>What does it cost?</h4><p class="small" style="color:#3b3846">Three ways to build, run cost at three sizes, and the monthly cost and suggested price for eight kinds of customer.</p></div>
</div>
<div class="grid3" style="margin-bottom:5mm">
<div class="card soft"><div class="stat">25+<small>business types in 9 clusters, from cafes and sweet shops to schools and colleges</small></div></div>
<div class="card soft"><div class="stat">5<small>charts: customer flow, system map, customisation grid, money models, 24-month path</small></div></div>
<div class="card soft"><div class="stat">3 build<br>options<small>costed, with run cost at pilot, growth and scale</small></div></div>
</div>
<div class="callout warn"><b>How to read the numbers.</b> Market facts come from public sources listed on the last pages; several are vendor or secondary sources and are marked. Costs and prices are planning estimates built from the stated assumptions, not quotes. Legal sections are a research briefing to take to a lawyer and a chartered accountant, not legal advice.</div>
<p class="small">Built on the existing AIKIA.WALLET codebase (Next.js, Supabase, Google Wallet engine, spend tiers, venue wizard, geofencing and campaigns). Internal document. Do not circulate outside the founder group without review.</p></div></section>''')

# ================================================================ CONTENTS + EXEC SUMMARY
A('''<section class="sec"><div class="kicker">00 / SUMMARY</div><h2>The short version</h2>
<p class="lede">aikia.wallet can serve almost any business that has repeat customers, if we treat it as one membership engine with a small set of rules that each business configures, not as a custom app per industry.</p>
<div class="grid2">
<div class="card pink"><h3>What we sell</h3><p>A venue-branded card in the customer's phone wallet, a staff scanner, an owner dashboard and a ledger that records every visit and reward. The venue chooses what counts (a purchase, a visit, an attended class), what is earned (stamps, points, tiers, packs, badges) and how members are reached (wallet, WhatsApp, SMS).</p></div>
<div class="card"><h3>Why it can scale</h3><p>The same ledger and wallet pass serve a 400-member cafe and a 40,000-member supermarket. Differences live in presets, rules and integrations. Sales scale through partners (POS vendors, agencies, brands, distributors), because direct selling to millions of small venues does not pay.</p></div>
<div class="card"><h3>The biggest legal line</h3><p>Points and visits are low-risk. Stored money (wallet balance, top-ups, transfers) is a regulated payment product under RBI rules. <b>Recommendation: launch with points only, add venue-run prepaid packs later with counsel, never hold customer money.</b> Data protection (DPDP Act) applies from day one, and fully from about May 2027.</p></div>
<div class="card"><h3>The money</h3>
<p><b>Build:</b> about %s to %s with a small in-house team over about %d months (Option B). <b>Run:</b> about %s a month at pilot, %s at growth, %s at scale. <b>Break-even:</b> roughly %d paying venues at growth-stage cost, if the average venue pays about %s a month.</p></div>
</div>
<h3>What we recommend, in order</h3>
<ol>
<li><b>Pick three pilot venues</b> in Wave 1 types (a cafe, a sweet shop or bakery, a salon or court). RUH can be pilot zero for the sweets vertical.</li>
<li><b>Decide the money model now</b> (Chart 4): points only. Put venue-run prepaid packs on the Phase 2 list.</li>
<li><b>Fix the legal base before the first paying customer</b>: company, GST, trademark check on the name, privacy policy and venue data-processing terms, DLT registration for SMS.</li>
<li><b>Build the integration and messaging layer next</b>. POS and WhatsApp are what turn a pilot into a repeatable product.</li>
<li><b>Treat education as a separate programme</b>: start with one college campus (the PU PULSE idea) before schools, because minors' data raises the compliance bar.</li>
</ol></section>''' % (R(B_OPT["build"] * 0.8), R(B_OPT["build"] * 1.25), B_OPT["months"], R(STAGE[0]["total"]), R(STAGE[1]["total"]), R(STAGE[2]["total"]), round(STAGE[1]["breakeven"]), D.inr(STAGE[1]["arpa"])))

A('''<section class="sec"><div class="kicker">CONTENTS</div><h2>What is inside</h2>
<div class="toc">
<div><b>01</b><span>The product in one page: what it is and is not</span></div>
<div><b>02</b><span>Market: why Indian businesses need this</span></div>
<div><b>03</b><span>Every business type, cluster by cluster, with features</span></div>
<div><b>04</b><span>Chart 1: end-to-end flow</span></div>
<div><b>05</b><span>Chart 2: how the system works</span></div>
<div><b>06</b><span>Chart 3: what we customise for each business type</span></div>
<div><b>07</b><span>Education: schools and colleges</span></div>
<div><b>08</b><span>Feature catalogue, core and add-on modules</span></div>
<div><b>09</b><span>How to scale: pricing, channels, integrations, stage gates</span></div>
<div><b>10</b><span>Legal and money: what is needed and in what order</span></div>
<div><b>11</b><span>Cost to build, cost to run, cost to serve each customer type</span></div>
<div><b>12</b><span>Running the system: team, operations, support, security</span></div>
<div><b>13</b><span>Things you may have missed</span></div>
<div><b>14</b><span>Roadmap, risks, decisions needed, sources</span></div>
</div>
<h3>Words used in this document</h3>
<dl class="kv">
<dt>Qualifying action</dt><dd>The thing that earns progress: a purchase, a completed appointment, an attended class, a scanned invoice.</dd>
<dt>Ledger</dt><dd>The append-only record of every earn and redeem event. The source of truth. The wallet card only shows it.</dd>
<dt>Preset</dt><dd>A ready-made configuration for a business type (cafe, salon, school) that a venue can accept in minutes.</dd>
<dt>Venue-run prepaid</dt><dd>A pack or credit the venue itself sells and honours, with the money collected by the venue. aikia only records balance and use.</dd>
<dt>PPI</dt><dd>Prepaid Payment Instrument: the RBI term for wallets, prepaid cards and similar stored value.</dd>
<dt>DPDP</dt><dd>India's Digital Personal Data Protection Act 2023 and the Rules notified in November 2025.</dd>
<dt>DLT, BSP</dt><dd>DLT is the telecom registry for business SMS. A BSP is a WhatsApp Business Solution Provider.</dd>
</dl></section>''')

# ================================================================ 01 PRODUCT
A('''<section class="sec"><div class="kicker">01 / THE PRODUCT</div><h2>One engine, many shop types</h2>
<p class="lede">Every loyalty idea in this document is built from the same six parts. A new business type is a new combination of these parts, not a new product.</p>
<div class="grid3">
<div class="card"><h4>1. Trigger</h4><p>What counts. A paid bill closed in the POS, a staff scan, a booking marked attended, a class check-in, a teacher marking attendance, a scanned invoice.</p></div>
<div class="card"><h4>2. Accrual</h4><p>What is earned. A stamp, points per rupee, a visit, a session credit, a house point, a bonus multiplier at off-peak hours.</p></div>
<div class="card"><h4>3. Reward</h4><p>What is unlocked. A free item, rupees off, an add-on service, priority booking, a badge, a brand-funded coupon, a guest pass.</p></div>
<div class="card"><h4>4. Tier</h4><p>Where the member stands. By spend, by visits or by time in the programme: Ink, Chrome, Pink in the current build.</p></div>
<div class="card"><h4>5. Limits and expiry</h4><p>Caps per day, one-time redemption, points expiry, pack validity, exclusions, reversal on returns or cancellations.</p></div>
<div class="card"><h4>6. Channel</h4><p>How the member is reached: the wallet card itself, WhatsApp, SMS, a nearby-store alert, a booking or reorder link.</p></div>
</div>
<h3>What is already built (from the repository, 8 October 2026)</h3>
<table><thead><tr><th>Area</th><th>Status in the codebase</th></tr></thead><tbody>
<tr><td>Owner and staff workspaces, invitations, platform console</td><td>Built</td></tr>
<tr><td>Member join page, QR poster, phone join, return of existing membership</td><td>Built</td></tr>
<tr><td>Spend-based and visit-based tiers, bill amount at the counter</td><td>Built</td></tr>
<tr><td>Append-only ledger, idempotent redemption, row-level security</td><td>Built</td></tr>
<tr><td>Own Google Wallet engine with AIKIA card layout and tier art; PassKit as a swappable engine</td><td>Built; Google public-pass approval and live end-to-end test still to confirm</td></tr>
<tr><td>New-venue wizard, business presets (cafe first)</td><td>Built; presets for other types still to write</td></tr>
<tr><td>Geofencing, wallet notifications, offers and campaigns</td><td>Built (8 October commit); needs real-venue testing</td></tr>
<tr><td>Apple Wallet</td><td>Adapter file exists; waits for the Apple Developer account and certificate</td></tr>
<tr><td>POS or booking integrations, WhatsApp, billing and plans, education module, analytics ROI report</td><td>Not built (see the backlog in section 11)</td></tr>
</tbody></table>
<div class="callout"><b>Positioning.</b> The product helps a venue recognise a customer, reward the next visit and measure whether it worked. It is <b>not</b> a payment app, a POS, a booking engine, a medical record or a ticketing system, and the pitch must not imply that. The word "wallet" in the name refers to the phone's wallet app; keep sales language on "membership card" so nobody confuses it with a payment wallet.</div>
</section>''')

# ================================================================ 02 MARKET
A('''<section class="sec"><div class="kicker">02 / MARKET</div><h2>Why Indian businesses need this</h2>
<p class="lede">The number of possible customers is very large. The question is not whether the market exists but which slice we can serve profitably first.</p>
<div class="grid4">
<div class="card soft"><div class="stat">Rs 5.69 lakh cr<small>India food-services sector, FY24 (NRAI, as reported); projected Rs 7.76 lakh cr by FY28</small></div></div>
<div class="card soft"><div class="stat">12-13 million<small>kirana stores, industry estimates (not an official count)</small></div></div>
<div class="card soft"><div class="stat">1.47 million<small>schools, UDISE+ 2024-25 (secondary analysis)</small></div></div>
<div class="card soft"><div class="stat">48,246<small>colleges and 1,289 universities, AISHE 2023-24 (newspaper report)</small></div></div>
</div>
<h3>Loyalty market size: sources disagree, so treat as a range</h3>
<table><thead><tr><th>Source</th><th>What it measures</th><th>Figure</th></tr></thead><tbody>
<tr><td>ResearchAndMarkets (2025)</td><td>India loyalty programmes market</td><td>About US$3.58 billion in 2025, +18.3% on the year</td></tr>
<tr><td>ResearchAndMarkets (later databook)</td><td>Same, different base</td><td>About US$1.79 billion in 2025 to US$3.91 billion by 2030</td></tr>
<tr><td>Future Market Insights</td><td>India loyalty programme market</td><td>About US$4.3 billion in 2025 to US$17.1 billion by 2035</td></tr>
<tr><td>MarketsandMarkets</td><td>Loyalty <i>management software</i> only</td><td>About US$648 million in 2025 to US$959 million by 2030 (8.2% CAGR)</td></tr>
<tr><td>Almonds.ai</td><td>B2B and channel loyalty</td><td>About Rs 25,400 crore, 14% CAGR; says 60% of new 2025 deployments were small and mid-sized businesses</td></tr>
</tbody></table>
<p class="small">These are vendor-sponsored research pages with different definitions; none is an audited number. The software-only figure (about US$0.65 billion) is the most relevant to what we sell, and even a small share of it is a real business.</p>
<h3>What the gap looks like</h3>
<div class="grid2">
<div class="card"><h4>Large chains</h4><p>Already served by enterprise platforms (custom pricing; Capillary is positioned for enterprise) and by their own apps. They buy on integration depth, security and support. Long sales cycles.</p></div>
<div class="card"><h4>Small and mid-sized venues</h4><p>Often use paper punch cards, a WhatsApp list or nothing. Mid-market tools exist (Zoho Loyalty is listed at about Rs 2,000 a month on a competitor's comparison page; unverified). The opening is a card that needs <b>no app download</b>, sets up in an hour and is priced like a utility.</p></div>
<div class="card"><h4>Education</h4><p>Large institution counts, but mostly served by ERP and fee-payment tools. Digital ID, attendance engagement and campus-merchant networks are thinly served. Higher compliance burden, so fewer fast followers.</p></div>
<div class="card"><h4>Our edge</h4><p>No-download wallet card; owner-friendly set-up; vertical presets; managed program design from the aikia growth agency; a ledger that is audit-ready from day one.</p></div>
</div>
<div class="callout warn"><b>Competition check still needed.</b> We have not compared features and pricing of Indian competitors in detail (for example Zoho Loyalty, Capillary, POS-bundled loyalty tools, Google Wallet pass vendors, QR stamp-card apps). Do a one-week competitor teardown before fixing prices.</div>
</section>''')

# ================================================================ 03 BUSINESS TYPES
A('<section class="sec"><div class="kicker">03 / WHERE IT FITS</div><h2>Every business type we can serve, and what each gets</h2><p class="lede">Organised by how customers behave, because behaviour decides the design. "When" shows the suggested order of attack: Wave 1 first (0 to 6 months), Wave 2 next, Wave 3 only after integrations, security reviews or legal design are ready.</p>')
A(cluster_html())
A('</section>')

# ================================================================ 04 FLOW CHART
A('<section class="sec wide"><div class="kicker">04 / CHART 1</div>' + C.flow_chart() + '''<div class="grid3" style="margin-top:2mm">
<div class="card"><h4>Joining (steps 1 to 4)</h4><p class="small" style="color:#3b3846">A QR poster or link starts it. The member gives a phone number and ticks consent once; the platform stores the consent record and issues the card. No app to download.</p></div>
<div class="card"><h4>Earning (steps 5 to 8)</h4><p class="small" style="color:#3b3846">Staff scan the card and enter the bill or mark the visit. The rules engine applies earn rules, tier moves and limits, and blocks duplicates. The result is written to the ledger and the card refreshes.</p></div>
<div class="card"><h4>Redeeming and returning (9 to 12)</h4><p class="small" style="color:#3b3846">When a reward unlocks, staff confirm it once and the cost is logged. Automated, consent-based messages (birthday, lapse, nearby, campaign) bring the member back to step 5.</p></div>
</div></section>''')

# ================================================================ 05 ARCH
A('<section class="sec wide"><div class="kicker">05 / CHART 2</div>' + C.arch_chart() + '''<div class="grid3" style="margin-top:2mm">
<div class="card"><h4>Who touches what</h4><p class="small" style="color:#3b3846">Members use the join page and the wallet card. Staff use the scanner. Owners use the dashboard. Only the aikia team uses the platform console, and every action there is logged.</p></div>
<div class="card"><h4>What stays swappable</h4><p class="small" style="color:#3b3846">The wallet engine and the messaging provider sit behind adapters, so a provider's price rise or rule change does not force a rebuild.</p></div>
<div class="card"><h4>Where money is</h4><p class="small" style="color:#3b3846">Payments for purchases go through the venue's own gateway. The platform records rewards and visits, not funds.</p></div>
</div></section>''')

# ================================================================ 06 CUSTOMISATION
A('''<section class="sec wide"><div class="kicker">06 / CHART 3</div><h2 style="font-size:14pt;margin-bottom:1.5mm">What we customise for each business type</h2>
<p class="small" style="margin-bottom:1mm"><span class="dot full"></span> core for this type &nbsp;&nbsp; <span class="dot half"></span> optional &nbsp;&nbsp; blank = not used. Modules are switched on per venue by the preset; nothing here needs custom code.</p>''')
A(matrix_html())
A('</section>')

A('''<section class="sec"><div class="kicker">06 / CHART 3 (CONTINUED)</div><h2>The same six parts, set four different ways</h2>
<table><thead><tr><th>Part</th><th>Cafe</th><th>Salon</th><th>Supermarket chain</th><th>School</th></tr></thead><tbody>
<tr><td><b>1. Trigger</b></td><td>Paid order at counter</td><td>Appointment marked completed</td><td>Bill closed in POS</td><td>Teacher marks attendance or activity</td></tr>
<tr><td><b>2. Accrual</b></td><td>1 stamp per order; 2x in the 3-5 pm slow window</td><td>1 visit per service; rupees spent tracked</td><td>1 point per Rs 100; 2x on brand-funded items</td><td>House points and badges (no cash value)</td></tr>
<tr><td><b>3. Reward</b></td><td>Free drink at 10 stamps</td><td>Free add-on at 5th visit; pack of 6 at a set price</td><td>Rupees off at 500 points; targeted coupons</td><td>Certificate, recognition, canteen credit funded by the school</td></tr>
<tr><td><b>4. Tier</b></td><td>None, or Regular / Gold</td><td>Silver / Gold by visits per year</td><td>Household tiers by monthly spend</td><td>None (avoid ranking children)</td></tr>
<tr><td><b>5. Limits and expiry</b></td><td>Stamps expire in 6 months; 1 scan per order</td><td>Pack valid 90 days; no reward on cancelled bookings</td><td>Points expire in 12 months; reverse on returns</td><td>Term-end reset; parent can view and withdraw consent</td></tr>
<tr><td><b>6. Channel</b></td><td>Wallet alert near the shop; WhatsApp offer</td><td>"Book again" link; reminder 4 weeks later</td><td>Wallet + WhatsApp; targeted by basket history</td><td>Notices to parents with consent; no ads to children</td></tr>
</tbody></table>
<h3>Different businesses, different primary job</h3>
<table><thead><tr><th>Behaviour</th><th>Examples</th><th>The card's main job</th></tr></thead><tbody>
<tr><td><b>High frequency, low ticket</b></td><td>Cafes, tea stalls, kiranas, bakeries, juice bars</td><td>Make the next purchase habitual: stamps and quick scans</td></tr>
<tr><td><b>Appointment-led</b></td><td>Salons, clinics, gyms, garages, tutors</td><td>Make rebooking easy; protect against no-shows; reminders</td></tr>
<tr><td><b>Occasion-led, high ticket</b></td><td>Sarees, jewellery, electronics, furniture</td><td>Recognise the family, remember occasions, hold invoices and warranties</td></tr>
<tr><td><b>Basket-led, thin margin</b></td><td>Supermarkets, pharmacies</td><td>Targeted offers, household accounts, brand-funded rewards</td></tr>
<tr><td><b>Capacity-led</b></td><td>Turfs, courts, games, cinemas, hotels</td><td>Fill quiet hours; reward attended sessions; team referral</td></tr>
<tr><td><b>Identity and engagement</b></td><td>Schools, colleges, coaching, clubs</td><td>Digital ID and pass, attendance, notices, campus network</td></tr>
</tbody></table></section>''')

# ================================================================ 07 EDUCATION
A('''<section class="sec"><div class="kicker">07 / EDUCATION</div><h2>Schools and colleges</h2>
<p class="lede">In education the product is a digital identity and engagement pass, not a spend-and-earn card. Rewards are mostly recognition, access and campus convenience. The compliance bar is higher because many users are children.</p>
<div class="grid2">
<div class="card"><h3>Colleges and universities</h3>
<ul><li><b>Campus ID pass</b> in the phone wallet: library, hostel, lab, bus, exam hall.</li>
<li><b>Attendance and event check-in</b> by QR; festival and fest tickets.</li>
<li><b>Campus merchant network</b>: cafeteria, stationery, print shops and nearby cafes give student discounts. The college earns from the network; students use one card. This is the PU PULSE idea.</li>
<li><b>Placement and alumni</b>: milestones, alumni membership with renewal and event access.</li>
<li><b>Notices</b> from departments, with opt-in.</li></ul>
<p class="small"><b>Sales:</b> Registrar, student affairs or the innovation cell; pilot with one department or hostel before a campus rollout.</p></div>
<div class="card"><h3>Schools (K-12)</h3>
<ul><li><b>Parent-owned account</b> with child sub-profiles. The adult is the contract party and consent-giver.</li>
<li><b>Student pass</b>: ID, library, bus, canteen, event entry.</li>
<li><b>Recognition, not ranking</b>: badges, reading streaks, house points. No public leaderboards of children.</li>
<li><b>School-run canteen or stationery credit</b> as venue-run prepaid, never held by aikia.</li>
<li><b>Parent notices</b>: PTM reminders, holidays, event passes.</li></ul>
<p class="small"><b>Sales:</b> Principal and trustees; longer cycle, annual contract, per-campus pricing.</p></div>
</div>
<h3>Education rules to design in from day one</h3>
<table><thead><tr><th>Issue</th><th>What the research says</th><th>Design response</th></tr></thead><tbody>
<tr><td>Children's data</td><td>DPDP Rules: processing data of anyone under 18 needs verifiable parental consent; tracking, behavioural monitoring and targeted advertising directed at children are prohibited. These duties apply from about May 2027.</td><td>Parent-first accounts; no marketing messages to children; no behavioural scoring; parent can view and delete the child's record.</td></tr>
<tr><td>Who is responsible for the data</td><td>The institution decides purpose and means, so it is the "data fiduciary"; aikia is typically its processor.</td><td>Data-processing agreement with every institution; institution-owned admin; export and exit rights.</td></tr>
<tr><td>Fees</td><td>School fee regulation varies by state.</td><td>Reminders only. Do not collect fees or give fee discounts through the wallet without counsel and institution approval.</td></tr>
<tr><td>Campus merchant coalition</td><td>Cross-merchant redemption raises settlement, GST and liability questions.</td><td>Start with merchant-funded discounts at each merchant's own counter; no shared balance.</td></tr>
<tr><td>Procurement</td><td>Institutions buy slowly and ask for security evidence.</td><td>Prepare a security summary, a DPA, uptime history and references from a pilot campus.</td></tr>
</tbody></table>
<div class="callout warn"><b>To confirm:</b> state-specific school regulations, UGC / AICTE guidance on student data and ID, and whether the institution's own policies bar third-party apps. Take these to counsel before the first education pilot.</div>
</section>''')

# ================================================================ 08 FEATURE CATALOGUE
A('''<section class="sec"><div class="kicker">08 / FEATURES</div><h2>Feature catalogue</h2>
<p class="lede">What every venue gets, what is switched on by preset, and what is a paid add-on. The core is shared; the add-ons are where verticals differ and where pricing steps up.</p>
<div class="grid2">
<div class="card pink"><h3>Core (every plan)</h3><ul>
<li>Venue-branded wallet card; QR join page; QR poster generator</li><li>Member profile, consent record, phone verification</li>
<li>Staff scanner with roles; duplicate-scan guard</li><li>Stamps or points; tiers; rewards and one-time redemption</li>
<li>Owner dashboard: members, activity, reward cost</li><li>Append-only ledger; data export</li><li>Setup wizard and vertical preset</li></ul></div>
<div class="card"><h3>Growth add-ons</h3><ul>
<li>WhatsApp and SMS campaigns with consent and quiet hours</li><li>Birthday, anniversary and lapse automations</li>
<li>Geofence alerts and offers</li><li>Referral programme</li><li>Packs and validity (venue-run prepaid)</li>
<li>Appointment or booking link; check-in</li><li>ROI report: repeat rate, reward cost, cohorts</li></ul></div>
<div class="card"><h3>Business and enterprise add-ons</h3><ul>
<li>Multi-outlet and franchise roll-ups</li><li>POS, ERP, Shopify and booking integrations</li>
<li>Brand-funded offers and co-op campaigns</li><li>Household / family accounts</li><li>Document and warranty vault</li>
<li>Single sign-on, API and webhooks, audit export</li><li>Priority support and SLA</li></ul></div>
<div class="card"><h3>Education add-ons</h3><ul>
<li>Student and parent profiles; parental consent flow</li><li>Campus ID, library, hostel, bus passes</li>
<li>Attendance and event check-in</li><li>Campus merchant network</li><li>Department admins and notices</li>
<li>Alumni membership and renewal</li></ul></div>
</div>
<h3>Wallet card behaviour to know</h3>
<ul>
<li><b>Google Wallet</b> works for Android users now. Developer-authored push messages are reported as not supported by Google's own FAQ; third-party sources describe limited update notifications (about three per pass per 24 hours, near a relevant time). Plan on card updates, geofence-style alerts and WhatsApp for outreach, and verify the current Google rules before promising any message type.</li>
<li><b>Apple Wallet</b> needs the Apple Developer account and a pass certificate. Until then, iPhone users need a fallback: a web card or a PassKit-issued pass.</li>
<li><b>Feature-phone and no-wallet users</b> need a fallback card (a link that shows a QR and balance) and SMS notices.</li>
<li><b>A pass shows data on the lock screen.</b> Keep anything sensitive (treatment, medical, student grades) off it.</li></ul>
</section>''')

# ================================================================ 09 SCALING
A('''<section class="sec"><div class="kicker">09 / HOW TO SCALE</div><h2>From three pilots to thousands of venues</h2>
<div class="grid2">
<div class="card"><h3>1. Productise before you grow</h3><p>Write one preset per vertical, one onboarding checklist per vertical, one reporting template per vertical. A new venue should go live in under an hour with no developer. Every request for "custom" is first tried as a rule or preset.</p></div>
<div class="card"><h3>2. Integrations are the real scaling lever</h3><p>Chains will not key a bill into a second screen. Wave 1 integrations should cover the POS tools your target venues already use, Shopify for online-first brands, one booking tool for salons and courts, and a CSV or webhook fallback. Confirm each vendor's API access terms before promising.</p></div>
<div class="card"><h3>3. Sell through partners</h3><p>Direct selling to millions of small venues does not pay. Partners who already visit venues: POS resellers, accounting and GST consultants, payment-device agents, distributors and FMCG field teams (brand-funded kirana programmes), franchise consultants, college innovation cells, and the aikia agency's own clients.</p></div>
<div class="card"><h3>4. Price on value, not on features</h3><p>Anchor on repeat revenue the venue can see. Keep three plans, publish them, and charge setup only for managed work (program design, creative, training).</p></div>
</div>
<h3>Pricing hypotheses to test with pilots (not market-validated)</h3>
<table><thead><tr><th>Plan</th><th>For</th><th class="n">Per month</th><th>Includes</th></tr></thead><tbody>
<tr><td><b>Starter</b></td><td>Single outlet cafe, bakery, boutique, kirana</td><td class="n">Rs 999 to 1,499</td><td>Core, 1 preset, 500 active members, 200 utility messages</td></tr>
<tr><td><b>Growth</b></td><td>Salon, gym, court, restaurant with up to 3 outlets</td><td class="n">Rs 1,999 to 2,999</td><td>Starter + campaigns, referral, packs, booking link, ROI report, 2,000 active members</td></tr>
<tr><td><b>Business</b></td><td>Chains, hotels, schools, colleges</td><td class="n">Rs 9,999 and up, per outlet or campus</td><td>Growth + multi-outlet, integrations, API, priority support</td></tr>
<tr><td><b>Enterprise</b></td><td>Supermarkets, electronics, large education groups</td><td class="n">Custom (about Rs 1.5 lakh+)</td><td>Business + SLA, security review, dedicated manager</td></tr>
<tr><td><b>Managed program (add-on)</b></td><td>Any venue wanting aikia to run the programme</td><td class="n">Setup Rs 5,000 to 25,000; monthly retainer</td><td>Programme design, creative, staff training, campaign calendar, reporting</td></tr>
<tr><td><b>Messaging</b></td><td>All</td><td class="n">Pass-through at cost +30%</td><td>WhatsApp and SMS billed per message after the allowance</td></tr>
</tbody></table>
<h3>Stage gates</h3>
<table><thead><tr><th>Stage</th><th>Venues</th><th>What must be true before moving on</th></tr></thead><tbody>
<tr><td>Prove</td><td>1 to 3</td><td>Repeat visits measurably up versus a baseline; staff scan in under 10 seconds; owner would pay; no legal blocker.</td></tr>
<tr><td>Repeat</td><td>10 to 25</td><td>Set-up under one hour; support under about 1 hour per venue per month; churn understood; two referenceable owners.</td></tr>
<tr><td>Systemise</td><td>25 to 250</td><td>Integrations live; self-serve onboarding; billing automated; monitoring and on-call in place; DPDP controls working.</td></tr>
<tr><td>Expand</td><td>250 to 2,000</td><td>Partner channel producing leads; enterprise security pack; regional language support; second wallet engine live.</td></tr>
</tbody></table>
<div class="callout ok"><b>Starting advantage.</b> You already run a growth agency with clients, a Wave 1 sweets brand (RUH), and a campus concept (PU PULSE). These are the fastest routes to the first pilots and references.</div>
</section>''')

# ================================================================ 10 LEGAL
A('<section class="sec wide"><div class="kicker">10 / LEGAL AND MONEY</div>' + C.money_models_chart() + '''
<p class="small">The single most important legal decision is which of these three the product does. Everything else in the legal section follows from it.</p>
<div class="grid3" style="margin-top:2mm">
<div class="card"><h4>A. What we need</h4><p class="small" style="color:#3b3846">Clear programme terms, expiry rules, consent, a ledger that can report points issued, redeemed and expired. No RBI authorisation is expected to be needed for points with no cash value and no cash-out, but get that in writing from counsel.</p></div>
<div class="card"><h4>B. What we need</h4><p class="small" style="color:#3b3846">Pack terms (validity, refund, transfer, expiry), the venue collecting money in its own account, consumer-law review, and a design where the balance can be spent only at that venue. Wait for the final RBI direction before launch.</p></div>
<div class="card"><h4>C. What it would take</h4><p class="small" style="color:#3b3846">RBI authorisation as a prepaid-instrument issuer (reported net worth thresholds of Rs 5 crore rising to Rs 15 crore under the 2026 draft) or a partnership with a licensed bank or issuer. Not a start-up-stage project.</p></div>
</div></section>''')

A('''<section class="sec"><div class="kicker">10 / LEGAL AND MONEY</div><h2>What the law touches, in the order you meet it</h2>
<div class="callout red"><b>Not legal advice.</b> This is research to brief a lawyer and a chartered accountant. Several rules are new or still in draft (RBI PPI draft of 2026, DPDP phase-in). Confirm each item below before relying on it.</div>
<h3>A. The company, tax and name</h3>
<table><thead><tr><th>Item</th><th>What and why</th><th>Rough cost</th></tr></thead><tbody>
<tr><td>Private limited company</td><td>Contracting party for venues, owner of IP, signs data-processing terms. SPICe+ incorporation; MCA fee nil up to Rs 15 lakh authorised capital; stamp duty varies by state.</td><td>Rs 7,000 to 25,000 all-in (sources vary)</td></tr>
<tr><td>GST registration and invoicing</td><td>Our subscription is a taxable service (commonly 18%; confirm with your CA). Issue GST invoices; claim input credit on tools and messaging.</td><td>CA retainer, see section 11</td></tr>
<tr><td>Startup recognition (optional)</td><td>DPIIT recognition can ease some compliances and tax matters; check eligibility with your CA.</td><td>Low</td></tr>
<tr><td>Trademark check on the name</td><td>Search "aikia", "aikia.wallet" and logo before spending on brand. "Wallet" in the name can also draw regulator and customer confusion with payment wallets.</td><td>Search plus filing: verify current government fees; allow professional fees</td></tr>
<tr><td>Founders' agreement, IP assignment</td><td>Everyone who writes code or design signs IP assignment to the company, including contractors and agencies.</td><td>Lawyer time</td></tr>
</tbody></table>
<h3>B. Money: the RBI line</h3>
<ul>
<li><b>Prepaid payment instruments (PPIs)</b> are regulated by the RBI. The 2021 Master Direction treats a "closed system" PPI (usable only to buy the issuer's own goods and services, no cash-out, not usable for third-party payments) as outside the authorisation requirement. Gift instruments were capped at Rs 10,000 and are non-reloadable.</li>
<li><b>Draft 2026 changes (comments were due 22 May 2026; final status not confirmed in this research).</b> The draft reportedly removes the closed-system category but keeps an exemption for PPIs issued by entities that are not marketplaces. Marketplace-issued PPIs would need a licensed issuer. Non-bank applicants would need a net worth of Rs 5 crore, rising to Rs 15 crore.</li>
<li><b>What this means for us.</b> A venue honouring its own pack at its own counter is the safest shape. A wallet balance usable across venues, on a marketplace, or transferable between people moves into licensed territory. Loyalty points with no cash value and no cash-out are generally treated differently from PPIs, but this research did not find RBI text that says so directly: ask counsel for a written view.</li>
<li><b>Payment aggregation.</b> If aikia collected customers' payments for venues and settled to them, it would be acting as a payment aggregator, which the RBI's 2025 directions regulate (authorisation required, with net-worth thresholds of Rs 15 crore at application rising to Rs 25 crore, per press reports). Avoid: let each venue use its own gateway account.</li>
<li><b>Savings and instalment schemes.</b> Jewellers, saree shops and others run "pay monthly, redeem later" schemes. These can fall under rules on unregulated deposits and chit schemes. Do not offer or administer them through the product without counsel.</li>
</ul>
<h3>C. Tax treatment of rewards</h3>
<ul><li>GST on vouchers and gift cards is a developing area: tribunals and advance-ruling bodies have held that tax is levied on the underlying supply at redemption rather than on the voucher itself (for example the Kalyan Jewellers appellate ruling cited in commentary). Reward points were once characterised as actionable claims. The venue's CA should decide treatment; aikia should make the ledger able to report issued, redeemed and expired points by period.</li>
<li>For dealer and channel incentives, TDS on business benefits (Section 194R) can apply to the payer; confirm limits with a CA before building channel loyalty.</li></ul>
</section>''')

A('''<section class="sec"><div class="kicker">10 / LEGAL AND MONEY (CONTINUED)</div><h2>Data, messaging, consumers and security</h2>
<h3>D. Data protection: DPDP Act 2023 and Rules 2025</h3>
<table><thead><tr><th>Topic</th><th>What applies</th><th>What we build or sign</th></tr></thead><tbody>
<tr><td>Timeline</td><td>Rules notified November 2025. Data Protection Board set up at notification; consent-manager registration about 12 months later; core duties (notice, consent, safeguards, breach intimation, children's data, rights) apply about 18 months after notification, around May 2027. Check the Gazette for exact dates.</td><td>Build to the final standard now; do not wait for the date.</td></tr>
<tr><td>Roles</td><td>Each venue decides why and how member data is used, so it is the data fiduciary. aikia, acting on its instructions, is a data processor.</td><td>Data-processing agreement in every venue contract.</td></tr>
<tr><td>Notice and consent</td><td>Plain-language notice; specific, informed, withdrawable consent; the Act allows notice in English or any of the 22 scheduled languages.</td><td>Join page with notice and separate ticks for marketing; consent log; language options.</td></tr>
<tr><td>Rights and grievance</td><td>Access, correction, erasure, grievance redress, nomination.</td><td>Member self-service request page; grievance contact; 30-day internal SLA target.</td></tr>
<tr><td>Security and breach</td><td>Reasonable security safeguards; breach intimation to the Board and affected people. Penalties reported up to Rs 250 crore for safeguard failures and up to Rs 200 crore for breach-notice and children's-data failures (sources differ; verify in the Act's schedule).</td><td>Row-level security, encryption, access logs, tested incident runbook, cyber insurance.</td></tr>
<tr><td>Children</td><td>Under-18: verifiable parental consent; no tracking, behavioural monitoring or targeted ads.</td><td>Parent-first education design (section 07).</td></tr>
<tr><td>Retention</td><td>Erase when purpose ends unless law requires retention.</td><td>Retention schedule per data type; automatic deletion jobs.</td></tr>
</tbody></table>
<h3>E. Messaging</h3>
<ul>
<li><b>SMS:</b> register the company as a principal entity on a telecom operator's DLT platform (one-time fee reported around Rs 5,900), then register sender headers and templates. Unregistered business SMS is blocked.</li>
<li><b>WhatsApp:</b> use an official Business Solution Provider. Meta India rates reported for 2026: about Rs 0.86 per marketing message and Rs 0.115 per utility message, plus provider markup and GST. Templates need approval; opt-in must be recorded. Check Meta's rate card before pricing; it changes.</li>
<li><b>Promotional hours and do-not-disturb:</b> promotional messages are limited by time of day and by the national preference registry. Confirm the current TRAI rules with the SMS provider.</li></ul>
<h3>F. Consumers and advertising</h3>
<ul>
<li>Consumer Protection Act 2019 covers unfair trade practices and misleading advertisements. Programme terms must be clear on earn, expiry, exclusions and change of terms; changing rules after points are earned is a classic dispute.</li>
<li>The Central Consumer Protection Authority's 2023 guidelines on dark patterns apply to consent screens, false urgency and hidden terms. Avoid "only 2 left" style pressure and pre-ticked marketing boxes.</li>
<li>ASCI advertising codes apply to offer claims. A "free" reward must be free of hidden conditions.</li></ul>
<h3>G. Cyber security</h3>
<ul>
<li>CERT-In directions (28 April 2022): report cyber incidents within 6 hours of becoming aware; keep logs for 180 days within India; synchronise clocks to government time sources; name a point of contact.</li>
<li>Run an independent web-application penetration test before the first large customer and yearly. Enterprise and education buyers will ask for the report. ISO 27001 or SOC 2 is a later step.</li></ul>
<h3>H. Sector-specific cautions</h3>
<table><thead><tr><th>Sector</th><th>Caution</th></tr></thead><tbody>
<tr><td>Bars and liquor</td><td>Alcohol promotion rules differ by state; keep alcohol out of rewards and messages unless counsel clears it.</td></tr>
<tr><td>Pharmacies, clinics, dentists, opticians</td><td>Health data is sensitive; medical advertising and inducement rules for professionals are strict; rules on discounts for prescription medicines. No clinical data on the pass.</td></tr>
<tr><td>Jewellery, saree and gold schemes</td><td>Deposit and chit-scheme rules; cash-transaction and KYC duties sit with the shop.</td></tr>
<tr><td>Education</td><td>Children's data, state fee regulation, institution policies (section 07).</td></tr>
<tr><td>Trusts, NGOs, clubs</td><td>Donations raise 80G and FCRA questions; do not process donations.</td></tr>
</tbody></table>
</section>''')

A('''<section class="sec"><div class="kicker">10 / LEGAL AND MONEY (CONTINUED)</div><h2>The documents and the procedure</h2>
<h3>Documents to have before the first paying customer</h3>
<table><thead><tr><th>Document</th><th>Between</th><th>Must cover</th></tr></thead><tbody>
<tr><td>Master subscription agreement</td><td>aikia and venue</td><td>Scope, plans, fees, GST, term, support hours, uptime goals, limits of liability, exit and data return.</td></tr>
<tr><td>Data-processing agreement</td><td>aikia and venue</td><td>Roles, purposes, security measures, sub-processors (cloud, wallet, messaging), breach duties, deletion on exit.</td></tr>
<tr><td>Member privacy notice (template)</td><td>Venue and member</td><td>What is collected, why, who sees it, rights, grievance contact. Languages.</td></tr>
<tr><td>Programme terms (template)</td><td>Venue and member</td><td>Earn rules, expiry, exclusions, changes with notice, fraud, disputes.</td></tr>
<tr><td>Acceptable-use and staff rules</td><td>Venue and its staff</td><td>No self-scanning, no sharing cards, audit trail.</td></tr>
<tr><td>Sub-processor list</td><td>Public page</td><td>Cloud host, wallet engine, messaging providers, analytics.</td></tr>
<tr><td>Wallet platform terms</td><td>aikia and Google / Apple / PassKit</td><td>Read and comply; platforms can change terms or suspend issuers. Keep the engine swappable.</td></tr>
<tr><td>Partner and reseller agreement</td><td>aikia and channel partner</td><td>Commission, territory, data access limits, brand use.</td></tr>
<tr><td>Incident response and breach-notice plan</td><td>Internal</td><td>Who decides, 6-hour CERT-In report, Board and member notices, venue notice.</td></tr>
</tbody></table>
<h3>Procedure, step by step</h3>
<ol>
<li><b>Week 1.</b> Incorporate; open a current account; GST registration; engage a CA and a technology lawyer on retainer.</li>
<li><b>Week 2.</b> Trademark search and filing decision; founders' agreement and IP assignment; domain and brand assets locked.</li>
<li><b>Weeks 2 to 3.</b> Decide the money model (points only) and get counsel's written view on points versus PPI, and on the venue-run pack design for Phase 2.</li>
<li><b>Weeks 3 to 4.</b> Draft the six core documents above; map personal data (what is collected, where it lives, who sees it); decide retention periods.</li>
<li><b>Weeks 4 to 6.</b> DLT registration; WhatsApp provider onboarding and templates; consent screens built and tested; grievance and breach processes written.</li>
<li><b>Before the first customer.</b> Independent security test; backup restore test; cyber insurance quote; pilot venue signs the agreement and DPA.</li>
<li><b>Every quarter.</b> Review regulator updates (RBI PPI final text, DPDP dates, TRAI changes); update documents; re-test breach drill.</li>
<li><b>Every year.</b> Penetration test; sub-processor review; accounts and GST filings; insurance renewal.</li>
</ol>
<div class="callout"><b>Costs of this section</b> are in section 11. The cheapest way to stay safe is to keep money out of the product, keep data minimal, and make every member consent and every ledger entry traceable.</div>
</section>''')

# ================================================================ 11 COSTS
A('''<section class="sec"><div class="kicker">11 / COSTS</div><h2>Cost to build</h2>
<p class="lede">What is still to build, and three ways to deliver it. The existing codebase already covers the core, so these figures are for the remaining work, not a from-scratch build.</p>''')
A(backlog_tbl)
A('<p class="small">Planning cost per dev-equivalent person-month: %s (mid-level engineer; India salary guides show roughly Rs 6 to 10 lakh a year for full-stack developers; a 30-40%% overhead is added). Engineering effort total: %.1f person-months, about %s before design, QA, product and management.</p>' % (D.inr(D.BLENDED_PM), PM, R(DEVCOST)))
A('<h3>Delivery options</h3>')
A(delivery_tbl)
A('''<h3>One-off launch and compliance costs (estimates)</h3>
<table><thead><tr><th>Item</th><th class="n">Estimate</th><th>Basis</th></tr></thead><tbody>
<tr><td>Company incorporation</td><td class="n">Rs 7,000 to 25,000</td><td>Published 2026 guides; state stamp duty varies</td></tr>
<tr><td>Trademark search and filing</td><td class="n">Rs 15,000 to 50,000</td><td>Our estimate incl. professional fees; verify govt fees</td></tr>
<tr><td>Legal drafting: agreements, DPA, privacy, terms</td><td class="n">Rs 75,000 to 2,50,000</td><td>Our estimate; depends on counsel and review depth</td></tr>
<tr><td>Written opinion on points vs PPI and prepaid packs</td><td class="n">Rs 50,000 to 1,50,000</td><td>Our estimate</td></tr>
<tr><td>DLT registration (one-time)</td><td class="n">about Rs 5,900</td><td>Operator platform fee reported by providers</td></tr>
<tr><td>Apple Developer Program</td><td class="n">about Rs 8,700 a year</td><td>Reported by Indian developers; payment can fail in India, plan a workaround</td></tr>
<tr><td>Penetration test (web app + API)</td><td class="n">Rs 50,000 to 2,00,000</td><td>Our estimate; yearly</td></tr>
<tr><td>Brand, pitch deck, sales kit, demo videos</td><td class="n">Rs 50,000 to 1,50,000</td><td>Mostly reuse of existing assets</td></tr>
<tr><td>Cyber insurance (first year)</td><td class="n">Rs 30,000 to 1,50,000</td><td>Our estimate; get quotes</td></tr>
<tr><td>Contingency</td><td class="n">15% of the above</td><td>Prudence</td></tr>
</tbody></table></section>''')

A('<section class="sec"><div class="kicker">11 / COSTS (CONTINUED)</div><h2>Cost to run</h2><p class="lede">Monthly cost at three sizes. Cloud and tool costs are small compared with people, support and compliance.</p>')
A(stage_tbl)
A('''<p class="small">Break-even uses a 70% contribution margin (revenue less messaging, hosting share and per-venue support). It does not include sales commissions or marketing. Growth-stage break-even sits above the stage's own venue count, which tells you something real: the team needed to build integrations and run support costs more than 250 venues can pay for at about Rs 3,500 each, so either price higher, sell more business-tier customers, or keep the team smaller until revenue arrives. The pilot column is an investment stage: with 25 venues it cannot cover its own cost, so it must be funded by founders, the agency or outside money.</p>
<h3>Variable costs you can count on</h3>
<table><thead><tr><th>Cost</th><th>Rate used</th><th>Note</th></tr></thead><tbody>
<tr><td>Cloud database and hosting</td><td>Supabase Pro about US$25 a month plus compute; Vercel Pro about US$20 per seat (third-party figures; verify)</td><td>Converted at Rs 90 per US$ (assumption)</td></tr>
<tr><td>WhatsApp utility message</td><td>About Rs 0.115 + provider markup (assumed Rs 0.25)</td><td>Free inside a 24-hour customer-service window</td></tr>
<tr><td>WhatsApp marketing message</td><td>About Rs 0.86 + markup (assumed Rs 0.25)</td><td>Meta can change rates; check the rate card</td></tr>
<tr><td>SMS (OTP and alerts)</td><td>About Rs 0.10 to 0.18 per SMS; Rs 0.15 used</td><td>After DLT registration</td></tr>
<tr><td>Wallet pass issue and update</td><td>No per-pass fee found for Google's API; PassKit charges by active pass volume</td><td>Confirm Google's current terms; the direct engine is our cost advantage</td></tr>
<tr><td>Hosting share per active member</td><td>Rs 0.15 a month (assumption)</td><td>Database rows, storage, bandwidth</td></tr>
<tr><td>Support time</td><td>Rs 300 per hour (loaded)</td><td>Hours per venue differ by type (below)</td></tr>
<tr><td>Payment gateway for our own subscriptions</td><td>Typically a percentage per transaction; UPI autopay is often cheaper than cards</td><td>Check the gateway's current pricing</td></tr>
</tbody></table></section>''')

A('<section class="sec"><div class="kicker">11 / COSTS (CONTINUED)</div><h2>Cost to serve, by business model</h2><p class="lede">What a typical customer of each kind costs us each month, against a suggested price. Prices are hypotheses to test, set so every type earns at least about 60% gross margin before marketing messages, which are passed through.</p>')
A(archetype_html())
A('''<p class="small">Assumptions per row (active members, new members a month, utility and marketing messages per member a month, support hours) are in the model file <code>data.py</code> and can be changed. Supermarket and college rows assume integration support is billed separately as setup.</p>
<h3>How the cost differs by business model</h3>
<div class="grid2">
<div class="card"><h4>Small venues (cafe, salon, boutique)</h4><p>Cost is mostly support time and a few hundred utility messages. The business case depends on <b>self-serve onboarding</b>: if setup takes a person-day, a Rs 1,499 plan loses money in its first year.</p></div>
<div class="card"><h4>Appointment and capacity venues (gym, court)</h4><p>More utility messages (reminders, check-in), more support. Booking-tool integration lowers staff effort and makes the product stick.</p></div>
<div class="card"><h4>Chains and supermarkets</h4><p>Cost scales with members and messages, not venues. Integration, security review and procurement are the real costs; recover them with setup fees and annual contracts.</p></div>
<div class="card"><h4>Education</h4><p>Moderate message volume, but compliance and relationship work are high. Price per campus per year; budget extra for consent flows, security evidence and onboarding days.</p></div>
</div>
<h3>Where the money is made</h3>
<ul><li>Plan fees: the base.</li><li>Messaging markup: small per message, large at volume.</li><li>Managed programme retainers: high margin per venue, but needs people.</li><li>Setup and integration fees for business and enterprise customers.</li><li>Brand-funded campaigns (FMCG and consumer brands pay to reach members of kirana and retail programmes): possible later, only with member consent.</li></ul>
<div class="callout warn"><b>Check before relying on these figures.</b> Every price and cost here is an estimate. Use them to pick the first price list, then replace them with real quotes (BSP, security tester, lawyer, hosting) and real hours logged during the pilots.</div></section>''')

# ================================================================ 12 OPERATIONS
A('''<section class="sec"><div class="kicker">12 / RUNNING THE SYSTEM</div><h2>Team, operations, support and security</h2>
<h3>Who does what, by stage</h3>
<table><thead><tr><th>Role</th><th>Pilot</th><th>Growth</th><th>Scale</th></tr></thead><tbody>
<tr><td>Founders (product, sales, partners)</td><td>2</td><td>2</td><td>2 (plus heads of function)</td></tr>
<tr><td>Engineering (lead, backend, frontend, integrations)</td><td>1 part-time contract</td><td>1 lead + 2</td><td>6 to 8</td></tr>
<tr><td>Design and product</td><td>Part-time</td><td>1</td><td>2</td></tr>
<tr><td>QA and release</td><td>Founder + automation</td><td>1</td><td>2</td></tr>
<tr><td>Customer success and support</td><td>1 part-time</td><td>2</td><td>6 to 10 (shifts, languages)</td></tr>
<tr><td>Sales and partnerships</td><td>Founders</td><td>1 to 2</td><td>5 to 8</td></tr>
<tr><td>Finance, legal, compliance</td><td>Outsourced CA and lawyer</td><td>Outsourced + part-time</td><td>1 in-house, DPO/grievance officer</td></tr>
</tbody></table>
<div class="grid2">
<div class="card"><h3>Onboarding a venue (target: under one hour)</h3><ol>
<li>Sign agreement and DPA online</li><li>Choose preset; set logo, colours, rewards</li><li>Add staff; send invitations</li>
<li>Print QR poster; test join on a phone</li><li>Staff 15-minute training (video + cheat sheet)</li><li>First-week check-in call; fix issues</li></ol></div>
<div class="card"><h3>Support model</h3><ul>
<li>In-app help and short videos in Hindi, Gujarati, English first</li><li>WhatsApp support line with business-hour SLA</li>
<li>Severity levels: S1 (cannot scan or redeem) responds in 1 hour in business hours</li><li>Weekly review of top tickets; fix root causes, not repeats</li>
<li>Monthly venue health report: scans, members, reward cost, repeat rate</li></ul></div>
<div class="card"><h3>Engineering operations</h3><ul>
<li>Staged releases; automatic tests in CI; rollback plan</li><li>Uptime monitoring and error tracking with alerts to a phone</li>
<li>Daily backups; restore drill every quarter</li><li>Separate staging and production; no real data in staging</li><li>Secrets only in the host's secret store; rotate on staff exit</li></ul></div>
<div class="card"><h3>Fraud and abuse controls</h3><ul>
<li>One-time redemption codes; duplicate-scan window</li><li>Staff action log; alerts on unusual scan patterns</li>
<li>Per-day and per-member limits</li><li>Reversal when a bill is cancelled or returned</li><li>Owner approval for manual adjustments</li></ul></div>
</div>
<h3>Metrics to run the business on</h3>
<table><thead><tr><th>For venues</th><th>For aikia</th></tr></thead><tbody>
<tr><td>Members joined; share of customers enrolled; repeat rate versus before; visits per member; reward cost as share of revenue; reactivation of lapsed members</td><td>Paying venues; monthly recurring revenue; churn; time to go live; support hours per venue; gross margin; message cost per venue; incidents; payback on acquisition cost</td></tr>
</tbody></table>
</section>''')

# ================================================================ 13 MISSED
A('''<section class="sec"><div class="kicker">13 / THINGS YOU MAY HAVE MISSED</div><h2>The unglamorous things that decide success</h2>
<div class="grid2">
<div class="card"><h4>Product</h4><ul>
<li><b>iPhone and no-wallet users.</b> A large share of customers need a fallback; do not launch with Android-only if the venue's customers skew iPhone.</li>
<li><b>Offline scanning.</b> Shop Wi-Fi and mobile data fail. The scanner needs a safe offline queue.</li>
<li><b>Returns, cancellations, voids.</b> Rewards must reverse.</li>
<li><b>Staff turnover.</b> Staff change monthly in cafes and salons; training must be 15 minutes.</li>
<li><b>Language.</b> Hindi, Gujarati, Marathi and others on the join page and staff app.</li>
<li><b>Family and household.</b> Matters for saree, grocery, pharmacy and school.</li>
<li><b>Venue exit.</b> Owners will ask for their data; build export and deletion.</li></ul></div>
<div class="card"><h4>Business model</h4><ul>
<li><b>Reward economics calculator.</b> Many owners over-reward. Show the cost of a reward as a share of sales before they publish it.</li>
<li><b>ROI proof.</b> Renewal depends on a one-page report showing repeat visits up.</li>
<li><b>Points liability.</b> Unredeemed points are a liability the venue's accountant must see; export it monthly.</li>
<li><b>Venue churn and seasonality.</b> Sweets, hotels and sports venues have quiet months; consider seasonal billing.</li>
<li><b>Platform dependency.</b> Google, Apple, Meta or PassKit can change terms. Keep engines and providers swappable.</li>
<li><b>Aggregator terms.</b> Delivery platforms may restrict steering customers off-platform.</li></ul></div>
<div class="card"><h4>Legal and trust</h4><ul>
<li><b>Name risk.</b> "Wallet" may invite RBI-type questions; consider "membership card" in all marketing.</li>
<li><b>Expiry fairness.</b> Hidden or sudden expiry creates disputes and bad press.</li>
<li><b>Consent for messaging.</b> A joined member is not automatically opted in for marketing.</li>
<li><b>Dark-pattern rules.</b> Keep consent screens honest.</li>
<li><b>Contractors' IP.</b> Get assignments signed.</li>
<li><b>Insurance.</b> Cyber and professional indemnity.</li></ul></div>
<div class="card"><h4>Growth and operations</h4><ul>
<li><b>The POS question is the first question every chain asks.</b></li>
<li><b>Partner enablement.</b> Resellers need demo accounts, price lists, training and a lead-sharing rule.</li>
<li><b>Billing the venues.</b> Subscriptions, GST invoices, failed-payment handling, dunning.</li>
<li><b>Venue success management.</b> A monthly call in the first 90 days cuts churn.</li>
<li><b>Data in India.</b> Choose an India region for the database and keep logs in India.</li>
<li><b>Accessibility.</b> Large text and high contrast for the staff and card screens.</li></ul></div>
</div></section>''')

# ================================================================ 14 ROADMAP
A('<section class="sec wide"><div class="kicker">14 / ROADMAP</div>' + C.roadmap_chart() + '''
<div class="grid3" style="margin-top:3mm">
<div class="card"><h4>Months 0 to 3</h4><ul><li>Legal base, DLT, trademark check</li><li>3 pilots: cafe, sweets (RUH), salon or court</li><li>Cafe, bakery, salon presets</li><li>Real-phone Google card test; Apple account started</li><li>Price list v1</li></ul></div>
<div class="card"><h4>Months 3 to 12</h4><ul><li>Billing and plans; self-serve onboarding</li><li>WhatsApp and SMS layer</li><li>POS wave 1; ROI report</li><li>Penetration test; DPDP toolkit</li><li>25 to 100 paying venues</li></ul></div>
<div class="card"><h4>Months 12 to 24</h4><ul><li>Multi-outlet and enterprise pack</li><li>Apple Wallet live</li><li>Campus pilot, then schools</li><li>Partner channel (POS resellers, distributors)</li><li>Venue-run packs, with counsel sign-off</li></ul></div>
</div></section>''')

A('''<section class="sec"><div class="kicker">14 / RISKS AND DECISIONS</div><h2>Risks to manage</h2>
<table><thead><tr><th>Risk</th><th>Why it matters</th><th>Mitigation</th></tr></thead><tbody>
<tr><td>Regulatory drift on stored value</td><td>RBI PPI rules are being redrawn in 2026</td><td>Points only now; counsel opinion before packs; watch RBI notices quarterly</td></tr>
<tr><td>Data breach or misuse</td><td>Penalties are large; trust is the product</td><td>Minimal data; security test; insurance; drilled runbook</td></tr>
<tr><td>Wallet platform changes</td><td>Google or Apple can change terms or limits</td><td>Swappable engines; web-card fallback</td></tr>
<tr><td>Low venue adoption by staff</td><td>If scanning is slow, staff stop</td><td>10-second scan target; training; owner incentives</td></tr>
<tr><td>Small-venue unit economics</td><td>Support time can erase margin</td><td>Self-serve onboarding; partner-led support; higher minimum plan</td></tr>
<tr><td>Integration dependence</td><td>POS vendors can refuse or change APIs</td><td>CSV and webhook fallback; partnerships</td></tr>
<tr><td>Education sales cycle</td><td>Slow decisions drain a small team</td><td>One campus pilot; do not hire ahead of revenue</td></tr>
<tr><td>Founder bandwidth</td><td>Product, sales and compliance at once</td><td>Stage gates; outsource legal and accounts; hire support first</td></tr>
</tbody></table>
<h3>Decisions we need from the founders</h3>
<ol>
<li>Confirm <b>points only</b> as the launch money model.</li>
<li>Choose delivery <b>Option A, B or C</b> and a monthly budget ceiling.</li>
<li>Pick the <b>three pilot venues</b> and the first campus.</li>
<li>Set the <b>first price list</b> (Starter, Growth, Business) to test.</li>
<li>Name the <b>owner for legal and compliance</b> (a founder plus outside counsel and a CA).</li>
<li>Decide whether to start the <b>Apple Developer account</b> now.</li>
<li>Decide the <b>brand language</b>: "wallet" or "membership card".</li>
</ol>
<h3>What this research did not settle</h3>
<ul>
<li>Final text of the RBI PPI Master Direction after the 2026 draft; whether points fall outside it, in writing.</li>
<li>Exact current TRAI rules for promotional messaging, and Meta's current India rate card.</li>
<li>Google Wallet's current terms on fees, message limits and issuer approval in India.</li>
<li>Competitor features and prices beyond a single comparison page.</li>
<li>Official counts of restaurants, salons and retail outlets (sources are estimates).</li>
<li>Whether our assumed prices will be accepted by venues; the pilots decide.</li></ul></section>''')

A('<section class="sec"><div class="kicker">SOURCES</div><h2>Sources consulted</h2><p class="small">Accessed October 2026. Many are consultancy, vendor or news pages; they inform planning and are not authoritative legal text. Check the primary source (RBI, MeitY, Gazette, Meta, Google, Apple) before acting.</p><ol class="srclist">')
for t, u in SOURCES:
    A('<li>%s<br><a href="%s">%s</a></li>' % (e(t), e(u), e(u)))
A('</ol></section></body></html>')

open(OUT_HTML, "w", encoding="utf-8").write("".join(html))
print("html written", len("".join(html)))

os.makedirs(os.path.dirname(OUT_PDF), exist_ok=True)
cmd = [EDGE, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--print-to-pdf=" + os.path.abspath(OUT_PDF), "file:///" + OUT_HTML.replace("\\", "/")]
r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
print("edge rc", r.returncode, r.stderr[-300:])
print(os.path.exists(OUT_PDF) and os.path.getsize(OUT_PDF))
