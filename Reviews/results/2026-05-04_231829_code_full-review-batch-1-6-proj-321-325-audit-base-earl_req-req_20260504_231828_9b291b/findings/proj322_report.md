# PROJ-322 Deferred Items Disposition Audit

**Review date:** 2026-05-04
**Source:** PROJ-322 plan.md Final disposition summary + all 6 phase checklists + production code verification
**Objective:** Verify that the 25 deferral dispositions are accurate — that RESOLVED items are genuinely resolved in production code and that ACCEPTED-DEFERRED / RE-CONFIRMED DEFERRED items are appropriately classified (not bugs that should have been fixed).

## Executive Summary

**Result: CLEAN with 1 misclassification.** All 5 spot-checked disposition claims verified correct via production code inspection. One task (3.14) is included in a resolution row whose closure mechanism does not describe how that task was actually resolved. The disposition itself (RESOLVED) is correct.

## Spot-Check Verification Results

| Spot-Check | Claimed Disposition | Verified | Evidence |
|---|---|---|---|
| APC-001 UIWindow cluster (5.6/5.7/5.11/5.12/5.29) | RESOLVED | PASS | `strategy_modal_window.py:118-131` bypass_init guard; `fleet_report_window.py:191-206` two-stage + ui_builder seam; `race_setup/screen.py:151-163` two-stage + delegate factory; `new_game_setup_screen.py:177-191` bypass_init + MockBuilder; `build_queue_list_window.py:157-182` two-stage + row collector + ui_builder; `orders_window.py:65-80` OrderDescriber + OrdersUiBuilder; `transfer_dialog.py:123-159` TransferViewModel + two-stage |
| Task 3.25 (strategy_screen) | RESOLVED by PROJ-327 | PASS | `strategy_screen_composition.py:47-114` — `StrategyScreenComposition` Protocol + `StrategyScreenCompositionFactory`; `strategy_screen.py:53-138` accepts `composition` kwarg; `tests/fixtures/strategy_screen_composition.py` exists |
| Task 4.3 (LLM polling) | RESOLVED by PROJ-324 | PASS | `background.py:104` `_done_event: threading.Event`; `background.py:197-210` `wait(timeout)` public method; `test_background.py` uses `call.wait(timeout=2.0)` (8 occurrences, zero `time.sleep` polling loops) |
| Task 5.10 (workshop_screen) | ACCEPTED-DEFERRED | PASS | `DesignWorkshopScreen` (line 50 of `workshop_screen.py`) is a bare class — no UIWindow inheritance. The two-stage construction recipe does not apply. Test file `tests/unit/ui/screens/test_workshop_screen.py` still exists; Phase 5 checklist sub-items remain `[ ]`. Correct disposition. |
| Tasks 6.1/6.4 (DUP-001/HLP-001) | RE-CONFIRMED DEFERRED | PASS | Measurement evidence documented in PROJ-327 Phase 3 findings supports the re-confirmation: combined file runtime ~1.73s, per-test fixture setup negligible, `make_mock_ship` at ~627 µs/call accounts for only ~3.6% of file runtime. Deferral rationale (readability cost > LOC win) holds. |

## Findings

### FND-001: Task 3.14 misclassified in "13 UIWindow / LLM-blocked deferrals" resolution row

**Severity:** MAJOR
**File:** `Projects/active_projects/PROJ-322/plan.md`
**Line:** 50
**Description:** The Final disposition summary row "13 UIWindow / LLM-blocked deferrals" includes Task 3.14 (`test_virtual_table.py` module-scope autouse fixture migration), but this task was:

1. **Not UIWindow-blocked.** Its original PROJ-322 deferral rationale was "high regression risk across 700 LOC" — a general risk assessment, not a UIWindow super-init chain blocker. It does not involve bypass_init, UIWindow subclasses, or any class inheriting from `StrategyModalWindow`.
2. **Not resolved via the listed closure mechanism.** The row claims resolution via "PROJ-324 Phases 1+2 production foundation (`bypass_init` guard + `LLMBackgroundCall.wait()`) → PROJ-325 Phase 3 PoC → PROJ-328 A/B/C." Task 3.14 was actually resolved by **PROJ-327 Phase 1** (commit 742c67910) using a completely different technique: collapsing 80 `@patch` decorators into a module-scoped autouse fixture, with outcome parity verified via pre/post `pytest -v` diff-checking.

The other 12 items in the row (3.19, 3.20, 3.21, 3.24, 3.26, 4.3, 5.6, 5.7, 5.11, 5.12, 5.16, 5.29) are correctly attributed — all were UIWindow-blocked and resolved via the bypass_init + two-stage construction pattern by PROJ-324/325/328. Only Task 3.14 is misattributed.

**Recommendation:** Either (a) split Task 3.14 into its own row resolved by PROJ-327 Phase 1, reducing the count from 13 to 12; or (b) add "PROJ-327 Phase 1 (virtual_table module-scope fixture)" to the closure cascade for that row.

### FND-002: Task 5.29 verify checkbox stale after resolution

**Severity:** MINOR
**File:** `Projects/active_projects/PROJ-322/phase_5_checklist.md`
**Line:** 314
**Description:** Task 5.29's main action checkbox `[x]` correctly records RESOLVED status, but the Verify sub-item at line 314 reads `[ ] Verify: pytest tests/unit/ui/screens/test_build_queue_list_window.py passes; LOC delta approximately -5 _(deferred-out-of-scope — see above.)_`. The "(deferred-out-of-scope)" annotation is stale — it was written during the original PROJ-322 pass 3 deferral and was never updated after PROJ-328 Phase A resolved the task. The production code refactoring (`BuildQueueRowCollector` + `BuildQueueListUiBuilder`, `build_queue_list_window.py:43-182`) and test migration (`test_build_queue_list_window.py:27-40` uses `bypass_init` + `MockBuildQueueListUiBuilder`) are complete. No `patch.object(BuildQueueListWindow, '_build_list')` remains in the test file.

**Recommendation:** Mark the Verify sub-item `[x]` and replace the stale "(deferred-out-of-scope)" note with a reference to PROJ-328 Phase A Task A.2.

## Additional Notes

- **Both systemic blockers confirmed RESOLVED** in `docs/known-issues.md` (lines 8, 44): UIWindow super-init chain and LLMBackgroundCall polling are marked `[RESOLVED in PROJ-324 + PROJ-325 PoC + PROJ-328]` with full resolution narratives.
- **PROJ-326 linter** exists and is complete (all 3 phases Complete per `plan.md:16-18`).
- **All builder fixtures** matching the claimed resolution files exist: `tests/fixtures/{build_queue_list_ui_builder, fleet_report_ui_builder, orders_ui_builder, transfer_ui_builder, new_game_setup_ui_builder, race_setup_ui_builders}.py`.
- **StrategyScreenComposition pattern** is documented at `docs/02_PATTERNS.md` §32 and the `bypass_init` retrofit pattern at §33.
- **Task 2.11 + 2.19 fixture rescope** (RESOLVED row) verified: both rescoped to module scope after PROJ-327 Phase 2 audit confirmed zero attribute writes.
- **Task 2.15 split from 2.11/2.19** (RE-CONFIRMED DEFERRED row) is correct: `make_mock_ship` is a plain function, not a pytest fixture, so fixture-rescope strategies don't apply.
- **Task 5.10 exclusion from UIWindow row** is correct: `DesignWorkshopScreen` does not inherit from `UIWindow` or `StrategyModalWindow`; the bypass_init pattern genuinely does not apply.
- Zero CRITICAL findings (no deferral was actually a bug; no RESOLVED claim is false).
