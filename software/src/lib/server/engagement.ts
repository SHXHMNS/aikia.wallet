import 'server-only';
import { createSupabaseAdminClient } from '@/lib/supabase/admin';
import { venueWalletConfig } from '@/lib/server/member-wallet-sync';
import { activeProviderIds, getWalletProvider } from '@/lib/wallet/provider';
import type { VenueLocation, WalletMessage } from '@/lib/wallet/types';

type Admin = ReturnType<typeof createSupabaseAdminClient>;
export type Campaign = { id: string; venue_id: string; name: string; kind: 'broadcast' | 'daily' | 'weather_rain' | 'weather_hot' | 'winback'; header: string; body: string; weekdays: number[]; winback_days: number; active: boolean; last_sent_at: string | null };

const IST = 'Asia/Kolkata';
const istDay = (d = new Date()) => new Intl.DateTimeFormat('en-CA', { timeZone: IST }).format(d);
const istWeekday = (d = new Date()) => ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].indexOf(new Intl.DateTimeFormat('en-US', { timeZone: IST, weekday: 'short' }).format(d));

async function venueContext(admin: Admin, venueId: string) {
  const [{ data: venue }, { data: tiers }, { data: locations }] = await Promise.all([
    admin.from('venues').select('*').eq('id', venueId).single(),
    admin.from('venue_tiers').select('name').eq('venue_id', venueId).order('rank'),
    admin.from('venue_locations').select('label,lat,lng,lock_screen_message').eq('venue_id', venueId).order('created_at'),
  ]);
  if (!venue) throw new Error('Venue not found.');
  // With weather moods on, today's mood message replaces each location's nearby text (clear days keep the venue's own text).
  const moods = venue.nearby_moods as NearbyMoods | null;
  const mood = venue.nearby_mood_today as Mood | null;
  const moodText = moods?.enabled && mood && moods[mood] ? moods[mood] : null;
  return { venue, tierNames: (tiers || []).map(t => t.name as string), locations: (locations || []).map(l => ({ label: l.label, lat: l.lat, lng: l.lng, lockScreenMessage: moodText && (mood !== 'clear' || !l.lock_screen_message) ? moodText : l.lock_screen_message })) as VenueLocation[] };
}

/** Pushes the venue's saved locations to every active wallet engine. */
export async function syncVenueLocations(venueId: string) {
  const admin = createSupabaseAdminClient();
  const { venue, tierNames, locations } = await venueContext(admin, venueId);
  for (const id of activeProviderIds()) await getWalletProvider(id).syncVenueLocations(venueWalletConfig(venue), locations, tierNames);
  return locations.length;
}

import { moodFor, type Mood, type NearbyMoods } from '@/lib/mood';
export type { Mood, NearbyMoods };

/** Today's forecast and current conditions at the venue's first location (Open-Meteo, no API key). */
export async function venueWeather(lat: number, lng: number) {
  const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lng}&daily=precipitation_probability_max,temperature_2m_max,temperature_2m_min&current=temperature_2m,precipitation,weather_code&timezone=Asia%2FKolkata&forecast_days=1`;
  const response = await fetch(url, { cache: 'no-store' });
  if (!response.ok) throw new Error(`Weather service ${response.status}`);
  const body = await response.json() as { daily?: { precipitation_probability_max?: number[]; temperature_2m_max?: number[]; temperature_2m_min?: number[] }; current?: { temperature_2m?: number; precipitation?: number; weather_code?: number } };
  return {
    rainChance: body.daily?.precipitation_probability_max?.[0] ?? 0, maxTemp: body.daily?.temperature_2m_max?.[0] ?? 0, minTemp: body.daily?.temperature_2m_min?.[0] ?? 0,
    nowTemp: body.current?.temperature_2m ?? null, nowRain: (body.current?.precipitation ?? 0) > 0, weatherCode: body.current?.weather_code ?? null,
  };
}

/** Works out today's weather mood for one venue, stores it, and pushes the matching nearby message to the cards. */
export async function refreshVenueMood(venueId: string) {
  const admin = createSupabaseAdminClient();
  const { data: loc } = await admin.from('venue_locations').select('lat,lng').eq('venue_id', venueId).order('created_at').limit(1).maybeSingle();
  if (!loc) throw new Error('Add the venue location first (Geofencing).');
  const weather = await venueWeather(loc.lat, loc.lng);
  const mood = moodFor(weather);
  await admin.from('venues').update({ nearby_mood_today: mood, nearby_mood_updated_at: new Date().toISOString() }).eq('id', venueId);
  await syncVenueLocations(venueId);
  const { data: venue } = await admin.from('venues').select('nearby_moods').eq('id', venueId).single();
  return { weather, mood, message: (venue?.nearby_moods as NearbyMoods | null)?.[mood] || '' };
}

/** Sends today's mood message to every card right now (notification on Google; lock-screen text on Apple). */
export async function sendMoodNow(venueId: string) {
  const { mood, message, weather } = await refreshVenueMood(venueId);
  const admin = createSupabaseAdminClient();
  const { venue, tierNames } = await venueContext(admin, venueId);
  const providers = activeProviderIds();
  if (!providers.length) throw new Error('No wallet engine is configured.');
  const header = ({ rain: 'Rainy day', hot: 'Hot day', cold: 'Cool day', clear: venue.name } as Record<Mood, string>)[mood];
  for (const id of providers) await getWalletProvider(id).broadcastMessage(venueWalletConfig(venue), { id: `mood${Date.now().toString(36)}`, header, body: message }, tierNames);
  await admin.from('campaign_sends').insert({ venue_id: venueId, trigger: 'manual', audience: 0, status: 'sent', detail: `Weather mood "${mood}": ${message}`.slice(0, 400) });
  return { mood, message, weather };
}

async function lapsedMembers(admin: Admin, venueId: string, days: number) {
  // Members whose last visit (or join, if they never visited) falls on exactly `days` days ago — each lapsed member is nudged once.
  const { data: members } = await admin.from('members').select('id,created_at').eq('venue_id', venueId).eq('status', 'active');
  const { data: visits } = await admin.from('ledger_transactions').select('member_id,created_at').eq('venue_id', venueId).eq('event_type', 'qualifying_action').order('created_at', { ascending: false });
  const last = new Map<string, string>();
  for (const v of visits || []) if (!last.has(v.member_id)) last.set(v.member_id, v.created_at);
  const target = istDay(new Date(Date.now() - days * 86400000));
  return (members || []).filter(m => istDay(new Date(last.get(m.id) || m.created_at)) === target).map(m => m.id as string);
}

/** Sends one campaign now. Returns how many cards were reached. */
export async function sendCampaign(campaign: Campaign, trigger: 'manual' | 'scheduled') {
  const admin = createSupabaseAdminClient();
  const { venue, tierNames } = await venueContext(admin, campaign.venue_id);
  const providers = activeProviderIds();
  const message: WalletMessage = { id: `c${campaign.id.replace(/-/g, '').slice(0, 20)}${Date.now().toString(36)}`, header: campaign.header, body: campaign.body };
  let audience = 0; let status: 'sent' | 'skipped' | 'failed' = 'sent'; let detail = '';
  try {
    if (!providers.length) throw new Error('No wallet engine is configured.');
    if (campaign.kind === 'winback') {
      const ids = await lapsedMembers(admin, campaign.venue_id, campaign.winback_days);
      const { data: passes } = ids.length ? await admin.from('wallet_passes').select('member_id,provider,provider_class_id,provider_object_id').in('member_id', ids) : { data: [] };
      for (const p of passes || []) {
        if (!providers.includes(p.provider)) continue;
        if (await getWalletProvider(p.provider).messageMember({ classId: p.provider_class_id, objectId: p.provider_object_id }, message)) audience += 1;
      }
      if (!audience) { status = 'skipped'; detail = ids.length ? 'This wallet engine cannot message single members yet (works on the Google engine).' : 'No members became inactive today.'; }
    } else {
      for (const id of providers) await getWalletProvider(id).broadcastMessage(venueWalletConfig(venue), message, tierNames);
      await admin.from('venues').update({ current_offer: `${campaign.header}: ${campaign.body}`.slice(0, 200) }).eq('id', campaign.venue_id);
      const { count } = await admin.from('wallet_passes').select('member_id', { count: 'exact', head: true }).eq('venue_id', campaign.venue_id);
      audience = count || 0;
    }
  } catch (error) { status = 'failed'; detail = error instanceof Error ? error.message.slice(0, 400) : 'Send failed.'; }
  await admin.from('campaign_sends').insert({ campaign_id: campaign.id, venue_id: campaign.venue_id, trigger, audience, status, detail: detail || null });
  if (status === 'sent') await admin.from('campaigns').update({ last_sent_at: new Date().toISOString() }).eq('id', campaign.id);
  return { status, audience, detail };
}

/** Daily run (cron): sends every active campaign whose condition matches today. Each campaign sends at most once per IST day. */
export async function runDueCampaigns() {
  const admin = createSupabaseAdminClient();
  // Morning weather check: each venue with moods switched on gets today's nearby message.
  const { data: moodVenues } = await admin.from('venues').select('id').eq('nearby_moods->>enabled', 'true');
  for (const v of moodVenues || []) await refreshVenueMood(v.id).catch(() => null);
  const { data: campaigns } = await admin.from('campaigns').select('*').eq('active', true).neq('kind', 'broadcast');
  const today = istDay(); const weekday = istWeekday();
  const weatherCache = new Map<string, { rainChance: number; maxTemp: number } | null>();
  const results = [];
  for (const c of (campaigns || []) as Campaign[]) {
    if (c.last_sent_at && istDay(new Date(c.last_sent_at)) === today) continue;
    if (!c.weekdays.includes(weekday)) continue;
    if (c.kind === 'weather_rain' || c.kind === 'weather_hot') {
      if (!weatherCache.has(c.venue_id)) {
        const { data: loc } = await admin.from('venue_locations').select('lat,lng').eq('venue_id', c.venue_id).order('created_at').limit(1).maybeSingle();
        weatherCache.set(c.venue_id, loc ? await venueWeather(loc.lat, loc.lng).catch(() => null) : null);
      }
      const w = weatherCache.get(c.venue_id);
      if (!w || (c.kind === 'weather_rain' && w.rainChance < 60) || (c.kind === 'weather_hot' && w.maxTemp < 35)) continue;
    }
    results.push({ campaign: c.name, ...(await sendCampaign(c, 'scheduled')) });
  }
  return results;
}
