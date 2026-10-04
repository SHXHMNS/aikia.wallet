'use client';

import { useState, type CSSProperties, type FormEvent } from 'react';

type Venue = { name: string; slug: string; brand_color: string; background_color: string | null; action_label: string; balance_label: string; reward_target: number; reward_name: string };

export default function JoinClient({ venue }: { venue: Venue }) {
  const [name, setName] = useState('');
  const [consent, setConsent] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [member, setMember] = useState<{ publicCode: string; saveUrl: string | null; walletSyncMessage: string | null } | null>(null);

  async function join(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setError('');
    try {
      const response = await fetch(`/api/join/${encodeURIComponent(venue.slug)}`, {
        method: 'POST', headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ fullName: name, consent }),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || 'We could not join this program. Please ask the team for help.');
      setMember(result.member); setName('');
    } catch (cause) { setError(cause instanceof Error ? cause.message : 'We could not join this program.'); }
    finally { setBusy(false); }
  }

  return <main className="join-shell" style={{ '--join-accent': venue.brand_color, '--join-background': venue.background_color || '#F5F6FA' } as CSSProperties}>
    <section className="join-card">
      <div className="join-brand-mark" aria-hidden="true">a</div>
      <span className="eyebrow">{venue.name} · LOYALTY CLUB</span>
      <h1>Good to see you again. Even better next time.</h1>
      <p>Join free. Collect a {venue.balance_label.toLowerCase()} with every {venue.action_label}, unlock your next {venue.reward_name.toLowerCase()}, and earn better perks as you come back.</p>
      <div className="join-reward"><b>{venue.reward_target} visits</b><span>toward a reward</span><small>Your venue may set different rewards and tier benefits.</small></div>
      {member ? <div className="join-success" role="status"><span className="eyebrow">YOU ARE IN</span><h2>Your member code</h2><code>{member.publicCode}</code>{member.saveUrl ? <a className="button primary" href={member.saveUrl}>Add to Google Wallet ↗</a> : <p>{member.walletSyncMessage || 'Ask the venue team to help add your pass.'}</p>}<p>Show this member code to the team if your wallet pass is not ready yet.</p><button className="join-reset" onClick={() => setMember(null)}>Join another time</button></div> : <form className="auth-form" onSubmit={join}>
        <label htmlFor="join-name">Your name</label><input id="join-name" autoComplete="name" required minLength={1} maxLength={120} value={name} onChange={e => setName(e.target.value)} placeholder="First and last name"/>
        <label className="join-consent"><input type="checkbox" checked={consent} onChange={e => setConsent(e.target.checked)} required/><span>I agree to this venue using my name and visit/reward history to run this loyalty program. <a href="/privacy" target="_blank" rel="noreferrer">Read the privacy notice</a>. To request account removal, ask the venue owner or manager.</span></label>
        <button className="button primary" disabled={busy || !consent}>{busy ? 'Joining...' : 'Join the loyalty club'}</button>
        {error && <p className="auth-message" role="alert">{error}</p>}
      </form>}
      <footer>Loyalty membership powered by AIKIA.WALLET · No payment details collected</footer>
    </section>
  </main>;
}
