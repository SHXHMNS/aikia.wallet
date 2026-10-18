'use client';

import { useEffect, useState } from 'react';

type Row = { id: string; name: string; code: string; venue: string; createdAt: string; cards: string[] };

/** Pick the card(s) to keep; every other member and their wallet card is deleted. */
export default function DemoCards() {
  const [rows, setRows] = useState<Row[]>([]);
  const [keep, setKeep] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');

  async function load() {
    const response = await fetch('/api/platform/demo-cards', { cache: 'no-store' });
    const body = await response.json();
    if (response.ok) setRows(body.members); else setMessage(body.error || 'Could not load members.');
  }
  useEffect(() => { load(); }, []);

  async function run() {
    const doomed = rows.length - keep.length;
    const typed = window.prompt(`This permanently deletes ${doomed} member(s) and their wallet cards, keeping ${keep.length}. Type DELETE to continue.`);
    if (typed !== 'DELETE') return;
    setBusy(true); setMessage('');
    try {
      const response = await fetch('/api/platform/demo-cards', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ keep, confirm: 'DELETE' }) });
      const body = await response.json();
      if (!response.ok) throw new Error(body.error || 'Clean-up failed.');
      setMessage(`${body.removed} removed, ${body.failed} failed.${body.failed ? ' ' + body.results.filter((r: { removed: boolean }) => !r.removed).map((r: { name: string; error?: string }) => `${r.name}: ${r.error}`).join(' · ') : ''}`);
      setKeep([]); await load();
    } catch (error) { setMessage(error instanceof Error ? error.message : 'Clean-up failed.'); }
    finally { setBusy(false); }
  }

  return <div>
    {rows.map(r => <label className="activity-item" key={r.id} style={{ cursor: 'pointer' }}>
      <input type="checkbox" checked={keep.includes(r.id)} onChange={e => setKeep(e.target.checked ? [...keep, r.id] : keep.filter(id => id !== r.id))}/>
      <div><b>{r.name} · {r.code}</b><small>{r.venue} · {new Date(r.createdAt).toLocaleDateString('en-IN')} · {r.cards.length ? r.cards.join(', ') + ' card' : 'no card'}</small></div>
    </label>)}
    {!rows.length && <p>No members.</p>}
    <button className="button primary" disabled={busy || !keep.length || keep.length === rows.length} onClick={run}>{busy ? 'Deleting' : `Keep ${keep.length || 'ticked'}, delete the rest`}</button>
    {message && <p>{message}</p>}
  </div>;
}
