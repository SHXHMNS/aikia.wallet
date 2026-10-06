'use client';

import { useState, type FormEvent } from 'react';
import { venuePresets, type BusinessType } from '@/config/presets';

type Result = { joinUrl: string; posterUrl: string; ownerMessage: string };
const slugify = (v: string) => v.toLowerCase().normalize('NFKD').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 40);

export default function NewVenueForm() {
  const [type, setType] = useState<BusinessType>('cafe');
  const [name, setName] = useState('');
  const [slug, setSlug] = useState('');
  const [basis, setBasis] = useState<'actions' | 'spend'>('spend');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<Result | null>(null);
  const p = venuePresets[type];

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setError(''); setResult(null);
    const f = Object.fromEntries(new FormData(event.currentTarget));
    try {
      const response = await fetch('/api/platform/venues', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ ...f, businessType: type, tierBasis: basis, slug, rewardTarget: Number(f.rewardTarget), chromeAt: Number(f.chromeAt), pinkAt: Number(f.pinkAt) }) });
      const body = await response.json();
      if (!response.ok) throw new Error(body.error || 'Could not create the venue.');
      setResult(body); event.currentTarget.reset(); setName(''); setSlug('');
    } catch (e) { setError(e instanceof Error ? e.message : 'Could not create the venue.'); }
    finally { setBusy(false); }
  }

  return <form className="settings-form wizard" onSubmit={submit} key={type + basis}>
    <label>Venue name<input required minLength={2} maxLength={80} value={name} onChange={e => { setName(e.target.value); setSlug(slugify(e.target.value)); }} placeholder="Café Noor"/></label>
    <label>Join link name<input required pattern="[a-z0-9]+(-[a-z0-9]+)*" value={slug} onChange={e => setSlug(slugify(e.target.value))} placeholder="cafe-noor"/></label>
    <label>Business type<select value={type} onChange={e => setType(e.target.value as BusinessType)}>{(Object.keys(venuePresets) as BusinessType[]).map(t => <option key={t} value={t}>{venuePresets[t].label}</option>)}</select></label>
    <label>Owner email (gets the login invite)<input name="ownerEmail" type="email" required placeholder="owner@venue.com"/></label>
    <label>What earns a stamp<input name="actionLabel" defaultValue={p.actionLabel} maxLength={24}/></label>
    <label>Stamps for a reward<input name="rewardTarget" type="number" min={1} max={1000} defaultValue={p.rewardTarget}/></label>
    <label>Reward<input name="rewardName" defaultValue={p.rewardName} maxLength={80}/></label>
    <label>Tiers unlock by<select value={basis} onChange={e => setBasis(e.target.value as 'actions' | 'spend')}><option value="spend">Total money spent (₹)</option><option value="actions">Number of visits</option></select></label>
    <label>Chrome tier starts at {basis === 'spend' ? '(₹)' : '(visits)'}<input name="chromeAt" type="number" min={1} required defaultValue={basis === 'spend' ? p.tiers[1].minLifetimeSpend : p.tiers[1].minLifetimeActions}/></label>
    <label>Pink tier starts at {basis === 'spend' ? '(₹)' : '(visits)'}<input name="pinkAt" type="number" min={2} required defaultValue={basis === 'spend' ? p.tiers[2].minLifetimeSpend : p.tiers[2].minLifetimeActions}/></label>
    <label>Card colour<input name="brandColor" type="color" defaultValue="#A98BFF"/></label>
    <label>Logo link (https, optional)<input name="logoUrl" type="url" placeholder="https://…/logo.png"/></label>
    <label>Venue photo link (https, optional)<input name="heroUrl" type="url" placeholder="https://…/photo.jpg"/></label>
    <button className="button primary" disabled={busy}>{busy ? 'Creating…' : 'Create venue'}</button>
    {error && <p className="wizard-error">{error}</p>}
    {result && <div className="wizard-done"><b>Venue created.</b> {result.ownerMessage}<br/>Join link: <a href={result.joinUrl} target="_blank" rel="noreferrer">{result.joinUrl}</a><br/><a href={result.posterUrl} target="_blank" rel="noreferrer">Open printable QR poster ↗</a></div>}
  </form>;
}
