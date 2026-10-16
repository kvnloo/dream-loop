#!/usr/bin/env python3
"""Build a source-bound rating catalog, preserving existing trial IDs.

Historical inferences are NOT events and never enter learning until confirmed.
New historical trials are imported only when the ledger had a report, not a trial.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
from PIL import Image
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


def seed(data):
    data = Path(data)
    root = data.parents[1]
    night = root/'process/night-v2'
    rows = json.loads((data/'ledger.json').read_text())
    trials = {r['trial_id']: r for r in rows}
    raw_rows, errors = ml.read_jsonl(root/'process/blender-mastery/evals/rounds.jsonl')
    anchors, issues = ml.read_jsonl(root/'process/blender-mastery/evals/owner_labels.jsonl')
    if errors or issues:
        raise ValueError(errors+issues)
    raw = {r['id']: r for r in raw_rows}
    target_receipt = night/'banner-generator/target-statistics.json'
    target = Path(json.loads(target_receipt.read_text())['target'])
    catalog = Catalog(data)
    imported = []

    def register(folder, element, mechanism, hypothesis, report, images):
        tid = 'q:'+str(folder.relative_to(root))
        if tid in trials:
            return trials[tid]
        row = ml.blank_trial(tid, 'rating-import', element, mechanism)
        row.update(hypothesis=hypothesis, run_id='night-v2', defect_id=element+'-appearance',
                   timestamp=None, source={'path': str(report), 'sha256': ml.digest(report),
                   'adapter': 'owner-rating-explicit-variant-v1', 'timestamp_basis': 'unknown',
                   'reason': 'Existing report was evidence-only; reconstructed distinct rendered variant.'})
        row['artifacts'] = [dict(path=str(p), sha256=ml.digest(p)) for p in [report]+images]
        row['event_id'] = 'rating-import-'+hashlib.sha256(ml.json_text(row).encode()).hexdigest()[:24]
        ml.validate_trial(row)
        trials[tid] = row
        imported.append(row)
        return row

    # Native event image paths come directly from the materialized producer ledger.
    for row in rows:
        tid = row['trial_id']
        if row['lane'] not in ('banner-traced', 'banner-generator') or row.get('source', {}).get('evidence_only'):
            continue
        paths = [Path(a['path']) for a in row['artifacts'] if a['path'].endswith('.png')]
        paths = [p for p in paths if p.name == 'native.png' or p.name.startswith(('201mp-', '1gp-'))]
        if not paths:
            continue
        views = []
        for p in sorted(paths, key=lambda p: (p.name != 'native.png', p.name)):
            settings = p.with_name(p.stem+'-settings.json')
            meta = json.loads(settings.read_text()) if settings.exists() else {}
            kind = 'native' if p.name == 'native.png' else p.stem.split('-')[0]
            region = p.stem.split('-', 1)[1] if '-' in p.stem else 'banner'
            views.append(catalog.view(p, target, kind, region, meta, settings if settings.exists() else target_receipt))
        views.insert(0, dict(views[0], kind='hero'))  # fit view of same native image, not new evidence
        control = 'banner-traced-T' if row['lane'] == 'banner-traced' else 'banner-generator-b1-T'
        catalog.add(row, 'banner', tid, views, control if tid != control else None)

    variants = [
        ('comic-style/C', 'night-banner', 'layer_stack', 'Interrupted hatch with tone-driven dark/light polarity', 'comic-style/REPORT.md'),
        ('comic-style/r2/M', 'night-banner', 'procedural_shader', 'Analytical stepped Truchet paths with tone-driven width and dropout', 'comic-style/r2/REPORT.md'),
        ('comic-style/r2/N', 'night-banner', 'procedural_shader', 'Open nested bundles with tone-dependent stroke count', 'comic-style/r2/REPORT.md'),
        ('relief-2/A', 'night-banner', 'geometry', 'Curvature-deepened recesses with subtractive plane scrapes', 'relief-2/REPORT.md'),
        ('relief-2/B', 'night-banner', 'geometry', 'Stronger scrape depth and curl return displacement', 'relief-2/REPORT.md'),
        ('relief-2/C', 'night-banner', 'geometry', 'Connected irregular planar relief with restrained cheek influence', 'relief-2/REPORT.md'),
        ('stone-lowpoly/A', 'night-stone', 'geometry', 'Angular fractured slate with flat tops and planar shoulders', 'stone-lowpoly/REPORT.md'),
        ('stone-lowpoly/B', 'night-stone', 'geometry', 'Continuous shallow displaced and decimated triangular slab', 'stone-lowpoly/REPORT.md'),
        ('stone-lowpoly/C', 'night-stone', 'geometry', 'Eight instanced low-poly kit meshes with varied scale and orientation', 'stone-lowpoly/REPORT.md'),
        ('stone-lowpoly/r2/A2', 'night-stone', 'geometry', 'Smaller dark overlapping slate plates with reflective microfacets', 'stone-lowpoly/r2/REPORT.md'),
        ('stone-lowpoly/r2/A3', 'night-stone', 'geometry', 'A2 slate plus sparse BVH-seated olive tufts at joints', 'stone-lowpoly/r2/REPORT.md'),
    ]
    for rel, element, mechanism, hypothesis, report_rel in variants:
        folder, report = night/rel, night/report_rel
        names = ['native.png', 'zoom.png'] if rel == 'comic-style/C' else (
            ['native.png']+[f'{density}-{region}.png' for density in ('201mp', '1gp') for region in ('cheek','brow','curls')]
            if 'comic-style/r2' in rel else ['portrait-native.png'] if 'relief-2' in rel else
            ['full.png','maxzoom.png'] if '/r2/' in rel else ['full-safe.png'])
        images = [folder/name for name in names]
        row = register(folder, element, mechanism, hypothesis, report, images)
        views = []
        for p in images:
            meta = {}
            kind = 'native'
            region = 'banner' if element == 'night-banner' else 'stone'
            if p.stem.startswith(('201mp-', '1gp-')):
                kind, region = p.stem.split('-', 1)
                receipt = p.with_name(p.stem+'-settings.json')
                meta = json.loads(receipt.read_text())
            elif rel == 'comic-style/C':
                receipt = night/'comic-style/delivery-verification.json'
                meta = json.loads(receipt.read_text())['C'][p.stem]
                if p.stem == 'zoom':
                    kind, region = '201mp', 'cheek'
            elif p.stem == 'maxzoom':
                receipt = folder/'maxzoom-receipt.json'
                meta = json.loads(receipt.read_text())
                kind, region = '201mp', 'plinth'
            else:
                receipt = report
                if element == 'night-banner':
                    meta = {'full_frame': [2048,3072], 'box': [1320,0,2048,1510]}
            use_target = night/'stone-lowpoly/target-stone-isolated.png' if element == 'night-stone' and kind == 'native' else target
            views.append(catalog.view(p, use_target, kind, region, meta, receipt))
        views.insert(0, dict(views[0], kind='hero'))
        catalog.add(row, 'stone' if element == 'night-stone' else 'banner', rel, views)

    # Stack receipts bind both full-frame density and crop placement.
    stack_records = json.loads((night/'layer-stack/all-trials.json').read_text())
    assert len(stack_records) == 14, 'Expected the 14 retained layer stacks'
    for rec in stack_records:
        row = trials['LS-'+rec['key']]
        views = []
        for render in rec['receipt']['renders']:
            p = Path(render['path'])
            kind = 'native' if render['family'] == '3x' else render['family']
            region = render['element']
            views.append(catalog.view(p, target, kind, region, render, night/'layer-stack/all-trials.json'))
        catalog.add(row, 'stacks', 'Layer stack '+rec['key'], views)
    integrated = trials['LS-integrated']
    receipt = night/'layer-stack/integrated-receipt.json'
    views = [catalog.view(Path(r['path']), target, r['family'], r['element'], r, receipt)
             for r in json.loads(receipt.read_text())['renders']]
    catalog.add(integrated, 'stacks', 'Integrated B5 + S6', views, 'q:process/night-v2/integrated/it12')
    itid = 'q:process/night-v2/integrated/it12'
    it_images = [a for a in raw[itid]['artifacts'] if a['path'].endswith('/full.png')]
    if not it_images:
        raise ValueError('it12 full render absent from source ledger')
    itpath = Path(it_images[0]['path'])
    catalog.add(trials[itid], 'stacks', 'it12 control', [catalog.view(itpath, target, 'hero', 'full', provenance=trials[itid]['source']['path'])], 'LS-integrated')

    whitebase = root/'dreamloop-runs/themes-port-2026-10-13/white-r111'
    white_receipt = whitebase/'comparison-receipt.json'
    white = json.loads(white_receipt.read_text())
    for name in ('white-r111', 'white-r111b'):
        tid = 'q:dreamloop-runs/themes-port-2026-10-13/'+name
        full = next(Path(a['path']) for a in white['sources'] if Path(a['path']).parent.name == name)
        reference = Path(white['sources'][0]['path'])
        views = [catalog.view(full, reference, 'hero', 'full', provenance=white_receipt)]
        for region, meta in white['native_crops'].items():
            views.append(dict(kind='native', region=region,
                image=catalog.crop(full, meta['render_box'], white_receipt),
                target=catalog.crop(reference, meta['reference_box'], white_receipt),
                target_note='Original reference pixels; render has twice the source resolution.', receipt=str(white_receipt)))
        comparisons = [catalog.asset(a['path'], raw[tid]['hypothesis_basis']) for a in raw[tid]['artifacts'] if a.get('role') == 'compare']
        other = 'q:dreamloop-runs/themes-port-2026-10-13/'+('white-r111b' if name == 'white-r111' else 'white-r111')
        catalog.add(trials[tid], 'white', 'White A / r102 arch' if name == 'white-r111' else 'White B / soft r103 arch', views, other, comparisons)

    # Append real reconstructed trials only; never write synthetic or inferred labels.
    path = data/'events/rating-import.jsonl'
    existing, errors = ml.read_jsonl(path)
    if errors:
        raise ValueError(errors)
    ids = {e['event_id'] for e in existing}
    with path.open('a') as f:
        for row in imported:
            if row['event_id'] not in ids:
                f.write(ml.json_text(row)+'\n')
    history = infer_history(list(trials.values()), anchors, raw)
    for entry, anchor in zip(history, anchors):
        entry['review_images'] = [dict(role=image.get('role'), image=catalog.asset(image['path'], anchor.get('source')),
                                      recorded_sha256=image.get('sha256'))
                                 for image in anchor.get('images', []) if Path(image['path']).is_file()]
        # Suggestions are displayed for explicit confirmation, never ingested as labels.
        entry['suggested_verdict'] = {'owner:72494':'accept','owner:73430':'accept',
            'owner:77290':'accept','owner:79989':'reject','owner:82349':'reject',
            'owner:89883':'reject'}.get(entry['id'], 'maybe')
    present = {c['trial_id'] for c in catalog.candidates}
    # Make all inferred history bindings reviewable, including old Day/White frames.
    for entry in history:
        for tid in entry['trial_ids']:
            if tid in present:
                continue
            image_rows = raw.get(tid, {}).get('artifacts', [])
            image = next((a['path'] for a in image_rows if a.get('role') == 'capture' and Path(a['path']).is_file()), None)
            if image:
                reference = next((i['path'] for a in anchors if a['id'] == entry['id'] for i in a.get('images', []) if i.get('role') == 'reference'), None)
                views = [dict(kind='hero', region='historical', image=catalog.asset(image, raw[tid].get('hypothesis_basis')),
                    target=catalog.asset(reference) if reference else None, target_note='No target bound to this historical receipt.' if not reference else 'Historical source reference')]
                catalog.add(trials[tid], 'history-only', tid.split('/')[-1], views)
                present.add(tid)
    counts = dict(Counter(c['queue'] for c in catalog.candidates))
    result = dict(generated_at=ml.now(), candidates=catalog.candidates, history=history, assets=catalog.assets,
                  counts=counts, history_counts=dict(Counter(h['status'] for h in history)),
                  imported_trials=[r['trial_id'] for r in imported],
                  limitations=['Hero may be a fit-to-pane display of the native crop, not a separate full-frame render.',
                    'Reference is source-resolution only. 201 MP / 1 GP refer to candidate render density, never target truth.',
                    'Historical component feedback does not count as whole-trial acceptance.'])
    atomic_json(data/'rating-catalog.json', result)
    atomic_json(data/'owner-history-inferred.json', history)
    return {k: result[k] for k in ('counts', 'history_counts', 'imported_trials')}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=ml.DEFAULT_DATA)
    args = parser.parse_args()
    print(json.dumps(seed(args.data), indent=2))
