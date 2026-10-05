import { createHmac, randomBytes } from 'node:crypto';
import { NextResponse } from 'next/server';
import { createSupabaseAdminClient } from '@/lib/supabase/admin';
import { issueMemberWallets } from '@/lib/server/member-wallet-sync';

export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';
type Context = { params: Promise<{ slug: string }> };

export async function POST(request: Request, { params }: Context) {
  const { slug } = await params;
  let input: { fullName?: unknown; consent?: unknown };
  try { input = await request.json(); } catch { return NextResponse.json({ error: 'Enter your name and agree to the membership terms.' }, { status: 400 }); }
  const fullName = typeof input.fullName === 'string' ? input.fullName.trim() : '';
  if (!fullName || fullName.length > 120 || input.consent !== true) return NextResponse.json({ error: 'Enter your name and agree to the membership terms.' }, { status: 400 });
  const rateSecret = process.env.JOIN_RATE_LIMIT_SECRET;
  const ip = request.headers.get('x-forwarded-for')?.split(',')[0]?.trim() || (process.env.NODE_ENV !== 'production' ? 'local-development' : '');
  if (!rateSecret || !ip) return NextResponse.json({ error: 'Membership sign-up is temporarily unavailable. Please ask the venue team.' }, { status: 503 });

  const admin = createSupabaseAdminClient();
  const { data: venue } = await admin.from('venues').select('*').eq('slug', slug).maybeSingle();
  if (!venue) return NextResponse.json({ error: 'This loyalty program is not available.' }, { status: 404 });

  // A phone that already joined this venue gets its existing membership and card back instead of a duplicate.
  const cookieName = `aikia_member_${venue.id.slice(0, 8)}`;
  const remembered = readMemberCookie(request.headers.get('cookie'), cookieName, rateSecret);
  if (remembered) {
    const { data: existing } = await admin.from('members').select('id,public_code,status').eq('id', remembered).eq('venue_id', venue.id).maybeSingle();
    if (existing?.status === 'active') {
      const { saveLinks, walletSyncMessage } = await issueMemberWallets(existing.id);
      return NextResponse.json({ member: { publicCode: existing.public_code, saveLinks, returning: true, walletSyncMessage: walletSyncMessage && 'Welcome back. Your wallet card is not available right now; please show this code to the venue team.' } }, { status: 200 });
    }
  }
  const fingerprint = createHmac('sha256', rateSecret).update(ip).digest('hex');
  const { data: allowed, error: limitError } = await admin.rpc('consume_public_join_attempt', {
    p_venue_id: venue.id, p_fingerprint: fingerprint, p_limit: 5, p_window_seconds: 600,
  });
  if (limitError) return NextResponse.json({ error: 'Membership sign-up is temporarily unavailable. Please ask the venue team.' }, { status: 503 });
  if (!allowed) return NextResponse.json({ error: 'Too many sign-up attempts. Please wait a few minutes or ask the venue team.' }, { status: 429 });

  const { data: tier } = await admin.from('venue_tiers').select('*').eq('venue_id', venue.id).eq('min_lifetime_actions', 0).maybeSingle();
  if (!tier) return NextResponse.json({ error: 'This venue has not finished setting up its rewards.' }, { status: 503 });
  const publicCode = `A${randomBytes(5).toString('hex').toUpperCase()}`;
  const { data: member, error: memberError } = await admin.from('members').insert({
    venue_id: venue.id, full_name: fullName, public_code: publicCode, current_tier_id: tier.id,
    consented_at: new Date().toISOString(), consent_version: 'venue-loyalty-v1',
  }).select('*').single();
  if (memberError || !member) return NextResponse.json({ error: 'Your membership could not be created. Please try once more or ask the venue team.' }, { status: 503 });

  const { saveLinks, walletSyncMessage } = await issueMemberWallets(member.id);
  const response = NextResponse.json({ member: { publicCode: member.public_code, saveLinks, walletSyncMessage: walletSyncMessage && 'Your membership is ready. Your wallet card is not available yet; please ask the venue team.' } }, { status: 201 });
  response.cookies.set(cookieName, signMemberCookie(member.id, rateSecret), { httpOnly: true, secure: process.env.NODE_ENV === 'production', sameSite: 'lax', path: '/', maxAge: 60 * 60 * 24 * 400 });
  return response;
}

function signMemberCookie(memberId: string, secret: string) {
  return `${memberId}.${createHmac('sha256', secret).update(`member:${memberId}`).digest('base64url')}`;
}

function readMemberCookie(header: string | null, name: string, secret: string) {
  const raw = header?.split(';').map(part => part.trim()).find(part => part.startsWith(`${name}=`))?.slice(name.length + 1);
  if (!raw) return null;
  const [memberId, signature] = decodeURIComponent(raw).split('.');
  if (!memberId || !signature || !/^[0-9a-f-]{36}$/i.test(memberId)) return null;
  const expected = signMemberCookie(memberId, secret).split('.')[1];
  return signature === expected ? memberId : null;
}
