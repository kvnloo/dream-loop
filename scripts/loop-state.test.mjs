import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { appendRound, readRounds, validateRound } from './loop-state.mjs';

function tmp(t) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'loop-state-'));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  return dir;
}

test('appendRound validates plus and pro records and readRounds returns them in order', t => {
  const dir = tmp(t);
  assert.equal(readRounds(dir).length, 0);
  appendRound(dir, { score: 6, blockers: ['gate scale'] });
  appendRound(dir, {
    score: { composition: 2, lighting: 2, materials: 1.5, details: 0.5 },
    total: 6, blockers: ['wet floor reflection too dull'], fps_ok: true,
  });
  const rows = readRounds(dir);
  assert.equal(rows.length, 2);
  assert.equal(rows[0].score, 6);
  assert.equal(rows[1].total, 6);
  assert.equal(validateRound(rows[0]), 'plus');
  assert.equal(validateRound(rows[1]), 'pro');
});

test('appendRound refuses invalid records and does not write a partial line', t => {
  const dir = tmp(t);
  assert.throws(() => appendRound(dir, { score: 11, blockers: [] }), /0-10/);
  assert.throws(() => appendRound(dir, { score: { composition: 2, lighting: 2, materials: 2, details: 0.5 }, total: 6.5, blockers: [] }), /fps_ok/);
  assert.equal(fs.existsSync(path.join(dir, 'rounds.jsonl')), false);
});
