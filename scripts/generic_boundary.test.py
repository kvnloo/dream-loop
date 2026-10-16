"""The public runtime has no implicit scene, lane, or UI queue identity."""
from pathlib import Path
import unittest


class BoundaryTests(unittest.TestCase):
    def test_ui_queues_come_from_catalog(self):
        text = Path(__file__).with_name('owner-rating.js').read_text()
        self.assertIn('data.queue_labels', text)
        self.assertIn('data.candidates', text)
        self.assertIn('c.queues', text)
        self.assertNotIn("queue = 'banner'", text)


if __name__ == '__main__': unittest.main()
