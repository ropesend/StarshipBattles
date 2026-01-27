# Phase 4: Legacy Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-36 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Clean up deprecated methods and unused code

---

## Tasks

### Task 4.1: Remove legacy wrapper methods [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/test_turn_engine.py`

- [ ] Search for callers of `_calculate_next_hex`:
  ```bash
  grep -r "_calculate_next_hex" game/ tests/
  ```
- [ ] Update any callers to use `FleetMovementEngine.calculate_next_hex()` directly
- [ ] Remove `_calculate_next_hex` method (lines 243-252)

- [ ] Search for callers of `_spawn_complex`:
  ```bash
  grep -r "_spawn_complex" game/ tests/
  ```
- [ ] Update any callers to use `ProductionEngine._spawn_complex()` directly
- [ ] Remove `_spawn_complex` method (lines 196-202)

- [ ] Search for callers of `_spawn_ship`:
  ```bash
  grep -r "_spawn_ship" game/ tests/
  ```
- [ ] Update any callers to use `ProductionEngine._spawn_ship()` directly
- [ ] Remove `_spawn_ship` method (lines 204-210)

- [ ] Verify: No remaining references to removed methods

**Notes:**

---

### Task 4.2: Clean up imports and type hints [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/test_turn_engine.py`

- [ ] Review imports at top of file - remove unused:
  - `random` (moved to ConflictResolutionEngine)
  - `game.core.registry` (moved to ResourceManagementEngine)
  - `game.strategy.services.ship_stats_service` (if moved)
- [ ] Update TYPE_CHECKING block with new engine imports:
  ```python
  if TYPE_CHECKING:
      from game.strategy.interfaces.battle_resolver import IBattleResolver
      from game.strategy.engine.fleet_movement_engine import FleetMovementEngine
      from game.strategy.engine.production_engine import ProductionEngine
      from game.strategy.engine.fleet_order_processor import FleetOrderProcessor
      from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
      from game.strategy.engine.resource_management_engine import ResourceManagementEngine
  ```
- [ ] Verify no circular import issues:
  ```bash
  python -c "from game.strategy.engine.turn_engine import TurnEngine"
  ```
- [ ] Run `pytest tests/` to verify nothing broken

**Notes:**

---

### Task 4.3: Final TurnEngine cleanup [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/`

- [ ] Count lines in TurnEngine (should be ~100, down from 479):
  ```bash
  wc -l game/strategy/engine/turn_engine.py
  ```
- [ ] Update module docstring to reflect new role:
  ```python
  """
  Turn Engine - Strategy Layer Turn Orchestration

  PROJ-36: Refactored to be a lightweight orchestrator that delegates
  to specialized engines.

  Turn Phases:
      1. SUBTURN LOOP (100 ticks):
         - Phase 0: Per-turn resources (via ResourceManagementEngine)
         - Phase 1: Instant orders (via FleetOrderProcessor)
         - Phase 2: Calculate moves (via FleetMovementEngine)
         - Phase 3: Apply moves (via FleetMovementEngine)
         - Phase 4: Combat (via ConflictResolutionEngine)
      2. END-OF-TURN ORDERS (via FleetOrderProcessor)
      3. PRODUCTION (via ProductionEngine)

  Delegated Engines:
      - FleetMovementEngine: Movement calculation and application
      - ProductionEngine: Construction queue processing
      - FleetOrderProcessor: Order lifecycle management
      - ConflictResolutionEngine: Combat detection and resolution
      - ResourceManagementEngine: Per-turn resource consumption
  """
  ```
- [ ] Verify all 5 tick phases still work correctly:
  - Phase 0: `self.resource_engine.process_per_turn_consumption(tick, empires)`
  - Phase 1: `self.order_processor.process_instant_orders(empires)`
  - Phase 2-3: `self.movement_engine.collect_movements()` + `apply_movements()`
  - Phase 4: `self.conflict_engine.resolve_all_conflicts(empires)`
- [ ] Run full test suite: `pytest tests/`
- [ ] Verify: All tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] TurnEngine is ~100 lines (verify with `wc -l`)
- [ ] No legacy wrapper methods remain
- [ ] No unused imports
- [ ] Run `pytest tests/` - all tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
