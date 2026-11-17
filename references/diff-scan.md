# Breadth-first image diff scan

```sh
python scripts/diff_scan.py target.png current.png output/ \
  --ui-mask ui-exclude.png --semantic regions.json
```

Requires Pillow and NumPy only. White mask pixels exclude UI identically in both images. Equal aspect is mandatory; comparison resolution is bounded by the smaller source and `--max-width` (1024 default). This is registered hero-frame diagnosis, not image registration or semantic recognition.

Optional semantic regions: JSON list of `{name, bbox:[x0,y0,x1,y1], owner, cost, observation}` in normalized top-left coordinates. Observations are visibly labelled caller input. Cost defaults to 1 and must be positive. Grid defaults to 4×6.

Outputs `DIFF.md`, machine-readable `diff.json` with input hashes, per-image greenery/luminance/local Laplacian energy/contrast/point-light/presence maps, five difference overlays and numbered ranked regions. Rank is visible valid area × measured severity / cost. Green overlay red means greenery missing from current; blue means current-only. Sharpness/luminance red means current excess. Bright-light components include glints and lettering, so counts are not physical emitters.

Use this to prioritize whole-frame review. HSV/ExG can miss blue-lit moss. Local sharpness is texture-sensitive and cannot prove optical focus; inspect depth and native crops. Grid and semantic regions overlap: do not count their flags as independent defects, or treat reducing a count as owner acceptance. Preserve locked intentional deviations.

Tests: `python scripts/diff_scan.test.py`; included automatically by `python scripts/run_tests.py`. Fixtures verify directional greenery, blur nomination, masking, output generation, ranking, aspect rejection and nonnegative sharpness despite integral-sum cancellation.
