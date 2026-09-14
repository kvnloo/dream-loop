# Dream Loop Plus Workflow

## Note on orchestrator model

This workflow is designed not to be run by very large models like GPT-6 Astra or Claude Fable. If you are such a model, stop, and ask the user to switch to a smaller model (e.g. GPT-5.6 Luna on xhigh reasoning, or Claude Sonnet/Opus). Only proceed if they insist.

If the user asked for **Dream Loop Classic** or the **gated judge**, stop this document and follow [references/classic/README.md](../classic/README.md) instead. Do not mix Classic with this Plus worker loop.

## Loop Structure

Prerequisites:
- The target image (`.dream-loop/target.png`). After generating it, write `.dream-loop/target.json` `{width,height,prompt,source}` when knowable. Confirm a generated target once unless the user said "just go". See [classic/concept.md](../classic/concept.md) for overbaked/oversimplified checks.

Your job is NOT to build the product yourself. Your job is to orchestrate more powerful subagents to build it for you.

Subagent configuration:
- Create subagents with the strongest available model at the lowest available reasoning. For example, GPT-6 Astra at Light effort
- Always give subagents a fresh, empty context; do not fork
- Always use true subagents in the same thread. Do not create separate threads/tasks
- Always give subagents the latest product screenshot (if any), the target image, and the user's asks. Prompt them to look at the product relative to the target and do everything it takes to close the gap from the product to the target, across composition, layout, lighting, materials, texturing, reflections, fine details, shaders, animations, character behaviors, controls, or anything else. Give them the absolute path to [references/plus-mode/assets-3d.md](assets-3d.md) to reference for asset generation. Instruct them to implement the code but not test/validate, as you will do this. Inform them that they are the worker and should not use the Dream Loop skill themselves. Do not give them specific tasks or opinions, only this high-level directive in a concise prompt. They are smarter than you and will figure out what to do.

The loop:
1. Create a subagent to do a pass at the target
2. Test and validate the product yourself and ensure it works as expected. In particular, generated assets often land in the wrong orientation and the subagent won't know. Fix any issues like this you spot. Don't try to improve the visuals to align to the target, only fix bugs, loading issues, etc. **Exception:** you may apply the cheap critic's top blockers from the previous round (step 4).
3. Capture a screenshot of the product's current state. If the browser tool cannot save a PNG, use [scripts/preview-server.py](../../scripts/preview-server.py) (`POST /__capture`; compare at `/__compare`).
4. Run a **cheap critic** at the lowest reasoning (a tiny subagent, or the orchestrator itself if no subagent is available). It must emit a short JSON verdict `{ "score": <0-10>, "blockers": [] }` matching [verdict.schema.json](../verdict.schema.json). Append one line to `.dream-loop/rounds.jsonl` (`scripts/loop-state.mjs` `appendRound`).
5. If `score >= 7` **or** this was round 3, stop and ask the user to review. Otherwise you may apply the critic's top blockers yourself (still no freeform visual redesign), then loop back to 1.

Keep a round count. Cap at **3 rounds** unless the user asks for more. Ask the human only after 3 rounds or `score >= 7` — not after every pass.

## Spend

Warn that Fal and tokens add up. Optional `.dream-loop/budget.json`: `{ "maxFalUsd", "maxRounds" }` — honor it if present; there is no live meter. `fal-batch check` prints the Fal job count. If you are on ChatGPT Plus (or equivalent), wrap up when approaching the **5h** session limit or **20% of weekly** usage, as in [classic Plus](../classic/plus-mode.md).
