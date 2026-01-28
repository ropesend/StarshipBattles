# Phase 5: Strategy Layer Refinements

**Status:** Not Started
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
**Location:** `game/strategy/data/pathfinding.py:229-370`
**Effort:** Medium

- [ ] Extract logging to `_log_intercept_calculation()` helper
- [ ] Split into smaller functions:
  - `_calculate_base_intercept()`
  - `_apply_intercept_corrections()`
  - `_validate_intercept_result()`
- [ ] Reduce nesting depth (currently 6+ levels)
- [ ] Remove or consolidate ~20 debug log statements
- [ ] Add docstring explaining algorithm
- [ ] Run: `pytest tests/unit/strategy/ -v -k pathfinding`

---

### 5.3 Add Type Hints to Pathfinding (NEW-STRAT-006)
**Location:** `game/strategy/data/pathfinding.py:6, 13, 87, 105`
**Effort:** Simple

- [ ] Add type hints to `find_path_deep_space()`
- [ ] Add type hints to `find_path_interstellar()`
- [ ] Add type hints to `get_system_at_hex()`
- [ ] Add type hints to `find_nearest_system()`
- [ ] Include return types for all functions
- [ ] Run mypy if available

---

### 5.4 Fix Movement/Order Coupling (NEW-STRAT-007)
**Location:** `game/strategy/engine/fleet_movement_engine.py:79`
**Effort:** Medium

- [ ] Analyze FleetMovementEngine dependencies on FleetOrderProcessor
- [ ] Extract shared concepts to interfaces
- [ ] Use constructor injection for dependencies
- [ ] Document dependency graph in code comments
- [ ] Run: `pytest tests/unit/strategy/ -v -k fleet`

---

### 5.5 Fix ShipInstance Serial Handling (NEW-STRAT-008)
**Location:** `game/strategy/data/ship_instance.py:64-98`
**Effort:** Simple

- [ ] Add validation for `serial` parameter
- [ ] Raise warning if `empire` is None but serial expected
- [ ] Document serial assignment behavior in docstring
- [ ] Run: `pytest tests/unit/strategy/ -v -k ship_instance`

---

### 5.6 Inline/Remove Helper Methods (NEW-STRAT-009)
**Location:** `game/strategy/engine/game_session.py:472-481`
**Effort:** Simple

- [ ] Review `_get_fleet_by_id()` usage
- [ ] Review `_get_planet_by_id()` usage
- [ ] Either inline these 2-3 line methods or move to Galaxy/Empire
- [ ] Run: `pytest tests/unit/strategy/ -v`

---

### ~~5.7 Fix Runtime Import (NEW-STRAT-010)~~
**Status:** REMOVED - NOT AN ISSUE
**Reason:** Runtime import of `SimulationBattleResolver` at lines 80-81 in turn_engine.py is intentional lazy-loading for the DI pattern.

---

## Verification

- [ ] Run strategy tests: `pytest tests/unit/strategy/ -v`
- [ ] Run strategy integration: `pytest tests/strategy/ -v`
- [ ] Verify no circular imports: `python -c "import game.strategy"`

---

## Notes
- Task 5.1 (refactor) is the most complex
- Task 5.1 should maintain exact same behavior - add characterization tests first
