# Phase 2: Constants & Import Migration [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-56 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate all 41 import sites from re-exported constants to canonical locations.

---

## Tasks

### Task 2.1: Migrate Path Constant Imports in Game Code [Simple]
**Files:** 10 production files
**Tests:** `pytest tests/unit/ui/ tests/integration/ui/ -x`

All these files import path constants from `game.core.constants`. Change to `from game.core.paths import Paths`.

- [ ] `game/core/screenshot_manager.py` - Change `from game.core.constants import ROOT_DIR, SCREENSHOT_DIR` → use `Paths.ROOT_DIR`, `Paths.SCREENSHOTS_DIR`
- [ ] `game/research/data/tech_tree.py` - Change `from game.core.constants import DATA_DIR` → use `Paths.DATA_DIR`
- [ ] `game/ui/assets/ship_theme_manager.py` - Change `from game.core.constants import ASSET_DIR` → use `Paths.ASSET_DIR`
- [ ] `game/ui/panels/race_portrait_gallery.py` - Change `from game.core.constants import ASSET_DIR` → use `Paths.ASSET_DIR`
- [ ] `game/ui/panels/race_flag_gallery.py` - Change `from game.core.constants import ASSET_DIR` → use `Paths.ASSET_DIR`
- [ ] `game/ui/screens/race_setup_screen.py` - Change `from game.core.constants import ASSET_DIR` → use `Paths.ASSET_DIR`
- [ ] `game/ui/screens/race_asset_loader.py` - Change `from game.core.constants import ASSET_DIR` → use `Paths.ASSET_DIR`
- [ ] `game/ui/screens/planet_list_presets.py` - Change `from game.core.constants import DATA_DIR` → use `Paths.DATA_DIR`
- [ ] `game/ui/screens/strategy_ui.py` - Change `from game.core.constants import DATA_DIR` → use `Paths.DATA_DIR`
- [ ] `game/ui/screens/workshop_screen.py` - Change inline imports of `ROOT_DIR, DATA_DIR, ASSET_DIR` (~lines 99, 259) → use `Paths.*`
- [ ] Run tests: `pytest tests/unit/ui/ tests/integration/ui/ -x`
**Notes:** For each file: add `from game.core.paths import Paths` if not present, replace constant references with `Paths.CONSTANT`, remove old import.

### Task 2.2: Migrate Path Constant Imports in Test/Script Code [Simple]
**Files:** 12 test/script files
**Tests:** `pytest tests/repro_issues/ tests/unit/performance/ tests/unit/ui/test_theme_discovery.py -x`

- [ ] `tests/infrastructure/session_cache.py` - `DATA_DIR` → `Paths.DATA_DIR`
- [ ] `tests/repro_issues/test_bug_08_fuel_validation.py` - `COMPONENTS_FILE, VEHICLE_CLASSES_FILE` → `Paths.*`
- [ ] `tests/repro_issues/test_bug_09_endurance.py` - `COMPONENTS_FILE` → `Paths.COMPONENTS_FILE`
- [ ] `tests/repro_issues/test_bug_12_hull_layer_addition.py` - `COMPONENTS_FILE` → `Paths.COMPONENTS_FILE`
- [ ] `tests/unit/performance/profile_simulation.py` - `COMPONENTS_FILE, MODIFIERS_FILE` → `Paths.*`
- [ ] `tests/unit/performance/reproduce_scaling.py` - `COMPONENTS_FILE, MODIFIERS_FILE` → `Paths.*`
- [ ] `tests/unit/performance/strategy_tournament.py` - `SHIPS_DIR, COMPONENTS_FILE, MODIFIERS_FILE` → `Paths.*`
- [ ] `tests/unit/performance/stress_test.py` - `COMPONENTS_FILE, MODIFIERS_FILE` → `Paths.*`
- [ ] `tests/unit/ui/test_theme_discovery.py` - `ASSET_DIR` → `Paths.ASSET_DIR`
- [ ] `scripts/verify_determinism_current.py` - `COMPONENTS_FILE, MODIFIERS_FILE` → `Paths.*`
- [ ] `scripts/repro_shield.py` - `COMPONENTS_FILE` → `Paths.COMPONENTS_FILE`
- [ ] `scripts/repro_energy_stats.py` - `COMPONENTS_FILE` → `Paths.COMPONENTS_FILE`
- [ ] Run targeted tests: `pytest tests/repro_issues/ tests/unit/performance/ -x`
**Notes:** Same migration pattern as Task 2.1.

### Task 2.3: Remove Path Re-exports from constants.py and paths.py [Simple]
**File:** `game/core/constants.py`, `game/core/paths.py`
**Tests:** `pytest tests/ -x` (full suite - ensures no missed callers)
- [ ] `game/core/constants.py` - Remove lines 64-78 (ROOT_DIR, DATA_DIR, ASSET_DIR, SHIPS_DIR, SCREENSHOT_DIR, COMPONENTS_FILE, MODIFIERS_FILE, VEHICLE_CLASSES_FILE re-exports)
- [ ] `game/core/constants.py` - Remove the `from game.core.paths import Paths` import IF only used for re-exports (verify it's not used elsewhere first)
- [ ] `game/core/paths.py` - Remove lines 123-134 (backward compat module-level exports and deprecation comment)
- [ ] Run full test suite: `pytest tests/ -x`
**Notes:** Only do this AFTER Tasks 2.1 and 2.2 are complete. Running full suite catches any missed callers.

### Task 2.4: Migrate LayerType Imports [Simple]
**Files:** 19 files importing from `component_constants.py`
**Tests:** `pytest tests/ --testmon`

All these files import LayerType from `game.simulation.components.component_constants`. Change to `from game.core.constants import LayerType`.

- [ ] `scripts/repro_energy_stats.py`
- [ ] `scripts/repro_shield.py`
- [ ] `tests/fixtures/components.py`
- [ ] `tests/fixtures/ships.py`
- [ ] `tests/repro_issues/test_bug_01_crew_delay.py`
- [ ] `tests/repro_issues/test_bug_05_logistics.py`
- [ ] `tests/repro_issues/test_bug_07_crash.py`
- [ ] `tests/repro_issues/test_bug_09_endurance.py`
- [ ] `tests/repro_issues/test_bug_11_hull_update.py`
- [ ] `tests/repro_issues/test_bug_13_clear_removes_hull.py`
- [ ] `tests/unit/ai/target_evaluator/test_evaluation_rules.py`
- [ ] `tests/unit/ai/test_movement_and_ai.py`
- [ ] `tests/unit/builder/test_builder_validation.py`
- [ ] `tests/unit/builder/test_bulk_add.py`
- [ ] `tests/unit/builder/test_requirement_abilities.py`
- [ ] `tests/unit/combat/test_combat_endurance.py`
- [ ] `tests/unit/combat/test_damage_weighted.py`
- [ ] `tests/unit/combat/test_fighter_launch.py`
- [ ] `tests/unit/combat/test_multitarget.py`
- [ ] Run tests: `pytest tests/ --testmon`
**Notes:** Change `from game.simulation.components.component_constants import LayerType` to `from game.core.constants import LayerType`.

### Task 2.5: Remove LayerType Re-export from component_constants.py [Simple]
**File:** `game/simulation/components/component_constants.py`
**Tests:** `pytest tests/ -x`
- [ ] Remove lines 24-26: the `from game.core.constants import LayerType` re-export and PROJ-17 comment
- [ ] Run full test suite: `pytest tests/ -x`
**Notes:** Only do this AFTER Task 2.4 is complete.

### Task 2.6: Remove WIDTH/HEIGHT Re-exports from constants.py [Simple]
**File:** `game/core/constants.py`
**Tests:** `pytest tests/ --testmon`
- [ ] Search for all imports of `WIDTH` and `HEIGHT` from `game.core.constants`
- [ ] Migrate any found callers to `from game.core.config import DisplayConfig` and use `DisplayConfig.DEFAULT_WIDTH`/`DisplayConfig.DEFAULT_HEIGHT`
- [ ] Remove lines 54-58 from `game/core/constants.py` (WIDTH, HEIGHT re-exports and DisplayConfig import)
- [ ] Run tests: `pytest tests/ -x`
**Notes:** These are re-exported from DisplayConfig for backward compatibility.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
- [ ] No remaining path constant re-exports in `constants.py` or `paths.py`
- [ ] No remaining LayerType re-export in `component_constants.py`
