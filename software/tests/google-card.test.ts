import assert from 'node:assert/strict';
import { test } from 'node:test';
import { googleCardLayout, googleTextModules, tierArtSlug } from '../src/lib/wallet/google-card.ts';

test('every text module the card layout points at is filled in', () => {
  const modules = googleTextModules({ fullName: 'Aarav Shah', tierName: 'Chrome', tierBenefits: ['Free upgrade'], rewardsAvailable: 1 });
  const ids = new Set(modules.map(m => m.id));
  const referenced = JSON.stringify(googleCardLayout).match(/textModulesData\['([^']+)'\]/g)!.map(s => s.slice(17, -2));
  for (const id of referenced) assert.ok(ids.has(id), `missing module ${id}`);
  assert.equal(modules.find(m => m.id === 'first-name')!.body, 'Aarav');
  assert.equal(modules.find(m => m.id === 'last-name')!.body, 'Shah');
  assert.equal(modules.find(m => m.id === 'rewards-ready')!.body, '1');
});

test('tier artwork falls back to ink for custom tier names', () => {
  assert.equal(tierArtSlug('Pink'), 'pink');
  assert.equal(tierArtSlug(' chrome '), 'chrome');
  assert.equal(tierArtSlug('Gold'), 'ink');
});
