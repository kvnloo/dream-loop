#!/usr/bin/env python3
"""Run all offline helper tests and lint; retain each exit code, fail on any failure."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--test-dir',type=Path,default=Path(__file__).resolve().parent)
    p.add_argument('--no-lint',action='store_true');p.add_argument('--receipt',type=Path)
    a=p.parse_args();folder=a.test_dir.resolve()
    if a.receipt and a.receipt.exists():p.exit(2,'receipt exists; choose a new name\n')
    commands=[]
    for f in sorted(folder.glob('*.test.py')):commands.append(([sys.executable,str(f)],f))
    for f in sorted(folder.glob('*.test.mjs')):commands.append((['node','--test',str(f)],f))
    if not commands:p.exit(2,'No tests discovered\n')
    if not a.no_lint:
        f=Path(__file__).with_name('lint_skill.py');commands.append(([sys.executable,str(f)],f))
    runs=[]
    for argv,source in commands:
        print('\n=== '+' '.join(argv)+' ===',flush=True);start=time.monotonic()
        try:
            r=subprocess.run(argv,cwd=folder.parent,capture_output=True,text=True,timeout=180,check=False)
            code=r.returncode;output=r.stdout+r.stderr
        except (OSError,subprocess.TimeoutExpired) as e:
            code=124 if isinstance(e,subprocess.TimeoutExpired) else 127;output=str(e)
        print(output,flush=True)
        runs.append({'argv':argv,'exit_code':code,'elapsed_seconds':time.monotonic()-start,
                     'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'output':output})
    result={'started_suite_at':datetime.now(timezone.utc).isoformat(),'ok':all(r['exit_code']==0 for r in runs),'runs':runs}
    if a.receipt:
        a.receipt.parent.mkdir(parents=True,exist_ok=True)
        with a.receipt.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({'ok':result['ok'],'commands':len(runs),'failed':sum(r['exit_code']!=0 for r in runs)}))
    raise SystemExit(0 if result['ok'] else 1)


if __name__=='__main__':main()
