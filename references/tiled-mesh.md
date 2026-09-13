# Optional stage: tiled mesh maps (Star Wars / Jedi method)

Not a scene stage. Do not run this on a full hero still or to invent a new target.

Use when a **single mesh** needs fabric, hair, skin pores, chainmail, court grain, CMU mortar, or other microtexture that a 1k atlas cannot hold. Proven on Temple Guard: split source into an N×N grid with overlap, restore each tile at higher res (ComfyUI ControlNet-tile / Flux denoise ~0.18), stitch, bake onto the mesh.

## Gate

Run only if **all** are true:

1. Camera/crop already matches (gated shape tier passed).
2. The object exists as geometry (not a missing aisle or wrong FOV).
3. The judge named **material microdetail** on that object, not layout.
4. You have a locked albedo/ortho of **that object only**, not the whole gym.

Otherwise skip. Tiled img2img on a scene still makes a prettier fake the 3D cannot reproduce.

## Grid

Default `N=4` (16 tiles). Overlap 32px. Replicate edges instead of black pad.

```
python scripts/tile_grid.py split --input OBJECT.png --out .dream-loop/tiles --n 4 --overlap 32
```

Each tile is an independent restore. Do not redesign geometry in the prompt. Recover fibers / pores / weave only.

```
python scripts/tile_grid.py stitch --tiles .dream-loop/tiles --out .dream-loop/object-4k.png --n 4 --overlap 32
```

## Comfy (optional)

If ComfyUI is up (`http://127.0.0.1:8188`): per-tile Flux/SDXL tile ControlNet, low denoise, same seed family. Reference implementation: `zer0/experiments/jedi_temple_guard/scripts/comfyui_fullbody_tiled_restore.py`.

If Comfy is down, still split/stitch with `tile_grid.py` and restore tiles via the image tool you already have. Same lock: no new objects, no crop change.

## After stitch

Bake the 4k (or 16k) map onto the mesh (albedo + optional normal from high-frequency). Recapture the **same locked camera**. Fresh judge. The scene camera does not move because a fabric map changed.

## Do not

- Tile the Rally House hero vs target to “gain resolution.”
- Replace `target.png` with a tiled generation.
- Run this before shape (camera, aisle, window grid) is done.
