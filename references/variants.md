# Siblings, themes and complete review history

## Port quality without flattening style

- Inventory references against each other first: shared geometry does not imply shared print, emission, palette, DOF or lighting. Search historical theme-specific work before assuming a sibling has only the base/shipped version.
- Diff geometry/topology/UV hashes, transforms, material bindings and every visible element before porting. Equal object names/matrices can hide older simple meshes or missing replacements. Reconcile prerequisites explicitly.
- Implement carry-over fixes as ONE shared apply layer plus per-variant config. Keep geometry, registration, label placement, defect repairs and quality source reusable; keep palette, view transform/exposure, per-theme optical response and owner exceptions in configs. Reapply exceptions after the shared layer.
- Hold geometry-dependent ports until source geometry is approved. Prefer transplanting frozen exact mesh/UV data over replaying a topology-sensitive builder when identity is required. Verify the consuming shader/renderer actually reads the transferred data.
- Port MATERIAL QUALITY as well as geometry: retain map source/detail/scale/normal/roughness structure and adapt albedo tone separately. A soft target may need scoped detail/bump contrast adaptation; judge it rather than forcing every sibling to look like the lead.
- Split lighting into reusable direction/color/source recipe, optional named local fills/gobo, and per-theme view/look/exposure. Do not transplant a global tone mapper merely because the lead improved. Check light occluders and receiver/include/exclude memberships, then rendered region colors.
- Capture a no-layer control with the same environment. Baseline renderer drift must not be credited to a shared layer. Check every theme, not just the source.
- On owner approval of a shared change, synchronize siblings promptly in parallel CPU prep with the shared GPU lock. Send exact new asset paths/parameters to already-running workers. Each sync gets a fresh output directory, reference | prior | synced plus isolation and gate receipts.

## CURRENT is selection, not inference

Use [CURRENT.json](../templates/CURRENT.json) as a single variant→artifact/capture/round/status/approval selector. Snapshot before read-only review; change only the owned entry under a serialized read-modify-write with a stale-hash check, then read back. Do not replace another lane's entries or select by mtime/highest round. A working preview requested for display must say so; keep the owner-approved fixture separately. Failed or incomplete candidates never silently replace the accepted selection.

Merge separate valid fixes into one selected artifact per variant before the next polish stage, then verify each source region survived. A selector pointing to a relight-only branch cannot claim the separate eye/interaction fix is included.

## Persistent gallery and history since v0

Generate one persistent review page: references, explicitly selected current images, status/approval and reports, candidate/alternate rows, then full history. Refresh on each arrival and verify the actual page/image in the owner's viewer. Use compact cached thumbnails linked to full resolution; source hash belongs in thumbnail/cache keys.

Discover EVERY full-frame artifact since v0, not only the latest run: shipped plates from Git blobs (extract without checkout), calibration, early experiments, overnight runs, ports, component full frames and integration. Declare bounded source roots and exclusions; avoid claiming exhaustive coverage when a root/history is missing. Maintain a skip list for current eligibility, not history deletion.

Write re-runnable `history.json`: variant, ordinal v0 oldest, source date (and meaning), phase, status with source, paths/hashes, report, lineage and all occurrences. Deduplicate byte-identical images without dropping provenance; near-duplicates need declared thresholds and preserve each occurrence/status. Never infer approval from image quality or directory naming. Keep rejected rounds and parked features clickable so owner choices can recover them.

Validate counts per variant, broken/full-size links, ordering controls, current selector hash, thumbnail identity and actual image loads. Historical shipped paths prove distribution artifacts, not a currently verified deployment.
