# Critics: rankers, not rulers

## Routine blind A/B

Use fresh, no-history sessions for both orders: target + anonymous A/B; swap A/B in the second session and keep decoding private until both finish. Preserve source and anonymized-image hashes. Give no round numbers, previous scores, persuasive implementation story or identity hints. Require actual image loads, not a prose claim of seeing them. Recalibrate against the same anchor when model, rubric or evidence resolution changes.

Each prompt includes target/brief revision, ART STYLE, COPY/INTENT rows, approved deviations (“approved; do not penalize”), frozen items (“record-only; no edit authorization”), exact evidence paths and review scope. Preserve raw verdicts and adjudicate separately. A net preference plus a protected regression is not a strict nonregression PASS. A tie remains a tie; disagreement triggers investigation or owner review, not repeated score-shopping.

Use a fixed category rubric: composition 0–3, lighting 0–3, materials/visual surface 0–3, details 0–1. For UI use surface/typography counterparts explicitly fixed in the brief. Never score an absent modality by pretending it exists. If hard structure/local correspondence is blocked, score only composition; leave lighting/materials/details/total null. Absolute scores from different framings are not a trajectory or objective distance.

## Native evidence and image budgets

Inspect full frame for hierarchy, native crops for fine detail, and final-output-density crops for deep zoom. A large sheet of native pixels may be downscaled by the vision loader. Prefer separate bounded target and candidate crops plus one compact context/overlay image: three images per tiled call. Verify actual delivered dimensions and successful tool results. A three-loads-per-path limit is not proof of a universal three-image limit; the three-image protocol is a conservative budget, not a claim about every model.

Do not enlarge a small capture and call it native. Label alignment resizing and border-render valid areas. Border compositing can change glow/DOF; use full-frame-derived evidence for final optics/halo approval. The panel must see the entire disputed element before asserting absence; a crown crop cannot prove a portrait lacks printed detail elsewhere.

## Full tiled milestone review (read-only)

1. Snapshot CURRENT selection, target, mask and hashes. Do not follow concurrent promotions. No scene edits, new rendering or GPU work.
2. Verify aspect and uniform alignment. Run overlay, crop and masked structure diagnostics with commands/exits. Retain physical markings. A mask detector must not erase subject pixels where web text touches silhouettes.
3. Split semantic regions plus a complete padded grid with [tile_splitter](scripts.md). Default example is 4×6, not a required portrait aspect. Record core/padded boxes, core and padded ignore fractions, source/delivered dimensions and hashes. Prove grid cores cover every pixel exactly once before skips; skip only >90% ignored core and list it. Coverage of unmasked pixels is not native-detail coverage when sources are smaller.
4. Launch one fresh critic per active tile in bounded foreground batches (at most four, or owner limit). Supply three bounded images and [tile prompt](../templates/judge-tile.md). Include overlay legend: cyan = target structure missing from capture, red = capture-only. No evidence from other reviewers.
5. Validate exact IDs/boxes/revisions/keys, finite scores/ranges/sums, blocked nulls, one proposed change, evidence paths, unique native sessions and requested model. Retry invalid/incomplete results once if authorized, retaining both attempts. Never invent missing verdicts.
6. Aggregate in code, with every active/skipped/missing ID accounted for. Deduplicate by element + concrete physical discrepancy, not a global keyword such as “stone.” Keep verbatim tile citations; count one strongest contribution per tile/defect. Separate blocked composition priority from scored totals; never manufacture a total.
7. Publish all tile scores, worst ten scored tiles, blocked list, worst-eight contact sheet, preserve list, ranked fixes and conflicts. Means/severity are overlapping diagnostics, not independent samples, confidence or a global scene score. Severity may be unique citing tiles × mean deficit, but recurrence is not perceptual importance.
8. Adjudicate raw prescriptions against locks, actual scene probes, previous failures and owner's style reading. Keep raw tier votes separate from owner-adjudicated tiers. Retain contradictions: missing fine weathering is not excessive coarse splatter; optical defocus is not material smoothing; lighting/albedo guesses are not measured scene facts. End with source hashes unchanged and a viewer checkpoint.

## Panel and multi-scale review

At milestones use fresh senior-art-director, lookdev-supervisor and phone-viewer framings. Each sees whole-frame evidence and bounded native details, classifies elements as PERFECT / MOSTLY GOOD / NEEDS WORK, states first-glance tells and ranks impact per effort. Same model three times is not three independent experts. Mark owner-approved locks as KEEP/LOCK in adjudicated output while retaining honest raw votes. Use a trajectory sheet of matched crops to expose persistent defects, not a graph of incomparable numeric scores.

Judge the scene, UI/layout/type, interaction/motion, and delivery/performance as separate layers. Use a real device for feel-sensitive acceptance; emulated/software-rendered screenshots cannot prove phone smoothness. Report disagreements and unknown evidence explicitly.
