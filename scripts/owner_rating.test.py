#!/usr/bin/env python3
import json
from pathlib import Path
import tempfile
import unittest
import meta_loop as ml


class OwnerIngestion(unittest.TestCase):
    def test_ingest_owner_accept_then_correction_without_duplicate_trials(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)
            (data/'events').mkdir()
            trial = ml.blank_trial('trial-A', 'lane', 'sample-panel', 'traced_vector')
            (data/'events/lane.jsonl').write_text(json.dumps(trial)+'\n')
            label = dict(event='owner_label', schema_version=1, event_id='label-1',
                         trial_id='trial-A', element='sample-panel', verdict='accept', stars=4,
                         pairwise=None, note='synthetic temporary test only', timestamp=ml.now(),
                         source='owner-ui', status='confirmed', scope='trial')
            (data/'events/owner.jsonl').write_text(json.dumps(label)+'\n')
            rows, errors = ml.ingest(data)
            self.assertEqual(errors, [])
            self.assertEqual(len(rows), 1)
            self.assertEqual(ml.owner_outcome(rows[0]), 1)
            self.assertEqual(ml.plan(rows, 'sample-panel', {})['learned_best'], 'traced_vector')
            label.update(event_id='label-2', verdict='maybe', stars=3)
            with (data/'events/owner.jsonl').open('a') as f:
                f.write(json.dumps(label)+'\n')
            rows, errors = ml.ingest(data)
            self.assertEqual(errors, [])
            self.assertIsNone(ml.owner_outcome(rows[0]))
            self.assertEqual(len(rows[0]['owner_label_history']), 2)


    def test_http_append_is_idempotent_and_refreshes_real_payoff(self):
        import importlib.util
        self.assertIsNotNone(importlib.util.find_spec('owner_rating'), 'rating server module missing')
        import owner_rating as ui
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)
            (data/'events').mkdir()
            trial = ml.blank_trial('trial-A', 'lane', 'sample-panel', 'traced_vector')
            (data/'events/lane.jsonl').write_text(json.dumps(trial)+'\n')
            ml.ingest(data)
            (data/'rating-catalog.json').write_text(json.dumps({'candidates': [], 'history': [], 'assets': {}}))
            app = ui.RatingApp(data)
            label = dict(judged_on='clear', event_id='request-1', trial_id='trial-A', element='sample-panel',
                         verdict='accept', stars=5, note='temporary test', pairwise=None)
            result = app.submit(label)
            self.assertEqual(result['next']['learned_best'], 'traced_vector')
            self.assertEqual(app.submit(label)['event']['event_id'], 'request-1')
            self.assertEqual(len((data/'events/owner.jsonl').read_text().splitlines()), 1)
            label['stars'] = 1
            with self.assertRaises(ValueError):
                app.submit(label)
            rows, errors = ml.ingest(data)
            self.assertEqual(errors, [])
            self.assertEqual(ml.owner_outcome(rows[0]), 1)


    def test_history_never_guesses_from_timestamps_or_feedback_keywords(self):
        import importlib.util
        self.assertIsNotNone(importlib.util.find_spec('seed_owner_rating'), 'seed importer missing')
        import seed_owner_rating as seed
        rows = [ml.blank_trial('trial-A', 'lane', 'sample-panel')]
        anchors = [dict(id='owner:1', quote='looks good', date=ml.now(), linked_nodes=['trial-A'], scope='banner'),
                   dict(id='owner:2', quote='looks good', date=ml.now(), linked_nodes=[])]
        result = seed.infer_history(rows, anchors, {})
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['status'], 'inferred')
        self.assertEqual(result[0]['trial_ids'], ['trial-A'])
        self.assertEqual(result[1]['status'], 'unresolved')
        self.assertEqual(result[1]['trial_ids'], [])


    def test_http_serves_app_and_rejects_foreign_origin(self):
        import owner_rating as ui
        import threading
        import urllib.request
        import urllib.error
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)
            (data/'rating-catalog.json').write_text(json.dumps({'candidates': [], 'history': [], 'assets': {}}))
            app = ui.RatingApp(data)
            server = ui.make_server(app, 0)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base = 'http://127.0.0.1:'+str(server.server_port)
            try:
                try:
                    with urllib.request.urlopen(base) as response:
                        text = response.read().decode()
                except Exception as exc:
                    self.fail('App not served: '+str(exc))
                self.assertIn('Owner review', text)
                for path in ('/app.js', '/app.css', '/health'):
                    with urllib.request.urlopen(base+path) as response:
                        self.assertEqual(response.status, 200)
                request = urllib.request.Request(base+'/api/label', data=b'{}',
                    headers={'Origin': 'https://evil.invalid', 'X-Owner-Token': app.token, 'Content-Type':'application/json'})
                with self.assertRaises(urllib.error.HTTPError) as error:
                    urllib.request.urlopen(request)
                self.assertEqual(error.exception.code, 403)
                error.exception.close()
                self.assertFalse((data/'events/owner.jsonl').exists())
            finally:
                server.shutdown()
                server.server_close()
                thread.join()


    def test_history_matches_identical_image_hash_and_known_round_directory(self):
        import seed_owner_rating as seed
        rows = [ml.blank_trial('fixture-A', 'history', 'sample-one'), ml.blank_trial('fixture-B', 'history', 'sample-two')]
        raw = {'fixture-A': {'artifacts':[{'path':'/fictional/a/scene.png','sha256':'a'*64}]},
               'fixture-B': {'artifacts':[{'path':'/fictional/b/full.png','sha256':'b'*64}]}}
        anchors = [dict(id='owner:1',quote='Fictional preference A',images=[dict(path='/fictional/a/detail.png',role='candidate')]),
                   dict(id='owner:2',quote='Fictional preference B',images=[dict(path='/fictional/full.png',role='reviewed_context',sha256='b'*64)])]
        result = seed.infer_history(rows, anchors, raw)
        self.assertEqual(result[0]['trial_ids'], ['fixture-A'])
        self.assertEqual(result[1]['trial_ids'], ['fixture-B'])


    def test_pairwise_and_component_feedback_are_not_acceptance(self):
        a = ml.blank_trial('A', 'lane', 'sample-panel', 'traced_vector')
        b = ml.blank_trial('B', 'lane', 'sample-panel', 'geometry')
        label = dict(event='owner_label', schema_version=1, event_id='label-1', trial_id='A',
                     element='sample-panel', verdict='accept', stars=4, note='sample corner only',
                     timestamp=ml.now(), source='owner-ui', status='confirmed', scope='component',
                     pairwise={'other_trial_id':'B','preference':'candidate'})
        rows, errors = ml.apply_owner_labels([a,b], [label], '/test/owner.jsonl')
        self.assertEqual(errors, [])
        self.assertIsNone(ml.owner_outcome(rows[0]))
        self.assertFalse(ml.eligible_recipe(rows[0], {}))
        stats = ml.learn(rows, {})['sample-panel']['traced_vector']
        self.assertEqual(stats['owner_accept']['n'], 0)
        self.assertEqual(stats.get('owner_preference', {}).get('n'), 1)
        label['status'] = 'inferred'
        rejected, errors = ml.apply_owner_labels([a,b], [label], '/test/owner.jsonl')
        self.assertTrue(errors)
        self.assertIsNone(ml.owner_outcome(rejected[0]))


    def test_invalid_labels_do_not_append_and_parallel_retries_append_once(self):
        import owner_rating as ui
        from concurrent.futures import ThreadPoolExecutor
        with tempfile.TemporaryDirectory() as tmp:
            data=Path(tmp)
            (data/'events').mkdir()
            trial=ml.blank_trial('A','lane','sample-panel','traced_vector')
            (data/'events/lane.jsonl').write_text(json.dumps(trial)+'\n')
            ml.ingest(data)
            (data/'rating-catalog.json').write_text(json.dumps({'candidates':[],'history':[],'assets':{}}))
            app=ui.RatingApp(data)
            valid=dict(judged_on='clear', event_id='once',trial_id='A',element='sample-panel',verdict='accept',stars=4,note='',pairwise=None)
            for change in ({'stars':0},{'stars':True},{'stars':6},{'verdict':'approved'},
                           {'trial_id':'missing'},{'element':'sample-base'},
                           {'pairwise':{'other_trial_id':'A','preference':'candidate'}},
                           {'history_id':'missing'}):
                with self.subTest(change=change), self.assertRaises(ValueError):
                    app.submit(dict(valid,**change))
            self.assertFalse((data/'events/owner.jsonl').exists())
            with ThreadPoolExecutor(max_workers=4) as executor:
                results=list(executor.map(lambda _:app.submit(valid), range(4)))
            self.assertTrue(all(r['saved'] for r in results))
            self.assertEqual(len((data/'events/owner.jsonl').read_text().splitlines()),1)
            self.assertEqual(json.loads((data/'summary.json').read_text())['owner_accept_observations'],1)
            with (data/'events/owner.jsonl').open('a') as f:
                f.write('{"partial":')
            before=(data/'events/owner.jsonl').read_bytes()
            with self.assertRaises(ValueError):
                app.submit(dict(valid,event_id='second'))
            self.assertEqual(before,(data/'events/owner.jsonl').read_bytes())

    def test_nonobject_labels_and_unterminated_complete_record_fail_closed(self):
        import owner_rating as ui
        trial=ml.blank_trial('A','lane','sample-panel','traced_vector')
        rows,errors=ml.apply_owner_labels([trial], [None, [], 'bad'], '/test/owner.jsonl')
        self.assertEqual(len(errors),3)
        self.assertIsNone(ml.owner_outcome(rows[0]))
        with tempfile.TemporaryDirectory() as tmp:
            data=Path(tmp)
            (data/'events').mkdir()
            (data/'events/lane.jsonl').write_text(json.dumps(trial)+'\n')
            ml.ingest(data)
            (data/'rating-catalog.json').write_text(json.dumps({'candidates':[],'history':[],'assets':{}}))
            app=ui.RatingApp(data)
            payload=dict(judged_on='clear', event_id='once',trial_id='A',element='sample-panel',verdict='accept',stars=4)
            app.submit(payload)
            path=data/'events/owner.jsonl'
            path.write_bytes(path.read_bytes().rstrip(b'\n'))
            before=path.read_bytes()
            with self.assertRaises(ValueError):
                app.submit(dict(payload,event_id='twice'))
            self.assertEqual(path.read_bytes(),before)


if __name__ == '__main__':
    unittest.main()
