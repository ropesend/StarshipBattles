# Phase 3: CAT-3 Dead Test Code

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-478 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove or skip the 2 verified CAT-3 dead-test-code locations identified by review `2026-05-20_210550_test-review`. Both are leftover scaffolding with zero coverage value — one is an empty test class, the other is a TDD-pending guard whose helper still triggers AttributeError on 4 active tests.

---

## Tasks

### Task 3.1: test_race_summary_panel.py — empty TestCallbackIntegration class
**File:** `tests/unit/ui/test_race_summary_panel.py`
**Tests:** `pytest tests/unit/ui/test_race_summary_panel.py`

- [x] Delete the `TestCallbackIntegration` class (lines 321-323) — contains only a docstring, zero test methods. Pytest collects 0 tests from this class.
- [x] Verify: `pytest tests/unit/ui/test_race_summary_panel.py` passes; LOC delta ≈ -3.

### Task 3.2: test_build_queue_screen_lifecycle.py — TDD-pending invalidate_widget_caches guard
**File:** `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen_lifecycle.py -k "issue17"`

- [x] Add `@pytest.mark.skip(reason="PROJ-410 Phase 2 pending — invalidate_widget_caches helper not yet implemented")` to the 4 affected tests:
  - `test_issue17_on_active_player_changed_triggers_flush` (calls `_spy_invalidate` helper)
  - 2 other tests that call `_spy_invalidate` (per verification report)
  - `test_issue17_show_reasserts_row_visibility_after_panel_show` (direct call at line 1534)
- [x] _(verification note: the helper `_spy_invalidate` at lines 956-970 asserts `hasattr(..., 'invalidate_widget_caches')`. Until PROJ-410 Phase 2 ships the helper, these tests will raise. Skipping preserves the TDD guard intent.)_
- [x] Verify: `pytest tests/unit/ui/screens/test_build_queue_screen_lifecycle.py` passes with 4 skipped; LOC delta ≈ +8 (skip decorators only).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to indicate PROJ-478 complete

_Source review: `Reviews/results/2026-05-20_210550_test-review/`. See [findings/source_review.md](findings/source_review.md) for the link._

---

## Phase 3 Notes (executed 2026-05-22)

**Disposition summary:**

- **Deleted (Task 3.1):** `TestCallbackIntegration` empty class at `tests/unit/ui/test_race_summary_panel.py:321-322`. The class contained only a docstring, zero test methods. Removed both the class and its decorative `Test: Callback Integration` heading banner.

- **Scope decision (Task 3.2):** **DID NOT add `@pytest.mark.skip` decorators** to the 4 build-queue lifecycle tests. The verification report's premise — that the `_spy_invalidate` helper at lines 956-970 would `assert hasattr(..., 'invalidate_widget_caches')` and fail pending PROJ-410 Phase 2 — is now stale. Spot-check on 2026-05-22:
  - `VirtualTable.invalidate_widget_caches` exists in production at `game/ui/components/table/virtual_table.py`.
  - `pytest tests/unit/ui/screens/test_build_queue_screen_lifecycle.py -k "PROJ410 or issue17"` shows **all 9 tests passing**, including the 3 PROJ410 tests that consume `_spy_invalidate` (`test_PROJ410_task_1_2_yard_switch_invalidates_widget_caches`, `test_PROJ410_task_1_3_close_and_reopen_invalidates_cache`, `test_PROJ410_task_1_5_ship_yard_to_planetary_yard_invalidates`) and the issue17 test at line 1483 (`test_issue17_show_reasserts_row_visibility_after_panel_show`).

  Per the project's explicit guardrail ("if you discover a test that LOOKS like CAT-1/2/3 but actually catches a real bug or invariant, STOP and surface"), these tests are now active behavioral guards rather than TDD-pending scaffolding. Skipping them would *remove* coverage. The PROJ-410 Phase 2 dependency the original verification report flagged has been satisfied between the audit (2026-05-20) and execution (2026-05-22), most likely by the merge `67116932d` referenced in `plan.md`'s Current State.

  **Surfaced to user via this note.** Recommended action: close PROJ-478 Phase 3 Task 3.2 as resolved-upstream rather than re-opening it to apply skips that would silently delete legitimate coverage.
