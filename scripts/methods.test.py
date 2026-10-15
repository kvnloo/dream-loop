"""Offline synthetic helper contracts, not visual-quality evidence."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from PIL import Image
import numpy as np

SCRIPTS = Path(__file__).resolve().parent

class Methods(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='dream-methods-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for name, color in [('target', 'red'), ('capture', 'blue'), ('parent', 'green')]:
            Image.new('RGB', (103, 79), color).save(self.root / f'{name}.png')

    def run_cli(self, script, *args):
        return subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)],
                              cwd=self.root, capture_output=True, text=True)

    def test_tile_manifest_covers_odd_dimensions_with_native_semantics(self):
        semantic = self.root / 'regions.json'
        semantic.write_text(json.dumps({'regions': [{'id':'face', 'name':'face', 'box':[5,6,30,40]}]}))
        out = self.root / 'tiles'
        p = self.run_cli('tile_splitter.py', self.root/'target.png', self.root/'capture.png', out,
                         '--semantic', semantic, '--cols', 4, '--rows', 6, '--padding', 7)
        self.assertEqual(p.returncode, 0, p.stderr)
        m = json.loads((out/'manifest.json').read_text())
        self.assertEqual(len(m['regions']), 25)
        self.assertTrue(m['native_pair'])
        cover = np.zeros((79,103), dtype=int)
        for row in m['regions']:
            x0,y0,x1,y1 = row['box']
            with Image.open(out/row['target']) as im:
                self.assertEqual(im.size, (x1-x0,y1-y0))
            with Image.open(out/row['capture']) as im:
                self.assertEqual(im.getpixel((0,0)), (0,0,255))
            if row['layer']=='grid':
                a,b,c,d = row['core_box']; cover[b:d,a:c] += 1
                self.assertLessEqual(x0,a); self.assertGreaterEqual(x1,c)
        self.assertTrue(np.all(cover==1))
        self.assertEqual(m['coverage']['pixels'], 103*79)
        self.assertEqual(m['regions'][0]['box'], [5,6,30,40])
        self.assertEqual(len(m['inputs']['target']['sha256']), 64)

    def test_aggregate_deduplicates_defects_without_inventing_blocked_totals(self):
        out = self.root/'tiles'
        self.assertEqual(self.run_cli('tile_splitter.py', self.root/'target.png', self.root/'capture.png', out,
                                     '--cols',1,'--rows',2).returncode,0)
        m = json.loads((out/'manifest.json').read_text())
        vd = self.root/'verdicts'; vd.mkdir()
        gap = dict(element='dial',defect='flat coating',change_class='material',action='test coat',
                   evidence='highlight absent',protected=False)
        for i,r in enumerate(m['regions']):
            v = dict(id=r['id'],box=r['box'],brief_revision='brief-v1',alignment='blocked' if i else 'pass',
                     scores=dict(composition=2,lighting=None if i else 2,materials=None if i else 1,
                                 details=None if i else .5,total=None if i else 5.5),
                     gaps=[gap,gap],preserve=['layout'],tiers=[])
            (vd/(r['id']+'.json')).write_text(json.dumps(v))
        report = self.root/'report.json'
        p = self.run_cli('aggregate_verdicts.py',out/'manifest.json',vd,report)
        self.assertEqual(p.returncode,0,p.stderr)
        a = json.loads(report.read_text())
        self.assertEqual(a['counts'],dict(expected=2,valid=2,skipped=0,missing=0,invalid=0))
        self.assertEqual(a['category_means']['total'],dict(mean=5.5,n=1))
        self.assertEqual(a['fixes'][0]['tile_count'],2)
        self.assertEqual(a['fixes'][0]['scored_severity'],4.5)
        self.assertEqual(len(a['blocked']),1)
        self.assertFalse(a['review_verified'])

    def test_compare_sheet_preserves_native_pixels_and_source_hashes(self):
        output=self.root/'compare.png'
        p=self.run_cli('compare_sheet.py',output,self.root/'target.png',self.root/'parent.png',
                       self.root/'capture.png','--labels','TARGET','PARENT','CANDIDATE',
                       '--box','5','6','30','40')
        self.assertEqual(p.returncode,0,p.stderr)
        with Image.open(output) as im:
            self.assertEqual(im.size,(75,62))
            self.assertEqual(im.getpixel((2,30)),(255,0,0))
            self.assertEqual(im.getpixel((27,30)),(0,128,0))
            self.assertEqual(im.getpixel((52,30)),(0,0,255))
        receipt=json.loads(output.with_suffix('.json').read_text())
        self.assertTrue(receipt['native'])
        self.assertEqual(len(receipt['inputs']),3)
        self.assertEqual(self.run_cli('compare_sheet.py',output,self.root/'target.png').returncode,2)

    def test_ab_runner_swaps_anonymous_images_and_retains_process_receipts(self):
        brief=self.root/'BRIEF.md';brief.write_text('Approved deviation: keep dial wording.')
        preferences=self.root/'OWNER-PREFERENCES.md';preferences.write_text('LOCK: lettering. No paint-over.')
        fake=self.root/'hermes-test.py'
        fake.write_text('import json,sys\nprint(json.dumps({"type":"test_receipt","argv":sys.argv[1:]}))\n')
        out=self.root/'judges'
        p=self.run_cli('ab_judge.py',self.root/'target.png',self.root/'parent.png',self.root/'capture.png',
                       brief,out,'--preferences',preferences,'--provider','test','--model','test-model','--hermes',sys.executable,'--hermes-arg',fake,'--execute')
        self.assertEqual(p.returncode,0,p.stderr)
        for name,colors in [('trial-1',[(0,128,0),(0,0,255)]),('trial-2',[(0,0,255),(0,128,0)])]:
            for label,color in zip(['A','B'],colors):
                with Image.open(out/name/(label+'.png')) as im:self.assertEqual(im.getpixel((0,0)),color)
            receipt=json.loads((out/name/'receipt.json').read_text())
            self.assertEqual(receipt['exit_code'],0)
            self.assertEqual(receipt['status'],'executed-needs-evidence-audit')
            event=json.loads((out/name/'stream.jsonl').read_text())
            self.assertIn('file,vision',event['argv']);self.assertIn('--safe-mode',event['argv'])
            prompt=(out/name/'prompt.md').read_text()
            self.assertIn('Approved deviation: keep dial wording.',prompt)
            self.assertIn('LOCK: lettering. No paint-over.',prompt)
            self.assertNotIn('{{OWNER_PREFERENCES}}',prompt)
            self.assertNotIn(str(self.root/'parent.png'),prompt)
        manifest=json.loads((out/'manifest.json').read_text())
        self.assertFalse(manifest['review_verified'])
        self.assertEqual(manifest['mapping']['trial-2']['B'],'parent')

    def test_integration_adapter_orders_layers_and_reopens_before_render(self):
        import importlib.util
        path=SCRIPTS.parent/'templates/integrate.py'
        self.assertTrue(path.exists(),'integration adapter template missing')
        spec=importlib.util.spec_from_file_location('integration_template',path)
        assert spec is not None and spec.loader is not None
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        fixture=self.root/'base.json';fixture.write_text('{"protected":42,"order":[]}')
        class Adapter:
            def load(self,path):return json.loads(Path(path).read_text())
            def guard(self,state):return state['protected']
            def apply(self,state,layer):
                if layer['id'] not in state['order']:state['order'].append(layer['id'])
            def fingerprint(self,state):return json.dumps(state,sort_keys=True)
            def save(self,state,path):Path(path).write_text(json.dumps(state))
            def render(self,state,path):
                Path(path).write_text('|'.join(state['order']))
        layers=[dict(id='material',stage='materials'),dict(id='bloom',stage='postprocess'),dict(id='light',stage='baseline')]
        out=self.root/'integrated'
        result=mod.integrate(Adapter(),fixture,layers,out)
        self.assertEqual((out/'capture.bin').read_text(),'light|material|bloom')
        self.assertEqual(result['status'],'working-preview')
        self.assertTrue(result['reopened_guard_pass'])
        with self.assertRaises(FileExistsError):mod.integrate(Adapter(),fixture,layers,out)

if __name__ == '__main__':
    unittest.main()
