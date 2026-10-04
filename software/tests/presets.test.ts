import assert from 'node:assert/strict';
import { test } from 'node:test';
import { venuePresets } from '../src/config/presets.ts';

// Mirrors the validation in the venue theme and tier API routes, so every preset can be saved as-is.
for (const [type, preset] of Object.entries(venuePresets)) {
  test(`${type} preset passes the venue and tier rules`, () => {
    assert.ok(preset.actionLabel.length >= 2 && preset.actionLabel.length <= 24);
    assert.ok(preset.balanceLabel.length >= 2 && preset.balanceLabel.length <= 9);
    assert.equal(preset.balanceLabel, preset.balanceLabel.toUpperCase());
    assert.ok(Number.isInteger(preset.rewardTarget) && preset.rewardTarget >= 1 && preset.rewardTarget <= 1000);
    assert.ok(preset.rewardName.length >= 1 && preset.rewardName.length <= 80);
    assert.match(preset.brandColor, /^#[0-9a-fA-F]{6}$/);
    assert.ok(preset.tiers.length >= 1 && preset.tiers.length <= 8);
    assert.equal(preset.tiers[0].minLifetimeActions, 0);
    preset.tiers.forEach((tier, index) => {
      assert.ok(tier.name.length >= 1 && tier.name.length <= 32);
      assert.match(tier.accentColor, /^#[0-9a-fA-F]{6}$/);
      assert.ok(tier.benefits.length <= 10);
      if (index > 0) assert.ok(tier.minLifetimeActions > preset.tiers[index - 1].minLifetimeActions);
    });
  });
}
