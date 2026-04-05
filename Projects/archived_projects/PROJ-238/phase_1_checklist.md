# Phase 1: Merge OrderType Enum

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-238 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add ACTIVATE_SHIELD and DEACTIVATE_SHIELD to OrderType enum. Update all PlanetOrderType references to use OrderType. Remove PlanetOrderType enum.

---

## Tasks

### Task 1.1: Add Planet Order Types to OrderType Enum [Simple]
**File:** `game/strategy/data/order_types.py`
**Tests:** `python -m pytest tests/unit/strategy/data/ -q`

- [ ] Add to OrderType enum (after UNLOAD_POPULATION, ~line 35):
  ```python
  ACTIVATE_SHIELD = auto()
  DEACTIVATE_SHIELD = auto()
  ```
- [ ] Add to ACTION_ORDER_TYPES frozenset
- [ ] Add PLANET_ACTION_ORDER_TYPES frozenset (subset of ACTION_ORDER_TYPES, for engine filtering)

**Notes:**

### Task 1.2: Update All PlanetOrderType References [Medium]
**Files:** 7 production files + 2 test files reference PlanetOrderType
**Tests:** `python -m pytest tests/ -n 12 -q` after completing all

- [ ] `game/strategy/engine/planet_action_engine.py` — `PlanetOrderType` → `OrderType`
- [ ] `game/strategy/engine/planet_command_handlers.py` — `PlanetOrderType` → `OrderType`
- [ ] `game/strategy/services/planet_action_time_resolver.py` — update mapping keys
- [ ] `game/strategy/validation/planet_order_validator.py` — update local imports
- [ ] `game/strategy/data/planet_order_types.py` — PlanetOrder class uses OrderType, remove PlanetOrderType enum
- [ ] `tests/unit/strategy/engine/test_planet_action_engine.py` — update imports
- [ ] Any other files found via `grep -r "PlanetOrderType" game/ tests/`

### Task 1.3: Verify All Tests Pass [Simple]
**Tests:** `python -m pytest tests/ -n 12 -q`

- [ ] Full test suite passes with same count as baseline (14016+)
- [ ] No import errors

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] OrderType has ACTIVATE_SHIELD and DEACTIVATE_SHIELD
- [ ] No code references PlanetOrderType
- [ ] `python -m pytest tests/ -n 12` passes
- [ ] Update status to `Complete`, update plan.md
