# dream-loop

By [@anshuc](https://x.com/anshuc). Maintained fork: [kvnloo/dream-loop](https://github.com/kvnloo/dream-loop).

An agent skill that builds a game, app, or scene with impressive visuals, by creating a closed loop:

1. AI "dreams" up a high-quality target screenshot using image generation
2. AI builds with this target in mind
3. A separate AI critic compares the live screenshot to the target and provides feedback
4. AI loops back to step 2 until the critic is satisfied
5. Optionally, AI loops back to step 1 and dreams up an even better target based on the current state.

## Installation

Upstream: `npx skills add achimala/dream-loop`

This maintained fork: `npx skills add kvnloo/dream-loop`, or clone into your agent's skills directory, or paste the link into your agent and tell it to figure it out.

## Drop into Hermes

1. Clone this repo into a Hermes skills dir, e.g. `~/.hermes/skills/software-development/dream-loop` or a profile `skills/software-development/dream-loop`.
2. Confirm `SKILL.md` is at the skill root (Hermes loads that file).
3. Product work stays in **that product’s** gitignored `.dream-loop/` (copy `templates/meta.md` there). Never merge other products’ worktrees or stills.
4. Lock one frame (a close-up or facility hero), one camera, one capture. Each round: overlay + `scripts/crop_gate.py` (exit ≠ 0 skips lighting/materials judging; continue with a camera or massing action). Then a **fresh** judge child with the verbatim prompt in `references/hard-gates.md`.
5. One change class per round. Stall if best score is not +1 in 2 rounds — ask the user; do not nibble.
6. Progress is MEDIA (target + capture + overlay), not a status paragraph.
7. Do not git-track sqlite under `.dream-loop/`. Do not TDD the render.

This fork’s gates live in `references/hard-gates.md`.

## Prerequisites

You need an AI agent with:

- access to image generation, either built-in (e.g. Codex, Grok) or via API (e.g. give it a Gemini API key)
- vision input
- subagents (optional but strongly preferred)

Install Blender if you want custom 3D modeling. The Blender MCP or scripting interface is preferred to computer use; it produces better results.

At the moment this is only tested with GPT-6 Astra in Codex. Other strong models like Claude Fable 5.1 can likely work too.

## Example

Prompt:
> Build me a graphics demo: isometric camera, voxel-ish art style with realistic shading and reflective wet floors, a character in an interesting scene. Fantasy setting (think Elden Ring, Diablo). Three.js in browser, >60fps. Don't download assets. Time limit of 1 hour. Controls: click to move the character, camera lazy-follows; drag to rotate camera; scroll to zoom in/out. No gameplay for now. World should feel alive: motion, animations, subtle environmental behaviors. Area around player should look expansive, but only allow movement in a limited space. No need to confirm the art with me or ask questions, just go!

GPT-6 Astra on high effort in Codex:

![Vesper demo: an isometric fantasy scene](assets/vesper-preview.gif)

[Try the live demo](https://dream-loop-demo.anshu.dev)

## Classic workflow

The [pre-simplify gated judge + asset-first loop](references/classic/README.md) lives under `references/classic/` (restored from upstream git history). Use it when you want stricter iteration than the default Plus/Pro split. Say **Dream Loop Classic** in your prompt.

## Contributing

This fork welcomes PRs at [kvnloo/dream-loop](https://github.com/kvnloo/dream-loop). Please still credit Anshu as the original author.

See [CONTRIBUTING.md](CONTRIBUTING.md). If you open a PR, please provide example results produced by the skill when the change could affect visual quality, to ensure the changes don't regress performance.
