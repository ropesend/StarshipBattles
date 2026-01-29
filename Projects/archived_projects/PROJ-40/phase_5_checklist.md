# Phase 5: Strategy Layer Refinements

**Status:** Complete
**Estimated Effort:** 3-4 hours
**Priority:** Medium

## Overview
Address issues in `game/strategy/` focusing on complex functions, coupling concerns, and code quality.

> **Note:** This phase was reduced from 8 tasks to 5 after Category 3 audit verification:
> - Task 5.1 (NEW-STRAT-001, NEW-STRAT-003) REMOVED - Facade methods fully implemented
> - Task 5.7 (NEW-STRAT-010) REMOVED - Lazy-loading is intentional DI pattern

---

## Tasks

### ~~5.1 Complete StrategySessionFacade (NEW-STRAT-001, NEW-STRAT-003)~~
**Status:** REMOVED - ALREADY COMPLETE
**Reason:** Both methods are now fully implemented:
- `get_fleet()`: Lines 108-120, returns FleetInfo DTO
- `get_fleets_at_hex()`: Lines 122-136, iterates empires and returns FleetInfo list

---

### 5.1 Refactor calculate_intercept_point (NEW-STRAT-002)
**Location:** `game/strategy/data/pathfinding.py:236-327`
**Effort:** Medium

- [x] Split into smaller functions:
  - `_extract_chaser_info()` - extracts location, speed, ID, warp capability from Fleet/NavigationState
  - `_evaluate_intercept_candidates()` - main loop finding optimal intercept point
  - `_ChaserProxy` - class for warp capability proxy (moved to module level)
- [x] Reduce nesting depth (from 6+ to 3 levels)
- [x] Remove or consolidate ~20 debug log statements (reduced to 4 strategic logs)
- [x] Add docstring explaining algorithm
- [x] Run: `pytest tests/unit/strategy/ -v -k pathfinding`

**Notes:** Refactored from 176 lines to ~90 lines. Extracted helper functions maintain identical behavior. All 120 pathfinding tests pass.

---

### 5.3 Add Type Hints to Pathfinding (NEW-STRAT-006)
**Location:** `game/strategy/data/pathfinding.py:13, 22, 103, 120`
**Effort:** Simple

- [x] Add type hints to `find_path_deep_space()`
- [x] Add type hints to `find_path_interstellar()`
- [x] Add type hints to `get_system_at_hex()`
- [x] Add type hints to `find_nearest_system()`
- [x] Include return types for all functions
- [x] Run tests: all 55 pathfinding tests pass

**Notes:** Added TYPE_CHECKING imports for Galaxy and StarSystem. All functions now have complete parameter and return type hints with improved docstrings.

---

### 5.4 Fix Movement/Order Coupling (NEW-STRAT-007)
**Location:** `game/strategy/engine/fleet_movement_engine.py:49`
**Effort:** Medium

- [x] Analyze FleetMovementEngine dependencies on FleetOrderProcessor
- [x] Use constructor injection for dependencies (FleetNavigationService)
- [x] Document dependency graph in class docstring
- [x] Run: `pytest tests/unit/strategy/ -v -k fleet`

**Notes:** Analysis showed no direct coupling to FleetOrderProcessor - the implicit coupling was with FleetNavigationService. Added constructor injection pattern with optional parameter (backward compatible). Documented dependencies in class docstring. All 238 fleet tests pass.

---

### 5.5 Fix ShipInstance Serial Handling (NEW-STRAT-008)
**Location:** `game/strategy/data/ship_instance.py:66-111`
**Effort:** Simple

- [x] Add validation for `serial` parameter
- [x] Raise warning if `empire` is None but serial expected
- [x] Document serial assignment behavior in docstring
- [x] Run: `pytest tests/unit/strategy/ -v -k ship_instance`

**Notes:** Added `log_warning()` when empire is None. Enhanced docstring with explanation of serial number purpose and behavior. All 73 ship_instance tests pass.

---

### 5.6 Inline/Remove Helper Methods (NEW-STRAT-009)
**Location:** `game/strategy/engine/game_session.py:478-505`
**Effort:** Simple

- [x] Review `_get_fleet_by_id()` usage (used 7 times - provides valuable abstraction)
- [x] Review `_get_planet_by_id()` usage (used 2 times - consistent API with fleet helper)
- [x] Decision: Keep both helpers (inlining would increase code duplication)
- [x] Added type hints and comprehensive docstrings
- [x] Run: `pytest tests/unit/strategy/ -v`

**Notes:** Analysis showed these helpers reduce code duplication and provide consistent API. `_get_fleet_by_id()` is used 7 times for command validation. Inlining would require duplicating 5-line iteration logic 7 times. Added type hints and documented reasoning for keeping them. All 781 strategy tests pass.

---

### ~~5.7 Fix Runtime Import (NEW-STRAT-010)~~
**Status:** REMOVED - NOT AN ISSUE
**Reason:** Runtime import of `SimulationBattleResolver` at lines 80-81 in turn_engine.py is intentional lazy-loading for the DI pattern.

---

## Verification

- [x] Run strategy tests: `pytest tests/unit/strategy/ -v` (781 passed)
- [x] Run strategy integration: `pytest tests/strategy/ -v` (249 passed)
- [x] Verify no circular imports: `python -c "import game.strategy"` (OK)

---

## Notes
- Task 5.1 (refactor) is the most complex
- Task 5.1 should maintain exact same behavior - add characterization tests first
