# 3D: what actually works

> **V2 compatibility record.** Read SKILL.md and references/loop-and-gates.md at the skill root first. Current owner preferences, COPY/INTENT, three separate gates and batch checkpoints override historical literal-match, model-ranking and score-only promotion advice below. Legacy Pro/Plus are opt-in, mutually exclusive orchestration recipes; external uploads/spending still require authorization. Historical rules remain for reproducibility, not as a competing v2 policy.

Shared process for any product using this skill. No product names, no scores, no stills. If a round taught something, write the **rule** here, not the round id.

Read this after `SKILL.md` / Pro workflow. Product skills (`dream-loop-cycles`, garden, house) add isolation only. They do not rewrite the judge.

## Pick the generator before you model

| Job | Use | Do not use |
|-----|-----|------------|
| Photoreal object from a **private** still (plant, pot, prop) | Local TRELLIS / Hunyuan. TRELLIS (`Structured 3D Latents`, 2024) is the paper of record. Keep crops off public APIs. | LLM bpy “growing” leaves from cubes |
| Untextured clay from Hunyuan | One retry max, then textured TRELLIS or cards | More Hunyuan rounds hoping texture appears |
| Hard-surface / pot / soil / wall / court that you **author** | LLM writes **bpy**, Cycles render | Image-to-3D of a whole building from nadir satellite |
| Ground, dirt, lawn, masonry, acrylic, bark | Tiled PBR (albedo + normal + roughness; displace on a **plane/disk**) | Icospheres, cube nibble, “perlite” |
| Aerial massing | OSM / 3D tiles as **scaffold** | Extruded boxes judged against a photoreal ortho |
| LLM writing bpy | **Astra high-effort** first. Grok-4.6 and GPT-5.6-sol are backups. | Free Nemotron (fails camera + materials) |

Same-prompt bakeoff (terracotta pot + PBR dirt, 64 spp): Astra high > Grok ≈ sol >> Nemotron. Nemotron cropped a gray cylinder. None used pebbles when the prompt forbade them.

BlenderAlchemy (ECCV 2024) is VLM **editing** a live scene. Closer to this loop than one-shot scripts. Prefer bpy file in git over clicking the viewport.

## Materials

For opt-in real-photo material grounding (camera/shape already gated), use [photo-material-grounding.md](photo-material-grounding.md): keep held-out views and lights separate from the generator, evaluate per-mesh PBR changes, and log accepted/rejected branches.

1. Download or crop a seamless set. `scripts/polyhaven_pbr.py dirt --out .dream-loop/pbr --res 1k`. 1k is enough to gate; 2k/4k after composition holds. See [creative-3d.md](creative-3d.md).
2. One Principled BSDF. Image textures: sRGB albedo, Non-Color normal/rough/disp.
3. Displacement on the soil/ground mesh, scale ~0.001–0.003 object space, method BOTH. Not a pile of spheres.
4. Pot glaze / CMU / acrylic: roughness map, not a second mesh.
5. Leaves: alpha cards from the photo beat paddle geometry. Do not nibble leaf count to chase 0.1 judge.
6. Hero plant like a game artist, not a render farm: **stem curve + leaf atlas cards cut from the locked still**, authored pot, PBR soil disk. TRELLIS the **whole crop** (plant+pot as one mesh) or do not TRELLIS. Do not glue a nursery GLB onto a cylinder and dolly until MSE drops — MSE rewards green pixels, not the still.

## Camera and composition

- Lock one crop. Overlay 50/50 then `scripts/crop_gate.py` **before** any shader pass. Non-zero exit skips lighting/materials judging; continue with a camera or massing action. Vanishing-line miss is composition, not lighting.
- If composition rose, keep that camera. If the next round drops it, revert the camera, do not “fix” with euler nibble.
- Hero camera inside the volume looking at the subject. Above-roof / inside-wall stills are composition zero — do not judge materials.
- `primitive_plane_add(size=2)` then scale by half-extents. `size=1` with the same scale halves the floor.

## Loop (this repo)

1. Lock `.dream-loop/target.png`. Do not swap subject.
2. One change class per round (camera **or** massing **or** material **or** one mesh).
3. Recapture the same camera unless this round’s change class is camera.
4. Fresh judge child every round. Rubric: composition 0–3, lighting 0–3, materials 0–3, details 0–1, /10. Nitpick.
5. Stall: best score not +1 in two rounds → stop. Meta table every 5 rounds in **that product’s** `.dream-loop/meta.md`.
6. Exit ≥ 8/10 or user stop.

## Failures that keep repeating

- Primitive dirt / court pebbles: looks “3D”, loses the judge on materials.
- Judging OSM boxes vs a satellite photo: topology only, scores < 1.
- Mixing two products’ stills or merging worktrees “to coordinate.”
- Reusing the same judge context.
- Whole-scene tiled maps on the hero still (use one-mesh ortho after shape is gated). See `references/tiled-mesh.md`.
- Chasing lighting while overlay lines disagree.
- Camera dolly / crop to cheat MSE. Keep requires **both** judge /10 and MSE, with pot+soil+backdrop still in frame. Skip `crop_gate.py` and you will judge materials on a composition fail.
- Stall ignored: if best /10 is not +1 in two rounds, stop. A new generator class is a rethink, not r10–r15 of the same plant.
- Pixel-match a plant still before the set exists. Blockout first: same camera skeleton (pot in frame, ground plane, wall masses, light direction). Invent materials. Hero foliage later.

## Hard-surface product from a photo (remote, gadget, box)

Pipeline that reached about 6–7/10 realism on the first afternoon:

1. **Prep:** RGBA cutout → crop to the alpha bbox → pad to a square with about 8% margin → 1024² → upload with `curl -F image=@in.png -F overwrite=true 127.0.0.1:8192/upload/image` (ComfyUI-next).
2. **Shape:** run the TRELLIS.2 template `3d_pixal3d_trellis2_image_to_model.json` (in the uv cache `comfyui_workflow_templates_json`), converted to API format with `going-home/remake/char/ui2api.py TEMPLATE out.json 316.value=true 122.image=in.png 15.clip_name=dino_v3_vit_l.safetensors 322.filename_prefix=3d/NAME`. POST it to `/prompt`. Each job takes about 3–4 min. Fetch the GLB with `/view?filename=…&subfolder=3d&type=output`, not by guessing the output dir. Raw TRELLIS gets the silhouette and depth right, but the keys come out melted and the legends unreadable (about 4/10).
3. **Photo skin:** take the faces whose world normal has y < -0.35 (facing the camera) and planar-project the high-res cutout onto them, using percentile bounds (0.05%/99.95%) because TRELLIS leaves floaters. Then:
   - Flatten that front relief in depth only: Laplacian smooth with only Y enabled (`use_x = use_z = False`), on a vertex group that excludes the rim. Why: the mesh bumps sit offset from the printed keys and read as doubled buttons; locking X/Z keeps the UVs registered.
   - Front shader = 85% Emission(photo) + 15% Principled. Why: the photo already carries the real relief and gloss; relighting it turns black plastic grey and adds a second set of key shadows.
   - Put sides and back on a plain satin material (dark base, roughness about 0.38) in place of TRELLIS's hallucinated streaky texture.
   - Save a `.blend` as well as the GLB. A GLB export drops the emission mix.
4. **Judge:** Cycles renders, one orthographic front at the photo's aspect and one 85 mm 3/4 view that fills the frame. Compare photo | front | 3/4. Re-check any "doubled" verdict on a full-resolution crop: downscaled sheets produce false ghosting reports. Render with the Standard view transform, not AgX: AgX washes display-referred photo textures grey.
5. Put large .glb/.blend files in gitignore and copy them under `project-artifacts/` so the offsite blob backup covers them. Commit only the scripts and renders.

Next levers if more realism is needed: smooth the side lumps, skin the back from a back photo, add a contact shadow.

## A new building inside photogrammetry tiles (Google 3D tiles, Cesium)

Generator ladder, measured with fresh "does it look real" readers at a close and a journey camera:

1. Code-extruded massing plus a procedural facade tops out fast: readers call it a CG placeholder. Stop it under the no-gain rule, don't polish it further.
2. **Headless Blender built from the plan's numbers** (footprint polygon, storeys, storey height, style → GLB with brick/wood PBR, inset windows, shopfront, parapet, rooftop units). It can't drift from the plan (3 storeys stays 3), and it reads as real at a close camera. Run it on a compute box; it takes about 40 s and 2 MB / 12k triangles per building.
3. Image→3D (TRELLIS/Hunyuan) of a generated concept: it smears textures, bakes trees into the walls, ignores the footprint and storey count, and needs stretching. Don't use it for planned buildings.

Seating checklist (each item is one dream round): the shadow map is on AND the tileset receives shadows (otherwise the shadow is invisible on the tiles); a cut that removes the old building's mesh, kept to the footprint plus about 1 m, with the void behind it filled; cut walls in street or neighbour colour; a contact line at the wall's foot; the selection outline only in edit mode; tone and sharpness graded toward the tiles.

Rules:
- Before any look round at a camera, calibrate the realism reader there: ask the same question about an existing tile building of similar size in the same capture, with the analysis panel shown and hidden. Why: readers scored the proposal 0/5 through three lanes and about 20 rounds whatever changed. If the real neighbours also read 0–1/5, that camera's question measures nothing, so change the question ("does it belong as much as its neighbours") or the camera and re-baseline.
- A HUD that states the analysis sun ("29°, 17 m") makes readers judge the shadow against the sun baked into the tiles. Test the cheapest causal hypothesis as one round: measure the tiles' sun from the neighbours' shadow vectors and light the subject with it in a view-only look, keeping the study numbers unchanged. Either result is informative.
- A lone high read (4/5 once) has to repeat twice before you build on it; the same building can read 0/5 on the next pass.
- An image-edit target can draw the subject at the wrong scale (e.g. 1.6× the planned height). Check the target against the plan's countables before copying window sizes or proportions from it.
- When the realism metric is the goal, make it the lead judge on every kept round, not every Nth round.

## How to add a lesson

One imperative rule + why. No round numbers. Patch this file on the current feature branch (or main once merged). Profile skills may **point** here; they must not fork a second rubric.

Lessons file (camera-projected textures, sharpness, stone): [lessons-quackles-2026-10.md](lessons-quackles-2026-10.md).
