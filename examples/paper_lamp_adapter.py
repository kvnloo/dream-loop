"""Fictional paper-lamp study. No real project paths or records.

Select explicitly with DREAM_LOOP_ADAPTER=/absolute/path/to/this/file.py.
The custom intake is deliberately small; native meta_trial events need no adapter.
"""
import hashlib
from pathlib import Path
from meta_loop import blank_trial, json_text, read_jsonl

LIVE_LANES = ('sample-lab',)
DEFAULT_ELEMENTS = ()


def mechanism_key(row):
    return 'generated_vector' if row.get('parameters', {}).get('authored') is True else row['mechanism_class']


def adapt_lane(raw, path, line):
    if raw.get('event') != 'sample_trial':
        raise ValueError('Not a fictional sample_trial')
    row = blank_trial(raw['trial_id'], Path(path).stem, raw['element'], raw['mechanism_class'])
    row['event_id'] = row['trial_id']+'-'+hashlib.sha256(json_text(raw).encode()).hexdigest()[:16]
    row['parents'] = raw.get('parents', [])
    row['source'] = dict(path=str(path), line=line, raw=raw)
    row['status'] = 'pending'
    return row


def import_history(folder):
    path = Path(folder)/'samples.jsonl'
    rows, errors = read_jsonl(path)
    if errors:
        raise ValueError('; '.join(errors))
    return [adapt_lane(row, path, line) for line, row in enumerate(rows, 1)], []


def read_chat_labels(path):
    """Accept only explicitly mapped canonical labels, not guessed sentiment."""
    from import_chat import canonical_labels
    return canonical_labels(path)


def build_catalog(data, catalog, rows):
    """Fictional live producer supplies explicit views and hash-bound paths."""
    import copy
    from catalog import Catalog
    from meta_loop import digest, now
    result = copy.deepcopy(catalog)
    builder = Catalog(data)
    builder.assets.update(result['assets'])
    for row in rows:
        if row['status'] != 'completed':
            continue
        bound = {a['path']: a['sha256'] for a in row['artifacts']}
        views = []
        for spec in row['metrics'].get('review_views', []):
            for key in ('path', 'target'):
                if spec[key] not in bound or digest(spec[key]) != bound[spec[key]]:
                    raise ValueError('Review view must be hash-bound')
            view = builder.view(spec['path'], spec['target'], spec.get('kind', 'hero'), spec.get('region', 'main'))
            mode = spec['mode']
            if mode not in ('look', 'clear'):
                raise ValueError('Explicit look/clear required')
            view[mode] = view['image']
            views.append(view)
        if views:
            builder.add(row, row['lane'], row['trial_id'], views)
    result['candidates'] = [c for c in result['candidates'] if c['queue'] not in LIVE_LANES]+builder.candidates
    result.update(assets=builder.assets, generated_at=now(), queue_labels={'sample-lab': 'Paper lamp samples'})
    return result
