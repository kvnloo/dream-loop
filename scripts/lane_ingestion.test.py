"""Synthetic regressions for isolated producer diagnostics and strict owner state."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import meta_loop as m


class LaneIsolationTests(unittest.TestCase):
    def test_bad_producer_rows_do_not_block_other_elements(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root/'events').mkdir()
            good = m.blank_trial('fixture-good', 'fixture', 'paper-lamp', 'geometry')
            bad = m.blank_trial('fixture-bad', 'broken', 'clay-vase', 'geometry')
            bad['metrics'] = {}
            lane = root/'events/broken.jsonl'
            lane.write_text('{broken}\nnull\n'+json.dumps(bad)+'\n'+json.dumps(good)+'\n{"trial_id": []}\n{"partial":')
            before = lane.read_bytes()
            for command in ('next', 'dream', 'stuck'):
                args = [] if command == 'stuck' else ['--element', 'paper-lamp']
                proc = subprocess.run([sys.executable, m.__file__, '--data', str(root), command, *args],
                                      capture_output=True, text=True)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                result = json.loads(proc.stdout)
                self.assertTrue(result['ingestion_warnings'])
                self.assertIn('broken.jsonl:3:', '\n'.join(result['ingestion_warnings']))
                if command == 'dream':
                    self.assertEqual(result, json.loads((root/'dream/paper-lamp.json').read_text()))
            self.assertEqual(lane.read_bytes(), before)
            self.assertFalse((root/'ledger.json').exists())
            summary = m.refresh(root)
            self.assertEqual(summary['record_count'], 1)
            plan = json.loads((root/'next-paper-lamp.json').read_text())
            self.assertNotIn('blocked', plan)
            self.assertTrue(plan['ingestion_warnings'])
            self.assertIn('broken.jsonl:3:', (root/'index.html').read_text())

    def test_revisions_conflicts_and_owner_errors_remain_auditable(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root/'events').mkdir()
            row = m.blank_trial('fixture-one', 'fixture', 'paper-lamp', 'geometry')
            bad = dict(row, event_id='partial', metrics={})
            fixed = dict(row, event_id='corrected', status='completed')
            conflict = dict(fixed, element='clay-vase')
            (root/'events/fixture.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in [bad, fixed, conflict]))
            rows, errors = m.ingest(root, persist=False)
            self.assertEqual([r['event_id'] for r in rows], ['corrected'])
            self.assertIn('fixture.jsonl:1: $.metrics: missing required field: max_zoom_texel_density, crop_gate, sharpness', '\n'.join(errors))
            self.assertIn('fixture.jsonl:3: event_id conflict', '\n'.join(errors))
            (root/'events/owner.jsonl').write_text('{broken}\n')
            proc = subprocess.run([sys.executable, m.__file__, '--data', str(root), 'next', '--element', 'paper-lamp'],
                                  capture_output=True, text=True)
            self.assertEqual(proc.returncode, 2)
            self.assertIn('owner.jsonl', proc.stderr)


if __name__ == '__main__':
    unittest.main()
