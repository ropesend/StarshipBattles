# PROJ-299: Race Description Generator (LLM) — Design

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to [decisions.md](decisions.md).

---

## Project shape

This is a **consumer** of PROJ-296 (LLM Service Foundation). It is the first one — the patterns set here become the canonical reference for diplomacy and any other future LLM consumer.

```
┌─────────────────────────────────────────────────────────────────┐
│  Tools/captioning/         (one-time external authoring)        │
│  ├─ schemas/{flag,portrait,theme}.schema.json                  │
│  ├─ prompts/{flag,portrait,theme}_prompt.md  → user pastes     │
│  │                                              into Gemini    │
│  └─ validate_captions.py   → "missing/invalid sidecars: N"     │
└─────────────────────────────────────────────────────────────────┘
                                 │ (writes 37 sidecar files)
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  assets/Images/Flags/Processed/flag_<id>/flag_<id>.caption.json │
│  assets/Images/Race Portraits/<file>.caption.json              │
│  assets/ShipThemes/<theme>/theme.caption.json                  │
└─────────────────────────────────────────────────────────────────┘
                                 │ (read at runtime)
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  RaceCaptionLoader  ──→  RaceDescriptionPromptBuilder           │
│  (game/strategy/data)    (game/strategy/services, pure fn)      │
└─────────────────────────────────────────────────────────────────┘
                                 │ (yields list[Message])
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  RaceDescriptionLLMController     (game/strategy/services)      │
│  ├─ owns LLMBackgroundCall × 2   (PROJ-296)                     │
│  ├─ tracks status per-field      (IDLE/RUNNING/DONE/ERROR/CAN)  │
│  ├─ dispatches bio + socio in parallel                          │
│  ├─ on_change callback to UI                                    │
│  └─ pygame-free                                                 │
└─────────────────────────────────────────────────────────────────┘
                                 │ (on_change → rebuild)
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  RaceDescriptionPanel + RaceSetupScreen                         │
│  ├─ 2 Generate buttons (bio, socio)                             │
│  ├─ 2 Cancel buttons (visible while RUNNING)                    │
│  ├─ 2 Re-roll buttons (visible after first DONE)                │
│  ├─ 2 status labels (below text boxes)                          │
│  ├─ text boxes locked while RUNNING                             │
│  ├─ 30s "still working" modal (re-armed at 90s)                 │
│  ├─ per-error-type popup                                        │
│  └─ kill() hook → controller.cancel_all()                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Module placement

All within established layers (no new layer rule needed):

| Module | Layer | Why |
|--------|-------|-----|
| `Tools/captioning/*` | Tools (outside layer hierarchy) | Authoring scripts; no production dep |
| `game/strategy/data/race_caption_loader.py` | Strategy data | Mirrors `homeworld_presets.py`, `classification_config.py` — JSON-loading pattern |
| `game/strategy/services/race_description_prompt_builder.py` | Strategy services | Pure transform, mirrors `build_test_battle_spec` style |
| `game/strategy/services/race_description_llm_controller.py` | Strategy services | Pygame-free state machine; UI polls it. Strategy may import from `game.services.llm` per PROJ-296 layer rule. |
| `game/ui/panels/race_description_panel.py` | UI | Existing file — receives buttons, status labels, gets `controller` injected |
| `game/ui/screens/race_setup_screen.py` | UI | Existing file — slim event routing, polling, kill hook |

---

## Caption schemas (final)

Three asset-specific schemas. All have `schema_version: 1` for forward-compatibility.

### `flag.schema.json`
```json
{
  "schema_version": 1,
  "geometry": "string — shapes, divisions, dominant motifs",
  "color_palette": "string — primary/secondary/accent colours, with hex if extractable",
  "symbolism": "string — what the marks/icons evoke",
  "cultural_hints": "string — what kind of society would adopt this",
  "mood": "enum: patriotic | aggressive | peaceful | mysterious | unified | technological | religious | naturalistic",
  "distinctive_traits": "string — anything unusual or memorable"
}
```

### `portrait.schema.json`
```json
{
  "schema_version": 1,
  "anatomy": "string — body plan, distinctive features (limbs, eyes, skin/scale/fur)",
  "coloration": "string — hue, pattern, contrast",
  "attire_and_adornment": "string — clothing, jewelry, tools, scars, paint",
  "posture_and_expression": "string — bearing, gaze, mood",
  "technology_level_hint": "enum: primitive | medieval | industrial | advanced | post-human | unknown",
  "distinctive_traits": "string — anything unusual or memorable"
}
```

### `theme.schema.json`
```json
{
  "schema_version": 1,
  "hull_geometry": "string — silhouette, symmetry, sectional shapes",
  "materials_and_finish": "string — apparent materials, surface treatment, weathering",
  "design_philosophy": "string — what the engineering choices imply (speed/durability/elegance/intimidation)",
  "color_scheme": "string — palette, accent placement",
  "technology_level_hint": "enum: primitive | medieval | industrial | advanced | post-human | unknown",
  "distinctive_traits": "string — anything unusual or memorable"
}
```

Sidecar locations:
- Flag: `assets/Images/Flags/Processed/flag_<id>/flag_<id>.caption.json` (one per flag dir, NOT per shape × resolution)
- Portrait: next to the image, `<portrait>.caption.json`
- Theme: `assets/ShipThemes/<theme>/theme.caption.json`

---

## Prompt assembly (final)

### Bio prompt — system message

A single fixed system prompt, ~280 tokens, including:
- Role: "You are a lore writer for a 4X space strategy game…"
- Output spec: "Write a single biological description, ~200-250 words, plain prose, no markdown."
- Tone: "Immersive, specific, slightly poetic. Avoid generic sci-fi clichés. Show, don't tell."
- ONE example bio (~150 tokens) for the fictional Zarlith species, demonstrating tone

### Socio prompt — system message

Same shape, focused on society/culture. Includes ONE example socio.

### User message (assembled per-call)

A JSON payload combining:
- `identity`: race_name, faction_name, government_type/organization, leader_title/name, physical_type, society_type
- `aptitudes`: 7 stats with values + their human-meaning labels (from `race_aptitudes_panel.py:APTITUDE_DISPLAY_NAMES`)
- `environment`: render each `EnvironmentalPreference` via FACTOR_REGISTRY (`display_name` + `display_unit` + `display_scale` + `display_precision`)
- `homeworld_type` (subordinate)
- `flag_caption`, `portrait_caption`, `theme_caption`: parsed sidecars OR `{"note": "no visual reference"}` if missing

### Why JSON in the user message
- Easy to assemble programmatically
- Easy for the LLM to parse and ignore unfamiliar fields
- Easy to debug by reading the prompt log

---

## RaceDescriptionLLMController state machine

Two parallel sub-machines (one per field — bio, socio):

```
   ┌──────┐  generate()    ┌─────────┐  call.status==DONE  ┌──────┐
   │ IDLE │ ──────────────▶│ RUNNING │ ──────────────────▶ │ DONE │
   └──────┘                └─────────┘                     └──────┘
       ▲                       │                              │
       │                       │ call.status==ERROR           │ re_roll()
       │                       ▼                              │
       │                   ┌───────┐                          │
       │                   │ ERROR │ ◀────────────────────────┤
       │                   └───────┘                          │
       │                       │                              │
       │ dismiss_error()       │                              │
       └───────────────────────┘                              │
                                                              │
       ┌─────────┐  cancel()                                  │
       │ CANCELLED│◀────────── (any non-IDLE state) ◀─────────┘
       └─────────┘
              │ generate() / re_roll()
              ▼
        (back to RUNNING)
```

### Public API
```python
class RaceDescriptionLLMController:
    def __init__(
        self,
        race_config: RaceConfig,
        provider: LLMProvider,
        caption_loader: RaceCaptionLoader,
        on_change: Callable[[], None],
    ) -> None: ...

    # Per-field actions
    def generate_bio(self) -> None: ...      # Idempotent if RUNNING
    def generate_socio(self) -> None: ...
    def re_roll_bio(self) -> None: ...        # Cancels prior + starts new
    def re_roll_socio(self) -> None: ...
    def cancel_bio(self) -> None: ...         # Logical cancel
    def cancel_socio(self) -> None: ...
    def cancel_all(self) -> None: ...         # Called from screen.kill()

    # Per-field state (read by UI per frame)
    @property
    def bio_status(self) -> FieldStatus: ...  # IDLE/RUNNING/DONE/ERROR/CANCELLED
    @property
    def socio_status(self) -> FieldStatus: ...
    @property
    def bio_elapsed_seconds(self) -> float: ...
    @property
    def socio_elapsed_seconds(self) -> float: ...
    @property
    def bio_error(self) -> Optional[LLMException]: ...
    @property
    def socio_error(self) -> Optional[LLMException]: ...

    # Main update — called every frame from RaceSetupScreen.update()
    def update(self) -> None:
        """Poll the LLMBackgroundCalls; transition state on completion;
        invoke on_change callback when state changes; populate
        race_config.bio_description / socio_description on DONE."""
```

### `on_change` triggers
- Status transition (IDLE → RUNNING, RUNNING → DONE, etc.)
- Result populated (text written into race_config)
- Error encountered

The UI's panel rebuilds itself from the controller state when `on_change` fires (button visibility, status label text, text-box lock state).

---

## UI integration

### Buttons on the Description tab
| State | Bio buttons visible | Socio buttons visible |
|-------|---------------------|------------------------|
| Both IDLE (initial) | [Generate Bio] | [Generate Socio] |
| Bio RUNNING, Socio IDLE | [Generate Bio (disabled)] [Cancel Bio] | [Generate Socio] |
| Bio DONE, Socio IDLE | [Generate Bio] [Re-roll Bio] | [Generate Socio] |
| Both DONE | [Generate Bio] [Re-roll Bio] | [Generate Socio] [Re-roll Socio] |

### Status labels (below text boxes)
- IDLE: hidden / empty
- RUNNING: "Generating Bio… 12s" (live timer)
- DONE: "Generated 47s ago" (or hide after a few seconds)
- ERROR: "Bio generation failed" (red text)
- CANCELLED: hidden / empty

### Text box lock
Text boxes are `disabled` while `bio_status == RUNNING` (or `socio_status` for the socio box). On state transition out of RUNNING, re-enable.

### 30s + 90s modal dialog flow
- Screen polls `controller.bio_elapsed_seconds` and `socio_elapsed_seconds` each frame
- When EITHER passes 30s and is still RUNNING, show modal (single modal even if both fields qualify)
- Modal: "Still generating after 30 seconds. Keep waiting or stop?" + [Keep Waiting] [Stop]
- "Keep Waiting" → close modal; flag re-arm threshold = 90s
- "Stop" → controller.cancel_all() (or just the qualifying field?)
- At 90s if still RUNNING, modal re-appears
- LLM `timeout_seconds=90` is passed on `complete()` so the network timeout fires shortly after the second modal — user sees a final timeout error popup rather than waiting forever

---

## Risks already mitigated in design

| Risk (Phase B) | Mitigation in design |
|---|---|
| Screen closed mid-call | `RaceSetupScreen.kill()` → `controller.cancel_all()` |
| Double-click spam | Generate button is `enabled` only when status == IDLE |
| Half-populated state | Bio + socio are independent; user re-rolls the failed one. Save is allowed in any combination. |
| Re-roll race | `re_roll_bio()` calls `cancel_bio()` first |
| MAX_CONCURRENT_CALLS exceeded | Catch `LLMConfigError` from `LLMBackgroundCall.start()` → show "too many requests" popup |
| MAX_LENGTH=5000 char-label overflow | Phase 7 task: widen the char-count label to fit 4-digit values |
| Caption sidecar missing | Loader returns None → builder injects `{"note": "no visual reference"}` |

---

## Test strategy

### Test directory layout (mirrors source per `docs/03_CONVENTIONS.md` §4.1)
```
tests/unit/strategy/
├── data/
│   └── test_race_caption_loader.py
└── services/
    ├── test_race_description_prompt_builder.py
    └── test_race_description_llm_controller.py

tests/unit/ui/
├── panels/
│   └── test_race_description_panel.py    (extend; add ~6 tests)
└── screens/
    └── test_race_setup_screen.py          (extend; add ~6 tests)

tests/regression/
└── test_caption_schemas_validate.py        (sanity: shipped schemas are valid JSON Schema)

tests/fixtures/
└── captions/
    ├── flag_minimal.caption.json
    ├── flag_full.caption.json
    ├── portrait_full.caption.json
    ├── theme_full.caption.json
    └── malformed.caption.json
```

### Critical fixtures
- `mock_llm_provider` (already exists in `tests/unit/services/llm/conftest.py`) — reuse via the conftest hierarchy
- `stub_llm_provider` (already exists) — for controller tests
- New: `caption_fixtures_dir` pytest fixture pointing at `tests/fixtures/captions/`

### Estimated test count (per Phase B Test Impact)
| Phase | Tests | Notes |
|-------|-------|-------|
| 1 | ~6 | Schema validity + validator tool integration |
| 2 | ~8 | Loader: present/missing/malformed/wrong-schema |
| 3 | ~16 | Pure function — many edge cases (missing captions, all aptitudes high, exotic envs) |
| 4 | ~12 | Controller state machine (transitions, re-roll, cancel-all, error paths) |
| 5 | ~6 | UI integration (button visibility, status labels, text-box lock) |
| 6 | ~6 | Dialog timing, error popups, kill hook |
| 7 | ~2 | MAX_LENGTH bump regression on the char-label |
| **Total** | **~56** | |

---

## Future extension notes

### Adding a third description type (e.g. "history")

The current design's bio/socio split is hardcoded in the controller. If we add a 3rd type, the controller needs a small refactor toward a registry:

```python
# Hypothetical post-extension shape
controller.start("bio")
controller.start("history")
controller.status_for("socio")
```

Architecture review flagged this; refactor is ~50 LOC if it ever comes up. Defer until requested.

### Adding a new asset type (e.g. "music_theme")

1. Add a 4th caption schema under `Tools/captioning/schemas/`
2. Add a 4th capture prompt under `Tools/captioning/prompts/`
3. Extend `RaceCaptionLoader` with a `load_music_theme()` method
4. Extend the user prompt assembly in `prompt_builder.py` to include the new caption

No controller or UI changes needed.

### Streaming responses

If a real-time use case appears (live narration), PROJ-296 would need to add `LLMProvider.complete_stream()`. This consumer would then add a streaming variant of `generate_bio()`. v1 is sync-only.

### When to swap providers

Set `LLM_PROVIDER` env var to a different name registered with `LLMProviderFactory`. PROJ-296's factory dispatch is data-driven, so adding `OpenAIProvider` or `AnthropicProvider` is a one-line change in their respective module's `register_provider()` call. This consumer is provider-agnostic.
