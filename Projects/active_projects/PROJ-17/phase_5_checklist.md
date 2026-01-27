# Phase 5: Audit Fixes (Cycle 1) [Medium Risk]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-17 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Pending
**Objective:** Address issues found in Audit Cycle 1 - complete ShipThemeManager migration.

**Tests to run after phase:** `pytest tests/unit/ui/ tests/unit/entities/test_ship_theme_logic.py -v`

---

## Task 5.1: Update Files Importing from Orphaned Location [Medium]

These 6 files import from `game/ui/renderer/ship_theme` instead of `game/ui/assets`:

### game/ui/renderer/renderer.py (line 40)
- [ ] Change `from game.ui.renderer.ship_theme import ShipThemeManager` to `from game.ui.assets import ShipThemeManager`
- [ ] Change all `.get_instance()` calls to `.instance()`
- [ ] Verify no other references to old module

### game/ui/screens/builder/main.py (line 25)
- [ ] Change import to `from game.ui.assets import ShipThemeManager`
- [ ] Change all `.get_instance()` calls to `.instance()`
- [ ] Verify no other references to old module

### tests/unit/test_regressions.py
- [ ] Update ShipThemeManager import to `from game.ui.assets import ShipThemeManager`
- [ ] Update any mock/patch paths

### tests/unit/test_ship_classes.py
- [ ] Update ShipThemeManager import to `from game.ui.assets import ShipThemeManager`
- [ ] Update any mock/patch paths

### tests/unit/test_ship_theme_logic.py
- [ ] Verify import is correct (was reported as needing update)
- [ ] Update if needed

### tests/unit/verify_themes.py
- [ ] Update ShipThemeManager import to `from game.ui.assets import ShipThemeManager`
- [ ] Update any mock/patch paths

**Notes:**

---

## Task 5.2: Update Rendering Test Mock Paths [Simple]

### tests/unit/ui/test_rendering_logic.py (line 60)
- [ ] Change patch path from `game.simulation.ship_theme.ShipThemeManager` to match actual import location of code under test
- [ ] Verify test still passes

### tests/unit/test_rendering_logic.py (line 60)
- [ ] Change patch path from `game.simulation.ship_theme.ShipThemeManager` to match actual import location of code under test
- [ ] Verify test still passes

**Notes:**

---

## Task 5.3: Delete Orphaned ShipThemeManager [Simple]

**File to delete:** `game/ui/renderer/ship_theme.py`

- [ ] Verify no remaining imports from this file: `grep -rn "from game.ui.renderer.ship_theme" game/ tests/`
- [ ] Delete the file: `rm game/ui/renderer/ship_theme.py`
- [ ] Verify tests pass without it

**Notes:**

---

## Phase 5 Verification

After completing all tasks:

- [ ] Run: `pytest tests/unit/ui/ -v` (should all pass)
- [ ] Run: `pytest tests/unit/entities/test_ship_theme_logic.py -v` (should pass)
- [ ] Run: `pytest tests/unit/test_regressions.py tests/unit/test_ship_classes.py -v` (should pass)
- [ ] Verify file deleted: `ls game/ui/renderer/ship_theme.py` (should fail - file not found)
- [ ] Verify no imports from deleted location: `grep -rn "from game.ui.renderer.ship_theme" .` (should return nothing)
- [ ] Run full test suite: `pytest tests/`

**Phase complete when all boxes checked.**
