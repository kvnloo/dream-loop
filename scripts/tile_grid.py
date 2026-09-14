#!/usr/bin/env python3
"""Split/stitch an N×N overlapping grid for mesh-map restore (not scene stills)."""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

Image.MAX_IMAGE_PIXELS = None


def _pad(source: Image.Image, overlap: int) -> Image.Image:
    w, h = source.size
    pad = Image.new("RGB", (w + 2 * overlap, h + 2 * overlap), source.getpixel((0, 0)))
    pad.paste(source, (overlap, overlap))
    if overlap <= 0:
        return pad
    pad.paste(source.crop((0, 0, w, 1)).resize((w, overlap)), (overlap, 0))
    pad.paste(source.crop((0, h - 1, w, h)).resize((w, overlap)), (overlap, overlap + h))
    pad.paste(source.crop((0, 0, 1, h)).resize((overlap, h)), (0, overlap))
    pad.paste(source.crop((w - 1, 0, w, h)).resize((overlap, h)), (overlap + w, overlap))
    return pad


def split(input_path: Path, out_dir: Path, n: int, overlap: int) -> None:
    source = Image.open(input_path).convert("RGB")
    out_dir.mkdir(parents=True, exist_ok=True)
    core_w, core_h = source.width // n, source.height // n
    pad = _pad(source, overlap)
    expanded_w, expanded_h = core_w + 2 * overlap, core_h + 2 * overlap
    for row in range(n):
        for col in range(n):
            idx = row * n + col
            crop = pad.crop(
                (
                    col * core_w,
                    row * core_h,
                    col * core_w + expanded_w,
                    row * core_h + expanded_h,
                )
            )
            crop.save(out_dir / f"input-{idx:02d}.png")
    meta = out_dir / "grid.txt"
    meta.write_text(f"n={n}\noverlap={overlap}\nwidth={source.width}\nheight={source.height}\n")
    print(f"wrote {n*n} tiles to {out_dir}")


def stitch(tiles_dir: Path, out_path: Path, n: int, overlap: int) -> None:
    cores = []
    sample = None
    for row in range(n):
        row_imgs = []
        for col in range(n):
            idx = row * n + col
            path = tiles_dir / f"tile-{idx:02d}.png"
            if not path.exists():
                path = tiles_dir / f"input-{idx:02d}.png"
            im = Image.open(path).convert("RGB")
            sample = im
            if overlap > 0 and im.width > 2 * overlap and im.height > 2 * overlap:
                im = im.crop((overlap, overlap, im.width - overlap, im.height - overlap))
            row_imgs.append(im)
        cores.append(row_imgs)
    assert sample is not None
    tw, th = cores[0][0].size
    canvas = Image.new("RGB", (tw * n, th * n))
    for row, row_imgs in enumerate(cores):
        for col, im in enumerate(row_imgs):
            canvas.paste(im, (col * tw, row * th))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path)
    print(f"stitched {out_path} {canvas.size}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("split")
    sp.add_argument("--input", type=Path, required=True)
    sp.add_argument("--out", type=Path, required=True)
    sp.add_argument("--n", type=int, default=4)
    sp.add_argument("--overlap", type=int, default=32)
    st = sub.add_parser("stitch")
    st.add_argument("--tiles", type=Path, required=True)
    st.add_argument("--out", type=Path, required=True)
    st.add_argument("--n", type=int, default=4)
    st.add_argument("--overlap", type=int, default=32)
    args = p.parse_args()
    if args.cmd == "split":
        split(args.input, args.out, args.n, args.overlap)
    else:
        stitch(args.tiles, args.out, args.n, args.overlap)


if __name__ == "__main__":
    main()
