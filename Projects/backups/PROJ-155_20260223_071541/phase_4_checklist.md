# Phase 4: Partial Cleanups Within Files

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-155 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (PROJ-154 + PROJ-157)
**Objective:** Remove dead code segments from files that have both good and bad content.
**Priority:** Normal

---

## PROJ-154 / PROJ-157 Overlap Summary

PROJ-157 Phase 3 completed most partial cleanups. Tasks 4.1, 4.2, 4.3, 4.5, 4.6, 4.8, 4.10 are done.
PROJ-154 completed Task 4.4 (removed TestGameSwitchScene from test_scene_protocol.py).
Tasks 4.7 and 4.9 are N/A (files don't exist — already deleted before either project).
Task 4.11 was investigated — the TestLayoutConstants classes found are legitimate, not trivial.

**All Phase 4 work is complete.**

---

## Tasks

### Task 4.1: Remove TestAllowedLayersRemoval [Simple] — DONE by PROJ-157

- [x] Removed `TestAllowedLayersRemoval` class — PROJ-157
- [x] Kept `TestBuilderDropValidation` class — PROJ-157

### Task 4.2: Remove empty stubs from test_bulk_add.py [Simple] — DONE by PROJ-157

- [x] Removed `test_bulk_add_with_limit` method — PROJ-157
- [x] Removed `test_bulk_performance_mock` method — PROJ-157

### Task 4.3: Remove empty TestShipExpectedStats [Simple] — DONE by PROJ-157

- [x] Removed `class TestShipExpectedStats` — PROJ-157

### Task 4.4: Remove TestGameSwitchScene [Simple] — DONE by PROJ-154

- [x] Removed `TestGameSwitchScene` class (~40 lines) — PROJ-154
- [x] Kept `TestISceneProtocolCompliance` and `TestSceneCallback` — PROJ-154
- [x] Tests verified — PROJ-154

### Task 4.5: Remove trivial tests from test_config.py [Medium] — DONE by PROJ-157

- [x] Removed pure `assert X > 0` positivity checks (~18 tests) — PROJ-157
- [x] Kept relationship and validation tests — PROJ-157

### Task 4.6: Remove duplicate tests from test_battle_screen_edge_cases.py [Medium] — DONE by PROJ-157

- [x] Removed 19 duplicate/trivial tests — PROJ-157
- [x] Kept 6 unique edge case tests — PROJ-157
- [x] File reduced to 142 lines — PROJ-157

### Task 4.7: Remove mock-property tests from test_strategy_detail_formatter.py [Simple] — N/A

- [x] File does not exist. Already deleted before PROJ-155/157.

### Task 4.8: Remove trivial tests from test_colors.py [Simple] — DONE by PROJ-157

- [x] Removed `TestBasicColors` and `TestFontConstants` classes — PROJ-157
- [x] Kept `TestColorsValidation` and `TestColorAccessibility` — PROJ-157

### Task 4.9: Remove test_legacy_cleanup [Simple] — N/A

- [x] File `tests/unit/strategy/test_production_refactor.py` does not exist. Already deleted before PROJ-155/157.

### Task 4.10: Remove duplicate classes from tech tree test_validation.py [Medium] — DONE by PROJ-157

- [x] Removed `TestDetectCycles` and `TestDepthCalculation` classes — PROJ-157
- [x] Kept `TestValidateRequirements`, `TestValidate`, `TestEdgeCases` — PROJ-157

### Task 4.11: Remove layout constants tests [Simple] — DROPPED

- [x] DROPPED: `TestLayoutConstants` classes found in 2 files are legitimate layout constant validation tests (sidebar width, column spacing, etc.), not trivial `assert X > 0` checks. — Verified during PROJ-155 code review

---

## Remaining Work Summary

No remaining work. All tasks complete, dropped, or N/A.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/ -n 12 -q` — verified by PROJ-154
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5
