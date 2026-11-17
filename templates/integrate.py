"""Project adapter skeleton: fixed-order, idempotent, guarded integration.

Implement load/guard/apply/fingerprint/save/render on your adapter. Blender:
load a fixture, expose the protected camera/layout/collections in guard, apply
owned bpy edits, save/reopen .blend, render PNG. Three.js/UI: hydrate a versioned
config, expose camera/layout/shared tokens, build/reopen and capture real output.
No generic adapter can prove your identity contract; choose guard fields in BRIEF.
"""
import hashlib
import json
from pathlib import Path

ORDER=('baseline','cleanup','materials','form','fixtures','postprocess')


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def integrate(adapter,fixture,layers,output,artifact_name='artifact.bin',capture_name='capture.bin'):
    fixture=Path(fixture).resolve();output=Path(output).resolve()
    if not fixture.is_file():raise ValueError('fixture missing')
    if output.exists():raise FileExistsError(output)
    if any(Path(n).name!=n or n in {'','.','..'} for n in [artifact_name,capture_name]):
        raise ValueError('output names must be basenames')
    if artifact_name==capture_name or 'receipt.json' in [artifact_name,capture_name]:
        raise ValueError('output names collide')
    ids=[layer['id'] for layer in layers]
    if len(ids)!=len(set(ids)):raise ValueError('duplicate layer IDs')
    if any(layer['stage'] not in ORDER for layer in layers):raise ValueError('unknown stage')
    if sum(layer['stage']=='postprocess' for layer in layers)>1:raise ValueError('one postprocess/bloom owner')
    ordered=sorted(layers,key=lambda x:(ORDER.index(x['stage']),x['id']))
    input_hash=sha(fixture);state=adapter.load(fixture)
    # Immutable snapshot: a guard may return a reference into mutable state.
    protected=json.dumps(adapter.guard(state),sort_keys=True)
    for layer in ordered:adapter.apply(state,layer)
    first=adapter.fingerprint(state)
    for layer in ordered:adapter.apply(state,layer)
    if adapter.fingerprint(state)!=first:raise ValueError('layers are not idempotent')
    if json.dumps(adapter.guard(state),sort_keys=True)!=protected:raise ValueError('protected state drift')
    output.mkdir(parents=True,exist_ok=False)
    artifact=output/artifact_name;capture=output/capture_name
    adapter.save(state,artifact)
    reopened=adapter.load(artifact)
    if json.dumps(adapter.guard(reopened),sort_keys=True)!=protected:raise ValueError('saved artifact guard drift')
    if adapter.fingerprint(reopened)!=first:raise ValueError('save/reopen state drift')
    adapter.render(reopened,capture)
    if not capture.is_file() or not capture.stat().st_size:raise ValueError('no capture produced')
    if sha(fixture)!=input_hash:raise ValueError('fixture was modified')
    result=dict(schema_version=1,status='working-preview',fixture=str(fixture),fixture_sha256=input_hash,
                layers=[x['id'] for x in ordered],idempotence_pass=True,reopened_guard_pass=True,
                artifact={'path':artifact.name,'sha256':sha(artifact)},
                capture={'path':capture.name,'sha256':sha(capture)},owner_gate='not-reviewed')
    with (output/'receipt.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    return result
