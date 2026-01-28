# Phase 8: Audit Fixes (Cycle 3)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-38 8`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Fix DI test pollution bug found in Audit Cycle 3

---

## Root Cause Analysis (Audit Cycle 3)

### Audit Cycle 3 Findings

**Phase 7 incorrectly claimed:** "15 failures are PRE-EXISTING bugs with module-level singleton aliases"

**Audit Cycle 3 investigation proved:** These are **PROJ-38 REGRESSIONS**

**Evidence:**
1. Checkout pre-PROJ-38 code (commit `6623075`)
2. Run: `pytest tests/unit/entities/test_ship_helpers.py tests/unit/entities/test_hull_layer.py tests/unit/refactor/test_multi_ability_effects.py -n 0`
3. **Result: 67 passed, 0 failed** (tests pass on pre-PROJ-38 code!)
4. Current code: 15 failures

### Confirmed Root Cause

The DI test files added by PROJ-38 call `set_default_registries(mock_registries)` without cleanup:

| File | `set_default_registries` calls | Cleanup fixture |
|------|-------------------------------|-----------------|
| `test_workshop_context_di.py` | 6 calls | **NONE** |
| `test_workshop_viewmodel_di.py` | 2 calls | **NONE** |
| `test_vehicle_design_service_di.py` | 1 call | **NONE** |
| `test_ship_stats_service_di.py` | 1 call | **NONE** |
| `test_modifier_service_di.py` | 1 call | **NONE** |
| `test_component_di.py` | 3 calls | **NONE** |
| `test_ship_di.py` | 2 calls | **NONE** |

### Pollution Path

1. `test_workshop_context_di.py` runs (alphabetically before `tests/unit/entities/`)
2. It calls `set_default_registries(mock_registries)` where `mock_registries.resources = {}`
3. **No cleanup occurs**
4. Later tests in `tests/unit/entities/` run
5. Ship class's module-level `VEHICLE_CLASSES` was captured at import with full data
6. But `get_vehicle_classes()` now returns mock data (incomplete)
7. Mismatch causes assertion failures

---

## Tasks

### Task 8.1: Add Cleanup Fixture to DI Test Files [Critical] ✓ COMPLETE

Add an autouse fixture to each DI test file that restores `_default_registries` after each test.

**Files to fix:**
- [x] `tests/unit/builder/test_workshop_context_di.py`
- [x] `tests/unit/builder/test_workshop_viewmodel_di.py`
- [x] `tests/unit/services/test_vehicle_design_service_di.py`
- [x] `tests/unit/services/test_ship_stats_service_di.py`
- [x] `tests/unit/services/test_modifier_service_di.py`
- [x] `tests/unit/entities/test_component_di.py`
- [x] `tests/unit/entities/test_ship_di.py`

**Fixture pattern:**
```python
@pytest.fixture(autouse=True)
def restore_default_registries():
    """Restore _default_registries after each test to prevent pollution."""
    import game.core.registry as registry_module
    original = registry_module._default_registries
    yield
    registry_module._default_registries = original
```

**Tests:** `pytest tests/ -n 0 -q` should show 0 failures

**Notes:** Added autouse cleanup fixture to all 7 DI test files. Each fixture saves the original `_default_registries` value before the test and restores it after.

---

### Task 8.2: Verify Full Suite with -n 0 [Simple] ✓ COMPLETE

- [x] Run: `pytest tests/ -n 0 --tb=short -q`
- [x] Result should be: 5159+ passed, 0 failed
- [x] Document actual pass count

**Notes:** 5159 passed, 1 skipped, 0 failed (134.86s)

---

### Task 8.3: Verify Full Suite with -n auto [Simple] ✓ COMPLETE

- [x] Run: `pytest tests/ -n auto --tb=short -q`
- [x] Result should be: 5159+ passed, 0 failed
- [x] Confirm no new regressions

**Notes:** 5159 passed, 1 skipped, 0 failed (24.08s)

---

## Phase Completion Checklist

- [x] Task 8.1 complete (cleanup fixtures added to all 7 DI test files)
- [x] Task 8.2 complete (full suite passes with -n 0)
- [x] Task 8.3 complete (full suite passes with -n auto)
- [x] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Awaiting Audit Cycle 4"

## Summary

PROJ-38 introduced test pollution in its DI test files. Each file that calls `set_default_registries()` must have a cleanup fixture to restore the original value after the test. This fix was straightforward - added autouse fixtures to all 7 affected files.

**Result:** All 5159 tests pass with both `-n 0` (single process) and `-n auto` (parallel).
