# Phase 2: UI-window/panel constructor-smoke + bypass_init cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-491 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Clean up 7 UI window/panel test files. Some already use `bypass_init` (canonical at `tests/fixtures/ui_widget_factory.py:254-328`) but retain ad hoc `__new__` / manual-attr leftover patterns alongside; others still use the old pattern entirely. Either way: migrate fully to `bypass_init` AND/OR add a constructor-smoke test so constructor regressions are catchable. No production code changes.

**Mechanical pattern:**
- For files already using `bypass_init`: scan for leftover `Class.__init__ = lambda ...` or `Class.__new__(Class)` patterns inside specific test methods and replace.
- For files not yet using `bypass_init`: replace the `__new__` + manual attr wiring with `bypass_init(Class, attr1=..., attr2=...)`.
- Add a constructor-smoke test (real construction with minimal real deps) where missing — surfacing regressions is the goal.

---

## Tasks

### Task 2.1: test_orders_window.py — bypass_init smoke test
**Source:** PROJ-479 Task 3.16
**File:** `tests/unit/ui/screens/test_orders_window.py` (lines 48-59)
**Tests:** `pytest tests/unit/ui/screens/test_orders_window.py`

- [ ] Replace `_make_window` bypass_init + MagicMock `ui_manager` with real construction so constructor regressions are catchable. If constructor genuinely cannot run without pygame display, fall back to `bypass_init` (canonical) but ensure at least one smoke test uses real construction.
- [ ] Verify: tests pass.

### Task 2.2: test_event_log_window.py — _make_window no-op lambda
**Source:** PROJ-479 Task 3.13
**File:** `tests/unit/ui/screens/test_event_log_window.py` (lines 44-88)
**Tests:** `pytest tests/unit/ui/screens/test_event_log_window.py`

- [ ] Replace `_make_window` no-op `__init__` lambda + 10+ manually-wired attrs with real construction + `bypass_init` from `tests/fixtures/ui_widget_factory.py:254-328`.
- [ ] Verify: tests pass.

### Task 2.3: test_empire_build_queue_window.py — __init__ no-op + manual wiring
**Source:** PROJ-479 Task 3.6
**File:** `tests/unit/ui/screens/test_empire_build_queue_window.py` (lines 63-100)
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [ ] Replace `__init__` patch + manual 30+ attr wiring with `bypass_init` from `tests/fixtures/ui_widget_factory.py:254-328`.
- [ ] Verify: tests pass.

### Task 2.4: test_build_queue_list_window.py — pygame_gui kill patches
**Source:** PROJ-479 Task 3.7
**File:** `tests/unit/ui/screens/test_build_queue_list_window.py` (lines 264-280)
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_list_window.py`

- [ ] Wrap pygame_gui `UIWindow.kill` behind an overridable method (test-side wrapper, not production change) OR extend the `bypass_init` pattern to register a kill-side-effect stub. Avoid patching pygame_gui directly.
- [ ] Verify: tests pass.

### Task 2.5: test_fleet_report_sidebar.py — 4-patch nested stack
**Source:** PROJ-479 Task 3.11
**File:** `tests/unit/ui/screens/test_fleet_report_sidebar.py` (lines 38-48)
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_sidebar.py`

- [ ] Replace the 4-patch nested stack (UILabel + UIButton ×2 + TriStateFilterWidget) with a `make_ui_widget` factory OR `bypass_init`. If a factory needs creating, add it to `tests/fixtures/ui_widget_factory.py:254-328` rather than per-file.
- [ ] Verify: tests pass.

### Task 2.6: test_race_browser_dialog.py — 12 bypass-init tests
**Source:** PROJ-479 Task 3.23
**File:** `tests/unit/ui/test_race_browser_dialog.py` (lines 78, 106, 132, 158, 172, 208, 233, 267, 290, 315, 333, 373)
**Tests:** `pytest tests/unit/ui/test_race_browser_dialog.py`

- [ ] Migrate the 12 `patch.object(__init__, no-op) + __new__ + manual attrs` tests to the `bypass_init` fixture. Pattern already in use per PROJ-327.
- [ ] Verify: 12 migrated tests pass.

### Task 2.7: test_race_summary_panel.py — __new__ + 12 private attrs
**Source:** PROJ-479 Task 3.25
**File:** `tests/unit/ui/test_race_summary_panel.py` (lines 391-411)
**Tests:** `pytest tests/unit/ui/test_race_summary_panel.py`

- [ ] Replace `RaceSummaryPanel.__new__()` + 12+ private attr wirings with `bypass_init` OR provide all required pygame_gui fixtures to the real constructor. Pick the lower-risk option for this panel.
- [ ] Verify: tests pass.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3

_Source: PROJ-479 Phase 3 deferred tasks. See [findings/source_review.md](findings/source_review.md)._
