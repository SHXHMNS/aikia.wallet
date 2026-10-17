# -*- coding: utf-8 -*-
"""Budget model for AIKIA.WALLET: Scope A (2-3 business types, 12 months) and Scope B (all 29 types, 24 months).
All money in INR. Every figure is a planning estimate built from the assumptions below."""
import data as D

# ---------------- assumptions ----------------
RATE_PARTNER = 70000     # engineering person-month at a negotiated rate with a long-standing partner company (ASSUMPTION)
RATE_MARKET = 95000      # mid-level engineering person-month at market (from India salary guides + overhead)
LOAD = 1.45              # uplift for design, QA, project management and partner margin on engineering cost
CONTINGENCY = 0.15
COMMISSION = 0.15        # partner/reseller commission on first-year revenue (ASSUMPTION)

def loaded(rate): return rate * LOAD

# ---------------- shared platform work packages: (name, pm in Scope A, pm in Scope B) ----------------
SHARED = [
 ("Multi-tenant billing: plans, limits, subscriptions, GST invoices",        1.2, 2.0),
 ("Rules engine v2: points, stamps, expiry, tiers, offer templates",        1.5, 2.5),
 ("Vertical presets and self-serve onboarding wizard",                      0.8, 1.5),
 ("Staff scanner: offline mode, fraud and duplicate-scan controls",         1.5, 2.0),
 ("Integrations: CSV + one POS (A); three POS + Shopify + booking (B wave 1)", 1.5, 3.0),
 ("Integrations wave 2: further POS, ERP and booking tools",                0.0, 4.0),
 ("Apple Wallet adapter and Android / iOS parity",                          1.0, 1.0),
 ("Messaging: WhatsApp provider, SMS with DLT, opt-in, quiet hours",        1.5, 2.0),
 ("Analytics and ROI report; exports",                                      1.0, 1.5),
 ("Advanced analytics and dashboards for chains",                           0.0, 2.0),
 ("Multi-outlet and franchise hierarchy",                                   0.0, 1.5),
 ("Referral engine",                                                        0.5, 0.8),
 ("DPDP toolkit: notices, consent records, access and erasure, retention",  1.0, 1.5),
 ("Platform console, support tools, audited impersonation",                 0.5, 1.0),
 ("More operations tooling: health checks, alerts, admin automation",       0.0, 1.5),
 ("QA automation, load tests, security fixes",                              1.0, 1.5),
 ("Performance and scale engineering (for 1M+ members)",                    0.0, 3.0),
 ("Localisation: Hindi, Gujarati, Marathi (A: Hindi + Gujarati)",           0.5, 0.8),
 ("Localisation: further regional languages",                               0.0, 1.5),
 ("Family / household accounts",                                            0.0, 1.0),
 ("Document and warranty vault",                                            0.0, 1.0),
 ("Brand-funded offers module",                                             0.0, 2.0),
 ("Enterprise pack: single sign-on, API, audit export, SLA tooling",        0.0, 2.5),
 ("Education module: student and parent profiles, parental consent",        0.0, 2.5),
 ("Venue-run prepaid packs (ledger only) and liability report",             0.0, 1.5),
 ("Security and audit readiness work (ISO 27001 / SOC 2 evidence)",         0.0, 2.0),
]

def shared_totals():
    a = sum(x[1] for x in SHARED); b = sum(x[2] for x in SHARED)
    return a, b

# ---------------- per business type launch items ----------------
# name: dict(int=integration pm, spec=special build pm, legal=Rs, sales=Rs, train=Rs, pilot=Rs, sec=Rs)
DEF = dict(int=0.0, spec=0.0, legal=15000, sales=30000, train=20000, pilot=15000, sec=0)
PRESET_PM = 0.3
OV = {
 "QSR and restaurant chains (multi-outlet)": dict(int=1.5, pilot=30000),
 "Fine dining, bars and lounges": dict(legal=60000),
 "Sweets, bakeries and namkeen": dict(sales=40000),
 "Clothing and boutique stores": dict(int=1.0),
 "Saree shops and ethnic wear": dict(spec=0.8, legal=50000),
 "Jewellery": dict(spec=0.5, legal=75000),
 "Electronics and appliance stores (Croma-type)": dict(int=2.0, spec=1.0, legal=40000, sec=100000, pilot=40000),
 "Mobile and accessories shops": dict(int=0.5),
 "Supermarkets and hypermarket chains (DMart, Reliance Fresh type)": dict(int=3.0, spec=2.0, legal=60000, sec=150000, pilot=60000, sales=60000),
 "Kirana and neighbourhood stores": dict(spec=1.0, legal=25000, sales=40000, pilot=40000),
 "Pharmacies and wellness stores": dict(int=1.5, legal=75000),
 "Salons, barbers, spas and nail studios": dict(int=0.5, spec=1.0, legal=40000),
 "Gyms, yoga and fitness studios": dict(int=1.0, spec=0.5),
 "Clinics, dental, diagnostics and optical": dict(int=0.5, spec=0.5, legal=90000),
 "Car wash, garages and two-wheeler service": dict(spec=0.5, legal=20000),
 "Laundry, dry cleaning, tailors and repair": dict(spec=0.3),
 "Hotels, resorts and homestays": dict(int=1.5, legal=30000),
 "Turf, pickleball, padel and badminton venues": dict(int=1.0, spec=0.5, legal=25000),
 "Gaming parlours, bowling, trampoline parks, cinemas": dict(int=0.5, spec=0.3, legal=40000),
 "Schools (K-12)": dict(int=1.5, legal=150000, sec=150000, pilot=50000, sales=50000),
 "Colleges and universities": dict(int=1.5, spec=1.0, legal=100000, sec=150000, pilot=50000, sales=50000),
 "Coaching, tuition, music, dance and hobby classes": dict(int=0.5, legal=50000),
 "Malls, markets and city coalitions": dict(int=2.0, spec=4.0, legal=250000, sec=100000, pilot=60000, sales=50000),
 "Dealer and channel loyalty (electricians, painters, distributors)": dict(int=1.0, spec=4.0, legal=200000, sec=100000),
 "Clubs, societies, trusts and event organisers": dict(spec=1.0, legal=100000),
}
def type_params(name):
    p = dict(DEF); p.update(OV.get(name, {})); return p

def short(name):
    return name.split(" (")[0]

def type_cost(name, rate=RATE_PARTNER):
    p = type_params(name)
    pm = PRESET_PM + p["int"] + p["spec"]
    eng = pm * loaded(rate)
    other = p["legal"] + p["sales"] + p["train"] + p["pilot"] + p["sec"]
    return dict(pm=pm, eng=eng, legal=p["legal"], sales=p["sales"], train=p["train"], pilot=p["pilot"], sec=p["sec"], other=other, total=eng + other, int=p["int"], spec=p["spec"])

def all_type_names():
    return [(ci, cname, r[0], r[5]) for ci, (cname, why, rows) in enumerate(D.CLUSTERS, 1) for r in rows]

SCOPE_A_TYPES2 = ["Cafes, tea and coffee shops", "Sweets, bakeries and namkeen"]
SCOPE_A_TYPES3 = SCOPE_A_TYPES2 + ["Salons, barbers, spas and nail studios"]

# ---------------- one-time costs (mid of ranges used in the Founder Playbook) ----------------
ONE_A = [
 ("Company set-up and first compliance (incorporation, GST)", 15000),
 ("Agreements, DPA, privacy notice, programme terms (lawyer)", 125000),
 ("Written opinion on points vs prepaid rules and venue-run packs", 100000),
 ("Trademark search and filing (1 class)", 30000),
 ("DLT registration (SMS)", 5900),
 ("Apple Developer Program (first year)", 8700),
 ("Penetration test, web app + API", 125000),
 ("Cyber insurance, first year", 80000),
 ("Brand, pitch deck, sales kit, demo video (shared)", 100000),
 ("Demo devices, QR stands, printing", 40000),
]
ONE_B_EXTRA = [
 ("Additional trademark classes and logo marks", 60000),
 ("Second penetration test and yearly retest", 125000),
 ("ISO 27001 or SOC 2 audit and certification (year 2)", 400000),
 ("Partner programme kit: price lists, demo accounts, training", 150000),
 ("Brand refresh and website expansion", 200000),
 ("Statutory audit, ROC filings, tax returns (annual)", 60000),
 ("Recruitment fees for hires (about 8% of annual pay)", 250000),
 ("Laptops and equipment for hires", 250000),
]

# ---------------- run costs ----------------
INFRA_PILOT = dict(cloud=10000, tool=8000, comms=5000, sec=5000, legal=25000)
INFRA_GROWTH = dict(cloud=60000, tool=40000, comms=30000, sec=40000, legal=80000)
def infra_mid():
    return {k: (INFRA_PILOT[k] + INFRA_GROWTH[k]) / 2 for k in INFRA_PILOT}

def venues_A():     return [3, 8, 15, 25]
def venues_B():     return [3, 10, 25, 60, 120, 200, 300, 400]
def arpa_A():       return [1800] * 4
def arpa_B():       return [1800, 1800, 2500, 2500, 3500, 3500, 3500, 3500]

def avg_venues(v):
    out, prev = [], 0
    for x in v:
        out.append((prev + x) / 2.0); prev = x
    return out

def scope_A(rate=RATE_PARTNER, vmult=1.0, delay=0, types=SCOPE_A_TYPES3):
    q = 4
    loadr = loaded(rate)
    shared_pm = sum(x[1] for x in SHARED)
    build_shared = shared_pm * loadr
    tc = [type_cost(t, rate) for t in types]
    build_types = sum(x["eng"] for x in tc)
    build_total = build_shared + build_types
    type_other = sum(x["other"] for x in tc)
    one_total = sum(x[1] for x in ONE_A) + type_other
    build_q = [0.5 * build_total, 0.5 * build_total, 0, 0]
    one_q = [0.6 * one_total, 0.2 * one_total, 0.2 * one_total, 0]
    infra_m = sum(INFRA_PILOT.values())
    support_m = [0, 45000, 45000, 45000]
    sales_m = [30000] * 4
    maint_m = [0, 0, 0.5 * loadr, 0.5 * loadr]
    vv = [x * vmult for x in venues_A()]
    av = avg_venues(vv)
    if delay:
        av = [0] * delay + av[:q - delay]
    rev = [av[i] * arpa_A()[i] * 3 for i in range(q)]
    comm = [COMMISSION * r for r in rev]
    rows = []
    for i in range(q):
        run = 3 * (infra_m + support_m[i] + sales_m[i] + maint_m[i])
        sub = build_q[i] + one_q[i] + run + comm[i]
        cont = CONTINGENCY * (build_q[i] + one_q[i] + run)
        cost = sub + cont
        rows.append(dict(q=i + 1, build=build_q[i], one=one_q[i], run=run, comm=comm[i], cont=cont, cost=cost, rev=rev[i], venues=vv[i]))
    return finish(rows, dict(build_shared=build_shared, build_types=build_types, build_total=build_total, one_total=one_total, tc=tc, shared_pm=shared_pm, types=types))

def scope_B(rate=RATE_PARTNER, vmult=1.0, delay=0):
    q = 8
    loadr = loaded(rate)
    shared_pm = sum(x[2] for x in SHARED)
    build_shared = shared_pm * loadr
    names = [t[2] for t in all_type_names()]
    tc = [type_cost(t, rate) for t in names]
    build_types = sum(x["eng"] for x in tc)
    build_total = build_shared + build_types
    type_other = sum(x["other"] for x in tc)
    one_total = sum(x[1] for x in ONE_A) + sum(x[1] for x in ONE_B_EXTRA) + type_other
    # spend shapes
    shared_shape = [.15, .15, .15, .15, .10, .10, .10, .10]
    type_shape = [0, 0, .15, .20, .20, .20, .15, .10]
    build_q = [build_shared * shared_shape[i] + build_types * type_shape[i] for i in range(q)]
    one_shape = [.30, .10, .12, .10, .08, .12, .08, .10]
    one_q = [one_total * s for s in one_shape]
    im = infra_mid()
    infra_m = [sum(INFRA_PILOT.values())] * 2 + [sum(im.values())] * 2 + [sum(INFRA_GROWTH.values())] * 4
    support_m = [45000, 45000, 90000, 90000, 180000, 180000, 180000, 180000]
    sales_m = [0, 0, 60000, 60000, 180000, 180000, 180000, 180000]
    prod_m = [0, 120000, 120000, 120000, 120000, 120000, 120000, 120000]
    fin_m = [0, 0, 60000, 60000, 60000, 60000, 60000, 60000]
    mkt_m = [30000, 30000, 60000, 60000, 150000, 150000, 150000, 150000]
    maint_m = [0] * 7 + [2.0 * loadr]
    vv = [x * vmult for x in venues_B()]
    av = avg_venues(vv)
    if delay:
        av = [0] * delay + av[:q - delay]
    rev = [av[i] * arpa_B()[i] * 3 for i in range(q)]
    comm = [COMMISSION * r for r in rev]
    rows = []
    for i in range(q):
        run = 3 * (infra_m[i] + support_m[i] + sales_m[i] + prod_m[i] + fin_m[i] + mkt_m[i] + maint_m[i])
        sub = build_q[i] + one_q[i] + run + comm[i]
        cont = CONTINGENCY * (build_q[i] + one_q[i] + run)
        cost = sub + cont
        rows.append(dict(q=i + 1, build=build_q[i], one=one_q[i], run=run, comm=comm[i], cont=cont, cost=cost, rev=rev[i], venues=vv[i]))
    return finish(rows, dict(build_shared=build_shared, build_types=build_types, build_total=build_total, one_total=one_total, tc=tc, shared_pm=shared_pm, types=names))

def finish(rows, extra):
    cum, peak, c = [], 0.0, 0.0
    for r in rows:
        c += r["rev"] - r["cost"]
        cum.append(c)
        peak = min(peak, c)
    tot = {k: sum(r[k] for r in rows) for k in ("build", "one", "run", "comm", "cont", "cost", "rev")}
    out = dict(rows=rows, cum=cum, peak=-peak, total=tot, **extra)
    return out

LEAN_ONE = [
 ("Lawyer review of privacy notice, programme terms, venue agreement", 25000),
 ("Company or existing-entity paperwork, GST check with CA", 10000),
 ("QR posters, table tents, staff cheat sheets", 5000),
 ("Domain and small extras", 2000),
]
LEAN_MONTHLY = [
 ("Supabase Pro (about US$25)", 2250),
 ("Vercel Pro (about US$20)", 1800),
 ("Printing, small pilot gifts, travel to cafes", 6000),
]
LEAN_BUILD = [("Optional: one contract developer for 1 month (polish, fixes, Google card test)", 70000)]

def lean():
    one = sum(x[1] for x in LEAN_ONE)
    monthly = sum(x[1] for x in LEAN_MONTHLY)
    opt = sum(x[1] for x in LEAN_BUILD)
    sub = one + monthly * 12 + opt
    return dict(one=one, monthly=monthly, opt=opt, year=sub, year_cont=sub * (1 + CONTINGENCY))

def round_up(x, step=100000):
    import math
    return math.ceil(x / step) * step

if __name__ == "__main__":
    for nm, f in (("A", scope_A), ("B", scope_B)):
        s = f()
        print(nm, "total cost", D.inr(s["total"]["cost"], True), "rev", D.inr(s["total"]["rev"], True), "peak need", D.inr(s["peak"], True), "build", D.inr(s["build_total"], True), "pm", s["shared_pm"])
    s2 = scope_A(types=SCOPE_A_TYPES2); print("A2", D.inr(s2["total"]["cost"], True), D.inr(s2["peak"], True))
    for nm, f in (("A", scope_A), ("B", scope_B)):
        print(nm, "market", D.inr(f(rate=RATE_MARKET)["peak"], True), "half venues", D.inr(f(vmult=.5)["peak"], True), "delay1", D.inr(f(delay=1)["peak"], True))
