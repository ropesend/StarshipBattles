# Phase 1: Infrastructure

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-26 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create the centralized paths module and update constants.py

---

## Tasks

### Task 1.1: Create game/core/paths.py [Medium]
**File:** `game/core/paths.py` (NEW)
**Tests:** `pytest tests/unit/core/ -v`

- [ ] Create `game/core/paths.py` with the implementation from design.md
- [ ] Include `_find_project_root()` function with marker-based detection
- [ ] Include `Paths` class with all path constants
- [ ] Include pathlib.Path accessor classmethods
- [ ] Include backward-compatible module-level exports
- [ ] Verify module imports without errors: `python -c "from game.core.paths import Paths; print(Paths.ROOT_DIR)"`

**Path Constants to Include:**
```
Directories: ROOT_DIR, GAME_DIR, CORE_DIR, DATA_DIR, ASSET_DIR, SHIPS_DIR,
             SAVES_DIR, RACES_DIR, SCREENSHOTS_DIR, FORMATIONS_DIR,
             TECH_PRESETS_DIR, BATTLES_DIR, SHIP_THEMES_DIR, IMAGES_DIR,
             COMPONENTS_IMAGES_DIR

Files:       COMPONENTS_FILE, MODIFIERS_FILE, VEHICLE_CLASSES_FILE,
             VEHICLE_LAYERS_FILE, RESOURCES_FILE, COMBAT_STRATEGIES_FILE,
             ASSET_MANIFEST_FILE, BATTLE_LOG, CRASH_LOG, PROFILING_HISTORY
```

**Notes:**

### Task 1.2: Update game/core/constants.py [Simple]
**File:** `game/core/constants.py`
**Tests:** `pytest tests/unit/core/ -v`

- [ ] Add import: `from game.core.paths import Paths`
- [ ] Replace local ROOT_DIR calculation with `ROOT_DIR = Paths.ROOT_DIR`
- [ ] Replace local GAME_DIR calculation with `GAME_DIR = Paths.GAME_DIR`
- [ ] Replace local CORE_DIR calculation with `CORE_DIR = Paths.CORE_DIR`
- [ ] Replace other path constants to use Paths class
- [ ] Keep the deprecated comment for old code
- [ ] Verify existing imports still work: `python -c "from game.core.constants import ROOT_DIR; print(ROOT_DIR)"`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `python -c "from game.core.paths import Paths; print(Paths.DATA_DIR)"` works
- [ ] `python -c "from game.core.constants import ROOT_DIR; print(ROOT_DIR)"` works
- [ ] All existing tests pass: `pytest tests/ -v`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
