# Lessons: camera-projected character textures and stone

Rules distilled from a character-plus-set lookdev run. Same format as [3d-what-works.md](3d-what-works.md): one imperative rule + why. No round numbers, no product scores.

## Targets

- **Inventory every reference and compare them against each other before assuming shared materials.** The same character can carry different print colours or emission per scene; one shared material silently fails every scene but the one you built it from.
- **Verify secrets and tool access before planning around them.** A vault key can exist and still lack the scopes the plan needs; find out in one call, not after the pipeline is designed.

## Texture correctness

- **Fix colour and texture correctness per region before sharpness or clarity.** A crisp wrong colour is still wrong, and sharpening work gets redone once the colour moves. Never dismiss a visible colour mismatch as "tone".
- **When projecting a 2D target onto a mesh through camera-space UVs, never stretch per part (anisotropic Mapping) to make it fit.** Per-axis scale shears and rotates the print. Use identity mapping plus a rigid or similarity registration per element, fitted in **pixel** space: in 0..1 UV on a non-square image a rotation turns into shear. A pose mismatch belongs to the pose, not the texture.
- **Gate camera-projected textures with a visibility bake and check a second pose every round.** Projection only holds at the projection pose; hidden and grazing faces smear the print and you only see it once the camera moves.

## Sharpness

- **For crisp low-resolution stills use Blackman-Harris filter width 1.0 plus 2x supersample and downsample.** That is where the crispness comes from; the denoiser choice barely matters.
- **Match an AI-generated target's measured sharpness and grain, not its artefacts.** Generated targets carry sharpening halos, per-pixel grain and invented detail; copying them makes the render look processed, measuring them gives the real target.
- **Light for edges: a lit side and a shadow side (rim or kicker plus a raking key).** Perceived sharpness is mostly lighting; flat front light kills texture no matter how sharp the maps are.

## Stone and concrete

- **Use scanned or generated tiled PBR with sparse recessed voids on a honed base, lit by a raking key.** Dense procedural bump blobs read as stucco or cottage cheese; real stone reads through a few dark recesses that a low light catches.

## Tool chain for a texture from a target

- **Chain tools instead of asking one model for a finished material:** segment the target (SAM2) -> rectify the surface to a flat swatch -> image model (gpt-image class) for a delit, tileable albedo + height -> derive normal and roughness -> apply with real-world-scale UVs. Each step fixes one thing (mask, perspective, lighting, tiling, scale) that the next step cannot.

## Scoring

- **Gate and judge the 3D scene against the target with any 2D UI/overlay masked out identically on both images; score the UI separately against the shipped page.** A website mockup target bakes logo, nav, headline and text panels into the still; the render never contains them, so they add edge residual and judge penalties no scene change can remove, and they hide whether the camera and massing actually moved. Masking only the target (or masking differently) creates fake edges, so fill the same mask with the same neutral colour in temp copies of both, run the gate scripts unchanged, and keep the locked target file untouched.
