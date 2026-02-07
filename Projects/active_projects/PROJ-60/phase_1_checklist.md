# Phase 1: Create Package & Extract Constants

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-60 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create the `galaxy_test/` package skeleton and extract `constants.py`. Verify the original file still works through the package re-export.

---

## Tasks

### Task 1.1: Create Package Directory and `__init__.py` [Simple]
**File:** `game/ui/screens/galaxy_test/__init__.py`
**Tests:** `pytest tests/ -x -q --tb=short`

- [ ] Create directory `game/ui/screens/galaxy_test/`
- [ ] Create `__init__.py` following `formation/` pattern:
  ```python
  """Galaxy test screen components.

  This package contains the GalaxyTestScreen decomposed into mode-specific modules:
  - GalaxyTestScreen: Main coordinator screen (screen.py)
  """

  from game.ui.screens.galaxy_test.screen import GalaxyTestScreen

  __all__ = ['GalaxyTestScreen']
  ```
- [ ] Note: This will fail until screen.py exists (that's expected at this step)

**Notes:**

### Task 1.2: Extract `constants.py` [Simple]
**File:** `game/ui/screens/galaxy_test/constants.py`
**Source:** `game/ui/screens/galaxy_test_screen.py` lines 22-35 (PLANET_TYPE_COLORS), lines 54-55 (class constants)

- [ ] Create `constants.py` with:
  - `PLANET_TYPE_COLORS` dict (lines 23-35)
  - `SIDEBAR_WIDTH = 320` (line 54)
  - `HEX_SIZE = 10.0` (line 55)
  - Import `PlanetType` from `game.strategy.data.planet`
- [ ] Verify no circular imports by running: `python -c "from game.ui.screens.galaxy_test.constants import PLANET_TYPE_COLORS"`

**Notes:**

### Task 1.3: Copy Original File as `screen.py` [Simple]
**File:** `game/ui/screens/galaxy_test/screen.py`
**Tests:** `pytest tests/ -x -q --tb=short`

- [ ] Copy `galaxy_test_screen.py` to `galaxy_test/screen.py` (full copy, no changes yet)
- [ ] Update `screen.py` to import constants from `constants.py`:
  - Replace `PLANET_TYPE_COLORS` definition with `from game.ui.screens.galaxy_test.constants import PLANET_TYPE_COLORS, SIDEBAR_WIDTH, HEX_SIZE`
  - Remove `PlanetType` import (now comes through constants or keep if needed elsewhere)
  - Replace `self.SIDEBAR_WIDTH` with `SIDEBAR_WIDTH` and `self.HEX_SIZE` with `HEX_SIZE` throughout
- [ ] Update `game/app.py` line 31: change `from game.ui.screens.galaxy_test_screen import GalaxyTestScreen` to `from game.ui.screens.galaxy_test import GalaxyTestScreen`
- [ ] Delete `game/ui/screens/galaxy_test_screen.py`
- [ ] Run `pytest tests/ -x -q --tb=short` - all tests pass (1185+ passed)
- [ ] Verify: `python -c "from game.ui.screens.galaxy_test import GalaxyTestScreen; print('OK')"` prints OK

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `galaxy_test/` package exists with `__init__.py`, `constants.py`, `screen.py`
- [ ] Original `galaxy_test_screen.py` is deleted
- [ ] `app.py` import updated
- [ ] All tests passing
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
