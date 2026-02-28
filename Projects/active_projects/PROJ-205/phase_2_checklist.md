# Phase 2: Legacy Code Path Eradication

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-205 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove the legacy colonization path and the test-only `column_mgr` alias.

---

## Tasks

### Task 2.1: Remove legacy colonization code path [Medium]
**File:** `game/strategy/engine/fleet_order_processor.py`
**Tests:** `pytest tests/unit/strategy/test_fleet_order_processor.py tests/unit/strategy/engine/ tests/integration/strategy/ tests/integration/colonization/`

- [ ] Make `component_registry` parameter required (remove `Optional` and `= None` default) in `process_colonize()` signature (line 176)
- [ ] Remove legacy planet selection fallback: lines 242-244 (`else: final_planet = valid_candidates[0]`)
- [ ] Remove legacy fleet removal fallback: lines 276-278 (`else: empire.remove_fleet(fleet)`)
- [ ] Remove the `if component_registry is not None:` guard at line 249 (make the colony ship pre-check unconditional)
- [ ] Update `process_end_turn_orders()` caller at line 629 if needed (already passes registry)
- [ ] Update type annotation imports if `Optional` no longer needed for this param
- [ ] Remove any docstring references to "legacy behavior" or "When None, entire fleet is removed"

**Notes:** 19 tests call without registry - all need updating in Task 2.2

### Task 2.2: Update colonization tests to provide component_registry [Medium]
**Files:**
- `tests/unit/strategy/test_fleet_order_processor.py`
- `tests/unit/strategy/engine/test_process_colonize_validation.py`
- `tests/unit/strategy/engine/test_colonize_population.py`
- `tests/unit/strategy/test_engine_event_emission.py`
- `tests/integration/strategy/test_colonize_logic.py`
- `tests/integration/colonization/test_planet_specific_colonization.py`

**Tests:** `pytest tests/unit/strategy/test_fleet_order_processor.py tests/unit/strategy/engine/ tests/integration/strategy/ tests/integration/colonization/ -v`

- [ ] Add `component_registry` parameter to all 19 legacy test call sites
- [ ] Delete explicit legacy test: `test_process_colonize_legacy_without_registry_still_works` (~line 325 in test_process_colonize_validation.py)
- [ ] Delete `test_process_colonize_without_registry_removes_fleet` (~line 662 in test_fleet_order_processor.py)
- [ ] Update remaining tests to use modern behavior (fleet kept when ships remain, only colony ship removed)
- [ ] Run full colonization test suite

**Notes:** Follow pattern from existing registry-path tests (e.g., `test_process_colonize_with_registry_removes_ship` at line 574).

### Task 2.3: Remove column_mgr test alias [Simple]
**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [ ] Remove line 155: `self.column_mgr = self._column_manager  # Alias for tests`
- [ ] Fix comment on line 153-154: change "Store references for backward compatibility with tests" to "Store reference for scroll wheel handling"
- [ ] Keep `self.scroll_bar = self._virtual_table.scroll_bar` (line 154) - this IS production code

**Notes:**

### Task 2.4: Update tests using column_mgr [Simple]
**File:** `tests/unit/ui/screens/test_empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py -v`

- [ ] Replace all `win.column_mgr` references with `win._column_manager` (8 locations):
  - Line 111: `win.column_mgr = win._column_manager` → remove line entirely
  - Line 112: `win.column_mgr.handle_header_clicks` → `win._column_manager.handle_header_clicks`
  - Line 113: `win.column_mgr.rebuild_headers` → `win._column_manager.rebuild_headers`
  - Line 1592: `assert win.column_mgr is not None` → `assert win._column_manager is not None`
  - Line 1597: `win.column_mgr.sort_column_id` → `win._column_manager.sort_column_id`
  - Line 1598: `win.column_mgr.sort_descending` → `win._column_manager.sort_descending`
  - Line 1609: `win.column_mgr.sort_column_id` → `win._column_manager.sort_column_id`
  - Line 1610: `win.column_mgr.sort_descending` → `win._column_manager.sort_descending`
- [ ] Run tests

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/strategy/ tests/integration/strategy/ tests/integration/colonization/` passes
- [ ] `pytest tests/unit/ui/screens/test_empire_build_queue_window.py` passes
- [ ] `pytest tests/ --testmon` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
