import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import meta_loop as m


def trial(i, **kwargs):
    r = m.blank_trial(str(i), 'lane', 'sample-base', 'geometry')
    r.update(timestamp=f'2026-10-15T12:00:{i:02d}Z', defect_id='front',
             parameters={'height': i}, artifacts_verified=True,
             artifacts=[{'path': f'/fixture/{i}.png', 'sha256': '0'*64}],
             self_review={'status': 'reject', 'notes': 'Reject appearance: tiled surface.'},
             failure_class='mechanism')
    r.update(kwargs)
    return r


class DreamTests(unittest.TestCase):
    def test_recombination_prefers_specific_partial_win_and_correct_attribution(self):
        rows = [trial(1, element='sample-panel', self_review={'status':'partial','notes':'Sharp sample edge; repeated pattern remains.'}),
                trial(2, element='sample-panel', self_review={'status':'partial','notes':'Strongest local sample structure; placement still fails.'}),
                trial(3, element='sample-panel', lane='stack', self_review={'status':'partial','notes':'Selected stronger sample contrast.'})]
        p = m.dream(rows, 'sample-panel', {})
        combo = next(d for d in p['directions'] if d['kind']=='recombination')
        self.assertEqual(combo['parameters']['components'][0], '2')
        import dream_step as d
        wrong = trial(4, self_review={'status':'hold','notes':'Q repairs P sample boundary.'})
        self.assertEqual(d.partial_features(wrong), [])

    def test_portfolio_consolidates_topics_and_reserves_unreviewed_work(self):
        rows = [trial(i, element='sample-panel', defect_id='engraving' if i<3 else 'density',
                      self_review={'status':'reject','notes':'Reject sample shape and texture.'}) for i in range(1,5)]
        result = m.dream(rows, 'sample-panel', {})
        breadth = [d for d in result['directions'] if d['kind']=='breadth']
        self.assertEqual(len({d['technique'] for d in breadth}), len(breadth))
        self.assertTrue(any(set(d['defect_ids'])=={'engraving','density'} for d in breadth))
        rows.append(trial(5, status='completed', failure_class='none', self_review={'status':'pending','notes':'Awaiting review.'}))
        result = m.dream(rows, 'sample-base', {})
        self.assertTrue(any(d['mechanism_class']=='geometry' for d in result['reserved_directions']))

    def test_publisher_blocks_dreams_when_any_lane_is_invalid(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            rows = [trial(i, owner_reaction={'status':'rejected','receipt':f'test:{i}'}) for i in (1,2)]
            m.publish_materialized(root, rows, ['invalid lane'])
            plan = json.loads((root/'next-sample-base.json').read_text())
            self.assertIsNone(plan['dream'])
            self.assertEqual(plan['batch'], [])



    def test_control_delivery_and_same_configuration_do_not_inflate_stuck(self):
        a = trial(1, parameters={'height': .1})
        repeat = trial(2, parameters={'height': .1})
        control = trial(3, self_review={'status': 'control', 'notes': 'Control only'}, metrics={'mode': 'CLEAR'})
        delivery = trial(4, metrics={'technical_delivery': True, 'max_zoom_gate': 'fail', 'max_zoom_evidence': 'r'})
        self.assertEqual(m.stuck([a, repeat, control, delivery], {}), [])
        second = trial(5, parameters={'height': .5})
        self.assertEqual(m.stuck([a, repeat, second], {})[0]['consecutive_nonwins'], 2)

    def test_near_duplicate_and_pending_filters_are_auditable(self):
        import dream_step as d
        self.assertGreaterEqual(d.parameter_similarity({'height': .3, 'seed': 5}, {'height': .31, 'seed': 91}), .8)
        rows = [trial(1, mechanism_class='traced_vector',
                      parameters={'construction': 'source-bound-tracing', 'regional_control': True}), trial(2)]
        result = m.dream(rows, 'sample-base', {})
        self.assertTrue(any(x['reason'].startswith('near-duplicate') for x in result['suppressed']))
        rows.append(trial(3, status='pending', mechanism_class='layer_stack'))
        result = m.dream(rows, 'sample-base', {})
        self.assertFalse(any(x['mechanism_class']=='layer_stack' for x in result['directions']))
        self.assertTrue(any(x['reason']=='pending mechanism' for x in result['suppressed']))

    def test_cli_dream_stuck_and_next_publish_without_touching_archive(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root/'events').mkdir()
            # Owner rejection is a test-only receipt, never a real owner log.
            rows = [trial(i, owner_reaction={'status': 'rejected', 'receipt': f'test:{i}'}) for i in (1, 2)]
            (root/'events/lane.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
            (root/'events/owner.jsonl').write_text('')
            before = {str(p): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            def cli(*args):
                return subprocess.run([sys.executable, str(Path(m.__file__).resolve()), '--data', str(root), *args],
                                      text=True, capture_output=True)
            result = cli('stuck')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['stuck'][0]['element'], 'sample-base')
            result = cli('dream', '--element', 'sample-base')
            self.assertEqual(result.returncode, 0, result.stderr)
            portfolio = json.loads(result.stdout)
            self.assertEqual(json.loads((root/'dream/sample-base.json').read_text()), portfolio)
            self.assertIn('Cheapest coupon', (root/'dream/sample-base.md').read_text())
            result = cli('next', '--element', 'sample-base')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(json.loads(result.stdout)['dream']['directions'])
            for path, content in before.items():
                self.assertEqual(Path(path).read_bytes(), content)
            self.assertFalse((root/'ledger.json').exists(), 'read-only commands must not race the rating materializer')
            result = cli('dream', '--element', '../missing')
            self.assertEqual(result.returncode, 2)
            (root/'events/broken.jsonl').write_text('{broken}\n')
            for args in [('stuck',), ('dream', '--element', 'sample-base'), ('next', '--element', 'sample-base')]:
                self.assertEqual(cli(*args).returncode, 2)

    def test_replay_prefix_is_invariant_to_future_and_unknown_has_no_reward(self):
        import dream_step as d
        self.assertTrue(hasattr(d, 'schedule_replay'), 'schedule replay missing')
        rows = [trial(i) for i in range(1, 6)]
        short = d.schedule_replay(rows[:3], {})
        full = d.schedule_replay(rows, {})
        for policy, result in full['policies'].items():
            self.assertEqual(short['policies'][policy]['decisions'], result['decisions'][:3])
            for decision in result['decisions']:
                self.assertNotIn(decision['trial_id'], decision['observed_ids'])
                if not decision['matched']:
                    self.assertIsNone(decision['reward'])
            self.assertIsNone(result['value_estimate'])
        self.assertTrue(full['exploration_gaps'])
        self.assertEqual(full['policies']['earlier_switch']['decisions'][2]['recommended'], 'procedural_shader')
        changed = copy.deepcopy(rows)
        changed[-1]['owner_reaction'] = {'status': 'approved', 'receipt': 'o:5'}
        self.assertEqual(full['policies']['earlier_switch']['decisions'][:4],
                         d.schedule_replay(changed, {})['policies']['earlier_switch']['decisions'][:4])
        self.assertEqual(d.schedule_replay([trial(1, timestamp=None)], {})['excluded_unknown_order'], ['1'])

    def test_portfolio_has_diverse_evidenced_experiments_and_no_failed_clones(self):
        self.assertTrue(hasattr(m, 'dream'), 'dream portfolio missing')
        rows = [trial(1), trial(2)]
        rows += [trial(3, element='sample-donor', lane='other', mechanism_class='layer_stack',
                       failure_class='none', self_review={'status': 'partial', 'notes': 'Useful isolated wet coat; form remains soft.'},
                       recipe={'script_path': '/fixture/apply.py', 'entrypoint': 'apply'})]
        rows[0]['self_review']['notes'] = 'Useful sample outline, but spacing fails.'
        rows[1]['lane'] = 'second-lane'
        rows[1]['self_review']['notes'] = 'Improved sample highlights, but depth fails.'
        before = copy.deepcopy(rows)
        result = m.dream(rows, 'sample-base', {})
        self.assertEqual(rows, before)
        directions = result['directions']
        self.assertTrue({'breadth', 'recombination', 'recipe_transfer', 'counterfactual', 'wildcard'}
                        <= {r['kind'] for r in directions})
        self.assertEqual(sum(r['kind']=='wildcard' for r in directions), 1)
        self.assertGreaterEqual(len({r['mechanism_class'] for r in directions}), 3)
        for direction in directions:
            for field in ('hypothesis', 'mechanism_class', 'cheapest_coupon_test', 'expected_signal',
                          'cost_estimate', 'risk', 'start_artifacts', 'evidence_ids', 'reason', 'parameters'):
                self.assertIn(field, direction)
            self.assertTrue(direction['evidence_ids'])
            self.assertFalse(any(direction['mechanism_class']==r['mechanism_class'] and
                                 direction['parameters']==r['parameters'] for r in rows[:2]))
        self.assertEqual([d['rank'] for d in directions], list(range(1, len(directions)+1)))
        self.assertTrue(all(d['cost_estimate']['gpu_seconds'] is None for d in directions))
        with self.assertRaises(ValueError):
            m.dream(rows, 'sample-base', {}, 'missing')

    def test_stuck_is_element_scoped_and_resets_on_success(self):
        self.assertTrue(hasattr(m, 'stuck'), 'stuck detector missing')
        a, b = trial(1), trial(2)
        other = trial(3, element='sample-panel')
        result = m.stuck([other, b, a], {})
        self.assertEqual([(r['element'], r['defect_id'], r['failed_trials']) for r in result],
                         [('sample-base', 'front', ['1', '2'])])
        win = trial(4, owner_reaction={'status': 'approved', 'receipt': 'owner:4'})
        self.assertEqual(m.stuck([a, b, win], {}), [])
        excluded = [trial(5, failure_class='resource'), trial(6, timestamp=None),
                    trial(7, status='pending'), trial(8, source={'evidence_only': True})]
        self.assertEqual(m.stuck([a]+excluded, {}), [])
        hold = trial(9, failure_class='none', self_review={'status': 'hold', 'notes': 'No owner approval.'})
        self.assertEqual(m.stuck([a, hold], {}), [])


if __name__ == '__main__':
    unittest.main()
