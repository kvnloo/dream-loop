# Local owner rating

The owner-review service is Python stdlib HTTP on **127.0.0.1:43220**. It does not
launch a desktop browser, render Blender scenes, call models or promote scenes.
The seed helper uses the existing Pillow dependency to produce non-resampled
reference crops. The loop retains its existing jsonschema dependency.

## Start and use

```sh
python scripts/meta_loop.py --data /path/to/meta-loop report
python scripts/seed_owner_rating.py --data /path/to/meta-loop
python scripts/meta_loop.py --data /path/to/meta-loop report
python scripts/owner_rating.py --data /path/to/meta-loop --port 43220
```

The second report ingests any previously report-only variants reconstructed by
the seed helper. The seeded Quackles catalog contains 45 unique current trials:
22 banners, five low-poly stone trials, 14 layer stacks plus their integration
and it12 control, and White A/B. Six stone stacks are also visible in the Stone
queue without duplicating trial identity. Historical-only frames are separate.
Existing trial IDs are retained. Eleven missing comic/relief/low-poly variants
were reconstructed from their reports and real rendered images into
`events/rating-import.jsonl`; evidence-only reports cannot receive owner labels.

A persistent launch may use `nohup ... >>rating-server.log 2>&1 &`. Record the
actual PID and URL in `RATING-SERVER.md` after verifying `/health`. Never kill or
reuse an occupied port owned by another process. No external bind flag exists.

- **1–5** selects quality, **A/R/M** selects accept/reject/maybe.
- **Enter** saves and advances; changing stars/decision alone does not save.
- **N/P** next/previous; unsaved drafts survive navigation within this page.
- **Left/right arrows** prefer the left comparison/current right candidate.
  A preference does not implicitly accept either trial. A tie button is available.
- **Z** jumps to the highest available density at 1:1 pixels, with scrollable crops.
- **Space** flips the current pane to the target and back.
- Typing in an input/select suppresses global shortcuts; Escape releases focus.
- Density/region controls expose real available evidence. Missing 201 MP or 1 GP
  views are disabled. The target is always source-resolution evidence, not
  invented deep-zoom truth. Hero may simply fit the native crop into the pane.

## History

`owner-history-inferred.json` accounts for all 65 retained quotes: 13 inferred
bindings and 52 unresolved at initial delivery. An inference needs a curated
linked trial, unique reviewed-image path, identical image hash, or a unique
retained trial directory. It records the exact quote and evidence. Timestamps
and coarse sentiment keywords never establish a binding.

Confirm History displays each quote, its source images, mapping evidence and a
binding selector. Suggested decisions are drafts only; stars are not invented.
The owner can correct the trial before saving. History confirmations remain
component-scoped, preserving praise/correction without approving an entire
scene. Unresolved quotes remain available for manual resolution. Inferences
are never appended to `events/owner.jsonl` without owner action.

## Persistence and learning

The [event contract](../templates/meta-events.md) defines `owner_label`.
Writes use an RLock, process flock, one O_APPEND syscall, fsync and exact read-back.
Retries retain their request ID; conflicting reused IDs are rejected. An
incomplete tail blocks further writes rather than overwriting evidence.

A confirmed label immediately updates the materialized ledger, separate
owner-accept/preference payoffs, next recommendations, recipes, summary and
reports. The last label replaces the statistical observation, not its history.
Maybe is unknown, not failure. Stars never infer acceptance. Native crop gates
and artifact integrity still control recipe qualification.

The responsive path re-hashes the touched trial and uses the latest ingested
producer snapshot. Use `meta_loop.py report` when new lane events arrive, then
reseed/restart the app if new candidates should appear. Keep one materializer;
do not run a concurrent report/watch writer during an owner rating session.
The service has loopback Host checks, same-origin request checks and a
per-process request token. Only allowlisted image assets are served; arbitrary
filesystem paths, source code, directory indexes and cross-origin requests are
not exposed. This is a single-owner local tool, not a multi-user hosted service.

## Verify without polluting owner evidence

```sh
python scripts/owner_rating.test.py
python scripts/run_tests.py
python scripts/verify_owner_rating.py --data /path/to/meta-loop --receipt /path/to/e2e.json
python scripts/verify_owner_visual.py --url http://127.0.0.1:43220/ --output /path/to/screenshots
```

The functional harness starts an owned server on port zero using a disposable
copy, posts a synthetic label through the real app in Lightpanda, verifies
learning and full CLI re-ingestion, and proves the real owner file is unchanged.
The visual harness uses owned chrome-headless-shell, never clicks Save, waits
for decoded images, and checks desktop/mobile overflow, native zoom, target
flip and White A/B. Both close their owned browsers and test servers.
