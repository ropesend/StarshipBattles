# Race Description Generation

## Context
QA Session 20260426_083959: on the Race Setup screen Description tab,
the user wants a button that calls an LLM to generate a biological +
sociological description of the race based on every prior choice
(identity, visuals, ships, environment, aptitudes). The generated text
must be consistent with the *visual appearance* of the selected images
(flag, portrait, ship theme).

Today the Description tab is two free-text boxes
([game/ui/panels/race_description_panel.py:120-125](../../game/ui/panels/race_description_panel.py#L120-L125)).

**Depends on:** `llm_provider_abstraction.md` (foundation project — must
land first).

## User Decisions (locked in during triage)

| Decision | Value |
|---|---|
| Image consistency strategy | Pre-bake structured captions via Gemini vision (one-time external run). Narrative model is text-only — does NOT need to be multimodal. |
| Caption schema | Structured (multiple fields) with high level of detail |
| Caption storage | JSON sidecar per asset (next to the image file) |
| Captioning workflow | User runs Gemini externally; this project provides the prompt and the schema spec. The captioning isn't done inside the game. |
| Generated text editable | Yes |
| Re-roll button | Yes |
| Cost UI | None |

## Scope

### Phase 1 — Image caption schema and capturing prompt
- Define a structured JSON schema for image captions
  (`{visual_features, colour_palette, mood, implied_culture,
  technology_level_hint, distinctive_traits}` — exact field set TBD in
  design phase).
- Sidecar location: `<image_path>.caption.json` next to each PNG/JPG.
- Write the Gemini-targeted captioning prompt that produces this schema
  for flags, portraits, and ship themes (three slightly different
  prompts since the categories ask for different information).
- Document a small `Tools/` script that *validates* sidecar files
  against the schema (doesn't generate them — the user runs Gemini
  externally and saves the output).

### Phase 2 — Caption loader
- Module that, given a flag/portrait/theme asset id, returns the
  parsed caption JSON. Returns `None` if the sidecar is missing
  (graceful degradation — generation still runs without image
  awareness, just less specific).

### Phase 3 — Prompt assembly layer
- `RaceDescriptionPromptBuilder.build(race_config, captions) ->
  list[Message]`
- Assembles system + user messages combining: identity choices,
  aptitudes (with their meanings), environmental preferences (made
  human-readable from FACTOR_REGISTRY), and the structured captions
  for the selected images.
- Pure function — fully unit-testable without an LLM.

### Phase 4 — Description tab UI integration
- Add "Generate from choices" button to the Description tab.
- Add "Re-roll" button (visible after the first generation).
- Both buttons run the LLM call on a background thread (using the
  abstraction's threading helper) with a loading indicator, cancel
  support, and error display.
- Generated text populates `bio_description` and `socio_description`
  (the existing text boxes), which remain editable.

### Phase 5 — Polish and tests
- Empty-state handling (no API key set → button disabled with helpful
  tooltip).
- Network error → keep current text, show error popup.
- Tests: prompt builder unit tests, caption loader tests, UI button
  state tests.

## Out of Scope
- In-game image captioning (user runs Gemini externally)
- Streaming token-by-token UI
- Multi-language generation
- Storing generation history / "previous versions" UI
- Auto-regenerate on every choice change

## Scope Notes
This depends on `llm_provider_abstraction.md` and shouldn't start until
that foundation is at least design-complete. The phases above are
mostly sequential — the captioning prompt + schema (Phase 1) is
authoring work the user does once, separate from any code, so it can
proceed in parallel with the other phases as long as Phase 4 can wait
for sidecars to exist before testing image-aware output.
