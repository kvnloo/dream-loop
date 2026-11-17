# Dream step: change the exploration direction when a defect sticks

Run this step after **two assessed visual nonwins on the same element and stable defect**, or when the owner asks for new directions. Dream-RSI here means an archive-grounded portfolio plus a prefix-only scheduling audit. It does **not** mean generating a new target, training model weights, predicting unseen render scores or claiming the official Dream-RSI simulator has been reproduced.

## Executable entry point

The implementation is included in this tree. Run from the repository root with an explicit external data directory; optionally select a trusted adapter as described in [meta-learning](meta-learning.md).

```sh
python scripts/meta_loop.py --data /path/to/meta-loop stuck
python scripts/meta_loop.py --data /path/to/meta-loop dream --element sample-base
python scripts/meta_loop.py --data /path/to/meta-loop dream --element sample-panel --defect sample-density
python scripts/meta_loop.py --data /path/to/meta-loop next --element sample-lens
python scripts/dream_step.test.py
```

`dream` writes `dream/<element>.json` and `.md`; an exact `--defect` adds a stable hash suffix so it cannot overwrite the whole-element portfolio. `stuck` lists all qualifying element/defect pairs. `next` includes `dream` automatically when its element is stuck. No command launches Blender, contacts a model, changes CURRENT or appends an owner label.

Analytical subelements and specialist taxonomies are adapter policies. The default uses the supplied element identity and a general proposal vocabulary; it invents no stable defect IDs.

## Evidence and trigger

1. Materialize event revisions once per trial and apply the real owner overlay. Check artifact hashes. Fail closed on invalid or incomplete event streams and on archive changes during the CLI read.
2. Count only timestamped, completed visual experiments. Owner decisions and qualified judge results retain their provenance. Explicit verified hard-gate failures, producer crop failures, mechanism failures and residual reference mismatches can trigger **diagnostic** exploration without becoming acceptance-learning labels.
3. HOLD, missing approval, a pending review or absent cost is not failure. Implementation/resource/evidence failures, controls, delivery-only records and report documents do not consume the visual budget. Repeated configurations without evidence of a distinct scene do not inflate it. A later evidenced success clears the assessed failure streak.
4. Preserve unknown observations and unresolved defect IDs visibly. Missing chronology cannot prove a streak. Do not rename a family to reset the defect budget.

## Portfolio contract

Each ranked direction contains a hypothesis, mechanism class, explicit construction parameters, cheapest coupon, expected signal, cost estimate and basis, risk, reason, evidence trial IDs and hash-bound starting artifacts. Rank is a disclosed heuristic, not a learned probability of aesthetic success.

Include these distinct sources of ideas:

- **Breadth:** untried or under-tried classes and materially different constructions—target-projected regional masks, separate response layers and source-bound traced vectors; specialist constructions require an explicit adapter. Broad classes can contain different constructions; another seed or small parameter change is not a new direction.
- **Partial-feature recombination:** quote precisely what each source trial got right, including the surrounding warning. Prefer different lanes. Use A-only, B-only, A+B and unchanged-parent coupons. Do not require completed recipe promotion to investigate a partial feature, and do not mistake investigation for promotion.
- **Recipe transfer:** preserve the donor script, inputs, parameters and failure notes. Select a compatible component, not its whole failed appearance: Compatibility must be established by the receiver adapter; the default leaves it unproven. Test inert import, idempotence and receiver compatibility.
- **Counterfactual scheduling:** compare breadth, continued depth and an earlier switch after two assessed nonwins, revealing only strictly earlier timestamped observations. List where alternatives lacked exploration. Unsupported outcomes and policy value stay null.
- **One wildcard:** reserve an explicit interpretation-changing coupon, such as a negative-space exemplar. Keep the target locked and obtain owner interpretation approval before expanding it.

Reject near-duplicates on mechanism plus semantic parameters; ignore cosmetic seeds/names and tolerate small numeric differences. Record suppressed proposals. Missing common parameters mean similarity is poorly observed, not proof of novelty—read the structural hypothesis against the failed artifacts before dispatch.

Do not duplicate a pending mechanism or a completed experiment still awaiting review. Preserve its full proposals under `reserved_directions` with `await_pending_mechanism`; re-evaluate when the active experiment is adjudicated. Consolidate identical directions across defects while retaining every covered defect and evidence ID. A reserved optical portfolio is still useful analysis, not authorization to start a second optics worker.

## Replay limits

The current implementation audits **timestamped materialized trial observations**, not an original-time reconstruction of every revision. Recommendations see only earlier rows in their element/defect sequence; equal-time peers are not secretly ordered. A mechanism match is weak logged support, not proof of identical parameters, parent state, cohort or worker behavior. Archive revisions, coupled scene changes and unknown chronology limit interpretation.

Never report a counterfactual beauty score, GPU saving or superior controller from this audit. A listed exploration gap means “the earlier-switch rule would have tried another class here,” not “that class would have worked.” Test the next controller prospectively on real coupons and retain rejected outcomes.

## Dispatch and publication

- Read the ranked portfolio and the exact source artifacts, not only the first headline. Check the current brief, permissions, source hash and pending queue again.
- Select a structurally different coupon under a locked fixture. Keep LOOK and CLEAR paired. A structure defect cannot be solved by blur or surface noise.
- Publish the element JSON/Markdown and a summary enumerating every stuck defect from `stuck`; count coverage programmatically. Explain missing or reserved slots rather than inventing donors or costs.
- Keep archive reads separate from the rating service's materializer: `stuck`, `dream` and `next` use read-only ingestion and write no producer logs, owner events, ledger or shared reports. `dream` writes only its portfolio files. Do not restart the owner server just to run this CLI.
- Test trigger reset/exclusions, revision identity, duplicate filtering, pending reservations, exact defect filtering, cross-lane component transfer, prefix invariance, fail-closed CLI behavior and publication. Verify the real owner log remains unchanged during tests; synthetic fixtures belong only in disposable directories.

Source distinction: the procedural inspiration is the [official Dream-RSI code](https://github.com/google-research/dream-rsi); the local adapter deliberately makes narrower claims.
