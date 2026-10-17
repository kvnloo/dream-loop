#!/usr/bin/env python3
"""Make a labelled full-frame or native-crop sheet; refuse reused paths."""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw


def make_sheet(output, images, labels=None, box=None, max_width=None):
    output=Path(output)
    receipt=output.with_suffix('.json')
    if output.exists() or receipt.exists():raise ValueError('output/receipt already exists')
    if output.suffix.lower()!='.png':raise ValueError('use .png output')
    if not images or (labels is not None and len(labels)!=len(images)):
        raise ValueError('one label per image required')
    labels=labels or [Path(x).stem for x in images]
    sources=[];crops=[];size=None
    for name in images:
        path=Path(name)
        with Image.open(path) as im:image=im.convert('RGB')
        if size is None:size=image.size
        if image.size!=size:raise ValueError('dimensions differ; align explicitly before comparison')
        if box:
            x0,y0,x1,y1=box
            if not 0<=x0<x1<=image.width or not 0<=y0<y1<=image.height:raise ValueError('invalid crop box')
            image=image.crop(box)
        sources.append(dict(path=str(path.resolve()),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),size=list(size)))
        crops.append(image)
    w,h=crops[0].size
    sheet=Image.new('RGB',(w*len(crops),h+28),(24,24,24));draw=ImageDraw.Draw(sheet)
    for i,(im,label) in enumerate(zip(crops,labels)):
        sheet.paste(im,(i*w,28));draw.text((i*w+4,6),label,fill='white')
    native=True
    if max_width is not None:
        if max_width<1:raise ValueError('max width must be positive')
        if sheet.width>max_width:
            sheet=sheet.resize((max_width,max(1,round(sheet.height*max_width/sheet.width))),Image.Resampling.LANCZOS);native=False
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('xb') as f:sheet.save(f,format='PNG')
    data=dict(inputs=sources,labels=labels,box=box,native=native,output_size=list(sheet.size),
              output_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
              warning='Native source pixels may still be downscaled by the viewer; verify delivered dimensions.')
    with receipt.open('x') as f:json.dump(data,f,indent=2);f.write('\n')
    return data


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('output');p.add_argument('images',nargs='+');p.add_argument('--labels',nargs='+')
    p.add_argument('--box',type=int,nargs=4);p.add_argument('--max-width',type=int)
    a=p.parse_args()
    try:r=make_sheet(**vars(a))
    except (ValueError,OSError) as e:p.exit(2,str(e)+'\n')
    print(json.dumps({'size':r['output_size'],'native':r['native']}))


if __name__=='__main__':main()
