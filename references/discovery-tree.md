# Dream-RSI discovery tree

Dream Loop keeps the full search history in the existing append-only `.dream-loop/rounds.jsonl` ledger. Legacy Plus/Pro judge rows remain unchanged. Dream-RSI adds typed `discovery_node` events beside them.

A failed branch is evidence. Do not delete rejected or rolled-back nodes.

## Node contract

Every attempted intervention records:

```json
{
  "event": "discovery_node",
  "schema_version": 1,
  "run_id": "run-2026-10-03-a",
  "node_id": "camera-left-1",
  "parent_id": "root",
  "hypothesis": "moving the camera left improves framing",
  "uncertainty": 0.6,
  "intervention": {
    "type": "EXPLORE",
    "parameters": { "coordinate": "camera.x", "delta": -0.2 }
  },
  "artifacts": [".dream-loop/captures/round-2.png"],
  "measurements": { "composition": 2.0, "total": 5.5 },
  "verifiers": { "crop_gate": { "ok": true } },
  "outcome": "rejected",
  "rollback_reason": null,
  "cost": { "latency_ms": 820, "gpu_ms": 740, "api_usd": 0.002 },
  "timestamp": "2026-10-03T04:21:00Z"
}
```

Valid outcomes: `pending`, `accepted`, `rejected`, `rolled_back`, `failed`, `no_update`.

## Invariants

- `node_id` is unique across the ledger.
- Each `run_id` has exactly one root (`parent_id: null`) once a run has started.
- A parent must already exist before its child is appended.
- Parent and child must have the same `run_id`.
- `uncertainty` is `null` or 0..1.
- Costs are explicit non-negative numbers; zero is valid.
- `rolled_back` requires a non-empty `rollback_reason`.
- Intervention, measurements, and verifier payloads must be JSON-safe.
- Never rewrite history to hide a failed branch.

## API

`scripts/loop-state.mjs` exports:

- `appendDiscoveryNode(dir, node)` — validate tree invariants, then append atomically as one JSONL line.
- `readDiscoveryTree(dir, runId?)` — return ordered nodes, roots, `by_id`, and child adjacency.
- `readLedger(dir)` — return all legacy and Dream-RSI events in append order.
- `readRounds(dir)` — compatibility view containing legacy critic/judge rows only.

The replay layer should consume `readDiscoveryTree()`, not reconstruct branches from score history.

## Compatibility

Do not migrate or rewrite old `rounds.jsonl` files. New discovery events can start at any point in an existing ledger. Legacy `appendRound()`, `validateRound()`, and `readRounds()` remain supported.
