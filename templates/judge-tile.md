# Fresh read-only tile critic

Tile ID {{ID}}; box {{BOX}}; brief revision {{REVISION}}.
{{BRIEF}}
Canonical scoped OWNER-PREFERENCES (verbatim resolved entries):
{{OWNER_PREFERENCES}}
Scope: {{SCOPE}}. Global gate mode and evidence: {{GATE}}.
Do not render, edit sources, follow concurrent CURRENT changes or read other verdicts.

This default packet has a three-image BRIEF budget, not a platform limit. Adjust
the packet to the agreed budget without sacrificing native detail. View once each:
1. {{TARGET_DETAIL}} — target crop, source and delivered dimensions {{TARGET_SIZE}}.
2. {{CAPTURE_DETAIL}} — candidate crop, source and delivered dimensions {{CAPTURE_SIZE}}.
3. {{CONTEXT}} — full frames with a yellow crop box (tile splitter default). If a separate
   structure overlay is supplied, cyan = target missing, red = capture-only.
   Crop boundaries are not missing geometry.

Respect COPY/INTENT, ART STYLE, approved deviations (do not penalize) and frozen items (record-only). Local alignment is pass / limited / blocked. Blocked means only composition numeric; lighting/materials/details/total null. Otherwise composition 0–3, lighting 0–3, materials 0–3, details 0–1 and exact sum /10. Score visible appearance; hidden detail is unknown, and guessed object/shader/EV values are hypotheses.

Write one JSON verdict with exactly: id, box, brief_revision, alignment, scores, gaps, preserve, tiers.
scores keys: composition, lighting, materials, details, total.
gaps: list of {element, defect, change_class, action, evidence, protected}; use one class per gap, concrete defect, exact visual evidence, boolean protected.
tiers: list of {element, tier, reason}; tier = PERFECT / MOSTLY_GOOD / NEEDS_WORK / UNKNOWN. These are RAW votes, not owner adjudication.
preserve: list of strings. No extra keys, no markdown, no invented measurements. Use {{OUTPUT}} only.
