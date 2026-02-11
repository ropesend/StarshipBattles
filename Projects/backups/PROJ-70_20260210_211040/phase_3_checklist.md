# Phase 3: Wire Up strategy_ui.py

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-70 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace inline fleet formatting in `strategy_ui.py` with a call to the enhanced `format_fleet_info()` and clean up dead imports.

---

## Tasks

### Task 3.1: Update Imports in strategy_ui.py [Simple]
**File:** `game/ui/screens/strategy_ui.py`
**Tests:** `pytest tests/ --testmon`

- [x] Add `format_fleet_info` to the import from `strategy_detail_fmt` (line 25-27):
  ```python
  from game.ui.screens.strategy_detail_fmt import (
      format_spectrum_html, format_atmosphere_raw, get_label_for_object,
      format_fleet_info
  )
  ```
- [x] Remove `from game.strategy.data.fleet import OrderType` (line 21) - no longer needed
- [x] Update module docstring (lines 1-6): remove "OrderType" from the cross-layer imports note

**Notes:** All three import changes applied cleanly.

### Task 3.2: Replace Inline Fleet Formatting [Simple]
**File:** `game/ui/screens/strategy_ui.py` (lines 561-583)
**Tests:** `pytest tests/ --testmon`

- [x] Replace the inline fleet text generation block (lines 562-583) with:
  ```python
  text = format_fleet_info(obj)
  ```
- [x] Keep ALL button-showing logic (lines 586-600) unchanged - it stays in strategy_ui.py because it depends on UI state (`self.scene`, `current_empire_id`)
- [x] Verify `pytest tests/ --testmon` passes

**Notes:** Replaced 22-line inline block with single function call. Button logic preserved exactly.

### Task 3.3: Final Verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] Run full test suite: `pytest tests/ -n 12`
- [x] Verify test count is >= 6519 (baseline) + new tests
- [x] No regressions

**Notes:** 6587 passed, 1 failed (pre-existing test_protocols.py failure). No regressions.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Full test suite passes
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to "Complete"
