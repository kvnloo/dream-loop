---
name: dream-loop
description: Build a game or app from a description so that a live screenshot matches a generated rendering. Use when the user says "dream loop" or asks for something built to a very high level of graphical fidelity.
license: MIT
---

# dream-loop

This is a process for you to autonomously build extremely impressive visuals, especially for 3D scenes (e.g. in a game or app).

Closed loop: lock a target still, capture one locked frame with one camera, overlay + crop_gate (failure skips lighting/materials, not camera/massing action), independent judge, one change class, stall.

If this is the first run, or you do not have image generation, read [references/onboarding.md](references/onboarding.md) before continuing.

Your first step is to determine which workflow to use:
- If the user told you to use the Plus or Pro workflow explicitly, that's your answer
- If not, check if the user is on a low or high tier coding subscription. "Low tier" means ChatGPT Plus or equivalent. "High tier" means ChatGPT Pro. For low-tier subscriptions, use the Plus workflow. For high-tier, use the Pro workflow.

- Plus: [references/plus-mode/workflow.md](references/plus-mode/workflow.md)
- Pro: [references/pro-mode/workflow.md](references/pro-mode/workflow.md)

After that choice, also read [references/common.md](references/common.md). That is the one shared document both workflows may load.

Do not read both Plus and Pro workflow documents. They are not inter-compatible.

**Classic workflow (optional):** If the user asks for **Dream Loop Classic**, the **gated judge**, or **asset-first** iteration, read [references/classic/README.md](references/classic/README.md) and follow that read order instead of Plus/Pro above. Classic and Plus/Pro must not be mixed in one run.

Hard gates (required every Pro / Classic still-match round): [references/hard-gates.md](references/hard-gates.md)
Same skill, different products: [references/lanes.md](references/lanes.md)
3D process: [references/3d-what-works.md](references/3d-what-works.md)
Creative skills that earned a seat: [references/creative-3d.md](references/creative-3d.md)

Do not merge product worktrees. Do not mix stills. Product skills must not rewrite the judge rubric; this repo wins.

# Guidance applicable to both workflows

## General

Create and use a `.dream-loop` folder for working context/files, and gitignore it. Copy [templates/meta.md](templates/meta.md) there once.

Record 3D assets in `.dream-loop/assets.json` (see [references/assets.schema.json](references/assets.schema.json)) before composing the scene.

If the browser tool cannot save a PNG, run [scripts/preview-server.py](scripts/preview-server.py) (`POST /__capture`; side-by-side at `/__compare`). Captures land in `.dream-loop/captures/`.

## Hard gates

1. One **locked frame**, one camera, one capture. The frame is whatever `target.png` is (plant close-up **or** facility hero). Do not add a second product, HUD, or sibling subject into that frame.
2. Overlay target vs capture **before shaders**: `python scripts/overlay.py .dream-loop/target.png capture.png .dream-loop/overlays`
3. `python scripts/crop_gate.py .dream-loop/target.png capture.png .dream-loop/overlays` — if exit ≠ 0, **do not judge lighting/materials**. Still take a camera or massing action this round. It is not a freeze.
4. Keep the camera that raised composition. Revert if score drops. Camera **is** a valid change class when overlay lines miss. Euler-only is forbidden only when massing blockers are already listed (do not hunt loc/look instead of adding the missing aisle/opening).
5. Fresh judge child every round (never reuse). Composition 0–3, lighting 0–3, materials 0–3, details 0–1. Prompt: [references/hard-gates.md](references/hard-gates.md) verbatim.
6. One change class per round (camera **or** massing **or** material **or** one mesh).
7. Meta table every 5 rounds in **that product’s** `.dream-loop/meta.md` from [templates/meta.md](templates/meta.md).
8. Stall: best score not +1 in 2 rounds → stop nibble, ask the user.
9. Tiled PBR for dirt/lawn; no sphere nibble.
10. Progress = MEDIA of target + capture, not status text.
11. `.dream-loop/` gitignored. No git-tracked sqlite process. Do not TDD renders.

## The target image

The key piece of Dream Loop is to first create the "dream version" of the user request using image generation, then iterate to build it.

If the user supplies this, use that directly.
If not, you need to generate it.

If you don't have an image generation tool, stop and ask the user to either provide the target image, or connect you to an image generation API. See [references/onboarding.md](references/onboarding.md).

Before generating the image, determine if there is an existing product or if you're starting fresh. If fresh, you can directly generate a new image. If there's an existing product, you should capture a screenshot of the current version of it, then use that as the baseline input to the image model and generate a refined version of it based on the user direction, so that it is an improvement over the original and not a divergence.

When generating images, avoid using words like "concept art" in the prompt. This is not an artist's interpretation. It is meant to be an exact, realistic target screenshot. You will try to match it down to the pixel. For example, if the user is asking you to make a game, you should prompt the image model for a real in-engine screenshot of the target. Not a cinematic shot, photo, painting, artist concept, etc.

Watch for **overbaked** (noisy photographic clutter) and **oversimplified** (toy/flat) targets; see [references/classic/concept.md](references/classic/concept.md). Confirm a generated target with the user once unless they said "just go".

Store the image in `.dream-loop/target.png`. After generating it, write `.dream-loop/target.json` `{width,height,prompt,source}` when those are knowable. Optional `vertical`: `realtime-game` | `product-viz` | `ad-still` (see [references/target.schema.json](references/target.schema.json)). Do not swap subjects mid-round.

## Optional: tiled mesh maps

For **one object** that needs fabric, hair, pores, or other microtexture, after camera/crop is locked, use [references/tiled-mesh.md](references/tiled-mesh.md) and `scripts/tile_grid.py`. Do not tile a full scene still or replace `target.png`.

## Time budget

If the user gives a time budget, record the time at start of the loop (after locking target.png), and check the clock between rounds.

Don't degrade visual fidelity to hit the time budget. Don't take shortcuts. It's better to hit the time limit with meaningful, beautiful progress than with something roughly complete but ugly.

If the user doesn't give a time budget, run until you hit an exit criterion, but warn that this may consume a lot of tokens.

## Spend caps

Warn before a long Fal or token run. Optional `.dream-loop/budget.json`: `{ "maxFalUsd": <number>, "maxRounds": <number> }`. There is no live spend meter; honor the file if present. `node scripts/fal-batch.mjs check .dream-loop/fal-jobs.json` prints the Fal job count. ChatGPT Plus: wrap up near **5h** or **20% of weekly** quota (see the Plus workflow).
