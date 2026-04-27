# Phase 2: Caption loader [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-299 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** `RaceCaptionLoader.load_flag(flag_id) / load_portrait(portrait_id) / load_theme(theme_id)` — returns parsed sidecar dict or None. Graceful degradation on missing/malformed.

---

## Tasks

### Task 2.1: Create test fixtures [Simple]
**File:** `tests/fixtures/captions/*.caption.json` (NEW)
**Tests:** N/A (data only)

- [ ] Create `tests/fixtures/captions/flag_minimal.caption.json` — only required fields
- [ ] Create `tests/fixtures/captions/flag_full.caption.json` — all fields populated
- [ ] Create `tests/fixtures/captions/portrait_full.caption.json`
- [ ] Create `tests/fixtures/captions/theme_full.caption.json`
- [ ] Create `tests/fixtures/captions/malformed.caption.json` — invalid JSON to verify graceful failure

**Notes:**

### Task 2.2: Implement `RaceCaptionLoader` [Medium]
**File:** `game/strategy/data/race_caption_loader.py` (NEW)
**Tests:** `pytest tests/unit/strategy/data/test_race_caption_loader.py`

- [ ] Write failing tests (TDD):
  - `load_flag(flag_id)` returns parsed dict when sidecar exists
  - `load_flag(flag_id)` returns None when sidecar missing
  - `load_flag(flag_id)` returns None and logs warning when JSON is malformed
  - `load_flag(flag_id)` returns None and logs warning when required fields missing (schema validation lite)
  - Same three behaviors for `load_portrait(portrait_id)` and `load_theme(theme_id)`
  - Loader is stateless — multiple instances do not interfere
  - Sidecar paths are constructed via `game.core.paths.Paths` (no hardcoded paths)
- [ ] Implement per design.md:
  - `class RaceCaptionLoader` with three load methods
  - Use `game.core.json_utils.load_json` (returns default on failure — already logs)
  - Validate the loaded dict has at least `schema_version: 1` (defensive minimum check; full schema validation is the validator tool's job)
  - Sidecar locations:
    - Flag: `<ASSETS>/Images/Flags/Processed/<flag_id>/<flag_id>.caption.json`
    - Portrait: `<ASSETS>/Images/Race Portraits/<portrait_id>.caption.json`
    - Theme: `<ASSETS>/ShipThemes/<theme_id>/theme.caption.json`
- [ ] Run tests, confirm all pass

**Notes:**

### Task 2.3: Add to package exports [Simple]
**File:** `game/strategy/data/__init__.py` (or wherever the package's `__all__` lives)
**Tests:** Smoke import

- [ ] Verify `RaceCaptionLoader` can be imported from `game.strategy.data`
- [ ] Add to `__all__` if the package uses one

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] ~8 new tests in `test_race_caption_loader.py`
- [ ] `pytest tests/unit/strategy/data/` — all green
- [ ] No regression in baseline
- [ ] Update status at top of this file to `Complete`
- [ ] Update `plan.md` phase table row to `Complete`
- [ ] Update `plan.md` Current State to point to Phase 3
