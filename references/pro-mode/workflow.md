# Dream Loop Pro Workflow

## Loop Structure

Prerequisites:
- The target image (`.dream-loop/target.png`). After generating it, write `.dream-loop/target.json` `{width,height,prompt,source}` when knowable, including optional `vertical`: `realtime-game` | `product-viz` | `ad-still`. Confirm a generated target once unless the user said "just go". See [classic/concept.md](../classic/concept.md) for overbaked/oversimplified checks.

The loop:
1. Take a first pass at implementing the target. One locked frame, one camera, one capture. Match `target.png`, whether a close-up or facility hero.
2. Test and validate the product yourself and ensure it works and looks as you intend.
3. Capture a screenshot of the product's current state. If the browser tool cannot save a PNG, use [scripts/preview-server.py](../../scripts/preview-server.py) (`POST /__capture`; compare at `/__compare`).
4. Overlay then crop_gate **before shaders**. If `scripts/crop_gate.py` exits non-zero, composition fail — skip lighting/materials judging, but continue with a camera or massing action. Keep/revert camera based on composition.
5. One change class this round only (camera **or** massing **or** material **or** one mesh).
6. Submit the screenshot + target + overlay/crop-gate result to an independent judge subagent with a fresh context (see below).
7. Address the judge’s **one** change class carefully. Recapture the same camera unless the class was camera. If composition dropped, revert the camera. Camera is a valid change class; do not euler-nibble when massing blockers are already listed.
8. Test and validate the product yourself and ensure it works and looks as you intend.
9. Every 5 rounds: append [templates/meta.md](../../templates/meta.md) in this product’s `.dream-loop/meta.md`.
10. Evaluate exit criteria (below). If you should exit, stop here. If not, return to step 3 and loop again.

## 3D Assets

During implementation, you may need 3D assets. At such times, consult [references/pro-mode/assets-3d.md](assets-3d.md) to decide how to get them. Do not just make procedural assets out of laziness, read the doc and make the correct decision. Write `.dream-loop/assets.json` before scene compose.

## Judge

Judging should ideally be done by a fresh subagent with a clean context each time, to keep it objective and cheap.

The judge should be given the latest live screenshot, the target image, the overlay and crop gate result, the previous round's screenshot and verdict if any, `.dream-loop/target.json` (for `vertical`), and the verbatim prompt in [hard-gates.md](../hard-gates.md). On crop failure, use its composition-only override (no total /10). The full-score rubric below applies only after the crop gate passes:

> You are judging how close the current product is relative to the target image. Score along this rubric:
>
> - **Composition (0-3):** Are the camera, framing, and layout correct? Are the position and scale of all major components correct compared to the target image?
> - **Lighting (0-3):** Check color palette, exposure, shadows, contrast, and atmosphere. Pay attention to reflections, glows, etc. Ensure the scene overall is not too dark or too light compared to the target.
> - **Materials (0-3):** Check that every surface looks right, with the expected textures, roughness, translucency, wetness, etc. Ensure assets don't look blocky, plasticky, smooth, or fake, unless the target image specifically also does this.
> - **Details (0-1):** Go through everything with a fine-toothed comb. Not a single pixel should be different. Every tiny speck and detail should match between the two images.
>
> You can give fractional scores. You should be nitpicky and precise, and include a list of all gaps and blockers that need to be resolved for a perfect score on each category. It's OK to output a gigantic list if the current product is nowhere close to the target. It needs to be comprehensive and actionable so that another agent could go fix everything on the list, come back, and get a substantially improved score. Avoid non-actionable feedback like "This tree looks fake." You need to name exactly what's giving that impression and how the agent should fix it.
> Everything is within reason. If models or scenes need to be completely redesigned, say so. Don't sugarcoat it. The goal is for both images to be identical. The product should exactly reach the target. Do not settle for less.
>
> You should lastly also provide a total score out of 10 by summing these up.
>
> If a previous verdict and screenshot are provided, maintain consistency with prior judgment, but do not feel obligated to match or increase score. If the product regressed, it should score worse.
>
> If `vertical` is `ad-still`, FPS is optional; also note Brand/fidelity (logo, product, copy, uncluttered hero) as a short extra note, not a fifth numeric category.
>
> Output MUST be JSON matching references/verdict.schema.json: `score` (composition, lighting, materials, details), `total`, `blockers` (array of strings), `fps_ok` (boolean).

Append one JSON line per round to `.dream-loop/rounds.jsonl` (use `scripts/loop-state.mjs` `appendRound`). Plus cheap critic uses the same file.

## Same skill, different products

Unrelated products may reuse this workflow. Follow [../lanes.md](../lanes.md). Do not mix their stills or extras. Overlay + crop_gate before judging lighting. One change class per round. No git-tracked sqlite. No TDD-for-renders.

## Exit criteria

Measure FPS when the product is interactive: `requestAnimationFrame` average over 2 seconds, or Chrome's FPS meter if available. Write `.dream-loop/fps.json` `{ "fps": <number>, "method": "raf-2s" | "chrome-fps" }` ([fps.schema.json](../fps.schema.json)). Do not invent a number if you cannot measure. For `vertical: ad-still`, FPS is optional.

- **score >= 8 and target FPS acceptable**: done! Show the user the latest screenshot and ask if they want more iterations. (`ad-still` may treat FPS as acceptable without a measurement.)
- **score >= 8 but target FPS unacceptable**: optimize, aiming for lossless wins first, then optimizations that have minimal visual impact. Re-judge after optimizations to ensure you didn't regress visuals.
- **Stall approaching**: the best score hasn't improved by a full point in 2 rounds, or the judge has named the same gap 2 times in a row. **Stop nibble. Do not euler-hunt.** Step back and rethink the entire approach and scene, and try to find architectural or big-picture reasons why you're not reaching the target image. It may be that assets are just not good enough, in completely wrong places, the lighting needs to be reworked entirely, the camera is totally wrongly positioned, or other such major issues. Do not make small changes, aim for a dramatic improvement.
- **Stalled**: you tried the **Stall approaching** large architectural change but it didn't work; the judge still gave the same score or worse. Don't waste tokens trying other dramatic changes. Stop and ask the user to weigh in on if the current state looks good enough or if something is significantly off compared to the target. A later architectural rethink is allowed only after the user says continue.
- **None of the above**: Continue looping. Do not exit.
