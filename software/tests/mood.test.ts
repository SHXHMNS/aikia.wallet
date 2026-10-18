import assert from 'node:assert/strict';
import { test } from 'node:test';
import { moodFor } from '../src/lib/mood.ts';

const base = { rainChance: 10, maxTemp: 30, minTemp: 22, nowTemp: 28, nowRain: false, weatherCode: 1 };

test('rain wins over heat', () => {
  assert.equal(moodFor({ ...base, maxTemp: 38, rainChance: 70 }), 'rain');
  assert.equal(moodFor({ ...base, nowRain: true }), 'rain');
  assert.equal(moodFor({ ...base, weatherCode: 63 }), 'rain');
});

test('hot, cold and clear days', () => {
  assert.equal(moodFor({ ...base, maxTemp: 36 }), 'hot');
  assert.equal(moodFor({ ...base, minTemp: 12, nowTemp: 16 }), 'cold');
  assert.equal(moodFor(base), 'clear');
});
