"""Temporary synthetic fixtures only; not visual production evidence."""
import ast
from pathlib import Path
import subprocess
import sys
import tempfile
from PIL import Image, ImageDraw

repo = Path(__file__).resolve().parent.parent
with tempfile.TemporaryDirectory(prefix='crop-gate-smoke-') as tmp:
    root = Path(tmp)
    target = Image.new('RGB', (128, 128), 'black')
    ImageDraw.Draw(target).rectangle((20, 20, 55, 100), fill='white')
    target.save(root / 'target.png')
    shifted = Image.new('RGB', target.size, 'black')
    ImageDraw.Draw(shifted).rectangle((70, 20, 105, 100), fill='white')
    shifted.save(root / 'shifted.png')
    blank = Image.new('RGB', target.size, 'black')
    blank.save(root / 'blank.png')
    target.convert('RGBA').save(root / 'rgba.png')
    Image.new('RGB', (64, 64), 'black').save(root / 'small.png')
    cases = [('identical', 'target.png', 'target.png', 0),
             ('shifted sparse edges', 'target.png', 'shifted.png', 2),
             ('missing subject', 'target.png', 'blank.png', 2),
             ('RGBA', 'target.png', 'rgba.png', 0),
             ('blank identical', 'blank.png', 'blank.png', 0),
             ('resize', 'blank.png', 'small.png', 0)]
    failures = []
    for name, a, b, expected in cases:
        out = root / name
        p = subprocess.run([sys.executable, str(repo / 'scripts/crop_gate.py'), str(root/a), str(root/b), str(out)], capture_output=True, text=True)
        print(name, 'exit=', p.returncode, p.stdout.strip(), p.stderr.strip())
        if p.returncode != expected:
            failures.append(name)
        if p.returncode in (0, 2):
            result = ast.literal_eval(p.stdout)
            assert result['ok'] == (p.returncode == 0)
            with Image.open(result['preview']) as preview:
                assert preview.size == target.size
    p = subprocess.run([sys.executable, str(repo/'scripts/crop_gate.py')], capture_output=True, text=True)
    assert p.returncode != 0 and 'usage:' in p.stderr
    p = subprocess.run([sys.executable, str(repo/'scripts/crop_gate.py'), str(root/'missing.png'), str(root/'target.png'), str(root/'invalid')], capture_output=True, text=True)
    assert p.returncode != 0 and not (root/'invalid/crop_gate.png').exists()
    subprocess.run([sys.executable, str(repo/'scripts/overlay.py'), str(root/'target.png'), str(root/'shifted.png'), str(root/'overlay')], check=True)
    for filename, size in [('overlay_50.png', (128,128)), ('overlay_checker.png', (128,128)), ('overlay_side.png', (256,128))]:
        with Image.open(root/'overlay'/filename) as image:
            assert image.size == size
    assert not failures, failures
    print('PASS: 6 gate cases, usage/missing-input checks, 3 overlay artifacts; temporary fixtures removed on exit')
