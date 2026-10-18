'use client';

import { useEffect, useState } from 'react';

type Pack = { pay: number; get: number };
type Item = { name: string; price: number };
type Tx = { id: string; kind: string; amount_paise: number; paid_delta_paise: number; bonus_delta_paise: number; payment_method: string | null; verified_by_code: boolean; reversed: boolean; note: string | null; created_at: string; members?: { full_name: string; public_code: string } | null };
type Gift = { id: string; item_name: string; quantity: number; source: string; status: string; recipient_name: string | null; created_at: string; members?: { full_name: string } | null };
type Report = { loadedPaise: number; spentPaise: number; giftedPaise: number; outstandingPaidPaise: number; outstandingBonusPaise: number };

const rupees = (paise: number) => `₹${(Number(paise || 0) / 100).toLocaleString('en-IN', { maximumFractionDigits: 2 })}`;
const KIND: Record<string, string> = { load: 'Top-up', spend: 'Paid from credit', reversal: 'Reversal', gift_out: 'Gift sent', gift_return: 'Gift returned', adjust: 'Adjustment' };

/** Owner/admin: switch credit on, set top-up packs, limits and the gift menu, and see the money report. */
export default function CreditPanel({ venueId, flash }: { venueId: string; flash: (m: string) => void }) {
  const [enabled, setEnabled] = useState(false);
  const [packs, setPacks] = useState<Pack[]>([]);
  const [items, setItems] = useState<Item[]>([]);
  const [limits, setLimits] = useState({ taplessLimit: 300, dailyCap: 5000, giftDailyLimit: 2, giftValidDays: 30 });
  const [report, setReport] = useState<Report | null>(null);
  const [tx, setTx] = useState<Tx[]>([]);
  const [gifts, setGifts] = useState<Gift[]>([]);
  const [busy, setBusy] = useState(false);

  async function api(path: string, method = 'GET', body?: unknown) {
    const r = await fetch(path, { method, headers: body ? { 'content-type': 'application/json' } : undefined, body: body ? JSON.stringify(body) : undefined, cache: 'no-store' });
    const j = await r.json(); if (!r.ok) throw new Error(j.error || 'Request failed.'); return j;
  }
  async function load() {
    try {
      const j = await api(`/api/venues/${venueId}/credit`);
      const s = j.settings || {};
      setEnabled(Boolean(s.credit_enabled)); setPacks(s.credit_packs || []);
      setLimits({ taplessLimit: Number(s.tapless_limit_paise ?? 30000) / 100, dailyCap: Number(s.daily_spend_cap_paise ?? 500000) / 100, giftDailyLimit: s.gift_daily_limit ?? 2, giftValidDays: s.gift_valid_days ?? 30 });
      setItems((j.giftItems || []).map((i: { name: string; credit_cost_paise: number }) => ({ name: i.name, price: Number(i.credit_cost_paise) / 100 })));
      setReport(j.report); setTx(j.transactions || []); setGifts(j.gifts || []);
    } catch (e) { flash(e instanceof Error ? e.message : 'Could not load credit settings.'); }
  }
  useEffect(() => { load(); }, [venueId]); // eslint-disable-line react-hooks/exhaustive-deps

  async function save() {
    setBusy(true);
    try { await api(`/api/venues/${venueId}/credit`, 'PUT', { creditEnabled: enabled, packs, giftItems: items, ...limits }); flash('Credit & gift settings saved.'); await load(); }
    catch (e) { flash(e instanceof Error ? e.message : 'Could not save.'); } finally { setBusy(false); }
  }
  async function reverse(t: Tx) {
    if (!window.confirm(`Reverse this ${KIND[t.kind].toLowerCase()} of ${rupees(t.amount_paise)} for ${t.members?.full_name || 'this member'}?`)) return;
    setBusy(true);
    try { await api(`/api/credit/${t.id}/reverse`, 'POST', {}); flash('Reversed. The member’s balance and card are updated.'); await load(); }
    catch (e) { flash(e instanceof Error ? e.message : 'Could not reverse.'); } finally { setBusy(false); }
  }
  const setPack = (i: number, patch: Partial<Pack>) => setPacks(packs.map((p, j) => j === i ? { ...p, ...patch } : p));
  const setItem = (i: number, patch: Partial<Item>) => setItems(items.map((p, j) => j === i ? { ...p, ...patch } : p));

  return <div className="program-layout">
    <section className="console-panel">
      <span className="eyebrow">PREPAID CREDIT · SCAN TO PAY</span><h2>Let regulars skip the payment queue.</h2>
      <p>Guests top up at your counter (UPI, card or cash into your own account). Staff then scan their card and take each bill from the balance.</p>
      <div className="legal-note">Prototype for demos. Before taking real money for credit, get a lawyer&apos;s written opinion (RBI closed-system prepaid rules, GST on top-ups). Credit works only at this venue, cannot be cashed out and cannot be sent as money.</div>
      <div className="settings-form">
        <label><span>Credit</span><select value={enabled ? 'on' : 'off'} onChange={e => setEnabled(e.target.value === 'on')}><option value="off">Off</option><option value="on">On: guests can top up and pay by scan</option></select></label>
        <label>Scan-only limit per bill (₹)<input type="number" min={0} value={limits.taplessLimit} onChange={e => setLimits({ ...limits, taplessLimit: Number(e.target.value) })}/></label>
        <label>Daily spend limit per guest (₹)<input type="number" min={1} value={limits.dailyCap} onChange={e => setLimits({ ...limits, dailyCap: Number(e.target.value) })}/></label>
      </div>
      <h3 className="send-log-title">Top-up packs</h3>
      <div className="tiers-form">
        {packs.map((p, i) => <fieldset key={i}><legend>Pack {i + 1}</legend>
          <label>Guest pays (₹)<input type="number" min={1} value={p.pay} onChange={e => setPack(i, { pay: Number(e.target.value) })}/></label>
          <label>Guest gets (₹)<input type="number" min={1} value={p.get} onChange={e => setPack(i, { get: Number(e.target.value) })}/></label>
          <button type="button" className="secondary-action" onClick={() => setPacks(packs.filter((_, j) => j !== i))}>Remove</button>
        </fieldset>)}
        {packs.length < 6 && <button type="button" className="secondary-action" onClick={() => setPacks([...packs, { pay: 1000, get: 1100 }])}>＋ Add pack</button>}
      </div>
      <h3 className="send-log-title">Send a gift</h3>
      <p>Items a guest can send a friend from their credit, 1 or 2 at a time. Guests can also gift a free reward they have earned.</p>
      <div className="settings-form">
        <label>Gifts per guest per day<input type="number" min={0} max={10} value={limits.giftDailyLimit} onChange={e => setLimits({ ...limits, giftDailyLimit: Number(e.target.value) })}/></label>
        <label>Gift valid for (days)<input type="number" min={1} max={365} value={limits.giftValidDays} onChange={e => setLimits({ ...limits, giftValidDays: Number(e.target.value) })}/></label>
      </div>
      <div className="tiers-form">
        {items.map((it, i) => <fieldset key={i}><legend>{it.name || `Item ${i + 1}`}</legend>
          <label>Item<input value={it.name} maxLength={60} onChange={e => setItem(i, { name: e.target.value })} placeholder="Cappuccino"/></label>
          <label>Price in credit (₹)<input type="number" min={1} value={it.price} onChange={e => setItem(i, { price: Number(e.target.value) })}/></label>
          <button type="button" className="secondary-action" onClick={() => setItems(items.filter((_, j) => j !== i))}>Remove</button>
        </fieldset>)}
        {items.length < 12 && <button type="button" className="secondary-action" onClick={() => setItems([...items, { name: '', price: 180 }])}>＋ Add gift item</button>}
        <button className="button primary" disabled={busy} onClick={save}>Save credit & gifts</button>
      </div>
    </section>

    <section className="console-panel">
      <span className="eyebrow">MONEY REPORT</span><h2>Credit at a glance</h2>
      {report && <div className="report-row">
        <div><span>LOADED</span><b>{rupees(report.loadedPaise)}</b></div>
        <div><span>SPENT</span><b>{rupees(report.spentPaise)}</b></div>
        <div><span>GIFTED</span><b>{rupees(report.giftedPaise)}</b></div>
        <div><span>OWED TO GUESTS</span><b>{rupees(report.outstandingPaidPaise + report.outstandingBonusPaise)}</b><small> of which bonus {rupees(report.outstandingBonusPaise)}</small></div>
      </div>}
      <h3 className="send-log-title">Recent credit activity</h3>
      {tx.map(t => <div className="activity-item" key={t.id}><span className="activity-dot" style={{ opacity: t.reversed ? .3 : 1 }}/><div><b>{KIND[t.kind] || t.kind} · {rupees(t.amount_paise)}{t.reversed ? ' (reversed)' : ''}</b><small>{t.members?.full_name || 'Member'} · {new Date(t.created_at).toLocaleString('en-IN')}{t.payment_method ? ` · ${t.payment_method.toUpperCase()}` : ''}{t.verified_by_code ? ' · pay code' : ''}{t.note ? ` · ${t.note}` : ''}</small></div>{(t.kind === 'spend' || t.kind === 'load') && !t.reversed && <button className="secondary-action team-remove" disabled={busy} onClick={() => reverse(t)}>Reverse</button>}</div>)}
      {!tx.length && <p>No credit activity yet. Switch credit on, then record a top-up from the Staff scanner.</p>}
      {!!gifts.length && <><h3 className="send-log-title">Gifts</h3>{gifts.map(g => <div className="activity-item" key={g.id}><span className="activity-dot"/><div><b>{g.quantity} × {g.item_name} · {g.status}</b><small>From {g.members?.full_name || 'a member'}{g.recipient_name ? ` to ${g.recipient_name}` : ''} · {new Date(g.created_at).toLocaleDateString('en-IN')}</small></div></div>)}</>}
    </section>
  </div>;
}
