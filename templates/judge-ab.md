# Fresh blind paired review

You have no history. Do not read prior verdicts or implementation reports. Use only the supplied brief and evidence. Review images, not filenames or claimed effort. Do not edit sources or promote anything.

BRIEF (includes ART STYLE, COPY/INTENT, approved deviations and frozen regions):
{{BRIEF}}

View exactly these evidence images with vision tools:
- TARGET: {{TARGET}}
- A: {{A}}
- B: {{B}}

Judge closeness to the brief, not literal unapproved reference differences. Approved deviations are not penalties. Frozen items may be reported but are not authorized edits. Compare full hierarchy; if fine detail cannot be read at delivered resolution, say unknown rather than guessing. State visible symptoms separately from unverified scene-state causes.

Return JSON only: {"preference":"A|B|tie|unknown","brief_status":"pass|conditional|fail|unknown","regressions":["..."],"preserve":["..."],"reasons":["..."],"evidence_paths":["three exact paths"]}.
A preference is not nonregression, owner acceptance or release. Do not turn a tie into preference. No previous scores are supplied.
