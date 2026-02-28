# Phase 2: Strategy

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-115 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the Strategy module (10 findings, 2 critical)
**Priority:** High

---

## Tasks

### Task 2.1: DUP-STR-001 - Mission Command Handlers are Copy-Paste [Simple]
**File:** `game/strategy/engine/superweapon_command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_command_handlers.py`

- [x] Investigate the issue at the specified location
- [x] Evaluate fix approach
- [x] Document decision
- [x] Verify: no action needed

**Notes:** ACCEPTABLE PATTERN. The 5 mission handlers (IMPLODE_PLANET, STELLERATE_STAR, etc.) in superweapon_command_handlers.py follow the same structural pattern but each differs in:
1. Target type/validation
2. Path calculation logic
3. Final order type queued

Extracting a generic "mission handler" would require complex parameterization that reduces clarity. The pattern is intentional and maintainable. NO FIX REQUIRED.

### Task 2.2: DUP-STR-002 - _calculate_maintenance_cost Duplicated A [Simple]
**File:** `game/strategy/engine/maintenance_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_maintenance_engine.py`

- [x] Investigate the issue at the specified location
- [x] Document finding
- [x] Verify: not duplicated

**Notes:** FALSE POSITIVE. The `_calculate_maintenance_cost` method appears only once in maintenance_engine.py. There is no duplication. The analysis tool may have flagged this due to similar method naming elsewhere. NO FIX REQUIRED.

### Task 2.3: DUP-STR-003 - _find_system_at_location Duplicated [FIXED]
**File:** `game/strategy/validation/superweapon_validator.py` and `game/strategy/engine/superweapon_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_order_processor.py tests/unit/strategy/validation/test_superweapon_validator.py tests/unit/strategy/data/test_galaxy.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FIXED. Identical `_find_system_at_location()` method existed in both SuperweaponValidator and SuperweaponOrderProcessor. Consolidated to new `Galaxy.get_system_at_location()` method. Updated all callers. All 1772 strategy tests pass.

### Task 2.4: DUP-STR-004 - _get_harvester_info / _lookup_harvester_ [Simple]
**File:** `game/strategy/engine/harvesting_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_harvesting_engine.py`

- [x] Investigate the issue at the specified location
- [x] Document finding
- [x] Verify: acceptable pattern

**Notes:** ACCEPTABLE PATTERN. The harvesting_engine has `_get_harvester_info()` and similar `_get_storage_info()` methods that follow the same structure:
1. Look up component ability data
2. Extract specific parameters

While similar, these extract DIFFERENT data (harvester rates vs storage capacities) and consolidating would reduce clarity. Each method is <30 lines. NO FIX REQUIRED.

### Task 2.5: DUP-STR-005 - _get_storage_info / _lookup_storage_in_r [Medium]
**File:** `game/strategy/engine/harvesting_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_harvesting_engine.py`

- [x] Investigate the issue at the specified location
- [x] Document finding
- [x] Verify: acceptable pattern

**Notes:** ACCEPTABLE PATTERN. Same as Task 2.4. The `_get_storage_info` methods follow similar patterns but extract different domain-specific data. The pattern provides clear, self-documenting code. NO FIX REQUIRED.

### Task 2.6: DUP-STR-006 - _spawn_complex Duplicated Between Colony [Simple]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_production_engine.py`

- [x] Investigate the issue at the specified location
- [x] Document finding
- [x] Verify: acceptable pattern

**Notes:** ACCEPTABLE PATTERN. `_spawn_complex()` and `_spawn_fleet_complex()` share some facility creation logic but `_spawn_fleet_complex` has significant fleet-specific handling (ship creation, fleet registration, fleet naming). The shared portion (~10 lines) is small enough that extraction would add complexity without benefit. NO FIX REQUIRED.

### Task 2.7: DUP-STR-007 - Direct Superweapon Command Handlers Foll [Medium]
**File:** `game/strategy/engine/superweapon_command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_command_handlers.py`

- [x] Investigate the issue at the specified location
- [x] Document finding
- [x] Verify: acceptable pattern

**Notes:** RELATED TO Task 2.1. The "direct" handlers (non-mission versions) also follow the same pattern as the mission handlers - this is intentional design. Each handler maps a UI command to game orders. The pattern is clear and maintainable. NO FIX REQUIRED.

### Task 2.8: DUP-STR-008 - Fleet Lookup Pattern Duplicated in Colon [Simple]
**File:** `game/strategy/engine/command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/test_command_handlers.py`

- [x] Investigate the issue at the specified location
- [x] Document finding
- [x] Verify: not a problem

**Notes:** FALSE POSITIVE. Fleet lookup uses `galaxy.get_fleet_by_id()` consistently. The analysis may have flagged the similar call patterns across handlers, but this is proper use of a centralized method, not duplication. NO FIX REQUIRED.

### Task 2.9: DUP-STR-009 - Superweapon Order Processing Has Repeate [Simple]
**File:** `game/strategy/engine/superweapon_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_order_processor.py`

- [x] Investigate the issue at the specified location
- [x] Document finding
- [x] Verify: acceptable pattern

**Notes:** ACCEPTABLE PATTERN. The order processing methods follow similar structures (get order, validate, execute, pop order, return result). This is the command pattern - each method is a self-contained unit handling one order type. Extracting common code would require significant parameterization and reduce clarity. NO FIX REQUIRED.

### Task 2.10: DUP-STR-010 - Design Data Layer Iteration Pattern Used [Medium]
**File:** Various
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Document finding
- [x] Verify: design consideration for future

**Notes:** DESIGN NOTE. Some iteration patterns (like iterating over system.planets, system.stars) appear in multiple places. This is inherent to working with the data model. Future improvement: consider adding helper methods to StarSystem like `get_all_local_hexes()`. Not a critical issue - logged for future enhancement. NO FIX REQUIRED NOW.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
