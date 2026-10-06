import { NextResponse } from 'next/server';
import { isBusinessType, venuePresets } from '@/config/presets';
import { createSupabaseServerClient } from '@/lib/supabase/server';

export async function POST(request: Request) {
  const supabase = await createSupabaseServerClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: 'Sign in first.' }, { status: 401 });
  let input: unknown;
  try { input = await request.json(); } catch { return NextResponse.json({ error: 'Expected JSON.' }, { status: 400 }); }
  const body = input as { name?: unknown; slug?: unknown; businessType?: unknown };
  const name = typeof body.name === 'string' ? body.name.trim() : '';
  const slug = typeof body.slug === 'string' ? body.slug.trim().toLowerCase() : '';
  if (name.length < 2 || name.length > 80 || !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug)) {
    return NextResponse.json({ error: 'Enter a venue name and a URL-safe slug.' }, { status: 400 });
  }
  const { data, error } = await supabase.rpc('create_venue', { p_name: name, p_slug: slug });
  if (error) return NextResponse.json({ error: error.message }, { status: 400 });
  // create_venue seeds the café program; apply the chosen business type on top of it.
  const businessType = isBusinessType(body.businessType) ? body.businessType : 'cafe';
  if (businessType !== 'cafe') {
    const preset = venuePresets[businessType];
    const venueId = data as string;
    const { error: venueError } = await supabase.from('venues').update({
      business_type: businessType, action_label: preset.actionLabel, balance_label: preset.balanceLabel,
      reward_target: preset.rewardTarget, reward_name: preset.rewardName, brand_color: preset.brandColor,
    }).eq('id', venueId);
    const { error: tierError } = await supabase.rpc('replace_venue_tiers', {
      p_venue_id: venueId,
      p_tiers: preset.tiers.map((tier, rank) => ({ rank, name: tier.name, min_lifetime_actions: tier.minLifetimeActions, min_lifetime_spend_paise: tier.minLifetimeSpend * 100, benefits: tier.benefits, accent_color: tier.accentColor })),
    });
    if (venueError || tierError) return NextResponse.json({ venueId, warning: 'Venue created with the café starter program; the business preset could not be applied. Adjust it in Brand & tiers.' }, { status: 201 });
  }
  return NextResponse.json({ venueId: data }, { status: 201 });
}
