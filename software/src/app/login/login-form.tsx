'use client';

import { FormEvent, useState } from 'react';
import { createSupabaseBrowserClient } from '@/lib/supabase/browser';

export default function LoginForm() {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setMessage('');
    try {
      const supabase = createSupabaseBrowserClient();
      const { error } = await supabase.auth.signInWithOtp({ email, options: { emailRedirectTo: `${window.location.origin}/auth/callback?next=/` } });
      if (error) throw error;
      setMessage('Check your inbox for a secure sign-in link.');
    } catch (error) { setMessage(error instanceof Error ? error.message : 'Sign-in could not be started.'); }
    finally { setBusy(false); }
  }
  return <form className="auth-form" onSubmit={submit}><label htmlFor="email">Work email</label><input id="email" autoComplete="email" type="email" required value={email} onChange={e => setEmail(e.target.value)} placeholder="you@venue.com"/><button className="button primary" disabled={busy}>{busy ? 'Sending link…' : 'Email me a secure sign-in link'} <span>↗</span></button>{message && <p className="auth-message" role="status">{message}</p>}</form>;
}
