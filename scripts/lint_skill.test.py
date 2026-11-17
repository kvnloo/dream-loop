"""CLI lint contract: metadata and local links, not model behavior."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

class Lint(unittest.TestCase):
    def test_good_skill_then_invalid_trigger_and_missing_reference(self):
        with tempfile.TemporaryDirectory(prefix='skill-lint-') as tmp:
            root=Path(tmp);(root/'references').mkdir()
            (root/'references/loop.md').write_text('# Loop\n')
            skill=root/'SKILL.md'
            skill.write_text('---\nname: sample\ndescription: Use when testing a visual workflow.\n---\n# Sample\nRead [loop](references/loop.md).\n')
            cmd=[sys.executable,str(Path(__file__).with_name('lint_skill.py')),str(root)]
            p=subprocess.run(cmd,capture_output=True,text=True);self.assertEqual(p.returncode,0,p.stderr+p.stdout)
            skill.write_text('---\nname: sample\ndescription: This is not a trigger.\n---\n[missing](references/missing.md)\n')
            p=subprocess.run(cmd,capture_output=True,text=True);self.assertEqual(p.returncode,1)
            self.assertIn('description',p.stdout);self.assertIn('missing.md',p.stdout)

if __name__=='__main__':unittest.main()
