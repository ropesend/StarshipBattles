# Phase 2: Path Constant Import Migration [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-58 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate 23 import sites from `game.core.constants` path re-exports to `game.core.paths.Paths`, plus 2 WIDTH/HEIGHT sites.

---

## Tasks

### Task 2.1: Migrate Path Constants in Production Code [Simple]
**Files:** 10 production files
**Tests:** `pytest tests/unit/ui/ tests/integration/ui/ -x`

Change `from game.core.constants import ROOT_DIR, DATA_DIR, ...` → `from game.core.paths import Paths` then use `Paths.ROOT_DIR`, etc.

- [ ] `game/core/screenshot_manager.py:6` - `ROOT_DIR, DEBUG_SCREENSHOTS, SCREENSHOT_DIR` → `Paths.ROOT_DIR`, `Paths.SCREENSHOTS_DIR` (keep DEBUG_SCREENSHOTS from constants)
- [ ] `game/research/data/tech_tree.py:9` - `DATA_DIR` → `Paths.DATA_DIR`
- [ ] `game/ui/assets/ship_theme_manager.py:7` - `ASSET_DIR` → `Paths.ASSET_DIR`
- [ ] `game/ui/panels/race_portrait_gallery.py:17` - `ASSET_DIR` → `Paths.ASSET_DIR`
- [ ] `game/ui/panels/race_flag_gallery.py:17` - `ASSET_DIR` → `Paths.ASSET_DIR`
- [ ] `game/ui/screens/race_setup_screen.py:22` - `ASSET_DIR` → `Paths.ASSET_DIR`
- [ ] `game/ui/screens/race_asset_loader.py:14` - `ASSET_DIR` → `Paths.ASSET_DIR`
- [ ] `game/ui/screens/planet_list_presets.py:6` - `DATA_DIR` → `Paths.DATA_DIR`
- [ ] `game/ui/screens/strategy_ui.py:20` - `DATA_DIR` → `Paths.DATA_DIR`
- [ ] `game/ui/screens/workshop_screen.py:99,259` - `ROOT_DIR, DATA_DIR, ASSET_DIR` → `Paths.*`
- [ ] Run tests: `pytest tests/unit/ui/ tests/integration/ui/ -x`
**Notes:** For each file: add `from game.core.paths import Paths`, replace references, remove old import.

### Task 2.2: Migrate Path Constants in Test/Script Code [Simple]
**Files:** 12 test/script files
**Tests:** `pytest tests/repro_issues/ tests/unit/performance/ -x`

- [ ] `tests/infrastructure/session_cache.py:54` - `DATA_DIR` → `Paths.DATA_DIR`
- [ ] `tests/repro_issues/test_bug_08_fuel_validation.py:12` - `COMPONENTS_FILE, VEHICLE_CLASSES_FILE` → `Paths.*`
- [ ] `tests/repro_issues/test_bug_09_endurance.py:10` - `COMPONENTS_FILE` → `Paths.COMPONENTS_FILE`
- [ ] `tests/repro_issues/test_bug_12_hull_layer_addition.py:12` - `COMPONENTS_FILE` → `Paths.COMPONENTS_FILE`
- [ ] `tests/unit/performance/profile_simulation.py:23` - `COMPONENTS_FILE, MODIFIERS_FILE` → `Paths.*`
- [ ] `tests/unit/performance/reproduce_scaling.py:6` - `COMPONENTS_FILE, MODIFIERS_FILE` → `Paths.*`
- [ ] `tests/unit/performance/strategy_tournament.py:28` - `SHIPS_DIR, COMPONENTS_FILE, MODIFIERS_FILE` → `Paths.*`
- [ ] `tests/unit/performance/stress_test.py:18` - `COMPONENTS_FILE, MODIFIERS_FILE` → `Paths.*`
- [ ] `tests/unit/ui/test_theme_discovery.py:7` - `ASSET_DIR` → `Paths.ASSET_DIR`
- [ ] `scripts/verify_determinism_current.py:16` - `COMPONENTS_FILE, MODIFIERS_FILE` → `Paths.*`
- [ ] `scripts/repro_shield.py:10` - `COMPONENTS_FILE` → `Paths.COMPONENTS_FILE`
- [ ] `scripts/repro_energy_stats.py:10` - `COMPONENTS_FILE` → `Paths.COMPONENTS_FILE`
- [ ] Run tests: `pytest tests/repro_issues/ tests/unit/performance/ -x`

### Task 2.3: Migrate WIDTH/HEIGHT Imports [Simple]
**Files:** 2 files
**Tests:** `pytest tests/unit/ui/ -x`
- [ ] `game/ui/screens/test_lab_screen.py:9` - Remove `WIDTH, HEIGHT` from import, add `from game.core.config import DisplayConfig`, use `DisplayConfig.DEFAULT_WIDTH`/`DEFAULT_HEIGHT`
- [ ] `game/ui/screens/test_lab.py:9` - Same migration
- [ ] Run tests: `pytest tests/unit/ui/ -x`
**Notes:** These imports also pull WHITE, BLACK, BLUE, FONT_MAIN from constants - only migrate WIDTH/HEIGHT.

### Task 2.4: Remove Path Re-exports from constants.py and paths.py [Simple]
**File:** `game/core/constants.py`, `game/core/paths.py`
**Tests:** `pytest tests/ -x` (full suite)
- [ ] `game/core/constants.py` - Remove lines 54-58 (WIDTH, HEIGHT re-exports and DisplayConfig import)
- [ ] `game/core/constants.py` - Remove lines 64-78 (ROOT_DIR, GAME_DIR, CORE_DIR, ASSET_DIR, DATA_DIR, SHIPS_DIR, SCREENSHOT_DIR, COMPONENTS_FILE, MODIFIERS_FILE, VEHICLE_CLASSES_FILE)
- [ ] `game/core/constants.py` - Remove the `from game.core.paths import Paths` import IF only used for re-exports
- [ ] `game/core/paths.py` - Remove lines 130-141 (backward compat module-level exports)
- [ ] Run full test suite: `pytest tests/ -x`
**Notes:** Only do this AFTER Tasks 2.1-2.3 are complete.

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
