#!/usr/bin/env python3
"""Prepare anonymous swapped A/B trials; --execute runs fresh Hermes one-shots.

Default is preparation only (no paid requests). Raw logs/process receipts are not
verified image-view evidence or automatic promotion. Audit native sessions before
using either verdict. No arbitrary shell commands are interpolated.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import time
from PIL import Image


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(target,parent,candidate,brief,output,provider,model,preferences,hermes='hermes',hermes_arg=None,
        execute=False,timeout=300,max_turns=12):
    if timeout<=0 or max_turns<=0:raise ValueError('positive timeout/turn budget required')
    sources={k:Path(v).resolve() for k,v in [('target',target),('parent',parent),('candidate',candidate),('brief',brief),('preferences',preferences)]}
    for path in sources.values():
        if not path.is_file():raise ValueError('missing input: '+str(path))
    images={}
    for name in ['target','parent','candidate']:
        with Image.open(sources[name]) as im:images[name]=im.convert('RGB')
    if len({im.size for im in images.values()})!=1:raise ValueError('evidence dimensions differ')
    text=sources['brief'].read_text()
    template=(Path(__file__).resolve().parents[1]/'templates/judge-ab.md').read_text()
    output=Path(output).resolve();output.mkdir(parents=True,exist_ok=False)
    mapping={'trial-1':{'A':'parent','B':'candidate'},'trial-2':{'A':'candidate','B':'parent'}}
    manifest=dict(inputs={k:{'path':str(p),'sha256':sha(p)} for k,p in sources.items()},
                  mapping=mapping,requested_provider=provider,requested_model=model,
                  review_verified=False,promotion='not-authorized',trials=[])
    failed=False
    for trial,decode in mapping.items():
        folder=output/trial;folder.mkdir()
        for label,name in [('TARGET','target'),*decode.items()]:images[name].save(folder/(label+'.png'))
        prompt=template.replace('{{BRIEF}}',text).replace('{{OWNER_PREFERENCES}}',sources['preferences'].read_text())
        for key in ['TARGET','A','B']:prompt=prompt.replace('{{'+key+'}}',str(folder/(key+'.png')))
        prompt+='\nRead no files outside these three images and this prompt. Return JSON only; do not write files.\n'
        path=folder/'prompt.md';path.write_text(prompt)
        argv=[hermes,*(hermes_arg or []),'chat','--oneshot','-Q','--provider',provider,'-m',model,
              '-t','file,vision','--safe-mode','--in',str(folder),'--format','stream-json',
              '--max-turns',str(max_turns),'--run-budget',str(timeout),'--query-file',str(path)]
        receipt=dict(argv=argv,prompt_sha256=sha(path),image_hashes={k:sha(folder/(k+'.png')) for k in ['TARGET','A','B']},
                     status='prepared',exit_code=None,started_at=None,elapsed_seconds=None)
        if execute:
            receipt['started_at']=datetime.now(timezone.utc).isoformat();start=time.monotonic()
            try:
                with (folder/'stream.jsonl').open('x') as log,(folder/'stderr.log').open('x') as err:
                    result=subprocess.run(argv,cwd=folder,stdin=subprocess.DEVNULL,stdout=log,stderr=err,timeout=timeout+10,check=False)
                receipt.update(exit_code=result.returncode,status='executed-needs-evidence-audit' if result.returncode==0 else 'failed')
            except subprocess.TimeoutExpired:
                receipt.update(status='timeout',exit_code=124)
            except OSError as e:
                receipt.update(status='launch-failed',exit_code=127,error=str(e))
            receipt['elapsed_seconds']=time.monotonic()-start
            failed |= receipt['exit_code']!=0
        (folder/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
        manifest['trials'].append({'trial':trial,'receipt':str((folder/'receipt.json').relative_to(output)),'status':receipt['status']})
        # Incremental records survive a disconnected worker. This manifest is a
        # new run's progress file, never an accepted evidence image/selector.
        (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        if failed:break  # Do not spend another request after a failed transport.
    manifest['inputs_unchanged']=all(sha(p)==manifest['inputs'][k]['sha256'] for k,p in sources.items())
    if not manifest['inputs_unchanged']:failed=True
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest,failed


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['target','parent','candidate','brief','output']:p.add_argument(key)
    p.add_argument('--provider',required=True);p.add_argument('--model',required=True)
    p.add_argument('--preferences',required=True,help='resolved scoped OWNER-PREFERENCES excerpt')
    p.add_argument('--hermes',default='hermes');p.add_argument('--hermes-arg',action='append')
    p.add_argument('--execute',action='store_true');p.add_argument('--timeout',type=int,default=300)
    p.add_argument('--max-turns',type=int,default=12)
    a=p.parse_args()
    try:m,failed=run(**vars(a))
    except (ValueError,OSError) as e:p.exit(2,str(e)+'\n')
    print(json.dumps({'trials':m['trials'],'review_verified':False}))
    if failed:p.exit(2,'Execution incomplete; inspect receipts, do not promote.\n')


if __name__=='__main__':main()
