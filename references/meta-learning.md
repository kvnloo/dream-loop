# Blender meta-learning loop

`python scripts/meta_loop.py --help` is the executable entry point. It learns from immutable observations, not edits to the model's weights. Python 3.10+ is required. The ledger, review server and schema checks use the standard library; image judging helpers may need Pillow and provider dependencies. The learner itself does not import bpy, contact models or start renders.

## Commands

```sh
python scripts/meta_loop.py --data /path/to/meta-loop report --evals /path/to/evals
python scripts/meta_loop.py --data /path/to/meta-loop next --element sample-panel
python scripts/meta_loop.py --data /path/to/meta-loop next --element sample-base --exploration-slots 2
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

Each lane appends complete newline-terminated events; a new event_id revises an existing trial_id. Element/run/stable-defect identity cannot change across native revisions. Parent corrections (e.g. resolving a provisional batch alias to actual trial IDs) retain `parent_history` and rerun cycle quarantine; raw events remain unchanged. Producer mechanism-label corrections retain `classification_history` and move the same observation between groups rather than creating another trial. A substantively new intervention needs a new trial ID. Duplicate identical events are ignored; conflicting IDs and cross-lane ownership are errors. An unfinished final line is deferred. Cycles are quarantined; unresolved external parents remain visible. A formal valid native event supersedes pre-contract intake for that same trial without double counting; raw intake stays on disk and in `superseded-intake.json`. Non-native formats require an explicitly selected trusted adapter. Preserve original tokens under `source.raw`; never guess missing acceptance, timestamps or gate outcomes.

Generated artifacts (`ledger.json`, `payoffs.json`, `replay.json`, next portfolios, recipe cards, HTML) are rebuildable projections. `events/` is the authority. Revisions replace a trial's statistical observation rather than incrementing the denominator. Artifact hash checks are recomputed from disk, not trusted from a lane flag. `polls.jsonl` records live refresh summaries. Single-writer ownership is cooperative, not a security boundary.

## Payoff and portfolio

Each element × mechanism has separate Beta(1,1) posteriors for owner acceptance, qualified judge wins, historical kept decisions and evidenced max-zoom passes. Historical keep is NOT owner acceptance. Unknowns, ties and abstentions do not become failures. Judge votes are admitted only with a matching registered prospective calibration, an evidence-verified verdict and a receipt. Repeated agreeing votes count once; disagreement abstains. Retrospective calibration is deliberately unqualified for prospective promotion.

The 95% interval uses deterministic seeded Beta samples. These are descriptive uncertainty estimates, not proof of IID trials; projects, difficulty and coupled interventions confound mechanism comparisons. Costs preserve measured phase scope and missing values. GPU utilization seconds are not inferred from render elapsed time. Report-level priors do not invent subtrial outcomes.

Default portfolio: four slots, two for breadth and two for depth/repair/recombination. Pending representations are not dispatched again. No established winner means an evidence/interpretation repair, not a made-up best. Two nonwins against the same stable defect request a checkpoint or mechanism switch, never global termination. Implementation/resource/evidence failures are not counted as failed mechanism hypotheses. Recombination requires two gated winning recipes. Adapters can restrict the mechanism space and preference order; it is a proposal subject to the owner brief, not execution permission.

## Stuck-defect dream step

```sh
python scripts/meta_loop.py --data /path/to/meta-loop stuck
python scripts/meta_loop.py --data /path/to/meta-loop dream --element sample-base
python scripts/meta_loop.py --data /path/to/meta-loop dream --element sample-panel --defect sample-density
python scripts/dream_step.test.py
```

`stuck` detects two timestamped assessed visual nonwins within an element/stable defect. Unknowns, controls, delivery records, pending reviews and implementation/resource/evidence errors do not count. Same configurations without distinct scene evidence count once; a later evidenced success clears the streak. Explicit producer failures remain diagnostic observations, not owner labels or calibrated payoff. Adapters may define analytical subelements while preserving native producer identity.

`dream` writes ranked JSON/Markdown portfolios under `dream/`, with exact source IDs and hash-bound starting artifacts. It includes taxonomy breadth (with under-tried classes), quoted cross-lane partial-feature recombinations, compatible other-element recipe components, breadth/depth/earlier-switch prefix audits, and one wildcard. Cost anchors are recorded source-trial medians, not measured coupon times. Hypotheses and rank are explicit heuristics, not visual payoff predictions. Mechanism+semantic-parameter similarity with a 15% numeric tolerance suppresses nearby failed clones; missing common parameters cannot prove novelty. The fixed taxonomy distinguishes actual construction changes from renamed families. Pending mechanisms and completed renders awaiting review are withheld as full `reserved_directions`, not dispatched twice. Identical proposals across defects are consolidated with all covered defect IDs and evidence retained. When active producers prevent a stable long read, freeze the small event/calibration streams with immediate source/copy hash verification, then hash artifacts once and publish all element portfolios from that shared snapshot. Retain the snapshot timestamp and original path/hash manifest; do not disable the live CLI's fail-closed guard.

`next` automatically includes the dream portfolio for stuck elements. Invalid streams block both the legacy batch and the dream. `stuck`, `dream` and `next` now use read-only ingestion with before/after archive hash checks, so they do not race the owner server's ledger/report writer. Only `dream` writes its own portfolio files. Exact defect requests use hash-suffixed filenames and cannot replace an all-defect portfolio. No owner events, CURRENT pointers, scene files or model weights are changed.

The new replay is a timestamped **materialized-observation** support audit; it does not reconstruct original-time revision histories. Decisions see strictly earlier rows, never equal-time peers. Mechanism matches are weak support, not exact parameter/parent matches. Unknown outcomes and policy values stay null. Exploration gaps are places an earlier-switch rule would allocate differently—not predictions that unexplored branches would succeed. Full behavioral tests exercise these limits.

## Dream-RSI-style replay — bounded claim

Replay groups only rows with explicit original-ledger locators; file mtimes do not establish decision order. Unknown mechanism classifications are excluded. Each recommendation sees only the earlier prefix, using one fixed mechanism action space. Compare a two-breadth/two-depth scheduler against previous-mechanism refinement and fixed round-robin. Evaluate reward only when the recommendation matches the recorded action; unmatched actions are unsupported, not failed. Matched subsets differ, logging propensities are absent, and changing one action changes future states. Therefore the output deliberately leaves `value_estimate` null: this is a prefix/leakage/support audit, not a causal simulator or proven scheduler win.

The online plan has richer pending-work and repair gates than this coarse historical replay. Do not describe the replay as validating the entire online policy. No replay of counterfactual geometry, cost savings or future owner acceptance is synthesized.

## Judge qualification

Leave-one-family-out can select a rubric using training families and evaluate the held-out family's existing prediction. This is a retrospective diagnostic, not prospective generalization. Genuinely frozen-before-label independent evidence is required before qualifying a judge. An optional trusted `prepare_anchor_judges` adapter can build provider-specific packets; inspect its costs and data handling before `--execute`.

## Recipes and executable transfer

Cards retain inputs, exact script hashes, parameters, evidence and failure notes. Promote only owner approval OR qualified calibrated judge win, AND a hash-bound passing native max-zoom/crop receipt. The script itself must also be among verified artifacts. Candidate cards are usable experiments, not winning recipes.

Executable recipes and live-scene verification belong in the project's external artifact package. This repository does not ship recorded scene receivers or default material settings. Test recipes for inert import, idempotence and fixture preservation on disposable synthetic receivers; successful transfer is not owner approval.

## Explicit adapters

Set `DREAM_LOOP_ADAPTER` to an **absolute trusted Python file** before invoking any entry point. No adapter is discovered from a ledger, repository name or current working directory. Loading an adapter executes local code; never load an untrusted adapter. Invalid paths fail closed. Without an adapter, only native trial events and canonical chat labels are accepted, no default elements or live lanes are injected, and Dream uses its generic proposal vocabulary.

Hooks: `mechanism_key(row)`, `infer_identity(row)`, `import_history(path)`, `import_reports(root, rows)`, `adapt_lane(raw, path, line)`, `plan_candidates(element)`, `plan_preferred(element)`, `scope(row)`, `topics(element, defect, rows)`, `transfer_component(topic, row)`, `build_catalog(data, catalog, rows)`, `review_catalog(catalog)`, `read_chat_labels(path)` and `prepare_anchor_judges(evals, output, execute)`. Settings: `DEFAULT_ELEMENTS`, `LIVE_LANES`, `TAXONOMY` and `CROSS_SCOPE_TOPICS` (topics whose donor ranking may cross analytical scopes). All are optional; overridden policy is the adapter author's responsibility. Keep scene-specific defaults, globs, layout rules, source adapters, credentials and receipts outside the public tree.

The [fictional paper-lamp adapter](../examples/paper_lamp_adapter.py) demonstrates custom intake and explicit hash-bound live views. Its fixtures are not anonymized historical results.

```sh
export DREAM_LOOP_ADAPTER="$PWD/examples/paper_lamp_adapter.py"
python scripts/meta_loop.py --data /path/to/sample-data report
python scripts/import_chat.py --data /path/to/sample-data --source /path/to/mapped-labels.jsonl
# Inspect the dry-run and evidence before explicitly adding --commit.
```

The chat importer validates the whole batch before append, honors the review server's lock, detects conflicts and incomplete tails, fsyncs and reads back exact events. Retries are idempotent. It does not infer sentiment or mapping, invent stars, restart services or refresh shared projections. Use the existing single materializer after import.
