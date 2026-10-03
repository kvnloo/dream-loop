import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { checkBackends, listBackends } from './image-generate.mjs';

test('listBackends reads env without treating empty strings as configured', () => {
  const none = checkBackends({ PATH: '/usr/bin' });
  assert.equal(none.ok, false);
  assert.equal(none.configuredCount, 0);
  assert.deepEqual(listBackends({}).map(item => item.id), ['host-tool', 'grok/xai', 'openai', 'comfy', 'fal-flux']);
  const some = checkBackends({ OPENAI_API_KEY: 'sk-test', COMFY_VENV: '/opt/ComfyUI/venv' });
  assert.equal(some.ok, true);
  assert.equal(some.configuredCount, 2);
});

test('--check reports backends and exits 1 when none are configured', () => {
  const script = fileURLToPath(new URL('./image-generate.mjs', import.meta.url));
  const env = { PATH: process.env.PATH, HOME: process.env.HOME || '' };
  const empty = spawnSync(process.execPath, [script, '--check'], { encoding: 'utf8', env });
  assert.equal(empty.status, 1);
  const parsed = JSON.parse(empty.stdout);
  assert.equal(parsed.ok, false);
  const ready = spawnSync(process.execPath, [script, '--check'], {
    encoding: 'utf8', env: { ...env, FAL_KEY: 'test-only-key' },
  });
  assert.equal(ready.status, 0);
  assert.equal(JSON.parse(ready.stdout).ok, true);
});
