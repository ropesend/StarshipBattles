# Code Review Action Plan

## Overview

This document provides a comprehensive, actionable plan to address all issues identified during the code review of the Starship Battles codebase. The plan is organized into phases with clear priorities, dependencies, and verification steps.

**Review Date:** January 2026
**Overall Foundation Quality:** ~75%
**Goal:** Bring the codebase to a solid, maintainable foundation before adding new features.

---

## How to Use This Plan

### Checklist Syntax
- `[ ]` - Not started
- `[~]` - In progress
- `[x]` - Completed
- `[!]` - Blocked or needs attention

### Workflow

1. **Work through phases in order** - Later phases depend on earlier ones
2. **Complete all tasks in a phase before moving on** - Unless marked as parallelizable
3. **Run tests after each task** - Command: `pytest tests/unit/ -v`
4. **Commit after each task** - Small, atomic commits make rollback easier
5. **Update this checklist** - Mark tasks as complete as you go

### Task Structure

Each task includes:
- **Objective**: What needs to be done
- **Files**: Which files to modify
- **Steps**: Detailed implementation steps
- **Verification**: How to confirm the task is complete
- **Estimated Scope**: Approximate lines of code affected

### Running Specific Test Suites

```bash
# Full test suite
pytest

# Unit tests only
pytest tests/unit/ -v

# Specific module tests
pytest tests/unit/ai/ -v
pytest tests/unit/combat/ -v
pytest tests/unit/entities/ -v

# Simulation tests
pytest simulation_tests/ -v

# With coverage
pytest tests/unit/ --cov=game --cov-report=html
```

---

## Phase 0: Critical Safety Fixes
**Priority:** 🔴 HIGH - Do these first
**Estimated Time:** 2-3 hours
**Dependencies:** None

These tasks fix potential runtime errors and thread safety issues that could cause hard-to-debug problems.

### Task 0.1: Add Thread Safety to Logger Singleton
- [x] **Objective:** Prevent race conditions in Logger initialization

**Files to Modify:**
- `game/core/logger.py`

**Steps:**
1. [ ] Read the current Logger implementation
2. [ ] Add `threading.Lock()` import
3. [ ] Add class-level `_lock = threading.Lock()`
4. [ ] Refactor `__new__` to use double-checked locking pattern:
   ```python
   _instance = None
   _lock = threading.Lock()

   def __new__(cls):
       if cls._instance is None:
           with cls._lock:
               if cls._instance is None:
                   cls._instance = super(Logger, cls).__new__(cls)
                   cls._instance._initialized = False
       return cls._instance

   def __init__(self):
       if self._initialized:
           return
       self._initialized = True
       self.setup()
   ```
5. [ ] Add `reset()` classmethod for testing
6. [ ] Run tests: `pytest tests/unit/core/ -v`

**Verification:**
- [ ] No race conditions in parallel test runs
- [ ] Logger can be reset between tests

**Estimated Scope:** ~30 lines changed

---

### Task 0.2: Add Thread Safety to TestRegistry
- [x] **Objective:** Prevent race conditions in test scenario discovery

**Files to Modify:**
- `test_framework/registry.py`

**Steps:**
1. [ ] Read the current TestRegistry implementation
2. [ ] Add `threading.Lock()` import
3. [ ] Add class-level lock
4. [ ] Wrap `__new__` method with lock
5. [ ] Add `reset()` classmethod
6. [ ] Run tests: `pytest simulation_tests/ -v`

**Verification:**
- [ ] Parallel test discovery works without errors

**Estimated Scope:** ~25 lines changed

---

### Task 0.3: Add Thread Safety to Component Cache
- [x] **Objective:** Make component caching thread-safe

**Files to Modify:**
- `game/simulation/components/component.py`

**Steps:**
1. [ ] Locate the module-level cache globals (lines 517-520)
2. [ ] Create a `ComponentCacheManager` singleton class:
   ```python
   class ComponentCacheManager:
       _instance = None
       _lock = threading.Lock()

       def __init__(self):
           self.component_cache = None
           self.modifier_cache = None
           self.last_component_file = None
           self.last_modifier_file = None

       @classmethod
       def instance(cls):
           if cls._instance is None:
               with cls._lock:
                   if cls._instance is None:
                       cls._instance = cls()
           return cls._instance

       @classmethod
       def reset(cls):
           with cls._lock:
               if cls._instance:
                   cls._instance.component_cache = None
                   cls._instance.modifier_cache = None
                   cls._instance.last_component_file = None
                   cls._instance.last_modifier_file = None
   ```
3. [ ] Update `reset_component_caches()` to use new class
4. [ ] Update all cache access to use `ComponentCacheManager.instance()`
5. [ ] Update `conftest.py` to use new reset method
6. [ ] Run tests: `pytest tests/unit/entities/ -v`

**Verification:**
- [ ] All component loading tests pass
- [ ] Cache properly resets between tests

**Estimated Scope:** ~60 lines changed

---

### Task 0.4: Fix Validation Rule Guard Clauses
- [x] **Objective:** Prevent KeyError exceptions in validation rules

**Files to Modify:**
- `game/simulation/ship_validator.py`

**Steps:**
1. [ ] Read `MountDependencyRule._do_validate()` method
2. [ ] Add guard clause at start:
   ```python
   if layer_type not in ship.layers:
       return ValidationResult(True)
   ```
3. [ ] Read `LayerRestrictionDefinitionRule._do_validate()` method
4. [ ] Add same guard clause
5. [ ] Run tests: `pytest tests/unit/entities/test_ship_validator.py -v`
6. [ ] Add test cases for missing layer scenarios

**Verification:**
- [ ] No KeyError when validating with invalid layer types
- [ ] All existing validation tests still pass

**Estimated Scope:** ~20 lines changed

---

## Phase 1: Logging Consistency ✅ COMPLETE
**Priority:** 🟡 MEDIUM
**Estimated Time:** 1-2 hours
**Dependencies:** Phase 0 (Logger thread safety)

### Task 1.1: Migrate asset_manager.py to Centralized Logging
- [x] **Objective:** Use consistent logging throughout codebase

**Files to Modify:**
- `game/assets/asset_manager.py`

**Steps:**
1. [x] Read current logging usage (8 calls)
2. [x] Add import: `from game.core.logger import log_error, log_info, log_warning`
3. [x] Remove: `import logging`
4. [x] Replace each call:
   - [x] Line 73: `logging.error()` → `log_error()`
   - [x] Line 79: `logging.info()` → `log_info()`
   - [x] Line 81: `logging.error()` → `log_error()`
   - [x] Line 95: `logging.warning()` → `log_warning()`
   - [x] Line 102: `logging.error()` → `log_error()`
   - [x] Line 115: `logging.warning()` → `log_warning()`
   - [x] Line 124: `logging.error()` → `log_error()`
   - [x] Line 155: `logging.error()` → `log_error()`
5. [x] Run tests: `pytest tests/unit/ -v -k asset`

**Verification:**
- [x] No `import logging` in asset_manager.py
- [x] All 8 log calls use centralized logger

**Estimated Scope:** ~15 lines changed

---

## Phase 2: JSON Utilities Migration ✅ COMPLETE
**Priority:** 🟡 MEDIUM
**Estimated Time:** 3-4 hours
**Dependencies:** None (can run parallel with Phase 1)

### Task 2.1: Migrate profiling.py to json_utils
- [x] **Objective:** Fix encoding issues and use consistent JSON handling

**Files to Modify:**
- `game/core/profiling.py`

**Steps:**
1. [x] Add import: `from game.core.json_utils import load_json, save_json`
2. [x] Replace `json.loads()` call (line ~121-124) with `load_json()`
3. [x] Replace `json.dump()` call with `save_json()`
4. [x] Remove direct `json` import if no longer needed
5. [x] Run tests: `pytest tests/unit/performance/test_profiling.py -v`

**Verification:**
- [x] Profiling loads and saves correctly
- [x] UTF-8 encoding properly handled

**Estimated Scope:** ~20 lines changed

---

### Task 2.2: Migrate Test Framework JSON Operations
- [x] **Objective:** Use json_utils in test setup code

**Files to Modify:**
- `tests/test_framework/services/conftest.py`
- `tests/test_framework/services/test_scenario_data_service.py`

**Steps:**
1. [x] Add `from game.core.json_utils import save_json` to conftest.py
2. [x] Replace 3 `json.dump()` calls in conftest.py with `save_json()`
3. [x] Replace 4 `json.dump()` calls in test_scenario_data_service.py
4. [x] Run tests: `pytest tests/test_framework/ -v`

**Verification:**
- [x] All test framework tests pass
- [x] No direct json.dump calls remain

**Estimated Scope:** ~15 lines changed

---

### Task 2.3: Migrate Builder Test JSON Operations
- [x] **Objective:** Use json_utils in builder tests

**Files to Modify:**
- `tests/unit/builder/test_builder_data_loader.py`
- `tests/unit/builder/test_ship_loading.py`

**Steps:**
1. [x] Add json_utils imports
2. [x] Replace `json.dump()` and `json.load()` calls
3. [x] Run tests: `pytest tests/unit/builder/ -v`

**Verification:**
- [x] All builder tests pass

**Estimated Scope:** ~10 lines changed

---

### Task 2.4: Migrate UI detail_panel.py JSON Serialization
- [x] **Objective:** Add error handling to component serialization

**Files to Modify:**
- `ui/builder/detail_panel.py`

**Steps:**
1. [x] Locate `json.dumps()` call (line ~189)
2. [x] Wrap in try/except with proper error handling
3. [x] Added `default=str` parameter for non-serializable objects
4. [x] Run tests: `pytest tests/unit/ui/ -v`

**Verification:**
- [x] UI doesn't crash on malformed component data

**Estimated Scope:** ~10 lines changed

---

## Phase 3: Test Infrastructure Consolidation ✅ COMPLETE
**Priority:** 🟡 MEDIUM
**Estimated Time:** 4-5 hours
**Dependencies:** None

### Task 3.1: Create Centralized AI Fixtures Module
- [x] **Objective:** Eliminate duplicate strategy_manager fixture

**Files to Create:**
- `tests/fixtures/ai.py`

**Files to Modify:**
- `tests/fixtures/__init__.py`
- `tests/unit/ai/conftest.py`
- `tests/unit/combat/conftest.py`

**Steps:**
1. [ ] Create `tests/fixtures/ai.py`:
   ```python
   """AI-related test fixtures."""
   import pytest
   from game.ai.strategy_manager import StrategyManager
   from tests.fixtures.paths import get_unit_test_data_dir

   @pytest.fixture
   def strategy_manager_with_test_data():
       """Provide StrategyManager loaded with test data."""
       manager = StrategyManager.instance()
       data_dir = get_unit_test_data_dir()
       manager.load_data(
           str(data_dir),
           targeting_file="test_targeting_policies.json",
           movement_file="test_movement_policies.json",
           strategy_file="test_combat_strategies.json"
       )
       manager._loaded = True
       yield manager
       manager.clear()
   ```
2. [ ] Add to `tests/fixtures/__init__.py`:
   ```python
   from tests.fixtures.ai import strategy_manager_with_test_data
   ```
3. [ ] Update `tests/unit/ai/conftest.py`:
   - Remove local `strategy_manager_with_test_data` definition
   - Add: `from tests.fixtures.ai import strategy_manager_with_test_data  # noqa: F401`
4. [ ] Update `tests/unit/combat/conftest.py`:
   - Remove local `strategy_manager_with_test_data` definition
   - Add: `from tests.fixtures.ai import strategy_manager_with_test_data  # noqa: F401`
5. [ ] Run tests: `pytest tests/unit/ai/ tests/unit/combat/ -v`

**Verification:**
- [ ] Only one definition of `strategy_manager_with_test_data` exists
- [ ] All AI and combat tests pass

**Estimated Scope:** ~40 lines changed

---

### Task 3.2: Consolidate unit_test_data_dir Fixture
- [x] **Objective:** Single source for test data directory fixture

**Files to Modify:**
- `tests/unit/ai/conftest.py`
- `tests/unit/ui/conftest.py`

**Steps:**
1. [ ] Verify `tests/fixtures/paths.py` has `unit_test_data_dir` fixture
2. [ ] In `tests/unit/ai/conftest.py`:
   - Remove local definition
   - Add: `from tests.fixtures.paths import unit_test_data_dir  # noqa: F401`
3. [ ] In `tests/unit/ui/conftest.py`:
   - Remove local definition (lines 74-76)
   - Add: `from tests.fixtures.paths import unit_test_data_dir  # noqa: F401`
4. [ ] Run tests: `pytest tests/unit/ai/ tests/unit/ui/ -v`

**Verification:**
- [ ] No duplicate `unit_test_data_dir` definitions
- [ ] All tests pass

**Estimated Scope:** ~20 lines changed

---

### Task 3.3: Consolidate Ship Fixtures
- [x] **Objective:** Remove duplicate ship fixtures from module conftest files

**Files to Modify:**
- `tests/unit/builder/conftest.py`
- `tests/unit/systems/conftest.py`

**Steps:**
1. [ ] Verify `tests/fixtures/ships.py` has `basic_cruiser_ship` and `basic_escort_ship`
2. [ ] In `tests/unit/builder/conftest.py`:
   - Remove local `basic_cruiser_ship` and `basic_escort_ship` definitions
   - Add: `from tests.fixtures.ships import basic_cruiser_ship, basic_escort_ship  # noqa: F401`
3. [ ] In `tests/unit/systems/conftest.py`:
   - Remove local definitions
   - Add same import
4. [ ] Run tests: `pytest tests/unit/builder/ tests/unit/systems/ -v`

**Verification:**
- [ ] No duplicate ship fixture definitions
- [ ] All tests pass

**Estimated Scope:** ~30 lines changed

---

### Task 3.4: Consolidate Path Fixtures in UI Conftest
- [x] **Objective:** Use centralized path fixtures

**Files to Modify:**
- `tests/unit/ui/conftest.py`

**Steps:**
1. [ ] Remove local definitions of `data_dir`, `project_root`, `assets_dir` (lines 62-82)
2. [ ] Add import:
   ```python
   from tests.fixtures.paths import (
       data_dir,
       project_root,
       unit_test_data_dir,
       assets_dir
   )  # noqa: F401
   ```
3. [ ] Run tests: `pytest tests/unit/ui/ -v`

**Verification:**
- [ ] No duplicate path fixtures
- [ ] All UI tests pass

**Estimated Scope:** ~25 lines changed

---

### Task 3.5: Remove Orphaned ship_fixtures.py
- [x] **Objective:** Clean up unused fixture file

**Files to Check/Remove:**
- `tests/fixtures/ship_fixtures.py`

**Steps:**
1. [ ] Search codebase for imports of `ship_fixtures`
2. [ ] If no imports found, delete the file
3. [ ] If imports found, either:
   - Migrate content to `ships.py`
   - Or update imports
4. [ ] Run full test suite: `pytest`

**Verification:**
- [ ] No orphaned fixture files
- [ ] All tests pass

**Estimated Scope:** File deletion or ~50 lines migrated

---

## Phase 4: Service Layer Adoption ✅ COMPLETE
**Priority:** 🟡 MEDIUM
**Estimated Time:** 4-5 hours
**Dependencies:** None

### Task 4.1: Refactor BuilderEventRouter to Use ShipBuilderService
- [x] **Objective:** UI should use service layer, not direct domain access

**Files to Modify:**
- `game/ui/screens/builder_event_router.py`

**Steps:**
1. [ ] Read current implementation, noting direct Ship method calls
2. [ ] Identify all locations calling:
   - `ship.add_component()`
   - `ship.remove_component()`
3. [ ] Add ShipBuilderService dependency (likely via BuilderSceneGUI)
4. [ ] Replace direct calls with service methods:
   ```python
   # Before
   gui.ship.remove_component(found_layer, found_idx)

   # After
   result = gui.ship_service.remove_component(gui.ship, found_layer, found_idx)
   if not result.success:
       # Handle error appropriately
   ```
5. [ ] Handle `ShipBuilderResult` return values appropriately
6. [ ] Run tests: `pytest tests/unit/builder/ -v`

**Verification:**
- [ ] No direct `ship.add_component()` calls in BuilderEventRouter
- [ ] No direct `ship.remove_component()` calls in BuilderEventRouter
- [ ] All builder tests pass

**Estimated Scope:** ~50 lines changed

---

### Task 4.2: Refactor BuilderScreen to Use Service for Class Changes
- [x] **Objective:** Class change operations should go through service

**Files to Modify:**
- `game/ui/screens/builder_screen.py`

**Steps:**
1. [ ] Locate `ship.change_class()` calls (lines ~392, 398)
2. [ ] Route through `BuilderViewModel.change_ship_class()` instead
3. [ ] Or use `ShipBuilderService.change_class()` directly
4. [ ] Handle result appropriately
5. [ ] Run tests: `pytest tests/unit/builder/ -v`

**Verification:**
- [ ] No direct `ship.change_class()` calls in BuilderScreen
- [ ] Class changes work correctly through UI

**Estimated Scope:** ~20 lines changed

---

### Task 4.3: Add DataService Usage in UI (Optional Enhancement)
- [x] **Objective:** Demonstrate DataService usage pattern (Note: Service pattern demonstrated via ShipBuilderService; DataService usage deferred as no clear UI benefit found)

**Files to Modify:**
- `game/ui/screens/builder_data_loader.py` (or similar)

**Steps:**
1. [ ] Identify a location that queries components by type/ability
2. [ ] Replace direct registry access with DataService calls
3. [ ] Document the pattern for future use
4. [ ] Run tests: `pytest tests/unit/builder/ -v`

**Verification:**
- [ ] DataService successfully used in at least one UI location

**Estimated Scope:** ~15 lines changed

---

## Phase 5: Ship Helper Method Adoption ✅ COMPLETE
**Priority:** 🟢 LOW-MEDIUM
**Estimated Time:** 3-4 hours
**Dependencies:** None

### Task 5.1: Refactor builder_event_router.py Layer Iterations ✅ COMPLETE
- [x] **Objective:** Use Ship helper methods instead of manual iteration

**Files to Modify:**
- `game/ui/screens/builder_event_router.py`

**Steps:**
1. [x] Find all `for layer_data in ship.layers.values()` patterns
2. [x] Replace with `ship.get_all_components()` where appropriate
3. [x] Find all `for layer_type, layer_data in ship.layers.items()` patterns
4. [x] Replace with `ship.iter_components()` where appropriate
5. [x] Run tests: `pytest tests/unit/builder/ -v`

**Locations updated (5 of 7 - 2 require index tracking, not refactorable):**
- [x] Lines using `.layers.values()` for component iteration → get_all_components()
- [x] Lines using `.layers.items()` for layer lookup → iter_components()
- [x] Lines using sum() for component counting → len(get_all_components())

**Note:** Lines 215-224 and 234-241 require layer+index tracking for removal operations
and cannot be simplified with current helpers (would need a find_component_with_index helper).

**Verification:**
- [x] Reduced direct `.layers` access
- [x] All tests pass

**Estimated Scope:** ~30 lines changed

---

### Task 5.2: Refactor builder_viewmodel.py Layer Iterations ✅ COMPLETE
- [x] **Objective:** Use Ship helper methods (Analysis: No refactoring needed)

**Files to Modify:**
- `game/ui/screens/builder_viewmodel.py`

**Analysis:**
1. [x] Find layer iteration patterns (2 locations)
   - Line 141-148: `_normalize_selection` - needs layer+index, not refactorable
   - Line 528: `clear_design` - modifies layer_data directly (not components), not refactorable
2. [x] Determined neither pattern benefits from helper methods:
   - `_normalize_selection` needs index for tuple creation
   - `clear_design` needs to skip HULL and modify layer properties

**Verification:**
- [x] Existing tests pass - no changes required

**Estimated Scope:** No changes needed

---

### Task 5.3: Refactor ship_stats.py Layer Iterations ✅ COMPLETE
- [x] **Objective:** Use Ship helper methods in stats calculation

**Files to Modify:**
- `game/simulation/entities/ship_stats.py`

**Steps:**
1. [x] Find 3 layer iteration patterns
   - Lines 29-32: Mass calculation per layer - needs layer_data, not refactorable
   - Lines 72-101: Component status/supply gathering - refactored to use iter_components()
   - Lines 358-368: Mass limits check - needs layer_data, not refactorable
2. [x] Replace with appropriate helper methods (1 of 3 patterns)
3. [x] Run tests: `pytest tests/unit/entities/test_ship_stats.py -v`

**Verification:**
- [x] All ship stats tests pass
- [x] Stats calculation unchanged

**Estimated Scope:** ~5 lines changed (1 pattern refactored)

---

### Task 5.4: Refactor game_renderer.py Layer Iterations ✅ COMPLETE
- [x] **Objective:** Use Ship helper methods in rendering (Analysis: No refactoring needed)

**Files to Modify:**
- `game/ui/renderer/game_renderer.py`

**Analysis:**
1. [x] Find layer iteration patterns (2 locations)
   - Lines 96-127 (`draw_ship`): Needs layer-specific radius for positioning, not refactorable
   - Lines 188-221 (`draw_hud`): Iterates in specific layer order with section headers, not refactorable
2. [x] Determined patterns are layer-dependent rendering that benefits from direct layer access
3. [x] Using `iter_components()` would add complexity for no benefit

**Verification:**
- [x] No changes required - current pattern is appropriate for rendering

**Estimated Scope:** No changes needed

---

### Task 5.5: Add has_components() Helper Method (Optional) ✅ COMPLETE
- [x] **Objective:** Simplify component existence checks

**Files to Modify:**
- `game/simulation/entities/ship.py`
- `tests/unit/entities/test_ship_helpers.py`

**Steps:**
1. [x] Add method to Ship class (more efficient iteration-based implementation)
2. [x] Add tests for the new method (5 test cases in TestHasComponents)
3. [x] Update `builder_event_router.py` to use new method
4. [x] Run tests: `pytest tests/unit/entities/test_ship_helpers.py -v`

**Verification:**
- [x] New helper method works correctly
- [x] Builder uses simplified check

**Estimated Scope:** ~20 lines added

---

## Phase 6: Configuration Consolidation ✅ COMPLETE
**Priority:** 🟢 LOW
**Estimated Time:** 2-3 hours
**Dependencies:** None

### Task 6.1: Add Missing UI Constants to Config ✅ COMPLETE
- [x] **Objective:** Centralize scattered UI dimension constants

**Files Modified:**
- `game/core/config.py`

**Changes:**
- Added 6 new constants to UIConfig class:
  - `GRID_SPACING: int = 5000`
  - `TRAIL_LENGTH: int = 100`
  - `ROW_HEIGHT_STANDARD: int = 40`
  - `ROW_HEIGHT_LARGE: int = 50`
  - `SIDEBAR_WIDTH: int = 300`
  - `HEADER_HEIGHT: int = 40`

**Verification:**
- [x] New constants available in UIConfig
- [x] All tests pass

---

### Task 6.2: Update battle_screen.py to Use Config ✅ COMPLETE
- [x] **Objective:** Remove hardcoded grid_spacing

**Files Modified:**
- `game/ui/screens/battle_screen.py`

**Changes:**
- Replaced `grid_spacing = 5000` with `grid_spacing = UIConfig.GRID_SPACING`
- Note: UIConfig was already imported in this file

**Verification:**
- [x] All tests pass

---

### Task 6.3: Update battle_scene.py to Use Config ✅ COMPLETE
- [x] **Objective:** Remove hardcoded trail_length

**Files Modified:**
- `game/ui/screens/battle_scene.py`

**Changes:**
- Added import: `from game.core.config import UIConfig`
- Replaced `trail_length = 100` with `trail_length = UIConfig.TRAIL_LENGTH`

**Verification:**
- [x] All tests pass

---

### Task 6.4: Update Window Classes to Use Config ✅ COMPLETE
- [x] **Objective:** Centralize window dimension constants

**Files Modified:**
- `game/ui/screens/planet_list_window.py`
- `game/ui/screens/fleet_orders_window.py`

**Changes in planet_list_window.py:**
- Added import: `from game.core.config import UIConfig`
- Replaced `self.sidebar_width = 300` with `UIConfig.SIDEBAR_WIDTH`
- Replaced `self.header_height = 40` with `UIConfig.HEADER_HEIGHT`
- Replaced `self.row_height = 50` with `UIConfig.ROW_HEIGHT_LARGE`

**Changes in fleet_orders_window.py:**
- Added import: `from game.core.config import UIConfig`
- Replaced `row_height = 40` with `UIConfig.ROW_HEIGHT_STANDARD`

**Verification:**
- [x] All tests pass (1113 passed)

---

## Phase 7: Event Bus Enhancement
**Priority:** 🟢 LOW
**Estimated Time:** 1-2 hours
**Dependencies:** None

### Task 7.1: Add Callable Validation to EventBus
- [ ] **Objective:** Fail fast on invalid callback registration

**Files to Modify:**
- `ui/builder/event_bus.py`
- `tests/unit/systems/test_event_bus.py`

**Steps:**
1. [ ] Add validation to `subscribe()` method:
   ```python
   def subscribe(self, event_type: str, callback) -> None:
       if not callable(callback):
           raise TypeError(f"Callback must be callable, got {type(callback)}")
       # ... existing code
   ```
2. [ ] Add test for invalid callback:
   ```python
   def test_subscribe_non_callable_raises_error(self):
       bus = EventBus()
       with pytest.raises(TypeError):
           bus.subscribe("TEST", "not a callback")
   ```
3. [ ] Run tests: `pytest tests/unit/systems/test_event_bus.py -v`

**Verification:**
- [ ] TypeError raised for non-callable callbacks
- [ ] All existing tests pass

**Estimated Scope:** ~15 lines added

---

### Task 7.2: Standardize Event Type Constants
- [ ] **Objective:** Use constants instead of string literals

**Files to Modify:**
- `game/ui/screens/builder_utils.py`
- `game/ui/screens/builder_viewmodel.py`
- `ui/builder/right_panel.py`
- `ui/builder/left_panel.py`
- `ui/builder/detail_panel.py`

**Steps:**
1. [ ] Ensure all event types are defined in `BuilderEvents` class
2. [ ] Search for string literal event names in emit/subscribe calls
3. [ ] Replace with `BuilderEvents.*` constants
4. [ ] Run tests: `pytest tests/unit/builder/ -v`

**Verification:**
- [ ] No string literal event names in code
- [ ] All builder functionality works

**Estimated Scope:** ~20 lines changed

---

## Phase 8: Validation Improvements
**Priority:** 🟢 LOW
**Estimated Time:** 2-3 hours
**Dependencies:** Phase 0 (Task 0.4)

### Task 8.1: Extract Restriction Parsing Helper
- [ ] **Objective:** Reduce string parsing duplication in validation rules

**Files to Modify:**
- `game/simulation/ship_validator.py`

**Steps:**
1. [ ] Create helper function:
   ```python
   def _parse_restriction(rule_str: str, prefix: str) -> Optional[str]:
       """Extract value from restriction string with given prefix."""
       if rule_str.startswith(prefix + ":"):
           parts = rule_str.split(":", 1)
           return parts[1] if len(parts) > 1 else None
       return None
   ```
2. [ ] Replace 6 string parsing locations in `LayerRestrictionDefinitionRule`
3. [ ] Run tests: `pytest tests/unit/entities/test_ship_validator.py -v`

**Verification:**
- [ ] All validation tests pass
- [ ] Reduced code duplication

**Estimated Scope:** ~30 lines changed

---

### Task 8.2: Extract Restriction Prefix Constants
- [ ] **Objective:** Replace magic strings with constants

**Files to Modify:**
- `game/simulation/ship_validator.py`

**Steps:**
1. [ ] Add constants at module or class level:
   ```python
   class RestrictionPrefixes:
       BLOCK = "block_"
       ALLOW = "allow_"
       DENY = "deny_"
       HULL_ONLY = "HullOnly"
   ```
2. [ ] Update rule implementations to use constants
3. [ ] Run tests: `pytest tests/unit/entities/test_ship_validator.py -v`

**Verification:**
- [ ] No magic strings in restriction checking
- [ ] All tests pass

**Estimated Scope:** ~20 lines changed

---

### Task 8.3: Add ModifierService Unit Tests
- [ ] **Objective:** Ensure modifier service has test coverage

**Files to Create:**
- `tests/unit/services/test_modifier_service.py`

**Steps:**
1. [ ] Create test file with tests for:
   - `is_modifier_allowed()`
   - `get_mandatory_modifiers()`
   - `is_modifier_mandatory()`
   - `get_initial_value()`
   - `ensure_mandatory_modifiers()`
   - `get_local_min_max()`
2. [ ] Run tests: `pytest tests/unit/services/test_modifier_service.py -v`

**Verification:**
- [ ] All ModifierService methods have test coverage

**Estimated Scope:** ~150 lines added

---

## Phase 9: Documentation Updates
**Priority:** 🟢 LOW
**Estimated Time:** 1-2 hours
**Dependencies:** All previous phases

### Task 9.1: Update SERVICES.md
- [ ] **Objective:** Document all services accurately

**Files to Modify:**
- `docs/architecture/SERVICES.md`

**Steps:**
1. [ ] Add BattleService API documentation
2. [ ] Add DataService usage examples
3. [ ] Document result object handling patterns
4. [ ] Add service layer diagram

**Verification:**
- [ ] All four services documented
- [ ] Usage examples are accurate

---

### Task 9.2: Create TEST_FIXTURES.md
- [ ] **Objective:** Document fixture organization

**Files to Create:**
- `tests/fixtures/README.md`

**Steps:**
1. [ ] Document fixture locations
2. [ ] Document when to use factory functions vs fixtures
3. [ ] Document fixture dependencies
4. [ ] Add examples

**Verification:**
- [ ] New developers can understand fixture organization

---

### Task 9.3: Update This Plan
- [ ] **Objective:** Mark plan as complete

**Steps:**
1. [ ] Review all tasks are marked complete
2. [ ] Note any deferred items
3. [ ] Update overall assessment scores
4. [ ] Add completion date

---

## Summary Checklist

### Phase 0: Critical Safety Fixes 🔴 ✅ COMPLETE
- [x] Task 0.1: Logger thread safety
- [x] Task 0.2: TestRegistry thread safety
- [x] Task 0.3: Component cache thread safety
- [x] Task 0.4: Validation guard clauses

### Phase 1: Logging Consistency 🟡 ✅ COMPLETE
- [x] Task 1.1: Migrate asset_manager.py

### Phase 2: JSON Utilities Migration 🟡 ✅ COMPLETE
- [x] Task 2.1: Migrate profiling.py
- [x] Task 2.2: Migrate test framework
- [x] Task 2.3: Migrate builder tests
- [x] Task 2.4: Migrate detail_panel.py

### Phase 3: Test Infrastructure 🟡 ✅ COMPLETE
- [x] Task 3.1: Create AI fixtures module
- [x] Task 3.2: Consolidate unit_test_data_dir
- [x] Task 3.3: Consolidate ship fixtures
- [x] Task 3.4: Consolidate path fixtures
- [x] Task 3.5: Remove orphaned files

### Phase 4: Service Layer Adoption 🟡 ✅ COMPLETE
- [x] Task 4.1: Refactor BuilderEventRouter
- [x] Task 4.2: Refactor BuilderScreen
- [x] Task 4.3: Add DataService usage (optional - deferred)

### Phase 5: Ship Helper Method Adoption 🟢 ✅ COMPLETE
- [x] Task 5.1: Refactor builder_event_router.py
- [x] Task 5.2: Refactor builder_viewmodel.py (no changes needed)
- [x] Task 5.3: Refactor ship_stats.py
- [x] Task 5.4: Refactor game_renderer.py (no changes needed)
- [x] Task 5.5: Add has_components() helper

### Phase 6: Configuration Consolidation 🟢 ✅ COMPLETE
- [x] Task 6.1: Add missing UI constants
- [x] Task 6.2: Update battle_screen.py
- [x] Task 6.3: Update battle_scene.py
- [x] Task 6.4: Update window classes

### Phase 7: Event Bus Enhancement 🟢
- [ ] Task 7.1: Add callable validation
- [ ] Task 7.2: Standardize event type constants

### Phase 8: Validation Improvements 🟢
- [ ] Task 8.1: Extract restriction parsing helper
- [ ] Task 8.2: Extract restriction prefix constants
- [ ] Task 8.3: Add ModifierService tests

### Phase 9: Documentation Updates 🟢
- [ ] Task 9.1: Update SERVICES.md
- [ ] Task 9.2: Create TEST_FIXTURES.md
- [ ] Task 9.3: Update this plan

---

## Completion Metrics

**Target State After All Phases:**

| Area | Before | After |
|------|--------|-------|
| Core Infrastructure | 95% | 98% |
| Singleton Patterns | 85% | 98% |
| Service Layer | 75% | 95% |
| Test Infrastructure | 60% | 90% |
| Layer Iteration Refactoring | 25% | 80% |
| JSON Utils Migration | 26% | 70% |
| Configuration Centralization | 70% | 90% |
| Logging Practices | 95% | 100% |
| Event Bus | 90% | 95% |
| Validation Architecture | 80% | 95% |
| **Overall** | **~75%** | **~92%** |

---

## Notes

- Tasks marked (optional) can be deferred if time is limited
- Run `pytest` after each phase to ensure no regressions
- Commit frequently with descriptive messages
- Update this checklist as you progress

**Plan Created:** January 2026
**Last Updated:** January 2026
**Status:** Ready for execution
