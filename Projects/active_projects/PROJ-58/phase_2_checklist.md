# Phase 2: Path Constant Import Migration [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-58 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Migrate 23 import sites from `game.core.constants` path re-exports to `game.core.paths.Paths`, plus 2 WIDTH/HEIGHT sites.

---

## Tasks

### Task 2.1: Migrate Path Constants in Production Code [Simple]
**Files:** 10 production files
**Tests:** `pytest tests/unit/ui/ tests/integration/ui/ -x`

Change `from game.core.constants import ROOT_DIR, DATA_DIR, ...` → `from game.core.paths import Paths` then use `Paths.ROOT_DIR`, etc.

- [x] `game/core/screenshot_manager.py:6` - `ROOT_DIR, DEBUG_SCREENSHOTS, SCREENSHOT_DIR` → `Paths.ROOT_DIR`, `Paths.SCREENSHOTS_DIR` (keep DEBUG_SCREENSHOTS from constants)
- [x] `game/research/data/tech_tree.py:9` - `DATA_DIR` → `Paths.DATA_DIR`
- [x] `game/ui/assets/ship_theme_manager.py:7` - `ASSET_DIR` → `Paths.ASSET_DIR`
- [x] `game/ui/panels/race_portrait_gallery.py:17` - `ASSET_DIR` → `Paths.ASSET_DIR`
- [x] `game/ui/panels/race_flag_gallery.py:17` - `ASSET_DIR` → `Paths.ASSET_DIR`
- [x] `game/ui/screens/race_setup_screen.py:22` - `ASSET_DIR` → `Paths.ASSET_DIR`
- [x] `game/ui/screens/race_asset_loader.py:14` - `ASSET_DIR` → `Paths.ASSET_DIR`
- [x] `game/ui/screens/planet_list_presets.py:6` - `DATA_DIR` → `Paths.DATA_DIR`
- [x] `game/ui/screens/strategy_ui.py:20` - `DATA_DIR` → `Paths.DATA_DIR`
- [x] `game/ui/screens/workshop_screen.py:99,259` - `ROOT_DIR, DATA_DIR, ASSET_DIR` → `Paths.*`
- [x] Run tests: `pytest tests/unit/ui/ tests/integration/ui/ -x`
**Notes:** For each file: add `from game.core.paths import Paths`, replace references, remove old import.

### Task 2.2: Migrate Path Constants in Test/Script Code [Simple]
**Files:** 12 test/script files
**Tests:** `pytest tests/repro_issues/ tests/unit/performance/ -x`

- [x] `tests/infrastructure/session_cache.py:54` - `DATA_DIR` → `Paths.DATA_DIR`
- [x] `tests/repro_issues/test_bug_08_fuel_validation.py:12` - `COMPONENTS_FILE, VEHICLE_CLASSES_FILE` → `Paths.*`
- [x] `tests/repro_issues/test_bug_09_endurance.py:10` - `COMPONENTS_FILE` → `Paths.COMPONENTS_FILE`
- [x] `tests/repro_issues/test_bug_12_hull_layer_addition.py:12` - `COMPONENTS_FILE` → `Paths.COMPONENTS_FILE`
- [x] `tests/unit/performance/profile_simulation.py:23` - `COMPONENTS_FILE, MODIFIERS_FILE` → `Paths.*`
- [x] `tests/unit/performance/reproduce_scaling.py:6` - `COMPONENTS_FILE, MODIFIERS_FILE` → `Paths.*`
- [x] `tests/unit/performance/strategy_tournament.py:28` - `SHIPS_DIR, COMPONENTS_FILE, MODIFIERS_FILE` → `Paths.*`
- [x] `tests/unit/performance/stress_test.py:18` - `COMPONENTS_FILE, MODIFIERS_FILE` → `Paths.*`
- [x] `tests/unit/ui/test_theme_discovery.py:7` - `ASSET_DIR` → `Paths.ASSET_DIR`
- [x] `scripts/verify_determinism_current.py:16` - `COMPONENTS_FILE, MODIFIERS_FILE` → `Paths.*`
- [x] `scripts/repro_shield.py:10` - `COMPONENTS_FILE` → `Paths.COMPONENTS_FILE`
- [x] `scripts/repro_energy_stats.py:10` - `COMPONENTS_FILE` → `Paths.COMPONENTS_FILE`
- [x] Run tests: `pytest tests/repro_issues/ tests/unit/performance/ -x`

### Task 2.3: Migrate WIDTH/HEIGHT Imports [Simple]
**Files:** 2 files
**Tests:** `pytest tests/unit/ui/ -x`
- [x] `game/ui/screens/test_lab_screen.py:9` - Remove `WIDTH, HEIGHT` from import, add `from game.core.config import DisplayConfig`, use `DisplayConfig.DEFAULT_WIDTH`/`DEFAULT_HEIGHT`
- [x] `game/ui/screens/test_lab.py:9` - Same migration
- [x] Run tests: `pytest tests/unit/ui/ -x`
**Notes:** These imports also pull WHITE, BLACK, BLUE, FONT_MAIN from constants - only migrate WIDTH/HEIGHT. Used local aliases for readability.

### Task 2.4: Remove Path Re-exports from constants.py and paths.py [Simple]
**File:** `game/core/constants.py`, `game/core/paths.py`
**Tests:** `pytest tests/ -x` (full suite)
- [x] `game/core/constants.py` - Remove lines 54-58 (WIDTH, HEIGHT re-exports and DisplayConfig import)
- [x] `game/core/constants.py` - Remove lines 64-78 (ROOT_DIR, GAME_DIR, CORE_DIR, ASSET_DIR, DATA_DIR, SHIPS_DIR, SCREENSHOT_DIR, COMPONENTS_FILE, MODIFIERS_FILE, VEHICLE_CLASSES_FILE)
- [x] `game/core/constants.py` - Remove the `from game.core.paths import Paths` import IF only used for re-exports
- [x] `game/core/paths.py` - Remove lines 130-141 (backward compat module-level exports)
- [x] Run full test suite: `pytest tests/ -x`
**Notes:** Discovered missing `from game.core.paths import Paths` import in workshop_screen.py after removing re-exports. Fixed by adding direct import. Also fixed 4 test files that tried to set `builder.ship = ` directly on real DesignWorkshopScreen instances (property is read-only) — changed to `builder.viewmodel._ship = `.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
