'use client';

import { useEffect, useState, type FormEvent } from 'react';

type Loc = { label: string; lat: number | string; lng: number | string; lock_screen_message?: string | null };
type Campaign = { id: string; name: string; kind: string; header: string; body: string; weekdays: number[]; winback_days: number; active: boolean; last_sent_at: string | null };
type Send = { campaign_id: string | null; trigger: string; audience: number; status: string; detail: string | null; sent_at: string };

const KIND: Record<string, string> = { broadcast: 'Send now only (one-off offer)', daily: 'Every chosen day at 9 am', weather_rain: 'When rain is likely today', weather_hot: 'When it is hotter than 35°C', winback: '“We miss you” after N days away' };
const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const IDEAS: Record<string, [string, string]> = {
  broadcast: ['Today only ✨', '20% off any cold coffee until 6 pm. Show this card at the counter.'],
  daily: ['Happy hour ☕', '3–5 pm: second coffee half price for members.'],
  weather_rain: ['Rainy day? ☔', 'Hot chocolate is on us with any snack today — just show your card.'],
  weather_hot: ['Too hot out ☀️', 'Cool down: free upgrade on any iced drink today.'],
  winback: ['We miss you 💗', 'Come back this week and get a double stamp on your next visit.'],
};

/** Paste "lat, lng" or a Google Maps link and get coordinates. */
function parseCoords(text: string): [number, number] | null {
  const m = text.match(/(-?\d{1,2}\.\d+)\s*,\s*(-?\d{1,3}\.\d+)/) || text.match(/@(-?\d{1,2}\.\d+),(-?\d{1,3}\.\d+)/);
  return m ? [Number(m[1]), Number(m[2])] : null;
}

export default function EngagePanel({ venueId, flash }: { venueId: string; flash: (m: string) => void }) {
  const [locs, setLocs] = useState<Loc[]>([]);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [sends, setSends] = useState<Send[]>([]);
  const [kind, setKind] = useState('weather_rain');
  const [days, setDays] = useState<number[]>([0, 1, 2, 3, 4, 5, 6]);
  const [busy, setBusy] = useState(false);

  async function api(path: string, method = 'GET', body?: unknown) {
    const r = await fetch(`/api/venues/${venueId}${path}`, { method, headers: body ? { 'content-type': 'application/json' } : undefined, body: body ? JSON.stringify(body) : undefined, cache: 'no-store' });
    const j = await r.json(); if (!r.ok) throw new Error(j.error || 'Request failed.'); return j;
  }
  async function load() {
    try { const [l, c] = await Promise.all([api('/locations'), api('/campaigns')]); setLocs(l.locations); setCampaigns(c.campaigns); setSends(c.sends); }
    catch (e) { flash(e instanceof Error ? e.message : 'Could not load offers.'); }
  }
  useEffect(() => { load(); }, [venueId]); // eslint-disable-line react-hooks/exhaustive-deps

  async function saveLocations() {
    setBusy(true);
    try { const r = await api('/locations', 'PUT', { locations: locs.map(l => ({ label: l.label, lat: Number(l.lat), lng: Number(l.lng), lockScreenMessage: l.lock_screen_message })) }); flash(r.walletSynced ? `${r.saved} location(s) saved and added to the wallet cards.` : `Saved. Wallet sync: ${r.walletSyncMessage}`); }
    catch (e) { flash(e instanceof Error ? e.message : 'Could not save locations.'); } finally { setBusy(false); }
  }
  async function create(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); const f = Object.fromEntries(new FormData(event.currentTarget)); setBusy(true);
    try { await api('/campaigns', 'POST', { ...f, kind, weekdays: days, winbackDays: Number(f.winbackDays || 14) }); event.currentTarget.reset(); flash('Campaign created.'); await load(); }
    catch (e) { flash(e instanceof Error ? e.message : 'Could not create campaign.'); } finally { setBusy(false); }
  }
  async function act(c: Campaign, action: 'send' | 'toggle' | 'delete') {
    if (action === 'delete' && !window.confirm(`Delete “${c.name}”?`)) return;
    if (action === 'send' && !window.confirm(`Send “${c.header}” to members now?`)) return;
    setBusy(true);
    try {
      if (action === 'send') { const r = await api(`/campaigns/${c.id}/send`, 'POST'); flash(r.status === 'sent' ? `Sent to ${r.audience} card(s).` : `${r.status}: ${r.detail || ''}`); }
      if (action === 'toggle') await api(`/campaigns/${c.id}`, 'PATCH', { active: !c.active });
      if (action === 'delete') await api(`/campaigns/${c.id}`, 'DELETE');
      await load();
    } catch (e) { flash(e instanceof Error ? e.message : 'Action failed.'); } finally { setBusy(false); }
  }
  const idea = IDEAS[kind];

  return <div className="program-layout">
    <section className="console-panel">
      <span className="eyebrow">GEOFENCING · NEARBY ALERTS</span><h2>Where is the venue?</h2>
      <p>Up to 10 locations. Members’ cards surface on the phone when they are nearby. Paste a Google Maps link or “lat, lng”.</p>
      <div className="tiers-form">
        {locs.map((l, i) => <fieldset key={i}><legend>{i + 1} · {l.label || 'Location'}</legend>
          <label>Name<input value={l.label} maxLength={60} onChange={e => setLocs(locs.map((x, j) => j === i ? { ...x, label: e.target.value } : x))} placeholder="Main branch"/></label>
          <label>Google Maps link or lat, lng<input defaultValue={l.lat && l.lng ? `${l.lat}, ${l.lng}` : ''} onBlur={e => { const c = parseCoords(e.target.value); if (c) setLocs(locs.map((x, j) => j === i ? { ...x, lat: c[0], lng: c[1] } : x)); else if (e.target.value) flash('Could not read coordinates. Paste “22.3072, 73.1812” or a Maps link with @lat,lng.'); }} placeholder="22.3072, 73.1812"/></label>
          <label>Nearby message (Apple lock screen)<textarea maxLength={120} value={l.lock_screen_message || ''} onChange={e => setLocs(locs.map((x, j) => j === i ? { ...x, lock_screen_message: e.target.value } : x))} placeholder="You’re 2 minutes away. Your usual is waiting ☕"/></label>
          <button type="button" className="secondary-action" onClick={() => setLocs(locs.filter((_, j) => j !== i))}>Remove</button>
        </fieldset>)}
        {locs.length < 10 && <button type="button" className="secondary-action" onClick={() => setLocs([...locs, { label: '', lat: '', lng: '' }])}>＋ Add location</button>}
        <button className="button primary" disabled={busy} onClick={saveLocations}>Save locations</button>
      </div>
    </section>

    <section className="console-panel">
      <span className="eyebrow">OFFERS · NOTIFICATIONS · CAMPAIGNS</span><h2>Bring members back</h2>
      <p>Messages appear on every member’s wallet card (Google sends a notification). Automatic campaigns run every morning at 9 am IST.</p>
      <form className="settings-form" onSubmit={create} key={kind}>
        <label>Type<select value={kind} onChange={e => setKind(e.target.value)}>{Object.entries(KIND).map(([k, v]) => <option key={k} value={k}>{v}</option>)}</select></label>
        <label>Campaign name<input name="name" required maxLength={60} defaultValue={KIND[kind].split(' (')[0]}/></label>
        <label>Title<input name="header" required maxLength={60} defaultValue={idea[0]}/></label>
        <label>Message<textarea name="body" required maxLength={300} defaultValue={idea[1]}/></label>
        {kind === 'winback' && <label>Days since last visit<input name="winbackDays" type="number" min={3} max={365} defaultValue={14}/></label>}
        {kind !== 'broadcast' && kind !== 'winback' && <div className="day-picks">{DAYS.map((d, i) => <button type="button" key={d} className={days.includes(i) ? 'on' : ''} onClick={() => setDays(days.includes(i) ? days.filter(x => x !== i) : [...days, i])}>{d}</button>)}</div>}
        <button className="button primary" disabled={busy}>Create campaign</button>
      </form>
      <div className="campaign-list">
        {campaigns.map(c => <div className="activity-item" key={c.id}><span className="activity-dot" style={{ opacity: c.active ? 1 : .3 }}/><div><b>{c.name}{c.active ? '' : ' (paused)'}</b><small>{KIND[c.kind]} · “{c.header}” {c.last_sent_at ? `· last sent ${new Date(c.last_sent_at).toLocaleString('en-IN')}` : ''}</small></div>
          <span className="campaign-actions"><button className="secondary-action" disabled={busy} onClick={() => act(c, 'send')}>Send now</button>{c.kind !== 'broadcast' && <button className="secondary-action" disabled={busy} onClick={() => act(c, 'toggle')}>{c.active ? 'Pause' : 'Resume'}</button>}<button className="secondary-action" disabled={busy} onClick={() => act(c, 'delete')}>Delete</button></span></div>)}
        {!campaigns.length && <p>No campaigns yet. Start with a rain offer — it only sends on rainy days.</p>}
      </div>
      {!!sends.length && <><h3 className="send-log-title">Recent sends</h3>{sends.slice(0, 8).map((s, i) => <div className="activity-item" key={i}><span className="activity-dot"/><div><b>{s.status} · {s.audience} card(s)</b><small>{new Date(s.sent_at).toLocaleString('en-IN')} · {s.trigger}{s.detail ? ` · ${s.detail}` : ''}</small></div></div>)}</>}
    </section>
  </div>;
}
