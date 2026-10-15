# Live meta-learning events — v1

Append one complete JSON object + newline to `meta-loop/events/<lane>.jsonl`. One writer per lane. Never rewrite a trial; append a revision with a NEW event_id and the SAME trial_id. Later revisions replace the materialized trial, not its history. Element/run/parents/stable-defect identity stays fixed. A mechanism-label correction is retained as classification history; a substantively new intervention needs a new trial_id. Finish each write before announcing it. Unknown is null, never zero/PASS. Files are private local evidence.

This is an intake extension of Dream-loop discovery-tree, NOT a replacement for legacy rounds.jsonl. `trial_id` maps to discovery `node_id`, `parents[0]` to `primary_parent`, remaining parents to `dependency_ids`. Full discovery_observation v2 may carry the same payload in optional `meta_trial`. Existing observation and v1 node contracts remain unchanged. Partial historical records stay intake records: missing cohort hashes are NOT fabricated.

## Required payload (copy and fill)
```json
{"event":"meta_trial","schema_version":1,"event_id":"banner-traced-001-v1","trial_id":"banner-traced-001","run_id":"night-v2","timestamp":"2026-10-15T12:00:00Z","lane":"banner-traced","parents":[],"element":"night-banner","defect_id":"banner-final-density","hypothesis":"Traced vector contours preserve native-scale edges","mechanism_class":"traced_vector","parameters":{},"cost":{"gpu_seconds":null,"wall_seconds":null},"artifacts":[],"metrics":{"max_zoom_texel_density":null,"crop_gate":null,"sharpness":null},"self_review":{"status":"pending","notes":""},"judge_verdicts":[],"owner_reaction":{"status":"not_reviewed","receipt":null},"status":"pending","failure_class":"unknown"}
```

Use the ACTUAL timestamp; the example timestamp is not evidence.

- `element`: `night-banner` or `night-stone` (other stable element ids allowed).
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

Run `python /workspace/dream-loop-meta/scripts/meta_loop.py ingest` and `... report`; `... next --element night-banner` reads current files. Polling is read-only with respect to lane artifacts. Runner owns only meta-loop output; lanes own their own JSONL.
