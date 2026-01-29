# Phase 4: Service Renaming (NCA-006, STR-003)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-46 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Rename calculator-pattern services: FleetMobilityService → FleetSpeedCalculator, ShipStatsService → ShipStatsCalculator

---

## Sub-phase 4A: FleetMobilityService → FleetSpeedCalculator

### Task 4A.1: Rename Class and File [Medium]
**File:** `game/strategy/services/fleet_mobility_service.py`
**Tests:** `pytest tests/unit/strategy/test_fleet_mobility_service.py`

- [ ] Rename class `FleetMobilityService` → `FleetSpeedCalculator`
- [ ] Rename method `recalculate_fleet_speed()` → `update_fleet_speed()`
- [ ] Update class docstring to reflect new name and purpose
- [ ] Rename file: `fleet_mobility_service.py` → `fleet_speed_calculator.py`

**Notes:**

---

### Task 4A.2: Update Production Imports [Medium]
**Files:** Multiple
**Tests:** `pytest tests/unit/strategy/ tests/integration/`

- [ ] `game/strategy/data/fleet.py` - Update import and usages
- [ ] `game/strategy/services/__init__.py` - Update exports if present
- [ ] `ui/builder/stats_config.py` - Update import if present
- [ ] Search for any other imports of `FleetMobilityService`
- [ ] Run affected tests

**Notes:**

---

### Task 4A.3: Update Test Imports [Simple]
**Files:** Test files
**Tests:** `pytest tests/unit/strategy/test_fleet_mobility_service.py`

- [ ] `tests/unit/strategy/test_fleet_mobility_service.py` - Update import and all class references
- [ ] Consider renaming test file to `test_fleet_speed_calculator.py`
- [ ] `tests/integration/test_strategic_abilities.py` - Update import if present
- [ ] Run all affected tests

**Notes:**

---

## Sub-phase 4B: ShipStatsService → ShipStatsCalculator

### Task 4B.1: Rename Class and File [Medium]
**File:** `game/strategy/services/ship_stats_service.py`
**Tests:** `pytest tests/unit/strategy/test_ship_stats_service.py`

- [ ] Rename class `ShipStatsService` → `ShipStatsCalculator`
- [ ] Update class docstring to reflect new name and purpose
- [ ] Rename file: `ship_stats_service.py` → `ship_stats_calculator.py`

**Notes:**

---

### Task 4B.2: Update Production Imports [Complex]
**Files:** 14 files
**Tests:** `pytest tests/unit/strategy/ tests/integration/`

Production files to update:
- [ ] `game/strategy/data/ship_instance.py`
- [ ] `game/strategy/data/fleet.py`
- [ ] `game/strategy/engine/resource_management_engine.py`
- [ ] `game/strategy/services/__init__.py` - Update exports
- [ ] `game/core/registry.py` - Update if referenced
- [ ] `game/ui/screens/fleet_report_filters.py`
- [ ] `game/simulation/components/modifiers.py` - Check if it imports this
- [ ] Search for any other imports

Run tests after each batch of updates.

**Notes:**

---

### Task 4B.3: Update Test Imports [Complex]
**Files:** Test files (77+ test methods affected)
**Tests:** `pytest tests/unit/strategy/ tests/unit/services/`

Test files to update:
- [ ] `tests/unit/strategy/test_ship_stats_service.py` - 77 methods, rename all references
- [ ] Consider renaming to `test_ship_stats_calculator.py`
- [ ] `tests/unit/services/test_ship_stats_service_di.py` - Update imports
- [ ] Consider renaming to `test_ship_stats_calculator_di.py`
- [ ] `tests/unit/strategy/test_ship_instance_proj08.py` - Update if affected
- [ ] `tests/integration/test_resource_system.py` - Update if affected
- [ ] `tests/integration/test_strategic_abilities.py` - Update if affected
- [ ] `tests/strategy/test_turn_engine_strategy.py` - Update if affected

Run all affected tests.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Grep for "FleetMobilityService" shows no occurrences
- [ ] Grep for "ShipStatsService" shows no occurrences
- [ ] Run `pytest tests/unit/strategy/ tests/integration/` - all tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
