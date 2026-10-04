'use client';

import { useEffect, useMemo, useRef, useState, type CSSProperties, type FormEvent } from 'react';
import { createSupabaseBrowserClient } from '@/lib/supabase/browser';

type Role = 'owner' | 'admin' | 'staff';
type Venue = { id: string; name: string; slug: string; business_type: string; action_label: string; balance_label: string; reward_target: number; reward_name: string; brand_color: string; background_color: string | null; program_logo_url: string | null; hero_image_url: string | null };
type Tier = { id?: string; rank: number; name: string; min_lifetime_actions: number; benefits: string[]; accent_color: string };
type Member = { id: string; full_name: string; public_code: string; stamp_balance: number; rewards_available: number; lifetime_actions: number; status: string; current_tier_id: string | null };
type Activity = { id: string; event_type: string; action_units: number; rewards_delta: number; created_at: string; members?: { full_name: string } | null };
type TeamMember = { user_id: string; role: string; email: string };
type ScannerHit = { rawValue: string };
type Scanner = { detect(source: HTMLVideoElement): Promise<ScannerHit[]> };
type WindowWithScanner = Window & { BarcodeDetector?: new (options: { formats: string[] }) => Scanner };

const businessTypes = ['cafe','restaurant','retail','salon','fitness','hotel','entertainment','other'];
const money = (value: number) => new Intl.NumberFormat(undefined, { maximumFractionDigits: 0 }).format(value);

export default function DashboardClient({ userEmail, role, venue: initialVenue, tiers: initialTiers, members: initialMembers, activity: initialActivity, team: initialTeam }: { userEmail: string; role: Role; venue: Venue | null; tiers: Tier[]; members: Member[]; activity: Activity[]; team: TeamMember[] }) {
  const [venue, setVenue] = useState(initialVenue);
  const [tiers, setTiers] = useState(initialTiers);
  const [members, setMembers] = useState(initialMembers);
  const [activity, setActivity] = useState(initialActivity);
  const [team, setTeam] = useState(initialTeam);
  const [view, setView] = useState<string>(role === 'staff' ? 'staff' : 'overview');
  const [notice, setNotice] = useState('');
  const [busy, setBusy] = useState(false);
  const [lookupCode, setLookupCode] = useState('');
  const [found, setFound] = useState<Record<string, unknown> | null>(null);
  const [memberName, setMemberName] = useState('');
  const [staffEmail, setStaffEmail] = useState('');
  const [saveUrl, setSaveUrl] = useState('');
  const [cameraOn, setCameraOn] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const actionKeyRef = useRef<string | null>(null);
  const redemptionKeyRef = useRef<string | null>(null);
  useEffect(() => () => { streamRef.current?.getTracks().forEach(track => track.stop()); }, []);
  const allowedViews = role === 'staff' ? ['staff'] : ['overview','members','staff','program','team'];
  const counts = useMemo(() => ({ actions: activity.filter(x => x.event_type === 'qualifying_action').reduce((n, x) => n + x.action_units, 0), rewards: members.reduce((n, m) => n + m.rewards_available, 0) }), [activity, members]);

  async function requestJson(path: string, method: string, body?: unknown) {
    const response = await fetch(path, { method, headers: body ? { 'content-type': 'application/json' } : undefined, body: body ? JSON.stringify(body) : undefined, cache: 'no-store' });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Request failed.');
    return result;
  }
  function flash(message: string) { setNotice(message); window.setTimeout(() => setNotice(''), 4500); }
  async function createVenue(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); const form = new FormData(event.currentTarget); setBusy(true);
    try { const result = await requestJson('/api/setup/venue','POST',{ name: form.get('name'), slug: form.get('slug') }); window.location.href = `/?created=${result.venueId}`; }
    catch (error) { flash(error instanceof Error ? error.message : 'Unable to create venue.'); }
    finally { setBusy(false); }
  }
  async function addMember(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (!venue) return; setBusy(true); setSaveUrl('');
    try {
      const result = await requestJson(`/api/venues/${venue.id}/members`,'POST',{ fullName: memberName });
      setSaveUrl(result.saveUrl || ''); setMemberName('');
      setMembers(current => [{ id: result.member.id, full_name: result.member.fullName, public_code: result.member.publicCode, stamp_balance: 0, rewards_available: 0, lifetime_actions: 0, status: 'active', current_tier_id: tiers[0]?.id || null }, ...current]);
      flash(result.walletSyncMessage || 'Member created. Google Wallet pass issued.');
    } catch (error) { flash(error instanceof Error ? error.message : 'Unable to add member.'); }
    finally { setBusy(false); }
  }
  async function inviteStaff(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (!venue) return; setBusy(true);
    try { const result = await requestJson(`/api/venues/${venue.id}/team`,'POST',{ email: staffEmail }); setTeam(current => [...current,{ user_id: crypto.randomUUID(), role: 'staff', email: result.invited.email }]); setStaffEmail(''); flash('Staff invitation sent. They will receive the staff/manager sign-in link.'); }
    catch (error) { flash(error instanceof Error ? error.message : 'Staff invite failed.'); }
    finally { setBusy(false); }
  }
  async function saveVenue(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (!venue) return; const form = new FormData(event.currentTarget); setBusy(true);
    const patch = {
      name: String(form.get('name')), businessType: String(form.get('businessType')), actionLabel: String(form.get('actionLabel')),
      balanceLabel: String(form.get('balanceLabel')), rewardTarget: Number(form.get('rewardTarget')), rewardName: String(form.get('rewardName')),
      brandColor: String(form.get('brandColor')), backgroundColor: String(form.get('backgroundColor') || '') || null,
      programLogoUrl: String(form.get('programLogoUrl') || '') || null, heroImageUrl: String(form.get('heroImageUrl') || '') || null,
    };
    try { const result = await requestJson(`/api/venues/${venue.id}/theme`,'PATCH',patch); setVenue(result.venue); flash(result.walletSynced ? 'Venue brand saved and Google Wallet class updated.' : `Venue setup saved. Wallet sync: ${result.walletSyncMessage || 'not configured yet'}`); }
    catch (error) { flash(error instanceof Error ? error.message : 'Unable to save venue settings.'); }
    finally { setBusy(false); }
  }
  async function saveTiers(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (!venue) return; setBusy(true);
    try { await requestJson(`/api/venues/${venue.id}/tiers`,'PUT',{ tiers: tiers.map(t => ({ name: t.name, minLifetimeActions: Number(t.min_lifetime_actions), benefits: t.benefits, accentColor: t.accent_color })) }); flash('Tier rules saved. New actions now unlock levels from these thresholds.'); window.setTimeout(() => window.location.reload(), 600); }
    catch (error) { flash(error instanceof Error ? error.message : 'Unable to save tiers.'); }
    finally { setBusy(false); }
  }
  async function lookup(code = lookupCode) {
    if (!venue || !code.trim()) return;
    try { const result = await requestJson(`/api/venues/${venue.id}/members/lookup?code=${encodeURIComponent(code.trim())}`,'GET'); actionKeyRef.current = null; redemptionKeyRef.current = null; setFound(result); setLookupCode(result.member.publicCode); }
    catch (error) { setFound(null); flash(error instanceof Error ? error.message : 'Member lookup failed.'); }
  }
  async function recordAction() {
    if (!found || !venue) return; const member = found.member as { id: string; fullName: string };
    setBusy(true);
    const idempotencyKey = actionKeyRef.current || crypto.randomUUID(); actionKeyRef.current = idempotencyKey;
    try { const result = await requestJson(`/api/members/${member.id}/actions`,'POST',{ units: 1, idempotencyKey }); actionKeyRef.current = null; setFound({ ...found, member: { ...(found.member as object), ...(result.member || {}) } }); flash(result.walletSynced ? `${venue.action_label} recorded and Google Wallet updated.` : `${venue.action_label} recorded.${result.walletSyncMessage ? ` Wallet sync: ${result.walletSyncMessage}` : ''}`); }
    catch (error) { flash(error instanceof Error ? error.message : 'Could not record this action.'); }
    finally { setBusy(false); }
  }
  async function redeem() {
    if (!found) return; const member = found.member as { id: string };
    const idempotencyKey = redemptionKeyRef.current || `redeem-${crypto.randomUUID()}`; redemptionKeyRef.current = idempotencyKey;
    setBusy(true); try { const result = await requestJson(`/api/members/${member.id}/redeem`,'POST',{ idempotencyKey }); redemptionKeyRef.current = null; setFound({ ...found, member: { ...(found.member as object), rewardsAvailable: result.redemption?.rewards_available } }); flash('Reward redemption recorded.'); }
    catch (error) { flash(error instanceof Error ? error.message : 'Redemption failed.'); } finally { setBusy(false); }
  }
  async function startCamera() {
    const browser = window as WindowWithScanner;
    if (!navigator.mediaDevices?.getUserMedia || !browser.BarcodeDetector) { flash('This browser cannot scan QR codes. Enter the member code instead.'); return; }
    try {
      streamRef.current = await navigator.mediaDevices.getUserMedia({ video: { facingMode: { ideal: 'environment' } }, audio: false });
      if (!videoRef.current) { stopCamera(); return; }
      videoRef.current.srcObject = streamRef.current; await videoRef.current.play(); setCameraOn(true);
      const detector = new browser.BarcodeDetector({ formats: ['qr_code'] });
      while (streamRef.current && videoRef.current) {
        const results = await detector.detect(videoRef.current);
        if (results[0]?.rawValue) { setLookupCode(results[0].rawValue); stopCamera(); await lookup(results[0].rawValue); break; }
        await new Promise(resolve => window.setTimeout(resolve, 180));
      }
    } catch { stopCamera(); flash('Camera access was blocked. Enter the member code instead.'); }
  }
  function stopCamera() { streamRef.current?.getTracks().forEach(t => t.stop()); streamRef.current = null; setCameraOn(false); }
  function navigate(nextView: string) { if (nextView !== 'staff') stopCamera(); setView(nextView); }
  async function signOut() { await createSupabaseBrowserClient().auth.signOut(); window.location.assign('/login'); }
  function setTier(index: number, patch: Partial<Tier>) { setTiers(current => current.map((tier, i) => i === index ? { ...tier, ...patch } : tier)); }

  if (!venue) return <main className="setup-shell"><div className="brand"><span className="brand-mark">a</span><span>AIKIA.WALLET</span></div><section className="setup-card"><span className="eyebrow">NEW VENUE WORKSPACE</span><h1>Set up your first venue.</h1><p>These details can be replaced with the buyer’s brand, reward rules, and program tiers during onboarding.</p><form className="auth-form" onSubmit={createVenue}><label>Venue name</label><input name="name" required minLength={2} maxLength={80} placeholder="Café Noor"/><label>Venue URL name</label><input name="slug" required pattern="[a-z0-9]+(-[a-z0-9]+)*" placeholder="cafe-noor"/><button disabled={busy} className="button primary">Create owner workspace <span>↗</span></button></form><p className="fine">A sample Ink / Chrome / Pink loyalty program will be added. You can change tier names, action thresholds, colors, and benefits.</p></section></main>;

  return <main className="console-shell" style={{ '--venue-accent': venue.brand_color, '--venue-background': venue.background_color || '#F5F6FA' } as CSSProperties}>
    <aside className="console-sidebar"><div className="brand"><span className="brand-mark">a</span><span>AIKIA.WALLET</span></div><div className="console-venue"><span className="eyebrow">VENUE</span><b>{venue.name}</b><small>{role === 'staff' ? 'STAFF / MANAGER' : 'OWNER / ADMIN'}</small></div><nav>{allowedViews.map(item => <button key={item} className={view === item ? 'selected' : ''} onClick={() => navigate(item)}>{({overview:'Overview',members:'Members',staff:'Staff scanner',program:'Brand & tiers',team:'Team access'} as Record<string,string>)[item]}</button>)}</nav><div className="console-side-foot"><span>{userEmail}</span><button onClick={signOut}>Sign out</button></div></aside>
    <section className="console-main"><header className="console-top"><div><span className="eyebrow">AIKIA / {venue.name}</span><h1>{view === 'staff' ? 'Staff counter' : view === 'members' ? 'Members' : view === 'program' ? 'Program settings' : 'Owner dashboard'}</h1></div><span className="live-provider">GOOGLE WALLET · {process.env.NEXT_PUBLIC_SUPABASE_URL ? 'CONNECTED APP' : 'SETUP NEEDED'}</span></header>
      {notice && <div className="notice" role="status">{notice}<button onClick={() => setNotice('')}>×</button></div>}
      {view === 'overview' && <>
        <section className="console-hero"><div><span className="eyebrow">LOYALTY THAT FITS THE VENUE</span><h2>Bring regulars<br/>back for their usual.</h2><p>One wallet membership, familiar counter flow, and rewards that adapt to your business.</p><button onClick={() => navigate('program')}>Customize this venue →</button></div><article className="pass-mock"><div className="pass-logo">{venue.name}</div><span className="tier-pill">{tiers[0]?.name || 'MEMBER'} MEMBER</span><b>GUEST PREVIEW</b><div className="pass-score">{members[0]?.stamp_balance ?? 0}<small> / {venue.reward_target} {venue.balance_label.toLowerCase()}</small></div><small>{venue.reward_name} · {venue.action_label}</small></article></section>
        <div className="metric-row"><article><span>MEMBERS</span><strong>{members.length}</strong></article><article><span>{venue.action_label.toUpperCase()}S RECORDED</span><strong>{money(counts.actions)}</strong></article><article><span>REWARDS READY</span><strong>{money(counts.rewards)}</strong></article><article><span>TIERS</span><strong>{tiers.length}</strong></article></div>
        <div className="split-row"><section className="console-panel"><div className="panel-title"><div><span className="eyebrow">RECENT ACTIVITY</span><h2>Member ledger</h2></div><button onClick={() => navigate('members')}>View members →</button></div>{activity.slice(0,8).map(row => <div className="activity-item" key={row.id}><span className="activity-dot"/><div><b>{row.members?.full_name || 'Member'}</b><small>{row.event_type === 'qualifying_action' ? `${row.action_units} qualifying action${row.action_units === 1 ? '' : 's'}` : row.event_type.replace('_',' ')}</small></div><time>{new Date(row.created_at).toLocaleDateString()}</time></div>)}</section><section className="console-panel"><span className="eyebrow">MEMBERSHIP VALUE</span><h2>Give regulars a reason to return.</h2><p>Members collect rewards with repeat actions and unlock venue-defined tiers with exclusive benefits.</p><div className="benefit-pills">{tiers.map(t => <span key={t.id || t.name} style={{ borderColor: t.accent_color }}>{t.name} · {t.min_lifetime_actions}+</span>)}</div><button className="secondary-action" onClick={() => navigate('program')}>Edit program rules</button></section></div>
      </>}
      {view === 'members' && role !== 'staff' && <div className="console-grid"><section className="console-panel"><div className="panel-title"><div><span className="eyebrow">FIRST-PARTY MEMBER BOOK</span><h2>{members.length} members</h2></div></div><div className="member-table"><div className="member-line header"><span>MEMBER</span><span>CODE</span><span>PROGRESS</span><span>TIER</span></div>{members.map(m => <div className="member-line" key={m.id}><span><b>{m.full_name}</b><small>{m.lifetime_actions} lifetime actions</small></span><code>{m.public_code}</code><span>{m.stamp_balance} / {venue.reward_target} · {m.rewards_available} rewards</span><span>{tiers.find(t => t.id === m.current_tier_id)?.name || 'Member'}</span></div>)}</div></section><div className="console-grid-stack"><section className="console-panel"><span className="eyebrow">CUSTOMER SIGN-UP</span><h2>Let guests join from their phone.</h2><p>Share this page or turn it into a QR code for the counter. Guests enter their name and can add their Google Wallet pass.</p><a className="join-link" href={`/join/${venue.slug}`} target="_blank" rel="noreferrer">/join/{venue.slug} ↗</a><button className="secondary-action join-copy" onClick={async () => { const url = `${window.location.origin}/join/${venue.slug}`; try { await navigator.clipboard.writeText(url); flash('Customer sign-up link copied.'); } catch { flash(url); } }}>Copy customer sign-up link</button></section><section className="console-panel"><span className="eyebrow">STAFF TOOL</span><h2>Add a member</h2><p>Creates the venue member record, unique scan value, and Google Wallet pass when issuer credentials are enabled.</p><form className="auth-form" onSubmit={addMember}><label>Member name</label><input value={memberName} onChange={e => setMemberName(e.target.value)} required maxLength={120} placeholder="Guest name"/><button disabled={busy} className="button primary">Create member <span>＋</span></button></form>{saveUrl && <a className="save-pass" href={saveUrl} target="_blank" rel="noreferrer">Save to Google Wallet ↗</a>}</section></div></div>}
      {view === 'staff' && <div className="staff-layout"><section className="console-panel scanner-panel"><span className="eyebrow">AUTHORIZED STAFF / MANAGER</span><h2>Scan a member’s Google Wallet QR</h2><p>Scan the member barcode. The server checks this venue’s membership and records the action in its ledger.</p><button className="secondary-action" onClick={cameraOn ? stopCamera : startCamera}>{cameraOn ? 'Stop scanner' : 'Open QR camera'}</button><video ref={videoRef} playsInline muted className="camera-video" hidden={!cameraOn}/><label>Member code or scanned QR value</label><div className="lookup-row"><input value={lookupCode} onChange={e => setLookupCode(e.target.value)} onKeyDown={e => e.key === 'Enter' && lookup()} placeholder="Scan or type the member code"/><button disabled={busy} onClick={() => lookup()}>Find member</button></div>{found && <article className="found-card"><span className="eyebrow">{(found.member as {tier:string}).tier.toUpperCase()} MEMBER</span><h3>{(found.member as {fullName:string}).fullName}</h3><p>{(found.member as {publicCode:string}).publicCode} · {(found.member as {lifetimeActions:number}).lifetimeActions} total actions</p><strong>{(found.member as {stampBalance:number}).stampBalance} / {venue.reward_target} {venue.balance_label.toLowerCase()}</strong><small> {(found.member as {rewardsAvailable:number}).rewardsAvailable} {venue.reward_name} reward(s) available</small><div className="benefit-pills">{((found.member as {tierBenefits:string[]}).tierBenefits || []).map(b => <span key={b}>{b}</span>)}</div><button className="button primary" disabled={busy || (found.member as {status:string}).status !== 'active'} onClick={recordAction}>Record 1 {venue.action_label} <span>＋</span></button>{(found.member as {rewardsAvailable:number}).rewardsAvailable > 0 && <button className="secondary-action" disabled={busy} onClick={redeem}>Redeem {venue.reward_name}</button>}</article>}</section><aside className="console-panel rules-panel"><span className="eyebrow">CURRENT PROGRAM</span><h2>{venue.name}</h2><p>Every qualifying <b>{venue.action_label}</b> adds one {venue.balance_label.toLowerCase()}. At {venue.reward_target}, the member earns:</p><strong className="reward-name">{venue.reward_name}</strong><hr/>{tiers.map(t => <div className="tier-rule" key={t.id || t.name}><b>{t.name}</b><span>{t.min_lifetime_actions}+ actions</span><small>{t.benefits.join(' · ')}</small></div>)}</aside></div>}
      {view === 'program' && role !== 'staff' && <div className="program-layout"><section className="console-panel"><span className="eyebrow">OWNER / ADMIN CONTROLS</span><h2>Venue and rewards identity</h2><p>Set the business type, card look, repeat-action rule, and the labels members see.</p><form className="settings-form" onSubmit={saveVenue}><label>Venue name<input name="name" required maxLength={80} defaultValue={venue.name}/></label><label>Business type<select name="businessType" defaultValue={venue.business_type}>{businessTypes.map(t => <option value={t} key={t}>{t[0].toUpperCase()+t.slice(1)}</option>)}</select></label><label>Qualifying action<input name="actionLabel" required maxLength={24} defaultValue={venue.action_label}/></label><label>Wallet balance label<input name="balanceLabel" required maxLength={9} defaultValue={venue.balance_label}/></label><label>Actions per reward<input name="rewardTarget" type="number" min="1" max="1000" required defaultValue={venue.reward_target}/></label><label>Reward name<input name="rewardName" required maxLength={80} defaultValue={venue.reward_name}/></label><label>Wallet card color<input name="brandColor" type="color" defaultValue={venue.brand_color}/></label><label>Dashboard background<input name="backgroundColor" type="color" defaultValue={venue.background_color || '#F5F6FA'}/></label><label>Program logo URL<input name="programLogoUrl" type="url" defaultValue={venue.program_logo_url || ''} placeholder="https://…"/></label><label>Card artwork URL<input name="heroImageUrl" type="url" defaultValue={venue.hero_image_url || ''} placeholder="https://…"/></label><button disabled={busy} className="button primary">Save venue setup</button></form></section><section className="console-panel"><span className="eyebrow">LIFETIME TIER LADDER</span><h2>Unlock exclusive benefits.</h2><p>Higher qualifying-action totals automatically promote members to the matching level.</p><form className="tiers-form" onSubmit={saveTiers}>{tiers.map((tier,index)=><fieldset key={tier.id || index}><legend>{index+1} · {tier.name}</legend><label>Tier name<input value={tier.name} onChange={e=>setTier(index,{name:e.target.value})}/></label><label>Starts at actions<input type="number" min={index===0?0:1} value={tier.min_lifetime_actions} disabled={index===0} onChange={e=>setTier(index,{min_lifetime_actions:Number(e.target.value)})}/></label><label>Tier color<input type="color" value={tier.accent_color} onChange={e=>setTier(index,{accent_color:e.target.value})}/></label><label>Exclusive benefits, one per line<textarea value={tier.benefits.join('\n')} onChange={e=>setTier(index,{benefits:e.target.value.split('\n').map(x=>x.trim()).filter(Boolean)})}/></label></fieldset>)}<button disabled={busy} className="button primary">Save tier ladder</button></form></section></div>}
      {view === 'team' && role !== 'staff' && <div className="console-grid"><section className="console-panel"><span className="eyebrow">OWNER CONTROL · STAFF / MANAGER</span><h2>Invite the counter team.</h2><p>Managers and staff get a separate, focused workspace for member lookup, action recording, and reward redemption.</p><form className="auth-form" onSubmit={inviteStaff}><label>Staff email address</label><input type="email" value={staffEmail} onChange={e=>setStaffEmail(e.target.value)} required placeholder="manager@venue.com"/><button disabled={busy} className="button primary">Send staff invitation ↗</button></form></section><section className="console-panel"><span className="eyebrow">AUTHORIZED TEAM</span><h2>{team.length} accounts</h2>{team.map(person=><div className="activity-item" key={person.user_id}><span className="activity-dot"/><div><b>{person.email}</b><small>{person.role.toUpperCase()}</small></div></div>)}</section></div>}
      <footer className="console-footer"><span>AIKIA.WALLET · {role === 'staff' ? 'STAFF CONSOLE' : 'OWNER CONSOLE'}</span><span>Google Wallet enabled · Apple Wallet provider seam reserved</span></footer>
    </section>
  </main>;
}
