# FEAT-13: Generate visual asset captions for race images (LLM description metadata)

## Description
PROJ-296/299 wired the Race Setup Description tab to an LLM
(`RaceDescriptionLLMController`) that loads `.caption.json` sidecars for each
visual asset (flags, race portraits, ship themes) and embeds them into the
biological / sociological description prompts.

The infrastructure is in place (loader, schema, prompt builder, graceful
fallback), but **no caption sidecars currently exist** on disk. The LLM
therefore receives the placeholder `{"note": "no visual reference available
for this asset"}` for every asset, producing generic descriptions that don't
reflect what the player actually sees.

This feature populates the missing caption data.

## Scope
Generate `.caption.json` sidecars for every existing visual asset, conforming
to the schemas in `Tools/captioning/schemas/` (schema_version 1):

- **Flags** (~15 assets) → `assets/Images/Flags/Processed/{flag_id}/{flag_id}.caption.json`
  (fields: geometry, color_palette, symbolism, cultural_hints, mood, distinctive_traits)
- **Race Portraits** (~14 assets) → `assets/Images/Race Portraits/{filename}.caption.json`
  (fields: anatomy, coloration, attire_and_adornment, posture_and_expression,
  technology_level_hint, distinctive_traits)
- **Ship Themes** (~8 assets) → `assets/ShipThemes/{theme_id}/theme.caption.json`
  (fields: hull_geometry, materials_and_finish, design_philosophy, color_scheme,
  technology_level_hint, distinctive_traits)

The captioning toolchain already exists at `Tools/captioning/` with prompt
templates and a Gemini-vision-based generation flow.

## Acceptance
- All existing flags, race portraits, and ship themes have a `.caption.json`
  sidecar that passes `Tools/captioning/validate_captions.py`.
- A regenerated bio/socio description on a known race visibly references
  visual traits (anatomy, palette, geometry) instead of generic species filler.
- New asset additions document the captioning step (extend
  `Tools/captioning/README.md` if needed).

## Priority
Medium

## Status
Pending

## Work Log
- 2026-04-27: Created from QA Session 20260427_151244.
