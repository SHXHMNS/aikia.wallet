# -*- coding: utf-8 -*-
"""Inline SVG charts for the founder playbook."""
from html import escape as e

INK, PINK, MUTE, LINE = "#15131c", "#e6007a", "#6f6b7a", "#d9d5e3"
LANE_COL = {"member": ("#fff0f7", "#e6007a"), "staff": ("#e6f5f5", "#0f8b8d"),
            "platform": ("#eeeaf6", "#15131c"), "wallet": ("#e9eef9", "#2b5fb3")}

def box(cx, cy, title, sub, kind, w=112, h=64, num=None):
    bg, bd = LANE_COL[kind]
    x, y = cx - w / 2, cy - h / 2
    out = ['<rect x="%.1f" y="%.1f" width="%d" height="%d" rx="9" fill="#fff" stroke="%s" stroke-width="1.6"/>' % (x, y, w, h, bd)]
    if num is not None:
        out.append('<circle cx="%.1f" cy="%.1f" r="9.5" fill="%s"/><text x="%.1f" y="%.1f" font-size="10" font-weight="700" fill="#fff" text-anchor="middle">%s</text>' % (x + 2, y + 2, bd, x + 2, y + 5.4, num))
    out.append('<text x="%.1f" y="%.1f" font-size="10.6" font-weight="700" fill="%s" text-anchor="middle">%s</text>' % (cx, cy - 7, INK, e(title)))
    lines = sub.split("|")
    for i, ln in enumerate(lines):
        out.append('<text x="%.1f" y="%.1f" font-size="9.2" fill="%s" text-anchor="middle">%s</text>' % (cx, cy + 6 + i * 10.5, MUTE, e(ln)))
    return "".join(out)

def arrow(d, dashed=False, color=INK):
    da = ' stroke-dasharray="5 4"' if dashed else ""
    return '<path d="%s" fill="none" stroke="%s" stroke-width="1.5"%s marker-end="url(#ah%s)"/>' % (d, color, da, "p" if color == PINK else "i")

def defs():
    return ('<defs><marker id="ahi" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="%s"/></marker>'
            '<marker id="ahp" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="%s"/></marker></defs>' % (INK, PINK))

def flow_chart():
    W, H = 1180, 560
    lane_y = {"member": 50, "staff": 168, "platform": 286, "wallet": 404}
    lane_h = 112
    lane_names = {"member": "MEMBER|(phone)", "staff": "VENUE STAFF|(counter)", "platform": "AIKIA.WALLET|(platform)", "wallet": "WALLET AND|MESSAGING"}
    cy = {k: v + lane_h / 2 for k, v in lane_y.items()}
    cx = [190, 330, 470, 610, 750, 890, 1030]
    s = ['<svg class="chart" viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg">' % (W, H), defs()]
    s.append('<text x="14" y="26" font-size="15" font-weight="700" fill="%s" font-family="Bahnschrift, Segoe UI">Chart 1. End-to-end flow: from first scan to repeat visit</text>' % INK)
    for k, y in lane_y.items():
        bg, bd = LANE_COL[k]
        s.append('<rect x="8" y="%d" width="%d" height="%d" rx="8" fill="%s" opacity=".55"/>' % (y, W - 16, lane_h, bg))
        a, b = lane_names[k].split("|")
        s.append('<text x="20" y="%d" font-size="10.5" font-weight="700" fill="%s">%s</text><text x="20" y="%d" font-size="9" fill="%s">%s</text>' % (y + lane_h / 2 - 2, bd, a, y + lane_h / 2 + 11, MUTE, b))
    B = []
    B.append(box(cx[0], cy["member"], "Scans QR poster", "counter, table|or receipt", "member", num=1))
    B.append(box(cx[1], cy["member"], "Joins", "phone OTP|+ consent tick", "member", num=2))
    B.append(box(cx[1], cy["platform"], "Member created", "consent record|stored", "platform", num=3))
    B.append(box(cx[2], cy["wallet"], "Card issued", "taps Add to|Google / Apple Wallet", "wallet", num=4))
    B.append(box(cx[3], cy["staff"], "Visit or purchase", "staff scans card,|enters bill value", "staff", num=5))
    B.append(box(cx[4], cy["platform"], "Rules engine", "earn, tier, limits,|duplicate guard", "platform", num=6))
    B.append(box(cx[5], cy["platform"], "Ledger entry", "append-only,|audited", "platform", num=7))
    B.append(box(cx[5], cy["wallet"], "Pass refreshes", "balance, tier,|next reward", "wallet", num=8))
    B.append(box(cx[6], cy["member"], "Sees progress", "reward unlocked|on the card", "member", num=9))
    B.append(box(cx[6], cy["staff"], "Redeem", "staff confirms,|one-time use", "staff", num=10))
    B.append(box(cx[6], cy["platform"], "Redeem logged", "ledger + stock|cost recorded", "platform", num=11))
    B.append(box(cx[4], cy["wallet"], "Re-engage", "birthday, lapse,|nearby, campaign", "wallet", num=12))
    A = []
    h = 56
    A.append(arrow("M%d,%d H%d" % (cx[0] + h, cy["member"], cx[1] - h - 2), color=PINK))
    A.append(arrow("M%d,%d V%d" % (cx[1], cy["member"] + 32, cy["platform"] - 34), color=PINK))
    A.append(arrow("M%d,%d H%d V%d" % (cx[1] + h, cy["platform"], cx[2], cy["wallet"] - 34)))
    A.append(arrow("M%d,%d H%d V%d" % (cx[2] + h, cy["wallet"] + 10, cx[3] - 30, cy["staff"] + 34)))
    A.append(arrow("M%d,%d H%d V%d" % (cx[3] + h, cy["staff"], cx[4], cy["platform"] - 34)))
    A.append(arrow("M%d,%d H%d" % (cx[4] + h, cy["platform"], cx[5] - h - 2)))
    A.append(arrow("M%d,%d V%d" % (cx[5], cy["platform"] + 32, cy["wallet"] - 34)))
    A.append(arrow("M%d,%d H%d V%d H%d" % (cx[5] + h, cy["wallet"], cx[5] + h + 14, cy["member"], cx[6] - h - 2), color=PINK))
    A.append(arrow("M%d,%d V%d" % (cx[6], cy["member"] + 32, cy["staff"] - 34), color=PINK))
    A.append(arrow("M%d,%d V%d" % (cx[6], cy["staff"] + 32, cy["platform"] - 34)))
    A.append(arrow("M%d,%d V%d" % (cx[4], cy["platform"] + 32, cy["wallet"] - 34)))
    A.append(arrow("M%d,%d H%d V%d" % (cx[4] - h, cy["wallet"] - 10, cx[3] + 30, cy["staff"] + 34), dashed=True, color=PINK))
    s += A + B
    s.append('<text x="%d" y="%d" font-size="9" fill="%s" font-style="italic">member returns for the next visit</text>' % (cx[3] + 36, cy["wallet"] + 48, PINK))
    s.append('<text x="14" y="%d" font-size="9.4" fill="%s">The ledger (step 7) is the source of truth. The wallet card is a synchronised display of it. No money moves through aikia.wallet in this flow: points and visits only.</text>' % (H - 22, MUTE))
    s.append('<text x="14" y="%d" font-size="9.4" fill="%s">Pink arrows = what the member sees and does. Dashed = automated re-engagement, only for members who gave consent.</text>' % (H - 9, MUTE))
    s.append('</svg>')
    return "".join(s)

def sbox(x, y, w, h, title, sub="", fill="#fff", stroke=LINE, tcolor=INK, bold=True, fs=10.2):
    out = ['<rect x="%d" y="%d" width="%d" height="%d" rx="7" fill="%s" stroke="%s" stroke-width="1.4"/>' % (x, y, w, h, fill, stroke)]
    ty = y + (h / 2 + 3.5 if not sub else h / 2 - 3)
    out.append('<text x="%.1f" y="%.1f" font-size="%s" font-weight="%s" fill="%s" text-anchor="middle">%s</text>' % (x + w / 2, y + ty - y, fs, "700" if bold else "400", tcolor, e(title)))
    for i, ln in enumerate(sub.split("|") if sub else []):
        out.append('<text x="%.1f" y="%.1f" font-size="8.4" fill="%s" text-anchor="middle">%s</text>' % (x + w / 2, y + h / 2 + 9 + i * 9.6, MUTE, e(ln)))
    return "".join(out)

def arch_chart():
    W, H = 1180, 600
    s = ['<svg class="chart" viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg">' % (W, H), defs()]
    s.append('<text x="14" y="26" font-size="15" font-weight="700" fill="%s" font-family="Bahnschrift, Segoe UI">Chart 2. How the system works: building blocks and who touches what</text>' % INK)
    # column headings
    for x, t in [(24, "PEOPLE AND PLACES"), (322, "AIKIA.WALLET PLATFORM (multi-tenant, one codebase)"), (888, "OUTSIDE SERVICES")]:
        s.append('<text x="%d" y="52" font-size="9.4" font-weight="700" fill="%s" letter-spacing="1">%s</text>' % (x, PINK, t))
    # left column
    left = [("Member", "join page (QR), wallet card,|WhatsApp / SMS messages", "#fff0f7", PINK),
            ("Venue staff", "scanner app (phone browser):|scan, enter bill, redeem", "#e6f5f5", "#0f8b8d"),
            ("Venue owner / manager", "dashboard: brand, rules, tiers,|staff, reports, campaigns", "#e6f5f5", "#0f8b8d"),
            ("Venue systems", "POS, ERP, booking tool,|Shopify, school / college ERP", "#f6f4f9", "#6f6b7a"),
            ("aikia team", "platform console: onboarding,|support, billing, audit", "#eeeaf6", INK)]
    y = 64
    for t, sub, f, st in left:
        s.append(sbox(24, y, 250, 70, t, sub, f, st))
        y += 82
    # center platform
    s.append('<rect x="306" y="62" width="548" height="400" rx="12" fill="#faf9fc" stroke="%s" stroke-width="2"/>' % INK)
    s.append(sbox(322, 76, 516, 42, "Secure API layer: sign-in, roles (owner / manager / staff), rate limits, input checks", "", "#fff", INK, fs=9.6))
    mods = [("Program rules engine", "earn, burn, tiers, expiry,|limits, offers"), ("Ledger", "append-only record of|every action: the truth"),
            ("Members + consent", "who, what they agreed to,|household / parent link"), ("Campaigns and offers", "birthday, lapse, geofence,|festival, brand-funded")]
    x = 322
    for t, sub in mods:
        s.append(sbox(x, 130, 123, 76, t, sub, "#fff", PINK, fs=9.2)); x += 131
    mods2 = [("Billing and plans", "subscriptions, limits,|GST invoices"), ("Analytics and ROI", "repeat rate, reward cost,|cohorts, exports"),
             ("Integrations hub", "webhooks, CSV, POS and|booking adapters"), ("Vertical presets", "cafe, salon, retail,|school, college, more")]
    x = 322
    for t, sub in mods2:
        s.append(sbox(x, 218, 123, 70, t, sub, "#fff", LINE, fs=9.2)); x += 131
    s.append(sbox(322, 300, 516, 44, "Wallet adapter (one interface, swappable engines)", "direct Google engine, PassKit, Apple adapter (later)", "#e9eef9", "#2b5fb3", fs=9.8))
    s.append(sbox(322, 356, 516, 44, "Messaging adapter", "WhatsApp provider, SMS with DLT, e-mail  ·  consent and quiet-hour checks before every send", "#e9eef9", "#2b5fb3", fs=9.8))
    s.append(sbox(322, 412, 516, 40, "Database with row-level security per venue  ·  India region  ·  encrypted backups", "", "#15131c", INK, tcolor="#fff", fs=9.6))
    # right column
    right = [("Google Wallet", "loyalty / membership passes|(own engine)", "#e9eef9", "#2b5fb3"),
             ("PassKit (optional engine)", "Apple + Google passes|as a rented service", "#e9eef9", "#2b5fb3"),
             ("WhatsApp and SMS providers", "per-message fees|DLT-registered templates", "#e9eef9", "#2b5fb3"),
             ("Venue's own payment gateway", "UPI / cards for any purchase.|Money never touches aikia", "#fdeeed", "#c0392b"),
             ("Hosting and monitoring", "cloud, error tracking, uptime,|log archive", "#f6f4f9", "#6f6b7a")]
    y = 64
    for t, sub, f, st in right:
        s.append(sbox(888, y, 268, 70, t, sub, f, st)); y += 82
    # arrows left->center
    for yy in (99, 181, 263, 345, 427):
        s.append(arrow("M274,%d H304" % yy))
    for yy in (99, 181, 263, 345, 427):
        s.append(arrow("M856,%d H886" % yy))
    # bottom band
    s.append('<rect x="24" y="478" width="1132" height="84" rx="10" fill="#fff" stroke="%s" stroke-width="1.6" stroke-dasharray="6 4"/>' % PINK)
    s.append('<text x="40" y="498" font-size="9.4" font-weight="700" fill="%s" letter-spacing="1">OPERATIONS AND SAFETY AROUND EVERYTHING</text>' % PINK)
    ops = ["Monitoring and alerts", "Daily backups + restore drills", "Audit log kept 180 days (CERT-In)", "Incident runbook, 6-hour report", "DPDP controls: notice, consent, erase", "Release checks + staged rollout"]
    x = 40
    for t in ops:
        s.append('<rect x="%d" y="508" width="172" height="38" rx="7" fill="#fff0f7" stroke="#ffd0e6"/><text x="%d" y="531" font-size="9.2" font-weight="600" fill="%s" text-anchor="middle">%s</text>' % (x, x + 86, INK, e(t)))
        x += 182
    s.append('<text x="14" y="%d" font-size="9.2" fill="%s">The platform is one product configured per venue. New business types are solved with presets and rules first, custom code last.</text>' % (H - 12, MUTE))
    s.append('</svg>')
    return "".join(s)

def roadmap_chart():
    W, H = 1100, 330
    s = ['<svg class="chart" viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg">' % (W, H), defs()]
    s.append('<text x="14" y="24" font-size="14" font-weight="700" fill="%s" font-family="Bahnschrift, Segoe UI">Chart 5. Suggested 24-month path (stage gates, not promises)</text>' % INK)
    x0, x1 = 190, 1070
    months = 24
    step = (x1 - x0) / months
    for m in range(0, months + 1, 3):
        xx = x0 + m * step
        s.append('<line x1="%.1f" y1="44" x2="%.1f" y2="300" stroke="%s" stroke-width="1"/><text x="%.1f" y="40" font-size="9" fill="%s" text-anchor="middle">M%d</text>' % (xx, xx, LINE, xx, MUTE, m))
    rows = [("1. Prove it (1-3 pilots)", 0, 3, PINK), ("2. Cafes, sweets, salons, courts", 2, 9, "#0f8b8d"),
            ("3. Integrations + messaging", 4, 12, "#2b5fb3"), ("4. Chains + retail + Apple Wallet", 8, 17, "#8e44ad"),
            ("5. Education (pilot, then roll-out)", 10, 22, "#b7791f"), ("6. Partner channel + coalition", 14, 24, INK)]
    y = 54
    for t, a, b, c in rows:
        s.append('<text x="14" y="%d" font-size="10" font-weight="600" fill="%s">%s</text>' % (y + 16, INK, e(t)))
        s.append('<rect x="%.1f" y="%d" width="%.1f" height="22" rx="6" fill="%s" opacity=".9"/>' % (x0 + a * step, y, (b - a) * step, c))
        y += 40
    s.append('<text x="14" y="%d" font-size="9" fill="%s">Gate to move on: each stage needs paying venues, a repeat-rate lift you can show, clean support load, and no open legal issue.</text>' % (H - 10, MUTE))
    s.append('</svg>')
    return "".join(s)

def money_models_chart():
    W, H = 1000, 250
    s = ['<svg class="chart" viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg">' % (W, H), defs()]
    s.append('<text x="12" y="22" font-size="13" font-weight="700" fill="%s" font-family="Bahnschrift, Segoe UI">Chart 4. Three ways money can appear in the product, and our recommendation</text>' % INK)
    cols = [("A. Points and visits only", "No cash value, no stored money", "Venue gives rewards for purchases or visits.|aikia keeps the ledger.", "START HERE", "#1e8449", "#eaf7ef"),
            ("B. Venue-run prepaid credit or packs", "Venue sells its own packs, redeemable only at that venue", "Venue collects money through its own gateway.|aikia only records balance and use.", "PHASE 2, WITH COUNSEL", "#b7791f", "#fff7e6"),
            ("C. aikia holds or moves money", "Wallet balance, top-up, transfer, cross-merchant spend", "aikia would be issuing or operating a payment product.|Needs RBI authorisation or a licensed partner.", "DO NOT BUILD YET", "#c0392b", "#fdeeed")]
    x = 12
    for t, sub, body, tag, c, bg in cols:
        s.append('<rect x="%d" y="38" width="320" height="190" rx="10" fill="%s" stroke="%s" stroke-width="1.6"/>' % (x, bg, c))
        s.append('<text x="%d" y="64" font-size="12.4" font-weight="700" fill="%s">%s</text>' % (x + 14, INK, e(t)))
        s.append('<text x="%d" y="82" font-size="9.2" fill="%s">%s</text>' % (x + 14, MUTE, e(sub)))
        for i, ln in enumerate(body.split("|")):
            s.append('<text x="%d" y="%d" font-size="9.6" fill="%s">%s</text>' % (x + 14, 110 + i * 14, INK, e(ln)))
        s.append('<rect x="%d" y="190" width="%d" height="24" rx="12" fill="%s"/><text x="%d" y="206" font-size="9.2" font-weight="700" fill="#fff" text-anchor="middle" letter-spacing=".6">%s</text>' % (x + 14, 24 + len(tag) * 6.4, c, x + 14 + (24 + len(tag) * 6.4) / 2, tag))
        x += 334
    s.append('</svg>')
    return "".join(s)

if __name__ == "__main__":
    for n, f in [("flow", flow_chart), ("arch", arch_chart), ("road", roadmap_chart), ("money", money_models_chart)]:
        open("_t_%s.svg" % n, "w", encoding="utf-8").write(f())
    print("ok")
