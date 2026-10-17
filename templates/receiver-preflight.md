# Receiver and fixture preflight

Defect/ROI: <id/box>; fixture + code hashes: <hashes>; preferences revision: <id>
Question: <what uncertainty does each probe resolve?>

- Actual visible receiver: <ray hits/evaluated object + face + normal in 3D;
  hit-test DOM element/computed style/canvas draw owner in UI>
- Effective material/style: <object-linked and data slots, reachable shader branch,
  UV/coordinate source; CSS cascade/theme/token/shadow-root in UI>
- Visibility and contributors: <occluders, inherited geometry/lights, modifiers,
  disabled layers, alpha/clipping; layout/overlay/network/font readiness in UI>
- Light-link receivers: <collections/membership after replacement; N/A with reason>
- Fixture: <camera, world/key/reflection sources, scale, exposure, view transform,
  look, compositor/glare owner; browser tone mapping/color profile/DPR>
- Protected-state baseline and no-change replay: <actual checks + outputs>
- Falsifier/intermediate preview: <mask/normal/height/ID/pass/native capture>
- Result: <PASS/BLOCKED/UNKNOWN + exact observations, command/exits and evidence>

Preflight BEFORE candidate rendering. Node existence is not proof the visible
surface uses it. Candidate probes cannot reveal nonexistent hidden target geometry.
Do not create a full source dump when a bounded ray/material probe answers it.
