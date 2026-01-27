# Phase 3: Strategy Layer

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-26 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate strategy layer files - eliminate os.getcwd() and dirname chains

---

## Tasks

### Task 3.1: Migrate game/strategy/systems/save_game_service.py [Complex]
**File:** `game/strategy/systems/save_game_service.py`
**Tests:** `pytest tests/unit/strategy/ -v` and manual save/load test

- [ ] Add import: `from game.core.paths import Paths`
- [ ] Replace `DEFAULT_SAVES_FOLDER = "saves"` with direct use of `Paths.SAVES_DIR`
- [ ] Replace ALL `os.getcwd()` occurrences (6+ instances):
  - Line ~58: `os.path.join(os.getcwd(), DEFAULT_SAVES_FOLDER)`
  - Line ~164: Similar pattern
  - Line ~254: Similar pattern
  - Line ~297: Similar pattern
  - Line ~339: Similar pattern
  - Line ~435: Similar pattern
- [ ] Search file for any remaining `os.getcwd()` calls
- [ ] Verify save game creates files in correct location
- [ ] Verify load game finds saved files

**Notes:** This is the highest-risk file. Test thoroughly.

### Task 3.2: Migrate game/strategy/systems/race_library.py [Medium]
**File:** `game/strategy/systems/race_library.py`
**Tests:** `pytest tests/unit/strategy/ -v`

- [ ] Add import: `from game.core.paths import Paths`
- [ ] Remove the 4-level dirname chain (lines ~55-59):
  ```python
  # REMOVE:
  # base_path = os.path.dirname(os.path.dirname(os.path.dirname(
  #     os.path.dirname(os.path.abspath(__file__)))))
  # self.races_folder = os.path.join(base_path, "races")
  ```
- [ ] Replace with: `self.races_folder = Paths.RACES_DIR`
- [ ] Verify race library loads races correctly

**Notes:**

### Task 3.3: Migrate game/strategy/systems/design_library.py [Medium]
**File:** `game/strategy/systems/design_library.py`
**Tests:** `pytest tests/unit/strategy/ -v`

- [ ] Add import: `from game.core.paths import Paths`
- [ ] Identify all hardcoded paths and temp folder references
- [ ] Replace with appropriate Paths constants
- [ ] Verify design library functions correctly

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] No `os.getcwd()` calls remain in strategy layer: `grep -r "os.getcwd()" game/strategy/ --include="*.py"`
- [ ] No dirname chains remain: `grep -r "dirname.*dirname.*dirname" game/strategy/ --include="*.py"`
- [ ] Save/Load game works correctly (manual test)
- [ ] Race selection works in game UI
- [ ] All existing tests pass: `pytest tests/ -v`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
