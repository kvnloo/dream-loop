#!/usr/bin/env python3
"""Disposable fixtures only; never touches the real owner event log."""
import json
from pathlib import Path
import tempfile
import unittest
from synthetic_fixture import png
import meta_loop as ml
import owner_rating as ui


class LiveRating(unittest.TestCase):
    def test_labels_require_and_preserve_judged_on(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)
            (data/'events').mkdir()
            row = ml.blank_trial('A', 'lane', 'sample-panel', 'geometry')
            (data/'ledger.json').write_text(json.dumps([row]))
            (data/'rating-catalog.json').write_text(json.dumps(dict(candidates=[], assets={}, history=[])))
            app = ui.RatingApp(data)
            payload = dict(event_id='test', trial_id='A', element='sample-panel', stars=4, verdict='maybe')
            for value in (None, '', 'unknown', ['look']):
                with self.subTest(value=value), self.assertRaises(ValueError):
                    app.submit(dict(payload, judged_on=value))
            self.assertFalse((data/'events/owner.jsonl').exists())
            for value in ('look', 'clear', 'both'):
                result = app.submit(dict(payload, event_id='test-'+value, judged_on=value))
                self.assertEqual(result['event']['judged_on'], value)
            self.assertEqual([e['judged_on'] for e in ml.read_jsonl(data/'events/owner.jsonl')[0]], ['look', 'clear', 'both'])

    def test_http_does_not_serve_changed_pixels_under_old_asset_identity(self):
        from catalog import Catalog
        import threading
        import urllib.request
        import urllib.error
        with tempfile.TemporaryDirectory() as tmp:
            data=Path(tmp);path=data/'render.png'
            png(path,20,30,(255,0,0))
            catalog=Catalog(data);url=catalog.asset(path)
            (data/'rating-catalog.json').write_text(json.dumps(dict(candidates=[],history=[],assets=catalog.assets)))
            app=ui.RatingApp(data);server=ui.make_server(app,0)
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            try:
                base=f'http://127.0.0.1:{server.server_port}'
                with urllib.request.urlopen(base+url) as response:
                    self.assertEqual(response.status,200)
                png(path,20,30,(0,0,255))
                with self.assertRaises(urllib.error.HTTPError) as error:
                    urllib.request.urlopen(base+url)
                self.assertEqual(error.exception.code,409)
                error.exception.close()
            finally:
                server.shutdown();server.server_close();thread.join()

    def test_replaced_image_gets_new_asset_identity(self):
        from catalog import Catalog
        with tempfile.TemporaryDirectory() as tmp:
            data=Path(tmp);path=data/'render.png'
            png(path,20,30,(255,0,0))
            catalog=Catalog(data);before=catalog.asset(path)
            png(path,20,30,(0,0,255))
            after=catalog.asset(path)
            self.assertNotEqual(before,after)
            self.assertEqual(catalog.assets[after.split('/')[-1]]['sha256'],ml.digest(path))


    def test_rejects_unavailable_judging_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            data=Path(tmp);(data/'events').mkdir()
            (data/'ledger.json').write_text(json.dumps([ml.blank_trial('A','lane','sample-base','geometry')]))
            (data/'rating-catalog.json').write_text(json.dumps(dict(candidates=[dict(trial_id='A',views=[dict(clear='/assets/test')])],history=[],assets={})))
            app=ui.RatingApp(data)
            for mode in ('look','both'):
                with self.assertRaisesRegex(ValueError,'unavailable'):
                    app.submit(dict(event_id='bad',trial_id='A',element='sample-base',stars=4,verdict='maybe',judged_on=mode))
            self.assertFalse((data/'events/owner.jsonl').exists())



if __name__ == '__main__':
    unittest.main()
