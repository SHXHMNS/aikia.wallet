(() => {
  const STORE_KEY = 'aikia.wallet.demo.v1';
  const uid = () => Math.random().toString(36).slice(2, 8).toUpperCase();
  const now = () => new Date().toISOString();
  const daysAgo = n => new Date(Date.now() - n * 86400000).toISOString();
  const seed = () => ({
    venue: { name: 'Café Noor', target: 9, reward: 'Free coffee', accent: '#ff3d9a', logoUrl: '', heroUrl: '', tiers: [
      { name: 'Ink', threshold: 0, color: '#171421', benefits: ['Collect a stamp with every coffee'] },
      { name: 'Chrome', threshold: 15, color: '#aeb4c4', benefits: ['Complimentary size upgrade', 'Members-only seasonal menu'] },
      { name: 'Pink', threshold: 40, color: '#ff3d9a', benefits: ['Complimentary coffee', 'First access to new drinks', 'Member events'] },
    ] },
    members: [
      { id: 'm-aarav', code: 'AK-4F21', name: 'Aarav Shah', phone: '000-000-0111', joinedAt: daysAgo(18), lastVisit: daysAgo(0), consent: true, stamps: 7, lifetimeVisits: 22, rewardsAvailable: 1, scanToken: 'AK-4F21' },
      { id: 'm-mira', code: 'AK-8C10', name: 'Mira Patel', phone: '000-000-0222', joinedAt: daysAgo(12), lastVisit: daysAgo(1), consent: true, stamps: 4, lifetimeVisits: 14, rewardsAvailable: 0, scanToken: 'AK-8C10' },
      { id: 'm-kabir', code: 'AK-2D63', name: 'Kabir Mehta', phone: '000-000-0333', joinedAt: daysAgo(8), lastVisit: daysAgo(2), consent: true, stamps: 8, lifetimeVisits: 39, rewardsAvailable: 1, scanToken: 'AK-2D63' },
      { id: 'm-anaya', code: 'AK-7A95', name: 'Anaya Rao', phone: '000-000-0444', joinedAt: daysAgo(3), lastVisit: daysAgo(3), consent: false, stamps: 2, lifetimeVisits: 2, rewardsAvailable: 0, scanToken: 'AK-7A95' },
    ],
    ledger: [
      { id: 'e1', memberId: 'm-aarav', type: 'stamp', amount: 1, actor: 'Demo staff', at: daysAgo(0) },
      { id: 'e2', memberId: 'm-kabir', type: 'stamp', amount: 1, actor: 'Demo staff', at: daysAgo(1) },
      { id: 'e3', memberId: 'm-mira', type: 'stamp', amount: 1, actor: 'Demo staff', at: daysAgo(1) },
      { id: 'e4', memberId: 'm-anaya', type: 'join', amount: 0, actor: 'Guest join', at: daysAgo(3) },
    ],
    campaigns: []
  });
  let state;
  try { state = JSON.parse(localStorage.getItem(STORE_KEY)) || seed(); } catch { state = seed(); }
  const defaults = seed();
  state.venue = { ...defaults.venue, ...state.venue, tiers: state.venue?.tiers || defaults.venue.tiers };
  state.members = (state.members || []).map(m => ({ ...m, lifetimeVisits: m.lifetimeVisits ?? m.stamps ?? 0, rewardsAvailable: m.rewardsAvailable ?? 0, scanToken: m.scanToken || m.code }));
  state.activeRole = state.activeRole || 'owner';
  const $ = s => document.querySelector(s);
  const $$ = s => [...document.querySelectorAll(s)];
  const initials = name => name.split(/\s+/).slice(0, 2).map(x => x[0]).join('').toUpperCase();
  const esc = value => String(value).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const persist = () => { localStorage.setItem(STORE_KEY, JSON.stringify(state)); renderAll(); };
  const memberById = id => state.members.find(m => m.id === id);
  const relative = iso => {
    if (!iso) return 'No visits yet';
    const d = Math.max(0, Math.floor((Date.now() - new Date(iso).getTime()) / 86400000));
    return d === 0 ? 'Today' : d === 1 ? 'Yesterday' : `${d} days ago`;
  };
  const stampDots = (count, target, limit = 12) => {
    const n = Math.min(target, limit);
    return `<div class="stamp-track">${Array.from({ length: n }, (_, i) => `<i class="${i < count ? 'filled' : ''}"></i>`).join('')}</div>`;
  };
  const updateDots = (selector, count, target) => {
    const node = $(selector); if (!node) return;
    node.innerHTML = Array.from({ length: Math.min(target, 12) }, (_, i) => `<i class="${i < count ? 'filled' : ''}"></i>`).join('');
  };
  let toastTimer;
  function toast(message) {
    const node = $('#toast'); node.textContent = message; node.classList.add('show');
    clearTimeout(toastTimer); toastTimer = setTimeout(() => node.classList.remove('show'), 2500);
  }
  function setView(name) {
    const allowed = state.activeRole === 'staff' ? ['staff'] : ['overview', 'members', 'guest', 'campaigns', 'settings', 'staff'];
    if (!allowed.includes(name)) name = state.activeRole === 'staff' ? 'staff' : 'overview';
    $$('.view').forEach(v => v.classList.toggle('active', v.id === `view-${name}`));
    $$('.nav-item').forEach(b => b.classList.toggle('active', b.dataset.view === name));
    const label = ({ overview: state.activeRole === 'staff' ? 'Staff dashboard' : 'Owner overview', members: 'Members', staff: 'Staff scanner', guest: 'Guest join', campaigns: 'Campaigns', settings: 'Venue setup' })[name];
    $('#crumbView').textContent = label;
    if (name === 'guest') { $('#guestCardName').textContent = 'Your name'; }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
  function renderHeader() {
    $('#sidebarVenue').textContent = state.venue.name;
    $('#crumbView').textContent = $$('.nav-item.active')[0]?.textContent.trim() || 'Overview';
    $('#welcomeLine').textContent = `Here is the latest from ${state.venue.name}.`;
    $('#miniVenue').textContent = state.venue.name;
    $('#offerVenue').textContent = state.venue.name.toUpperCase();
    $('#notificationVenue').textContent = state.venue.name.toUpperCase();
    $('#staffVenueName').textContent = state.venue.name;
    $('#guestVenue').textContent = state.venue.name;
    document.documentElement.style.setProperty('--accent', state.venue.accent);
    document.documentElement.style.setProperty('--venue-accent', state.venue.accent);
    $$('.role-option').forEach(b => b.classList.toggle('active', b.id === (state.activeRole === 'staff' ? 'staffMode' : 'ownerMode')));
    $$('.nav-item').forEach(b => b.classList.toggle('hidden', !b.dataset.roles.split(',').includes(state.activeRole)));
    $('.nav-caption:not(.staff-nav-caption)').classList.toggle('hidden', state.activeRole === 'staff');
    $('.staff-nav-caption').textContent = state.activeRole === 'staff' ? 'STAFF WORKSPACE' : 'TEAM WORKSPACE';
    $('.demo-warning strong').textContent = state.activeRole === 'staff' ? 'Staff demo workspace.' : 'Product demo only.';
    $('.demo-warning span:nth-child(2)').innerHTML = state.activeRole === 'staff'
      ? '<strong>Staff dashboard.</strong> Scan a member QR or enter a member code, then record the coffee purchase.'
      : '<strong>Product demo only.</strong> No live wallet pass, messages, account security or cloud sync. Use fictional details.';
    if (state.activeRole === 'staff' && !$('#view-staff').classList.contains('active')) setView('staff');
    if (state.activeRole !== 'staff' && $('#view-staff').classList.contains('active')) setView('overview');
    const topMember = state.members.find(m => m.id === 'm-aarav') || state.members[0];
    if (topMember) {
      $('#heroStamps').innerHTML = `${Math.min(topMember.stamps, state.venue.target)} <small>/ ${state.venue.target}</small>`;
      updateDots('#heroStampTrack', topMember.stamps, state.venue.target);
      setTierBadge($('.mini-card .tier-badge'), tierFor(topMember).name, tierFor(topMember).color);
    }
    $('#settingsLogo').value = state.venue.logoUrl || '';
    $('#settingsHero').value = state.venue.heroUrl || '';
    $('#customColor').value = state.venue.accent;
    $('#roleModeLabel') && ($('#roleModeLabel').textContent = state.activeRole === 'staff' ? 'STAFF WORKSPACE' : 'OWNER / ADMIN WORKSPACE');
  }
  function tierFor(member) {
    const tiers = [...state.venue.tiers].sort((a, b) => a.threshold - b.threshold);
    return tiers.filter(t => member.lifetimeVisits >= t.threshold).at(-1) || tiers[0];
  }
  function setTierBadge(node, name, color) {
    if (!node) return;
    node.textContent = `${name.toUpperCase()} MEMBER`;
    node.style.setProperty('--tier-accent', color);
  }
  function renderStats() {
    const visits = state.ledger.filter(e => e.type === 'stamp').reduce((total, e) => total + (e.amount || 1), 0);
    const rewards = state.ledger.filter(e => e.type === 'reward').length;
    $('#statMembers').textContent = state.members.length;
    $('#statVisits').textContent = visits;
    $('#statRewards').textContent = rewards;
    $('#navMemberCount').textContent = state.members.length;
  }
  function renderActivity() {
    const events = [...state.ledger].sort((a, b) => b.at.localeCompare(a.at)).slice(0, 5);
    const html = events.map(e => {
      const m = memberById(e.memberId);
      const line = e.type === 'stamp' ? 'earned a visit stamp' : e.type === 'reward' ? 'unlocked a reward' : e.type === 'redeemed' ? 'redeemed a member reward' : e.type === 'tier' ? 'unlocked a new tier' : e.type === 'join' ? 'joined the club' : 'activity recorded';
      const glyph = e.type === 'stamp' ? '＋' : e.type === 'reward' ? '✳' : e.type === 'tier' ? '↑' : e.type === 'redeemed' ? '✓' : '◎';
      return `<div class="activity-row"><span class="activity-glyph">${glyph}</span><div class="activity-copy"><b>${esc(m?.name || 'Demo member')} ${line}</b><small>${esc(e.actor || 'Demo staff')}</small></div><span class="activity-time">${relative(e.at)}</span></div>`;
    }).join('');
    $('#activityList').innerHTML = html || '<div class="activity-row"><span class="activity-copy">No activity yet. Add a demo member to begin.</span></div>';
  }
  function renderMembers() {
    const query = ($('#memberSearch')?.value || '').trim().toLowerCase();
    const filtered = state.members.filter(m => `${m.name} ${m.code}`.toLowerCase().includes(query));
    $('#membersTable').innerHTML = filtered.map(m => { const tier = tierFor(m); return `<tr><td><div class="member-person"><span class="member-avatar">${initials(esc(m.name))}</span><span><b>${esc(m.name)}</b><small>${esc(m.phone)}</small></span></div></td><td><span class="code-chip">${esc(m.code)}</span></td><td>${m.stamps} / ${state.venue.target} <small>· ${m.lifetimeVisits} lifetime</small></td><td><span class="status-chip">${esc(tier.name.toUpperCase())}${m.rewardsAvailable ? ` · ${m.rewardsAvailable} REWARD` : ''}</span></td><td>${relative(m.lastVisit)}</td></tr>`; }).join('') || '<tr><td colspan="5">No matching sample members.</td></tr>';
    $('#memberCountLabel').textContent = `${filtered.length} ${filtered.length === 1 ? 'member' : 'members'}`;
  }
  function renderStaff() {
    $('#staffTarget').textContent = state.venue.target;
    $('#staffRewardTitle').textContent = `${state.venue.reward} is on us.`;
    $('#samplePickers').innerHTML = state.members.map(m => `<button type="button" data-member-code="${esc(m.code)}">${esc(m.name)} · ${esc(tierFor(m).name)}</button>`).join('');
  }
  function renderSettings() {
    $('#settingsVenue').value = state.venue.name;
    $('#settingsTarget').value = state.venue.target;
    $('#settingsReward').value = state.venue.reward;
    $('#settingsLogo').value = state.venue.logoUrl || '';
    $('#settingsHero').value = state.venue.heroUrl || '';
    $('#settingsPreviewVenue').textContent = state.venue.name;
    $('#settingsPreviewTarget').textContent = state.venue.target;
    $('#settingsPreviewReward').textContent = state.venue.reward;
    const previewMember = state.members.find(m => m.id === 'm-aarav') || state.members[0];
    const previewTier = previewMember ? tierFor(previewMember) : state.venue.tiers[0];
    setTierBadge($('#settingsPreviewTier'), previewTier.name, previewTier.color);
    renderTierEditor();
    $('#tierPreviewList').innerHTML = state.venue.tiers.map(t => `<div class="tier-preview-row"><span class="tier-dot" style="--tier-accent:${esc(t.color)}"></span><b>${esc(t.name)}</b><span>${Number(t.threshold).toLocaleString()} coffees</span></div>`).join('');
    $$('.color-choice').forEach(b => b.classList.toggle('active', b.dataset.color === state.venue.accent));
    updateDots('#settingsStampTrack', 7, state.venue.target);
  }
  function renderGuest() {
    const me = state.members.find(m => m.id === state.lastJoinedId);
    if (!me) return;
    $('#guestCardName').textContent = me.name;
    $('#guestCardStamps').innerHTML = `${Math.min(me.stamps, state.venue.target)} <small>/ ${state.venue.target}</small>`;
    $('#guestCardReward').textContent = state.venue.reward;
    $('#guestCode').textContent = me.code;
    setTierBadge($('#guestCard .tier-badge'), tierFor(me).name, tierFor(me).color);
    updateDots('#guestStampTrack', me.stamps, state.venue.target);
  }
  function renderTierEditor() {
    const host = $('#tierEditor'); if (!host) return;
    host.innerHTML = state.venue.tiers.map((tier, index) => `<div class="tier-edit" data-tier-index="${index}"><div class="tier-edit-top"><span class="tier-order">0${index + 1}</span><input class="tier-name" maxlength="24" aria-label="Tier name" value="${esc(tier.name)}"><input class="tier-color" type="color" aria-label="${esc(tier.name)} tier color" value="${esc(tier.color)}">${index > 0 ? '<button class="remove-tier" type="button" aria-label="Remove tier">×</button>' : '<span class="entry-tier">ENTRY</span>'}</div><label class="field-label">UNLOCK AT LIFETIME COFFEES</label><input class="tier-threshold" type="number" min="0" max="99999" value="${Number(tier.threshold)}" ${index === 0 ? 'disabled' : ''}><label class="field-label">EXCLUSIVE BENEFITS (ONE PER LINE)</label><textarea class="tier-benefits" rows="2">${esc((tier.benefits || []).join('\n'))}</textarea></div>`).join('') + (state.venue.tiers.length < 6 ? '<button type="button" id="addTier" class="add-tier">＋ Add another tier</button>' : '');
  }
  function renderAll() { renderHeader(); renderStats(); renderActivity(); renderMembers(); renderStaff(); renderSettings(); renderGuest(); }
  function addStamp(member) {
    member.stamps += 1; member.lifetimeVisits += 1; member.lastVisit = now();
    const event = { id: uid(), memberId: member.id, type: 'stamp', amount: 1, actor: 'Demo staff', at: now() };
    state.ledger.push(event);
    if (member.stamps >= state.venue.target) {
      member.stamps = 0; member.rewardsAvailable += 1;
      state.ledger.push({ id: uid(), memberId: member.id, type: 'reward', amount: 1, actor: 'Demo rule', at: now() });
    }
    const oldTier = tierFor({ ...member, lifetimeVisits: member.lifetimeVisits - 1 });
    const nextTier = tierFor(member);
    if (oldTier.name !== nextTier.name) state.ledger.push({ id: uid(), memberId: member.id, type: 'tier', amount: 1, actor: `${nextTier.name} tier unlocked`, at: now() });
    persist();
    showStaffResult(member, member.rewardsAvailable > 0);
    toast(oldTier.name !== nextTier.name ? `${nextTier.name} tier unlocked.` : member.rewardsAvailable ? 'Coffee added. A reward is ready.' : 'Coffee purchase recorded.');
  }
  function showStaffResult(member, unlocked = false) {
    const node = $('#staffResult'); node.classList.remove('hidden');
    const tier = tierFor(member);
    const nextTier = [...state.venue.tiers].sort((a,b)=>a.threshold-b.threshold).find(t => t.threshold > member.lifetimeVisits);
    node.innerHTML = `<div class="member-found"><div><span class="eyebrow">DEMO MEMBER · ${esc(tier.name.toUpperCase())} TIER</span><h4>${esc(member.name)}</h4><p>${esc(member.code)} · ${esc(member.phone)}</p></div><span class="member-avatar">${initials(esc(member.name))}</span></div><div class="result-stamps"><div class="stamp-message">${member.stamps} of ${state.venue.target} toward ${esc(state.venue.reward)}. ${member.rewardsAvailable ? `<b>${member.rewardsAvailable} reward${member.rewardsAvailable === 1 ? '' : 's'} ready.</b>` : ''}</div>${stampDots(member.stamps, state.venue.target)}<div class="stamp-message">${nextTier ? `${nextTier.threshold - member.lifetimeVisits} coffees to ${esc(nextTier.name)} · ${esc(nextTier.benefits.join(' · '))}` : `Top tier unlocked · ${esc(tier.benefits.join(' · '))}`}</div></div><button type="button" class="button primary full" id="addStampButton">Record one coffee purchase <span>＋</span></button>${member.rewardsAvailable ? '<button type="button" class="button secondary full redeem-button" id="redeemButton">Redeem one earned reward</button>' : ''}`;
    $('#addStampButton').addEventListener('click', () => addStamp(member));
    $('#redeemButton')?.addEventListener('click', () => { member.rewardsAvailable--; state.ledger.push({ id: uid(), memberId: member.id, type: 'redeemed', amount: 1, actor: 'Demo staff', at: now() }); persist(); showStaffResult(member); toast('Reward redemption recorded.'); });
  }
  $$('.nav-item').forEach(b => b.addEventListener('click', () => setView(b.dataset.view)));
  $$('[data-go]').forEach(b => b.addEventListener('click', () => setView(b.dataset.go)));
  $('#dismissWarning').addEventListener('click', () => $('.demo-warning').classList.add('hidden'));
  function switchRole(role) {
    state.activeRole = role; persist();
    setView(role === 'staff' ? 'staff' : 'overview');
    toast(role === 'staff' ? 'Staff dashboard opened.' : 'Owner dashboard opened.');
  }
  $('#ownerMode').addEventListener('click', () => switchRole('owner'));
  $('#staffMode').addEventListener('click', () => switchRole('staff'));
  $('#memberSearch').addEventListener('input', renderMembers);
  $('#samplePickers').addEventListener('click', e => {
    const button = e.target.closest('[data-member-code]'); if (!button) return;
    $('#staffCode').value = button.dataset.memberCode;
    const member = state.members.find(m => m.code === button.dataset.memberCode);
    if (member) showStaffResult(member, member.stamps >= state.venue.target);
  });
  $('#lookupMember').addEventListener('click', () => {
    const code = $('#staffCode').value.trim().toUpperCase();
    const member = state.members.find(m => m.code.toUpperCase() === code || m.scanToken.toUpperCase() === code);
    if (!member) { $('#staffResult').classList.remove('hidden'); $('#staffResult').innerHTML = '<p class="stamp-message">No sample member found for that code. Try one of the buttons below.</p>'; return; }
    showStaffResult(member, member.stamps >= state.venue.target);
  });
  $('#joinForm').addEventListener('submit', e => {
    e.preventDefault();
    const name = $('#guestName').value.trim(); const phone = $('#guestPhone').value.trim();
    if (!name || !phone || !$('#guestConsent').checked) { toast('Enter fictional details and check demo consent.'); return; }
    const code = `AK-${uid().slice(0, 4)}`;
    const member = { id: `m-${uid().toLowerCase()}`, code, scanToken: code, name, phone, joinedAt: now(), lastVisit: null, consent: true, stamps: 0, lifetimeVisits: 0, rewardsAvailable: 0 };
    state.members.unshift(member); state.ledger.push({ id: uid(), memberId: member.id, type: 'join', amount: 0, actor: 'Guest join', at: now() }); state.lastJoinedId = member.id;
    persist(); $('#stepTwo').classList.add('active'); toast('Your demo membership is ready.');
  });
  $('#saveSettings').addEventListener('click', () => {
    const name = $('#settingsVenue').value.trim(); const target = Math.max(2, Math.min(20, Number($('#settingsTarget').value) || 9)); const reward = $('#settingsReward').value.trim() || 'Member reward';
    if (!name) { toast('Enter a venue name.'); return; }
    state.venue = { ...state.venue, name, target, reward, logoUrl: $('#settingsLogo').value.trim(), heroUrl: $('#settingsHero').value.trim() }; persist(); toast('Demo venue branding, reward, and tier rules saved.');
  });
  $$('.color-choice').forEach(b => b.addEventListener('click', () => {
    $$('.color-choice').forEach(x => x.classList.remove('active')); b.classList.add('active'); state.venue.accent = b.dataset.color; $('#customColor').value = b.dataset.color; persist();
  }));
  $('#customColor').addEventListener('input', e => { state.venue.accent = e.target.value; $$('.color-choice').forEach(b => b.classList.toggle('active', b.dataset.color === e.target.value)); persist(); });
  $('#tierEditor').addEventListener('change', e => {
    const box = e.target.closest('[data-tier-index]'); if (!box) return;
    const index = Number(box.dataset.tierIndex); const tier = state.venue.tiers[index];
    if (e.target.classList.contains('tier-name')) tier.name = e.target.value.trim() || `Tier ${index + 1}`;
    if (e.target.classList.contains('tier-threshold')) tier.threshold = Math.max(index ? state.venue.tiers[index - 1].threshold + 1 : 0, Number(e.target.value) || 0);
    if (e.target.classList.contains('tier-color')) tier.color = e.target.value;
    if (e.target.classList.contains('tier-benefits')) tier.benefits = e.target.value.split('\n').map(x => x.trim()).filter(Boolean);
    persist();
  });
  $('#tierEditor').addEventListener('click', e => {
    if (e.target.id === 'addTier') {
      const last = state.venue.tiers.at(-1);
      state.venue.tiers.push({ name: `Tier ${state.venue.tiers.length + 1}`, threshold: Number(last.threshold) + 15, color: '#a98bff', benefits: ['Add an exclusive member benefit'] }); persist();
    }
    if (e.target.classList.contains('remove-tier')) { state.venue.tiers.splice(Number(e.target.closest('[data-tier-index]').dataset.tierIndex), 1); persist(); }
  });
  const campaignDefaults = {
    quiet: 'Your usual is waiting. Drop by for a little something on us today.',
    welcome: 'Welcome to the club. We are glad you are here.',
    winback: 'It has been a little while. Come back for your next favorite.',
    reward: 'You earned it. Your member reward is ready to enjoy.'
  };
  $('#campaignType').addEventListener('change', e => { $('#campaignCopy').value = campaignDefaults[e.target.value]; $('#notificationCopy').textContent = $('#campaignCopy').value; });
  $('#campaignCopy').addEventListener('input', e => { $('#notificationCopy').textContent = e.target.value || 'Your sample message preview appears here.'; });
  $('#previewCampaign').addEventListener('click', () => { $('#notificationVenue').textContent = state.venue.name.toUpperCase(); $('#notificationCopy').textContent = $('#campaignCopy').value; toast('Preview refreshed. No message sent.'); });
  $('#resetDemo').addEventListener('click', () => { state = seed(); localStorage.setItem(STORE_KEY, JSON.stringify(state)); renderAll(); toast('Sample data restored.'); });
  let scannerStream = null; let scannerActive = false;
  async function scanLoop() {
    if (!scannerActive) return;
    const video = $('#scanVideo');
    try {
      if (window.BarcodeDetector) {
        const detector = new BarcodeDetector({ formats: ['qr_code'] });
        const hits = await detector.detect(video);
        if (hits.length) { $('#staffCode').value = hits[0].rawValue.trim(); $('#lookupMember').click(); stopScanner(); toast('QR code scanned.'); return; }
      }
    } catch (error) { $('#cameraHint').textContent = error instanceof Error ? error.message : 'Unable to read that QR. Try the member code.'; }
    requestAnimationFrame(scanLoop);
  }
  function stopScanner() { scannerActive = false; scannerStream?.getTracks().forEach(track => track.stop()); scannerStream = null; $('#cameraBox').classList.add('hidden'); }
  $('#startScanner').addEventListener('click', async () => {
    if (!navigator.mediaDevices?.getUserMedia || !window.BarcodeDetector) { toast('Camera QR scanning needs a modern browser on HTTPS or localhost. Use the member code below.'); return; }
    try { scannerStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: { ideal: 'environment' } }, audio: false }); $('#scanVideo').srcObject = scannerStream; await $('#scanVideo').play(); $('#cameraBox').classList.remove('hidden'); $('#cameraHint').textContent = 'Point the camera at the member’s QR code.'; scannerActive = true; scanLoop(); }
    catch { toast('Camera permission was not granted. Enter the member code instead.'); stopScanner(); }
  });
  $('#stopScanner').addEventListener('click', stopScanner);
  renderAll();
})();
