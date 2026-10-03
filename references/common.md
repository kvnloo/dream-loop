# Shared Dream Loop notes

Read this after choosing Plus or Pro. Do not load the other mode's workflow.

## Working directory

Create `.dream-loop/` for run state and **gitignore it** (this skill's `.gitignore` already lists it). Put the target screenshot at `.dream-loop/target.png`. After generating a target, also write `.dream-loop/target.json` when width, height, prompt, and source are knowable (see [target.schema.json](target.schema.json)). Optional `vertical`: `realtime-game` | `product-viz` | `ad-still`.

## Fal

Image-to-3D goes through [fal.md](fal.md) and [scripts/fal-batch.mjs](../scripts/fal-batch.mjs). Keep Fal job `id` values aligned with `.dream-loop/assets.json` (see [assets.schema.json](assets.schema.json)). Write that manifest **before** composing the scene. Default H3.1 `face_limit` is **80000**.

## Capture

If the browser tool cannot save a PNG, run [scripts/preview-server.py](../scripts/preview-server.py) from the product workspace:

```sh
python3 /path/to/dream-loop/scripts/preview-server.py --directory /path/to/workspace --port 4172
```

POST a PNG to `/__capture` (saved under `.dream-loop/captures/`, including atomic `latest.png`). Open `/__compare` for a side-by-side target | live | note view ([scripts/compare.html](../scripts/compare.html)). The server does not serve other dotfiles (no `.env`).

## Rounds

After each critic/judge pass, append one JSON line to `.dream-loop/rounds.jsonl` matching [verdict.schema.json](verdict.schema.json). Helper:

```sh
node --input-type=module -e "import { appendRound } from '/path/to/dream-loop/scripts/loop-state.mjs'; appendRound('.dream-loop', record)"
```

Plus cheap critic: `{ "score": <0-10>, "blockers": [] }`. Pro judge: rubric `score` + `total` + `blockers` + `fps_ok`.

## Spend

Warn before a long Fal or token run. Optional `.dream-loop/budget.json`: `{ "maxFalUsd": <number>, "maxRounds": <number> }`. There is no live meter — honor the file if present. `node scripts/fal-batch.mjs check .dream-loop/fal-jobs.json` prints `jobCount`.
