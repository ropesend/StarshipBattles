# Phase 3: Strategy Layer

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-39 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Eliminate os.getcwd() patterns and dirname chains in strategy layer

---

## Tasks

### Task 3.1: Update game/strategy/systems/save_game_service.py [Complex] ✓
**File:** `game/strategy/systems/save_game_service.py`
**Tests:** `pytest tests/ -v -k save` + manual save/load test

- [x] Add import: `from game.core.paths import Paths`
- [x] Replace all `os.getcwd()` patterns with `Paths.SAVES_DIR`
- [x] Removed `DEFAULT_SAVES_FOLDER` constant (no longer needed)
- [x] Search for any remaining `os.getcwd()` - None found
- [x] Test save game functionality - passes
- [x] Test load game functionality - passes

**Notes:** This was completed in a previous commit. Tests updated to patch `Paths.SAVES_DIR`.

### Task 3.2: Update game/strategy/systems/race_library.py [Medium] ✓
**File:** `game/strategy/systems/race_library.py`
**Tests:** `pytest tests/ -v -k race`

- [x] Add import: `from game.core.paths import Paths`
- [x] Remove the dirname chain and use `Paths.RACES_DIR`

**Notes:** Done.

### Task 3.3: Update game/strategy/systems/design_library.py [Medium] ✓
**File:** `game/strategy/systems/design_library.py`
**Tests:** `pytest tests/ -v -k design`

- [x] Check for hardcoded paths - None found
- [x] Check for `os.getcwd()` - None found

**Notes:** This file uses the savegame_path provided to it or falls back to tempfile. No project-relative paths needed.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] No `os.getcwd()` calls remain in updated files - Verified
- [x] No dirname chains remain in updated files - Verified
- [x] Save/load game tests pass
- [x] Race loading tests pass
- [x] Full test suite passes (4594 tests)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
