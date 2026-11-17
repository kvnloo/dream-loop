# Planning specs for number-bearing image loops

Use when an image-ideation loop renders screens that show figures (planning, traffic, transit, zoning, curb, data HUDs). Image critics judge look and layout; they cannot check arithmetic or honesty from pixels, and they will accept a screen while naming its clutter as the top issue. Put those checks in code.

## Spec contract (ideator emits one per direction)

- `numbers[]`: label, value, unit, exact on-screen `display` text, `source` (product data, formula, named citation, or ESTIMATE whose display says EST). At most 6 per screen.
- `before` on at least one number, so the screen shows before -> after. A bare result with no delta reads as decoration and the critic rejects it later anyway; reject it before render instead.
- `cost`: plain words for what the proposal gives up (lane, parking, lawn, sun, money). Require it to be stated, not invented: "unknowns" (zoning, limits not modelled) are valid content.
- Keep control labels out of `numbers[]`, even ones that contain digits (a timeline `NOW / 5 YR / 15 YR`, a `400 m` ring toggle). The transcriber reads them as controls and skips them, so they come back as a "missing on screen" error on every round, which drowns out real misses.
- `controls[]`: every control visible at once, short labels (<= 18 chars). Budget it in actionable targets, not containers (about 6), type a draggable multi-part control as `{label, targets: n}`, and tell the ideator to show one editing surface at a time. Each step of a segmented selector (NOW / 5 YR / 15 YR) is its own target, so a timeline plus two options plus BUILD already breaks a 6-target budget: say this in the prompt.
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
| Storey height | height / storeys within 2.8-4.5 m on both before and after; the error says "change the storey count, not the floor height" (planners squash floors to 2.5 m to dodge the duplicate-plan rule) |
| Receptor | the protected edge a shadow or setback falls on is pinned in the scenario as something the PARENT picture shows (e.g. the far sidewalk at the accepted section's measured distance); specs that name any other receptor fail |
| Delta, cost, controls | present; controls within budget |

Add rules state-aware (`validate(spec, state)`) so old callers keep the base rules. Write each rule's test red first. On failure, re-ask once with the error list; drop directions that still fail and close the round with 0 renders spent.

Normalize before validating. Ideators often put newly required fields (`scope`, `cells`, `mix`, `effects`, `section`) next to `spec` instead of inside it. A spec-only validator then reports them missing, the model resends the same shape because it thinks the fields are already there, and the round dies as a false reject. Use one `lift(direction)` helper that folds the known keys into `spec` in place (keys already in `spec` win), and call it at every validate site so the render brief and render checks see the same object. Also state in the schema text that the fields go INSIDE `spec`.

Diagnose a spec-invalid round by replaying it. Re-run the round's saved raw replies (first ask and re-ask) through the current validator before changing any rule, so you can tell a model failure from a validator or schema bug. Save each reply whole, or as head plus tail: a tail-only slice cuts off the JSON's opening and nested string escaping, so a replay needs layered unescaping by hand.

After a gate change, restart the ideation service at a round-end event (see terminal-agent-orchestration), not mid-round. Expect previously accepted parents to fail new rules; keep them as parents and let the next child meet the bar rather than evicting them to a wrong-state seed.

## Render checks (after the critic picks a winner, before it can become a parent)

1. One vision call transcribes every numeric readout verbatim and counts the planning tool's interactive controls, excluding the host app's own chrome (toolbars, side menus, bottom bar). Cache the result per round, keyed so older caches without a count are re-asked.
2. Compare deterministically: any figure on screen not in the spec's display strings (garbled digits such as 19.2 drawn as 1.9.2, or invented figures) -> park. Spec figures missing from the screen are reported, not parked.
3. Controls drawn > min(listed, budget) + slack (2) -> park. Vision counts are noisy, so park only on a clear excess.
4. Transcription or count failed -> park (fail closed). Give the transcriber a fallback model; a cheap model that answered the ping can still rate-limit the real call.
5. Calibrate the counter on the owner-approved reference and on screens the critic called cluttered before switching the gate on; the reference must pass and the cluttered screens must fail clearly. Without the chrome exclusion, every render fails.

Tesseract output on stylised HUD renders is noise; use a vision model.

## Code-drawn HUD (scene-only renders)

When spec-valid screens keep losing to garbled digits, dropped lines or extra controls, split the frame. The image model draws only the 3D scene and in-world geometry (target outline, massing, lane paint, route lines, shadows, ground tints). A compositor draws the HUD from the validated spec. Then figures and control counts are right by construction.

- In code, refuse a planning brief that quotes on-screen text, spec display strings or UPPERCASE control labels, so the image model cannot redraw the HUD. Send the scene model a scene-only brief, plus only the parent's scene layer (keep `candN-scene.png` next to the composite). If it sees the old composite, it copies the panels into the scene.
- Copy the product's own design tokens into the compositor: its CSS glass colour and alpha, accent colours and mono font. Keep a contrast check (dim text >= 7:1 on the worst-case glass), because small, low-contrast grey text was the first thing a vision check flagged.
- Have the compositor write a manifest (texts drawn, controls, targets, section labels, on-map card). Tests assert against the manifest, and failed rounds become fixtures: every spec line drawn, exact control list, nothing truncated.
- Never drop a label that doesn't fit. Shrink a button label's font down to a floor instead of truncating it. Put a narrow street-section segment's width above the bar on a tick, and add a legend naming each segment colour. When labels the reader can see don't add up to the stated right-of-way, the critic rejects the screen as a contradiction.
- Put every control on the map, using the product's own in-world control. Critics reject a screen whose decisions sit in a detached side card behind a thin leader line. Moving only BUILD onto an on-map card is not enough: the next round is rejected because the other controls (time steps, options) are still away from the parcel and the main verb is unclear. Find the product's at-target control in its CSS or components (for example a radial wheel around the selected plot) and draw all spec controls as its buttons around the target. Fill only the primary action, put a headline-delta chip beside it, and keep the side panel to readouts, section, consequences and cost. Move controls, never copy them, so the target budget stays the same. Record each button's centre and radius in the manifest, and test that buttons don't overlap each other or the panel and stay inside the frame. Have the scene brief make the outline mark the thing being changed: the stop, lane, kerb segment or section for street states, and the plot only for parcel states.
- The render check becomes "stray text or UI in the scene layer" (vision transcription of the scene image), not digit transcription.
- Put the validator's numeric ranges into the planner prompt, generated from the validator's own table (e.g. the segment width ranges). Otherwise every direction breaks the same unseen rule and the round spends its one re-ask on it.
- The loop imports the compositor once, so restart the loop at a round-end event after each compositor edit, and check that the next round's prompt file carries the new text.

## Cross-state consistency: one shared scenario

Left alone, each round's ideator invents its own baseline, so accepted screens for the same neighbourhood disagree (homes, FAR and population differ between zoning, architecture and growth). The critic only compares a candidate with its own parent and never sees other states, so enforce consistency in code:

- Keep one `scenario.json` (anchor plot id and area, block/district cell counts, street right-of-way, baseline FAR/unit size/persons per home), each entry with `status` measured|assumed and a source. Take the anchor area from the real product geometry (the game grid cell the code lane already uses), so dream math and the later code feature share one denominator. Inject it into the ideation prompt.
- `validate(spec, state, ledger)`: require `scope` parcel|block|district; parcel_m2 = cells x anchor area; street sections use the scenario right-of-way. With no ledger, the older rules apply unchanged.
- Correlated figures must agree: if homes and FAR both change and their factors differ by more than 15%, require a declared `mix` (shops, bigger units). Example of a failure this catches: FAR x2 while homes x1.5 with constant persons per home.

## Cross-domain effects

Critics accept screens whose change shows no effect on other areas (shade stays "pending" while you drag trees; growth shows no street or transit effect). Require `effects[]` on planning states: at least 2 different domains, and at least 1 `computed` effect whose `calc` code re-derives (shadow = h / tan(sun altitude); parking spaces = kerb m / 6; GFA = FAR x area; homes = GFA / unit size). Methods are computed|ledger|estimate|unknown; an estimate's display says EST. A domain the product has no real model for (for example walking access without a pedestrian network) must be `unknown`; never let the ideator estimate it. Effects' display strings count as allowed figures in the render check.

## Re-auditing accepted bases and a measurable exit

When rules tighten, re-check every accepted planning spec without re-rendering and classify it: PASS (no errors), RESCOPE (only fields that older rules did not ask for are missing) or CONTRADICT (arithmetic disagrees). Only CONTRADICT is a real defect; RESCOPE parents stay parents until a child meets the new bar. Log an exit metric every round (coverage and depth as defined below). When both hold, switch to convert mode and send the owner one reel asking "enough, or more of X?", instead of rotating forever.

Shape the exit so the loop can actually reach it. Count coverage with ANY passing accept per state, not only the newest: a later rescoped accept must not erase an earlier pass. Limit coverage to the states the loop still dreams. States frozen and handed to a code lane are credited by that lane's gate receipts, not by image rounds. Measure depth as one linked chain of at least 3 accepts across at least 2 states. Each spec names `chain_from`, and every quantity both panels show (homes, FAR, height, storeys, parking, lanes) has a `before` equal to the previous panel's value, within 5%. Three good screens in unrelated states prove breadth, not a coherent plan. Add a round cap that triggers the owner ask while the loop keeps running.

When a new rule makes an old "this spec passes cleanly" test fail, add the newly required field to that test's fixture and keep its assertion unchanged; deleting or loosening the assertion weakens the test.

## Judging one decision per round

- Tell the task critic which decision the round judges: pass the state's decision text (`critic.py --decision`) and add a task-only `decision_fit` criterion ("a screen that does a different planning job well scores 0-1"). Diagnose with the per-round task margin (candidate minus parent, order-corrected, from the verdict rows): a margin that falls to about 0 once the parent becomes an accepted screen of ANOTHER state means the critic is comparing planning jobs, not this decision.
- A state's first version (borrowed seed, or grown from another state's chain head) has no own version to beat. Accept it when no layer prefers the parent, after an absolute check: the state's defining geometry is drawn and the cost is on screen (`decide(bc, parent_entry, layer, manifest, state)`). Otherwise ties against a maxed screen of another state park forever.
- Calibrate judge noise with the exact prompt the loop sends (same decision text), and measure power, not only repeatability: add a control pair (the bare scene with the HUD stripped vs the real screen, in both orders) that must lose. Identical ties score flip 0.0, which proves nothing. Record order_flip per layer too; a layer that always picks one side is position-biased. Read a failing layer by the direction it flips. A layer that moves only between tie and candidate (never parent) cannot turn a decide() result into a reject on that screen, but it can still turn an accept into a park. Report it as uncalibrated and leave the 0.25 gate where it is. Re-measure it after the next HUD change, because crowded screens are what make the layout layer unstable.
- Verify an accept that came through the first-version rule as strictly as any other: the parent.json sha equals the chain head's image, man.shadow (or the state's geometry) is drawn, cost_shown is set, the spec arithmetic re-derives (height/tan(sun), m per floor, FAR cap), and your own vision read agrees with the drawn geometry.
- Ration renders per state on a flat metric with a budget file read at proposal time (`BUDGET.json`, e.g. shadow 1, growth 2); test fixtures that count distinct plans pin the budget back to the default.
- Pin receptors to the parent picture: vision-check the chain head before a shadow or setback round. A receptor the parent lacks (a park) gets invented in a new place each render, so one sun casts shadows in opposite directions across rounds.
- When the drawn geometry already shows a change (shadow WAS/NOW tips), keep one outline callout and move the second figure to the ticker. Tip labels name the quantity and carry EST on every computed value ('SHADOW WAS 32 m · 12 m ONTO SIDEWALK EST'). Wheel-disc labels split into the most balanced two lines and keep a unit token with its number ('SUN' / '09→15 H').
- Widening a label regex (park -> park|sidewalk) can catch unrelated figures (a sidewalk WIDTH read as a receptor distance). After any widening, rerun the exit check's audit over accepts as well as the spec replay, and pin the accepted figure as a passing test.

## Rotation

Pick the least-recently-run state; break ties toward states the owner named explicitly (e.g. traffic) and states a code lane is building, so his named topics are not left to a random tie-break. Leave a single spec-invalid round out of the state's last-run time. It spent no renders and may be a validator bug, so counting it pushes a never-rendered state to the back of the queue. Count it only once a state has 2 spec-invalid rounds, which means it really cannot be planned and the rotation must move on.
