# Stable defect / hypothesis ledger

Keep `defects.jsonl` append-only with one serialized writer. Assign a canonical
scoped defect ID before work (project/element/visible blocker); aliases must resolve
to it. Changing a parameter, family or lane cannot create a new budget.

Trial row (paths are evidence, not claims of owner authorization):
```json
{"event":"trial","trial_id":"t1","defect_id":"dial-reflection","family":"layered-coat","outcome":"unresolved","evidence":["round-1/native.png","round-1/receipt.json"]}
```
Outcomes: `unresolved`, `cleared`, `technical_failure`, `unknown`. Technical failure
consumes a trial conservatively; unknown evidence blocks more dispatch until review.
A cleared defect stops further work on that ID. Keep the underlying raw attempt
and directive state (LANDED/PARTIAL/NOT_DONE/SUPERSEDED_BY_OWNER/INVALID_DIAGNOSIS).

Run before the next dispatch:
```text
python <skill>/scripts/defect_guard.py defects.jsonl dial-reflection
```
Exit 0 = within budget, 3 = STOP, 2 = invalid evidence (also stop). Two failures mean
show both attempts, a distinct representation proposal, costs/risks, and obtain a
real owner decision. Do not let a worker manufacture its own approval.

Only after that checkpoint may the orchestrator append:
```json
{"event":"owner_restart","defect_id":"dial-reflection","after_trial_ids":["t1","t2"],"receipt":{"path":"owner-decision.md","sha256":"<actual SHA256>"}}
```
The guard verifies exact consumed trial IDs and unchanged receipt bytes; **a hash
cannot authenticate the owner**. The orchestrator must validate the actual message,
new scoped budget and preferences. Save the guard's JSON/exit with the dispatch.
This CLI enforces a caller's gate; it cannot prevent an agent bypassing the caller.
