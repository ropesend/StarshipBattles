# Phase 1: Add Type-Safety Guard to get_system_of_object

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-184 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add isinstance guard to auto-route Planet objects and prevent silent misuse

---

## Tasks

### Task 1.1: Add isinstance guard to GalaxySpatialIndex.get_system_of_object [Simple]
**File:** `game/strategy/data/galaxy_spatial_index.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py -x`

- [ ] Add isinstance(obj, Planet) check with auto-route to get_system_of_planet (line 44)
- [ ] Use runtime import `from game.strategy.data.planet import Planet` to avoid circular dependency
- [ ] Update docstring to say "Auto-routes Planet objects to get_system_of_planet()"
- [ ] Update facade docstring in `game/strategy/data/galaxy.py` (lines 203-217) to match

**Notes:**

### Task 1.2: Add unit tests for the type-safety guard [Simple]
**File:** `tests/unit/strategy/data/test_galaxy.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py -x`

- [ ] Add test: `test_get_system_of_object_autoroutes_planet` — passes a registered Planet, asserts correct system returned
- [ ] Add test: `test_get_system_of_object_returns_none_for_no_location` — passes object without location attribute
- [ ] Add test: `test_get_system_of_object_returns_system_for_fleet_at_system` — passes Fleet-like object at system global coord
- [ ] Add test: `test_get_system_of_object_returns_none_for_fleet_in_deep_space` — passes Fleet-like object NOT at system coord
- [ ] Run `pytest tests/unit/strategy/data/test_galaxy.py -x` — all pass

**Notes:**

### Task 1.3: Run full test suite [Simple]

- [ ] Run `pytest tests/ -n 12` — 12,366+ passed, 0 failed

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
