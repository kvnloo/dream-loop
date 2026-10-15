#!/usr/bin/env python3
"""Read-only dispatch guard: exit 0 allowed, 3 STOP, 2 invalid evidence.

Use stable scoped defect IDs. Run before dispatch; never change an ID to evade the
budget. Owner restart receipts must be authenticated by the orchestrator: a file
hash binds bytes, it does NOT prove who authorized them. Serialize ledger writers.
"""
import argparse
import hashlib
import json
from pathlib import Path


def check(ledger,defect_id):
    ledger=Path(ledger);states={};seen=set()
    for line in ledger.read_text().splitlines():
        if not line.strip():continue
        row=json.loads(line)
        if not isinstance(row,dict):raise ValueError('record must be an object')
        defect=row['defect_id']
        if not isinstance(defect,str) or not defect.strip():raise ValueError('defect ID required')
        s=states.setdefault(defect,{'failed':[],'unknown':[],'cleared':False})
        if row['event']=='trial':
            ident=row['trial_id']
            if not isinstance(ident,str) or not ident.strip() or ident in seen:raise ValueError('invalid/duplicate trial ID')
            seen.add(ident)
            if not isinstance(row['family'],str) or not row['family'].strip():raise ValueError('family required')
            if not isinstance(row['evidence'],list) or not row['evidence'] or not all(isinstance(x,str) and x.strip() for x in row['evidence']):raise ValueError('evidence required')
            outcome=row['outcome']
            if outcome not in {'unresolved','cleared','technical_failure','unknown'}:raise ValueError('unknown trial outcome')
            if len(s['failed'])>=2 or s['unknown'] or s['cleared']:raise ValueError('trial dispatched while STOP; owner restart required')
            if outcome in {'unresolved','technical_failure'}:s['failed'].append(ident)
            elif outcome=='unknown':s['unknown'].append(ident)
            else:s['cleared']=True
        elif row['event']=='owner_restart':
            if row['after_trial_ids']!=s['failed']+s['unknown'] or not row['after_trial_ids']:
                raise ValueError('restart must name exact consumed trial IDs')
            receipt=row['receipt'];path=Path(receipt['path'])
            if not path.is_absolute():path=ledger.parent/path
            if hashlib.sha256(path.read_bytes()).hexdigest()!=receipt['sha256']:raise ValueError('owner receipt hash mismatch')
            s.update(failed=[],unknown=[],cleared=False)
        else:raise ValueError('unknown event')
    s=states.get(defect_id,{'failed':[],'unknown':[],'cleared':False})
    stop=len(s['failed'])>=2 or bool(s['unknown']) or s['cleared']
    return dict(defect_id=defect_id,dispatch='STOP' if stop else 'allowed',
                failed_trial_ids=s['failed'],unknown_trial_ids=s['unknown'],cleared=s['cleared'],
                reason='two failures, unresolved evidence, or already cleared; owner checkpoint required' if stop else 'within recorded budget',
                authority_limit='hash integrity only; orchestrator must verify actual owner authorization and scoped preferences')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('ledger');p.add_argument('defect_id');a=p.parse_args()
    try:r=check(a.ledger,a.defect_id)
    except (OSError,ValueError,TypeError,KeyError) as e:p.exit(2,str(e)+'\n')
    print(json.dumps(r))
    if r['dispatch']=='STOP':p.exit(3)


if __name__=='__main__':main()
