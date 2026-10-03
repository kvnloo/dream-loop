# Human review: evidence first, one decision at a time

Applies to Plus, Pro, Classic Pro, and Classic Plus. This is a shared authority/checkpoint contract, not another judge rubric. Keep each mode's existing round and spend caps. Automated checks, visual fidelity, and human preference are separate evidence lanes; none substitutes for the others.

## Lock the contract, not the entire search

Reuse the user's existing instructions and acceptances. Record the authoritative target, last human-accepted control revision, candidate revision, intended improvement, protected properties, budget, and next checkpoint in the [review packet](../templates/human-review.md). If there is no accepted control, say so; do not invent one. Keep the target separate from the best implementation so far.

Preserve approved camera, material identity, typography, theme, and interaction behavior unless the user asks to change them. Higher resolution, a newer branch, or a higher critic score does not confer authority. Derivatives must belong to the selected master family; never color-correct a different scene to disguise a source mismatch. Record separate source identities and acceptance per theme.

## Interrupt only for a useful decision

Continue reversible work inside the agreed scope without requesting approval for every tool call. Request one decision when:
- the target is materially ambiguous, or an intervention would change a locked property, production source, architecture, or spend boundary;
- a reported regression cannot be resolved within the approved scope, or conflicting evidence exposes a real quality/latency tradeoff requiring their preference;
- the mode reaches its review/stop threshold, or a candidate is proposed for production promotion.

A clear correction authorizes scoped diagnosis and repair without asking the user to repeat it; it does not approve the result. A reported regression blocks promotion until resolved, even when checks are green. Existing stop requests apply immediately. While a decision is pending, stop dependent mutations, expensive renders, and promotion; unrelated evidence preparation may continue only within the approved scope. Silence, a compliment, and "keep going" are not acceptance. Explicit delegation can authorize bounded execution, but must be recorded as delegation, never as a human having inspected or preferred a result.

## Make the review cheap

Prepare the packet yourself; do not make the user assemble evidence or fill a form. Lead with actual media, one sentence about the change, and one concrete question. Default to the accepted control plus one candidate; include another only when it answers a real tradeoff. Use neutral A/B labels for a preference comparison and reveal the revision mapping afterward. Do not prime the choice with model scores.

For stills, show target/control/candidate at the same camera, crop, scale, and color handling, plus one or two native-resolution crops of the reported region. Retain a full-frame comparison to expose collateral changes. Label registration/difference views; never alter the locked source. Compare scene and UI separately with identical documented masks, then inspect the unmasked shipped page. Check a second pose/view for projected-texture changes. Review all affected themes, not only the best-looking one. See the [Quackles lessons](lessons-quackles-2026-10.md).

For interaction, provide the exact-build preview and matched input sequence or video: entry, motion, release, reversal, and re-entry. Test the action path, not just startup or final state. Report frame tails, blanks/source pops, and responsiveness separately from average FPS. Synthetic touch is not physical-phone acceptance. Keep cold/warm conditions and device/browser/viewport explicit. Missing media or device access stays `NOT RUN`; a prose success report does not replace it.

Example question: "Does B fix the shell color without losing A's blue glow? Keep A, accept B for this region, or point to the remaining mismatch."

## Turn feedback into a bounded experiment

Preserve the user's exact words and message/comment reference alongside the reviewed revision, source family, theme, region or gesture, and device. Separate the observed problem from the agent's proposed cause. "Too white" is not evidence that exposure is the cause; "feels laggy" is not disproved by an endpoint test.

Convert the correction into one falsifiable hypothesis and the smallest relevant intervention. Carry protected properties unchanged into the worker brief. Reproduce the complaint first; add behavioral regressions where possible, then recapture the same comparison. A material fix must not quietly move the camera or soften lettering. Validate a suspect visual gate with known-answer must-pass/must-fail cases before changing its threshold; do not tune it until the candidate passes.

If the user prefers the old version, preserve/recover that exact control and stop promoting the candidate. Investigate the gap instead of adding features or arguing from scores. When evidence does not justify a change, record `NO_UPDATE` rather than inventing progress.

## Record the decision and preserve its scope

Use `PENDING`, `ACCEPT`, `REVISE`, `REJECT`, or `DEFER` in the packet. Agents prepare packets and transcribe explicit decisions with attribution; they do not supply the human's decision. Start `PENDING`. Record any delegated authority separately. Append dated decision notes rather than replacing earlier feedback.

Acceptance binds to the inspected revision, artifact/source hashes, scope, and evidence. A later revision requires new review or an explicit, evidenced carry-forward for unchanged scope. Accepting one crop/theme is not accepting all themes, mobile behavior, or production deployment. Human preference does not waive failed hard requirements; a changed requirement needs its own explicit decision and new evidence. Promote only when required checks and scoped authority are both satisfied.

Store packets under `.dream-loop/reviews/` (gitignored); do not publish private targets or feedback as public evidence without authorization. Link the packet from discovery-node `artifacts`; retain rejected branches. A discovery node's `outcome: accepted` is a search outcome, not proof of human approval. Do not mix packet statuses into the discovery schema. Typed human-feedback replay/promotion enforcement is future work; this change governs the skill instructions, not a runtime access-control boundary.

## Credit / provenance

Anshu Chimala (@achimala) created Dream Loop's target/implementation/judge architecture. Kevin Rajan (@kvnloo)'s Quackles feedback and the recorded investigations exposed the gaps addressed here:
- [#41 deployed-action reproduction](https://github.com/kvnloo/quackles/issues/41#issuecomment-5775174649): initialization/build checks passed while real wheel input failed; physical-device evidence was explicitly absent.
- [#43 source-family contract](https://github.com/kvnloo/quackles/issues/43): a larger image could silently replace accepted art, motivating revision-bound source authority.
- [#50 owner-experience gate](https://github.com/kvnloo/quackles/issues/50) and [control audit](https://github.com/kvnloo/quackles/issues/50#issuecomment-5915031458): test-green motion could still feel worse, motivating control comparisons and human veto.
- [Quackles lookdev lessons](lessons-quackles-2026-10.md): region-first color correctness, cross-theme checks, second-pose validation, and calibrated gates.

The added contribution is the shared review packet, checkpoint policy, and scoped feedback/acceptance protocol, not a new claim over those diagnoses or Dream Loop itself. These source reports are not new measurements or a claim that Quackles has passed acceptance.
