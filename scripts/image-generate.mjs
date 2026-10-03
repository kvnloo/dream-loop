#!/usr/bin/env node
// Report configured image backends. Does not call paid APIs.
import path from 'node:path';
import { pathToFileURL } from 'node:url';

export function listBackends(env = process.env) {
  const has = (...keys) => keys.some(key => typeof env[key] === 'string' && env[key].trim());
  return [
    { id: 'host-tool', configured: false, note: 'Use the agent host image tool when the runtime provides one.' },
    { id: 'grok/xai', configured: has('XAI_API_KEY', 'GROK_API_KEY'), env: 'XAI_API_KEY or GROK_API_KEY' },
    { id: 'openai', configured: has('OPENAI_API_KEY'), env: 'OPENAI_API_KEY' },
    { id: 'comfy', configured: has('COMFY_URL', 'COMFYUI_URL', 'COMFYUI_PATH', 'COMFY_VENV'), env: 'COMFY_URL / COMFYUI_URL / COMFYUI_PATH / COMFY_VENV' },
    { id: 'fal-flux', configured: has('FAL_KEY', 'FAL_API_KEY'), env: 'FAL_KEY or FAL_API_KEY' },
  ];
}

export function checkBackends(env = process.env) {
  const backends = listBackends(env);
  const configured = backends.filter(item => item.configured);
  return { backends, configuredCount: configured.length, ok: configured.length > 0 };
}

function printHelp() {
  console.log(`Usage: node image-generate.mjs --check
Reports image backends from the environment without calling paid APIs.
Backends: host-tool, grok/xai, openai, comfy (COMFY_VENV / COMFYUI_PATH / COMFY_URL), fal flux.
See references/onboarding.md.`);
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  if (process.argv.includes('--help')) { printHelp(); process.exit(0); }
  const report = checkBackends();
  if (process.argv.includes('--check')) {
    console.log(JSON.stringify(report, null, 2));
    if (!report.ok) {
      console.error('No image-generation backend is configured. Read references/onboarding.md or provide a target image.');
      process.exitCode = 1;
    }
  } else {
    printHelp();
    console.log(JSON.stringify({ backends: report.backends.map(item => item.id) }, null, 2));
    if (!report.ok) {
      console.error('No image-generation backend is configured. This CLI does not generate images itself.');
      process.exitCode = 1;
    } else {
      console.error('Backends are configured, but this CLI does not call paid APIs. Use --check or the host image tool.');
      process.exitCode = 1;
    }
  }
}
