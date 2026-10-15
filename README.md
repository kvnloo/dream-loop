# dream-loop v2

A project-agnostic visual iteration skill: lock intent and target, capture real output, test one hypothesis, inspect fresh evidence, and checkpoint with the owner. Covers stills, Blender scenes, Three.js/games and UI without treating screenshots as proof of functionality.

Original dream-loop by [Anshu / @anshuc](https://x.com/anshuc), upstream [achimala/dream-loop](https://github.com/achimala/dream-loop). This [kvnloo fork](https://github.com/kvnloo/dream-loop) adds methods distilled with Kevin (kvnloo). MIT; original attribution and helper interfaces retained.

## Load and use

Install this repository as one `dream-loop` skill root in the **active** Hermes profile. The [current Hermes documentation](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/#external-skill-directories) supports `skills.external_dirs`; add the checkout path to that list through `hermes config set` while preserving other entries, or link the reviewed checkout once into the active profile's skills tree. Verify the chosen route in a fresh session with `skill_view(name="dream-loop")`, source path and version 2.0.0.

**Resolve the name collision first:** the official optional skill's actual name/path is `dream-loop` / `creative/dream-loop`; `creative-dream-loop` is its documentation slug, not a separate safe namespace. Local copies shadow external ones, project skills outrank both, and two different same-name skills inside one root require path-qualified loading. Back up and explicitly choose which copy stays active; do not delete/reset another profile or rely on scan order. Do not preload two competing loop policies. External directories are writable by skill tools when filesystem permissions allow them; they are not a sandbox. See [evaluation/compatibility](references/evals.md).

Other agents can consume SKILL.md directly. `npx skills add achimala/dream-loop` installs UPSTREAM, not this fork's v2; choose the repository/revision intentionally. No automatic install or profile changes are performed by this repository.

## Pack structure

- [SKILL.md](SKILL.md): core loop, hard rules and reference index.
- `references/`: target/style, gates, critics, owner loop, component lanes, research, variants, provenance, evaluation and domain contracts.
- `templates/`: brief/preferences, delegation, judge prompts, current selector, discovery ledger schema and integration adapter skeleton.
- `scripts/`: retained upstream helpers plus portable tiling, validation/aggregation, comparison and swapped A/B runner.
- [Quackles case study](case-studies/quackles-2026-10.md): provenance and limits, not a template product.

Use product-owned gitignored `.dream-loop/` or an assigned artifact directory. Keep input originals immutable and every attempt discoverable. Do not commit private renders, process databases or credentials here.

## Run tests

Through Hermes `terminal(command="python scripts/run_tests.py", workdir=<checkout>)`.
Python 3.10+ with Pillow, NumPy, PyYAML and jsonschema; Node 18+ for retained Fal tests. Tests are offline and use temporary synthetic fixtures, not visual-production claims. See [script contracts](references/scripts.md).

## Compatibility and intentional v2 changes

Existing script names/CLI interfaces remain. Legacy Pro and Plus docs and their asset recipes remain accessible, but do not mix those two orchestration modes. V2 is the default process and overrides historical policy where it conflicts:

- Owner-approved COPY/INTENT and locked deviations supersede “every pixel identical.” The old judge rubric remains verbatim for reproducibility, not authority to change owner choices.
- Structure gates remain hard unless an owner-authorized revision explicitly makes them diagnostic. After PASS, optimize appearance, not the gate fraction.
- Fresh swapped paired comparisons replace history-carrying absolute-score promotion. ≥8/10 alone is not done.
- Checkpoint after every batch and record every round; a five-round summary is not a substitute.
- Two failed focused trials trigger a strategy decision; uncalibrated +1 scores cannot justify endless nibbling.
- Asset sources, models, paid services and projection-painted **baked mesh textures** are opt-in according to project preferences, licences and privacy. A 2D paint-over of the finished render is excluded under v2. Legacy suggestions do not authorize external uploads or spending.
- Script/unit tests verify machinery; actual output and owner/device review verify visuals and behavior.

Retained illustration from upstream:

![Vesper isometric fantasy scene](assets/vesper-preview.gif)

[Original demo](https://dream-loop-demo.anshu.dev). This illustration is not a v2 evaluation result. Contribute new rules with controls, failure cases and transfer evidence, not just attractive examples.
