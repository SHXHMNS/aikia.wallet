import 'server-only';
import { createSupabaseAdminClient } from '@/lib/supabase/admin';

/** The member access token is the only key to a guest's private page; it is 48 hex characters. */
export const validAccessToken = (token: string) => /^[0-9a-f]{48}$/.test(token);

/** Everything the guest's private "My card" page shows. Returns null for an unknown or suspended card. */
export async function loadMemberCard(token: string) {
  if (!validAccessToken(token)) return null;
  const admin = createSupabaseAdminClient();
  const { data: member } = await admin.from('members')
    .select('id,venue_id,full_name,public_code,stamp_balance,rewards_available,lifetime_actions,current_tier_id,credit_paid_paise,credit_bonus_paise,status')
    .eq('access_token', token).maybeSingle();
  if (!member || member.status !== 'active') return null;
  const [{ data: venue }, { data: tier }, { data: tiers }, { data: items }, { data: gifts }] = await Promise.all([
    admin.from('venues').select('name,slug,balance_label,action_label,reward_target,reward_name,credit_enabled,credit_packs,tapless_limit_paise,gift_daily_limit,gift_valid_days').eq('id', member.venue_id).single(),
    admin.from('venue_tiers').select('name,benefits').eq('id', member.current_tier_id).maybeSingle(),
    admin.from('venue_tiers').select('name,rank').eq('venue_id', member.venue_id).order('rank'),
    admin.from('gift_items').select('id,name,credit_cost_paise').eq('venue_id', member.venue_id).eq('active', true).order('sort'),
    admin.from('gifts').select('id,token,item_name,quantity,source,status,recipient_name,expires_at,redeemed_at,created_at').eq('sender_member_id', member.id).order('created_at', { ascending: false }).limit(10),
  ]);
  if (!venue) return null;
  return {
    member: {
      firstName: member.full_name.split(/\s+/)[0] as string, fullName: member.full_name as string, publicCode: member.public_code as string,
      stampBalance: member.stamp_balance as number, rewardsAvailable: member.rewards_available as number, lifetimeActions: member.lifetime_actions as number,
      creditPaise: Number(member.credit_paid_paise || 0) + Number(member.credit_bonus_paise || 0),
      tier: (tier?.name || 'Member') as string, tierBenefits: (tier?.benefits || []) as string[],
    },
    venue: {
      name: venue.name as string, slug: venue.slug as string, balanceLabel: venue.balance_label as string, actionLabel: venue.action_label as string,
      rewardTarget: venue.reward_target as number, rewardName: venue.reward_name as string,
      creditEnabled: Boolean(venue.credit_enabled), creditPacks: (venue.credit_packs || []) as { pay: number; get: number }[], taplessLimitPaise: Number(venue.tapless_limit_paise),
      giftDailyLimit: venue.gift_daily_limit as number, giftValidDays: venue.gift_valid_days as number, tiers: (tiers || []).map(t => t.name as string),
    },
    giftItems: (items || []).map(i => ({ id: i.id as string, name: i.name as string, pricePaise: Number(i.credit_cost_paise) })),
    gifts: (gifts || []).map(g => ({
      id: g.id as string, token: g.token as string, itemName: g.item_name as string, quantity: g.quantity as number, source: g.source as string,
      status: (g.status === 'active' && new Date(g.expires_at) < new Date() ? 'expired' : g.status) as string,
      recipientName: g.recipient_name as string | null, expiresAt: g.expires_at as string, redeemedAt: g.redeemed_at as string | null,
    })),
  };
}

export type MemberCard = NonNullable<Awaited<ReturnType<typeof loadMemberCard>>>;
