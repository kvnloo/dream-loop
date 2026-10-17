# V2 reconciliation

## Scope and lineage

- Fork main / PRs #1, #5 and #6: `928a3510b2a1410312b84b1c50f79de117359165`.
- Original v2 branch `feat/codified-methods-v2`: `b1323322f8f4d214c05353a0747f3c53d4e4b375` (left unchanged).
- New `feat/dream-loop-v2` starts at fork main and merges the original v2 branch with both parents preserved. No rebase, force update, branch deletion or squash is used locally.
- Work is prepared in a separate worktree; the installed checkout changes only after validation and a clean-tree check. No push, PR or GitHub settings change is part of this reconciliation.

V2's structure, methods, templates, case study and core SKILL.md win. Main's newer Fal/preview safety fixes and discovery ledger win over older copies on the v2 branch. All **48 files in main** are accounted for below, including **20 main-only files absent from the original v2 tip**. None of main's executable helpers, tests, schema contracts or historical recipes is deleted. Main-only references are integrated into v2's reference index and compatibility layout; existing paths are deliberately retained rather than moved, to preserve links and script/API compatibility.

## File ledger

“Kept; policy scoped” preserves the technical content but removes its authority to override v2. Policy retirement is explicit below. V2-only additions are listed in [CHANGELOG.md](CHANGELOG.md), not repeated as main-file fates.

| File on main | Fate | Reason | Where its content lives now |
| --- | --- | --- | --- |
| `.gitignore` | extended | Keep product ledger/database exclusions; add v2 Python cache and virtual-environment exclusions. | [.gitignore](.gitignore) |
| `CONTRIBUTING.md` | rewritten | V2 contribution/tests and explicit fork PR target replace mode-only orientation; original attribution and evidence contract retained. | [CONTRIBUTING.md](CONTRIBUTING.md); [compatibility index](references/compatibility.md) |
| `LICENSE` | kept verbatim | MIT notice matches upstream license blob dd54a3e60d5fe9e2296c4745c5b826d74158c852; attribution unchanged. | [LICENSE](LICENSE) |
| `README.md` | rewritten | Own-project overview and three harness installs; original credit, demo, licensing and retained capability links preserved. | [README.md](README.md); [compatibility index](references/compatibility.md) |
| `SKILL.md` | v2 wins | Project-agnostic owner-gated v2 procedure replaces default Plus/Pro router; legacy modes and technical contracts are indexed through references/compatibility.md. | [SKILL.md](SKILL.md); [compatibility index](references/compatibility.md) |
| `assets/vesper-preview.gif` | kept verbatim | Retain original credited illustration, explicitly not v2 benchmark evidence. | [assets/vesper-preview.gif](assets/vesper-preview.gif) |
| `references/3d-what-works.md` | superset | Keep process lessons with v2 authority notice; replace stale branch-specific editing advice. | [references/3d-what-works.md](references/3d-what-works.md) |
| `references/assets.schema.json` | kept verbatim | Keep legacy machine-readable contract at stable path; lint validates schema syntax. V2 schemas are separate, not migrations. | [references/assets.schema.json](references/assets.schema.json) |
| `references/classic/README.md` | kept; policy scoped | Keep historical concept/asset-first/compose/tier/directive/quota capability under v2 authority; fix monolithic relative links and make Classic opt-in. | [references/classic/README.md](references/classic/README.md) |
| `references/classic/SKILL-full.md` | kept; policy scoped | Keep historical concept/asset-first/compose/tier/directive/quota capability under v2 authority; fix monolithic relative links and make Classic opt-in. | [references/classic/SKILL-full.md](references/classic/SKILL-full.md) |
| `references/classic/assets-3d.md` | kept; policy scoped | Keep historical concept/asset-first/compose/tier/directive/quota capability under v2 authority; fix monolithic relative links and make Classic opt-in. | [references/classic/assets-3d.md](references/classic/assets-3d.md) |
| `references/classic/compose.md` | kept; policy scoped | Keep historical concept/asset-first/compose/tier/directive/quota capability under v2 authority; fix monolithic relative links and make Classic opt-in. | [references/classic/compose.md](references/classic/compose.md) |
| `references/classic/concept.md` | kept; policy scoped | Keep historical concept/asset-first/compose/tier/directive/quota capability under v2 authority; fix monolithic relative links and make Classic opt-in. | [references/classic/concept.md](references/classic/concept.md) |
| `references/classic/judge.md` | kept; policy scoped | Keep historical concept/asset-first/compose/tier/directive/quota capability under v2 authority; fix monolithic relative links and make Classic opt-in. | [references/classic/judge.md](references/classic/judge.md) |
| `references/classic/plus-mode.md` | kept; policy scoped | Keep historical concept/asset-first/compose/tier/directive/quota capability under v2 authority; fix monolithic relative links and make Classic opt-in. | [references/classic/plus-mode.md](references/classic/plus-mode.md) |
| `references/common.md` | kept; policy scoped | Keep main target/assets/capture/rounds/discovery/budget conventions, under explicit v2 authority. | [references/common.md](references/common.md) |
| `references/creative-3d.md` | kept; policy scoped | Keep main lessons/rubric/lane content plus v2 authority notice; no lost technical capability. | [references/creative-3d.md](references/creative-3d.md) |
| `references/discovery-tree.md` | superset | Keep main documentation plus v2 provenance, single-writer warning and separate evidence-sidecar contract. | [references/discovery-tree.md](references/discovery-tree.md) |
| `references/fal.md` | kept verbatim | Keep main recipes aligned with hardened helper, including jailed paths, defaults, serial concurrency and failure recovery. | [references/fal.md](references/fal.md) |
| `references/fps.schema.json` | kept verbatim | Keep legacy machine-readable contract at stable path; lint validates schema syntax. V2 schemas are separate, not migrations. | [references/fps.schema.json](references/fps.schema.json) |
| `references/hard-gates.md` | kept; policy scoped | Keep main lessons/rubric/lane content plus v2 authority notice; no lost technical capability. | [references/hard-gates.md](references/hard-gates.md) |
| `references/lanes.md` | kept; policy scoped | Keep main lessons/rubric/lane content plus v2 authority notice; no lost technical capability. | [references/lanes.md](references/lanes.md) |
| `references/lessons-quackles-2026-10.md` | kept; policy scoped | Keep main lessons/rubric/lane content plus v2 authority notice; no lost technical capability. | [references/lessons-quackles-2026-10.md](references/lessons-quackles-2026-10.md) |
| `references/onboarding.md` | kept verbatim | Keep host/API/ComfyUI selection and no-spend onboarding; key presence is not permission. | [references/onboarding.md](references/onboarding.md) |
| `references/plus-mode/assets-3d.md` | kept; policy scoped | Use main technical content (manifests, capture, verdict/FPS/budget receipts and tiled-map links), not the older v2 copy; v2 notice retires conflicting promotion/permission rules. | [references/plus-mode/assets-3d.md](references/plus-mode/assets-3d.md) |
| `references/plus-mode/workflow.md` | kept; policy scoped | Use main technical content (manifests, capture, verdict/FPS/budget receipts and tiled-map links), not the older v2 copy; v2 notice retires conflicting promotion/permission rules. | [references/plus-mode/workflow.md](references/plus-mode/workflow.md) |
| `references/pro-mode/assets-3d.md` | kept; policy scoped | Use main technical content (manifests, capture, verdict/FPS/budget receipts and tiled-map links), not the older v2 copy; v2 notice retires conflicting promotion/permission rules. | [references/pro-mode/assets-3d.md](references/pro-mode/assets-3d.md) |
| `references/pro-mode/workflow.md` | kept; policy scoped | Use main technical content (manifests, capture, verdict/FPS/budget receipts and tiled-map links), not the older v2 copy; v2 notice retires conflicting promotion/permission rules. | [references/pro-mode/workflow.md](references/pro-mode/workflow.md) |
| `references/structure-gate.md` | kept verbatim | Existing helper, test, algorithm reference or meta template remains available; v2 adds contracts rather than replacing this capability. | [references/structure-gate.md](references/structure-gate.md) |
| `references/target.schema.json` | kept verbatim | Keep legacy machine-readable contract at stable path; lint validates schema syntax. V2 schemas are separate, not migrations. | [references/target.schema.json](references/target.schema.json) |
| `references/tiled-mesh.md` | superset | Keep single-object split/restore/stitch/bake recipe; add owner permissions, final-density evidence and explicit helper limits. | [references/tiled-mesh.md](references/tiled-mesh.md) |
| `references/verdict.schema.json` | kept verbatim | Keep legacy machine-readable contract at stable path; lint validates schema syntax. V2 schemas are separate, not migrations. | [references/verdict.schema.json](references/verdict.schema.json) |
| `scripts/compare.html` | kept verbatim | Retain target/live browser comparison UI; complements v2 immutable comparison sheets. | [scripts/compare.html](scripts/compare.html) |
| `scripts/crop_gate.py` | kept verbatim | Existing helper, test, algorithm reference or meta template remains available; v2 adds contracts rather than replacing this capability. | [scripts/crop_gate.py](scripts/crop_gate.py) |
| `scripts/crop_gate.test.py` | kept verbatim | Existing helper, test, algorithm reference or meta template remains available; v2 adds contracts rather than replacing this capability. | [scripts/crop_gate.test.py](scripts/crop_gate.test.py) |
| `scripts/fal-batch.mjs` | kept verbatim | Keep main safety/resume, allowlist/path checks, parameter validation, terminal states, result selection and regression tests; no rollback to pre-squash v2 copy. | [scripts/fal-batch.mjs](scripts/fal-batch.mjs) |
| `scripts/fal-batch.test.mjs` | kept verbatim | Keep main safety/resume, allowlist/path checks, parameter validation, terminal states, result selection and regression tests; no rollback to pre-squash v2 copy. | [scripts/fal-batch.test.mjs](scripts/fal-batch.test.mjs) |
| `scripts/image-generate.mjs` | kept verbatim | Retain offline backend discovery and tests; this is not an image generator or paid availability probe. | [scripts/image-generate.mjs](scripts/image-generate.mjs) |
| `scripts/image-generate.test.mjs` | kept verbatim | Retain offline backend discovery and tests; this is not an image generator or paid availability probe. | [scripts/image-generate.test.mjs](scripts/image-generate.test.mjs) |
| `scripts/loop-state.mjs` | kept verbatim | PR #6 event ledger and tests are the canonical v1 implementation; six cross-version test runs pass. | [scripts/loop-state.mjs](scripts/loop-state.mjs) |
| `scripts/loop-state.test.mjs` | kept verbatim | PR #6 event ledger and tests are the canonical v1 implementation; six cross-version test runs pass. | [scripts/loop-state.test.mjs](scripts/loop-state.test.mjs) |
| `scripts/overlay.py` | kept verbatim | Existing helper, test, algorithm reference or meta template remains available; v2 adds contracts rather than replacing this capability. | [scripts/overlay.py](scripts/overlay.py) |
| `scripts/polyhaven_pbr.py` | kept verbatim | Existing helper, test, algorithm reference or meta template remains available; v2 adds contracts rather than replacing this capability. | [scripts/polyhaven_pbr.py](scripts/polyhaven_pbr.py) |
| `scripts/preview-server.py` | kept verbatim | Keep main compare route, dotfile checks, ephemeral-port reporting and atomic latest capture, not the older v2 copy. | [scripts/preview-server.py](scripts/preview-server.py) |
| `scripts/preview-server.test.mjs` | kept verbatim | Retain live localhost capture/compare/dotfile regression. | [scripts/preview-server.test.mjs](scripts/preview-server.test.mjs) |
| `scripts/structure_gate.py` | v2 wins | Preserve main structure algorithm/API; portable import fallback and right/bottom edge-window fix with regression tests. | [scripts/structure_gate.py](scripts/structure_gate.py) |
| `scripts/tile_grid.py` | kept verbatim | Retain mesh-map split/stitch API, distinct from diagnostic tile_splitter; added CLI round-trip/replacement/scaled-overlap tests and documented limits. | [scripts/tile_grid.py](scripts/tile_grid.py) |
| `templates/meta.md` | kept verbatim | Existing helper, test, algorithm reference or meta template remains available; v2 adds contracts rather than replacing this capability. | [templates/meta.md](templates/meta.md) |

## Deliberately retired policies

No implementation capability is retired. These old defaults are retired as **authority**, while historical text remains labelled for reproducing old workflows:

| Source file(s) | Retired default | Reason / current home |
| --- | --- | --- |
| SKILL.md; references/classic/SKILL-full.md; references/plus-mode/workflow.md | Infer workflow/model from subscription; require a particular model tier | Project/domain/owner scope selects the method; availability and costs require preflight. [Domain packs](references/domain-packs.md), [evals](references/evals.md). |
| references/classic/concept.md | Mandatory AAA photorealism, automatic follow-up re-dream | Approved style and original target cannot be replaced silently. [Target](references/target.md), [fidelity/style](references/fidelity-and-style.md). |
| references/classic/assets-3d.md; references/classic/plus-mode.md; references/pro-mode/assets-3d.md; references/plus-mode/assets-3d.md | Default Fal permission; reinterpret “no downloads”; blanket tool/procedural bans | Explicit owner licenses/privacy/spend/representation choices rule. Technical sourcing options and manifest remain. [Target](references/target.md), [domain packs](references/domain-packs.md). |
| references/classic/judge.md; references/hard-gates.md; references/pro-mode/workflow.md | History-anchored score as promotion authority; score >=8 as done | Keep diagnostic rubric/directive history, but use fresh calibrated blind comparisons and separate owner acceptance. [Critics](references/critics.md), [loop/gates](references/loop-and-gates.md). |
| references/plus-mode/workflow.md; references/pro-mode/workflow.md; references/classic/SKILL-full.md | Ask only after a round cap; continue below score threshold; five-round meta as the only checkpoint | Checkpoint every batch; two failed focused trials block further dispatch pending strategy choice. Keep budget caps as upper bounds, not permission to keep spending. [Owner loop](references/owner-loop.md), [defect ledger](templates/defect-ledger.md). |

## Discovery ledger equivalence

`git diff 928a3510b2a1410312b84b1c50f79de117359165 b1323322f8f4d214c05353a0747f3c53d4e4b375 -- scripts/loop-state.mjs scripts/loop-state.test.mjs` shows only the missing final newline in original v2. Reconciled implementation **and test file are byte-identical to main**, including newline. Documentation is a superset adding provenance/single-writer/sidecar limits.

Cross-tested each implementation (main, original v2, reconciled) against both test suites (main and original v2): **six independent runs, six tests each, zero failures**. They exercise legacy round validation/readback, mixed-event replay, rejected/rolled-back retention, parent/run/duplicate/root enforcement, uncertainty/cost/timestamp validation and rollback reasons. No old ledger rewrite or fake unknown-cost event is introduced. V2 richer evidence remains in a linked sidecar; the original v1 API still requires numeric costs. This ledger is single-writer, not a multiwriter transaction or the full Dream-RSI replay optimizer.

## License and attribution

The local LICENSE blob is `dd54a3e60d5fe9e2296c4745c5b826d74158c852`, identical to the upstream GitHub license API result for achimala/dream-loop. Both are MIT; the original 2026 Anshu Chimala copyright and permission notice remain unchanged. README credits and links the original project and Tong Zheng et al.'s [Dream-RSI paper](https://arxiv.org/abs/2609.14858). No paper code/assets are imported or relicensed.

## Verification and limits

**Local validation passed:** `python scripts/run_tests.py` completed 13 commands (8 Python test files, 4 Node test files, skill lint), zero failed commands. Standalone `node --test scripts/*.test.mjs` passed 26 tests, zero failures/skips. Standalone `env -u HERMES_HOME python scripts/lint_skill.py` reported zero errors across 60 Markdown, 8 JSON and 22 Python files. `git diff --check` and staged whitespace checks passed. Six ledger cross-test combinations passed separately. External receipts are kept outside the source checkout; rerun these commands on the final committed tree.

The automated runner, standalone Node suite and standalone lint must all pass before switching the installed checkout. Tests use local/synthetic fixtures, not paid services or visual acceptance. The added tile-grid tests exercise supported divisible-grid round-trip, restored-tile precedence and explicitly scaled overlap; legacy arbitrary-size/corner-padding limits are documented in [compatibility](references/compatibility.md).

The first reconciliation run caught five broken relative links in the retained Classic monolithic document; they were corrected rather than excluding legacy documentation from lint. No test or lint rule was disabled. The skill-load equivalent is the standalone `lint_skill.py` against this worktree with HERMES_HOME unset; final frontmatter must remain `name: dream-loop`, `version: 2.0.0`.
