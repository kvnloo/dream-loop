#!/usr/bin/env python3
"""Structure gate: the dream-loop crop_gate idea, computed on STRUCTURE instead of raw pixels.

Same job as crop_gate.py: exit non-zero while COMPOSITION is wrong (camera, framing, lens,
layout, missing/misplaced masses), so lighting/materials are not judged yet.
crop_gate diffs FIND_EDGES of the full-resolution frame, so on a detailed target its
disagreement is dominated by fine texture (pores, halftone, print) and by exposure /
sharpening, and no massing change can pass it. This gate keeps crop_gate's edge
operator and strong-edge threshold but removes what is not composition first:

  1. luminance only (colour / white balance are lighting + material)
  2. ignore mask (UI overlay) excluded by normalised convolution, never filled
  3. Gaussian low-pass (SIGMA, full-res px), then area downscale to WIDTH px
     (fine texture is material)
  4. crop_gate._edges (FIND_EDGES) on both; strong edge = response > 40 (crop_gate's)
  5. only LONG strong edges count: 8-connected runs of >= MIN_LEN px (silhouettes,
     mass outlines, horizon/vanishing lines; not pores, halftone dots or print specks)
  6. hysteresis match: a long strong edge in one image is matched if the other image
     has an edge response >= MATCH_LO within MATCH_R px (exposure, contrast and
     sharpening change edge strength, not edge position)
  7. FAIL if  unmatched_frac = unmatched long edges (both directions) / all long edges
              >= UNMATCHED_FAIL                      (global: camera, lens, layout)
     or if    tile_unmatched = worst TILE x TILE window's unmatched px
              >= TILE_FAIL                            (local: one missing/moved mass)

edge_mae and disagree_frac (crop_gate's own statistics, on the structure images) are
reported for comparison but do not decide. All parameters come from the known-answer
validation (references/structure-gate.md), not from what makes a render pass. Inspect the
overlay even on PASS: this is an edge heuristic, not a vanishing-line detector, and it
cannot tell a moved cast shadow from a moved mass edge when the shadow is strong.

Usage: structure_gate.py target.png capture.png [out_dir] [--mask ui_mask.png]
Exit 0 = PASS, 2 = COMPOSITION FAIL.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

# ---- validated parameters (references/structure-gate.md) ----
SIGMA = 1.5            # Gaussian low-pass, full-res px
WIDTH = 256            # structure width, px (area downscale)
BIN = 40               # crop_gate's strong-edge threshold (unchanged)
MIN_LEN = 12           # long edge: 8-connected strong-edge run, px at WIDTH
MATCH_R = 1            # match radius, px at WIDTH
MATCH_LO = 15          # weaker response that still counts as "edge present"
UNMATCHED_FAIL = 0.028  # global term
TILE = 48              # local window, px at WIDTH (stride TILE/2)
TILE_FAIL = 36         # local term: unmatched long-edge px in the worst window
EDGE_FAIL = 28.0        # crop_gate's limits, reported only
DISAGREE_FAIL = 0.18


def _load_crop_gate():
    """Import the skill's crop_gate.py unchanged (for _fit and _edges)."""
    skill = Path(os.environ.get("DREAM_LOOP_SKILL", "/workspace/dream-loop"))
    here = Path(__file__).resolve().parent
    for p in (here / "crop_gate.py", skill / "scripts" / "crop_gate.py"):
        if p.exists():
            spec = importlib.util.spec_from_file_location("crop_gate", p)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    raise SystemExit("crop_gate.py not found (set DREAM_LOOP_SKILL)")


CG = _load_crop_gate()


def _blur(a: np.ndarray, sigma: float) -> np.ndarray:
    if sigma <= 0:
        return a
    r = max(1, int(round(3 * sigma)))
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2)
    k /= k.sum()
    p = np.pad(a, r, mode="reflect")
    p = np.apply_along_axis(lambda v: np.convolve(v, k, mode="valid"), 0, p)
    return np.apply_along_axis(lambda v: np.convolve(v, k, mode="valid"), 1, p)


def _luma(im: Image.Image) -> np.ndarray:
    return np.asarray(ImageOps.grayscale(im), dtype=np.float64)


def _structure(lum: np.ndarray, valid: np.ndarray, sigma: float, width: int):
    """Normalised-convolution low-pass (masked px never contribute), then area downscale."""
    v = valid.astype(np.float64)
    num, den = _blur(lum * v, sigma), _blur(v, sigma)
    low = np.where(den > 1e-3, num / np.maximum(den, 1e-3), 0.0)
    h, w = lum.shape
    size = (width, max(1, round(h * width / w))) if width and width < w else (w, h)
    small = np.asarray(Image.fromarray(low.astype(np.float32), "F").resize(size, Image.Resampling.BOX), dtype=np.float64)
    vs = np.asarray(Image.fromarray((den > 0.5).astype(np.float32), "F").resize(size, Image.Resampling.BOX)) > 0.999
    return small, vs


def _erode(m: np.ndarray, n: int = 1) -> np.ndarray:
    for _ in range(n):
        p = np.pad(m, 1, constant_values=False)
        m = p[1:-1, 1:-1] & p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]
    return m


def _dilate_max(a: np.ndarray, r: int) -> np.ndarray:
    p = np.pad(a, r, mode="constant")
    h, w = a.shape
    out = a.copy()
    for dy in range(2 * r + 1):
        for dx in range(2 * r + 1):
            out = np.maximum(out, p[dy:dy + h, dx:dx + w])
    return out


def _long(b: np.ndarray, min_len: int) -> np.ndarray:
    """Keep 8-connected components of b with >= min_len px."""
    h, w = b.shape
    seen = np.zeros_like(b)
    keep = np.zeros_like(b)
    for y0, x0 in zip(*np.nonzero(b)):
        if seen[y0, x0]:
            continue
        q = deque([(y0, x0)]); seen[y0, x0] = True; comp = []
        while q:
            y, x = q.popleft(); comp.append((y, x))
            for yy in (y - 1, y, y + 1):
                for xx in (x - 1, x, x + 1):
                    if 0 <= yy < h and 0 <= xx < w and b[yy, xx] and not seen[yy, xx]:
                        seen[yy, xx] = True; q.append((yy, xx))
        if len(comp) >= min_len:
            ys, xs = zip(*comp); keep[list(ys), list(xs)] = True
    return keep


def _worst_tile(un: np.ndarray, t: int) -> tuple[int, tuple[int, int]]:
    s = max(1, t // 2)
    best = (0, (0, 0))
    for y in range(0, max(1, un.shape[0] - t + 1), s):
        for x in range(0, max(1, un.shape[1] - t + 1), s):
            n = int(un[y:y + t, x:x + t].sum())
            if n > best[0]:
                best = (n, (x, y))
    return best


def gate(target, capture, out_dir: Path | None = None, mask=None, **kw) -> dict:
    P = dict(sigma=SIGMA, width=WIDTH, bin=BIN, min_len=MIN_LEN, match_r=MATCH_R, match_lo=MATCH_LO,
             unmatched_fail=UNMATCHED_FAIL, tile=TILE, tile_fail=TILE_FAIL)
    P.update(kw)
    t = (target if isinstance(target, Image.Image) else Image.open(target)).convert("RGB")
    c = CG._fit(capture if isinstance(capture, Image.Image) else Image.open(capture), t.size)  # crop_gate's Lanczos fit
    if mask is None:
        ign = np.zeros((t.size[1], t.size[0]), bool)
    elif isinstance(mask, np.ndarray):
        ign = mask.astype(bool)
    else:
        ign = np.asarray(Image.open(mask).convert("L").resize(t.size, Image.Resampling.NEAREST)) > 127
    valid = ~ign
    ts, vs = _structure(_luma(t), valid, P["sigma"], P["width"])
    cs, _ = _structure(_luma(c), valid, P["sigma"], P["width"])
    ti = Image.fromarray(np.clip(np.rint(ts), 0, 255).astype(np.uint8), "L")
    ci = Image.fromarray(np.clip(np.rint(cs), 0, 255).astype(np.uint8), "L")
    te = np.asarray(CG._edges(ti), dtype=np.float64)
    ce = np.asarray(CG._edges(ci), dtype=np.float64)
    # FIND_EDGES has a 1-px kernel: drop the frame border and px whose kernel touched the mask
    sv = _erode(vs, 1)
    sv[0, :] = sv[-1, :] = sv[:, 0] = sv[:, -1] = False
    tb, cb = (te > P["bin"]) & sv, (ce > P["bin"]) & sv
    # crop_gate's own statistics on the structure images (reported, not deciding)
    mae = float(np.abs(te - ce)[sv].mean())
    su = int((tb | cb).sum())
    dis = float((tb ^ cb).sum() / su) if su else 0.0
    # decision: long strong edges, hysteresis-matched
    tl, cl = _long(tb, P["min_len"]), _long(cb, P["min_len"])
    tm, cm = _dilate_max(te, P["match_r"]), _dilate_max(ce, P["match_r"])
    miss = tl & (cm < P["match_lo"])     # target structure absent from capture
    extra = cl & (tm < P["match_lo"])    # capture structure absent from target
    un = miss | extra
    ul = int((tl | cl).sum())
    ufrac = float((int(miss.sum()) + int(extra.sum())) / ul) if ul else 0.0
    tile_n, (tx, ty) = _worst_tile(un, P["tile"])
    g_fail = ufrac >= P["unmatched_fail"]
    l_fail = tile_n >= P["tile_fail"]
    ok = not (g_fail or l_fail)
    scale = t.size[0] / ts.shape[1]
    res = {"ok": ok,
           "unmatched_frac": round(ufrac, 4), "unmatched_fail_at": P["unmatched_fail"],
           "tile_unmatched": tile_n, "tile_fail_at": P["tile_fail"],
           "worst_tile_px": [round(tx * scale), round(ty * scale), round((tx + P["tile"]) * scale), round((ty + P["tile"]) * scale)],
           "fail_terms": [n for n, f in (("global", g_fail), ("local", l_fail)) if f],
           "edge_mae": round(mae, 3), "disagree_frac": round(dis, 4),
           "long_edges": ul, "missing_px": int(miss.sum()), "extra_px": int(extra.sum()), "params": P}
    if out_dir is not None:
        out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
        ti.save(out_dir / "structure_target.png"); ci.save(out_dir / "structure_capture.png")
        h, w = te.shape
        um = np.zeros((h, w, 3), np.uint8); um[..., 2] = miss * 255; um[..., 0] = extra * 255
        Image.fromarray(um).save(out_dir / "structure_unmatched.png")  # B = missing, R = extra (structure px)
        vis = np.zeros((h, w, 3), np.uint8)
        vis[(tl | cl) & ~un] = (235, 235, 235)   # matched long edges
        vis[miss] = (0, 200, 255)                # in target, missing from capture
        vis[extra] = (255, 60, 40)               # in capture, not in target
        vis[~sv] = (40, 40, 90)                  # ignored (UI mask)
        big = Image.fromarray(vis).resize(t.size, Image.Resampling.NEAREST)
        out = Image.blend(t, big, 0.75)
        from PIL import ImageDraw
        d = ImageDraw.Draw(out)
        d.rectangle(res["worst_tile_px"], outline=(255, 220, 0), width=3)
        d.text((12, 12), f"structure_gate {'PASS' if ok else 'FAIL'} unmatched={ufrac:.3f} (<{P['unmatched_fail']}) "
               f"tile={tile_n} (<{P['tile_fail']})  cyan=missing red=extra", fill=(255, 255, 255))
        out.save(out_dir / "structure_gate.png")
        res["preview"] = str(out_dir / "structure_gate.png")
        (out_dir / "structure_gate.json").write_text(json.dumps(res, indent=1))
    return res


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("target"); ap.add_argument("capture"); ap.add_argument("out_dir", nargs="?")
    ap.add_argument("--mask", help="ignore mask (white = ignore), e.g. ui_mask.png")
    a = ap.parse_args()
    r = gate(Path(a.target), Path(a.capture), Path(a.out_dir) if a.out_dir else None,
             Path(a.mask) if a.mask else None)
    print({k: v for k, v in r.items() if k != "params"})
    if not r["ok"]:
        print("COMPOSITION FAIL (structure): skip lighting/materials judging. Continue with a camera or massing action.", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
