# Phase 3: CAT-3 Dead Test Code

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-478 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove or skip the 2 verified CAT-3 dead-test-code locations identified by review `2026-05-20_210550_test-review`. Both are leftover scaffolding with zero coverage value — one is an empty test class, the other is a TDD-pending guard whose helper still triggers AttributeError on 4 active tests.

---

## Tasks

### Task 3.1: test_race_summary_panel.py — empty TestCallbackIntegration class
**File:** `tests/unit/ui/test_race_summary_panel.py`
**Tests:** `pytest tests/unit/ui/test_race_summary_panel.py`

- [ ] Delete the `TestCallbackIntegration` class (lines 321-323) — contains only a docstring, zero test methods. Pytest collects 0 tests from this class.
- [ ] Verify: `pytest tests/unit/ui/test_race_summary_panel.py` passes; LOC delta ≈ -3.

### Task 3.2: test_build_queue_screen_lifecycle.py — TDD-pending invalidate_widget_caches guard
**File:** `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen_lifecycle.py -k "issue17"`

- [ ] Add `@pytest.mark.skip(reason="PROJ-410 Phase 2 pending — invalidate_widget_caches helper not yet implemented")` to the 4 affected tests:
  - `test_issue17_on_active_player_changed_triggers_flush` (calls `_spy_invalidate` helper)
  - 2 other tests that call `_spy_invalidate` (per verification report)
  - `test_issue17_show_reasserts_row_visibility_after_panel_show` (direct call at line 1534)
- [ ] _(verification note: the helper `_spy_invalidate` at lines 877-891 asserts `hasattr(..., 'invalidate_widget_caches')`. Until PROJ-410 Phase 2 ships the helper, these tests will raise. Skipping preserves the TDD guard intent.)_
- [ ] Verify: `pytest tests/unit/ui/screens/test_build_queue_screen_lifecycle.py` passes with 4 skipped; LOC delta ≈ +8 (skip decorators only).

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate PROJ-478 complete

_Source review: `Reviews/results/2026-05-20_210550_test-review/`. See [findings/source_review.md](findings/source_review.md) for the link._
