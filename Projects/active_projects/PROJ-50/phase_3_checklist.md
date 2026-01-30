# Phase 3: Strategy Layer Services

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-50 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove fallbacks from strategy services

---

## Tasks

### Task 3.1: Update ShipStatsCalculator [Simple]
**File:** `game/strategy/services/ship_stats_calculator.py`
**Tests:** `pytest tests/unit/strategy/test_ship_stats_calculator*.py -v`

- [ ] Remove import of `get_default_registry_provider` (line 20)
- [ ] Remove import of `get_default_registries` (line 19)
- [ ] Remove `_get_registries_fallback()` static method (lines 72-90)
- [ ] Change constructor: `registries: Optional[GameRegistries] = None` to `registries: GameRegistries`
- [ ] Remove fallback in `__init__` (line 68)
- [ ] Add validation: `if registries is None: raise TypeError("registries is required")`

**Notes:**

---

### Task 3.2: Update ResourceManagementEngine [Simple]
**File:** `game/strategy/engine/resource_management_engine.py`
**Tests:** `pytest tests/unit/strategy/ -v`

- [ ] Remove import of `get_default_registry_provider` (line 17)
- [ ] Remove fallback conditional (line ~117)
- [ ] Make registries required in constructor
- [ ] Add validation

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/unit/strategy/ -v` - all pass
- [ ] Run `grep -r "get_default_registry_provider" game/strategy/services/` - returns 0
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
