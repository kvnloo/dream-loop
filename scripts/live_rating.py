"""Live catalogs use an explicitly selected trusted project adapter.

The default has no watched lanes and does not infer paths, views or crops.
Catalogs can also be supplied through the generic manifest seeder.
"""
import copy
from pathlib import Path
import meta_loop as ml
from project_adapter import hook, setting


def lanes():
    return tuple(setting('LIVE_LANES', ()))


def lane_rows(data):
    events = []
    for lane in lanes():
        if not isinstance(lane, str) or not lane or Path(lane).name != lane or lane in ('.', '..'):
            raise ValueError('Invalid lane filename')
        path = Path(data)/'events'/(lane+'.jsonl')
        rows, errors = ml.read_jsonl(path)
        if errors:
            raise ValueError('; '.join(errors))
        for line, row in enumerate(rows, 1):
            event = ml.adapt_lane(row, path, line)
            if event['lane'] != lane:
                raise ValueError('Unexpected lane in '+str(path))
            events.append(event)
    rows, errors = ml.materialize(events)
    if errors:
        raise ValueError('; '.join(errors))
    return rows


def build_catalog(data, catalog, rows):
    return hook('build_catalog', lambda data, catalog, rows: copy.deepcopy(catalog), data, catalog, rows)
