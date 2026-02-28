# Phase 3: ShipInstance Generic Methods

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-08 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add generic resource methods and component toggle support

---

## Tasks

### Task 3.1: Add Component Toggles Field [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/test_ship_instance.py`

- [x] Add `component_toggles: Dict[str, bool] = field(default_factory=dict)` to dataclass

**Notes:** Line 46 defines the field

### Task 3.2: Add Generic Resource Methods [Medium]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/`

- [x] Add `get_resource_capacity()`, `get_current_resource()`, `consume_resource()`
- [x] Add `get_all_resource_costs_per_hex()`, `get_all_resource_costs_per_turn()`
- [x] Add `get_warp_resource_costs()`

**Notes:** Lines 297-372 implement all generic resource methods

### Task 3.3: Add Component Toggle Methods [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/`

- [x] Add `set_component_enabled()` and `is_component_enabled()` methods

**Notes:** Lines 376-401 implement toggle methods with cache invalidation

### Task 3.4: Update get_calculated_stats to Pass Toggles [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/`

- [x] Update `get_calculated_stats()` to pass `component_toggles` to service

**Notes:** Lines 171-175 pass `component_toggles` to `calculate_stats()`

### Task 3.5: Update Serialization [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/`

- [x] Add `component_toggles` to `to_dict()`
- [x] Add `component_toggles` to `from_dict()`

**Notes:** Line 593 in `to_dict()`, line 613 in `from_dict()`, line 643 in `clone()`

### Task 3.6: Mark Legacy Methods as Deprecated [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** No test changes needed

- [x] Update docstrings for legacy methods (or keep for backward compatibility)

**Notes:** Legacy methods retained for backward compatibility

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
