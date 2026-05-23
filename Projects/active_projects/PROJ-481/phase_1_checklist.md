# Phase 1: Critical UI narrowings

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-481 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add the missing return type to the `StrategyModalWindow.check_clicked_inside_or_blocking` override — the sole CRITICAL UI finding. This is a pygame_gui `UIWindow` public override used in the event-dispatch pipeline; missing the annotation breaks the cross-layer contract.

---

## Tasks

### Task 1.1: Annotate `check_clicked_inside_or_blocking` [Simple]
**File:** `game/ui/screens/strategy_modal_window.py`
**Tests:** `pytest tests/ -k strategy_modal_window` then `mypy game/ui/screens/strategy_modal_window.py`

- [x] Add `-> bool` return annotation to `check_clicked_inside_or_blocking` (line 273); both return paths (L290 `False`, L292 `super().check_clicked_inside_or_blocking(event)`) are bool
- [x] Verify: `pytest tests/` passes; `mypy game/ui/screens/strategy_modal_window.py` shows no new errors

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-20_210540_type-audit/`. See `findings/source_audit.md` for the link._
