# Phase 4: Test Updates

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-161 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Update all tests broken by the per-tick changes and remove obsolete tests. After this phase, all tests must pass.

---

## Tasks

### Task 4.1: Update Integration Harvesting Tests [Medium] ✓
**File:** `tests/integration/strategy/turn_engine/test_harvesting.py`
**Tests:** `pytest tests/integration/strategy/turn_engine/test_harvesting.py`

- [x] `test_harvesting_called_during_process_turn` - Updated to verify 100 tick calls
- [x] `test_harvesting_extracts_resources_end_to_end` - Already passing (no changes needed)
- [x] `test_harvesting_before_production` - Rewritten for per-tick ordering (1-100 ticks)
- [x] `test_harvesting_with_storage_cap` - Already passing (no changes needed)
- [x] All 4 tests pass

**Notes:** Tests updated for 1-indexed ticks (1-100, not 0-99).

---

### Task 4.2: Update Integration Maintenance Tests [Medium] ✓
**File:** `tests/integration/strategy/turn_engine/test_maintenance.py`
**Tests:** `pytest tests/integration/strategy/turn_engine/test_maintenance.py`

- [x] `test_maintenance_engine_called_during_process_turn` - Updated to verify 100 tick calls
- [x] `test_maintenance_called_after_harvesting` - Rewritten for per-tick ordering (1-100 ticks)
- [x] `test_real_maintenance_deducts_facility_costs` - Already passing (no changes needed)
- [x] `test_real_maintenance_scuttles_facility` - Already passing (no changes needed)
- [x] `test_maintenance_engine_property_creates_default` - Already passing (no changes needed)
- [x] `test_maintenance_engine_injectable` - Already passing (no changes needed)
- [x] All 6 tests pass

**Notes:** _MockHarvestingEngine already had process_harvesting_tick method from Phase 2.

---

### Task 4.3: Update E2E Economy Tests [Medium] ✓
**File:** `tests/integration/strategy/test_economy_e2e.py`
**Tests:** `pytest tests/integration/strategy/test_economy_e2e.py`

- [x] `test_full_turn_cycle_harvest_then_maintenance` - Already passing
- [x] `test_empire_starts_with_resources_harvests_more` - Already passing
- [x] `test_harvesting_respects_storage_cap` - Already passing
- [x] `test_harvesting_before_maintenance_order` - Already passing
- [x] `test_multi_resource_construction` - Already passing
- [x] `test_non_operational_facilities_skip_harvest_and_maintenance` - Already passing
- [x] `test_maintenance_failure_causes_facility_scuttle` - Updated expectation: with per-tick
      maintenance, resources are drained before failure (20.0 → 0.0), not untouched
- [x] All 15 E2E tests pass

**Notes:** Per-tick behavior means partial payment occurs before scuttle. Test expectations updated.

---

### Task 4.4: Remove Obsolete Production Engine Tests [Simple] ✓
**File:** `tests/unit/strategy/production_engine/test_tick_consumption.py`
**Tests:** `pytest tests/unit/strategy/production_engine/test_tick_consumption.py`

- [x] Tests already deleted in Phase 3 (with comment at line 533)
- [x] No tests pass harvesting_engine parameter (removed in Phase 3)
- [x] All 17 production engine tests pass

**Notes:** Obsolete tests were removed in Phase 3 as part of _apply_partial_harvest removal.

---

### Task 4.5: Search for Any Other Broken Tests [Simple] ✓
**Tests:** `pytest tests/ -n 12`

- [x] Run full test suite: 11959 passed, 13 failed (pre-existing UI issues)
- [x] No PROJ-161-related test failures
- [x] All 112 PROJ-161 relevant tests pass
- [x] 13 failures are pre-existing UI issues (transfer dialog, cargo mode) - verified
      by checking against pre-PROJ-161 commit (same tests failed)

**Notes:** Pre-existing UI test failures in transfer_dialog and cargo mode tests are unrelated to PROJ-161.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/ -n 12` -- PROJ-161 tests pass (pre-existing UI failures excluded)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5
