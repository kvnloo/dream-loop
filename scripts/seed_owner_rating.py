#!/usr/bin/env python3
"""Build a source-bound rating catalog from an explicit external manifest.

Historical inferences are NOT events and never enter learning until confirmed.
No project-specific paths, trial reconstructions or decision mappings are bundled.
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import meta_loop as ml
from owner_rating import atomic_json


def infer_history(rows, anchors, raw):
    known = {r['trial_id'] for r in rows if not r.get('source', {}).get('evidence_only')}
    path_to_ids, hash_to_ids, directory_to_ids = defaultdict(set), defaultdict(set), defaultdict(set)
    for tid, row in raw.items():
        if tid in known:
            for artifact in row.get('artifacts', []):
                path_to_ids[artifact['path']].add(tid)
                if artifact.get('sha256'):
                    hash_to_ids[artifact['sha256']].add(tid)
                directory_to_ids[str(Path(artifact['path']).parent)].add(tid)
    result = []
    for anchor in anchors:
        matches, evidence = set(), []
        for tid in anchor.get('linked_nodes', []):
            if tid in known:
                matches.add(tid)
                evidence.append({'kind': 'curated_linked_node', 'trial_id': tid,
                                 'basis': anchor.get('binding_status')})
        for image in anchor.get('images', []):
            if image.get('role') in ('reference', 'owner_attachment'):
                continue
            ids = path_to_ids.get(image['path'], set())
            basis = 'exact_reviewed_image_path'
            if not ids and image.get('sha256'):
                ids = hash_to_ids.get(image['sha256'], set())
                basis = 'identical_reviewed_image_sha256'
            if not ids:
                ids = directory_to_ids.get(str(Path(image['path']).parent), set())
                basis = 'unique_trial_directory; subvariant feedback remains component scoped'
            if len(ids) == 1:
                matches.update(ids)
                evidence.append({'kind': basis, 'path': image['path'],
                                 'sha256': image.get('sha256'), 'trial_id': next(iter(ids))})
        pair = anchor.get('pair')
        mapped_pair = None
        if pair:
            left, right = path_to_ids.get(pair['baseline'], set()), path_to_ids.get(pair['candidate'], set())
            if len(left) == len(right) == 1 and left != right:
                mapped_pair = {'baseline': next(iter(left)), 'candidate': next(iter(right)),
                               'preferred': pair['preferred']}
        result.append(dict(id=anchor['id'], quote=anchor['quote'], date=anchor.get('date'),
            source=anchor.get('source'), scope=anchor.get('scope'),
            status='inferred' if matches else 'unresolved', trial_ids=sorted(matches),
            suggested_verdict='maybe', suggested_pairwise=mapped_pair, evidence=evidence,
            reason='Explicit curated link or unique reviewed image; owner confirmation required.' if matches else
                   'No unambiguous trial binding in retained receipt. Timestamp proximity and coarse keyword annotations are not evidence.'))
    return result


from catalog import Catalog


def seed(data, manifest=None):
    """Build views from explicit local configuration; never reconstruct trials."""
    if manifest is None:
        raise ValueError('An explicit external catalog manifest is required')
    data, manifest = Path(data), Path(manifest).resolve()
    config = json.loads(manifest.read_text())
    rows = json.loads((data/'ledger.json').read_text())
    trials = {r['trial_id']: r for r in rows}
    catalog = Catalog(data)
    seen = set()
    for entry in config['candidates']:
        tid = entry['trial_id']
        row = trials.get(tid)
        if row is None or row.get('source', {}).get('evidence_only') or tid in seen:
            raise ValueError('Manifest must identify unique existing trials: '+tid)
        seen.add(tid)
        views = [catalog.view(manifest.parent/Path(view['path']),
                 manifest.parent/Path(view['target']), view['kind'],
                 view.get('region', 'main'), view.get('metadata'), manifest)
                 for view in entry['views']]
        catalog.add(row, entry['queue'], entry.get('title', tid), views,
                    entry.get('compare_to'))
    anchors = config.get('anchors', [])
    history = infer_history(rows, anchors, trials)
    counts = dict(Counter(c['queue'] for c in catalog.candidates))
    result = dict(generated_at=ml.now(), candidates=catalog.candidates,
                  history=history, assets=catalog.assets, counts=counts,
                  history_counts=dict(Counter(h['status'] for h in history)),
                  imported_trials=[],
                  limitations=['Manifest is local configuration, not owner approval.',
                               'History suggestions require explicit owner confirmation.'])
    atomic_json(data/'rating-catalog.json', result)
    atomic_json(data/'owner-history-inferred.json', history)
    return {k: result[k] for k in ('counts', 'history_counts', 'imported_trials')}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=ml.DEFAULT_DATA)
    parser.add_argument('--manifest', type=Path, required=True,
                        help='External JSON manifest; image paths relative to its directory')
    args = parser.parse_args()
    print(json.dumps(seed(args.data, args.manifest), indent=2))
