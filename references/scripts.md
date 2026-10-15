# Helper contracts and verification

Dependencies: Python 3.10+, Pillow/NumPy; JSON Schema lint also uses PyYAML/jsonschema.
Node 18+ for original Fal and compatible discovery-ledger tests. Helpers are offline
unless explicitly documented. Resolve skill paths independently from product cwd.
Run `python scripts/run_tests.py` and `python scripts/lint_skill.py` at the skill root.

## Tile splitter
`tile_splitter.py TARGET CAPTURE NEW_DIR --semantic regions.json --cols 4 --rows 6 --padding 32`

- Semantic JSON: `regions:[{id,name,box:[x0,y0,x1,y1]}]`, integer exclusive bounds.
- Default rejects aspect/resolution mismatch. `--align` permits same-aspect uniform
  diagnostic resizing and marks it non-native; never invents source detail.
- `--mask` is white-ignore, same target dimensions. Grid core coverage is exact
  even for odd dimensions; >90% ignored core is skipped. Crops remain unaltered;
  mask fractions record scope and the judge brief must exclude ignored pixels.
- Outputs target/capture native crops, yellow-box context and manifest with hashes,
  boxes, dimensions, coverage and skip reasons. A context sheet is not a structure
  overlay. A native file still needs delivered-resolution audit in the vision tool.
- Refuses an existing output directory. Source resolution/boxes and budget belong
  to the brief; three images is a protocol choice, never a universal platform cap.

## Verdict aggregator
`aggregate_verdicts.py MANIFEST VERDICT_DIR NEW_REPORT.json`

One `<tile-id>.json` per active region using `judge-tile.md`. Validates exact keys,
identity/box/revision, finite ranges, sums, enums and blocked nulls. Exit 2 produces
an honest partial report for missing/invalid verdicts; no fabricated votes. It lists
means with denominators, blocked IDs, worst scored IDs, all raw votes and deduped
physical defects. One contribution per tile/defect; overlapping grid/semantic crops
are not independent confidence. Synonym/causal conflicts need human adjudication.

**Not automatic promotion:** JSON validity does not prove unique real sessions,
requested model or image loads. `review_verified` stays false until an external
native-session/evidence audit. Build a worst-region sheet separately if needed.

## Comparison sheets
`compare_sheet.py NEW.png target.png parent.png candidate.png --labels TARGET PARENT CANDIDATE`

Requires equal source dimensions. `--box x0 y0 x1 y1` crops all identically without
resizing. `--max-width N` explicitly makes a downsampled presentation sheet, marked
non-native. Saves source/output hashes in adjacent `.json`; refuses reused outputs.
Do not use an unreadably large montage as the only fine-detail evidence.

## Fresh swapped A/B
`ab_judge.py TARGET PARENT CANDIDATE BRIEF NEW_DIR --preferences OWNER-PREFERENCES.resolved.md --provider PROVIDER --model MODEL`

Default prepares only. Add `--execute` for two serial fresh Hermes one-shots
with file/vision tools, safe mode, bounded turns/time, separate anonymous PNGs,
prompts, raw stream logs, stderr and process receipts. Supply a scope-resolved
verbatim preference excerpt; the runner includes and hashes it. Preflight actual
CLI/model availability before paid work. `--hermes`/`--hermes-arg` permit a tested
launcher; no shell interpolation. An execution failure stops the second request.

The mapping is outside trial cwd, but prompts/tools are NOT an OS security sandbox.
Keep production secrets away and audit that judges read only assigned evidence.
Process success is not proof of visual review; inspect native sessions/model ID,
actual image loads/dimensions and raw verdicts before adjudication. Default first
order is parent/candidate; swapped second controls side bias, while a calibration
study should randomize first side independently. No automatic keeper or promotion.

## Integration and dispatch
`templates/integrate.py` is a tested adapter skeleton, not a renderer. Supply real
load/guard/apply/fingerprint/save/render methods and file names for your domain.
It orders stages, checks repeat-apply stability, protected state, save/reopen equality,
fixture immutability and capture existence; emits working-preview only. Failure may
leave a diagnostic directory; never reuse it as accepted evidence. Adapter ownership
is not an OS sandbox; only run reviewed project code.

`defect_guard.py` checks stable defect trial budgets; see [ledger](../templates/defect-ledger.md).
`scripts/loop-state.mjs` retains the fork's v1 append-only API; see [evals](evals.md)
for v2 sidecars and single-writer limits. No offline replay optimizer ships here.

## Retained helper boundaries

[Compatibility](compatibility.md) indexes legacy schemas, image-backend discovery, Classic/Pro/Plus, Fal and local capture. Main's Fal and preview implementations/tests are retained, including path/download checks and `/__compare`; these are not replaced by earlier v2 copies. [Tiled mesh maps](tiled-mesh.md) use `tile_grid.py` (split/stitch, with documented divisible-grid and scaled-overlap limits), distinct from the native diagnostic tile splitter above.

Original crop/structure/overlay/Fal/PBR/preview interfaces remain. The v2 structure
local-window scan includes right/bottom edge windows that the older stride omitted;
new synthetic regression covers that fix. Historical 85-case calibration belongs
to its original implementation; rerun/extend the real suite for a new target family.
Tests are executable helper contracts, not calibration of aesthetic taste, a real
model-quality benchmark, an actual renderer transfer, or an owner acceptance.
