#!/usr/bin/env python3
"""Exercise the retained mesh-map CLI, not source-text assertions."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from PIL import Image

SCRIPT = Path(__file__).with_name('tile_grid.py')


class GridCompatibility(unittest.TestCase):
    def run_cli(self, *args):
        subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                       check=True, capture_output=True, text=True)

    def fixture(self, root, overlap=2):
        source = Image.new('RGB', (12, 8))
        source.putdata([(x * 17, y * 29, (x + y) * 9)
                        for y in range(8) for x in range(12)])
        image = root / 'source.png'
        source.save(image)
        tiles = root / 'tiles'
        self.run_cli('split', '--input', image, '--out', tiles,
                     '--n', 2, '--overlap', overlap)
        return source, tiles

    def test_divisible_rgb_roundtrip_with_and_without_overlap(self):
        for overlap in (0, 2):
            with self.subTest(overlap=overlap), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                source, tiles = self.fixture(root, overlap)
                self.assertEqual(len(list(tiles.glob('input-*.png'))), 4)
                output = root / 'stitched.png'
                self.run_cli('stitch', '--tiles', tiles, '--out', output,
                             '--n', 2, '--overlap', overlap)
                with Image.open(output) as actual:
                    self.assertEqual(actual.size, source.size)
                    self.assertEqual(actual.tobytes(), source.tobytes())

    def test_restored_tile_takes_precedence_and_other_cores_survive(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            source, tiles = self.fixture(root)
            Image.new('RGB', (10, 8), 'red').save(tiles / 'tile-00.png')
            output = root / 'restored.png'
            self.run_cli('stitch', '--tiles', tiles, '--out', output,
                         '--n', 2, '--overlap', 2)
            source.paste(Image.new('RGB', (6, 4), 'red'), (0, 0))
            with Image.open(output) as actual:
                self.assertEqual(actual.tobytes(), source.tobytes())

    def test_uniform_upscale_requires_scaled_overlap(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            source, tiles = self.fixture(root)
            for original in tiles.glob('input-*.png'):
                with Image.open(original) as tile:
                    tile.resize((tile.width * 2, tile.height * 2),
                                Image.Resampling.NEAREST).save(
                                    tiles / original.name.replace('input-', 'tile-'))
            output = root / 'upscaled.png'
            self.run_cli('stitch', '--tiles', tiles, '--out', output,
                         '--n', 2, '--overlap', 4)
            expected = source.resize((24, 16), Image.Resampling.NEAREST)
            with Image.open(output) as actual:
                self.assertEqual(actual.size, expected.size)
                self.assertEqual(actual.tobytes(), expected.tobytes())


if __name__ == '__main__':
    unittest.main()
