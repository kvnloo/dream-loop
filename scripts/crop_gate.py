#!/usr/bin/env python3
"""Heuristic crop / edge gate. Exit 0 when edge residuals are below thresholds.

Do not judge lighting or materials if this script exits non-zero.
Continue with a camera or massing action; this is not a loop freeze.
A pass is not proof of matching vanishing lines; inspect the overlay too.
Usage: crop_gate.py target.png capture.png [out_dir]
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps, ImageChops, ImageDraw, ImageStat


# Mean abs edge residual above this (0-255) is a composition fail.
EDGE_FAIL = 28.0
# Fraction of bright edge pixels that disagree.
DISAGREE_FAIL = 0.18


def _fit(im: Image.Image, size: tuple[int, int]) -> Image.Image:
    return im.convert("RGB").resize(size, Image.Resampling.LANCZOS)


def _edges(im: Image.Image) -> Image.Image:
    g = ImageOps.grayscale(im)
    return g.filter(ImageFilter.FIND_EDGES)


def gate(target: Path, hero: Path, out_dir: Path | None = None) -> dict:
    t = Image.open(target).convert("RGB")
    h = _fit(Image.open(hero), t.size)
    te = _edges(t)
    he = _edges(h)
    diff = ImageChops.difference(te, he)
    mean = float(ImageStat.Stat(diff).mean[0])
    # Binary disagreement on strong edges
    def _bin(p: int) -> int:
        return 255 if p > 40 else 0

    tb = te.point(_bin)
    hb = he.point(_bin)
    tb, hb = tb.convert("1"), hb.convert("1")
    xor = ImageChops.logical_xor(tb, hb)
    union = ImageChops.logical_or(tb, hb)
    # Normalize by strong edges, not background pixels, which hide sparse misses.
    disagree = ImageStat.Stat(xor.convert("L")).sum[0]
    strong = ImageStat.Stat(union.convert("L")).sum[0]
    frac = float(disagree / strong) if strong else 0.0
    ok = mean < EDGE_FAIL and frac < DISAGREE_FAIL
    result = {
        "ok": ok,
        "edge_mae": round(mean, 3),
        "disagree_frac": round(frac, 4),
        "edge_fail_at": EDGE_FAIL,
        "disagree_fail_at": DISAGREE_FAIL,
    }
    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        vis = ImageOps.colorize(diff, black="black", white="red")
        draw = ImageDraw.Draw(vis)
        status = "PASS" if ok else "FAIL — composition; do not judge lighting"
        draw.text((12, 12), f"crop_gate {status} mae={mean:.1f} xor={frac:.3f}", fill=(255, 255, 255))
        vis.save(out_dir / "crop_gate.png")
        result["preview"] = str(out_dir / "crop_gate.png")
    return result


def main() -> None:
    if len(sys.argv) < 3:
        sys.exit("usage: crop_gate.py target.png capture.png [out_dir]")
    target = Path(sys.argv[1])
    hero = Path(sys.argv[2])
    out = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(".dream-loop/overlays")
    r = gate(target, hero, out)
    print(r)
    if not r["ok"]:
        print("COMPOSITION FAIL: skip lighting/materials judging. Continue with a camera or massing action.", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
