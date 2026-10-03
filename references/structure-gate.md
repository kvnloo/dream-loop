# Structure gate (crop_gate on structure)

`scripts/structure_gate.py` is an opt-in alternative to `scripts/crop_gate.py` for targets with heavy fine detail: AI stills, stone, halftone, printed decals. It has the same job and the same consequence. A non-zero exit means **composition FAIL**: camera, framing, lens, layout, or a missing or misplaced mass. Skip lighting/materials judging and take a camera or massing action.

`crop_gate.py` is unchanged. The structure gate imports it and uses its `_fit` and `_edges`.

```
python scripts/structure_gate.py .dream-loop/target.png capture.png .dream-loop/overlays [--mask ignore.png]
```

`--mask` takes a white-is-ignore mask, for example a website UI overlay. The masked pixels are excluded from the statistic by normalised convolution. They are never filled and diffed.

## When to switch

Switch only after you have shown, with a known-answer suite (below), that `crop_gate` is measuring texture rather than composition on your target. The symptom is a disagree_frac stuck near 0.8 that no massing change moves.

Do not switch just because a render fails.

## Method

1. **Structure.** Convert to luminance. Apply a Gaussian low-pass at sigma 1.5 full-res px, then an area downscale to 256 px wide.
2. **Edges.** Run `crop_gate._edges` (FIND_EDGES) on both images. A strong edge is a response >40, crop_gate's own cut.
3. **Long edges.** Keep only 8-connected strong-edge runs of at least 12 px. These are silhouettes, mass outlines and horizon lines; pores, halftone dots and print specks are dropped.
4. **Hysteresis match.** An edge counts as matched if the other image has a response of at least 15 within 1 px. Exposure, contrast and sharpening change edge strength, not position.
5. **FAIL** if either term trips:
   - **global** `unmatched_frac >= 0.028`, which catches camera, lens, framing and layout;
   - **local** worst 48 px tile `tile_unmatched >= 36`, which catches one missing mass that a whole-frame ratio cannot see.
6. **Reported, not deciding:** crop_gate's `edge_mae` and `disagree_frac`, computed on the structure pair.
7. **Overlay** (`structure_gate.png`): cyan = in target, missing from capture; red = in capture only; yellow = worst tile. Always read it, including on PASS.

## Validate before you trust it: the known-answer suite

Build the cases from the locked target and from your own renders. Run **both** gates on every case. The new gate must catch every must-fail that the old gate catches, and pass every must-pass.

- **Must fail (composition):**
  - translate 10/20/40 px; rotate 1/2/3 deg; scale 0.95/1.05; crop shift;
  - wrong lens: a real re-render at focal length x0.9/x1.1, or scale + keystone;
  - mirror; upside-down; a different target;
  - a mass painted out: the main subject, the plinth, a background mass, a small object;
  - your render minus a mass you just built.
- **Must pass (not composition):**
  - identity; JPEG/WebP re-encode; blur sigma 0.5-1.5; unsharp; grain;
  - exposure +/-1 EV; white balance; desaturation;
  - fine-texture swaps (keep the low-pass, replace the detail);
  - material-only render pairs;
  - relit re-renders: intensity, colour, and sun rotated.
- **Fairness:**
  - Warp the image together with its UI, then ignore `mask OR warped mask` in both gates.
  - Edge-replicate the out-of-frame pixels so no artificial border edge is added.
- **Choosing parameters:** take them from a plateau of the sweep, not its best point. Check them held-out: fit on the target-derived cases, test on the render-derived ones, and the reverse.

**Reference result** (one AI website-mockup target, 85 cases):

| gate | must-fail caught | must-pass passed | notes |
|:--|--:|--:|:--|
| crop_gate (full frame, UI-filled) | 35/40 | 12/36 | Fails re-encodes, blur, grain, texture swaps and material-only pairs. Misses 5 background-mass paint-outs (disagree 0.001-0.013). |
| crop_gate on blur/downscale only (best of 32 configs) | – | – | No config separates. The best has lowest must-fail 0.027 vs highest must-pass 0.318. |
| structure_gate | 40/40 | 36/36 | Global: highest must-pass 0.0125 vs geometric errors at 0.068 or more. Local: highest must-pass 24 vs lowest must-fail 48. |

## Limits

- **A strong moved cast shadow is structure to any luminance-edge gate.** Two sun rotations passed (tile 24 and 8 against a threshold of 36); a harder shadow move may not. If a lighting round fails only on shadow tiles, the overlay shows it, and that is an owner call.
- **Large-scale printed art counts as structure.** Poster or decal-panel content does; fine halftone does not.
- **Small masses are near the floor.** Below roughly 50 full-res px across, the local term is close to its threshold.
- **The thresholds are tuned on one target family at 1024x1536.** Re-run the suite for a new target family or aspect ratio.
