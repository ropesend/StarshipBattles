# Tools/captioning — Visual Asset Caption Authoring

Pre-bake structured JSON captions for the game's visual assets (flags, race
portraits, ship themes) so the in-game LLM narrative generator (PROJ-299)
can describe them without needing a multimodal model at runtime.

This tool **does not generate captions itself.** Captions are produced
by a vision-capable LLM and saved to JSON sidecars next to the source
images. Two workflows are supported, depending on what kind of LLM you
have available.

## Recommended workflow — single master prompt (file-aware agent)

If you have a vision LLM with filesystem access (Gemini Flash via the
file API, Claude with file tools, or any agent that can both view
images and write files), use the master prompt at
[`gemini_master_prompt.md`](gemini_master_prompt.md). Paste it into
your agent in one shot; it will discover every uncaptioned asset, view
each image, write the sidecar JSON to the correct path, and run the
validator at the end. This is the fastest path: one prompt, ~5–10
minutes, all 38 sidecars produced and verified.

The master prompt is idempotent — re-running it after a partial run
skips assets that already have a sidecar.

## Manual fallback workflow — paste-per-image (web UI)

If your vision LLM only runs in a browser tab without file access
(stock Gemini web UI, etc.), use the per-category prompts and paste
them by hand:

1. **Open Gemini** (or another vision-capable LLM) in your browser.
2. **Upload the image.** For multi-resolution flags (which have several
   PNG sizes) any resolution is fine — Gemini sees the same picture.
3. **Paste the corresponding capture prompt** from `prompts/`:
   - Flags → `prompts/flag_prompt.md`
   - Race portraits → `prompts/portrait_prompt.md`
   - Ship themes → `prompts/theme_prompt.md`
4. **Save Gemini's JSON output** to the sidecar location next to the asset:
   - Flag: `assets/images/flags/Processed/<flag_id>/<flag_id>.caption.json`
   - Portrait: `assets/images/race_portraits/<portrait_filename>.caption.json`
   - Theme: `assets/images/ship_themes/<theme_name>/theme.caption.json`
5. **Validate** with `python Tools/captioning/validate_captions.py`. The
   tool reports any sidecars that are missing, malformed, or fail schema
   validation.

The manual workflow is also the right choice when you only need to
regenerate or hand-fix a single caption.

## Schema versions

All schemas are at `schema_version: 1`. If the schema ever changes, bump
the version and update the validator to accept multiple versions during
the migration window.

## Why pre-baked, not runtime?

- Cheap: the runtime LLM (DeepSeek) is text-only, ~10x cheaper than vision.
- Fast: no vision-call latency at description-generation time.
- Stable: captions are deterministic across game runs.
- Reviewable: caption JSON sits in git, so you can read/edit them.

## Total work for the user

38 captions to generate (15 flags + 14 portraits + 9 themes). With the
master prompt: ~5–10 minutes one autonomous run. With the manual
fallback: ~1 minute per asset, ~40 minutes one-time.
