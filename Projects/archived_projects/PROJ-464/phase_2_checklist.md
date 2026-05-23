# Phase 2: Minor (bulk UI display narrowing)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-464 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Bulk-narrow the verified MINOR UI display helper `-> Any` returns and the `_to_tuple` cache helper. These are low-risk, internal UI-display narrowings.

---

## Tasks

### Task 2.1: Narrow UI display getter/formatter functions [Medium]
**File:** `game/ui/screens/builder/stat_getters.py`
**Tests:** `pytest tests/ --testmon` and `mypy game/ui/screens/builder/stat_getters.py game/ui/screens/builder/stat_rows_dynamic.py`

- [ ] Narrow the ~40 getter/formatter functions in `stat_getters.py` returning `-> Any` to `-> str | float | int` (or the specific display type each computes)
- [ ] Narrow the 23 module-level functions in `stat_rows_dynamic.py` (lines 36-557) returning `-> Any` to `-> dict[str, Any] | float | int`
- [ ] Verify: pytest passes; mypy shows no new errors on both files

### Task 2.2: Add _to_tuple return type [Simple]
**File:** `game/ui/pygame_gui_patch.py`
**Tests:** `pytest tests/ --testmon` and `mypy game/ui/pygame_gui_patch.py`

- [ ] Add `-> tuple | None` to `_to_tuple` (line 90) — used in `build_all_combined_ids` cache-key construction
- [ ] Verify: pytest passes; `mypy game/ui/pygame_gui_patch.py` shows no new errors

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-19_223900_type-audit/`. See `findings/source_audit.md` for the link._
