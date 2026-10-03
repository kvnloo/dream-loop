# Hard gates (Helios process, no product names)

These gate lighting/materials judging, not camera or massing action. Overlay + crop_gate before shaders. One locked frame, one camera, one capture.

`crop_gate.py` is an edge-residual heuristic, not a vanishing-line detector. Inspect the overlay even on PASS; texture and contrast changes can affect the metric. It resizes the capture to the target dimensions, so supply the same aspect ratio rather than relying on stretching. Python 3.10+ and Pillow are required (`python -m pip install Pillow`).

## Every round

1. Lock `.dream-loop/target.png`. Do not swap the locked frame.
2. One locked frame, one camera, one capture. The frame may be a close-up **or** a whole-hall hero — that is a product fact (`lanes.md`). Do not add extras that are not in `target.png`.
3. `python scripts/overlay.py .dream-loop/target.png capture.png .dream-loop/overlays`
4. `python scripts/crop_gate.py .dream-loop/target.png capture.png .dream-loop/overlays` — if exit ≠ 0, vanishing-line miss is composition fail: **skip lighting/materials judge**. Do **not** freeze the loop; change camera or massing.
5. Keep the camera that raised composition. Revert if the next score drops. Camera is a valid change class when overlay disagrees. Euler-only is forbidden when the judge already named a massing hole (aisle, opening, pot, soil).
6. Independent **fresh** judge child every round. Never reuse the child. Rubric: composition 0–3, lighting 0–3, materials 0–3, details 0–1, total /10.
7. One change class per round: camera **or** massing **or** material **or** one mesh. Not all of them.
8. Progress is MEDIA of target + capture (and overlay). Not a status paragraph.
9. Tiled PBR for dirt / lawn / masonry. No sphere nibble.
10. Every 5 rounds: table in **that product’s** `.dream-loop/meta.md` (see `templates/meta.md`).
11. Stall: best score not +1 in 2 rounds → stop nibble, ask the user.
12. Do not mix other products’ worktrees, stills, cameras, or extras. Same skill, different products: [lanes.md](lanes.md).
13. Do not git-track sqlite process state. `.dream-loop/` is gitignored.
14. Do not TDD the render. Tests do not substitute for overlay + judge.

## Judge prompt (verbatim)

Give the child this plus image paths. Do not rewrite the rubric.

You are judging how close the current product is relative to the target image. Score along this rubric:

- **Composition (0-3):** Are the camera, framing, and layout correct? Are the position and scale of all major components correct compared to the target image?
- **Lighting (0-3):** Check color palette, exposure, shadows, contrast, and atmosphere. Pay attention to reflections, glows, etc. Ensure the scene overall is not too dark or too light compared to the target.
- **Materials (0-3):** Check that every surface looks right, with the expected textures, roughness, translucency, wetness, etc. Ensure assets don't look blocky, plasticky, smooth, or fake, unless the target image specifically also does this.
- **Details (0-1):** Go through everything with a fine-toothed comb. Not a single pixel should be different. Every tiny speck and detail should match between the two images.

You can give fractional scores. You should be nitpicky and precise, and include a list of all gaps and blockers that need to be resolved for a perfect score on each category. It's OK to output a gigantic list if the current product is nowhere close to the target. It needs to be comprehensive and actionable so that another agent could go fix everything on the list, come back, and get a substantially improved score. Avoid non-actionable feedback like "This tree looks fake." You need to name exactly what's giving that impression and how the agent should fix it.
Everything is within reason. If models or scenes need to be completely redesigned, say so. Don't sugarcoat it. The goal is for both images to be identical. The product should exactly reach the target. Do not settle for less.

You should lastly also provide a total score out of 10 by summing these up.

If a previous verdict and screenshot are provided, maintain consistency with prior judgment, but do not feel obligated to match or increase score. If the product regressed, it should score worse.

If crop_gate failed, judge composition and name one camera or massing action only. Mark lighting, materials, details, and total /10 as not judged; do not invent a comparable total from a partial verdict.
