#!/usr/bin/env python3
"""Validate explicit chat-label mappings; dry-run unless --commit is given.

A trusted adapter may implement read_chat_labels(path). The default accepts only
canonical JSONL labels. Neither source text nor timestamps infer trial bindings,
verdicts or stars. The importer never stops a server or rewrites producer events.
"""
import argparse
import fcntl
import json
import os
from pathlib import Path
import meta_loop as ml
from project_adapter import hook


def canonical_labels(path):
    rows, errors = ml.read_jsonl(path)
    if errors:
        raise ValueError('; '.join(errors))
    return rows


def import_labels(data, source, *, commit=False):
    data, source = Path(data), Path(source)
    if not source.is_file():
        raise ValueError('Missing chat source')
    labels = list(hook('read_chat_labels', canonical_labels, source))
    # Share the owner server's cooperative write lock, not a second materializer.
    with (data/'owner-rating.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        from dream_step import archive_snapshot
        before = archive_snapshot(data)
        rows, errors = ml.ingest(data, persist=False)
        if errors or before != archive_snapshot(data):
            raise ValueError('Invalid or changing archive; retry on a coherent snapshot')
        path = data/'events/owner.jsonl'
        existing = canonical_labels(path)
        ids = {r['event_id']: r for r in existing}
        trials = {r['trial_id']: r for r in rows}
        additions = []
        for label in labels:
            ml.validate_owner_label(label, trials)
            if label['source'] != 'chat-backfill':
                raise ValueError('Importer accepts backfilled chat evidence only')
            eid = label['event_id']
            if eid in ids and ids[eid] != label:
                raise ValueError('Conflicting event_id '+eid)
            if eid not in ids:
                additions.append(label)
                ids[eid] = label
        _, _, errors = ml.reduce_owner_labels(rows, existing+additions)
        if errors:
            raise ValueError('; '.join(errors))
        if commit and additions:
            path.parent.mkdir(parents=True, exist_ok=True)
            payload = ''.join(ml.json_text(row)+'\n' for row in additions).encode()
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
            try:
                if os.write(fd, payload) != len(payload):
                    raise OSError('Incomplete append; repair final line before retry')
                os.fsync(fd)
            finally:
                os.close(fd)
            persisted = canonical_labels(path)
            if persisted != existing+additions:
                raise OSError('Chat import read-back failed')
        return dict(committed=commit, added=len(additions), total=len(existing)+len(additions),
                    source_sha256=ml.digest(source),
                    materialization='Not changed; refresh through the existing single writer')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--commit', action='store_true')
    args = parser.parse_args()
    print(json.dumps(import_labels(args.data, args.source, commit=args.commit), indent=2))


if __name__ == '__main__': main()
