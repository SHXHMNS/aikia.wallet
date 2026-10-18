// Pure weather-mood rules (no server-only import) so they can be unit-tested with node --test.

export type Mood = 'rain' | 'hot' | 'cold' | 'clear';
export type NearbyMoods = { enabled: boolean } & Record<Mood, string>;
export type WeatherReading = { rainChance: number; maxTemp: number; minTemp: number; nowTemp: number | null; nowRain: boolean; weatherCode: number | null };

/** Rain wins, then heat, then cold; otherwise a clear-day message. WMO codes 51-67, 80-82 and 95-99 are rain or storms. */
export function moodFor(w: WeatherReading): Mood {
  const code = w.weatherCode ?? -1;
  if (w.nowRain || w.rainChance >= 60 || (code >= 51 && code <= 67) || (code >= 80 && code <= 82) || code >= 95) return 'rain';
  if (w.maxTemp >= 35 || (w.nowTemp ?? 0) >= 34) return 'hot';
  if (w.minTemp <= 15 || (w.nowTemp !== null && w.nowTemp <= 17)) return 'cold';
  return 'clear';
}

