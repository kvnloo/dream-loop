# Data-driven loop evaluation

## Separate the things being measured

Use explicit owner labels as ground truth for scoped preference/acceptance. Keep
technical validity, brief compliance, pairwise preference, owner acceptance and
scheduler selection separate. No response is not approval; judge /10 is not truth
or a probability. Preserve raw verdicts and adjudication independently.

Freeze an evaluation cohort: target/brief/preferences, fixture/capture state,
renderer/version/settings, output and delivered evidence resolution, masks,
builder context, judge model/prompt, gate version and history visibility. A change
opens a new cohort; rejudge an unchanged anchor rather than splicing score curves.
Do not claim improvement caused by a changed prompt, resolution or reference.

## Compatible discovery records

Keep the [existing discovery-tree v1 ledger](discovery-tree.md) and its exported
`appendDiscoveryNode`, `readDiscoveryTree`, `readLedger`, `readRounds` APIs. Its
explicit numeric costs do NOT accept null. The older local branch lacked these
files; this pack imports the pinned fork's implementation/tests rather than
inventing an incompatible replacement. Serialize writes; validation+append is not
a multiwriter transaction.

Use [rounds.schema.json](../templates/rounds.schema.json) for linked **v2 observation
sidecars** in `observations-v2.jsonl`, NOT direct insertion into legacy rounds.
Reference run/node IDs without rewriting historical events. Preserve unknown cost
as null with measurement status; never manufacture zero to satisfy a v1 field.
If original costs are unknown, retain the record in v2 until a deliberate migration
is implemented. This pack specifies that bridge; it does not silently migrate it.

Record primary parent plus dependency parents; integrated combinations are a DAG,
not automatically the last round's child. Include observed-before IDs, legal actions,
context/policy hashes, hypothesis/family/defect, intended and realized intervention,
source/capture hashes, evidence completeness, typed failures, directives and owner
label events. Do not infer lineage/time from filenames or a contact-sheet order.
Include rejects, failed calls, no-ops, interrupted and censored attempts.

Use [defect ledger](../templates/defect-ledger.md) and `defect_guard.py` before dispatch.
After two failures of a stable defect, stop before a third; new parameter/family names
do not reset it. Reopening requires a real owner checkpoint and hash-bound receipt,
not a scheduler override. A located bug can justify a proposed repair, not bypass
this budget. Keep successful anchors and parked features.

## Owner-calibrated native-crop judges

1. Collect explicit historical choices only when bound to exact candidate hashes.
   Keep quote, scope, preference/tie/uncertain, acceptance separately, first blocker,
   and decision time. Then collect prospective blinded comparisons at native crop
   and intended whole-frame size. Include clear wins, subtle regressions, ties,
   approved deviations, wrong style, low-resolution and missing-image failures.
2. Randomize the first side, reverse the second; hide producer/round/score/history.
   An opaque path is not enough if artwork or a narrative leaks identity. Track
   successfully loaded images, delivered dimensions, crop boxes/resampling and unknowns.
3. Split by project/reference/defect lineage, not neighboring renders. Keep related
   crops and siblings together. Use development, calibration and untouched evaluation
   partitions; a small diagnostic pilot does not justify a universal accuracy claim.
4. Compare current critic, blinded pairwise judge, optionally another model family,
   and simple metrics. Same-model multiple sessions are correlated. Tune thresholds
   only on calibration; owner chooses false-acceptance tolerance and practical margin.
5. Report numerator/denominator: owner-decisive agreement, ties/abstention coverage,
   false acceptance and false rejection, swap consistency, repeated-call disagreement,
   blocker detection and protected-regression sensitivity. Cluster uncertainty by
   scene/project, not by repeated calls. Brier/calibration needs actual probabilities;
   do not divide /10 scores by ten. Small evidence means abstain, not universal PASS.
6. Retain sentinel anchors and known bad controls. Recalibrate after a model, prompt,
   preprocessing or domain change. LPIPS/DISTS/DreamSim can aid retrieval/regression
   triage; they are not a single reward for unattended artistic optimization.

## Prefix-only replay — specified protocol, not a deployed optimizer

Dream-RSI dreaming is replaying discovery history, not re-dreaming a target image.
A controller may reveal only recorded legal outcomes from the visible prefix.
Hide future scores/IDs/owner advice and evaluator-only normalization. Require parent
and all dependency closure. No parent+child in one batch, duplicate spending,
unrecorded merge, or inferred outcome for a new prompt/model/fixture/representation.
Unsupported is UNKNOWN, not zero and not predicted success. Real paid failures
remain charged. Owner labels are revealed only after a charged query when modeling
that action. Never invent propensities or claim causal off-policy correction without
known overlap and action probabilities.

Begin with incumbent, round-robin, random, greedy and fixed-depth/stop baselines.
Compare one bounded candidate portfolio/policy at a time, including the incumbent;
report all tested policies. Use whole trajectories and anchors, not only latest
scores. Distinguish repairable implementation bugs, underexplored and repeatedly
unpromising families. Replay plans remain inside owner scope and resource limits.

Tune on development worlds, select on validation, consume held-out whole projects/
late worlds once. Log policy decision tapes, unsupported actions, support coverage,
censored work and legal failures. Same-history non-regression from keeping the
incumbent is not a future-live guarantee. Replaying recorded outcomes and estimating
scheduling makespan are different claims; one GPU cannot become many in simulation.

Track a quality/cost frontier with cohort-specific named attainment stages, not
ratios of ordinal aesthetic totals. Charge builder, critic, policy search, repairs,
failed render, queue/CPU/GPU/wall time, validation, token/API cost and owner attention;
unknown stays unknown. Report best-observed AND delivered artifact, and time to
first acceptable result including censored never-acceptable runs.

An offline winner earns a bounded paired prospective test from identical frozen
inputs, matched budgets/models and randomized run order—not promotion. Owner judges
final artifacts blind. Count incumbent-success/candidate-failure regressions even
when average gains rise. Predeclare practical quality/cost margins, canary on fresh
projects, keep rollback pointer and all failure history. If evidence is weak, retain
incumbent. Fix poor measurement before optimizing scheduling; change candidate
families/headroom when trajectories are flat.

## Local pilot lesson (not a validated universal policy)

The Quackles 2026-10 offline evaluation reports three retrospectively bound owner
pairs: brief-aware judging matched 2/3, plain A/B 1/3; full-frame/native/both evidence
setups tied and three same-model votes did not improve pair-level accuracy. Briefs
were reconstructed with knowledge of owner priorities; this was not held out. Use
the result to justify prospective objective/calibration work, not an accuracy claim
or a mandate for more panels. Crops make fine details inspectable; this pilot did
not establish their accuracy advantage.

Its logged-path two-nonimprovement truncations also lost later kept changes. Our
two-defect-failure gate therefore stops **dispatch for an owner checkpoint or a new
authorized hypothesis**, not the entire project as finished. It is not a proven
GPU-time saving or complete off-policy replay. Dataset joins/unknown parents/costs
remain partial; see the case study for exact source identity and limitations.

## Qualify durable rules, not just documents

A fresh-agent plan test on an unseen Three.js game or Blender watch checks whether
instructions transfer. It does NOT prove visual skill, rendering, runtime or owner
acceptance. Save prompt/transcript and criterion audit. Then compare old/new rule
on real held-out fixtures with equal budgets, baseline controls and actual outputs.
Test known sabotage: wrong receiver, lost glow, stale capture, missing native crop,
wrong owner text, theme-port drift. Diagnostic tools can qualify by exposing seeded
failures before image improvement, but later repair utility remains to be shown.

Ablate noncritical prescriptions, not safety/owner locks. Keep concise facts+goals
when they outperform micromanagement; consolidate rules only with retained cases
and validation. Separate proposed/pilot/qualified/deployed states. No weight training,
novel-policy speedup or measured art-quality gain is claimed by this method pack.
