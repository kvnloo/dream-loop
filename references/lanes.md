# Multi-lane coordination

This skill is the shared loop. Product repos do not invent a second loop.

Worktrees stay isolated. Git stays isolated. Skills coordinate here.

## Lanes

Name the lane in `.dream-loop/lane.md` (one line: product + subject). Examples:

- `helio` — house/garden still vs a locked photo
- `rally` — empty facility hero vs a locked barn still
- `garden` — one plant/pot vs a locked close-up

Do not mix two lanes in one capture or one judge context.

## Shared loop (all lanes)

1. Lock `target.png`. Write a short massing list (camera, volumes, openings). One subject.
2. Capture with one camera. Overlay target vs capture (`scripts/overlay.py`) before shaders.
3. Fresh judge subagent (see `pro-mode/workflow.md`). Composition gates lighting/materials.
4. One change class per round. If composition drops, revert that class (especially camera).
5. Every 5 rounds: score table in `.dream-loop/meta.md` (round, /10, kept?, failure). Stall if best did not rise a full point in 2 rounds — stop nibble, ask.
6. Optional tiled maps: only after shape is gated, on one mesh ortho (`tiled-mesh.md`). Never on the hero still.

## What this repo owns vs product repos

| Here (dream-loop) | Product worktree |
| SKILL.md, plus/pro workflow, judge prompt | builders, `.blend`, engine, UI |
| `scripts/overlay.py`, `scripts/tile_grid.py` | `.dream-loop/target.png` (gitignored) |
| `references/lanes.md` | `.dream-loop/meta.md` log for that subject |

Hermes profile skills (`dream-loop-cycles`, `garden-visual-twin`) must point at this file. If they disagree, this file wins.

## Proven failure modes (carry across lanes)

- Overlay-on-photo as a “render”
- Camera hunt after composition already dropped
- Sphere/pebble nibble instead of tiled PBR
- Mesh without the supporting volume (pot, aisle, wall)
- Tiling a full scene still
- Reusing the same judge child
