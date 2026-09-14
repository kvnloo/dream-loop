#!/usr/bin/env node
// Fal queue helper. No dependencies; Node 18+. Run --help for the job format.
import fs from 'node:fs';
import net from 'node:net';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

export function parseConcurrency(value, fallback = 4) {
  const n = typeof value === 'number' ? value : Number(value);
  if (!Number.isFinite(n) || n < 0) return fallback;
  return n;
}

export function workerCount(concurrency, jobCount) {
  const n = Math.max(0, Number(jobCount) || 0);
  if (n === 0) return 0;
  const c = parseConcurrency(concurrency, 4);
  if (c <= 0) return 1;
  return Math.min(Math.floor(c), n);
}

export function jailedResolve(root, relative, label = 'path') {
  if (typeof relative !== 'string' || !relative) throw new Error(`${label} is required.`);
  const resolved = path.resolve(root, relative);
  const rel = path.relative(root, resolved);
  if (rel.startsWith('..') || path.isAbsolute(rel)) throw new Error(`${label} escapes the jobs file directory: ${relative}`);
  return resolved;
}

function asFile(value) {
  if (value == null) return null;
  if (typeof value === 'string' && value) return { url: value };
  if (typeof value === 'object' && typeof value.url === 'string' && value.url) return value;
  return null;
}

function isFbx(file) {
  const name = String(file.file_name || file.fileName || '').toLowerCase();
  if (name.endsWith('.fbx')) return true;
  const type = String(file.content_type || file.contentType || '').toLowerCase();
  if (type.includes('fbx')) return true;
  const raw = String(file.url || '').split('?')[0].toLowerCase();
  try {
    if (new URL(file.url).pathname.toLowerCase().endsWith('.fbx')) return true;
  } catch {
    if (raw.endsWith('.fbx')) return true;
  }
  return false;
}

export function selectModelFile(result, input = {}) {
  const urls = result?.model_urls && typeof result.model_urls === 'object' && !Array.isArray(result.model_urls)
    ? result.model_urls : {};
  const ordered = [];
  if (input.pbr) ordered.push(asFile(urls.pbr_model));
  ordered.push(asFile(urls.glb), asFile(result.model_glb), asFile(result.model_mesh));
  const present = ordered.filter(Boolean);
  const glb = present.find(file => !isFbx(file));
  if (glb?.url) return glb;
  if (present.some(isFbx)) throw new Error('Completed result has only an FBX mesh; no GLB URL was returned.');
  throw new Error('Completed result has no model file URL.');
}

export function assertAllowedDownloadUrl(urlString) {
  let u;
  try { u = new URL(urlString); } catch { throw new Error('Unexpected model download URL.'); }
  if (u.protocol !== 'https:' || u.username || u.password) throw new Error('Unexpected model download URL.');
  const host = u.hostname.toLowerCase().replace(/\.$/, '');
  if (net.isIP(host) || host === 'internal' || host.endsWith('.internal')) {
    throw new Error('Model download host is not an allowed Fal CDN.');
  }
  const allowed = host === 'queue.fal.run' || host === 'fal.media' || host.endsWith('.fal.media')
    || host === 'fal.ai' || host.endsWith('.fal.ai');
  if (!allowed) throw new Error('Model download host is not an allowed Fal CDN.');
  return u;
}

function validatePlan(data, { inputChecks = true, base } = {}) {
  if (!Array.isArray(data.jobs) || !data.jobs.length) throw new Error('jobs must be a nonempty array.');
  const ids = new Set();
  for (const job of data.jobs) {
    if (!job.id || ids.has(job.id)) throw new Error('Each job needs a unique id.');
    ids.add(job.id);
    if (!/^[\w.-]+\/[\w./-]+$/.test(job.endpoint) || job.endpoint.includes('..')) throw new Error(`Invalid endpoint: ${job.id}`);
    if (!job.image || !job.output) throw new Error(`Missing image/output: ${job.id}`);
    if (base) {
      jailedResolve(base, job.image, `${job.id} image`);
      jailedResolve(base, job.output, `${job.id} output`);
    }
    // Accepted jobs must remain collectable using their returned URLs even if their inputs were invalid.
    if (!inputChecks || job.request_id) continue;
    if (job.endpoint === 'fal-ai/trellis/image-to-3d') throw new Error(`${job.id}: single-image Trellis uses fal-ai/trellis (no /image-to-3d suffix).`);
    const input = job.input || {};
    if (typeof input !== 'object' || Array.isArray(input)) throw new Error(`${job.id}: input must be an object.`);
    if ('image_url' in input) throw new Error(`${job.id}: use the local image field; the helper supplies image_url.`);
    if (job.endpoint === 'fal-ai/trellis') {
      for (const field of ['face_limit', 'texture', 'pbr']) if (field in input) throw new Error(`${job.id}: ${field} is an H3.1 option, not a Trellis option.`);
      if ('texture_size' in input && ![512, 1024, 2048].includes(input.texture_size)) throw new Error(`${job.id}: Trellis texture_size must be 512, 1024, or 2048.`);
      if ('mesh_simplify' in input && !(typeof input.mesh_simplify === 'number' && input.mesh_simplify >= 0.9 && input.mesh_simplify <= 0.98)) {
        throw new Error(`${job.id}: mesh_simplify must be a number from 0.9 to 0.98.`);
      }
    }
    if (job.endpoint === 'tripo3d/h3.1/image-to-3d') {
      for (const field of ['mesh_simplify', 'texture_size']) if (field in input) throw new Error(`${job.id}: ${field} is a Trellis option, not an H3.1 option.`);
      if ('face_limit' in input && !(Number.isInteger(input.face_limit) && input.face_limit >= 1000 && input.face_limit <= 2_000_000)) {
        throw new Error(`${job.id}: face_limit must be an integer from 1000 to 2000000.`);
      }
    }
  }
}

function imageMime(bytes) {
  if (bytes.subarray(0, 8).equals(Buffer.from([137,80,78,71,13,10,26,10]))) return 'image/png';
  if (bytes[0] === 255 && bytes[1] === 216) return 'image/jpeg';
  if (bytes.toString('ascii',0,4) === 'RIFF' && bytes.toString('ascii',8,12) === 'WEBP') return 'image/webp';
  throw new Error('Input must be a nonempty PNG, JPEG, or WebP.');
}

function errorDetail(body, key) {
  // Select only human-readable error fields. Never retain echoed inputs or raw bodies.
  const clean = value => String(value).split(key).join('[redacted]')
    .replace(/data:[^\s"']+/gi, '[image redacted]')
    .replace(/https?:\/\/[^\s"']+/gi, '[URL redacted]')
    .replace(/[A-Za-z0-9+/_=-]{80,}/g, '[payload redacted]').slice(0, 400);
  const detail = body?.detail;
  if (Array.isArray(detail)) return detail.slice(0, 5).map(item => {
    const loc = Array.isArray(item.loc) ? item.loc.map(clean).join('.').slice(0, 160) : '';
    return [loc, clean(item.msg || item.type || 'Validation failed')].filter(Boolean).join(': ');
  }).join('; ');
  for (const value of [detail, body?.message, body?.error]) if (typeof value === 'string') return clean(value);
  return undefined;
}

export async function runBatch(command, filename, { concurrency = 4, fetchFn = fetch, key = process.env.FAL_KEY || process.env.FAL_API_KEY } = {}) {
  if (!['check', 'submit', 'collect'].includes(command)) throw new Error('Use check, submit or collect.');
  const absolute = path.resolve(filename), base = path.dirname(absolute);
  if (command === 'check') {
    const data = JSON.parse(fs.readFileSync(absolute, 'utf8')); validatePlan(data, { base });
    return data.jobs.map(job => {
      const file = jailedResolve(base, job.image, `${job.id} image`);
      try {
        if (!job.request_id && (job.status_url || job.response_url || job.cancel_url)) return { id: job.id, state: 'missing-request-id', error: 'Recover the original request_id before proceeding.' };
        if (['submitting', 'submission-uncertain'].includes(job.state)) return { id: job.id, state: job.state };
        if (!fs.existsSync(file)) return { id: job.id, state: 'waiting-for-image' };
        imageMime(fs.readFileSync(file));
        return { id: job.id, state: job.request_id ? 'already-submitted' : 'ready' };
      } catch (error) { return { id: job.id, state: 'invalid-image', error: error.message }; }
    });
  }
  if (!key) throw new Error('Set FAL_KEY or FAL_API_KEY in the environment.');
  const lock = absolute + '.lock';
  const fd = fs.openSync(lock, 'wx');
  try {
    const data = JSON.parse(fs.readFileSync(absolute, 'utf8'));
    validatePlan(data, { inputChecks: command !== 'collect', base });
    const save = () => {
      fs.writeFileSync(absolute + '.tmp', JSON.stringify(data, null, 2) + '\n');
      fs.renameSync(absolute + '.tmp', absolute);
    };
    const request = async (url, payload) => {
      const u = new URL(url);
      if (u.protocol !== 'https:' || u.hostname !== 'queue.fal.run' || u.username || u.password) throw new Error('Unexpected Fal queue URL.');
      const response = await fetchFn(url, {
        method: payload ? 'POST' : 'GET', redirect: 'error',
        headers: { Authorization: `Key ${key}`, ...(payload ? { 'Content-Type': 'application/json' } : {}) },
        ...(payload ? { body: JSON.stringify(payload) } : {}), signal: AbortSignal.timeout(60000),
      });
      if (!response.ok) {
        const error = new Error(`Fal HTTP ${response.status}`); error.status = response.status;
        try { error.detail = errorDetail(await response.json(), key); } catch { /* No raw HTML/body in logs. */ }
        throw error;
      }
      return response.json();
    };
    const work = async job => {
      let stage = command;
      try {
        if (command === 'submit') {
          // Never automatically repeat an accepted or uncertain paid submission.
          if (job.request_id || job.state === 'submitting' || job.state === 'submission-uncertain') return;
          if (job.status_url || job.response_url || job.cancel_url) throw new Error('Existing queue URLs have no request_id. Recover the original record; do not submit it again.');
          const imagePath = jailedResolve(base, job.image, `${job.id} image`);
          if (!fs.existsSync(imagePath)) { job.state = 'waiting-for-image'; save(); return; }
          const bytes = fs.readFileSync(imagePath);
          const mime = imageMime(bytes);
          job.state = 'submitting'; job.submitted_at = new Date().toISOString(); delete job.error; delete job.error_detail; delete job.error_stage; delete job.connection_error; save();
          const result = await request(`https://queue.fal.run/${job.endpoint}`, {
            ...job.input, image_url: `data:${mime};base64,${bytes.toString('base64')}`,
          });
          for (const field of ['request_id', 'status_url', 'response_url', 'cancel_url']) if (result[field]) job[field] = result[field];
          save();
          if (!result.request_id || !result.status_url || !result.response_url) throw new Error('Submission omitted request ID or queue URLs.');
          Object.assign(job, { request_id: result.request_id, status_url: result.status_url,
            response_url: result.response_url, cancel_url: result.cancel_url, state: result.status || 'IN_QUEUE' });
        } else {
          if (!job.request_id || job.state === 'downloaded' || job.terminal) return;
          stage = 'status';
          const status = await request(job.status_url);
          job.state = status.status; job.checked_at = new Date().toISOString(); delete job.error; delete job.error_detail; delete job.error_stage; delete job.connection_error; save();
          if (status.status === 'FAILED' || status.status === 'CANCELLED') {
            Object.assign(job, {
              state: 'result-error', terminal: true, fal_status: status.status,
              error_stage: 'status', error: `Fal job ${status.status}`,
            });
          } else if (status.status === 'COMPLETED') {
            stage = 'result';
            const result = await request(job.response_url);
            const file = selectModelFile(result, job.input || {});
            assertAllowedDownloadUrl(file.url);
            stage = 'download';
            // Do not forward the Fal credential to the output-file host.
            const response = await fetchFn(file.url, { signal: AbortSignal.timeout(120000) });
            if (!response.ok) throw new Error(`Model download HTTP ${response.status}`);
            const bytes = Buffer.from(await response.arrayBuffer());
            if (bytes.length < 20 || bytes.toString('ascii',0,4) !== 'glTF' || bytes.readUInt32LE(4) !== 2 || bytes.readUInt32LE(8) !== bytes.length) throw new Error('Output is not a complete GLB 2.0 file.');
            const output = jailedResolve(base, job.output, `${job.id} output`);
            fs.mkdirSync(path.dirname(output), { recursive: true });
            fs.writeFileSync(output + '.part', bytes); fs.renameSync(output + '.part', output);
            Object.assign(job, { state: 'downloaded', bytes: bytes.length, downloaded_at: new Date().toISOString() });
          }
        }
      } catch (error) {
        const connectionCode = error.cause?.code;
        const neverConnected = ['ENOTFOUND', 'EAI_AGAIN', 'ECONNREFUSED', 'ENETUNREACH', 'EHOSTUNREACH', 'UND_ERR_CONNECT_TIMEOUT'].includes(connectionCode);
        if (job.state === 'submitting') {
          job.state = neverConnected || ([429, 503].includes(error.status) && !job.request_id) ? 'not-submitted'
            : [400, 401, 403, 404, 405, 422].includes(error.status) ? 'rejected' : 'submission-uncertain';
        }
        if (stage === 'result' || stage === 'download') job.state = `${stage}-error`;
        job.error_stage = stage;
        if (error.detail) job.error_detail = error.detail;
        if (connectionCode) job.connection_error = connectionCode;
        // Avoid echoing service payloads, source images, or credentials into logs.
        job.error = /^Fal HTTP \d+$|^Model download HTTP \d+$/.test(error.message) ? error.message : error.message.includes(key) ? 'Request failed; credential redacted.' : error.message;
      }
      save();
    };
    const pending = [...data.jobs];
    await Promise.all(Array.from({ length: workerCount(concurrency, pending.length) }, async () => {
      while (pending.length) await work(pending.shift());
    }));
    return data.jobs.map(({ id, state, request_id, bytes, error, error_detail, error_stage, connection_error, terminal }) => ({ id, state, request_id, bytes, error, error_detail, error_stage, connection_error, terminal }));
  } finally { fs.closeSync(fd); fs.unlinkSync(lock); }
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  if (process.argv.includes('--help')) {
    console.log('Usage: node fal-batch.mjs check|submit|collect JOBS.json [CONCURRENCY]\ncheck is offline and needs no API key. Paths are relative to JOBS.json and must stay inside that directory. CONCURRENCY 0 runs serially. Examples:\n' + JSON.stringify({ jobs: [
      { id: 'gate', endpoint: 'tripo3d/h3.1/image-to-3d', image: 'assets/gate.png', output: 'models/gate.glb', input: { texture: true, pbr: true, face_limit: 80000 } },
      { id: 'rubble', endpoint: 'fal-ai/trellis', image: 'assets/rubble.png', output: 'models/rubble.glb', input: { mesh_simplify: 0.95, texture_size: 1024 } },
    ] }, null, 2));
  } else {
    const command = process.argv[2];
    runBatch(command, process.argv[3], { concurrency: parseConcurrency(process.argv[4], 4) })
      .then(rows => {
        if (command === 'check') console.log(JSON.stringify({ jobCount: rows.length, jobs: rows }, null, 2));
        else console.log(JSON.stringify(rows, null, 2));
        if (rows.some(row => row.error)) process.exitCode = 1;
      })
      .catch(error => { console.error(error.message); process.exitCode = 1; });
  }
}
