# Phase 3: Prompt assembly layer [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-299 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Pure module-level functions `build_bio_prompt(race_config, captions) -> list[Message]` and `build_socio_prompt(race_config, captions) -> list[Message]`. Includes few-shot examples in system prompt. Handles missing captions gracefully via `{"note": "no visual reference"}` in the prompt.

---

## Tasks

### Task 3.1: Implement `build_bio_prompt` [Complex]
**File:** `game/strategy/services/race_description_prompt_builder.py` (NEW)
**Tests:** `pytest tests/unit/strategy/services/test_race_description_prompt_builder.py`

- [x] Write failing tests (TDD; this is the densest test set in the project — pure function, lots of edge cases):
  - `build_bio_prompt(race_config, captions)` returns a `list[Message]` with at least 2 messages: one SYSTEM, one USER
  - System message includes the bio few-shot example (verify by content substring)
  - User message includes race identity (race_name, faction_name, government_type, society_type)
  - User message includes all 7 aptitudes with display names ("Strength: 75", etc. — verify mapping from `aptitude_*` field to display name)
  - User message includes environmental preferences in human-readable form (e.g., "Gravity: 9.81 m/s² (≈1.0 g) ±2.0")
  - User message includes flag caption content when provided
  - User message includes `{"note": "no visual reference"}` when caption is None for one or more assets
  - User message includes `homeworld_type` (subordinate)
  - Result is deterministic for identical input (no hidden randomness)
- [x] Implement `build_bio_prompt(race_config: RaceConfig, captions: Dict[str, Optional[dict]]) -> List[Message]`:
  - Constants: `SYSTEM_PROMPT_BIO` (system message text including the few-shot example), `USER_PROMPT_TEMPLATE_BIO` (or build dynamically)
  - Helper: `_render_aptitudes(race_config) -> str` (use `APTITUDE_DISPLAY_NAMES` from `race_aptitudes_panel.py`)
  - Helper: `_render_preferences(race_config) -> str` (iterate FACTOR_REGISTRY, use `display_name`/`display_unit`/`display_scale`/`display_precision`)
  - Helper: `_render_caption_or_note(caption) -> str` (returns the JSON or the explicit note marker)
- [x] Run tests, confirm pass

**Notes:**

### Task 3.2: Implement `build_socio_prompt` [Medium]
**File:** Same file as 3.1
**Tests:** Same file

- [x] Write failing tests (mirror 3.1's tests for the socio variant)
- [x] Implement `build_socio_prompt(...)` — same structure, different SYSTEM_PROMPT (focused on society/culture) and few-shot example
- [x] DRY check: extract shared helpers (`_render_aptitudes`, `_render_preferences`, `_render_caption_or_note`) so both functions reuse them
- [x] Run tests, confirm pass

**Notes:**

### Task 3.3: Verify prompt output by eye [Simple]
**File:** N/A (manual)
**Tests:** N/A

- [x] Construct a sample `RaceConfig` (use the QS race fixture or a fresh one)
- [x] Call `build_bio_prompt(...)` with full captions; print the messages to console
- [x] Manually verify the prompt reads like a coherent instruction to an LLM
- [x] Estimate the token count (rough: `len(text) / 4`); confirm well under 2000 tokens for input
- [x] Document any phrasing tweaks in the task notes

**Notes:**

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] ~16 new tests in `test_race_description_prompt_builder.py`
- [x] `pytest tests/unit/strategy/services/` — all green
- [x] No regression in baseline
- [x] Update status at top of this file to `Complete`
- [x] Update `plan.md` phase table row to `Complete`
- [x] Update `plan.md` Current State to point to Phase 4
