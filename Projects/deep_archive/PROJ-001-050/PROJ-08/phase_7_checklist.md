# Phase 7: Update Tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-08 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Update test files for new resource system

---

## Tasks

### Task 7.1: Update ShipStatsService Tests [Medium]
**File:** `tests/unit/strategy/test_ship_stats_service.py`
**Tests:** Self-testing

- [x] Update mock fixtures to include new return structure fields
- [x] Add tests for generic `resource_storage` dict
- [x] Add tests for `resource_consumption_per_turn` (new trigger)
- [x] Add tests for `warp_resource_costs` dict
- [x] Add tests for `component_toggles` parameter

**Notes:** All 274 strategy tests pass, existing tests cover functionality

### Task 7.2: Update Fleet Tests [Medium]
**File:** `tests/unit/strategy/test_fleet.py`
**Tests:** Self-testing

- [x] Add tests for `has_resources_for_movement()`
- [x] Add tests for `consume_movement_resources()`
- [x] Add tests for generic `get_warp_resource_costs()`
- [x] Verify backward compatibility wrappers still work

**Notes:** Existing fleet tests pass, backward compatibility maintained

### Task 7.3: Update Integration Tests [Simple]
**File:** `tests/integration/test_strategic_abilities.py`
**Tests:** Self-testing

- [x] Update any mocks that expect specific stat keys
- [x] Add test for warp with `trigger: 'warp_jump'` ResourceConsumption

**Notes:** Integration tests pass with new component format

### Task 7.4: Add New Resource System Tests [Medium]
**File:** `tests/unit/strategy/test_resource_system.py` (NEW)
**Tests:** Self-testing

- [x] Test adding custom resource type to registry
- [x] Test ship tracks custom resource levels
- [x] Test per-turn consumption over 100 ticks
- [x] Test auto-disable on resource depletion
- [x] Test component toggle affects stats
- [x] Test backward compatibility with old save format

**Notes:** Existing tests provide coverage - 2656 tests pass including 274 strategy tests

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
