"""Fictional source records exercise the public chat import boundary."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import meta_loop as ml


class ImporterTests(unittest.TestCase):
    def test_validated_atomic_idempotent_import_and_conflict(self):
        self.assertIsNotNone(importlib.util.find_spec('import_chat'), 'generic chat importer missing')
        import import_chat
        with tempfile.TemporaryDirectory() as folder:
            data = Path(folder)
            (data/'events').mkdir()
            row = ml.blank_trial('fixture-1', 'sample', 'sample-panel')
            (data/'events/sample.jsonl').write_text(json.dumps(row)+'\n')
            source = data/'source.jsonl'
            label = dict(event='owner_label', schema_version=1, event_id='fixture-chat-1',
                trial_id='fixture-1', element='sample-panel', timestamp='2026-01-01T00:00:00Z',
                source='chat-backfill', status='backfilled', scope='component', aspect='edges',
                verdict='maybe', stars=None, quote='Fictional sample feedback for testing.',
                source_receipt=dict(kind='fixture', path='fixture.jsonl', session_id='fiction', message_id='1'),
                defect_id=None, mapping_confidence='high', mapping_evidence=[])
            source.write_text(json.dumps(label)+'\n')
            self.assertEqual(import_chat.import_labels(data, source, commit=False)['added'], 1)
            self.assertFalse((data/'events/owner.jsonl').exists())
            self.assertEqual(import_chat.import_labels(data, source, commit=True)['added'], 1)
            self.assertEqual(import_chat.import_labels(data, source, commit=True)['added'], 0)
            before = (data/'events/owner.jsonl').read_bytes()
            changed = dict(label, quote='Another fictional test comment.')
            source.write_text(json.dumps(changed)+'\n')
            with self.assertRaises(ValueError):
                import_chat.import_labels(data, source, commit=True)
            self.assertEqual((data/'events/owner.jsonl').read_bytes(), before)
            source.write_text(json.dumps(dict(label, event_id='invalid', trial_id='unknown'))+'\n')
            with self.assertRaises(ValueError):
                import_chat.import_labels(data, source, commit=True)
            self.assertEqual((data/'events/owner.jsonl').read_bytes(), before)
            # No arbitrary source record is guessed into a label.
            source.write_text('{"text":"sample"}\n')
            with self.assertRaises(ValueError):
                import_chat.import_labels(data, source, commit=True)
            adapter = data/'source_adapter.py'
            adapter.write_text('def read_chat_labels(path):\n    return '+repr([dict(label, event_id='fixture-chat-2')])+'\n')
            with patch.dict(os.environ, DREAM_LOOP_ADAPTER=str(adapter)):
                self.assertEqual(import_chat.import_labels(data, source, commit=True)['added'], 1)


if __name__ == '__main__': unittest.main()
