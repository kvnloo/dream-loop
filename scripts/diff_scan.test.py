"""Deterministic image-only breadth-first diagnostics; no Blender dependency."""
import importlib.util
from pathlib import Path
import unittest
import numpy as np

class ScanTests(unittest.TestCase):
    def test_greenery_missing_is_directional(self):
        path=Path(__file__).with_name('diff_scan.py')
        self.assertTrue(path.exists(), 'diff scanner implementation missing')
        spec=importlib.util.spec_from_file_location('diff_scan',path)
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        target=np.zeros((80,80,3),dtype=np.float32);target[20:60,20:60]=(.08,.4,.1)
        current=np.zeros_like(target)
        r=m.measure(target,current,np.ones((80,80),bool))
        self.assertGreater(r['missing_greenery'],.20)
        self.assertEqual(r['excess_greenery'],0)
        r=m.measure(current,target,np.ones((80,80),bool))
        self.assertGreater(r['excess_greenery'],.20)
        self.assertEqual(r['missing_greenery'],0)

    def test_sharpness_nonnegative_on_large_dark_image(self):
        spec=importlib.util.spec_from_file_location('diff_scan',Path(__file__).with_name('diff_scan.py'))
        assert spec and spec.loader
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        rng=np.random.default_rng(9);a=rng.random((600,400,3))*.1;a[150:500,80:300]=0
        f=m.features(a)
        self.assertGreaterEqual(float(f['sharpness'].min()),0.)

    def test_ui_overlay_does_not_leak_into_presence_metrics(self):
        import tempfile
        from PIL import Image
        spec=importlib.util.spec_from_file_location('diff_scan',Path(__file__).with_name('diff_scan.py'))
        assert spec and spec.loader
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);a=np.zeros((96,64,3),dtype='uint8');a[:24]=255
            Image.fromarray(a).save(p/'target.png');Image.new('RGB',(64,96)).save(p/'current.png')
            mask=np.zeros((96,64),dtype='uint8');mask[:24]=255;Image.fromarray(mask).save(p/'ui.png')
            r=m.scan(p/'target.png',p/'current.png',p/'out',ui_mask=p/'ui.png',cols=1,rows=1)
            self.assertAlmostEqual(r['tiles'][0]['metrics']['target_presence'],0.,places=10)

    def test_invalid_regions_fail_closed(self):
        import tempfile
        from PIL import Image
        spec=importlib.util.spec_from_file_location('diff_scan',Path(__file__).with_name('diff_scan.py'))
        assert spec and spec.loader
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);Image.new('RGB',(64,96)).save(p/'a.png')
            with self.assertRaises(ValueError):m.scan(p/'a.png',p/'a.png',p/'out',cols=0)
            with self.assertRaises(ValueError):m.scan(p/'a.png',p/'a.png',p/'out',semantic=[{'name':'bad','bbox':[-1,0,1,1]}])

    def test_scan_outputs_masked_rankings_and_blur(self):
        import tempfile,json
        from PIL import Image,ImageFilter
        spec=importlib.util.spec_from_file_location('diff_scan',Path(__file__).with_name('diff_scan.py'))
        assert spec and spec.loader
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        self.assertTrue(hasattr(m,'scan'),'scan CLI pipeline missing')
        rng=np.random.default_rng(1);sharp=(rng.random((96,64,3))*255).astype('uint8')
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);Image.fromarray(sharp).save(p/'current.png')
            Image.fromarray(sharp).filter(ImageFilter.GaussianBlur(3)).save(p/'target.png')
            mask=np.zeros((96,64),dtype='uint8');mask[:24]=255;Image.fromarray(mask).save(p/'ui.png')
            result=m.scan(p/'target.png',p/'current.png',p/'out',ui_mask=p/'ui.png',cols=2,rows=3)
            self.assertEqual(len(result['tiles']),6)
            self.assertEqual(result['valid_pixels'],64*72)
            self.assertTrue(any(t['metrics']['excess_sharpness']>0 for t in result['tiles']))
            self.assertTrue((p/'out/DIFF.md').exists())
            self.assertTrue((p/'out/overlay-greenery.png').exists())
            self.assertTrue((p/'out/tiles/000/target-greenery.png').exists())
            self.assertTrue((p/'out/tiles/000/current-sharpness.png').exists())
            self.assertEqual(result['ranked'][0]['score'],max(t['score'] for t in result['ranked']))
            Image.new('RGB',(70,96)).save(p/'bad.png')
            with self.assertRaises(ValueError):m.scan(p/'target.png',p/'bad.png',p/'badout')

if __name__=='__main__':unittest.main()
