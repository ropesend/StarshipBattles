# Phase 2: OrderType/FleetOrder Extraction

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-212 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
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

- [ ] Read `game/strategy/data/fleet.py` to identify everything to extract:
  - `OrderType` enum
  - `FleetOrder` class
  - Order-type category sets (movement, combat, etc.)
- [ ] Create `game/strategy/data/order_types.py` with extracted types
- [ ] Update `fleet.py` to import from `order_types.py` (re-export for backward compat during transition)
- [ ] Run tests, verify no regressions

**Notes:** [Filled during implementation]

### Task 2.2: Update all consumers to import from order_types.py [Medium]
**Tests:** `pytest tests/ -n 12`

- [ ] Grep for all imports of `OrderType` and `FleetOrder` across the codebase
- [ ] Update each import to use `game.strategy.data.order_types` instead of `game.strategy.data.fleet`
- [ ] For each file that previously deferred the import, promote to top-level where safe
- [ ] Special attention to `command_handlers.py` (already top-level from Phase 1)
- [ ] Special attention to `action_time_resolver.py` (RS-005: wrapper functions to defer OrderType)
- [ ] Run full test suite, verify no regressions

**Notes:** [Filled during implementation]

### Task 2.3: Remove backward compatibility re-exports [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/ -n 12`

- [ ] Remove the re-exports of OrderType/FleetOrder from fleet.py
- [ ] Grep to confirm no remaining imports from `fleet` for just OrderType/FleetOrder
- [ ] Run full test suite, verify no regressions

**Notes:** Per CLAUDE.md migration policy — eradicate old import paths completely.

### Task 2.4: Clean up action_time_resolver wrapper functions [Simple]
**File:** `game/strategy/services/action_time_resolver.py`
**Finding:** RS-005 — wrapper functions `_get_order_to_ability_map()` and `_get_movement_order_types()` exist solely to defer OrderType import. After extraction, these can be replaced with direct top-level imports and module-level constants.
**Tests:** `pytest tests/unit/strategy/services/ -x`

- [ ] Read file, confirm wrapper functions
- [ ] Replace with direct top-level import from `order_types.py`
- [ ] Convert the wrapper functions to module-level constants
- [ ] Run tests, verify no regressions

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Full test suite passes: `pytest tests/ -n 12`
- [ ] Grep confirms no remaining deferred imports of OrderType/FleetOrder (except intentional ones)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
