#!/usr/bin/env python3
"""50/50, checker, and side-by-side overlay of target vs capture."""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw


def _fit(im: Image.Image, size: tuple[int, int]) -> Image.Image:
    return im.convert("RGB").resize(size, Image.Resampling.LANCZOS)


def overlay(target: Path, hero: Path, out_dir: Path) -> list[Path]:
    t = Image.open(target).convert("RGB")
    h = _fit(Image.open(hero), t.size)
    w, ht = t.size
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []

    p = out_dir / "overlay_50.png"
    Image.blend(t, h, 0.5).save(p)
    paths.append(p)

    chk = t.copy()
    cell = max(32, w // 16)
    for y in range(0, ht, cell):
        for x in range(0, w, cell):
            if ((x // cell) + (y // cell)) % 2:
                box = (x, y, min(x + cell, w), min(y + cell, ht))
                chk.paste(h.crop(box), box)
    p = out_dir / "overlay_checker.png"
    chk.save(p)
    paths.append(p)

    side = Image.new("RGB", (w * 2, ht))
    side.paste(t, (0, 0))
    side.paste(h, (w, 0))
    draw = ImageDraw.Draw(side)
    draw.text((12, 12), "TARGET", fill=(255, 80, 80))
    draw.text((w + 12, 12), "HERO", fill=(80, 200, 255))
    p = out_dir / "overlay_side.png"
    side.save(p)
    paths.append(p)
    return paths


def main() -> None:
    if len(sys.argv) < 3:
        sys.exit("usage: overlay.py target.png capture.png [out_dir]")
    target = Path(sys.argv[1])
    hero = Path(sys.argv[2])
    out = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(".dream-loop/overlays")
    for p in overlay(target, hero, out):
        print(p)


if __name__ == "__main__":
    main()
