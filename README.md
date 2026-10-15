# dream-loop

**An evidence-driven visual iteration method for agents and their owners.**

Dream-loop v2 turns “make it look right” into a repeatable process: lock the target and intent, reproduce the baseline, test one hypothesis, inspect real output, and keep only an evidenced improvement. It works across still images, Blender, Three.js, games, UI and interactive products. It is a method and a portable skill pack—not a renderer, an autonomous approval system, or a promise that a good screenshot means a working product.

Maintained by Kevin ([kvnloo](https://github.com/kvnloo)). Start with [SKILL.md](SKILL.md).

## What v2 does

- **Owner gates:** explicit COPY versus INTENT, approved deviations, scoped preferences, exemplar approval, and a visible checkpoint after every batch. Technical preservation, brief compliance and owner acceptance are separate decisions.
- **Calibrated critics:** structure before polish; fresh blind A/B judgments with swapped sides; owner-labelled anchors, ties and abstention. Scores and votes are evidence, never release permission.
- **Max-zoom fidelity:** final-density native crops, source-texel coverage and delivered-image audits. Upscaling is not recovered detail. Authorized projection-painted textures must be baked onto real meshes, not substituted as a paint-over of the final render.
- **Discovery tree:** append-only, parent-linked attempts—including rejects and rollbacks—with artifact hashes, uncertainty and costs. Legacy ledger readers still work. This is a history foundation, not a shipped replay-policy optimizer.
- **Domain packs:** renderer/capture, runtime, performance and style contracts for different products; isolated component lanes, deterministic integration, protected regions and variant propagation.
- **Bounded iteration:** a stable defect ledger blocks a third focused attempt after two failures until the owner chooses a new direction.

## Install

Review the checkout before giving an agent access to its scripts. Install the **whole repository**, not just SKILL.md: references, templates and scripts are part of the contract. Use one active copy named `dream-loop` per agent scope. Do not overwrite an existing installation without reviewing and backing it up.

The commands below are POSIX shell examples for Linux/macOS (or WSL). On Windows, clone/copy the complete directory into the equivalent skill directory. Python helpers are portable; host-specific capture/model tooling still needs a separate preflight.

**Release availability:** this v2 change is prepared locally, not yet published. After it is merged, the default clone below installs v2. Before merge, use a reviewed local v2 checkout, or the feature branch only after its owner publishes it; do not assume remote `main` already contains v2. Check `version: 2.0.0` in SKILL.md.

### Hermes Agent

Choose the **active profile's** home, not another profile. In a shell for that profile, with `HERMES_HOME` explicitly set to its directory:

```sh
mkdir -p "${HERMES_HOME:?Set HERMES_HOME to the active profile first}/skills/creative"
git clone https://github.com/kvnloo/dream-loop.git "$HERMES_HOME/skills/creative/dream-loop"
```

Alternatively, link a reviewed local checkout into that location, or add it to `skills.external_dirs` using `hermes config set` while preserving existing entries. Follow the [Hermes skills documentation](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/#external-skill-directories). Start a fresh session and load `/dream-loop`; ask `skill_view(name="dream-loop")` to verify the source path and version.

**Name collision:** the official optional skill is also `dream-loop` / `creative/dream-loop`; `creative-dream-loop` is its documentation slug, not a separate namespace. Project/local copies can shadow external copies. Explicitly choose one; do not rely on scan order or install two competing policies. External directories are writable when filesystem permissions permit—they are not a sandbox.

### Claude Code

Install for your user:

```sh
mkdir -p "$HOME/.claude/skills"
git clone https://github.com/kvnloo/dream-loop.git "$HOME/.claude/skills/dream-loop"
```

Or clone into `.claude/skills/dream-loop` inside a product repository for project scope. Start Claude Code and invoke `/dream-loop`. See [Claude Code skills](https://code.claude.com/docs/en/skills). Read SKILL.md and resolve its helper paths relative to the skill directory, not the product working directory.

### Codex

Install for your user:

```sh
mkdir -p "$HOME/.agents/skills"
git clone https://github.com/kvnloo/dream-loop.git "$HOME/.agents/skills/dream-loop"
```

Or use `.agents/skills/dream-loop` inside a product repository. Codex supports symlinked skill folders too. Select it with `/skills` or `$dream-loop`; restart if it does not appear. See [Codex skills](https://developers.openai.com/codex/skills/).

The method is harness-independent. Translate Hermes tool names to your host's equivalents. The optional `ab_judge.py --execute` adapter specifically requires a working Hermes CLI; its default prepare-only output can be used to run fresh judges manually in another harness. Verify actual vision delivery and model availability; installation alone does not qualify either.

## First run

1. Supply the exact target, current artifact, authorized scope and capture/viewer path. Existing targets are not regenerated without permission.
2. Resolve owner preferences into [BRIEF](templates/BRIEF.md), freeze inputs and reproduce a no-change baseline.
3. Follow [the core procedure](SKILL.md), select a [domain pack](references/domain-packs.md), and use [helper contracts](references/scripts.md) for commands.
4. Store working evidence in the **product's** gitignored `.dream-loop/`, not inside this installed skill. Preserve every attempt; CURRENT is explicit selection, not approval.

## Pack layout

| Location | Purpose |
| --- | --- |
| [SKILL.md](SKILL.md) | Default method and reference index |
| [references/](references/) | Target/style, gates, critics, owner loop, fidelity, research, provenance, domains and evaluation |
| [templates/](templates/) | Briefs, preferences, worker packets, judge prompts, selectors and ledger schemas |
| [scripts/](scripts/) | Offline image helpers, schema/lint tests, discovery ledger, optional Fal and capture utilities |
| [Compatibility index](references/compatibility.md) | Retained Classic/Pro/Plus, schemas, onboarding, capture and tiled mesh tools |
| [Quackles case study](case-studies/quackles-2026-10.md) | Provenance and limits of one application, not a required template |
| [RECONCILE.md](RECONCILE.md) | File-by-file accounting of fork-main capabilities and retired policies |

## Tests

Python 3.10+ and Node 18+ are required. From the checkout, create an isolated Python environment and install the test dependencies:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r scripts/requirements-test.txt
python scripts/run_tests.py
node --test scripts/*.test.mjs
python scripts/lint_skill.py
```

The runner executes every `*.test.py` and `*.test.mjs` plus the skill/link/schema/syntax lint, preserving each exit status. `--receipt PATH.json` writes a new receipt and refuses to overwrite one. Tests use synthetic fixtures and local HTTP; no paid API calls or real visual-quality claims. Live rendering, model quality, target-family calibration, interaction and owner approval require separate evidence.

## Compatibility

V2 is the default; Classic, Pro and Plus are opt-in historical orchestration recipes, not policies to mix together. Existing script paths and ledger APIs remain available. Owner intent and permissions supersede literal-pixel demands, default spending, model-tier assumptions and score-only promotion. A five-round summary does not replace per-batch checkpoints. Legacy asset manifests, FPS receipts, budget brakes and compare/capture tooling remain useful; see [compatibility](references/compatibility.md) and [v2.0.0 changes](CHANGELOG.md).

## Credits and license

Dream-loop grew from [Anshu Chimala's original dream-loop](https://github.com/achimala/dream-loop). We retain its history, original copyright notice, optional historical recipes and illustration. Kevin (kvnloo), with Hermes Agent, developed the project-agnostic v2 method and reconciliation. This is an independently maintained project, currently hosted in that GitHub fork network; it does not imply upstream endorsement.

The discovery-history design credits Tong Zheng et al., [**Dream-RSI: Recursive Self-Improvement through Evolving Worlds**](https://arxiv.org/abs/2609.14858), arXiv:2609.14858. This repository implements an event-sourced ledger inspired by that work, not the paper's complete system or reported results. The citation is not a license grant for paper code or datasets; none are vendored here.

[MIT licensed](LICENSE). The original `Copyright (c) 2026 Anshu Chimala` notice and permission text are retained unchanged. Upstream is also MIT, compatible with this continued MIT distribution. Keep that notice in copies or substantial portions; check separate licenses for third-party assets and services.

![Original Vesper scene](assets/vesper-preview.gif)

[Original demo](https://dream-loop-demo.anshu.dev). This inherited illustration is **not** a v2 evaluation result. See [CONTRIBUTING.md](CONTRIBUTING.md) for evidence requirements.
