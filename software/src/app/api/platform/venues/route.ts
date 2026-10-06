import { NextResponse } from 'next/server';
import { isBusinessType, venuePresets } from '@/config/presets';
import { getPlatformAdmin } from '@/lib/server/platform-access';
import { createSupabaseAdminClient } from '@/lib/supabase/admin';

export const runtime = 'nodejs';
const hex = /^#[0-9a-fA-F]{6}$/;
const text = (v: unknown, min: number, max: number) => typeof v === 'string' && v.trim().length >= min && v.trim().length <= max ? v.trim() : null;
const https = (v: unknown) => { if (typeof v !== 'string' || !v.trim()) return null; const u = new URL(v.trim()); if (u.protocol !== 'https:') throw new Error('Image links must start with https://'); return u.toString(); };

/** AIKIA team only: creates a complete venue (program, tiers, owner invite) in one step. */
export async function POST(request: Request) {
  if (!(await getPlatformAdmin())) return NextResponse.json({ error: 'Platform admin access required.' }, { status: 403 });
  let b: Record<string, unknown>;
  try { b = await request.json(); } catch { return NextResponse.json({ error: 'Expected JSON.' }, { status: 400 }); }
  const type = isBusinessType(b.businessType) ? b.businessType : 'cafe';
  const preset = venuePresets[type];
  const name = text(b.name, 2, 80);
  const slug = typeof b.slug === 'string' ? b.slug.trim().toLowerCase() : '';
  const ownerEmail = typeof b.ownerEmail === 'string' ? b.ownerEmail.trim().toLowerCase() : '';
  if (!name || !/^[a-z0-9]+(-[a-z0-9]+)*$/.test(slug)) return NextResponse.json({ error: 'Enter a venue name and a URL name (lowercase letters, numbers, dashes).' }, { status: 400 });
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(ownerEmail)) return NextResponse.json({ error: 'Enter the owner’s email.' }, { status: 400 });
  const rewardTarget = Number(b.rewardTarget ?? preset.rewardTarget);
  if (!Number.isInteger(rewardTarget) || rewardTarget < 1 || rewardTarget > 1000) return NextResponse.json({ error: 'Stamps per reward must be 1–1000.' }, { status: 400 });
  const tierBasis = b.tierBasis === 'spend' ? 'spend' : 'actions';
  const chromeAt = Number(b.chromeAt), pinkAt = Number(b.pinkAt);
  if (!(chromeAt > 0 && pinkAt > chromeAt)) return NextResponse.json({ error: 'Pink must start higher than Chrome, and both above zero.' }, { status: 400 });
  let logo: string | null, hero: string | null;
  try { logo = https(b.logoUrl); hero = https(b.heroUrl); } catch (e) { return NextResponse.json({ error: (e as Error).message }, { status: 400 }); }
  const brandColor = typeof b.brandColor === 'string' && hex.test(b.brandColor) ? b.brandColor : '#A98BFF';

  const admin = createSupabaseAdminClient();
  const { data: venue, error } = await admin.from('venues').insert({
    name, slug, business_type: type, brand_color: brandColor, program_logo_url: logo, hero_image_url: hero, tier_basis: tierBasis,
    action_label: text(b.actionLabel, 2, 24) || preset.actionLabel, balance_label: (text(b.balanceLabel, 2, 9) || preset.balanceLabel).toUpperCase(),
    reward_target: rewardTarget, reward_name: text(b.rewardName, 1, 80) || preset.rewardName,
  }).select('id,slug').single();
  if (error || !venue) return NextResponse.json({ error: error?.code === '23505' ? 'That URL name is already taken.' : error?.message || 'Venue could not be created.' }, { status: 400 });

  const [ink, chrome, pink] = preset.tiers;
  const actions = tierBasis === 'actions' ? [0, Math.round(chromeAt), Math.round(pinkAt)] : [0, chrome.minLifetimeActions, pink.minLifetimeActions];
  const spend = tierBasis === 'spend' ? [0, Math.round(chromeAt * 100), Math.round(pinkAt * 100)] : [0, chrome.minLifetimeSpend * 100, pink.minLifetimeSpend * 100];
  const { error: tierError } = await admin.from('venue_tiers').insert([ink, chrome, pink].map((t, rank) => ({
    venue_id: venue.id, rank, name: t.name, min_lifetime_actions: actions[rank], min_lifetime_spend_paise: spend[rank], benefits: t.benefits, accent_color: t.accentColor,
  })));
  if (tierError) { await admin.from('venues').delete().eq('id', venue.id); return NextResponse.json({ error: tierError.message }, { status: 400 }); }

  const origin = process.env.NEXT_PUBLIC_APP_URL || new URL(request.url).origin;
  const { data: invite, error: inviteError } = await admin.auth.admin.inviteUserByEmail(ownerEmail, { redirectTo: `${origin}/auth/callback?next=/` });
  let ownerId = invite?.user?.id;
  if (!ownerId) {
    // Already a user: look them up instead of inviting.
    const { data: list } = await admin.auth.admin.listUsers({ perPage: 1000 });
    ownerId = list?.users.find(u => u.email?.toLowerCase() === ownerEmail)?.id;
  }
  if (ownerId) await admin.from('venue_team_members').insert({ venue_id: venue.id, user_id: ownerId, role: 'owner' });
  return NextResponse.json({
    venueId: venue.id, joinUrl: `${origin}/join/${venue.slug}`, posterUrl: `${origin}/join/${venue.slug}/poster`,
    ownerInvited: Boolean(ownerId), ownerMessage: ownerId ? (invite?.user ? 'Owner invite email sent.' : 'Owner already had an account and was added.') : `Owner not added: ${inviteError?.message || 'unknown error'}`,
  }, { status: 201 });
}
