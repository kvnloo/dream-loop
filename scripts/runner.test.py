"""Test the suite runner with disposable executable tests."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

class Runner(unittest.TestCase):
    def test_suite_keeps_running_and_propagates_failure(self):
        with tempfile.TemporaryDirectory(prefix='suite-runner-') as tmp:
            root=Path(tmp);(root/'a.test.py').write_text('raise SystemExit(7)\n')
            (root/'b.test.py').write_text("from pathlib import Path\nPath(__file__).with_suffix('.ran').write_text('executed')\n")
            receipt=root/'receipt.json'
            p=subprocess.run([sys.executable,str(Path(__file__).with_name('run_tests.py')),'--test-dir',str(root),'--no-lint','--receipt',str(receipt)],capture_output=True,text=True)
            self.assertEqual(p.returncode,1,p.stderr)
            self.assertTrue((root/'b.test.ran').exists())
            results=json.loads(receipt.read_text())
            self.assertEqual([r['exit_code'] for r in results['runs']],[7,0])
            self.assertFalse(results['ok'])

if __name__=='__main__':unittest.main()
