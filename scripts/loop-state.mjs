#!/usr/bin/env node
// Append-only ledger for `.dream-loop/rounds.jsonl`. No dependencies; Node 18+.
import fs from 'node:fs';
import path from 'node:path';

export const DISCOVERY_SCHEMA_VERSION = 1;
export const DISCOVERY_EVENT = 'discovery_node';
export const DISCOVERY_OUTCOMES = new Set([
  'pending',
  'accepted',
  'rejected',
  'rolled_back',
  'failed',
  'no_update',
]);

function isNum(value) {
  return typeof value === 'number' && Number.isFinite(value);
}

function isPlainObject(value) {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
}

function nonEmptyString(value, field) {
  if (typeof value !== 'string' || value.trim() === '') throw new Error(`${field} must be a non-empty string.`);
}

function jsonSafe(value, field) {
  if (value === null || typeof value === 'string' || typeof value === 'boolean') return;
  if (isNum(value)) return;
  if (Array.isArray(value)) {
    value.forEach((item, index) => jsonSafe(item, `${field}[${index}]`));
    return;
  }
  if (isPlainObject(value)) {
    for (const [key, item] of Object.entries(value)) jsonSafe(item, `${field}.${key}`);
    return;
  }
  throw new Error(`${field} must contain only JSON-safe values.`);
}

function nonNegative(value, field) {
  if (!isNum(value) || value < 0) throw new Error(`${field} must be a non-negative finite number.`);
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

export function validateDiscoveryNode(record) {
  if (!isPlainObject(record)) throw new Error('discovery node must be an object.');
  if (record.event !== DISCOVERY_EVENT) throw new Error(`event must be "${DISCOVERY_EVENT}".`);
  if (record.schema_version !== DISCOVERY_SCHEMA_VERSION) {
    throw new Error(`schema_version must be ${DISCOVERY_SCHEMA_VERSION}.`);
  }

  nonEmptyString(record.run_id, 'run_id');
  nonEmptyString(record.node_id, 'node_id');
  if (record.parent_id !== null) nonEmptyString(record.parent_id, 'parent_id');
  if (record.parent_id === record.node_id) throw new Error('parent_id cannot equal node_id.');

  nonEmptyString(record.hypothesis, 'hypothesis');
  if (record.uncertainty !== null && (!isNum(record.uncertainty) || record.uncertainty < 0 || record.uncertainty > 1)) {
    throw new Error('uncertainty must be null or a number from 0 to 1.');
  }

  if (!isPlainObject(record.intervention)) throw new Error('intervention must be an object.');
  nonEmptyString(record.intervention.type, 'intervention.type');
  if (record.intervention.parameters !== undefined && !isPlainObject(record.intervention.parameters)) {
    throw new Error('intervention.parameters must be an object when present.');
  }
  jsonSafe(record.intervention, 'intervention');

  if (!Array.isArray(record.artifacts) || record.artifacts.some(item => typeof item !== 'string')) {
    throw new Error('artifacts must be an array of strings.');
  }

  if (!isPlainObject(record.measurements)) throw new Error('measurements must be an object.');
  if (!isPlainObject(record.verifiers)) throw new Error('verifiers must be an object.');
  jsonSafe(record.measurements, 'measurements');
  jsonSafe(record.verifiers, 'verifiers');

  if (!DISCOVERY_OUTCOMES.has(record.outcome)) {
    throw new Error(`outcome must be one of: ${[...DISCOVERY_OUTCOMES].join(', ')}.`);
  }

  if (record.rollback_reason !== null && typeof record.rollback_reason !== 'string') {
    throw new Error('rollback_reason must be null or a string.');
  }
  if (record.outcome === 'rolled_back' && (!record.rollback_reason || record.rollback_reason.trim() === '')) {
    throw new Error('rolled_back nodes require rollback_reason.');
  }

  if (!isPlainObject(record.cost)) throw new Error('cost must be an object.');
  nonNegative(record.cost.latency_ms, 'cost.latency_ms');
  nonNegative(record.cost.gpu_ms, 'cost.gpu_ms');
  nonNegative(record.cost.api_usd, 'cost.api_usd');

  nonEmptyString(record.timestamp, 'timestamp');
  if (!Number.isFinite(Date.parse(record.timestamp)) || !record.timestamp.includes('T')) {
    throw new Error('timestamp must be an ISO-8601 date-time string.');
  }

  return 'discovery_node';
}

export function readLedger(dir) {
  const file = path.join(path.resolve(dir), 'rounds.jsonl');
  if (!fs.existsSync(file)) return [];
  return fs.readFileSync(file, 'utf8').split('\n').filter(Boolean).map((line, index) => {
    try { return JSON.parse(line); } catch { throw new Error(`Invalid JSON on rounds.jsonl line ${index + 1}.`); }
  });
}

export function appendRound(dir, record) {
  validateRound(record);
  const folder = path.resolve(dir);
  fs.mkdirSync(folder, { recursive: true });
  fs.appendFileSync(path.join(folder, 'rounds.jsonl'), JSON.stringify(record) + '\n');
  return record;
}

export function readRounds(dir) {
  return readLedger(dir).filter(record => record?.event !== DISCOVERY_EVENT);
}

export function readDiscoveryTree(dir, runId = null) {
  const nodes = [];
  const byId = Object.create(null);
  const children = Object.create(null);
  const rootsByRun = Object.create(null);

  for (const record of readLedger(dir)) {
    if (record?.event !== DISCOVERY_EVENT) continue;
    validateDiscoveryNode(record);

    if (byId[record.node_id]) throw new Error(`duplicate discovery node_id: ${record.node_id}.`);
    if (record.parent_id !== null) {
      const parent = byId[record.parent_id];
      if (!parent) throw new Error(`parent_id ${record.parent_id} must appear before child ${record.node_id}.`);
      if (parent.run_id !== record.run_id) throw new Error(`parent_id ${record.parent_id} belongs to a different run.`);
    } else if (rootsByRun[record.run_id]) {
      throw new Error(`run_id ${record.run_id} already has root ${rootsByRun[record.run_id]}.`);
    } else {
      rootsByRun[record.run_id] = record.node_id;
    }

    byId[record.node_id] = record;
    children[record.node_id] = [];
    if (record.parent_id !== null) children[record.parent_id].push(record.node_id);
    nodes.push(record);
  }

  const selected = runId === null ? nodes : nodes.filter(node => node.run_id === runId);
  const selectedIds = new Set(selected.map(node => node.node_id));
  const selectedById = Object.create(null);
  const selectedChildren = Object.create(null);
  for (const node of selected) {
    selectedById[node.node_id] = node;
    selectedChildren[node.node_id] = children[node.node_id].filter(id => selectedIds.has(id));
  }

  const roots = selected.filter(node => node.parent_id === null).map(node => node.node_id);
  return { nodes: selected, roots, by_id: selectedById, children: selectedChildren };
}

export function appendDiscoveryNode(dir, record) {
  validateDiscoveryNode(record);
  const tree = readDiscoveryTree(dir);

  if (tree.by_id[record.node_id]) throw new Error(`duplicate discovery node_id: ${record.node_id}.`);

  if (record.parent_id === null) {
    const existingRoot = tree.nodes.find(node => node.run_id === record.run_id && node.parent_id === null);
    if (existingRoot) throw new Error(`run_id ${record.run_id} already has root ${existingRoot.node_id}.`);
  } else {
    const parent = tree.by_id[record.parent_id];
    if (!parent) throw new Error(`parent_id ${record.parent_id} does not exist.`);
    if (parent.run_id !== record.run_id) throw new Error(`parent_id ${record.parent_id} belongs to a different run.`);
  }

  const folder = path.resolve(dir);
  fs.mkdirSync(folder, { recursive: true });
  fs.appendFileSync(path.join(folder, 'rounds.jsonl'), JSON.stringify(record) + '\n');
  return record;
}
