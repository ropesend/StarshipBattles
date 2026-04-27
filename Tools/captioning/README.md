# Tools/captioning — Visual Asset Caption Authoring

Pre-bake structured JSON captions for the game's visual assets (flags, race
portraits, ship themes) so the in-game LLM narrative generator (PROJ-299)
can describe them without needing a multimodal model at runtime.

This tool **does not generate captions itself.** You run the prompts in
this directory through Gemini's web UI (or any vision-capable LLM), save
the JSON output to a sidecar file next to the image, and then run the
validator to confirm everything is in place.

## Workflow

For each image you want captioned:

1. **Open Gemini** (or another vision-capable LLM) in your browser.
2. **Upload the image.** For multi-resolution flags (which have several
   PNG sizes) any resolution is fine — Gemini sees the same picture.
3. **Paste the corresponding capture prompt** from `prompts/`:
   - Flags → `prompts/flag_prompt.md`
   - Race portraits → `prompts/portrait_prompt.md`
   - Ship themes → `prompts/theme_prompt.md`
4. **Save Gemini's JSON output** to the sidecar location next to the asset:
   - Flag: `assets/Images/Flags/Processed/<flag_id>/<flag_id>.caption.json`
   - Portrait: `assets/Images/Race Portraits/<portrait_filename>.caption.json`
   - Theme: `assets/ShipThemes/<theme_name>/theme.caption.json`
5. **Validate** with `python Tools/captioning/validate_captions.py`. The
   tool reports any sidecars that are missing, malformed, or fail schema
   validation.

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

Roughly 37 captions to generate (15 flags + 14 portraits + 8 themes).
Each takes ~1 minute in Gemini. Total: ~40 minutes one-time.
