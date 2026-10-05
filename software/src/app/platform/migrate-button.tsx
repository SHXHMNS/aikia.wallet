'use client';

import { useState } from 'react';

type Result = { code: string; name: string; google: string | null; error: string | null };

export default function MigrateButton() {
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  const [results, setResults] = useState<Result[]>([]);
  async function run() {
    if (!window.confirm('Issue wallet cards on the active engine for every member without one?')) return;
    setBusy(true); setMessage('');
    try {
      const response = await fetch('/api/platform/wallet-migrate', { method: 'POST' });
      const body = await response.json();
      if (!response.ok) throw new Error(body.error || 'Migration failed.');
      setResults(body.results); setMessage(`${body.migrated} card(s) issued, ${body.failed} failed.`);
    } catch (error) { setMessage(error instanceof Error ? error.message : 'Migration failed.'); }
    finally { setBusy(false); }
  }
  return <div>
    <button className="button primary" disabled={busy} onClick={run}>{busy ? 'Issuing cards…' : 'Issue missing cards'}</button>
    {message && <p>{message}</p>}
    {results.map(r => <div className="activity-item" key={r.code}><span className="activity-dot"/><div><b>{r.name} · {r.code}</b><small>{r.google ? <a href={r.google} target="_blank" rel="noreferrer">Google Wallet link ↗</a> : r.error}</small></div></div>)}
  </div>;
}
