#!/usr/bin/env python3
"""Fetch a PolyHaven PBR set (no MCP). Prints paths for bpy.

  python scripts/polyhaven_pbr.py dirt --out .dream-loop/pbr --res 1k
"""
from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path

UA = {"User-Agent": "dream-loop-polyhaven/1.0"}
API = "https://api.polyhaven.com/files/{id}"
MAPS = (
    ("Diffuse", "diff", "jpg"),
    ("nor_gl", "nor_gl", "jpg"),
    ("Rough", "rough", "jpg"),
    ("Displacement", "disp", "jpg"),
)


def get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r, dest.open("wb") as f:
        f.write(r.read())


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("asset_id", help="PolyHaven texture id, e.g. dirt")
    p.add_argument("--out", type=Path, default=Path(".dream-loop/pbr"))
    p.add_argument("--res", default="1k", choices=("1k", "2k", "4k"))
    args = p.parse_args()
    meta = get_json(API.format(id=args.asset_id))
    written = {}
    for key, slug, ext in MAPS:
        block = meta.get(key) or meta.get(slug)
        if not isinstance(block, dict):
            continue
        res = block.get(args.res) or next(iter(block.values()), None)
        if not isinstance(res, dict):
            continue
        url = (res.get(ext) or res.get("png") or {}).get("url") if isinstance(res.get(ext), dict) else None
        if url is None and isinstance(res, dict):
            inner = res.get(ext) or res.get("jpg") or res.get("png")
            if isinstance(inner, dict):
                url = inner.get("url")
        if not url:
            continue
        dest = args.out / f"{args.asset_id}_{slug}.{ext}"
        download(url, dest)
        written[slug] = str(dest.resolve())
        print(f"{slug}\t{dest}")
    if "diff" not in written and "Diffuse" not in meta:
        print("no maps; check asset id", file=__import__("sys").stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
