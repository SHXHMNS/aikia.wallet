# -*- coding: utf-8 -*-
"""Data + cost model for the AIKIA.WALLET founder playbook. All money in INR unless stated."""

# ----------------------------------------------------------------------------------------
# 1. Business types, grouped in clusters
#    (name, what counts, reward mechanics, standout modules, watch-outs, wave)
# ----------------------------------------------------------------------------------------
CLUSTERS = [
 ("Food and beverage", "Highest repeat frequency; fastest sales cycle; many already use a POS.", [
  ("Cafes, tea and coffee shops", "Each purchase or visit", "Stamp card (buy 9, 10th free); points per rupee; happy-hour multipliers; optional venue-run prepaid credit", "Stamps, tiers, birthday, geofence nudge, QR poster join", "Staff scan speed at peak; fake stamps; free-item cost", 1),
  ("QSR and restaurant chains (multi-outlet)", "Bill value, per outlet", "Points per rupee with cross-outlet earn and burn; spend tiers; family-combo and birthday offers", "Multi-outlet roll-up, POS integration, tiers, WhatsApp, campaign calendar", "POS integration is the gate; franchise vs company-owned outlets need separate rules; dine-in vs delivery", 1),
  ("Fine dining, bars and lounges", "Bill value, visits", "Invite-only tiers, priority tables, event access, anniversary offers", "Tiers, reservation link, event passes, anniversary reminders", "Alcohol: advertising and promotion rules differ by state. Keep alcohol out of rewards and messages unless counsel clears it", 2),
  ("Sweets, bakeries and namkeen", "Bill value; festival orders", "Points per rupee; festival-season bonus; reorder reminder; corporate and bulk-order tier", "Festival campaigns, gifting codes, reorder reminders, pre-order link", "Strongly seasonal (Diwali, Raksha Bandhan); perishable rewards; gift cards need clear expiry", 1),
  ("Ice cream, juice, dessert and cloud kitchens", "Each order", "Stamp card; free add-on; direct-order incentive to reduce aggregator dependence", "Stamps, direct-order link, WhatsApp reorder", "Aggregator terms may bar steering customers off-platform; read each platform's rules", 1),
 ]),
 ("Fashion, lifestyle and gifting retail", "Higher ticket, lower frequency: loyalty is about occasions, family and recognition.", [
  ("Clothing and boutique stores", "Bill value", "Spend tiers (Silver, Gold, Black); early access to new arrivals; birthday credit; referral reward", "Tiers, birthday and anniversary, referral, size and preference notes, return reversal", "Returns and exchanges must reverse points; discount-hunting members; outlet-level stock", 2),
  ("Saree shops and ethnic wear", "Bill value; occasions (wedding, festival)", "Family account (mother, daughter, in-laws); occasion reminders; spend tiers; private-preview invitations", "Family and household link, occasion calendar, referral, WhatsApp, invoice vault", "Monthly instalment or advance-savings schemes are a regulated area (see Legal). Do not hold member money without counsel", 2),
  ("Jewellery", "Bill value; occasions", "Tiers; making-charge benefits; occasion reminders; trade-in and upgrade offers", "Tiers, occasion calendar, invoice vault, family link", "Gold savings schemes drew regulatory attention in India. Cash-transaction limits and KYC are the jeweller's duty. Do not run schemes through the wallet", 3),
  ("Footwear, bags, accessories, gift shops", "Bill value", "Points per rupee; seasonal bonus; birthday offer", "Points, tiers, referral, geofence", "Low frequency: use occasion and season triggers instead of pure points", 2),
 ]),
 ("Electronics, appliances and durables", "Low frequency, high ticket: the value is lifecycle, warranty and the next purchase.", [
  ("Electronics and appliance stores (Croma-type)", "Bill value; product registration", "Warranty vault on the pass; service and AMC reminders; exchange and upgrade bonus; accessory points; brand-funded offers", "Document vault, lifecycle reminders, brand-funded offers, multi-outlet, ERP/POS integration", "Needs ERP/POS integration; brand co-funding contracts; serial-number data. Enterprise sales cycle", 3),
  ("Mobile and accessories shops", "Bill value; service visits", "Points on accessories; repair-status link; upgrade reminders", "Points, service reminder, referral", "Thin margins; counterfeit-accessory trust issues; keep claims factual", 2),
 ]),
 ("Grocery, supermarkets and pharmacies", "Highest transaction volume; value comes from basket-building and targeted offers.", [
  ("Supermarkets and hypermarket chains (DMart, Reliance Fresh type)", "Basket value; category mix", "Targeted coupons by behaviour; paid-membership perks; brand-funded offers; household account", "ERP/POS integration, household link, brand-funded offers, multi-store roll-up, analytics", "Everyday-low-price formats have thin margins: use targeted offers, not blanket points. Needs enterprise integration, security review and procurement", 3),
  ("Kirana and neighbourhood stores", "Each purchase", "Stamp card; home-delivery reorder via WhatsApp; brand-funded scheme points", "Stamps, WhatsApp reorder, brand-funded offers, very low price point", "Very price-sensitive; tiny staff training budget; best reached through distributors and FMCG brands, not direct sales", 3),
  ("Pharmacies and wellness stores", "Bill value; refill cycle", "Refill reminders; family account; points on wellness and OTC; brand-funded offers", "Household link, refill reminders, multi-outlet, POS integration", "Health data is sensitive: keep it off the pass. Rules on discounts and inducements for prescription medicines: confirm with counsel", 3),
 ]),
 ("Health, beauty and wellness", "Appointment-led repeat visits and prepaid packages.", [
  ("Salons, barbers, spas and nail studios", "Completed visit or service", "Visit-count reward; service packages with validity; rebook prompt; referral; stylist-wise preference", "Stamps, packs (venue-run), rebook link, referral, birthday, validity and renewal", "Count only completed appointments; prepaid package expiry must be disclosed; no treatment details on the lock screen", 1),
  ("Gyms, yoga and fitness studios", "Attendance (check-in)", "Attendance streaks; renewal reminders; referral; class packs; membership freeze and pause", "Check-in, validity and renewal, streaks, referral, geofence", "Membership billing stays in the gym's system; refunds and freezes need clear terms", 2),
  ("Clinics, dental, diagnostics and optical", "Completed visit; recall date", "Recall reminders (6-month check-up); family account; referral where permitted", "Household link, recall reminders, appointment link", "Medical advertising and inducement rules for doctors and clinics are strict. Never store clinical data in the wallet. Counsel review before launch", 3),
 ]),
 ("Auto and home services", "Service-interval businesses where the reminder is the product.", [
  ("Car wash, garages and two-wheeler service", "Completed service", "Wash packs (venue-run); service-interval reminders; referral; loyalty stamps", "Packs, service history, reminders, referral", "Prepaid packs need expiry and refund terms; keep vehicle data minimal", 2),
  ("Laundry, dry cleaning, tailors and repair", "Each order", "Stamp card; pickup reminders; prepaid order bundles", "Stamps, packs, WhatsApp pickup alerts", "Garment-loss disputes sit outside the wallet; keep terms clear", 2),
  ("Pet shops, vets and grooming; florists; bookshops", "Each purchase or visit", "Stamps and points; birthday (pet or person); refill and re-order reminders", "Stamps, occasions, reminders", "Small ticket, small budget: keep setup under one hour", 2),
 ]),
 ("Hospitality, sport and entertainment", "Bookings, groups and off-peak capacity.", [
  ("Hotels, resorts and homestays", "Completed stay or direct booking", "Stay-based tiers; direct-booking benefits (to reduce OTA commission); late check-out and upgrade perks", "Tiers, direct-booking link, check-in, multi-property roll-up", "Booking and payment stay in the booking engine; guest ID data is sensitive", 2),
  ("Turf, pickleball, padel and badminton venues", "Attended session", "Session packs; off-peak bonus; league tiers; team and captain referral", "Check-in, packs, validity, referral, booking link", "Booking system owns slots and payment; cancellations must not earn rewards (see the Vertical Expansion Blueprint)", 1),
  ("Gaming parlours, bowling, trampoline parks, cinemas", "Visit or ticket", "Visit stamps; group offers; birthday-party benefits; off-peak passes", "Stamps, packs, birthday, geofence, multi-site", "Ticketing and timed entry are a separate system; minors need parental consent", 2),
 ]),
 ("Education", "Not 'points for spending' but identity, attendance, engagement and a campus economy. Longer sales cycles and stricter data rules (minors).", [
  ("Schools (K-12)", "Attendance, reading, activities, on-time actions", "Non-monetary badges and house points; digital student and parent pass; canteen or stationery credit run by the school; event and PTM reminders", "Student and parent profile, parental consent, attendance check-in, notices, multi-branch", "Under-18 data needs verifiable parental consent; no tracking, behavioural monitoring or targeted advertising to children; fee rules differ by state", 3),
  ("Colleges and universities", "Attendance, events, campus spend, placement milestones", "Digital campus ID; library and hostel pass; fest and event tickets; campus-merchant discount network; alumni membership", "Student profile, campus coalition, event passes, check-in, validity", "Coalition with merchants adds liability and GST questions; many students are 18+ but some are not; institution is the data fiduciary", 3),
  ("Coaching, tuition, music, dance and hobby classes", "Class attendance", "Attendance streaks; renewal reminders; sibling and referral benefits; batch reminders", "Check-in, validity and renewal, referral, parent profile", "Fee collection stays with the institute; reminders only. Parents are the consent-givers for minors", 2),
 ]),
 ("Adjacent opportunities (later)", "Reachable once the core is proven; each needs its own product and legal design.", [
  ("Malls, markets and city coalitions", "Spend across member merchants", "Shared points across merchants; mall-level tiers", "Coalition ledger, settlement between merchants, shared analytics", "Cross-merchant redemption creates settlement, GST and liability questions. Design after the single-venue product is stable", 3),
  ("Dealer and channel loyalty (electricians, painters, distributors)", "Product or invoice scan", "Points per scan or invoice; tier rewards; brand-funded incentives", "Brand console, scan-per-pack, KYC, payout", "TDS on business benefits (Section 194R) and payout rules apply; a different product from consumer loyalty", 3),
  ("Clubs, societies, trusts and event organisers", "Membership, attendance", "Membership pass, renewal, event entry", "Validity, check-in, member directory", "Donations and trusts have their own rules (80G, FCRA); do not process donations without counsel", 3),
 ]),
]

# ----------------------------------------------------------------------------------------
# 2. Customisation matrix: rows = archetypes, columns = modules. 2=core, 1=optional, 0=not used
# ----------------------------------------------------------------------------------------
MODULES = ["Points per rupee", "Visit stamps", "Spend tiers", "Prepaid packs (venue-run)", "Appointment / booking link",
           "Membership validity + renewal", "Family / household", "Student / parent profile", "Referral",
           "Birthday + occasions", "Multi-outlet roll-up", "POS / ERP integration", "Geofence + wallet alerts",
           "WhatsApp / SMS", "Document / warranty vault", "Check-in / attendance", "Brand-funded offers"]

MATRIX = [
 ("Food and beverage", None),
 ("Cafe / tea shop",            [1,2,1,1,0,0,0,0,1,2,1,1,2,2,0,0,0]),
 ("QSR / restaurant chain",     [2,1,2,1,0,0,1,0,1,2,2,2,2,2,0,0,1]),
 ("Sweets / bakery",            [2,1,1,1,0,0,1,0,1,2,1,1,1,2,0,0,0]),
 ("Fashion and gifting", None),
 ("Clothing / boutique",        [2,0,2,0,0,0,1,0,2,2,1,2,1,2,0,0,0]),
 ("Saree / jewellery",          [1,0,2,0,0,0,2,0,2,2,1,1,1,2,1,0,0]),
 ("Electronics and grocery", None),
 ("Electronics / appliances",   [1,0,1,0,0,1,1,0,1,0,2,2,1,2,2,0,2]),
 ("Supermarket chain",          [2,0,1,0,0,1,2,0,1,1,2,2,2,2,0,0,2]),
 ("Kirana store",               [1,2,0,0,0,0,2,0,1,0,0,0,0,2,0,0,2]),
 ("Pharmacy",                   [1,0,0,0,0,1,2,0,1,0,2,2,1,2,0,0,2]),
 ("Health and services", None),
 ("Salon / spa",                [1,2,1,2,2,2,1,0,2,2,1,1,1,2,0,0,0]),
 ("Gym / yoga studio",          [0,1,1,1,1,2,1,0,2,1,1,1,2,2,0,2,0]),
 ("Clinic / dental / optical",  [0,0,0,0,2,1,2,0,1,1,1,0,0,2,1,1,0]),
 ("Car wash / garage",          [1,2,1,2,2,1,0,0,2,0,1,1,1,2,1,0,1]),
 ("Hospitality and sport", None),
 ("Hotel / homestay",           [2,0,2,0,1,1,1,0,1,2,2,1,2,2,0,1,1]),
 ("Turf / pickleball / courts", [0,2,1,2,2,2,0,0,2,1,1,1,1,2,0,2,0]),
 ("Gaming / bowling / cinema",  [1,2,1,2,1,1,1,0,1,2,2,1,2,2,0,1,1]),
 ("Education", None),
 ("School (K-12)",              [0,1,0,1,1,1,2,2,0,1,2,1,1,2,0,2,1]),
 ("College / university",       [1,1,1,1,0,2,0,2,1,0,2,1,2,2,1,2,2]),
 ("Coaching / hobby classes",   [0,2,0,1,1,2,1,2,2,1,2,1,0,2,0,2,0]),
 ("Channel", None),
 ("Dealer / channel loyalty",   [2,0,2,0,0,0,0,0,1,0,2,1,0,2,0,0,2]),
]

# ----------------------------------------------------------------------------------------
# 3. Cost model
# ----------------------------------------------------------------------------------------
USD_INR = 90.0           # planning assumption, not a quote
WA_UTILITY = 0.115       # Meta India utility message, per message, ex-GST (third-party sources, Jan 2026)
WA_MARKETING = 0.8631    # Meta India marketing message, ex-GST
BSP_MARKUP = 0.25        # assumed BSP markup per message
SMS_OTP = 0.15           # mid of 0.10-0.18 transactional
HOSTING_PER_MEMBER = 0.15  # assumed share of DB, compute, storage, egress per active member per month
SUPPORT_RATE = 300.0     # INR per support hour (loaded)
PASS_MARGIN = 1.30       # billed marketing messages at cost +30%

# archetype: (label, active members, new members/mo, utility msgs/member/mo, marketing msgs/member/mo, support hrs/mo, price/mo)
ARCHETYPES = [
 ("Cafe, 1 outlet",               400,   60, 1.0, 1.0, 1.0,  1499),
 ("Salon / spa, 1 outlet",        300,   40, 1.5, 1.0, 1.0,  1999),
 ("Boutique / saree shop",        800,   60, 0.5, 1.0, 1.0,  2499),
 ("Gym or sports venue",          500,   50, 3.0, 1.0, 1.5,  2999),
 ("Restaurant chain, 5 outlets", 3000,  400, 1.0, 2.0, 4.0,  9999),
 ("School, 1 campus (about 1,000 parents)", 1000, 100, 4.0, 0.5, 5.0, 15000),
 ("College, 5,000 students",     5000,  400, 3.0, 1.0, 8.0, 40000),
 ("Supermarket chain, 20 stores", 40000, 4000, 2.0, 3.0, 25.0, 150000),
]

def archetype_rows():
    rows = []
    for label, m, n, u, k, hrs, price in ARCHETYPES:
        util = m * u * (WA_UTILITY + BSP_MARKUP)
        otp = n * SMS_OTP
        host = m * HOSTING_PER_MEMBER
        sup = hrs * SUPPORT_RATE
        platform_cost = util + otp + host + sup
        mkt_cost = m * k * (WA_MARKETING + BSP_MARKUP)
        mkt_bill = mkt_cost * PASS_MARGIN
        gm = (price - platform_cost) / price
        rows.append(dict(label=label, members=m, price=price, platform_cost=platform_cost,
                         mkt_cost=mkt_cost, mkt_bill=mkt_bill, gm=gm,
                         util=util, otp=otp, host=host, sup=sup))
    return rows

# --- One-off build backlog (person-months of mid-level dev-equivalent effort) ---
BACKLOG = [
 ("Multi-tenant billing: plans, limits, subscriptions, invoices",            2.0),
 ("Rules engine v2: points per rupee, stamps, expiry, tiers, offer templates", 2.5),
 ("Vertical presets and self-serve onboarding wizard",                        1.5),
 ("Staff scanner: offline mode, fraud and duplicate-scan controls",           2.0),
 ("Integrations wave 1: three POS systems, Shopify, one booking tool, CSV",   3.0),
 ("Apple Wallet adapter and Android/iOS parity",                              1.0),
 ("Messaging: WhatsApp BSP, SMS with DLT, opt-in, quiet hours",               2.0),
 ("Analytics: repeat rate, reward cost, ROI report, exports",                 1.5),
 ("Multi-outlet and franchise hierarchy with roll-ups",                       1.5),
 ("Education module: student and parent profiles, parental consent, campus partners", 2.5),
 ("Venue-run prepaid packs (ledger only, never holds money) + liability report", 1.5),
 ("DPDP toolkit: notices, consent records, access and erasure, retention, breach log", 1.5),
 ("Platform console, support tools, audited impersonation",                   1.0),
 ("QA automation, load tests, security fixes",                                1.5),
 ("Localisation: Hindi, Gujarati, Marathi first",                             0.8),
]
BLENDED_PM = 95000       # INR cost per dev-equivalent person-month incl. overhead (planning figure)

def backlog_total():
    pm = sum(x[1] for x in BACKLOG)
    return pm, pm * BLENDED_PM

# --- Delivery options (months, monthly team cost, other one-offs) ---
def delivery_options():
    pm, dev_cost = backlog_total()
    opts = []
    # A: founder-led with AI tools + 1 contract dev + part-time designer
    a_monthly = 95000 + 35000 + 25000          # contract dev, part-time designer, part-time QA
    a_months = 9
    opts.append(dict(name="A. Founder-led + AI tools + 1 contract developer",
                     months=a_months, team="1 contract dev, part-time designer and QA, founders direct and sell",
                     build=a_monthly * a_months, note="Slowest, cheapest. Founders carry product, support and sales."))
    # B: small team
    b_monthly = 160000 + 2 * 95000 + 70000 + 55000 + 70000   # lead, 2 dev, designer, QA, product/ops
    b_months = 8
    opts.append(dict(name="B. Small in-house team (recommended)",
                     months=b_months, team="1 tech lead, 2 developers, 1 designer, 1 QA, 1 product/ops",
                     build=b_monthly * b_months, note="Ships the whole backlog; keeps the codebase and know-how in-house."))
    # C: agency
    c_total = dev_cost * 1.8
    opts.append(dict(name="C. Outsource to an agency",
                     months=7, team="Agency squad (PM, 3-4 engineers, QA, design)",
                     build=c_total, note="Fast start, higher cost, weaker ownership. Needs a strict spec and IP assignment."))
    return opts, pm, dev_cost

# --- Stage-wise monthly run cost ---
STAGES = [
 # name, venues, members, cloud, tooling, comms_infra, security, legal_acct, team_monthly, arpa
 ("Pilot",  "up to 25 venues, about 10k members",  25,  10000,  8000,  5000,  5000,  25000,  60000 + 95000 + 45000, 1800),
 ("Growth", "up to 250 venues, about 150k members", 250, 60000, 40000, 30000, 40000,  80000,  160000 + 2*95000 + 70000 + 55000 + 70000 + 2*45000 + 60000, 3500),
 ("Scale",  "up to 2,000 venues, about 1.5M members", 2000, 500000, 150000, 150000, 150000, 300000, 2600000, 5000),
]
GROSS_MARGIN = 0.70   # contribution margin after message and per-venue support costs

def stage_rows():
    out = []
    for name, desc, venues, cloud, tool, comms, sec, legal, team, arpa in STAGES:
        total = cloud + tool + comms + sec + legal + team
        contrib = arpa * GROSS_MARGIN
        be = total / contrib
        revenue_at_cap = venues * arpa
        out.append(dict(name=name, desc=desc, venues=venues, cloud=cloud, tool=tool, comms=comms,
                        sec=sec, legal=legal, team=team, total=total, arpa=arpa,
                        breakeven=be, rev=revenue_at_cap, contrib_at_cap=revenue_at_cap * GROSS_MARGIN))
    return out

def inr(x, short=False):
    """Indian digit grouping; short -> lakh / crore."""
    x = float(x)
    if short:
        if abs(x) >= 1e7: return "Rs %.2f cr" % (x / 1e7)
        if abs(x) >= 1e5: return "Rs %.1f lakh" % (x / 1e5)
        return "Rs {:,.0f}".format(x)
    s = "{:.0f}".format(abs(x))
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:]); head = head[:-2]
        if head: parts.insert(0, head)
        s = ",".join(parts + [tail])
    return "Rs " + ("-" if x < 0 else "") + s

if __name__ == "__main__":
    for r in archetype_rows():
        print(r["label"], round(r["platform_cost"]), round(r["mkt_cost"]), round(r["gm"] * 100))
    print(backlog_total())
    o, pm, dc = delivery_options()
    for x in o: print(x["name"], x["months"], inr(x["build"], True))
    for s in stage_rows(): print(s["name"], inr(s["total"], True), round(s["breakeven"]))
