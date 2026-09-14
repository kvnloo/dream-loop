# Same skills, different products

dream-loop is a **skill pack**. Helio-cortex, Rally House, and GrowTwin are **different products**. They do not share git, stills, cameras, or a status bus.

What they share: this repo’s loop (lock target → overlay → crop_gate **skips lighting if fail** → independent judge → one change class → stall), `scripts/overlay.py`, `scripts/crop_gate.py`, [hard-gates.md](hard-gates.md), optional `scripts/tile_grid.py`, and [3d-what-works.md](3d-what-works.md) (process, not product scores).

Product-specific procedure stays in that product’s profile skill (`dream-loop-cycles`, `garden-visual-twin`, helio docs). Those skills must not rewrite the judge rubric. If they disagree with the **judge rubric**, this repo wins. Product skills **do** define what the locked frame contains (one plant vs facility hero). Do not treat “one subject” as “never render a hall.”

## Per product

Each product has its own worktree and its own `.dream-loop/` (gitignored). Never judge product A’s capture against product B’s target. Never merge those worktrees to “coordinate.”

## Skill rules that travel (not product facts)

1. One locked frame, one camera, one capture. Frame = `target.png`, not “must be a single object.”
2. Overlay target vs capture before shaders. Vanishing-line miss is composition, not materials.
3. Keep the camera that raised composition. Revert if the next round drops.
4. Stall: best score not +1 in two rounds → stop nibble, ask. Meta table every 5 lives **in that product’s** `.dream-loop/meta.md`.
5. Tiled PBR for dirt/lawn/masonry/acrylic. No sphere nibble.
6. Tiled mesh maps only after shape is gated, on one mesh ortho — never on a full scene still.
7. Fresh judge child every round.
8. bpy authoring: prefer Astra high-effort. Grok-4.6 / GPT-5.6-sol are backups. Do not use free Nemotron for mesh/material scripts (camera + shading fail). Image-to-mesh is TRELLIS, not LLM bpy.

Product names (basil r9, barn r12, etc.) do not belong in this file.
