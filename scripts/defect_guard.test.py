"""Exercise dispatch stopping against immutable trial records."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT=Path(__file__).with_name('defect_guard.py')

class Guard(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='defect-guard-');self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.ledger=self.root/'defects.jsonl'
    def write(self,rows):self.ledger.write_text(''.join(json.dumps(x)+'\n' for x in rows))
    def run_guard(self):return subprocess.run([sys.executable,str(SCRIPT),str(self.ledger),'stone-form'],capture_output=True,text=True)
    def trial(self,i,outcome='unresolved'):
        return dict(event='trial',trial_id=f't{i}',defect_id='stone-form',family=f'renamed-{i}',outcome=outcome,evidence=['crop.png'])
    def test_two_failures_stop_even_when_hypothesis_is_renamed(self):
        self.write([self.trial(1)])
        p=self.run_guard();self.assertEqual(p.returncode,0,p.stderr)
        self.write([self.trial(1),self.trial(2)])
        p=self.run_guard();self.assertEqual(p.returncode,3,p.stderr)
        self.assertEqual(json.loads(p.stdout)['failed_trial_ids'],['t1','t2'])
    def test_restart_requires_bound_evidence_and_exact_consumed_trials(self):
        decision=self.root/'owner.md';decision.write_text('Owner authorizes one new family after reviewing t1/t2.')
        reset=dict(event='owner_restart',defect_id='stone-form',after_trial_ids=['t1','t2'],
                   receipt={'path':'owner.md','sha256':hashlib.sha256(decision.read_bytes()).hexdigest()})
        self.write([self.trial(1),self.trial(2),reset])
        p=self.run_guard();self.assertEqual(p.returncode,0,p.stderr)
        decision.write_text('Changed without receipt update')
        self.assertEqual(self.run_guard().returncode,2)
    def test_unscored_and_duplicate_records_fail_closed(self):
        self.write([self.trial(1,'unknown')]);self.assertEqual(self.run_guard().returncode,3)
        self.write([self.trial(1),self.trial(1)]);self.assertEqual(self.run_guard().returncode,2)
        self.ledger.write_text('{broken');self.assertEqual(self.run_guard().returncode,2)

if __name__=='__main__':unittest.main()
