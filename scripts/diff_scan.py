"""Breadth-first registered-image measurements. RGB is display-referred [0,1]."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter, ImageDraw


def boxmean(a,radius=4):
    p=np.pad(a,((radius,radius),(radius,radius)),mode='reflect')
    s=np.pad(p,((1,0),(1,0))).cumsum(0).cumsum(1)
    k=2*radius+1
    return (s[k:,k:]-s[:-k,k:]-s[k:,:-k]+s[:-k,:-k])/(k*k)


def features(rgb):
    gray=rgb@np.array([.2126,.7152,.0722])
    p=np.pad(gray,1,mode='edge')
    lap=4*gray-p[1:-1,:-2]-p[1:-1,2:]-p[:-2,1:-1]-p[2:,1:-1]
    mean=boxmean(gray)
    return {'greenery':greenery(rgb).astype(float),'luminance':gray,
            'sharpness':np.maximum(0,boxmean(lap*lap)),'contrast':np.sqrt(np.maximum(0,boxmean(gray*gray)-mean*mean)),
            'pointlight':((gray-mean)>.055)&(gray>.13),
            'presence':np.sqrt(np.maximum(0,boxmean(gray*gray,12)-boxmean(gray,12)**2))}


def light_components(mask,valid):
    """8-connected bright-core components, not semantic light-source identities."""
    mask=mask&valid;seen=np.zeros(mask.shape,bool);h,w=mask.shape;result=[]
    for y,x in zip(*np.nonzero(mask)):
        if seen[y,x]:continue
        seen[y,x]=True;stack=[(int(y),int(x))];pts=[]
        while stack:
            yy,xx=stack.pop();pts.append((yy,xx))
            for dy,dx in ((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)):
                ny,nx=yy+dy,xx+dx
                if 0<=ny<h and 0<=nx<w and mask[ny,nx] and not seen[ny,nx]:seen[ny,nx]=True;stack.append((ny,nx))
        if 1<=len(pts)<=1500:
            ys,xs=np.array(pts).T;area=len(pts)
            result.append({'x':float(xs.mean()),'y':float(ys.mean()),'area':area,'equivalent_diameter':float(2*np.sqrt(area/np.pi)),
                           'aspect':float((xs.max()-xs.min()+1)/(ys.max()-ys.min()+1))})
    return result


def scan(target_path,current_path,out,ui_mask=None,semantic=None,cols=4,rows=6,max_width=1024):
    """Scan registered equal-aspect frames. Semantic labels are caller-supplied, not detections."""
    if min(cols,rows,max_width)<1:raise ValueError('grid and analysis width must be positive')
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    ti=Image.open(target_path).convert('RGB');ci=Image.open(current_path).convert('RGB')
    native_t,native_c=ti.size,ci.size
    if abs(ti.width/ti.height-ci.width/ci.height)>.002:raise ValueError('aspect mismatch: register images explicitly first')
    w=min(ti.width,ci.width,max_width);h=round(w*ti.height/ti.width)
    t=np.array(ti.resize((w,h),Image.Resampling.LANCZOS),dtype=float)/255
    c=np.array(ci.resize((w,h),Image.Resampling.LANCZOS),dtype=float)/255
    valid=np.ones((h,w),bool)
    if ui_mask:valid=np.array(Image.open(ui_mask).convert('L').resize((w,h),Image.Resampling.NEAREST))<128
    ft,fc=features(t),features(c)
    # Never allow an excluded overlay's edges to leak into neighbouring metrics.
    eroded=np.array(Image.fromarray((valid*255).astype('uint8')).filter(ImageFilter.MinFilter(27)))>0
    valid=valid.astype(bool)
    sem=json.loads(Path(semantic).read_text()) if isinstance(semantic,(str,Path)) else (semantic or [])
    regs=[{'name':f'grid-{y+1}-{x+1}','bbox':[x/cols,y/rows,(x+1)/cols,(y+1)/rows],'kind':'grid'} for y in range(rows) for x in range(cols)]
    regs += [dict(q,kind='semantic') for q in sem]
    tiles=[]
    for q in regs:
        box=q['bbox']
        if len(box)!=4 or not all(np.isfinite(v) and 0<=v<=1 for v in box) or box[0]>=box[2] or box[1]>=box[3]:raise ValueError('invalid normalized region')
        x0,y0,x1,y1=[round(v*(w if i%2==0 else h)) for i,v in enumerate(box)]
        if x1<=x0 or y1<=y0:raise ValueError('region too small at analysis resolution')
        sl=np.s_[y0:y1,x0:x1];v=valid[sl];ve=eroded[sl]
        m=measure(t[sl],c[sl],v)
        for key in ft:
            vv=ve if key in ('sharpness','contrast','pointlight','presence') else v
            for label,f in [('target',ft),('current',fc)]:m[label+'_'+key]=float(f[key][sl][vv].mean()) if vv.any() else 0.
        m['excess_sharpness']=max(0.,m['current_sharpness']-m['target_sharpness'])
        m['sharpness_ratio']=(m['current_sharpness']+1e-8)/(m['target_sharpness']+1e-8)
        m['luminance_delta']=m['current_luminance']-m['target_luminance']
        m['presence_delta']=m['current_presence']-m['target_presence']
        m['mean_absolute_rgb_delta']=float(np.abs(t[sl]-c[sl])[v].mean()) if v.any() else 0.
        components={}
        for label,f in [('target',ft),('current',fc)]:
            comp=light_components(f['pointlight'][sl],ve)
            components[label]={'count':len(comp),'median_diameter':float(np.median([z['equivalent_diameter'] for z in comp])) if comp else 0.}
        # Combined proxies nominate inspection; not a similarity/acceptance score.
        severity=min(1.,2*m['mean_absolute_rgb_delta']+2*m['missing_greenery']+m['excess_greenery']+4*np.sqrt(m['excess_sharpness']))
        area=m['valid_pixels']/(w*h);cost=float(q.get('cost',1))
        if cost<=0:raise ValueError('cost must be positive')
        flags=[]
        if m['missing_greenery']>.005:flags.append('missing greenery')
        if m['excess_greenery']>.005:flags.append('excess/misplaced greenery')
        if m['sharpness_ratio']>1.7 and m['current_sharpness']>1e-5:flags.append('too sharp / inspect blur')
        if abs(m['luminance_delta'])>.015:flags.append('too bright' if m['luminance_delta']>0 else 'too dark')
        if abs(m['presence_delta'])>.008:flags.append('presence/structure mismatch')
        if abs(components['target']['count']-components['current']['count'])>3:flags.append('bright-core count mismatch')
        tiles.append(dict(q,metrics=m,lights=components,flags=flags,visible_area=area,severity=severity,cost=cost,score=area*severity/cost))
    ranked=sorted(tiles,key=lambda q:q['score'],reverse=True)
    sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    result={'schema_version':1,'target':str(target_path),'current':str(current_path),'target_sha256':sha(target_path),'current_sha256':sha(current_path),
            'ui_mask_sha256':sha(ui_mask) if ui_mask else None,'target_native':native_t,'current_native':native_c,'analysis_size':[w,h],
            'valid_pixels':int(valid.sum()),'tiles':tiles,'ranked':ranked,
            'counts':{'grid_tiles':cols*rows,'semantic_tiles':len(sem),'flagged_tiles':sum(bool(q['flags']) for q in tiles)},
            'caveats':['Grid/semantic tiles overlap: counts are flagged regions, not distinct defects.',
                       'HSV/ExG misses blue-lit moss and can include nonplants; inspect overlays.',
                       'Bright components are cores, not recovered lights; glints and lettering can count.',
                       'Sharpness is scale/texture sensitive; blur hypotheses require visual/depth verification.',
                       'Caller semantic labels and manual observations are not automatic rediscovery.',
                       'Approved deviations/locked subjects are not authority to modify them.']}
    (out/'diff.json').write_text(json.dumps(result,indent=2))
    def save_map(name,a):Image.fromarray((np.clip(a,0,1)*255).astype('uint8')).save(out/name)
    for label,f in [('target',ft),('current',fc)]:
        for key,a in f.items():
            scale=20 if key=='sharpness' else 1
            save_map(f'{label}-{key}.png',np.sqrt(a)*scale*valid if key=='sharpness' else a*valid)
    for index,q in enumerate(tiles):
        folder=Path('tiles')/f'{index:03d}';(out/folder).mkdir(parents=True,exist_ok=True)
        q['tile_directory']=str(folder)
        x0,y0,x1,y1=[round(v*(w if i%2==0 else h)) for i,v in enumerate(q['bbox'])];sl=np.s_[y0:y1,x0:x1]
        save_map(folder/'valid.png',valid[sl])
        for label,rgb,f in [('target',t,ft),('current',c,fc)]:
            save_map(folder/(label+'.png'),rgb[sl]*valid[sl][...,None])
            for key,a in f.items():
                data=np.sqrt(a[sl])*20 if key=='sharpness' else a[sl]
                save_map(folder/(label+'-'+key+'.png'),data*valid[sl])
    (out/'diff.json').write_text(json.dumps(result,indent=2))
    differences={'greenery':(ft['greenery']-fc['greenery']),'sharpness':np.sqrt(fc['sharpness'])-np.sqrt(ft['sharpness']),
                 'luminance':fc['luminance']-ft['luminance'],'presence':fc['presence']-ft['presence'],'pointlight':fc['pointlight'].astype(float)-ft['pointlight'].astype(float)}
    for key,d in differences.items():
        strength=np.clip(np.abs(d)*(1 if key in ('greenery','pointlight') else 5),0,1)*valid
        color=np.where((d>0)[...,None],np.array([1,.12,.1]),np.array([.1,.7,1]))
        overlay=(c*.7)*(1-strength[...,None]*.65)+color*strength[...,None]*.7
        save_map('overlay-'+key+'.png',overlay)
    im=Image.fromarray((c*255).astype('uint8'));draw=ImageDraw.Draw(im)
    for i,q in enumerate(ranked):
        box=tuple(round(v*(w if n%2==0 else h)) for n,v in enumerate(q['bbox']));draw.rectangle(box,outline='orange' if q['kind']=='semantic' else '#7799aa',width=1);draw.text((box[0]+3,box[1]+3),str(i+1),fill='white')
    im.save(out/'ranked-regions.png')
    lines=['# Whole-frame difference scan','',f'Analysis: {w}×{h}; target native {native_t}; current native {native_c}.',
           '','Rank = valid visible-area fraction × measured severity / caller cost. A review queue, not automatic acceptance.',
           '','| Rank | Region | Score | Flags | Missing green | Sharp ratio | Luma Δ | Core count T/C | Owner |',
           '|---:|---|---:|---|---:|---:|---:|---|---|']
    for i,q in enumerate(ranked):
        m=q['metrics'];lights=q['lights'];lines.append(f"| {i+1} | {q['name']} | {q['score']:.5f} | {', '.join(q['flags']) or 'inspect'} | {m['missing_greenery']:.3f} | {m['sharpness_ratio']:.2f} | {m['luminance_delta']:+.3f} | {lights['target']['count']}/{lights['current']['count']} | {q.get('owner','unassigned')} |")
    lines+=['','## Semantic observations supplied by reviewer']+[f"- **{q['name']}**: {q['observation']}" for q in sem if 'observation' in q]
    lines+=['','## Limits']+['- '+x for x in result['caveats']]
    (out/'DIFF.md').write_text('\n'.join(lines)+'\n')
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('target');p.add_argument('current');p.add_argument('out');p.add_argument('--ui-mask');p.add_argument('--semantic');p.add_argument('--cols',type=int,default=4);p.add_argument('--rows',type=int,default=6);p.add_argument('--max-width',type=int,default=1024)
    a=p.parse_args();r=scan(a.target,a.current,a.out,a.ui_mask,a.semantic,a.cols,a.rows,a.max_width);print(json.dumps(r['counts']))


def greenery(rgb):
    """Conservative HSV + normalized excess green, including dark blue-green."""
    hsv=np.asarray(Image.fromarray((np.clip(rgb,0,1)*255).astype('uint8')).convert('HSV'),dtype=float)/255
    r,g,b=np.moveaxis(rgb,-1,0)
    exg=(2*g-r-b)/(r+g+b+1e-6)
    return (hsv[...,0]>.16)&(hsv[...,0]<.48)&(hsv[...,1]>.18)&(hsv[...,2]>.025)&(exg>.06)


def measure(target,current,valid):
    if target.shape!=current.shape or target.shape[:2]!=valid.shape:raise ValueError('shape mismatch')
    if not valid.any():return {'valid_pixels':0,'missing_greenery':0.,'excess_greenery':0.}
    tg,cg=greenery(target),greenery(current)
    return {'valid_pixels':int(valid.sum()),'missing_greenery':float((tg&~cg)[valid].mean()),'excess_greenery':float((cg&~tg)[valid].mean())}


if __name__=='__main__':main()
