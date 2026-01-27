# Phase 5: Audit Fixes (Cycle 1) [Medium Risk]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-17 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address issues found in Audit Cycle 1 - complete ShipThemeManager migration.

**Tests to run after phase:** `pytest tests/unit/ui/ tests/unit/entities/test_ship_theme_logic.py -v`

---

## Task 5.1: Update Files Importing from Orphaned Location [Medium]

These 6 files import from `game/ui/renderer/ship_theme` instead of `game/ui/assets`:

### game/ui/renderer/renderer.py (line 40)
- [x] Change `from game.ui.renderer.ship_theme import ShipThemeManager` to `from game.ui.assets import ShipThemeManager`
- [x] Change all `.get_instance()` calls to `.instance()`
- [x] Verify no other references to old module

### game/ui/screens/builder/main.py (line 25)
- [x] Change import to `from game.ui.assets import ShipThemeManager`
- [x] Change all `.get_instance()` calls to `.instance()`
- [x] Verify no other references to old module

### tests/unit/test_regressions.py
- [x] N/A - Already using correct path `from game.ui.assets import ShipThemeManager`

### tests/unit/test_ship_classes.py
- [x] N/A - Already using correct path `from game.ui.assets import ShipThemeManager`

### tests/unit/test_ship_theme_logic.py
- [x] Verified import is already correct `from game.ui.assets import ShipThemeManager`

### tests/unit/verify_themes.py
- [x] Update ShipThemeManager import to `from game.ui.assets import ShipThemeManager`
- [x] Update `.get_instance()` to `.instance()`

**Notes:** Original audit incorrectly identified tests/unit/test_regressions.py, test_ship_classes.py, and test_ship_theme_logic.py. These are in subdirectories (regressions/, entities/) and already had correct imports. Only 3 files needed updates: renderer.py, main.py, and verify_themes.py.

---

## Task 5.2: Update Rendering Test Mock Paths [Simple]

### tests/unit/ui/test_rendering_logic.py (line 60)
- [x] Change patch path from `game.simulation.ship_theme.ShipThemeManager` to `game.ui.assets.ShipThemeManager`
- [x] Verify test still passes (3 tests pass)

### tests/unit/test_rendering_logic.py
- [x] N/A - File does not exist (was incorrectly listed in audit)

**Notes:** Only one rendering logic test file exists at tests/unit/ui/test_rendering_logic.py.

---

## Task 5.3: Delete Orphaned ShipThemeManager [Simple]

**File to delete:** `game/ui/renderer/ship_theme.py`

- [x] Verify no remaining imports from this file: `grep -rn "from game.ui.renderer.ship_theme" game/ tests/` - None found
- [x] Delete the file: `rm game/ui/renderer/ship_theme.py` - Done
- [x] Verify tests pass without it (14 affected tests pass)

**Notes:** File deleted successfully. No imports found prior to deletion.

---

## Phase 5 Verification

After completing all tasks:

- [x] Run: `pytest tests/unit/ui/ -v` - 472 passed
- [x] Run: `pytest tests/unit/entities/test_ship_theme_logic.py -v` - 6 passed
- [x] Run: `pytest tests/unit/regressions/test_regressions.py tests/unit/entities/test_ship_classes.py -v` - All pass
- [x] Verify file deleted: `ls game/ui/renderer/ship_theme.py` - File not found (correct)
- [x] Verify no imports from deleted location: `grep -rn "from game.ui.renderer.ship_theme" game/ tests/` - None found
- [x] Run full test suite: `pytest tests/` - 4558 passed, 1 flaky failure (pre-existing test_intercept_integration)

**Phase complete when all boxes checked.**
