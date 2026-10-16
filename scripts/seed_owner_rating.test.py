"""Catalog seeding uses only explicitly supplied synthetic manifest data."""
import json
from pathlib import Path
import tempfile
import unittest

import meta_loop as ml
import seed_owner_rating as seed
from synthetic_fixture import png


class ManifestSeed(unittest.TestCase):
    def test_seed_reads_only_manifest_and_existing_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / 'data'
            data.mkdir()
            image = root / 'synthetic.png'
            png(image)
            trial = ml.blank_trial('sample-A', 'synthetic', 'sample-panel')
            trial['artifacts'] = [dict(path=str(image), sha256=ml.digest(image))]
            ml.write_json(data / 'ledger.json', [trial])
            manifest = root / 'catalog-input.json'
            ml.write_json(manifest, dict(candidates=[dict(trial_id='sample-A', queue='banner',
                title='Synthetic panel', views=[dict(path='synthetic.png', target='synthetic.png',
                kind='hero', region='sample')])], anchors=[dict(id='synthetic-receipt',
                quote='Synthetic feedback only.', linked_nodes=['sample-A'])]))
            result = seed.seed(data, manifest)
            self.assertEqual(result['counts'], {'banner': 1})
            catalog = json.loads((data / 'rating-catalog.json').read_text())
            self.assertEqual(catalog['candidates'][0]['trial_id'], 'sample-A')
            self.assertEqual(catalog['history'][0]['suggested_verdict'], 'maybe')
            self.assertEqual(catalog['history'][0]['trial_ids'], ['sample-A'])
            self.assertFalse((data / 'events').exists())
            self.assertEqual(json.loads((data / 'ledger.json').read_text()), [trial])

    def test_seed_rejects_unknown_trial_without_writing_catalog(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)
            ml.write_json(data / 'ledger.json', [])
            manifest = data / 'manifest.json'
            ml.write_json(manifest, dict(candidates=[dict(trial_id='missing')]))
            with self.assertRaisesRegex(ValueError, 'unique existing trials'):
                seed.seed(data, manifest)
            self.assertFalse((data / 'rating-catalog.json').exists())

    def test_seed_requires_explicit_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / 'data'
            data.mkdir()
            with self.assertRaisesRegex(ValueError, 'manifest'):
                seed.seed(data)
            self.assertEqual(list(data.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
