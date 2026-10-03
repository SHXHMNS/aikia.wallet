import { NextResponse } from 'next/server';
import { getVenueRole } from '@/lib/server/venue-access';

type Context = { params: Promise<{ venueId: string }> };
const color = /^#[0-9a-fA-F]{6}$/;

export async function PUT(request: Request, { params }: Context) {
  const { venueId } = await params;
  const access = await getVenueRole(venueId);
  if (!access) return NextResponse.json({ error: 'Venue access required.' }, { status: 401 });
  if (access.role === 'staff') return NextResponse.json({ error: 'Owner or admin access required.' }, { status: 403 });
  let input: { tiers?: unknown };
  try { input = await request.json(); } catch { return NextResponse.json({ error: 'Expected JSON.' }, { status: 400 }); }
  if (!Array.isArray(input.tiers) || input.tiers.length < 1 || input.tiers.length > 8) return NextResponse.json({ error: 'Add between one and eight tiers.' }, { status: 400 });
  const tiers = input.tiers.map((item, rank) => {
    const tier = item as Record<string, unknown>;
    return {
      rank,
      name: typeof tier.name === 'string' ? tier.name.trim() : '',
      min_lifetime_actions: Number(tier.minLifetimeActions),
      benefits: Array.isArray(tier.benefits) ? tier.benefits.filter((benefit): benefit is string => typeof benefit === 'string').map(s => s.trim()).filter(Boolean).slice(0, 10) : [],
      accent_color: typeof tier.accentColor === 'string' ? tier.accentColor : '#171421',
    };
  });
  if (tiers.some(t => !t.name || t.name.length > 32 || !Number.isInteger(t.min_lifetime_actions) || t.min_lifetime_actions < 0 || !color.test(t.accent_color))) return NextResponse.json({ error: 'Each tier needs a name, a non-negative whole action threshold, and a valid color.' }, { status: 400 });
  if (tiers[0].min_lifetime_actions !== 0 || tiers.some((t, i) => i > 0 && t.min_lifetime_actions <= tiers[i - 1].min_lifetime_actions)) return NextResponse.json({ error: 'Start the first tier at zero and increase thresholds at every level.' }, { status: 400 });
  const { error } = await access.supabase.rpc('replace_venue_tiers', { p_venue_id: venueId, p_tiers: tiers });
  if (error) return NextResponse.json({ error: error.message }, { status: 400 });
  return NextResponse.json({ saved: true });
}
