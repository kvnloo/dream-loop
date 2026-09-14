---
name: dream-loop
description: Match a locked target still with a 3D capture via gated loop.
license: MIT
---

# dream-loop

Closed loop: lock a target still, capture one locked frame with one camera, overlay + crop_gate (failure skips lighting/materials, not camera/massing action), independent judge, one change class, stall. Pro workflow unless the user says Plus.

Do not read both Plus and Pro docs. They are not inter-compatible.

- Plus: [references/plus-mode/workflow.md](references/plus-mode/workflow.md)
- Pro: [references/pro-mode/workflow.md](references/pro-mode/workflow.md)

Hard gates (required every round): [references/hard-gates.md](references/hard-gates.md)
Same skill, different products: [references/lanes.md](references/lanes.md)
3D process: [references/3d-what-works.md](references/3d-what-works.md)
Creative skills that earned a seat: [references/creative-3d.md](references/creative-3d.md)

Do not merge product worktrees. Do not mix stills. Product skills must not rewrite the judge rubric; this repo wins.

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

## Target

Store `.dream-loop/target.png`. User photo or generated. Do not swap subjects mid-round. If no image tool, stop and ask.

Create `.dream-loop` for working files and gitignore it. Copy [templates/meta.md](templates/meta.md) there once.

## Time budget

If given, record time after locking target.png. Do not degrade fidelity to hit the clock. If none, run until exit, warn about tokens.
