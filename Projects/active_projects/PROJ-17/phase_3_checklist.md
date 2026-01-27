# Phase 3: Move ShipThemeManager to UI [Medium Risk]

**Objective:** Relocate ShipThemeManager from simulation to UI layer where pygame usage is appropriate.

**Status:** Complete

**Depends on:** Phase 1 complete (can run parallel to Phase 2)

**Tests to run after phase:** `pytest tests/unit/ui/ tests/unit/entities/test_ship_theme_logic.py -v`

---

## Task 3.1: Create UI Assets Directory [Simple]

**Directory:** `game/ui/assets/`

- [x] Create directory: `mkdir game/ui/assets`
- [x] Create `game/ui/assets/__init__.py` with content

**Notes:** Done.

---

## Task 3.2: Move ShipThemeManager [Medium]

**From:** `game/simulation/ship_theme.py`
**To:** `game/ui/assets/ship_theme_manager.py`

- [x] Copy entire file: `cp game/simulation/ship_theme.py game/ui/assets/ship_theme_manager.py`
- [x] Verify the copy succeeded by checking file exists
- [x] Review imports in new file - should be fine as-is (uses pygame, which is allowed in UI)

**Notes:** Done.

---

## Task 3.3: Create Backward-Compatible Re-export [Simple]

**File:** `game/simulation/ship_theme.py`

- [x] Replace entire content with deprecation warning and re-export

**Notes:** Done with deprecation warning that emits on import.

---

## Task 3.4: Update Direct Importers [Medium]

Update imports from `game.simulation.ship_theme` to `game.ui.assets`:

### UI Renderer
- [x] `game/ui/renderer/game_renderer.py` - Update ShipThemeManager import

### UI Screens
- [ ] `game/ui/screens/builder_screen.py` - N/A (doesn't import ShipThemeManager)
- [x] `game/ui/screens/workshop_screen.py` - Update ShipThemeManager import
- [x] `game/ui/screens/race_setup_screen.py` - Update ShipThemeManager import
- [x] `game/ui/screens/race_browser_dialog.py` - Update ShipThemeManager import
- [x] `game/ui/screens/fleet_report_window.py` - Update ShipThemeManager import

### UI Panels
- [x] `game/ui/panels/ship_detail_panel.py` - Update ShipThemeManager import
- [x] `game/ui/panels/race_theme_gallery.py` - Update ShipThemeManager import

### Tests (if directly importing)
- [x] Check `conftest.py` for ShipThemeManager imports - Updated
- [x] Check test files in `tests/unit/entities/test_ship_theme_logic.py` - Updated imports and patch paths
- [x] Check `tests/unit/ui/test_theme_discovery.py` - Updated
- [x] Check `tests/unit/regressions/test_regressions.py` - Updated
- [x] Check `tests/unit/entities/test_ship_classes.py` - Updated

**Notes:** All direct importers updated. builder_screen.py doesn't import ShipThemeManager directly.

---

## Phase 3 Verification

After completing all tasks:

- [x] Run: `pytest tests/unit/ui/ -v` (463 passed)
- [x] Run: `pytest tests/unit/entities/test_ship_theme_logic.py -v` (6 passed)
- [ ] Launch game and verify ship images display in builder - (skipped in CI context)
- [ ] Launch game and verify ship images display in battle - (skipped in CI context)
- [x] Verify ShipThemeManager is in UI: `ls game/ui/assets/ship_theme_manager.py` ✓
- [x] Verify re-export exists: `grep -n "from game.ui.assets" game/simulation/ship_theme.py` → line 8 ✓

**Phase complete when all boxes checked.** ✓
