# Max-zoom fidelity, style layers and real texture painting

## Fidelity at the deepest delivered zoom

Treat final pixel density as a contract, not an export setting. For every visible
component and material layer, require at least **one effective source texel per
final pixel in both mapped directions** at the deepest supported zoom; choose
headroom for filtering, obliquity and compression. A large atlas is not sufficient
if the occupied UV island or projected source is tiny. Never count interpolated
upscale pixels as independent source detail. Define screen/DPR/zoom bounds or final
print density explicitly; do not promise unlimited zoom with finite assets.

Audit actual visible receivers with camera rays, evaluated triangle UVs and their
screen-space derivatives. Scale UV derivatives by each source's native dimensions;
report the minimum singular value of the local screen-pixel→source-texel Jacobian,
coverage, percentiles and worst regions. This conservative two-direction criterion
catches anisotropy that an area ratio hides. Include the *effective* image node,
Mapping transforms, UV channel, UDIM tile, procedural-to-raster bakes, LOD/mips,
packed/compressed size and texture repeats. UV seams, discontinuities, ray misses,
procedural coordinates and ambiguous source branches require explicit categories,
not fabricated density values. Web/UI equivalents audit CSS/device-pixel scale,
image intrinsic density, vector/rasterization pipeline and GPU texture limits.

Track **two independent capacities**: output texture texels per final pixel, and original/generated observation pixels per projected final pixel. A huge UV bake can pass the former while failing the latter. A declared viewer tile manifest proves requested dimensions, not tile existence or source fidelity; check delivered tiles and their lineage. A crop qualified at one master density does not qualify a larger master.

Flag camera-projected sources bounded by the reference's own resolution. A 4K
reference projected onto an 8K render does not become 8K artwork because the bake
is large. Prefer resolution-independent geometry, bounded-frequency procedural
functions in object/UV space and genuine vectorized artwork. Rasterize vectors at
the final density; trace approved shapes rather than inventing recovered detail.
Procedural noise still needs sampling/anti-aliasing and visual approval. Generated
or authored new detail must be named as new and preserve approved low frequencies.

## Target pyramid and round gate

Build a versioned pyramid from one approved high-resolution master plus registered
zoom tiles. Record parent box, scale, overlap, target/capture hashes, native sizes,
authored versus observed detail and approval state. Each child downsample must agree
with its parent in protected structure/color; independently regenerated zoom tiles
are not automatically a coherent target. Use shared conditioning, overlap checks
and an owner approval step when the source lacks deep detail. Missing zoom truth
is an unresolved target contract, not permission to invent an acceptance PASS.

Each round affecting the deliverable runs a **max-zoom crop gate**: fixed semantic
border crops at full final render density, identical camera/settings, valid-region
masks and adequate overscan/context for DOF/glare/denoising. Never render a small
crop at reduced full-image resolution and upscale it. Include prior worst areas and
representative geometry/artwork/material/interface crops; explain unchanged cached
crops with exact input hashes. Evaluate source-density coverage plus calibrated
sharpness/aliasing metrics and a native-crop judge against the matching target tile.
Noise and oversharpening can inflate sharpness; no scalar proves native appearance.
Owner-approved optical blur is intentional, not a blanket failure or a waiver for
undersampled textures. Keep full-frame composition and actual final viewer delivery
as separate gates. Use [max-zoom contract](../templates/max-zoom.md).

## Separate style grammar from physical materials

Decompose the reference into geometry/faceting, reflectance/albedo/light, and style
layers: film grain, halftone/print screen, ink outlines, cel bands and low-poly
faceting. Record each layer's coordinate domain, scale/frequency, color/ramp,
mask/coverage, blend/order, continuity, density behavior and ownership. Low-poly
faceting may be geometry/normal design rather than a compositor filter; cel bands
may come from lighting/shading. Diagnose the visible cue before choosing its stage.

A wet coat does not create print dots; micro-roughness is not film grain. Test each
style layer on/off with one shared fixture before integrating. Decide whether grain
tracks world units, surface UVs, print units or screen pixels. Prevent halftone moiré,
outline crawling and band instability at all supported zooms and motion states.
A procedural in-engine style layer is not automatically permission for a forbidden
AI image edit. Use [style-layer analysis](../templates/style-layers.md) and keep
current owner restrictions explicit in every judge packet.

## AI artwork belongs on the actual mesh, not over the render

The owner's added rule permits AI images to be **projection-painted and baked into
real mesh textures**; it does not permit a 2D paint-over of the finished render.
Apply the no-final-render-paint-over boundary in this method; a proposed owner revision requires an explicit method/scope change, not a silent exception. Record this distinction in project scope, never silently broaden old permissions
or upload private imagery. Preserve generator/source/license and prompt lineage.

Paint through camera projection if useful, then bake into explicit material/UV/UDIM
textures with padding, seam/occlusion handling and the max-zoom source audit. Prove
the saved scene's visible mesh consumes those textures after reopening, and that a
fresh render produces the result without a screen-space image replacement. Inspect
off-axis/relighting controls when the deliverable requires them. A genuine bake can
still contain view-dependent or baked-light artifacts; it is not measured PBR or
multi-view truth. Never infer roughness/height/normal merely from painted luminance.
Retain old sources, bake settings, effective consumer identity and native controls.

For multiple paint observations, separate generate/refine/preserve masks, reject
backfaces and hidden receivers with depth/world-position consistency, and weight
facing/feather/source density rather than averaging conflicting images blindly.
Keep raw overlap disagreement. Small UV holes may be repaired within scope; large
unseen regions remain unknown or explicitly procedural. UV-island adjacency is
not image-grid adjacency. Hold out an oblique view to expose seams and view-locked
artifacts; preserve normal/roughness unless a separate mechanism justifies changing
them. GPU generation and rendering use sequential admitted phases; chunk CPU bakes
and texture tiles rather than assuming one advertised VRAM figure certifies the
whole pipeline. Remote generation is not local inference.
