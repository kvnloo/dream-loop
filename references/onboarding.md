# Image generation onboarding

Read this on the **first Dream Loop run**, or whenever image generation is missing.

Ask the user which backend to use. Do not silently create a ComfyUI venv or call a paid API to “see if it works.”

1. **Host tool** — If the agent runtime already has an image-generation tool (Codex, Grok, etc.), use that for `target.png` and asset extracts.
2. **API keys** — OpenAI (`OPENAI_API_KEY`), xAI/Grok (`XAI_API_KEY` or `GROK_API_KEY`), or Fal Flux (`FAL_KEY` / `FAL_API_KEY`).
3. **ComfyUI** — Ask whether to **set up** ComfyUI or **point at an existing venv**:
   - Existing install: `COMFYUI_PATH` (ComfyUI root) and/or `COMFY_VENV` (that environment’s Python, e.g. `/path/to/ComfyUI/venv`). If a server is already running, `COMFY_URL` or `COMFYUI_URL`.
   - New install: follow ComfyUI’s own docs; only proceed if the user asked you to set it up.

List what is configured without spending:

```sh
node /path/to/dream-loop/scripts/image-generate.mjs --check
```

That command does not call paid APIs. If nothing is configured, stop and ask for a target image or credentials rather than inventing a procedural fallback.
