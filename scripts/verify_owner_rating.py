#!/usr/bin/env python3
"""One-command HTTP + Lightpanda E2E; all synthetic labels go to a disposable copy."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
import meta_loop as ml
import owner_rating as ui


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=ml.DEFAULT_DATA)
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    source = args.data.resolve()
    owner = source/'events/owner.jsonl'
    before = owner.read_bytes() if owner.exists() else None
    binary = str(Path.home()/'.local/bin/agent-browser')
    session = 'owner-rating-test-'+str(os.getpid())
    calls = []
    def browser(*arguments):
        command = [binary, '--session', session, '--engine', 'lightpanda', '--json', *arguments]
        result = subprocess.run(command, capture_output=True, text=True, timeout=60)
        if result.returncode:
            raise AssertionError(result.stdout+result.stderr)
        value = json.loads(result.stdout)
        if not value.get('success'):
            raise AssertionError(value)
        calls.append({'command': arguments[0], 'ok': True})
        return value.get('data', {})
    def evaluate(script):
        return browser('eval', script).get('result')
    def wait_for(script, timeout=30):
        end = time.monotonic()+timeout
        while time.monotonic() < end:
            value = evaluate(script)
            if value:
                return value
            time.sleep(.1)
        raise AssertionError('Browser condition timed out: '+script)
    report: dict[str, object] = {}
    with tempfile.TemporaryDirectory(prefix='owner-rating-e2e-') as temporary:
        data = Path(temporary).resolve()/'meta-loop'
        data.mkdir()
        (data.parent/'night-v2').symlink_to(source.parent/'night-v2', target_is_directory=True)
        for name in ('ledger.json','rating-catalog.json','ingest.json','calibration.json','owner-anchors.json','artifact-verification.json'):
            if (source/name).exists():
                shutil.copy2(source/name, data/name)
        shutil.copytree(source/'events', data/'events')
        app = ui.RatingApp(data)
        assert app.poll(), app.poll_status
        server = ui.make_server(app, 0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = 'http://127.0.0.1:'+str(server.server_port)
        try:
            with urllib.request.urlopen(base+'/health', timeout=3) as response:
                assert json.load(response)['data'] == str(data)
            browser('open', base)
            wait_for("document.body.dataset.ready === 'true'")
            evaluate("Array.from(document.querySelectorAll('#queues button')).find(b=>b.firstChild.textContent==='Stone mosaic').click(); true")
            assert evaluate("document.getElementById('region').value === 'plinth front face'")
            assert evaluate("!document.getElementById('clear-figure').hidden")
            assert evaluate("document.getElementById('judge-mode').value === 'both'")
            first = evaluate("document.getElementById('title').textContent")
            assert first, 'No candidate rendered'
            # DOM key events intentionally exercise the app handlers, not synthetic geometry.
            def key(k):
                evaluate('document.dispatchEvent(new KeyboardEvent("keydown", {key:'+json.dumps(k)+',bubbles:true})); true')
            key('l')
            assert evaluate("document.getElementById('judge-mode').value === 'look'")
            key('l')
            assert evaluate("document.getElementById('judge-mode').value === 'clear'")
            key('l')
            assert evaluate("document.getElementById('judge-mode').value === 'both'")
            key('5');key('a')
            # A server refresh must not discard an unsaved rating or chosen trial.
            evaluate("document.getElementById('other').value='SMOS-coupon-B'; true")
            key('ArrowRight')
            evaluate("document.getElementById('note').value='refresh-preserved draft'; true")
            app.catalog['generated_at']='e2e-refresh'
            evaluate("refreshCatalog(); true")
            wait_for("data.generated_at==='e2e-refresh' && document.getElementById('note').value==='refresh-preserved draft' && document.getElementById('judge-mode').value==='both'")
            assert evaluate("document.getElementById('pair').checked && document.getElementById('other').value==='SMOS-coupon-B'")
            assert evaluate("document.querySelector('[data-verdict=accept]').getAttribute('aria-pressed') === 'true'")
            key('z')
            assert evaluate("document.getElementById('stage').classList.contains('zoomed')")
            key(' ')
            assert evaluate("document.getElementById('candidate-caption').textContent === 'TARGET FLIP'")
            key(' ')
            evaluate("document.getElementById('other').value='SMOS-coupon-B'; true")
            key('ArrowRight')
            assert evaluate("document.getElementById('preference').textContent === 'Right preferred'")
            started = time.monotonic()
            key('Enter')
            wait_for("document.getElementById('status').textContent.startsWith('Saved ')", 60)
            latency = time.monotonic()-started
            assert evaluate("!document.getElementById('recommendation').hidden")
            events, errors = ml.read_jsonl(data/'events/owner.jsonl')
            assert not errors
            event = events[-1]
            assert event['source']=='owner-ui' and event['verdict']=='accept' and event['stars']==5
            assert event['pairwise']['preference']=='candidate'
            assert event['judged_on']=='both'
            persisted = json.loads((data/'ledger.json').read_text())
            rated = next(r for r in persisted if r['trial_id']==event['trial_id'])
            assert ml.owner_outcome(rated)==1
            assert json.loads((data/'summary.json').read_text())['owner_accept_observations'] >= 1
            # Typing a note must not trigger global shortcuts.
            evaluate("document.getElementById('note').focus(); document.getElementById('note').dispatchEvent(new KeyboardEvent('keydown',{key:'a',bubbles:true})); true")
            assert evaluate("document.querySelector('[data-verdict=accept]').getAttribute('aria-pressed') === 'false'")
            evaluate("document.getElementById('note').blur(); true")
            key('p')
            assert evaluate("document.getElementById('title').textContent")==first
            # Read-only queue and history navigation checks.
            for name in ('Stone','Stone mosaic','Optics','Greenery','Layer stacks','White arch','Confirm history','Unresolved history'):
                evaluate("Array.from(document.querySelectorAll('#queues button')).find(b=>b.firstChild.textContent==="+json.dumps(name)+").click(); true")
                assert evaluate("document.getElementById('position').textContent !== '0 / 0'")
            # Full CLI re-ingestion must retain the same confirmed outcome.
            result = subprocess.run([sys.executable,str(Path(__file__).with_name('meta_loop.py')),
                '--data',str(data),'next','--element',event['element']], capture_output=True,text=True,timeout=180)
            assert result.returncode==0, result.stderr
            plan = json.loads(result.stdout)
            assert plan['learned_best'] is not None
            after_rows = json.loads((data/'ledger.json').read_text())
            assert ml.owner_outcome(next(r for r in after_rows if r['trial_id']==event['trial_id']))==1
            report = dict(ok=True, engine='agent-browser --engine lightpanda',
                temporary_copy=True, posted_trial_id=event['trial_id'], synthetic_event_id=event['event_id'],
                save_and_refresh_seconds=latency, next_learned_best=plan['learned_best'],
                checks=['HTTP readiness','plinth front-face default','LOOK/CLEAR side-by-side','L mode cycle','judged_on persisted','live refresh preserves draft','keyboard stars/verdict','Z max-zoom','space target flip',
                        'pairwise arrow preference','Enter durable POST','next-batch UI refresh',
                        'note input shortcut isolation','previous navigation','all queue navigation',
                        'full CLI re-ingestion preserves label'], browser_calls=len(calls))
        finally:
            try:
                browser('close')
            finally:
                server.shutdown();server.server_close();thread.join()
    after = owner.read_bytes() if owner.exists() else None
    assert before == after, 'Real owner event file changed during synthetic test'
    report['real_owner_file_unchanged'] = True
    report['real_owner_file_sha256'] = hashlib.sha256(after).hexdigest() if after is not None else None
    ui.atomic_json(args.receipt, report)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
