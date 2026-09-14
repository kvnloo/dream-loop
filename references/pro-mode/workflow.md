# Dream Loop Pro Workflow

## Loop Structure

Prerequisites:
- The target image

The loop:
1. One locked frame, one camera, one capture. Match `target.png`, whether a close-up or facility hero.
2. Overlay then crop_gate **before shaders**. If `scripts/crop_gate.py` exits non-zero, composition fail — skip lighting/materials judging, but continue with a camera or massing action. Keep/revert camera based on composition.
3. One change class this round only.
4. Fresh judge subagent (new context). Verbatim prompt in [hard-gates.md](../hard-gates.md).
5. Address the judge’s **one** change class. Recapture the same camera unless the class was camera.
6. If composition dropped, revert the camera. Camera is a valid change class; do not euler-nibble when massing blockers are already listed.
7. Every 5 rounds: append [templates/meta.md](../../templates/meta.md) in this product’s `.dream-loop/meta.md`.
8. Exit criteria (below). Else return to overlay + crop_gate.

## 3D Assets

During implementation, you may need 3D assets. At such times, consult [references/pro-mode/assets-3d.md](assets-3d.md) to decide how to get them. Do not just make procedural assets out of laziness, read the doc and make the correct decision.

## Judge

Judging should ideally be done by a fresh subagent with a clean context each time, to keep it objective and cheap.

The judge should be given the latest live screenshot, the target image, the overlay and crop gate result, the previous round's screenshot and verdict if any, and the verbatim prompt in [hard-gates.md](../hard-gates.md). On crop failure, use its composition-only override (no total /10). The full-score rubric below applies only after the crop gate passes:

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

## Same skill, different products

Unrelated products may reuse this workflow. Follow [../lanes.md](../lanes.md). Do not mix their stills or extras. Overlay + crop_gate before judging lighting. One change class per round. No git-tracked sqlite. No TDD-for-renders.

## Exit criteria

- **score >= 8 and target FPS acceptable**: done! Show the user the latest screenshot and ask if they want more iterations.
- **score >= 8 but target FPS unacceptable**: optimize, aiming for lossless wins first, then optimizations that have minimal visual impact. Re-judge after optimizations to ensure you didn't regress visuals.
- **Stall**: the best score hasn't improved by a full point in 2 rounds, or the judge named the same gap twice. **Stop nibble. Ask the user.** Do not euler-hunt. A later architectural rethink is allowed only after the user says continue.
- **None of the above**: Continue looping. Do not exit.