"""Synthetic algorithm checks, not a new target-family calibration."""
import importlib.util
from pathlib import Path
import unittest
import numpy as np
from PIL import Image, ImageDraw

spec=importlib.util.spec_from_file_location('structure_gate',Path(__file__).with_name('structure_gate.py'))
assert spec is not None and spec.loader is not None
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)

class Structure(unittest.TestCase):
    def test_last_tile_includes_right_and_bottom_edges(self):
        a=np.zeros((100,100),dtype=bool);a[90:99,90:99]=True
        count,origin=g._worst_tile(a,48)
        self.assertEqual(count,81)
        self.assertEqual(origin,(52,52))

    def test_identity_shift_and_mask(self):
        t=Image.new('RGB',(256,256),'black');ImageDraw.Draw(t).rectangle((40,40,100,210),fill='white')
        c=Image.new('RGB',t.size,'black');ImageDraw.Draw(c).rectangle((140,40,200,210),fill='white')
        self.assertTrue(g.gate(t,t)['ok'])
        self.assertFalse(g.gate(t,c)['ok'])
        mask=np.zeros((256,256),dtype=bool);mask[20:230,20:220]=True
        self.assertTrue(g.gate(t,c,mask=mask)['ok'])

if __name__=='__main__':unittest.main()
