import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import http from 'node:http';
import net from 'node:net';
import os from 'node:os';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const PNG = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a5XcAAAAASUVORK5CYII=', 'base64');
const SCRIPT = fileURLToPath(new URL('./preview-server.py', import.meta.url));

function freePort() {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.listen(0, '127.0.0.1', () => {
      const { port } = server.address();
      server.close(err => err ? reject(err) : resolve(port));
    });
    server.on('error', reject);
  });
}

function request(port, method, urlPath, { body, headers } = {}) {
  return new Promise((resolve, reject) => {
    const req = http.request({ hostname: '127.0.0.1', port, path: urlPath, method, headers }, res => {
      const chunks = [];
      res.on('data', chunk => chunks.push(chunk));
      res.on('end', () => resolve({ status: res.statusCode, headers: res.headers, body: Buffer.concat(chunks) }));
    });
    req.on('error', reject);
    if (body) req.write(body);
    req.end();
  });
}

async function requestRetry(port, method, urlPath, options = {}) {
  let last;
  for (let i = 0; i < 25; i++) {
    try { return await request(port, method, urlPath, options); } catch (error) {
      last = error;
      await new Promise(resolve => setTimeout(resolve, 40));
    }
  }
  throw last;
}

function waitForServer(child, port) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      cleanup();
      reject(new Error('preview-server did not start'));
    }, 8000);
    const onData = chunk => {
      if (String(chunk).includes(`127.0.0.1:${port}`)) {
        cleanup();
        resolve();
      }
    };
    const onError = err => { cleanup(); reject(err); };
    const onExit = code => { cleanup(); reject(new Error(`preview-server exited ${code}`)); };
    const cleanup = () => {
      clearTimeout(timer);
      child.stdout.off('data', onData);
      child.off('error', onError);
      child.off('exit', onExit);
    };
    child.stdout.on('data', onData);
    child.on('error', onError);
    child.on('exit', onExit);
  });
}

test('preview-server serves compare, captures atomically, and denies other dotfiles', async t => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'preview-server-'));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  fs.writeFileSync(path.join(dir, '.env'), 'SECRET=1\n');
  fs.mkdirSync(path.join(dir, '.dream-loop'), { recursive: true });
  fs.writeFileSync(path.join(dir, '.dream-loop', 'target.png'), PNG);
  const port = await freePort();
  const child = spawn('python3', [SCRIPT, '--directory', dir, '--port', String(port)], {
    stdio: ['ignore', 'pipe', 'pipe'],
    env: { ...process.env, PYTHONUNBUFFERED: '1' },
  });
  t.after(() => { child.kill('SIGTERM'); });
  await waitForServer(child, port);

  const compare = await requestRetry(port, 'GET', '/__compare');
  assert.equal(compare.status, 200);
  assert.match(compare.body.toString(), /target \| live|dream-loop compare/);

  const denied = await requestRetry(port, 'GET', '/.env');
  assert.equal(denied.status, 404);

  const capture = await requestRetry(port, 'POST', '/__capture', {
    body: PNG, headers: { 'Content-Type': 'image/png', 'Content-Length': String(PNG.length) },
  });
  assert.equal(capture.status, 200);
  const latest = path.join(dir, '.dream-loop', 'captures', 'latest.png');
  assert.deepEqual(fs.readFileSync(latest), PNG);

  const live = await requestRetry(port, 'GET', '/.dream-loop/captures/latest.png');
  assert.equal(live.status, 200);
  assert.deepEqual(live.body, PNG);
});
