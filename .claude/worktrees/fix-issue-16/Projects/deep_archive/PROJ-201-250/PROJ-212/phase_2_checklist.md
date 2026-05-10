# Phase 2: OrderType/FleetOrder Extraction

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-212 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extract OrderType enum, FleetOrder class, and related order-type sets from the monolithic fleet.py into a lightweight module, eliminating 15+ transitive deferred imports across the codebase
**Priority:** High
**Effort:** Medium

---

## Context
`fleet.py` contains:
- `OrderType` enum (lightweight, widely imported)
- `FleetOrder` class (lightweight data class)
- Order-type sets (movement types, combat types, etc.)
- `Fleet` class (heavyweight — imports FleetResourceAggregator, triggers speed recalculation, etc.)

Anyone who needs just `OrderType` must transitively import the entire Fleet class and all its dependencies. This forces 15+ files to use deferred imports to avoid pulling in the heavyweight Fleet at module load time.

## Tasks

### Task 2.1: Create order_types.py module [Medium]
**File:** `game/strategy/data/order_types.py` (new)
**Tests:** `pytest tests/unit/strategy/data/ -x`

- [x] Read `game/strategy/data/fleet.py` to identify everything to extract:
  - `OrderType` enum
  - `FleetOrder` class
  - Order-type category sets (movement, combat, etc.)
- [x] Create `game/strategy/data/order_types.py` with extracted types
- [x] Update `fleet.py` to import from `order_types.py` (re-export for backward compat during transition)
- [x] Run tests, verify no regressions

**Notes:** Created order_types.py with OrderType, FleetOrder, MOVEMENT_ORDER_TYPES, ACTION_ORDER_TYPES. Fleet.py imports from order_types.py for internal use.

### Task 2.2: Update all consumers to import from order_types.py [Medium]
**Tests:** `pytest tests/ -n 12`

- [x] Grep for all imports of `OrderType` and `FleetOrder` across the codebase
- [x] Update each import to use `game.strategy.data.order_types` instead of `game.strategy.data.fleet`
- [x] For each file that previously deferred the import, promote to top-level where safe
- [x] Special attention to `command_handlers.py` (already top-level from Phase 1)
- [x] Special attention to `action_time_resolver.py` (RS-005: wrapper functions to defer OrderType)
- [x] Run full test suite, verify no regressions

**Notes:** Updated 15 game source files and 73 test files. All now import from order_types.py.

### Task 2.3: Remove backward compatibility re-exports [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/ -n 12`

- [x] Remove the re-exports of OrderType/FleetOrder from fleet.py
- [x] Grep to confirm no remaining imports from `fleet` for just OrderType/FleetOrder
- [x] Run full test suite, verify no regressions

**Notes:** fleet.py still imports OrderType/FleetOrder for internal use (type hints, from_dict deserialization). No consumers import these from fleet.py anymore - verified with grep. The imports in fleet.py are necessary for the class itself.

### Task 2.4: Clean up action_time_resolver wrapper functions [Simple]
**File:** `game/strategy/services/action_time_resolver.py`
**Finding:** RS-005 — wrapper functions `_get_order_to_ability_map()` and `_get_movement_order_types()` exist solely to defer OrderType import. After extraction, these can be replaced with direct top-level imports and module-level constants.
**Tests:** `pytest tests/unit/strategy/services/ -x`

- [x] Read file, confirm wrapper functions
- [x] Replace with direct top-level import from `order_types.py`
- [x] Convert the wrapper functions to module-level constants
- [x] Run tests, verify no regressions

**Notes:** Replaced `_get_order_to_ability_map()` with `ORDER_TO_ABILITY_MAP` dict and `_get_movement_order_types()` with `MOVEMENT_ORDER_TYPES` frozenset at module level.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Full test suite passes: `pytest tests/ -n 12`
- [x] Grep confirms no remaining deferred imports of OrderType/FleetOrder (except intentional ones)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
