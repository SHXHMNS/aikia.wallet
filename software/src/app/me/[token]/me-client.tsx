'use client';

import { useCallback, useEffect, useRef, useState, type FormEvent } from 'react';
import QRCode from 'qrcode';
import type { MemberCard } from '@/lib/server/member-card';

const rupees = (paise: number) => `₹${(paise / 100).toLocaleString('en-IN', { maximumFractionDigits: 2 })}`;
const tierArt = (tier: string) => { const t = tier.trim().toLowerCase(); return `/brand/card-hero-${t === 'chrome' || t === 'pink' ? t : 'ink'}.png`; };
const STATUS: Record<string, string> = { active: 'Waiting to be used', redeemed: 'Used', cancelled: 'Taken back', expired: 'Expired, returned to you' };

type PayCode = { code: string; expiresAt: string; qrValue: string; image: string };

export default function MeClient({ token, initial }: { token: string; initial: MemberCard }) {
  const [card, setCard] = useState(initial);
  const [pay, setPay] = useState<PayCode | null>(null);
  const [secondsLeft, setSecondsLeft] = useState(0);
  const [payOpen, setPayOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [sent, setSent] = useState<{ url: string; item: string } | null>(null);
  const [source, setSource] = useState<'credit' | 'reward'>(initial.venue.creditEnabled && initial.giftItems.length ? 'credit' : 'reward');
  const timer = useRef<number | null>(null);
  const payRef = useRef<PayCode | null>(null);
  const fetching = useRef(false);
  const { member, venue } = card;

  const reload = useCallback(async () => {
    const r = await fetch(`/api/me/${token}`, { cache: 'no-store' });
    if (r.ok) setCard(await r.json());
  }, [token]);

  const newCode = useCallback(async () => {
    if (fetching.current) return; fetching.current = true;
    try {
      const r = await fetch(`/api/me/${token}/pay-code`, { method: 'POST', cache: 'no-store' });
      const j = await r.json(); if (!r.ok) throw new Error(j.error);
      const image = await QRCode.toDataURL(j.qrValue, { margin: 1, width: 520, color: { dark: '#14111F', light: '#FFFFFF' } });
      payRef.current = { ...j, image }; setPay(payRef.current);
    } catch { setError('Could not load a pay code. Check your connection and try again.'); }
    finally { fetching.current = false; }
  }, [token]);

  // While the pay code is open, it renews itself before it expires and the balance refreshes after each scan.
  useEffect(() => {
    if (!payOpen) { payRef.current = null; setPay(null); return; }
    newCode();
    timer.current = window.setInterval(() => {
      const current = payRef.current;
      const left = current ? Math.max(0, Math.round((new Date(current.expiresAt).getTime() - Date.now()) / 1000)) : 0;
      setSecondsLeft(left);
      if (current && left <= 3) { newCode(); reload(); }
    }, 1000);
    return () => { if (timer.current) window.clearInterval(timer.current); };
  }, [payOpen, newCode, reload]);

  async function sendGift(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setError(''); setSent(null);
    const f = new FormData(event.currentTarget);
    try {
      const r = await fetch(`/api/me/${token}/gifts`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ source, itemId: f.get('itemId'), quantity: Number(f.get('quantity') || 1), recipientName: f.get('recipientName'), message: f.get('message') }) });
      const j = await r.json(); if (!r.ok) throw new Error(j.error);
      setSent({ url: `${window.location.origin}/gift/${j.gift.token}`, item: `${j.gift.quantity} × ${j.gift.item_name}` });
      event.currentTarget.reset(); await reload();
    } catch (e) { setError(e instanceof Error ? e.message : 'The gift could not be sent.'); }
    finally { setBusy(false); }
  }

  async function takeBack(id: string) {
    if (!window.confirm('Take this gift back? Your friend will no longer be able to use it.')) return;
    setBusy(true); setError('');
    try { const r = await fetch(`/api/me/${token}/gifts?id=${id}`, { method: 'DELETE' }); const j = await r.json(); if (!r.ok) throw new Error(j.error); await reload(); }
    catch (e) { setError(e instanceof Error ? e.message : 'Could not take the gift back.'); }
    finally { setBusy(false); }
  }

  async function share(url: string, item: string) {
    const text = `I sent you ${item} at ${venue.name}. Show this at the counter: ${url}`;
    if (navigator.share) { try { await navigator.share({ title: `A gift from ${member.firstName}`, text, url }); return; } catch { /* closed */ } }
    window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, '_blank', 'noopener');
  }

  const canGiftReward = member.rewardsAvailable > 0;
  const canGiftCredit = venue.creditEnabled && card.giftItems.length > 0;

  return <main className="me-shell">
    <header className="me-top"><span>{venue.name}</span><small>Member {member.publicCode}</small></header>

    <section className="me-card" aria-label={`${member.tier} card`}>
      <img src={tierArt(member.tier)} alt="" width={1032} height={336}/>
      <div className="me-card-name"><b>{member.fullName}</b><span>{member.tier}</span></div>
    </section>

    <section className="me-balances">
      {venue.creditEnabled && <div><small>Credit</small><strong>{rupees(member.creditPaise)}</strong></div>}
      <div><small>{venue.balanceLabel.toLowerCase()}</small><strong>{member.stampBalance}<em>/{venue.rewardTarget}</em></strong></div>
      <div><small>Rewards ready</small><strong>{member.rewardsAvailable}</strong></div>
    </section>

    {error && <p className="me-error" role="alert">{error}</p>}

    {venue.creditEnabled && <section className="me-block">
      <h2>Pay at the counter</h2>
      {!payOpen ? <>
        <p>Show this code and the team takes the bill from your credit. No queue, no cash.</p>
        <button className="me-primary" onClick={() => setPayOpen(true)}>Show pay code</button>
      </> : <div className="me-pay">
        {pay ? <img src={pay.image} alt={`Pay code ${pay.code}`} width={260} height={260}/> : <div className="me-qr-skeleton" aria-hidden="true"/>}
        <div className="me-code">{pay ? `${pay.code.slice(0, 3)} ${pay.code.slice(3)}` : '··· ···'}</div>
        <p className="me-fine">Works once. Renews in {secondsLeft || 45}s, so a screenshot will not work.</p>
        <button className="me-secondary" onClick={() => { setPayOpen(false); reload(); }}>Done</button>
      </div>}
    </section>}

    {venue.creditEnabled && venue.creditPacks.length > 0 && <section className="me-block">
      <h2>Top up</h2>
      <p>Tell the team which pack you want and pay by UPI, card or cash. The credit lands on this card at once.</p>
      <div className="me-packs">{venue.creditPacks.map(p => <div key={p.pay}><span>Pay ₹{p.pay.toLocaleString('en-IN')}</span><b>Get ₹{p.get.toLocaleString('en-IN')}</b>{p.get > p.pay && <small>+₹{(p.get - p.pay).toLocaleString('en-IN')} extra</small>}</div>)}</div>
      <p className="me-fine">Credit can only be used at {venue.name}. It cannot be cashed out or sent as money.</p>
    </section>}

    <section className="me-block">
      <h2>Send a gift</h2>
      {!canGiftReward && !canGiftCredit ? <p>Earn your first {venue.rewardName.toLowerCase()} and you can send it to a friend from here.</p> : <>
        <p>Treat a friend at {venue.name}. They get a one-time voucher to show at the counter. Up to {venue.giftDailyLimit} gifts a day, valid {venue.giftValidDays} days.</p>
        {canGiftReward && canGiftCredit && <div className="me-toggle" role="tablist">
          <button role="tab" aria-selected={source === 'credit'} className={source === 'credit' ? 'on' : ''} onClick={() => setSource('credit')}>From my credit</button>
          <button role="tab" aria-selected={source === 'reward'} className={source === 'reward' ? 'on' : ''} onClick={() => setSource('reward')}>My free reward</button>
        </div>}
        <form className="me-form" onSubmit={sendGift}>
          {source === 'credit' && canGiftCredit ? <>
            <label htmlFor="g-item">What to send</label>
            <select id="g-item" name="itemId" required>{card.giftItems.map(i => <option key={i.id} value={i.id}>{i.name} · {rupees(i.pricePaise)}</option>)}</select>
            <label htmlFor="g-qty">How many</label>
            <select id="g-qty" name="quantity" defaultValue="1"><option value="1">1</option><option value="2">2</option></select>
          </> : <p className="me-fine">Sends 1 × {venue.rewardName} from your rewards.</p>}
          <label htmlFor="g-name">Friend&apos;s first name</label>
          <input id="g-name" name="recipientName" maxLength={60} placeholder="Optional"/>
          <label htmlFor="g-msg">Message</label>
          <input id="g-msg" name="message" maxLength={140} placeholder="Optional, e.g. Coffee is on me today"/>
          <button className="me-primary" disabled={busy}>{busy ? 'Sending' : 'Send gift'}</button>
        </form>
        {sent && <div className="me-sent" role="status"><b>{sent.item} is ready for your friend.</b><span>Share the link. It works once, only at {venue.name}.</span><div><button className="me-primary" onClick={() => share(sent.url, sent.item)}>Share link</button><button className="me-secondary" onClick={async () => { try { await navigator.clipboard.writeText(sent.url); } catch { window.prompt('Copy this link', sent.url); } }}>Copy</button></div></div>}
      </>}
    </section>

    {card.gifts.length > 0 && <section className="me-block">
      <h2>Gifts you sent</h2>
      <ul className="me-gifts">{card.gifts.map(g => <li key={g.id}>
        <div><b>{g.quantity} × {g.itemName}</b><small>{g.recipientName ? `For ${g.recipientName}. ` : ''}{STATUS[g.status] || g.status}</small></div>
        {g.status === 'active' && <span><button className="me-link" onClick={() => share(`${window.location.origin}/gift/${g.token}`, `${g.quantity} × ${g.itemName}`)}>Share</button><button className="me-link" disabled={busy} onClick={() => takeBack(g.id)}>Take back</button></span>}
      </li>)}</ul>
    </section>}

    {member.tierBenefits.length > 0 && <section className="me-block"><h2>{member.tier} benefits</h2><ul className="me-benefits">{member.tierBenefits.map(b => <li key={b}>{b}</li>)}</ul></section>}

    <footer className="me-foot">Keep this link private. It opens your card. Membership by aikia.wallet.</footer>
  </main>;
}
