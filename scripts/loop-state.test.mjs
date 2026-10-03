import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {
  DISCOVERY_EVENT,
  DISCOVERY_SCHEMA_VERSION,
  appendDiscoveryNode,
  appendRound,
  readDiscoveryTree,
  readLedger,
  readRounds,
  validateDiscoveryNode,
  validateRound,
} from './loop-state.mjs';

function tmp(t) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'loop-state-'));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  return dir;
}

function node(overrides = {}) {
  return {
    event: DISCOVERY_EVENT,
    schema_version: DISCOVERY_SCHEMA_VERSION,
    run_id: 'run-a',
    node_id: 'root',
    parent_id: null,
    hypothesis: 'initial locked target and scene state',
    uncertainty: 0.8,
    intervention: { type: 'ROOT', parameters: {} },
    artifacts: ['.dream-loop/target.png'],
    measurements: { composition: 1.5 },
    verifiers: { crop_gate: { ok: false } },
    outcome: 'pending',
    rollback_reason: null,
    cost: { latency_ms: 12, gpu_ms: 0, api_usd: 0 },
    timestamp: '2026-10-03T04:20:00Z',
    ...overrides,
  };
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

test('discovery nodes share the append-only ledger without changing legacy readRounds', t => {
  const dir = tmp(t);
  appendRound(dir, { score: 5, blockers: ['camera'] });
  appendDiscoveryNode(dir, node());
  appendDiscoveryNode(dir, node({
    node_id: 'camera-left',
    parent_id: 'root',
    hypothesis: 'moving camera left improves framing',
    intervention: { type: 'EXPLORE', parameters: { coordinate: 'camera.x', delta: -0.2 } },
    outcome: 'rejected',
    cost: { latency_ms: 800, gpu_ms: 740, api_usd: 0.002 },
    timestamp: '2026-10-03T04:21:00Z',
  }));

  assert.equal(readLedger(dir).length, 3);
  assert.equal(readRounds(dir).length, 1);

  const tree = readDiscoveryTree(dir, 'run-a');
  assert.deepEqual(tree.roots, ['root']);
  assert.equal(tree.nodes.length, 2);
  assert.deepEqual(tree.children.root, ['camera-left']);
  assert.equal(tree.by_id['camera-left'].outcome, 'rejected');
});

test('appendDiscoveryNode retains rejected and rolled-back branches', t => {
  const dir = tmp(t);
  appendDiscoveryNode(dir, node());
  appendDiscoveryNode(dir, node({
    node_id: 'candidate',
    parent_id: 'root',
    outcome: 'accepted',
    timestamp: '2026-10-03T04:21:00Z',
  }));
  appendDiscoveryNode(dir, node({
    node_id: 'rollback',
    parent_id: 'candidate',
    intervention: { type: 'ROLLBACK', parameters: { to: 'root' } },
    outcome: 'rolled_back',
    rollback_reason: 'composition regressed',
    timestamp: '2026-10-03T04:22:00Z',
  }));

  const tree = readDiscoveryTree(dir);
  assert.equal(tree.nodes.length, 3);
  assert.equal(tree.by_id.rollback.rollback_reason, 'composition regressed');
});

test('appendDiscoveryNode rejects disconnected, duplicate, cross-run, and second-root writes without partial lines', t => {
  const dir = tmp(t);
  appendDiscoveryNode(dir, node());

  assert.throws(() => appendDiscoveryNode(dir, node({ node_id: 'orphan', parent_id: 'missing' })), /does not exist/);
  assert.throws(() => appendDiscoveryNode(dir, node()), /duplicate/);
  assert.throws(() => appendDiscoveryNode(dir, node({ node_id: 'root-2' })), /already has root/);
  assert.throws(() => appendDiscoveryNode(dir, node({
    run_id: 'run-b',
    node_id: 'cross-run',
    parent_id: 'root',
  })), /different run/);

  assert.equal(readDiscoveryTree(dir).nodes.length, 1);
});

test('validateDiscoveryNode enforces bounded uncertainty, durable costs, and rollback reasons', () => {
  assert.equal(validateDiscoveryNode(node()), 'discovery_node');
  assert.throws(() => validateDiscoveryNode(node({ uncertainty: 1.1 })), /0 to 1/);
  assert.throws(() => validateDiscoveryNode(node({ cost: { latency_ms: -1, gpu_ms: 0, api_usd: 0 } })), /non-negative/);
  assert.throws(() => validateDiscoveryNode(node({ timestamp: 'yesterday' })), /ISO-8601/);
  assert.throws(() => validateDiscoveryNode(node({ outcome: 'rolled_back' })), /rollback_reason/);
});
