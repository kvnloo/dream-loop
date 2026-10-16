#!/usr/bin/env python3
"""Read-only pixel/layout checks in owned chrome-headless-shell; never posts labels."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time
from owner_rating import atomic_json


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url',default='http://127.0.0.1:43220/')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    browser=str(Path.home()/'.local/bin/agent-browser')
    binary=str(Path.home()/'.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell')
    session='owner-rating-pixels-'+str(os.getpid())
    def run(*command):
        p=subprocess.run([browser,'--session',session,'--engine','chrome','--executable-path',binary,
            '--headed','false','--json',*command],capture_output=True,text=True,timeout=60)
        assert p.returncode==0,p.stdout+p.stderr
        value=json.loads(p.stdout)
        assert value.get('success'),value
        return value.get('data',{})
    def js(code):return run('eval',code).get('result')
    def wait(code):
        until=time.monotonic()+30
        while time.monotonic()<until:
            if js(code):return
            time.sleep(.1)
        raise AssertionError('Timed out: '+code)
    def ready():
        wait("document.body.dataset.ready === 'true' && Array.from(document.images).filter(i=>!i.hidden).every(i=>i.complete&&i.naturalWidth>0&&!i.classList.contains('loading'))")
    shots=[]
    def shot(name):
        ready()
        assert js('document.documentElement.scrollWidth <= innerWidth'),'Horizontal page overflow'
        path=args.output/name
        run('screenshot',str(path))
        shots.append(str(path))
    try:
        run('open',args.url);run('set','viewport','1600','1100');shot('RATING-DESKTOP.png')
        js("Array.from(document.querySelectorAll('#queues button')).find(b=>b.firstChild.textContent==='Stone mosaic').click(); true")
        shot('RATING-LOOK-CLEAR.png')
        assert js("document.getElementById('region').value === 'plinth front face'")
        assert js("document.getElementById('judge-mode').value === 'both'")
        assert js("document.getElementById('candidate-image').getBoundingClientRect().right <= document.getElementById('clear-image').getBoundingClientRect().left")
        run('press','l');ready()
        assert js("document.getElementById('judge-mode').value === 'look' && document.getElementById('clear-figure').hidden")
        run('press','l');ready()
        assert js("document.getElementById('judge-mode').value === 'clear'")
        run('press','l');ready()
        for name in ('Optics','Greenery'):
            js("Array.from(document.querySelectorAll('#queues button')).find(b=>b.firstChild.textContent==="+json.dumps(name)+").click(); true")
            shot('RATING-'+name.upper()+'.png')
        # Real keyboard events with actual image decode; do not press rating/save keys.
        run('press','z');ready()
        assert js("document.getElementById('stage').classList.contains('zoomed')")
        shot('RATING-ZOOM.png')
        run('press','Space');ready()
        assert js("document.getElementById('candidate-caption').textContent === 'TARGET FLIP'")
        run('press','Space');run('press','z');ready()
        js("Array.from(document.querySelectorAll('#queues button')).find(b=>b.firstChild.textContent==='White arch').click(); true")
        run('check','#pair');shot('RATING-WHITE-PAIR.png')
        run('click','#theme');shot('RATING-LIGHT.png')
        run('set','viewport','390','844');shot('RATING-MOBILE.png')
        # Controls at bottom of a stacked mobile comparison must also fit.
        run('scrollintoview','#save');shot('RATING-MOBILE-CONTROLS.png')
        js("Array.from(document.querySelectorAll('#queues button')).find(b=>b.firstChild.textContent==='Stone mosaic').click(); true")
        run('scrollintoview','#stage');shot('RATING-LOOK-CLEAR-MOBILE.png')
        errors=run('errors')
        assert not errors.get('errors'),errors
        result=dict(ok=True,engine=binary,screenshots=shots,desktop=[1600,1100],mobile=[390,844],
                    checks=['decoded LOOK/CLEAR/target images','side-by-side geometry','L mode cycle','plinth front-face default','optics and greenery queues','native zoom','target flip','White A/B comparison','dark/light themes',
                            'no horizontal overflow','mobile rating controls','no page errors'],read_only=True)
        atomic_json(args.output/'RATING-VISUAL.json',result)
        print(json.dumps(result,indent=2))
    finally:run('close')


if __name__=='__main__':main()
