# Turning accepted dream screens into product code

Use when the owner asks to "implement it for real" after a dream loop has accepted planning screens. The accepted images and specs are the target and the golden data. They are never shipped as product.

## Procedure
1. Map each accepted state to the product's existing owner modules first (for example massing, sun, plot picker, EST formatter). Read their PRs or files. A dream decision usually extends an existing owner; never write a second one.
2. Write one lane per accepted state, in chain order. A dependent state (growth after shadow) stacks on the earlier lane's branch, and its launch is gated on the earlier lane's `LANE-DONE`. Arm that wait as a background job that launches the next lane, and log the job id.
3. Each brief carries:
   - the target picture path, the spec path (`ideas.json` direction plus the HUD manifest), and the decision in numbers;
   - the defects the critics or vision found on the accepted screen, marked "do not copy" (duplicated figures, a score with no basis on screen, a qualitative "cost");
   - the dream HUD's critic-learned display rules (one headline callout, quantity-named tips with EST, spaced arrows, each figure once), by pointing at the compositor and validator code.
4. M1 is a deterministic table over one pure function, written before any code. Its golden case reproduces the accepted spec's numbers (e.g. 6 → 3 storeys, shadow 32.5 → 16.2 m against a 20 m edge). Add cases for missing inputs (null, not 0), no-op, an infeasible edge (min 1, flagged) and one other locale. Where the dream pinned an assumed input (sun altitude), add a case deriving it from the product's own model, so the golden case is not a hand-typed constant.
5. Product figures come from the product's own estimators. When an estimator disagrees with the dream's figures, log the gap; never tune constants to match the picture.
6. M2 is a scripted journey with before/after screenshots that assert DOM readouts and drawn geometry equal to M1. Then fresh cheap readers per screenshot must read the decision's numbers back (≥4/5). A sheet of product screenshot | accepted dream image read by a stronger model is a critic, not the gate.
6b. Numbers-correct is not done: put a LOOK gate in the same brief. Readers that only read numbers back pass a translucent debug box with a pasted flat shadow polygon, on a substitute basemap, and the owner calls that slop on sight. Required in every 3D state brief:
   - capture on the same imagery/tiles the dream target sits on (e.g. photoreal 3D tiles, not a keyless fallback). If that needs a key, capture off the sandbox on a fleet node with the key injected into that job only; if it can't run, the lane reports BLOCKED, never a fallback dressed as the target;
   - geometry built from the decision (one band per storey, shopfront, windows, parapet, opaque and scene-lit; "proposal" marked by an edge glow, not transparency);
   - a real engine shadow measured by on/off luminance in the shadow polygon (≥25% drop, sun control <5%, far edge within ±2 m of the computed length), with the baseline taken first because overlay shadows measure ratio 1.00;
   - fresh art-director readers asked "real building / placeholder box, real cast shadow / overlay" (≥4/5 real/real), baselined on the current screenshot.
   Before reporting a done 3D PR, look at its after-shot next to the dream target yourself and name the look gap in the report; a disclaimer such as "the screenshot uses the fallback globe" is a known gap, not a finished state.
7. The later state must keep the earlier decision (a shadow-fitted building stays locked through growth stages): make it an M1 case and a journey assertion, not prose.
8. Verify every `LANE-DONE` yourself (PR head equals the gated sha, gate summary fail=0) before reporting it.
