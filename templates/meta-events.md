# Live meta-learning events — v1

Append one complete JSON object + newline to `meta-loop/events/<lane>.jsonl`. One writer per lane. Never rewrite a trial; append a revision with a NEW event_id and the SAME trial_id. Later revisions replace the materialized trial, not its history. Element/run/stable-defect identity stays fixed. Parent corrections retain parent_history and recheck cycles; use this to resolve provisional aliases, not to disguise a new experiment. A mechanism-label correction is retained as classification history; a substantively new intervention needs a new trial_id. Finish each write before announcing it. Unknown is null, never zero/PASS. Files are private local evidence.

This is an intake extension of Dream-loop discovery-tree, NOT a replacement for legacy rounds.jsonl. `trial_id` maps to discovery `node_id`, `parents[0]` to `primary_parent`, remaining parents to `dependency_ids`. Full discovery_observation v2 may carry the same payload in optional `meta_trial`. Existing observation and v1 node contracts remain unchanged. Partial historical records stay intake records: missing cohort hashes are NOT fabricated.

## Required payload (copy and fill)
```json
{"event":"meta_trial","schema_version":1,"event_id":"sample-traced-001-v1","trial_id":"sample-traced-001","run_id":"fictional-study","timestamp":"2026-01-01T12:00:00Z","lane":"sample-traced","parents":[],"element":"sample-panel","defect_id":"sample-density","hypothesis":"Traced vector contours preserve native-scale edges","mechanism_class":"traced_vector","parameters":{},"cost":{"gpu_seconds":null,"wall_seconds":null},"artifacts":[],"metrics":{"max_zoom_texel_density":null,"crop_gate":null,"sharpness":null},"self_review":{"status":"pending","notes":""},"judge_verdicts":[],"owner_reaction":{"status":"not_reviewed","receipt":null},"status":"pending","failure_class":"unknown"}
```

Use the ACTUAL timestamp; the example timestamp is not evidence.

- `element`: `sample-panel` or `sample-base` (other stable element ids allowed).
- `mechanism_class`: `geometry`, `procedural_shader`, `traced_vector`, `generated_vector`, `projection_paint`, `ai_udim`, `layer_stack`, `lighting`, `post`, `unknown`.
- `parents`: trial ids, never invented provenance. Unknown parents = [].
- `defect_id`: stable across parameter retries and family renames.
- `cost`: measured nonnegative seconds, or null. Optional `cost_status` records estimated vs measured.
- `artifacts`: `[{"path":"/absolute/file.png","sha256":"actual lowercase SHA256"}]`. Include native crops, bpy scripts, .blend and receipts as available. Hash after writing; no placeholder hashes.
- `metrics.max_zoom_texel_density`: minimum effective source texels per delivered pixel across both axes; procedural/vector representations use null plus `metrics.density_evidence` explaining their measured output sampling. `metrics.crop_gate`: `pass`, `fail` or null. `metrics.sharpness`: numeric or null (include definition in `metrics.sharpness_method`). Optional `metrics.max_zoom_gate`: `pass`/`fail`/null, with `metrics.max_zoom_evidence` receipt path.
- `judge_verdicts`: `[{"preference":"candidate|parent|tie|abstain","protocol_id":"brief-aware-v1","calibration_id":null,"receipt":"/absolute/verdict.json"}]`. Do not self-assert calibration; learner admits only registered, qualified held-out calibrations.
- `owner_reaction.status`: `approved`, `rejected`, `preferred`, `not_reviewed`, `uncertain`. Approval/preference requires an exact receipt; preferred is NOT approval.
- `status`: `pending`, `completed`, `failed`, `blocked`.
- `failure_class`: `none`, `implementation`, `mechanism`, `scope`, `evidence`, `resource`, `unknown`.
- Optional `recipe`: {"script_path":"/absolute/reusable.py","entrypoint":"apply","inputs":{},"parameters":{},"failure_notes":[]}.
- Optional `source`: source receipt and import metadata. Optional `cohort`: full discovery-observation cohort. Missing cohort forbids claims of causal cross-fixture replay.

A recipe is promoted only with owner approval OR qualified calibrated judge candidate win, AND a passed native max-zoom gate with evidence. Pending/non-qualified entries may be archived as candidates, never called winning recipes. Failed implementation is not a mechanism rejection.

From the repository root, run `python scripts/meta_loop.py --data "$OWNER_REVIEW_DATA" ingest` and `... report`; `... next --element sample-panel` reads current files. Polling is read-only with respect to lane artifacts. Runner owns only meta-loop output; lanes own their own JSONL.

## Owner UI labels (append-only overlay)

`events/owner.jsonl` is reserved for the local owner-rating server. A label does not
revise a producer trial or change its lane, hypothesis, artifact gates or provenance.
It references a real materialized `trial_id` and its exact `element`.

```json
{"event":"owner_label","schema_version":1,"event_id":"ui-unique-request-id","trial_id":"sample-traced-A","element":"sample-panel","verdict":"maybe","stars":3,"judged_on":"both","pairwise":{"other_trial_id":"sample-traced-T","preference":"candidate"},"note":"Exact owner note","timestamp":"2026-01-01T23:00:00+00:00","source":"owner-ui","status":"confirmed","scope":"trial"}
```

The timestamp above is an example, not a receipt. The server supplies the actual
UTC timestamp. `verdict` is `accept`, `reject`, or `maybe`; `stars` is an integer
1–5. New UI writes require `judged_on: look|clear|both`, the owner's selected
render basis. Older labels remain valid without rewriting or inventing their
judging basis. `pairwise` is null or `{other_trial_id, preference: candidate|other|tie}`.
Candidate means the event's trial; other means the named comparison trial.
Preference is a separate descriptive payoff, never implicit approval or a causal
ranking. The latest label per trial is materialized, all previous labels remain
in `owner_label_history`, and a repeated event ID must have identical content.

`scope: trial` updates owner acceptance (maybe resets it to unknown).
`scope: component` preserves scoped feedback without granting whole-trial
approval. History confirmation is always component-scoped and includes
`history_id`, `historical_quote`, `historical_evidence`, `historical_timestamp`,
and `scope_note`. The UI lets the owner correct the trial binding explicitly.
Stars never infer a verdict. Acceptance never bypasses max-zoom recipe gates.

`owner-history-inferred.json` audits every retained receipt with an exact quote,
evidence, status `inferred` or `unresolved`, and zero or more known trial IDs.
It is not an event log. No inference trains the learner until the owner confirms
it. Ambiguous timestamps, generic praise and coarse keyword annotations do not
establish a trial binding.

The server uses process/thread locking, one O_APPEND write, fsync and exact event
read-back. It rejects incomplete tails instead of repairing/overwriting them.
Retries retain the request ID; corrections use a new ID. After a confirmed save,
the ledger, payoffs, recipes, summary, report and next-batch files refresh. The
fast UI path rechecks the touched trial's artifacts and uses the last ingested
producer snapshot. The server auto-ingests the explicitly configured live lanes
every 15 minutes for a four-hour window, under the same write lock.
Run only one materializer at a time; do not run a separate report/watch writer
while owner ratings are being posted.
