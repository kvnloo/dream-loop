# Compatibility and retained capabilities

[V2's core](../SKILL.md) is the default and takes precedence. These references are integrated into the v2 index, not a second installation. Existing paths remain stable for scripts, external links and older projects; the Classic subtree is the compatibility layout. No fork-main helper or schema was dropped. See [file fates](../RECONCILE.md).

## Choose one optional orchestration recipe

- [Classic overview](classic/README.md): [concept QA](classic/concept.md), [asset-first kit](classic/assets-3d.md), [compose/self-review](classic/compose.md), [gated judge/directives](classic/judge.md), [Classic Plus quota/enablement](classic/plus-mode.md), [historical monolithic text](classic/SKILL-full.md).
- [Pro](pro-mode/workflow.md) and [asset sourcing](pro-mode/assets-3d.md).
- [Plus](plus-mode/workflow.md) and [asset sourcing](plus-mode/assets-3d.md).

Do not combine these worker recipes. Retain their technical recipes and budget brakes, but obey owner-authorized scope, style, assets, services and spending. Their historical model tiers/prices/quota figures are not current offers. A score is not approval; old “done at 8” and “ask only after three rounds” rules are retired. Native Blender/procedural craft and stylization are permitted when the approved domain/brief calls for them. Default external-service permission and reinterpretation of “no downloads” are retired.

## Schemas, provenance and runtime

[Common notes](common.md) retain the target, asset, budget, capture and round conventions. JSON schemas remain at their original paths:

- [target.schema.json](target.schema.json): image dimensions, prompt/source and optional product vertical.
- [assets.schema.json](assets.schema.json): asset IDs, roles, sources, paths, status and aligned Fal job identity.
- [fps.schema.json](fps.schema.json): measured FPS and method. Measure under the judged rendering settings; `raf-2s` is a short sample, not a full performance qualification. A noninteractive ad still can mark FPS not applicable, never fabricate a measurement.
- [verdict.schema.json](verdict.schema.json): legacy Plus/Pro verdicts only. This does not validate v2 evidence sidecars or Classic free-form tier reports.
- [discovery-tree.md](discovery-tree.md): mixed event ledger, parent identity, rejected/rolled-back branches, cost and uncertainty. [V2 evals](evals.md) describe linked evidence sidecars; never migrate or rewrite old rows.

Use [lanes](lanes.md), [3D lessons](3d-what-works.md), [creative 3D](creative-3d.md), [Quackles lessons](lessons-quackles-2026-10.md), [hard gates](hard-gates.md) and [structure algorithm](structure-gate.md) as scoped references, not independent promotion policies.

## Optional tools

- [Image onboarding](onboarding.md) + [image-generate.mjs](../scripts/image-generate.mjs): environment-only backend discovery via `--check`; this CLI does **not** generate images. A configured key does not prove access, vision support or consent.
- [Fal recipes](fal.md) + [fal-batch.mjs](../scripts/fal-batch.mjs): offline preflight, resumable authorized paid submission and collection. Main's path jail, allowlist, GLB/PBR handling, uncertain-request protection and terminal states are retained. Run only reviewed jobs in a trusted workspace; lexical path checks are not an OS sandbox.
- [Preview server](../scripts/preview-server.py) + [compare page](../scripts/compare.html): localhost-only capture and target/live comparison. `POST /__capture` writes immutable timestamped PNGs plus an atomic latest alias; `/__compare` serves the viewer. It denies other dotfile paths, but this is not an authenticated hosting service. Serve a dedicated, nonsecret product evidence directory; do not expose it to a network or treat `latest.png` as an approval pointer.
- [Tiled mesh maps](tiled-mesh.md) + [tile_grid.py](../scripts/tile_grid.py): overlap split/stitch for authorized single-object maps. Not the same as v2's diagnostic [tile_splitter.py](../scripts/tile_splitter.py), which pairs target/capture crops and emits a manifest. Neither helper generates texture detail.
- [Helper contracts](scripts.md) cover v2 tools plus retained crop/overlay/PBR, with test and provenance limits.

## Tiled-map compatibility limits

The retained grid helper divides dimensions with integer division: use images whose width and height are divisible by `n`; otherwise it discards right/bottom remainder pixels. Use positive `n` and nonnegative overlap with a nonempty core. All replacement tiles must share dimensions. Stitch prefers `tile-NN.png` over `input-NN.png` and uses the **supplied** overlap, not automatic scale detection; if tiles are uniformly upscaled, pass the scaled overlap. Edge strips are replicated, but corner padding inherits the top-left color; it is context only and removed on stitch. The supported divisible-grid round trip and replacement/scale behavior are tested. This retained legacy interface is not an arbitrary-size production upscaler.

## Retired authority, retained evidence

Literal-pixel demands outside approved COPY regions, uncalibrated historical judge scores, history-anchored promotion, mandatory photorealism, blanket tool bans, implicit spending and delayed checkpoints no longer control v2. Historical text stays labelled so old results remain interpretable. Current equivalents live in [target](target.md), [critics](critics.md), [owner loop](owner-loop.md), [domain packs](domain-packs.md), [fidelity/style](fidelity-and-style.md), and the [defect ledger](../templates/defect-ledger.md).
