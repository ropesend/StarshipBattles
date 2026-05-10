# Phase 4: Legacy Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-36 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Clean up deprecated methods and unused code

---

## Tasks

### Task 4.1: Remove legacy wrapper methods [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/test_turn_engine.py`

- [x] Search for callers of `_calculate_next_hex`:
  ```bash
  grep -r "_calculate_next_hex" game/ tests/
  ```
- [x] Update any callers to use `FleetMovementEngine.calculate_next_hex()` directly
- [x] Remove `_calculate_next_hex` method (lines 243-252)

- [x] Search for callers of `_spawn_complex`:
  ```bash
  grep -r "_spawn_complex" game/ tests/
  ```
- [x] Update any callers to use `ProductionEngine._spawn_complex()` directly
- [x] Remove `_spawn_complex` method (lines 196-202)

- [x] Search for callers of `_spawn_ship`:
  ```bash
  grep -r "_spawn_ship" game/ tests/
  ```
- [x] Update any callers to use `ProductionEngine._spawn_ship()` directly
- [x] Remove `_spawn_ship` method (lines 204-210)

- [x] Verify: No remaining references to removed methods

**Notes:** Updated tests in `test_turn_engine.py` and `test_advanced_fleet_orders.py` to use `turn_engine.movement_engine.calculate_next_hex()` directly. No callers for `_spawn_complex` and `_spawn_ship` wrappers existed in tests (they already patched `production_engine` directly).

---

### Task 4.2: Clean up imports and type hints [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/test_turn_engine.py`

- [x] Review imports at top of file - remove unused:
  - `OrderType` (removed - no longer used in TurnEngine)
- [x] TYPE_CHECKING block already correct - no changes needed
- [x] Verify no circular import issues:
  ```bash
  python -c "from game.strategy.engine.turn_engine import TurnEngine"
  ```
- [x] Run `pytest tests/` to verify nothing broken

**Notes:** Removed unused `OrderType` import. TYPE_CHECKING block already had correct imports for all engine types.

---

### Task 4.3: Final TurnEngine cleanup [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/`

- [x] Count lines in TurnEngine (should be ~100, down from 479):
  ```bash
  wc -l game/strategy/engine/turn_engine.py
  ```
  Result: 222 lines (better than expected, but still above target)
- [x] Update module docstring to reflect new role as orchestrator
- [x] Verify all 5 tick phases still work correctly:
  - Phase 0: `self.resource_engine.process_per_turn_consumption(tick, empires)`
  - Phase 1: `self.order_processor.process_instant_orders(empires)`
  - Phase 2-3: `self.movement_engine.collect_movements()` + `apply_movements()`
  - Phase 4: `self.conflict_engine.resolve_all_conflicts(empires)`
- [x] Run full test suite: `pytest tests/`
- [x] Verify: All tests pass

**Notes:** TurnEngine is 222 lines (down from 479, 54% reduction). Docstring updated to clearly describe orchestration role and delegated engines. Also fixed tests in `test_turn_engine_strategy.py` and `test_resource_system.py` that were calling old `_process_per_turn_resources` and `_auto_disable_components_for_resource` methods (now delegated to ResourceManagementEngine). Updated patch locations from `game.core.registry.get_component_registry` to `game.strategy.engine.resource_management_engine.get_component_registry`.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] TurnEngine is 222 lines (verify with `wc -l`) - above 100 target but significant improvement
- [x] No legacy wrapper methods remain (`_calculate_next_hex`, `_spawn_complex`, `_spawn_ship`)
- [x] No unused imports
- [x] Run `pytest tests/` - all tests pass (4963 tests)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5
