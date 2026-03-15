# Phase 6: Cleanup & Verification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-220 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove dead code, verify all windows work correctly, run full test suite.

---

## Tasks

### Task 6.1: Remove dead filter code [Simple]
**Files:** Multiple
**Tests:** `pytest tests/ -n 12`

- [ ] `fleet_report_view_model.py`: Remove any dead binary filter attribute code that was replaced by FilterStateManager
- [ ] `fleet_report_sidebar.py`: Remove dead `_create_filter_button()` if no longer used by any filter (status filter may still use it)
- [ ] `fleet_report_filters.py`: Remove any legacy bool-handling code paths if all callers now use FilterState
- [ ] `empire_build_queue_filter_manager.py`: Remove old `filter_location_type`, `filter_status`, `filter_capabilities` dicts if fully replaced
- [ ] `empire_build_queue_sidebar.py`: Remove old `filter_toggle_buttons` dict if fully replaced
- [ ] `empire_build_queue_window.py`: Remove old filter state property accessors if no longer needed
- [ ] Search for any remaining references to removed attributes: `grep -r "filter_show_warp_capable\|filter_show_not_warp_capable\|filter_show_has_spaceyard\|filter_show_no_spaceyard\|filter_show_has_cargo\|filter_show_no_cargo" game/`
- [ ] Verify: `pytest tests/ -n 12` — all tests pass after cleanup

**Notes:** Follow the "eradicate old system" convention. No backward compat layers.

---

### Task 6.2: Verify consistent styling across all windows [Simple]
**Tests:** Manual visual inspection

- [ ] Open Fleet Report window → verify tri-state radio buttons render correctly
- [ ] Open Fleet Report → verify status filter (checkboxes) still works independently
- [ ] Open Build Queue window → verify tri-state radio buttons render correctly
- [ ] Open Planet List window → verify existing filters still work (type toggles, owner toggles, sliders)
- [ ] Verify all tri-state widgets use consistent sizing and spacing
- [ ] Verify Yes/No/Ignore labels are readable and correctly indicate state
- [ ] Verify IGNORE state shows all items (no filtering)
- [ ] Verify YES state shows only matching items
- [ ] Verify NO state shows only non-matching items

**Notes:**

---

### Task 6.3: Final full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] All 13,178+ tests pass (baseline: 13,178 passed, 2 skipped)
- [ ] No new skips or xfails introduced
- [ ] Document final test count

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] No dead filter code remains
- [ ] All 3 windows render correctly
- [ ] Full test suite passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate project complete
