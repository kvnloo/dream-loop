#!/usr/bin/env python3
"""Validate tile verdicts and aggregate diagnostics, never promotion.

Exit 2 on missing/invalid verdicts, with an honest partial report. Evidence-session
verification and semantic adjudication remain separate requirements.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics

CATEGORIES = {'composition':3,'lighting':3,'materials':3,'details':1,'total':10}
CLASSES = {'camera','massing','material','lighting','mesh','layout','typography','behavior','display'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def strings(values):
    return isinstance(values,list) and all(isinstance(x,str) and x.strip() for x in values)


def validate(v, row, revision):
    require(isinstance(v,dict) and set(v)=={'id','box','brief_revision','alignment','scores','gaps','preserve','tiers'},'contract keys')
    require(v['id']==row['id'] and v['box']==row['box'] and v['brief_revision']==revision,'identity/box/revision')
    require(v['alignment'] in {'pass','limited','blocked'},'alignment')
    s = v['scores']; require(isinstance(s,dict) and set(s)==set(CATEGORIES),'score keys')
    for k,hi in CATEGORIES.items():
        if v['alignment']=='blocked' and k!='composition':
            require(s[k] is None,'blocked scores must be null')
        else:
            require(type(s[k]) in (int,float) and math.isfinite(s[k]) and 0<=s[k]<=hi,'score range/type')
    if v['alignment']!='blocked':
        require(abs(s['total']-sum(s[k] for k in CATEGORIES if k!='total')) < 1e-6,'score sum')
    require(strings(v['preserve']),'preserve list')
    require(isinstance(v['gaps'],list),'gaps list')
    for g in v['gaps']:
        require(isinstance(g,dict) and set(g)=={'element','defect','change_class','action','evidence','protected'},'gap keys')
        require(all(isinstance(g[k],str) and g[k].strip() for k in g if k!='protected'),'gap strings')
        require(type(g['protected']) is bool and g['change_class'] in CLASSES,'gap class/protection')
    require(isinstance(v['tiers'],list),'tiers list')
    for t in v['tiers']:
        require(isinstance(t,dict) and set(t)=={'element','tier','reason'},'tier keys')
        require(t['tier'] in {'PERFECT','MOSTLY_GOOD','NEEDS_WORK','UNKNOWN'},'tier enum')
        require(all(isinstance(t[k],str) and t[k].strip() for k in ['element','reason']),'tier text')
    return v


def aggregate(manifest, verdicts):
    manifest, verdicts = Path(manifest), Path(verdicts)
    m = json.loads(manifest.read_text())
    rows = m['regions']; ids = [r['id'] for r in rows]
    require(len(ids)==len(set(ids)), 'duplicate manifest ids')
    require(all(isinstance(i,str) and i and all(ch.isascii() and (ch.isalnum() or ch in '-_') for ch in i) for i in ids),'unsafe manifest id')
    valid,missing,invalid,skipped = {},[],{},[]
    for r in rows:
        if r['skipped']:
            skipped.append(r['id']);continue
        path = verdicts/(r['id']+'.json')
        if not path.exists():
            missing.append(r['id']);continue
        try:
            valid[r['id']] = validate(json.loads(path.read_text()),r,m['brief_revision'])
        except (ValueError,KeyError,TypeError) as e:
            invalid[r['id']] = str(e)
    means = {}
    for k in CATEGORIES:
        nums = [v['scores'][k] for v in valid.values() if v['scores'][k] is not None]
        means[k] = dict(mean=statistics.mean(nums) if nums else None,n=len(nums))
    groups = {}
    for ident,v in valid.items():
        for g in v['gaps']:
            key = (g['element'].strip().casefold(),g['defect'].strip().casefold())
            group = groups.setdefault(key,dict(element=g['element'],defect=g['defect'],tiles={},actions=set(),classes=set(),protected=False))
            group['tiles'].setdefault(ident,[])
            if g['evidence'] not in group['tiles'][ident]:group['tiles'][ident].append(g['evidence'])
            group['actions'].add(g['action']);group['classes'].add(g['change_class'])
            group['protected'] |= g['protected']
    fixes = []
    for g in groups.values():
        totals = [valid[i]['scores']['total'] for i in g['tiles'] if valid[i]['scores']['total'] is not None]
        fixes.append(dict(element=g['element'],defect=g['defect'],tiles=sorted(g['tiles']),
                          tile_count=len(g['tiles']),scored_severity=sum(10-t for t in totals),
                          scored_tiles=len(totals),blocked_tiles=[i for i in g['tiles'] if valid[i]['scores']['total'] is None],
                          actions=sorted(g['actions']),change_classes=sorted(g['classes']),
                          needs_adjudication=len(g['actions'])>1 or len(g['classes'])>1,
                          protected=g['protected'],evidence=[{'tile':i,'quotes':q} for i,q in sorted(g['tiles'].items())]))
    fixes.sort(key=lambda g:(-g['scored_severity'],g['element'],g['defect']))
    scored = sorted([v for v in valid.values() if v['scores']['total'] is not None],key=lambda v:(v['scores']['total'],v['id']))
    return dict(schema_version=1,diagnostic_only=True,review_verified=False,
                verification_limit='JSON contract only; verify native session/image receipts and adjudicate separately',
                manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest(),
                counts=dict(expected=len(rows)-len(skipped),valid=len(valid),skipped=len(skipped),missing=len(missing),invalid=len(invalid)),
                missing=missing,invalid=invalid,skipped=skipped,category_means=means,
                blocked=[v['id'] for v in valid.values() if v['alignment']=='blocked'],
                worst_ten=[v['id'] for v in scored[:10]],fixes=fixes,
                preserve=sorted({p for v in valid.values() for p in v['preserve']}),
                verdicts=list(valid.values()),
                severity_definition='Sum of 10-total per unique scored tile/defect. Blocked tiles listed separately; overlap is not independent confidence.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('manifest');p.add_argument('verdicts');p.add_argument('output')
    a=p.parse_args()
    try:
        result=aggregate(a.manifest,a.verdicts)
        with Path(a.output).open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    except (ValueError,OSError,KeyError,TypeError) as e:p.exit(2,str(e)+'\n')
    print(json.dumps(result['counts']))
    if result['missing'] or result['invalid']:p.exit(2,'Incomplete: see report\n')


if __name__=='__main__':main()
