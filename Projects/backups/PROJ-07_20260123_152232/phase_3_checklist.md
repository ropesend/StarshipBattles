# Phase 3: Refactor ShipInstance Methods

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-07 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace all expected_stats reads with get_calculated_stats()

---

## Tasks

### Task 3.1: Refactor HP and resource methods [Medium]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/`

- [x] Refactor `get_hp_percentage()` to use calculated stats
- [x] Refactor `get_resource_percentage()` to use calculated stats
- [x] Refactor `get_hp_display()` to use calculated stats
- [x] Refactor `get_resource_display()` to use calculated stats

**Notes:** All methods now call get_calculated_stats() instead of accessing expected_stats directly.

### Task 3.2: Refactor fuel methods [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/`

- [x] Refactor `get_fuel_cost_per_hex()` to use calculated stats
- [x] Refactor `get_current_fuel()` to use calculated stats
- [x] Refactor `consume_fuel()` to use calculated stats

**Notes:** Complete.

### Task 3.3: Refactor energy and repair methods [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/`

- [x] Refactor `get_warp_energy_cost()` to use calculated stats
- [x] Refactor `get_current_energy()` to use calculated stats
- [x] Refactor `consume_energy()` to use calculated stats
- [x] Refactor `repair()` to use calculated stats
- [x] Refactor `resupply()` to use calculated stats

**Notes:** Complete.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
