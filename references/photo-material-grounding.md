# Photo-grounded material fidelity (optional 3D stage)

Use this **only after** the existing camera/shape/crop gates in [3d-what-works.md](3d-what-works.md) pass. This is a material-only specialization of DreamLoop, **not** a new Plus/Pro/Classic mode or replacement judge. Do not rewrite the primary target, change products, change camera framing, or copy image pixels from the held-out evaluation set into generation.

The E0 offline benchmark and protocol live in the downstream [StableGen photo-material experiment](https://github.com/kvnloo/StableGen/pull/2). Its canonical tracker is [kvnloo/StableGen #1](https://github.com/kvnloo/StableGen/issues/1). The benchmark does not generate materials; it measures exported renders.

## Why this stage exists

A texture can look ultra-sharp while containing incorrect colors, baked highlights, invented surface detail, or projection seams. Tiled image restoration makes individual pixels clearer, but cannot certify physical plausibility. Real DSLR/smartphone photography can supply appearance and scale evidence. **One photo alone does not identify all normal, roughness, height and BRDF properties.**

## Separation of evidence

| Data | Who may inspect | Why |
| --- | --- | --- |
| Locked 3D scene, DreamLoop target and source mesh | artist + composition judge | geometry, camera and pose gate |
| **Conditioning** photos + approved derived swatches | generator / material editor | texture/PBR refinement |
| **Held-out** photographs, masks and alternate-light controls | isolated evaluator **only** | independent measurement |
| Evaluator scalar results, blockers and accepted/rejected decision | DreamLoop controller | choose one next intervention |
| Raw private photos or camera metadata | local authorized capture process only | never commit or upload by default |

Avoid creating a single image collage containing both conditioning and held-out references; the generator may unintentionally see test detail. The evaluator may return aggregate masked scores and error regions **without** revealing held-out pixels to the generator. Exact hash checks catch accidental duplicates, not near-duplicate leakage.

## One material experiment

1. **Gate shape first.** Freeze the full-scene target (`.dream-loop/target.png`), subject, mesh and UVs; match silhouette and camera using existing overlay/crop gates. Stop *material* evaluation on shape failure, but perform a camera/massing action under the usual DreamLoop rules.
2. **Choose one mesh/material region.** Prefer real-world scale and known geometry. Capture one or more conditioning photos, with optional scale and color checker. Use an isolated project copy for each variant.
3. **Prepare three same-model candidates:** A: StableGen baseline without photo; B: the same generator/settings with external reference; C: B plus one masked, tiled, or PBR edit per DreamLoop round. Do not change mesh, camera, seed, model or renderer to make B or C look better.
4. **Preserve blind observations.** Independently align reference photos, camera and lighting, then hide held-out images from any iterative model. Provide multiple angles and at least one fixed-camera pair with changed illumination where possible. Lock capture exposure/WB when comparing lighting response.
5. **Render with the same view plan.** For every candidate, bake or reproject with StableGen, then render the *exact* held-out cameras and lights. No auto resizing or image registration at scoring time. Use a single shared ROI mask per capture to avoid background dominance.
6. **Measure independently.** Run `experiments/photo_material/benchmark.py` from the downstream StableGen fork using its manifest. Read the per-condition color, structure, detail and multi-light errors, reference/output hashes, and validation warnings. Do not promote a candidate on one aesthetic score, one target camera or image sharpness alone.
7. **Accept or rollback.** Preserve best-known geometry and material. Promote only if image-alignment gates pass, the color/structure errors do not materially worsen, and at least one relevant held-out material metric improves beyond repeat-run jitter. Report the complete vector, including cost/VRAM. If real photos or calibrated relighting are missing, mark claims *unverified*, not *successful*. Keep rejected attempts in Dream-RSI.
8. **Stop on stall.** Use the existing two-round no-improvement rule, then ask for new material evidence or choose a different technique; never change the rubric to rescue a result.

## Mapping to Dream-RSI

Append **one** `discovery_node` per actual intervention using the existing `scripts/loop-state.mjs` API from [discovery-tree.md](discovery-tree.md). Record the material target and exact candidate/input revision, a single action class (`photo_reference`, `material_pbr` or `tiled_microdetail`), fixed render settings and a reference to the immutable JSON report.

Example data **inside** an actual node (not a replacement schema):

```json
{
  "hypothesis": "A registered wood photograph improves held-out microstructure",
  "intervention": {"type": "EXPLORE", "parameters": {"change_class": "material_pbr", "mesh": "wood_panel"}},
  "artifacts": ["runs/wood-round-02.json", "runs/diffs/photo"],
  "measurements": {
    "color_mae": null,
    "structure_mae": null,
    "detail_mae": null,
    "light_response_mae": null
  },
  "verifiers": {"crop_gate": {"ok": true}, "heldout_photo_benchmark": {"ok": null}},
  "outcome": "pending"
}
```

The example uses **null**, not invented test results. A real node also needs the required Dream-RSI `event`, `schema_version`, `run_id`, `node_id`, `parent_id`, `uncertainty`, `cost`, `rollback_reason`, and ISO timestamp fields.

## Adaptive capture requests

When the independent evaluator identifies insufficient evidence, request the **single next photo most likely to disambiguate material from geometry/lighting**. Examples: a near-perpendicular color+scale crop to clarify albedo; the same camera under raking light to see relief; another viewing direction to catch seam stretching; or a diffuse-light shot to distinguish colored shadow from pigment.

Keep extra photos out of the original test fold if they become conditioning references; establish a new held-out fold for the next evaluation. Do not retroactively retest on photos used for iteration and call that generalization.

## Scope and limitations

This stage is compatible with existing one-locked-frame and one-change-class rules; it augments only the **material evidence** after geometry is gated. Real smartphone/DSLR datasets and matching StableGen render receipts are not yet collected in the referenced draft PR. Offline synthetic unit tests prove evaluator behavior, **not** material realism. Physical reflectance needs controlled lighting and calibration; a photo-style reference alone is not photogrammetry or a measured PBR scan.
