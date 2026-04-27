# PROJ-299 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `Tools/captioning/README.md` | Tools doc | 1 | NEW — workflow doc |
| `Tools/captioning/schemas/flag.schema.json` | Tools data | 1 | NEW — flag caption JSON schema |
| `Tools/captioning/schemas/portrait.schema.json` | Tools data | 1 | NEW — portrait caption JSON schema |
| `Tools/captioning/schemas/theme.schema.json` | Tools data | 1 | NEW — theme caption JSON schema |
| `Tools/captioning/prompts/flag_prompt.md` | Tools doc | 1 | NEW — Gemini capture prompt for flags |
| `Tools/captioning/prompts/portrait_prompt.md` | Tools doc | 1 | NEW — Gemini capture prompt for portraits |
| `Tools/captioning/prompts/theme_prompt.md` | Tools doc | 1 | NEW — Gemini capture prompt for themes |
| `Tools/captioning/validate_captions.py` | Tools script | 1 | NEW — validator that scans assets/ for sidecars |
| `Tools/captioning/test_validate_captions.py` | Test | 1 | NEW — validator unit tests |
| `tests/regression/test_caption_schemas_validate.py` | Test | 1 | NEW — sanity check on shipped schemas |
| `game/strategy/data/race_caption_loader.py` | Production | 2 | NEW — sidecar loader |
| `tests/unit/strategy/data/test_race_caption_loader.py` | Test | 2 | NEW — loader tests |
| `tests/fixtures/captions/flag_minimal.caption.json` | Test fixture | 2 | NEW |
| `tests/fixtures/captions/flag_full.caption.json` | Test fixture | 2 | NEW |
| `tests/fixtures/captions/portrait_full.caption.json` | Test fixture | 2 | NEW |
| `tests/fixtures/captions/theme_full.caption.json` | Test fixture | 2 | NEW |
| `tests/fixtures/captions/malformed.caption.json` | Test fixture | 2 | NEW — invalid JSON for graceful-failure tests |
| `game/strategy/services/race_description_prompt_builder.py` | Production | 3 | NEW — pure functions `build_bio_prompt` / `build_socio_prompt` |
| `tests/unit/strategy/services/test_race_description_prompt_builder.py` | Test | 3 | NEW — ~16 prompt-builder tests |
| `game/strategy/services/race_description_llm_controller.py` | Production | 4 | NEW — pygame-free state machine |
| `tests/unit/strategy/services/test_race_description_llm_controller.py` | Test | 4 | NEW — ~12 controller tests |
| `game/ui/panels/race_description_panel.py` | Production | 5, 7 | MODIFIED — add buttons + status labels + `set_state()`; bump MAX_LENGTH; widen char-label |
| `tests/unit/ui/test_race_description_panel.py` | Test | 5, 7 | MODIFIED — extend with widget visibility + state tests; update MAX_LENGTH assertions |
| `game/ui/screens/race_setup_screen.py` | Production | 5, 6 | MODIFIED — controller construction, event routing, `update()` polling, kill() hook, dialogs, error popups |
| `tests/unit/ui/screens/test_race_setup_screen.py` | Test | 5, 6 | MODIFIED — extend with controller wiring + dialog + popup + kill tests |
| `docs/02_PATTERNS.md` | Docs | 7 | MODIFIED — add reference-consumer note to Pattern #28 |
| `docs/systems/strategy_layer.md` | Docs | 7 | MODIFIED — brief mention of prompt builder + controller |

## Summary

- **Tools new:** 9 (3 schemas + 3 prompts + 1 README + 1 validator + 1 validator test)
- **Production new:** 3 (caption loader, prompt builder, LLM controller)
- **Production modified:** 2 (race_description_panel, race_setup_screen)
- **Tests new:** 6 (caption schemas regression, loader, prompt builder, controller, 5 fixture files = 1 file + 5 fixtures)
- **Tests modified:** 2 (race_description_panel, race_setup_screen)
- **Test fixtures new:** 5 caption JSONs
- **Docs modified:** 2

**Total: ~30 files touched.**
