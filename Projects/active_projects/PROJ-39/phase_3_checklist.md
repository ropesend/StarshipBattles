# Phase 3: Strategy Layer

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-39 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Eliminate os.getcwd() patterns and dirname chains in strategy layer

---

## Tasks

### Task 3.1: Update game/strategy/systems/save_game_service.py [Complex]
**File:** `game/strategy/systems/save_game_service.py`
**Tests:** `pytest tests/ -v -k save` + manual save/load test

This file has **6+ os.getcwd() calls** that need replacement.

- [ ] Add import: `from game.core.paths import Paths`
- [ ] Replace `DEFAULT_SAVES_FOLDER = "saves"` (line 26) with:
  ```python
  DEFAULT_SAVES_FOLDER = Paths.SAVES_DIR
  ```
- [ ] Replace all `os.getcwd()` patterns:
  - Line 58: `os.path.join(os.getcwd(), "saves", ...)` → `os.path.join(Paths.SAVES_DIR, ...)`
  - Line 164: similar pattern
  - Line 254: similar pattern
  - Line 297: similar pattern
  - Line 339: similar pattern
  - Line 435: similar pattern
- [ ] Search for any remaining `os.getcwd()` in this file
- [ ] Test save game functionality
- [ ] Test load game functionality

**Notes:**

### Task 3.2: Update game/strategy/systems/race_library.py [Medium]
**File:** `game/strategy/systems/race_library.py`
**Tests:** `pytest tests/ -v -k race`

This file has a **4-level dirname chain** that's fragile.

- [ ] Add import: `from game.core.paths import Paths`
- [ ] Remove the dirname chain (lines 55-59):
  ```python
  # REMOVE:
  # base_path = os.path.dirname(os.path.dirname(os.path.dirname(
  #     os.path.dirname(os.path.abspath(__file__)))))
  # self.races_folder = os.path.join(base_path, "races")
  ```
- [ ] Replace with:
  ```python
  self.races_folder = Paths.RACES_DIR
  ```
- [ ] Verify race loading works

**Notes:**

### Task 3.3: Update game/strategy/systems/design_library.py [Medium]
**File:** `game/strategy/systems/design_library.py`
**Tests:** `pytest tests/ -v -k design`

- [ ] Add import: `from game.core.paths import Paths`
- [ ] Replace any hardcoded paths or temp folder references
- [ ] Replace any `os.getcwd()` patterns
- [ ] Verify design storage works

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] No `os.getcwd()` calls remain in updated files:
  ```bash
  grep -n "os.getcwd()" game/strategy/systems/save_game_service.py
  grep -n "os.getcwd()" game/strategy/systems/race_library.py
  grep -n "os.getcwd()" game/strategy/systems/design_library.py
  ```
- [ ] No dirname chains remain in updated files
- [ ] Save/load game works from any working directory
- [ ] Race loading works
- [ ] Full test suite passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
