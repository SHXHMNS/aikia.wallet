import assert from 'node:assert/strict';
import { createHmac } from 'node:crypto';
import { test } from 'node:test';
import { passKitSaveLinks, passKitTierId, passUrlBaseFor, signPassKitToken } from '../src/lib/wallet/passkit-core.ts';

test('PassKit JWT carries the API key as uid, expires in 60s and verifies with the secret', () => {
  const token = signPassKitToken('key-123', 'secret-xyz', 1_000);
  const [header, body, signature] = token.split('.');
  assert.deepEqual(JSON.parse(Buffer.from(header, 'base64url').toString()), { alg: 'HS256', typ: 'JWT' });
  assert.deepEqual(JSON.parse(Buffer.from(body, 'base64url').toString()), { uid: 'key-123', iat: 1_000, exp: 1_060 });
  assert.equal(signature, createHmac('sha256', 'secret-xyz').update(`${header}.${body}`).digest('base64url'));
});

test('pass URLs follow the API region', () => {
  assert.equal(passUrlBaseFor('https://api.pub1.passkit.io'), 'https://pub1.pskt.io/');
  assert.equal(passUrlBaseFor('https://api.pub2.passkit.io'), 'https://pub2.pskt.io/');
  assert.equal(passUrlBaseFor('https://api.pub2.passkit.io', 'https://cards.example.com'), 'https://cards.example.com/');
});

test('save links open Google Wallet now and Apple Wallet once enabled', () => {
  assert.deepEqual(passKitSaveLinks('https://pub1.pskt.io/', 'abc123', false), { google: 'https://pub1.pskt.io/abc123.gpay' });
  assert.deepEqual(passKitSaveLinks('https://pub1.pskt.io/', 'abc123', true), { google: 'https://pub1.pskt.io/abc123.gpay', apple: 'https://pub1.pskt.io/abc123.pkpass' });
});

test('tier IDs default to the lowercase tier name and accept overrides', () => {
  assert.equal(passKitTierId('Ink'), 'ink');
  assert.equal(passKitTierId('Rose Gold'), 'rose-gold');
  assert.equal(passKitTierId('Ink', { Ink: 'base' }), 'base');
});
