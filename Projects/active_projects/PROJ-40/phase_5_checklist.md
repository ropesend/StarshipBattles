# Phase 5: Strategy Layer Refinements

**Status:** Not Started
**Estimated Effort:** 4-6 hours
**Priority:** Medium

## Overview
Address issues in `game/strategy/` focusing on incomplete facades, complex functions, and coupling concerns.

---

## Tasks

### 5.1 Complete StrategySessionFacade (NEW-STRAT-001, NEW-STRAT-003)
**Location:** `game/strategy/facade/strategy_session_facade.py:88, 99`
**Effort:** Medium

- [ ] Implement `get_fleet()` method (currently raises NotImplementedError)
- [ ] Implement `get_fleets_at_hex()` method
- [ ] Review other NotImplementedError stubs
- [ ] Either implement or document as "Command-only facade"
- [ ] Update module docstring to clarify scope
- [ ] Run: `pytest tests/unit/strategy/ -v`

---

### 5.2 Refactor calculate_intercept_point (NEW-STRAT-002)
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

### 5.7 Fix Runtime Import (NEW-STRAT-010)
**Location:** `game/strategy/engine/turn_engine.py:80-81`
**Effort:** Simple

- [ ] Move `SimulationBattleResolver` import to module level
- [ ] Use TYPE_CHECKING if needed for type hints
- [ ] Resolve any circular import issues that arise
- [ ] Document why runtime import was originally used (if necessary)
- [ ] Run: `pytest tests/unit/strategy/ -v`

---

## Verification

- [ ] Run strategy tests: `pytest tests/unit/strategy/ -v`
- [ ] Run strategy integration: `pytest tests/strategy/ -v`
- [ ] Verify no circular imports: `python -c "import game.strategy"`

---

## Notes
- Task 5.1 and 5.2 are the most complex
- Task 5.2 (refactor) should maintain exact same behavior - add characterization tests first
- Consider creating a design document for StrategySessionFacade scope
