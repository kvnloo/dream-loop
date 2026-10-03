# Creative 3D skills that earned a seat

Upstream clones (arjun988 / kevinbadi blender-skills) live in the agent profile. **Only the rules below belong in this repo.** Do not vendor Meshy, Fal, or MCP-only CLIs for private stills.

## In (moved the judge)

| Source skill | Keep |
|--------------|------|
| polyhaven-texture-apply | Tiled albedo/normal/rough/disp on **one** mesh. `scripts/polyhaven_pbr.py` (HTTP, no MCP). 1k to gate, 2k+ after crop holds. |
| blender-materials | One Principled. Dirt/soil/concrete roughness 0.7–0.95, metallic 0. Terracotta: metallic 0, roughness 0.4–0.7, no second mesh for glaze. Hero ≤ 3–5 materials. |
| blender-lookdev | Clay/grey pass **then** beauty. Neutral 3-point or one HDRI to evaluate materials. Do not beauty-light a crop that failed overlay. |
| blender-lighting | Key 45° / fill ¼ / optional rim. Outdoor: sun + HDRI, not 12 area lights. Lighting is its own change class. |
| blender-vegetation-artist | Leaves = alpha cards from the photo, atlas, pivot at card base. Trunk opaque. Do not nibble icosphere foliage. |
| blender-rendering | Cycles, OptiX if present. Gate at 64 spp; hero 256+ only after composition holds. |

## Out (did not help this loop)

- image-to-3d **Meshy** / public Fal: private crops stay local TRELLIS/Hunyuan.
- polyhaven-scene-builder / studio-setup as a full scene replace: blows the locked camera.
- procedural-modeling rocks-as-dirt, sculpting pebbles.
- quality-refinement-autoloop as a second judge rubric — this repo’s judge wins.

## bpy node graph (soil / court / CMU)

Principled BSDF ← Image Texture (sRGB albedo)  
Normal Map ← Image Texture (Non-Color nor_gl)  
Roughness ← Image Texture (Non-Color)  
Displacement (OBJECT, scale 0.001–0.003, BOTH) ← Image Texture (Non-Color)  
UV: object size, not 1×1 on a 20 m plane.

## How to use from a product worktree

```
python /path/to/dream-loop/scripts/polyhaven_pbr.py dirt --out .dream-loop/pbr --res 1k
```

Then point the product’s bpy at those files. Do not commit the jpgs if the product gitignores `.dream-loop/`.
