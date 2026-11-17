#!/usr/bin/env python3
"""Split equal-aspect images into semantic crops and a complete padded grid.

Default rejects resolution mismatch; --align explicitly permits uniform resizing
for diagnostics, never inventing native detail. Paths in manifest are relative to
its directory. Existing output directories are refused to preserve evidence.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def split(target, capture, output, semantic=None, cols=4, rows=6, padding=32,
          mask=None, align=False, brief_revision='brief-v1'):
    target, capture, output = map(Path, (target, capture, output))
    t = Image.open(target).convert('RGB')
    c = Image.open(capture).convert('RGB')
    original = c.size
    w, h = t.size
    if w * c.height != h * c.width:
        raise ValueError('aspect ratios differ; do not warp evidence')
    if c.size != t.size and not align:
        raise ValueError('resolution mismatch; --align allows diagnostic resize only')
    if not (1 <= cols <= w and 1 <= rows <= h and padding >= 0):
        raise ValueError('invalid grid or padding')
    c = c.resize(t.size, Image.Resampling.LANCZOS) if c.size != t.size else c
    ignored = np.zeros((h, w), dtype=bool)
    if mask:
        im = Image.open(mask).convert('L')
        if im.size != t.size:
            raise ValueError('mask dimensions differ')
        ignored = np.asarray(im) > 127
    regions = []
    ids = set()
    if semantic:
        data = json.loads(Path(semantic).read_text())
        for r in data['regions']:
            ident = r['id']
            if (not isinstance(ident, str) or not ident or
                    not all(ch.isascii() and (ch.isalnum() or ch in '-_') for ch in ident) or
                    ident in ids or ident.startswith('grid-')):
                raise ValueError('invalid or duplicate semantic id')
            box = r['box']
            if (not isinstance(box, list) or len(box) != 4 or
                    not all(type(v) is int for v in box)):
                raise ValueError('box must have four integer coordinates')
            x0, y0, x1, y1 = box
            if not (0 <= x0 < x1 <= w and 0 <= y0 < y1 <= h):
                raise ValueError('semantic box outside image')
            ids.add(ident)
            regions.append(dict(id=ident, name=r.get('name', ident), layer='semantic',
                                box=box, core_box=box))
    coverage = np.zeros((h, w), dtype=np.uint8)
    for y in range(rows):
        for x in range(cols):
            core = [x*w//cols, y*h//rows, (x+1)*w//cols, (y+1)*h//rows]
            a, b, d, e = core
            coverage[b:e, a:d] += 1
            regions.append(dict(id=f'grid-{y+1}-{x+1}', name=f'grid {y+1}/{x+1}',
                                layer='grid', core_box=core,
                                box=[max(0,a-padding),max(0,b-padding),
                                     min(w,d+padding),min(h,e+padding)]))
    if not np.all(coverage == 1):
        raise ValueError('grid coverage failure')
    inputs = {name: {'path': str(p.resolve()), 'sha256': sha(p)}
              for name, p in [('target',target),('capture',capture)]}
    if mask:
        inputs['mask'] = {'path': str(Path(mask).resolve()), 'sha256': sha(mask)}
    if semantic:
        inputs['semantic'] = {'path': str(Path(semantic).resolve()), 'sha256': sha(semantic)}
    output.mkdir(parents=True, exist_ok=False)
    for row in regions:
        a,b,d,e = row['core_box']
        x0,y0,x1,y1 = row['box']
        row['mask_fraction_core'] = float(ignored[b:e,a:d].mean())
        row['mask_fraction_padded'] = float(ignored[y0:y1,x0:x1].mean())
        row['skipped'] = row['layer']=='grid' and row['mask_fraction_core'] > .9
        row['skip_reason'] = 'more than 90% of core ignored' if row['skipped'] else None
        row['brief_revision'] = brief_revision
        # Save unaltered native crops; scope masks travel separately in the manifest.
        for name, image in [('target',t),('capture',c)]:
            path = output/f"{row['id']}-{name}.png"
            image.crop(row['box']).save(path)
            row[name] = path.name
        context = Image.new('RGB',(2*w,h))
        context.paste(t,(0,0));context.paste(c,(w,0))
        draw = ImageDraw.Draw(context)
        for dx in (0,w):
            draw.rectangle([x0+dx,y0,x1-1+dx,y1-1], outline='yellow', width=2)
        context.thumbnail((1000,750))
        path = output/f"{row['id']}-context.png";context.save(path)
        row['context'] = path.name
        row['delivered_size'] = [x1-x0,y1-y0]
        row['hashes'] = {k:sha(output/row[k]) for k in ['target','capture','context']}
    manifest = dict(schema_version=1, brief_revision=brief_revision, inputs=inputs,
                    reference_size=list(t.size), capture_original_size=list(original),
                    native_pair=original==t.size, alignment='none' if original==t.size else 'uniform LANCZOS diagnostic only',
                    grid={'cols':cols,'rows':rows,'padding':padding}, regions=regions,
                    coverage={'pixels':w*h,'grid_cores_exactly_once':True},
                    counts={'total':len(regions),'active':sum(not r['skipped'] for r in regions),
                            'skipped':sum(r['skipped'] for r in regions)})
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('target');p.add_argument('capture');p.add_argument('output')
    p.add_argument('--semantic');p.add_argument('--mask');p.add_argument('--align',action='store_true')
    p.add_argument('--cols',type=int,default=4);p.add_argument('--rows',type=int,default=6)
    p.add_argument('--padding',type=int,default=32);p.add_argument('--brief-revision',default='brief-v1')
    a = p.parse_args()
    try:
        result = split(**vars(a))
    except (ValueError, OSError, KeyError, TypeError) as e:
        p.exit(2, str(e)+'\n')
    print(json.dumps(result['counts']))


if __name__ == '__main__':
    main()
