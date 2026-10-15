# Data-driven improvement of the loop

## Ground truth and discovery tree

Use the owner's versioned labels as ground truth for preference/acceptance, not the judge's highest score. Preserve separate technical, brief and owner fields. Append each attempted intervention to `rounds.jsonl` using [round schema](../templates/rounds.schema.json): project/target/brief, round/parent, hypothesis/gap/change class, inputs/outputs and hashes, execution, gate results, judge protocol/receipts, owner decision, keep/reject reason, parked features and next question. A branch is an experiment; a tree preserves alternatives and prevents rejected features disappearing.

Never rewrite raw verdicts to fit the owner. Store adjudication beside them. Record missing evidence, interrupted runs, costs, elapsed time and retries; excluding failures makes the process look better than it is.

## Calibrate before trusting automation

Freeze an owner-labelled calibration set containing clear wins/losses, ties, approved deviations, protected regressions, style ambiguities, mismatched evidence resolutions and invalid captures. Run identical paired prompts both orders, with fresh contexts and anchors. Measure agreement with owner, side/order sensitivity, false promotion of protected regressions, abstentions and evidence coverage. Report numerator/denominator and uncertainty; same-model agreement is not independent accuracy.

Freeze rubric/model/evidence transforms before evaluation. Split by project/target family rather than adjacent rounds of the same scene; otherwise near-duplicates leak into held-out tests. Do not tune thresholds on the final evaluation examples. Re-run old and proposed gate suites on must-pass/must-fail cases before changing policy.

## Offline replay and skill proposals

Replay historical decisions against immutable captures without new rendering where possible. Compare existing policy with one proposed rule under equal evidence and budget, blind to owner labels until scoring. Evaluate visual acceptance per cost/time, missed regressions, completion/evidence rate and repeated-blocker rate, not just average /10.

A retrospective plan test checks instruction transfer, not visual skill. Add fresh unseen projects (for example a Three.js isometric game and a Blender watch photograph), ask a fresh agent for a plan using only this pack, and manually check target/style, COPY/INTENT, gates, native review, owner cadence, research/coupons, protected state, integration and runtime needs. Preserve prompts/transcripts and gaps; fix the skill and repeat when necessary.

Promote a lesson only after a counterexample/control and successful replay or explicitly label it provisional. Keep proposed skill changes separate from production rules until reviewed. Detailed research integration and benchmark recommendations are added in the research synthesis; no claims of measured aesthetic improvement follow merely from this schema.
