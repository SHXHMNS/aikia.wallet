import Link from 'next/link';
import LoginForm from './login-form';
import { platform } from '@/config/platform';

export default function LoginPage() {
  return <main className="auth-shell"><Link href="/" className="brand"><span className="brand-mark">{platform.mark}</span><span>{platform.name}</span></Link><section className="auth-card"><span className="eyebrow">VENUE ACCESS</span><h1>Welcome back.</h1><p>Owners and authorized venue staff sign in with a one-time email link.</p><LoginForm/><small>Need a demo? The browser demo is separate from live venue accounts.</small></section></main>;
}
