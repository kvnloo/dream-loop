# Blender meta-learning loop

`python scripts/meta_loop.py --help` is the executable entry point. It learns from immutable observations, not edits to the model's weights. Python 3.10+, `jsonschema` (with `referencing`) and Pillow (existing A/B helper) are required. The learner itself does not import bpy, contact models or start renders.

## Commands

```sh
python scripts/meta_loop.py --data /path/to/meta-loop report --evals /path/to/evals
python scripts/meta_loop.py --data /path/to/meta-loop next --element night-banner
python scripts/meta_loop.py --data /path/to/meta-loop next --element night-stone --exploration-slots 2
python scripts/meta_loop.py --data /path/to/meta-loop calibrate --evals /path/to/evals
python scripts/meta_loop.py --data /path/to/meta-loop calibrate --evals /path/to/evals --prepare-ab /new/judge-packets
python scripts/meta_loop.py --data /path/to/meta-loop watch --interval 900 --polls 17
python scripts/meta_loop.test.py
python scripts/run_tests.py
```

The watch is foreground, bounded to at most four hours of waits (17 polls), and does not outlive the caller. Do not detach a polling loop. Use one report/ingest writer; concurrent lanes have separate event files. `--execute` on calibration explicitly opts into paid fresh A/B calls. Preparation alone makes no calls. Existing calibration results are not results from newly prepared packets.

## Owner rating app

See [owner-rating.md](owner-rating.md) for the keyboard-first loopback app, source-bound queue seeding, inferred-history confirmation, and disposable browser verification. Owner events are a separate append-only overlay; no producer lane is rewritten.

## Contracts and extension

`templates/meta-trial.schema.json` reuses discovery-observation v2 artifact, cohort, ID and timestamp definitions. The original `rounds.schema.json` accepts an optional `meta_trial`; its old required fields and additional-property restriction remain. Legacy v1 `loop-state.mjs` is unchanged. Partial historical imports stay intake records, never fake complete discovery observations. Map trial_id to node_id, first parent to primary_parent, and remaining parents to dependency_ids. Historical rounds are not rewritten.

Each lane appends complete newline-terminated events; a new event_id revises an existing trial_id. Element/run/stable-defect identity cannot change across native revisions. Parent corrections (e.g. resolving a provisional batch alias to actual trial IDs) retain `parent_history` and rerun cycle quarantine; raw events remain unchanged. Producer mechanism-label corrections retain `classification_history` and move the same observation between groups rather than creating another trial. A substantively new intervention needs a new trial ID. Duplicate identical events are ignored; conflicting IDs and cross-lane ownership are errors. An unfinished final line is deferred. Cycles are quarantined; unresolved external parents remain visible. A formal valid native event supersedes pre-contract intake for that same trial without double counting; raw intake stays on disk and in `superseded-intake.json`. The two explicit legacy lane adapters retain all original tokens under `source.raw`; they do not silently guess missing acceptance, timestamps or gate outcomes.

Generated artifacts (`ledger.json`, `payoffs.json`, `replay.json`, next portfolios, recipe cards, HTML) are rebuildable projections. `events/` is the authority. Revisions replace a trial's statistical observation rather than incrementing the denominator. Artifact hash checks are recomputed from disk, not trusted from a lane flag. `polls.jsonl` records live refresh summaries. Single-writer ownership is cooperative, not a security boundary.

## Payoff and portfolio

Each element × mechanism has separate Beta(1,1) posteriors for owner acceptance, qualified judge wins, historical kept decisions and evidenced max-zoom passes. Historical keep is NOT owner acceptance. Unknowns, ties and abstentions do not become failures. Judge votes are admitted only with a matching registered prospective calibration, an evidence-verified verdict and a receipt. Repeated agreeing votes count once; disagreement abstains. The current three-pair diagnostic is deliberately unqualified.

The 95% interval uses deterministic seeded Beta samples. These are descriptive uncertainty estimates, not proof of IID trials; projects, difficulty and coupled interventions confound mechanism comparisons. Costs preserve measured phase scope and missing values. GPU utilization seconds are not inferred from render elapsed time. Report-level priors do not invent subtrial outcomes.

Default portfolio: four slots, two for breadth and two for depth/repair/recombination. Pending representations are not dispatched again. No established winner means an evidence/interpretation repair, not a made-up best. Two nonwins against the same stable defect request a checkpoint or mechanism switch, never global termination. Implementation/resource/evidence failures are not counted as failed mechanism hypotheses. Recombination requires two gated winning recipes. The default banner mechanism space excludes geometry/light/post changes; it is a proposal subject to the owner brief, not execution permission.

## Stuck-defect dream step

```sh
python scripts/meta_loop.py --data /path/to/meta-loop stuck
python scripts/meta_loop.py --data /path/to/meta-loop dream --element night-stone
python scripts/meta_loop.py --data /path/to/meta-loop dream --element night-banner --defect banner-final-density
python scripts/dream_step.test.py
```

`stuck` detects two timestamped assessed visual nonwins within an element/stable defect. Unknowns, controls, delivery records, pending reviews and implementation/resource/evidence errors do not count. Same configurations without distinct scene evidence count once; a later evidenced success clears the streak. Explicit producer failures remain diagnostic observations, not owner labels or calibrated payoff. The greenery lane has the analytical subelement `night-banner-greenery`; native producer identity is preserved.

`dream` writes ranked JSON/Markdown portfolios under `dream/`, with exact source IDs and hash-bound starting artifacts. It includes taxonomy breadth (with under-tried classes), quoted cross-lane partial-feature recombinations, compatible other-element recipe components, breadth/depth/earlier-switch prefix audits, and one wildcard. Cost anchors are recorded source-trial medians, not measured coupon times. Hypotheses and rank are explicit heuristics, not visual payoff predictions. Mechanism+semantic-parameter similarity with a 15% numeric tolerance suppresses nearby failed clones; missing common parameters cannot prove novelty. The fixed taxonomy distinguishes actual construction changes from renamed families. Pending mechanisms and completed renders awaiting review are withheld as full `reserved_directions`, not dispatched twice. Identical proposals across defects are consolidated with all covered defect IDs and evidence retained. When active producers prevent a stable long read, freeze the small event/calibration streams with immediate source/copy hash verification, then hash artifacts once and publish all element portfolios from that shared snapshot. Retain the snapshot timestamp and original path/hash manifest; do not disable the live CLI's fail-closed guard.

`next` automatically includes the dream portfolio for stuck elements. Invalid streams block both the legacy batch and the dream. `stuck`, `dream` and `next` now use read-only ingestion with before/after archive hash checks, so they do not race the owner server's ledger/report writer. Only `dream` writes its own portfolio files. Exact defect requests use hash-suffixed filenames and cannot replace an all-defect portfolio. No owner events, CURRENT pointers, scene files or model weights are changed.

The new replay is a timestamped **materialized-observation** support audit; it does not reconstruct original-time revision histories. Decisions see strictly earlier rows, never equal-time peers. Mechanism matches are weak support, not exact parameter/parent matches. Unknown outcomes and policy values stay null. Exploration gaps are places an earlier-switch rule would allocate differently—not predictions that unexplored branches would succeed. Full behavioral tests exercise these limits.

## Dream-RSI-style replay — bounded claim

Replay groups only rows with explicit original-ledger locators; file mtimes do not establish decision order. Unknown mechanism classifications are excluded. Each recommendation sees only the earlier prefix, using one fixed mechanism action space. Compare a two-breadth/two-depth scheduler against previous-mechanism refinement and fixed round-robin. Evaluate reward only when the recommendation matches the recorded action; unmatched actions are unsupported, not failed. Matched subsets differ, logging propensities are absent, and changing one action changes future states. Therefore the output deliberately leaves `value_estimate` null: this is a prefix/leakage/support audit, not a causal simulator or proven scheduler win.

The online plan has richer pending-work and repair gates than this coarse historical replay. Do not describe the replay as validating the entire online policy. No replay of counterfactual geometry, cost savings or future owner acceptance is synthesized.

## Judge qualification

The existing owner set has three image-bound convenience pairs. Leave-one-family-out selects brief/plain from the other families and evaluates the held-out family's existing prediction. Because the original briefs were reconstructed with owner knowledge, this is post-hoc diagnostic holdout, NOT prospective generalization. `calibration.json` retains this limitation and disables promotion. Additional genuinely frozen-before-label independent pairs are required.

`--prepare-ab` wires split owner anchors, scope briefs and hash-bound full-frame inputs into the existing swapped `ab_judge.run`; withheld pair labels are omitted from its preferences. Exact original native crops remain in the prior calibration archive. Current packets use 384×576 context images and are NOT final-density gates.

## Recipes and executable transfer

Cards retain inputs, exact script hashes, parameters, evidence and failure notes. Promote only owner approval OR qualified calibrated judge win, AND a hash-bound passing native max-zoom/crop receipt. The script itself must also be among verified artifacts. Candidate cards are usable experiments, not winning recipes.

`recipes/procedural_ink.py` extracts the actual banner metric-dot mechanism into an import-inert, idempotent bpy function. It copies a receiver material; it never saves, renders, clears a scene, applies transforms, or changes the camera/world/lights. Use unit-scale meshes. It is not a finished comic treatment.

```sh
env -i HOME="$HOME" PATH=/usr/bin:/bin TMPDIR="$TMPDIR" \
  blender --background --factory-startup -t 2 --python-exit-code 1 \
  --python scripts/test_recipe_transfer.py -- /new/transfer-output /path/to/stone-lowpoly/A/scene.blend
```

The test uses a disposable factory scene, transfers onto the actual `SLP front folded facets` receiver, renders CPU-only coupons, and checks import inertia, idempotence, unchanged geometry and source file hash. This proves technical transfer, not owner approval or max-zoom fidelity. A completely clean environment is needed on hosts where the Hermes interpreter's environment leaks into system Blender.
