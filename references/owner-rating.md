# Local owner rating

The owner-review service is Python stdlib HTTP on **127.0.0.1:43220**. It does not
launch a desktop browser, render Blender scenes, call models or promote scenes.
The manifest seed helper uses the stdlib catalog to describe source-resolution
reference crops. The loop retains its schema validation.

## Start and use

```sh
python scripts/meta_loop.py --data /path/to/meta-loop report
python scripts/seed_owner_rating.py --data /path/to/meta-loop --manifest /path/to/catalog-input.json
python scripts/meta_loop.py --data /path/to/meta-loop report
python scripts/owner_rating.py --data /path/to/meta-loop --port 43220
```

Seeding requires an explicit external manifest and preserves existing trial IDs.
It does not reconstruct missing trials, scan project directories, import labels,
or append events. Evidence-only reports cannot receive owner labels. Paths in
the manifest are relative to its directory (explicit absolute paths also work).
Keep this manifest outside the source repository. Synthetic example:

```json
{"candidates":[{"trial_id":"sample-A","queue":"banner","title":"Synthetic panel","views":[{"path":"sample.png","target":"target.png","kind":"hero","region":"panel"}]}],"anchors":[]}
```

For a self-contained generated demo, run
`python scripts/synthetic_fixture.py --data /new/synthetic-review-data`. See the
[synthetic case study](../case-studies/owner-review-synthetic.md) for boundaries.

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
- **L** cycles Both (side by side), LOOK, CLEAR where those renders exist.
  TARGET stays visible. `Judged on` records the owner's selected basis as
  `judged_on: look|clear|both` on every new label. Missing variants are explicit;
  historical images with unclassified optics require the owner to identify the
  mode before Save becomes available. No image is silently treated as CLEAR.
- **Stone mosaic**, **Optics**, and **Greenery** are live producer queues.
  Stone mosaic opens on the measured plinth front-face crop, including native
  density front crops when the trial only contains density evidence.
- Typing in an input/select suppresses global shortcuts; Escape releases focus.
- Density/region controls expose real available evidence. Missing 201 MP or 1 GP
  views are disabled. The target is always source-resolution evidence, not
  invented deep-zoom truth. Hero may simply fit the native crop into the pane.

## History

`owner-history-inferred.json` records supplied local receipts as inferred or
unresolved. An inference needs a curated linked trial, unique reviewed-image
path, identical image hash, or a unique retained trial directory. It records the
exact quote and evidence locally; no real receipts ship with the source.
Timestamps and coarse sentiment keywords never establish a binding.

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
producer snapshot. The server refreshes `stone-mosaic`, `optics`, and
`banner-greenery` immediately at startup and every 900 seconds for up to 14,400
seconds. Its own server loop owns this finite schedule; there is no detached
polling process. The page checks the catalog every 30 seconds without discarding
unsaved stars/decision/notes. `/health` and `rating-poll.json` expose last refresh
and failures. After four hours the rating app stays available; restarting opens
a new four-hour watch window. Keep one materializer; do not run a concurrent
CLI report/watch writer during an owner rating session.

Live ingestion is serialized with label saves by the same RLock and flock.
Producer revisions are deduplicated/materialized; partial JSONL tails retain the
previous queue and report an error. Only hash-bound image artifacts from real
completed trials enter these queues. No lane or owner event file is written by
the poller. Render master/border receipts generate source-resolution TARGET
crops; inconsistent dimensions are withheld in `live_warnings`. Asset URLs bind
content hashes, and HTTP rejects images changed after cataloging.

`night-v2/optics/LOOK.json` is exposed with its exact settings and hash when
present. Each view also retains the actual optics receipt: historical/provisional
LOOKs are not misrepresented as renders of the latest selected settings. Optics
variants may share their same-source, same-size independently rendered CLEAR
control. This UI never renders Blender scenes or fabricates missing LOOK/CLEAR
counterparts; the producing lanes must deliver them.
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
