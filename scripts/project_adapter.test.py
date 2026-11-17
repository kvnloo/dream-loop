"""Fictional adapter fixtures; no real project data is loaded."""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import meta_loop as ml


class AdapterTests(unittest.TestCase):
    def test_default_report_has_only_observed_elements(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {}, clear=True):
            data = Path(folder)
            ml.publish_materialized(data, [ml.blank_trial('fixture-1', 'sample', 'sample-panel')], [])
            self.assertEqual(sorted(p.name for p in data.glob('next-*.json')), ['next-sample-panel.json'])

    def test_external_adapter_is_explicit_and_invalid_path_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'adapter.py'
            path.write_text("def mechanism_key(row): return 'generated_vector'\n")
            row = ml.blank_trial('fixture-1', 'sample', 'sample-panel', 'traced_vector')
            with patch.dict(os.environ, DREAM_LOOP_ADAPTER=str(path)):
                self.assertEqual(ml.mechanism_key(row), 'generated_vector')
                self.assertEqual(row['mechanism_class'], 'traced_vector')
            with patch.dict(os.environ, DREAM_LOOP_ADAPTER=str(path)+'-missing'):
                with self.assertRaises((ValueError, FileNotFoundError)):
                    ml.mechanism_key(row)


    def test_fictional_source_and_live_catalog(self):
        import json
        import live_rating
        import owner_rating
        from synthetic_fixture import png
        adapter = Path(__file__).resolve().parents[1]/'examples/paper_lamp_adapter.py'
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, DREAM_LOOP_ADAPTER=str(adapter)):
            data = Path(folder)
            (data/'events').mkdir()
            raw = dict(event='sample_trial', trial_id='fixture-1', element='paper-lamp', mechanism_class='geometry')
            (data/'samples.jsonl').write_text(json.dumps(raw)+'\n')
            rows, anchors = ml.import_history(data)
            self.assertEqual(rows[0]['source']['raw'], raw)
            self.assertEqual(rows[0]['owner_reaction']['status'], 'not_reviewed')
            self.assertIsNone(rows[0]['timestamp'])
            self.assertEqual(anchors, [])
            row = ml.blank_trial('fixture-2', 'sample-lab', 'paper-lamp', 'geometry')
            image, target = data/'render.png', data/'target.png'
            png(image); png(target)
            row['artifacts'] = [dict(path=str(p), sha256=ml.digest(p)) for p in (image,target)]
            row['metrics']['review_views'] = [dict(path=str(image),target=str(target),mode='look')]
            lane = data/'events/sample-lab.jsonl'
            lane.write_text(json.dumps(row)+'\n')
            (data/'ledger.json').write_text('[]')
            (data/'rating-catalog.json').write_text(json.dumps(dict(candidates=[],assets={},history=[])))
            app = owner_rating.RatingApp(data)
            self.assertTrue(app.poll(now=app.watch_start), app.poll_status)
            self.assertEqual(app.catalog['candidates'][0]['trial_id'], 'fixture-2')
            self.assertIn('look',app.catalog['candidates'][0]['views'][0])
            self.assertFalse((data/'events/owner.jsonl').exists())
            # A partial producer tail keeps the last usable queue.
            with lane.open('a') as stream: stream.write('{')
            self.assertFalse(app.poll(now=app.watch_start+900))
            self.assertEqual(len(app.catalog['candidates']),1)
            lane.write_text(json.dumps(row)+'\n')
            png(image,21,30)
            self.assertFalse(app.poll(now=app.watch_start+1800))
            self.assertIn('hash-bound',app.poll_status['error'])
            self.assertFalse(app.poll(now=app.watch_start+14401))
            self.assertFalse(app.poll_status['active'])


if __name__ == '__main__':
    unittest.main()
