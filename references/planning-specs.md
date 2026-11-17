# Planning specs for number-bearing image loops

Use when an image-ideation loop renders screens that show figures (planning, traffic, transit, zoning, curb, data HUDs). Image critics judge look and layout; they cannot check arithmetic or honesty from pixels, and they will accept a screen while naming its clutter as the top issue. Put those checks in code.

## Spec contract (ideator emits one per direction)

- `numbers[]`: label, value, unit, exact on-screen `display` text, `source` (product data, formula, named citation, or ESTIMATE whose display says EST). At most 6 per screen.
- `before` on at least one number, so the screen shows before -> after. A bare result with no delta reads as decoration and the critic rejects it later anyway; reject it before render instead.
- `cost`: plain words for what the proposal gives up (lane, parking, lawn, sun, money). Require it to be stated, not invented: "unknowns" (zoning, limits not modelled) are valid content.
- `controls[]`: every control visible at once. Budget it (7 was workable) and tell the ideator to show one editing surface at a time.
- `section` (required for street states: traffic, transit, curb, section): segments with a use and width that sum to the right-of-way within 0.1 m, each width inside NACTO-like ranges.
- `far`: parcel area, floor area, FAR, optional zone FAR, height, storeys.
- `shadow`: height, sun altitude, length.

## Validator rules (deterministic, no model calls)

| Rule | Check |
|---|---|
| FAR | floor area / parcel area = FAR (5%) |
| Shadow | length = height / tan(sun altitude) (5%) |
| Section | segments sum to row; widths in range |
| Variance | FAR above zone FAR needs a readout containing VARIANCE and the overage (real planning allows variances; a hard cap rules them out) |
| Lot coverage | FAR / storeys <= 1 |
| Storey height | height / storeys within 2.5-6 m |
| Delta, cost, controls | present; controls within budget |

Add rules state-aware (`validate(spec, state)`) so old callers keep the base rules. Write each rule's test red first. On failure, re-ask once with the error list; drop directions that still fail and close the round with 0 renders spent. Expect previously accepted parents to fail new rules; keep them as parents and let the next child meet the bar rather than evicting them to a wrong-state seed.

## Render checks (after the critic picks a winner, before it can become a parent)

1. One vision call transcribes every numeric readout verbatim and counts the planning tool's interactive controls, excluding the host app's own chrome (toolbars, side menus, bottom bar). Cache the result per round, keyed so older caches without a count are re-asked.
2. Compare deterministically: any figure on screen not in the spec's display strings (garbled digits such as 19.2 drawn as 1.9.2, or invented figures) -> park. Spec figures missing from the screen are reported, not parked.
3. Controls drawn > min(listed, budget) + slack (2) -> park. Vision counts are noisy, so park only on a clear excess.
4. Transcription or count failed -> park (fail closed). Give the transcriber a fallback model; a cheap model that answered the ping can still rate-limit the real call.
5. Calibrate the counter on the owner-approved reference and on screens the critic called cluttered before switching the gate on; the reference must pass and the cluttered screens must fail clearly. Without the chrome exclusion, every render fails.

Tesseract output on stylised HUD renders is noise; use a vision model.

## Rotation

Pick the least-recently-run state; break ties toward states the owner named explicitly (e.g. traffic) and states a code lane is building, so his named topics are not left to a random tie-break.
