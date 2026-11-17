# Loop, gates and stop rules

## Establish the comparison

Reproduce a no-change control before attributing improvement to an edit. Freeze target revision, capture state, renderer version, sampling, seed, color pipeline and masks. In games/pages also freeze viewport, DPR, fonts/assets readiness and animation state; test interaction/performance separately. Screenshot parity is not control parity.

Run overlay before expensive polish through `terminal`; use [script contracts](scripts.md). Assert equal aspect first: the retained crop/overlay helpers resize to target dimensions and can stretch a wrong-aspect capture. Never use local crop warps to hide misalignment.

## Technical gate hierarchy

- Use `crop_gate.py` for its documented edge heuristic, not as a vanishing-line detector. Inspect its overlay even on PASS. A hard structure failure restricts the next round to camera/massing; it does not freeze all work.
- Change camera only in an authorized camera round; keep improvements and restore the last accepted camera on regression. If the blocker is a missing mass/opening, stop Euler nudges and build the mass. With a camera-dependent projection, changing the camera also invalidates artwork and delivery evidence.
- If texture dominates the gate, compare old/new gates on a known-answer suite before switching to `structure_gate.py`. Include shifts, rotation, scale/lens, mirrors, missing small/large masses as must-fail; re-encodes, mild blur/sharpening, grain, color/exposure, material-only and relit renders as must-pass. Fit on target-derived cases and hold out render-derived cases, then reverse. Choose a stable parameter plateau, not one passing candidate. [Algorithm and limits](structure-gate.md).
- Structure thresholds are target-family-specific. Strong moved shadows or large printed artwork can register as structure. Record a disputed failure as a blocker; do not lower thresholds until the candidate passes.
- Mask scene-irrelevant UI identically on both images. White means ignore. Prefer normalized exclusion in the structure gate; neutral-filled temporary copies for the legacy crop gate can introduce boundary edges and remain diagnostic. Keep original target untouched. Physical text, labels and poster art stay in scope. Review DOM/UI as a separate layer against the shipped page.
- Owner-authorized exclusions (locked asset silhouette, accepted alternate geometry) need a versioned mask and revalidated suite: every remaining must-fail still fails. For explicit INTENT/local-alignment review, record acceptance revision and authorization; global gate may be diagnostic while each tile is pass/limited/blocked. Never silently reinterpret a failed hard gate as diagnostic.
- After a gate passes, it is PASS/FAIL, not an optimization score. Tiny numeric drift or denominator changes must not veto better imagery that still passes.

## Three independent decisions

| Gate | Evidence | What it does NOT prove |
|---|---|---|
| Technical preservation | identity/state guards, save/reopen replay, capture/gate, runtime tests | beauty or brief completion |
| Brief fidelity | fresh evidence, COPY/INTENT row status, blind preference, local gaps | owner approval or release |
| Owner acceptance | explicit checkpoint decision at a named version | permission to ignore technical defects |

An owner may accept a deliberate aesthetic deviation; update the brief and affected calibration without erasing raw judge findings. An owner-approved look does not magically fix a technical failure. A judge HOLD cannot block showing a preview. Promotion requires the declared technical constraints and explicit selection policy, not score ≥8 alone.

## Attributable rounds and stopping

- Start from the latest selected/kept lineage, not a rejected branch. Record a missing reject first. Make one change class (camera, massing/layout, material, lighting, mesh/component, typography, behavior, display) per round. If one physical hypothesis genuinely needs coupled classes, declare the coupling and controls before execution; do not smuggle unrelated edits into it.
- Record every round immediately; summarize after each batch (the old every-five-round table is supplementary, never the only checkpoint).
- If the same top blocker survives two focused trials, stop. Present the failed hypothesis and two different strategies, recommendation, cost/risk and required permissions. The legacy “no +1 in two rounds” is useful only with a fixed calibrated scoring setup; changed judges/resolution cannot reset the stall clock.
- Park useful rejected features with paths and reasons. If the owner chooses one later, port that feature onto current lineage, preserving later wins; do not roll the whole project back.
- Finish only when the owner's visual brief, technical requirements and delivery/runtime checks are met, or report the explicit stopped/blocked state. Tests for code are required; tests alone cannot approve a render.
