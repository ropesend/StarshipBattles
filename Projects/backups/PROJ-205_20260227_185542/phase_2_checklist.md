# Phase 2: Legacy Code Path Eradication

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-205 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove the legacy colonization path and the test-only `column_mgr` alias.

---

## Tasks

### Task 2.1: Remove legacy colonization code path [Medium]
**File:** `game/strategy/engine/fleet_order_processor.py`
**Tests:** `pytest tests/unit/strategy/test_fleet_order_processor.py tests/unit/strategy/engine/ tests/integration/strategy/ tests/integration/colonization/`

- [x] Make `component_registry` parameter required (remove `Optional` and `= None` default) in `process_colonize()` signature (line 176)
- [x] Remove legacy planet selection fallback: lines 242-244 (`else: final_planet = valid_candidates[0]`)
- [x] Remove legacy fleet removal fallback: lines 276-278 (`else: empire.remove_fleet(fleet)`)
- [x] Remove the `if component_registry is not None:` guard at line 249 (make the colony ship pre-check unconditional)
- [x] Update `process_end_turn_orders()` caller - added guard for COLONIZE requiring registry
- [x] Update docstrings to remove legacy references
- [x] Also updated validator to use duck typing for test compatibility

**Notes:** Updated to duck typing (hasattr) in fleet_order_processor and colonize_validator for test mock compatibility.

### Task 2.2: Update colonization tests to provide component_registry [Medium]
**Files:**
- `tests/unit/strategy/test_fleet_order_processor.py`
- `tests/unit/strategy/engine/test_process_colonize_validation.py`
- `tests/unit/strategy/engine/test_colonize_population.py`
- `tests/unit/strategy/test_engine_event_emission.py`
- `tests/integration/strategy/test_colonize_logic.py`
- `tests/integration/colonization/test_planet_specific_colonization.py`

**Tests:** `pytest tests/unit/strategy/test_fleet_order_processor.py tests/unit/strategy/engine/ tests/integration/strategy/ tests/integration/colonization/ -v`

- [x] Add `component_registry` parameter to all legacy test call sites
- [x] Delete explicit legacy test: `test_process_colonize_legacy_without_registry_still_works`
- [x] Delete `test_process_colonize_without_registry_removes_fleet`
- [x] Delete `test_colonize_backward_compatible_without_registry` from integration tests
- [x] Delete `test_colonize_without_registry_uses_legacy_behavior` from planet_specific tests
- [x] Update remaining tests to use modern behavior
- [x] Run full colonization test suite - 63 tests pass

**Notes:** Added component_registry fixtures and updated all test files.

### Task 2.3: Remove column_mgr test alias [Simple]
**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [x] Remove line 155: `self.column_mgr = self._column_manager  # Alias for tests`
- [x] Fix comment on line 153-154: changed to "Store reference for scroll wheel handling"
- [x] Kept `self.scroll_bar = self._virtual_table.scroll_bar` (production code)

**Notes:**

### Task 2.4: Update tests using column_mgr [Simple]
**File:** `tests/unit/ui/screens/test_empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py -v`

- [x] Removed backward compatibility alias line
- [x] Updated all `win.column_mgr` references to `win._column_manager`
- [x] Renamed test from `test_column_mgr_attribute_exists` to `test_column_manager_attribute_exists`
- [x] Run tests - 118 passed

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/strategy/ tests/integration/strategy/ tests/integration/colonization/` passes
- [x] `pytest tests/unit/ui/screens/test_empire_build_queue_window.py` passes
- [x] `pytest tests/ -n 12` passes (12831 passed, 1 skipped)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
