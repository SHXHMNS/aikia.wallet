import { NextResponse } from 'next/server';
import { loadMemberCard } from '@/lib/server/member-card';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
type Context = { params: Promise<{ token: string }> };

/** Guest's private card page data (balances, gift menu, gifts sent). Authorised by the secret link only. */
export async function GET(_r: Request, { params }: Context) {
  const { token } = await params;
  const card = await loadMemberCard(token);
  if (!card) return NextResponse.json({ error: 'This card link is not valid.' }, { status: 404 });
  return NextResponse.json(card, { headers: { 'cache-control': 'no-store' } });
}
