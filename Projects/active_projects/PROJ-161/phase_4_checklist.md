# Phase 4: Test Updates

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-161 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update all tests broken by the per-tick changes and remove obsolete tests. After this phase, all tests must pass.

---

## Tasks

### Task 4.1: Update Integration Harvesting Tests [Medium]
**File:** `tests/integration/strategy/turn_engine/test_harvesting.py`
**Tests:** `pytest tests/integration/strategy/turn_engine/test_harvesting.py`

- [ ] `test_harvesting_called_during_process_turn` (line 102):
  - Change to verify `process_harvesting_tick` called 100 times (not `process_harvesting` once)
  - Mock `process_harvesting_tick` instead of `process_harvesting`
- [ ] `test_harvesting_extracts_resources_end_to_end` (line 119):
  - Verify same total: 80.0 Metals after full turn (100 * 0.8 quality)
  - Verify planet depleted by 80.0 (from 5000 to 4920)
  - Use `pytest.approx` for floating-point comparison
- [ ] `test_harvesting_before_production` (line 147):
  - Rewrite completely: mock `process_harvesting_tick` and `process_construction_tick`
  - Verify `process_harvesting_tick` called before `process_construction_tick` within each tick
  - Fix existing bug: was mocking `process_production` (doesn't exist), should be `process_construction_tick`
- [ ] `test_harvesting_with_storage_cap` (line 168):
  - Verify storage cap still enforced: 950 + 100 harvest = capped at 1000
  - Use `pytest.approx` for comparison
- [ ] All 4 tests pass

**Notes:** The `_make_mock_engines()` helper (line 79) may need updating if it creates mocks for old method names.

---

### Task 4.2: Update Integration Maintenance Tests [Medium]
**File:** `tests/integration/strategy/turn_engine/test_maintenance.py`
**Tests:** `pytest tests/integration/strategy/turn_engine/test_maintenance.py`

- [ ] `test_maintenance_engine_called_during_process_turn` (line 124):
  - Change to verify `process_maintenance_tick` called 100 times
- [ ] `test_maintenance_called_after_harvesting` (line 134):
  - Rewrite: verify per-tick ordering (harvesting_tick before maintenance_tick within each tick)
  - Note: uses `_MockHarvestingEngine` (lines 30-36) -- update to mock new method
- [ ] `test_real_maintenance_deducts_facility_costs` (line 167):
  - Verify same total deduction after full turn with real engines
  - Use `pytest.approx` for floating-point comparison
- [ ] `test_real_maintenance_scuttles_facility` (line 179):
  - Verify scuttle still happens (on first tick that fails)
  - `last_scuttle_events` should contain the scuttle event
- [ ] `test_maintenance_engine_property_creates_default` (line 191):
  - Should pass unchanged (property creation logic unchanged)
- [ ] `test_maintenance_engine_injectable` (line 203):
  - Should pass unchanged (DI unchanged)
- [ ] All tests pass

**Notes:** The `_MockHarvestingEngine` at lines 30-36 and `_MockMaintenanceEngine` if present need updating to implement new per-tick methods.

---

### Task 4.3: Update E2E Economy Tests [Medium]
**File:** `tests/integration/strategy/test_economy_e2e.py`
**Tests:** `pytest tests/integration/strategy/test_economy_e2e.py`

- [ ] `test_full_turn_cycle_harvest_then_maintenance` (line 240):
  - Verify same net result: harvest 100 - maintenance 10 = 90 per turn
  - Use `pytest.approx`
- [ ] `test_empire_starts_with_resources_harvests_more` (line 267):
  - Verify same accumulation: 500 + 40 - 5 = 535
  - Use `pytest.approx`
- [ ] `test_harvesting_respects_storage_cap` (line 403):
  - Verify cap at 1000
- [ ] `test_harvesting_before_maintenance_order` (line 514):
  - Verify order still correct per-tick
  - Empire starts with 0, harvest gives 100, maintenance costs 10 -> net 90
- [ ] `test_multi_resource_construction` (line 442):
  - Verify construction still works with per-tick resource flow
- [ ] `test_non_operational_facilities_skip_harvest_and_maintenance` (line 594):
  - Verify skip behavior unchanged
- [ ] Run ALL E2E tests: `pytest tests/integration/strategy/test_economy_e2e.py -v`
- [ ] Fix any numerical rounding differences from tick spreading (use `pytest.approx`)

**Notes:** The `_make_economy_turn_engine()` helper (lines 210-218) creates TurnEngine with real engines -- should work with new per-tick methods automatically.

---

### Task 4.4: Remove Obsolete Production Engine Tests [Simple]
**File:** `tests/unit/strategy/production_engine/test_tick_consumption.py`
**Tests:** `pytest tests/unit/strategy/production_engine/test_tick_consumption.py`

- [ ] Delete `test_mid_turn_complex_triggers_partial_harvest` (lines 533-560)
- [ ] Delete `test_storage_recalculated_on_mid_turn_complex` (lines 562-589)
- [ ] Search for any other tests that pass `harvesting_engine` parameter to `process_construction_tick`
- [ ] Update those tests to remove the `harvesting_engine` parameter
- [ ] All remaining production engine tests pass

**Notes:**

---

### Task 4.5: Search for Any Other Broken Tests [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite
- [ ] Fix any remaining test failures related to:
  - Old `process_harvesting` method calls
  - Old `process_maintenance` method calls
  - `harvesting_engine` parameter in ProductionEngine
  - `_apply_partial_harvest` references
- [ ] All tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ -n 12` -- ALL tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
