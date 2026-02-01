# Phase 4: Service Renaming (NCA-006, STR-003)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-46 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Rename calculator-pattern services: FleetMobilityService → FleetSpeedCalculator, ShipStatsService → ShipStatsCalculator

---

## Sub-phase 4A: FleetMobilityService → FleetSpeedCalculator

### Task 4A.1: Rename Class and File [Medium]
**File:** `game/strategy/services/fleet_speed_calculator.py` (renamed)
**Tests:** `pytest tests/unit/strategy/test_fleet_speed_calculator.py`

- [x] Rename class `FleetMobilityService` → `FleetSpeedCalculator`
- [x] Rename method `recalculate_fleet_speed()` → `update_fleet_speed()`
- [x] Update class docstring to reflect new name and purpose
- [x] Rename file: `fleet_mobility_service.py` → `fleet_speed_calculator.py`

**Notes:** Completed - class, docstring, method renamed, file renamed via git mv

---

### Task 4A.2: Update Production Imports [Medium]
**Files:** Multiple
**Tests:** `pytest tests/unit/strategy/ tests/integration/`

- [x] `game/strategy/data/fleet.py` - Update import and usages
- [x] `game/strategy/services/__init__.py` - Already empty, no change needed
- [x] `ui/builder/stats_config.py` - Updated comment reference
- [x] Search for any other imports of `FleetMobilityService`
- [x] Run affected tests

**Notes:** Updated fleet.py to import FleetSpeedCalculator and call update_fleet_speed()

---

### Task 4A.3: Update Test Imports [Simple]
**Files:** Test files
**Tests:** `pytest tests/unit/strategy/test_fleet_speed_calculator.py`

- [x] `tests/unit/strategy/test_fleet_mobility_service.py` - Update import and all class references
- [x] Renamed test file to `test_fleet_speed_calculator.py`
- [x] `tests/integration/test_strategic_abilities.py` - Updated import
- [x] Run all affected tests - 25 passed

**Notes:** All test files renamed and updated

---

## Sub-phase 4B: ShipStatsService → ShipStatsCalculator

### Task 4B.1: Rename Class and File [Medium]
**File:** `game/strategy/services/ship_stats_calculator.py` (renamed)
**Tests:** `pytest tests/unit/strategy/test_ship_stats_calculator.py`

- [x] Rename class `ShipStatsService` → `ShipStatsCalculator`
- [x] Update class docstring to reflect new name and purpose
- [x] Rename file: `ship_stats_service.py` → `ship_stats_calculator.py`

**Notes:** Completed via replace_all and git mv

---

### Task 4B.2: Update Production Imports [Complex]
**Files:** 14 files
**Tests:** `pytest tests/unit/strategy/ tests/integration/`

Production files to update:
- [x] `game/strategy/data/ship_instance.py`
- [x] `game/strategy/data/fleet.py`
- [x] `game/strategy/engine/resource_management_engine.py`
- [x] `game/strategy/services/__init__.py` - Already empty
- [x] `game/core/registry.py` - Updated docstring example
- [x] `game/ui/screens/fleet_report_filters.py`
- [x] `game/simulation/components/modifiers.py` - Updated comment references
- [x] Search for any other imports - none found

Run tests after each batch of updates.

**Notes:** All production files updated

---

### Task 4B.3: Update Test Imports [Complex]
**Files:** Test files (77+ test methods affected)
**Tests:** `pytest tests/unit/strategy/ tests/unit/services/`

Test files to update:
- [x] `tests/unit/strategy/test_ship_stats_service.py` - Renamed to test_ship_stats_calculator.py
- [x] `tests/unit/services/test_ship_stats_service_di.py` - Renamed to test_ship_stats_calculator_di.py
- [x] `tests/unit/strategy/test_ship_instance_proj08.py` - Updated
- [x] `tests/integration/test_resource_system.py` - Updated
- [x] `tests/integration/test_strategic_abilities.py` - Already updated in 4A
- [x] `tests/strategy/test_turn_engine_strategy.py` - Updated
- [x] `tests/unit/core/test_service_injection.py` - Updated
- [x] `tests/unit/strategy/test_fleet_report_filters.py` - Updated
- [x] `tests/unit/strategy/conftest.py` - Updated

Run all affected tests.

**Notes:** All test files updated, tests passing

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Grep for "FleetMobilityService" shows no occurrences
- [x] Grep for "ShipStatsService" shows no occurrences
- [x] Run `pytest tests/ --testmon` - 5775 passed, 1 skipped (6 unrelated failures in test_io_interactive.py)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5
