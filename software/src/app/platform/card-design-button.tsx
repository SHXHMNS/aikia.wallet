'use client';

import { useState } from 'react';

/** Pushes the metallic card design to PassKit and refreshes every card. */
export default function CardDesignButton() {
  const [busy, setBusy] = useState(false);
  const [lines, setLines] = useState<string[]>([]);
  async function run() {
    if (!window.confirm('Apply the current card design to PassKit and refresh every member card?')) return;
    setBusy(true); setLines([]);
    try {
      const response = await fetch('/api/platform/card-design', { method: 'POST' });
      const body = await response.json();
      if (!response.ok) throw new Error(body.error || 'Card design update failed.');
      setLines([...body.log, `${body.refreshed} member card(s) refreshed.`]);
    } catch (error) { setLines([error instanceof Error ? error.message : 'Card design update failed.']); }
    finally { setBusy(false); }
  }
  return <div>
    <button className="button primary" disabled={busy} onClick={run}>{busy ? 'Updating cards' : 'Apply card design'}</button>
    {lines.map(line => <p key={line}>{line}</p>)}
  </div>;
}
