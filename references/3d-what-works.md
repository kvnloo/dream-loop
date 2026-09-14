# 3D: what actually works

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

1. Download or crop a seamless set. PolyHaven 1k is enough to gate; 2k/4k after composition holds.
2. One Principled BSDF. Image textures: sRGB albedo, Non-Color normal/rough/disp.
3. Displacement on the soil/ground mesh, scale ~0.001–0.003 object space, method BOTH. Not a pile of spheres.
4. Pot glaze / CMU / acrylic: roughness map, not a second mesh.
5. Leaves: alpha cards from the photo beat paddle geometry. Do not nibble leaf count to chase 0.1 judge.

## Camera and composition

- Lock one crop. Overlay 50/50 target vs capture **before** any shader pass. Vanishing-line miss is composition, not lighting.
- If composition rose, keep that camera. If the next round drops it, revert the camera, do not “fix” with euler nibble.
- Hero camera inside the volume looking at the subject. Above-roof / inside-wall stills are composition zero — do not judge materials.
- `primitive_plane_add(size=2)` then scale by half-extents. `size=1` with the same scale halves the floor.

## Loop (this repo)

1. Lock `.dream-loop/target.png`. Do not swap subject.
2. One change class per round (camera **or** massing **or** material **or** one mesh).
3. Recapture the same camera.
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

## How to add a lesson

One imperative rule + why. No round numbers. Patch this file on `feat/lanes-coordination` (or main once merged). Profile skills may **point** here; they must not fork a second rubric.
