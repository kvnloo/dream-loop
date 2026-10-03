#!/usr/bin/env node
// Round ledger for `.dream-loop/rounds.jsonl`. No dependencies; Node 18+.
import fs from 'node:fs';
import path from 'node:path';

function isNum(value) {
  return typeof value === 'number' && Number.isFinite(value);
}

export function validateRound(record) {
  if (!record || typeof record !== 'object' || Array.isArray(record)) throw new Error('round record must be an object.');
  if (!Array.isArray(record.blockers) || record.blockers.some(item => typeof item !== 'string')) {
    throw new Error('blockers must be an array of strings.');
  }
  if (typeof record.score === 'number') {
    if (!isNum(record.score) || record.score < 0 || record.score > 10) throw new Error('score must be 0-10.');
    return 'plus';
  }
  if (record.score && typeof record.score === 'object' && !Array.isArray(record.score)) {
    const { composition, lighting, materials, details } = record.score;
    if (![composition, lighting, materials].every(n => isNum(n) && n >= 0 && n <= 3)) {
      throw new Error('composition, lighting, and materials must be numbers from 0 to 3.');
    }
    if (!(isNum(details) && details >= 0 && details <= 1)) throw new Error('details must be a number from 0 to 1.');
    if (!(isNum(record.total) && record.total >= 0 && record.total <= 10)) throw new Error('total must be 0-10.');
    if (typeof record.fps_ok !== 'boolean') throw new Error('fps_ok must be a boolean.');
    return 'pro';
  }
  throw new Error('score must be a number (plus critic) or a rubric object (pro judge).');
}

export function appendRound(dir, record) {
  validateRound(record);
  const folder = path.resolve(dir);
  fs.mkdirSync(folder, { recursive: true });
  const line = JSON.stringify(record) + '\n';
  fs.appendFileSync(path.join(folder, 'rounds.jsonl'), line);
  return record;
}

export function readRounds(dir) {
  const file = path.join(path.resolve(dir), 'rounds.jsonl');
  if (!fs.existsSync(file)) return [];
  return fs.readFileSync(file, 'utf8').split('\n').filter(Boolean).map((line, index) => {
    try { return JSON.parse(line); } catch { throw new Error(`Invalid JSON on rounds.jsonl line ${index + 1}.`); }
  });
}
