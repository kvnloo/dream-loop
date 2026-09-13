# Classic workflow (pre–Sep 2026 simplify)

Anshu removed this stack in commit `9bddb90` (“simplify Plus workflow… cheaper”). It is **restored here as an optional path** for forks that want the stricter loop: gated judge, concept QA, asset-first gate, compose protocol, Plus quota brakes, and `assets.json` schema.

**Default remains** the current split: [plus-mode/workflow.md](../plus-mode/workflow.md) and [pro-mode/workflow.md](../pro-mode/workflow.md). Do not load classic and current Plus/Pro workflows in the same run.

## When to use classic

- User asks for **“Dream Loop Classic”**, **gated judge**, or **asset-first** workflow.
- You want **Tier 1–5** scoring with **LANDED / PARTIAL / NOT DONE** directive tracking (max 4 extra directives per round).
- Plus with **Astra enablement gate** and **5h / 20% weekly** quota tracking (see [plus-mode.md](plus-mode.md)).

## Read order (classic Pro or unified high-tier)

1. [concept.md](concept.md) — target QA, overbaked/oversimplified checks, `concept.png` (same role as `target.png` in the simplified skill; use one filename consistently in `.dream-loop/`).
2. [assets-3d.md](assets-3d.md) — plan kit → `.dream-loop/assets.json` → parallel Fal → **no scene code until kit validates**.
3. [compose.md](compose.md) — lighting, landmarks, FPS, self-review before judge.
4. [judge.md](judge.md) — gated 0–10 rubric for the critic subagent.

For **Classic Plus**, read [plus-mode.md](plus-mode.md) instead of the simplified Plus worker loop.

Full router text from the old monolithic skill: [SKILL-full.md](SKILL-full.md) (paths inside that file refer to `references/classic/` equivalents).

## Relation to current skill

| Classic | Current (simplified) |
|--------|----------------------|
| Gated tiers + directive ledger | Pro additive 0–3+0–3+0–3+0–1 |
| Asset-first, `assets.json` required | Assets doc only; no schema |
| Plus: judge + quota + enablement gate | Plus: 3 unguided workers, no judge |
| `concept.png` naming | `target.png` naming |

Upstream history: `9161a01` (classic) → `9bddb90` (simplify).
