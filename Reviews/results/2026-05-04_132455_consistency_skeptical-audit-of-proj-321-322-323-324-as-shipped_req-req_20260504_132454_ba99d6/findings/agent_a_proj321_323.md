# Agent A: PROJ-321 & PROJ-323 Consistency Audit Findings

**Reviewer:** OpenCode (agent_a)
**Date:** 2026-05-04

---

## FOCUS AREA 1: PROJ-321 — Were deletions over-aggressive?

### FND-A01 (CRIT) — SystemTreePanel production code has zero test coverage after 664 LOC unit test deletion

**File:** `game/ui/panels/system_tree_panel.py` (32,417 bytes) — production code still exists
**Evidence:** Searched `tests/integration/` for `SystemTreePanel` — zero matches. Searched all `tests/` for any file referencing `SystemTreePanel` — zero matches. The 664 LOC unit test file `tests/unit/ui/panels/test_system_tree_panel.py` is confirmed GONE from disk. The production code at `game/ui/panels/system_tree_panel.py` has zero pytest coverage.
**Prior review alignment:** The PROJ-321 review correctly flagged MAJ-001: "test_system_tree_panel.py deleted as CAT-2 rather than deferred as APC-001 cluster member." The concern is now confirmed critical — there is NO replacement coverage.
**Recommendation:** Add integration tests for SystemTreePanel in `tests/integration/ui/`.

---

### FND-A02 (MAJ) — Prior review falsified: test_strategy_session_facade_public_api.py claimed as whole-file deletion but file EXISTS

**File:** `tests/unit/strategy/facade/test_strategy_session_facade_public_api.py` (77 LOC, EXISTS on disk)
**Evidence:** The PROJ-321 review (report.md 1.1) listed this file as a 112 LOC whole-file deletion under Phase 1. It still appears in the PROJ-321 manifest as `CAT-1: 1 trivial-pass item(s)`. Verified on disk: file EXISTS at 77 LOC. `git show 148170d2f` reveals the PROJ-321 commit deleted 112 lines (old trivial tests) but the file was NOT fully deleted — 77 LOC of PROJ-309 contract test content remained (or was re-created). The current content is a PROJ-309 sub-phase 3.7 contract guard for `StrategySessionFacade` public surface — this is STRONGER coverage than the original trivial-pass test. MIN-002's concern about "missing contract guard" is moot because the contract guard IS the file's purpose.
**Recommendation:** Update PROJ-321 review report to correct the false claim. The file was a surgical deletion, not a whole-file deletion.

---

### FND-A03 (INFO) — test_bug_12_energy_gen.py relocation verified

**File:** `tests/repro_issues/test_bug_12_energy_gen.py` → `tests/regression/test_generator_crew_requirement_design.py`
**Evidence:** Original path GONE from disk. New path EXISTS at 110 LOC. The relocated file documents WORKING-AS-DESIGNED behavior as a design-intent regression guard.
**Recommendation:** None — relocation confirmed correct.

---

### FND-A04 (INFO) — test_event_log_window.py 6 item surgical deletions verified

**File:** `tests/unit/ui/screens/test_event_log_window.py` (694 LOC, EXISTS on disk)
**Evidence:** File contains real behavioral tests with `_make_event`, `_sample_events`, and `_make_window` helpers. The 6 deleted items (S06-CAT1-003 through S06-CAT1-008: module_exists, sidebar_attr_exists, sidebar_panel_attr_defined, update_method_exists, constant/hasattr tests, facade hasattr tests) were trivial hasattr/constant probes — their absence does not reduce behavioral coverage.
**Recommendation:** None — surgical deletions were targeted and correct.

---

### FND-A05 (INFO) — test_app_integration.py 3 item surgical deletions verified

**File:** `tests/integration/test_app_integration.py` (184 LOC, EXISTS on disk)
**Evidence:** File contains `TestAppNewGameFlow` with `test_on_new_game_start_creates_session_and_save` that imports real `GameConfig`, `GameSession`, `SaveGameService`. The 3 deleted items (S04-CAT1-002, S04-CAT2-004, S04-CAT2-005) were trivial lazy-creation path tests and helper-call pattern checks — their absence does not reduce behavioral coverage.
**Recommendation:** None — surgical deletions were targeted and correct.

---

### FND-A06 (MAJ) — PROJ-321 manifest vs. prior review whole-file deletion count mismatch

**Evidence:** The PROJ-321 manifest lists 63 test files. 14 files are GONE from disk (including `test_build_queue_screen.py` deleted by downstream PROJ-322). The prior review's table listed 13 whole-file deletions with `test_strategy_session_facade_public_api.py` incorrectly included (see FND-A02). The actual whole-file deletion count is 12 (PROJ-321) + 1 (PROJ-322 for test_build_queue_screen.py) = 13 total, but `test_strategy_session_facade_public_api.py` should NOT be counted — it was a surgical deletion. 49 manifest files still exist on disk (surgical deletion targets). All 14 GONE files were verified individually.
**Recommendation:** Correct the PROJ-321 review table: remove `test_strategy_session_facade_public_api.py` from the whole-file deletion list; note it as a surgical deletion.

---

## FOCUS AREA 2: PROJ-323 — CRIT-001 fix + false-positive checkmarks

### FND-B01 (MAJ) — Tasks 3.3 and 3.6: [x] checkmarks annotated but remain checked (CRIT-001 partial fix)

**File:** `Projects/active_projects/PROJ-323/phase_3_checklist.md`
**Evidence:** Both tasks (S11-CAT10-004/005 and S11-CAT10-006/007) have notes added by PROJ-325 Phase 1 Task 1.1 documenting that the target files were deleted by upstream PROJ-321 and the LOC deltas are fictitious. However, the `[x]` checkmarks remain on both the task sub-items and the verify lines. The prior PROJ-323 review's CRIT-001 (FND-CC-001) was only partially addressed: the EXPLANATORY notes were added but the `[x]` markings that falsely claim completion were NOT changed to `[~]` or otherwise unmarked.
**Recommendation:** Change the `[x]` checkmarks on Tasks 3.3 and 3.6 to `[s]` (skipped) or `[~]` (obsoleted) to visually indicate no work was done, consistent with the annotation text.

---

### FND-B02 (MAJ) — 7 Phase 5 tasks reference GONE files with [x] + "skipped" annotation

**Evidence:** Phase 5 checklist (`phase_5_checklist.md`) references 26 files. 7 are GONE from disk: `test_mass_validation.py`, `test_persistence.py`, `test_full_roundtrip.py`, `test_happiness_engine.py`, `test_save_game_service.py`, `test_warp_logic_rework.py`, `test_build_queue_portraits.py`. All 7 carry `[x]` + "(skipped — upstream project already deleted target file)" annotations. None of these 7 appear in the PROJ-323 manifest (cleaned by PROJ-325 Phase 1 Task 1.4). The pattern is consistent with the rest of the project: `[x]` + skip annotation = work obsoleted. This is NOT a finding against the checklist itself but against the convention: `[x]` implies "completed" but obsoleted tasks were never executed.
**Recommendation:** Adopt a distinct checkbox marker (e.g., `[s]` for skipped, `[o]` for obsoleted) in future project checklists so that obsoleted-by-upstream tasks are visually distinguishable from genuinely completed tasks.

---

### FND-B03 (INFO) — PROJ-323 manifest cleanup verified: 0 stale entries (FND-CC-004 fixed)

**Evidence:** All 96 file entries in `Projects/active_projects/PROJ-323/manifest.md` were verified against disk. 96 EXIST, 0 GONE. The manifest header documents "41 entries removed during PROJ-325 Phase 1 Task 1.4 cleanup." FND-CC-004 from the prior PROJ-323 review is confirmed addressed.
**Recommendation:** None — manifest is accurate.

---

### FND-B04 (INFO) — Task 3.10 "deferred" annotation removed (FND-CC-005 fixed)

**Evidence:** Task 3.10 (`test_defense_marker_bindings.py`) notes field states: "PROJ-325 Phase 1 Task 1.2: removed misplaced 'deferred' annotation per OpenCode 323-review FND-CC-005. Task 3.10 is genuinely landed." The file EXISTS and the `@pytest.mark.parametrize` collapsing 6 ability cases is present. FND-CC-005 is confirmed addressed.
**Recommendation:** None.

---

### FND-B05 (INFO) — Task 3.34 fleet_not_found parametrization resolved (PROJ-325 Phase 2)

**File:** `tests/unit/strategy/test_command_handlers.py`
**Evidence:** Commit `02c54631c` (PROJ-325 Phase 2 Task 2.1) added two-group parametrization at lines 1808–1893 of the file:
- `_fleet_id_handler_cases()` returns 9 (handler_cls, cmd_kwargs) tuples for fleet_id-based handlers
- `_construction_queue_entity_id_handler_cases()` returns 2 tuples for entity_id construction-queue handlers
- `test_fleet_id_handler_returns_failure_when_fleet_not_found` parametrizes Group A (9 cases)
- `test_construction_queue_handler_returns_failure_when_fleet_not_found` parametrizes Group B (2 cases)
The prior PROJ-323 review recommended parametrizing 11 handlers as the highest-value continuation item — this is now done. Net LOC delta: +9 (case factories consumed most deduplication savings, but duplication-elimination benefit is real).
**Recommendation:** None — Task 3.34 resolved.

---

### FND-B06 (MAJ) — Task 2.12 file gone from disk but task marked [x] as no-op instead of skipped

**File:** `tests/unit/simulation/services/test_ship_stats_calculator_phases.py` — GONE from disk
**Evidence:** This file is referenced in Task 2.12 of `phase_2_checklist.md` with `[x]` and "(no-op — same M-06 rationale...)" annotation. The file does NOT appear in the PROJ-323 manifest (removed during cleanup). Unlike other deleted-file tasks which carry "(skipped — upstream project already deleted target file)", this task carries "no-op" implying the work was evaluated and consciously not done. However, the file is GONE — git has no history for it in the current branch. The task was marked no-op when the file existed; the file was subsequently deleted by an upstream project. The checklist was never updated to reflect this.
**Recommendation:** Update Task 2.12 annotation to "(skipped — upstream project already deleted target file)" to match the actual state, or add a note documenting the file's deletion timeline.

---

### FND-B07 (MIN) — Tasks 3.27 and 3.32: "deferred" in Verify line conflicts with [x] task checkbox

**File:** `Projects/active_projects/PROJ-323/phase_3_checklist.md` lines 342–344 and 402–404
**Evidence:** Task 3.27: checkbox `[x]` on `Leave as-is` directive (correct decision made), but Verify line says "LOC delta ≈ 16 _(deferred — see task notes above)_". Task 3.32: same pattern — `[x]` on `left as-is` but Verify line says "(deferred)". In both cases, the work was NOT deferred — a deliberate decision was made to leave the code as-is (below 3-member parametrize threshold; or distinct validation paths). The word "deferred" in the Verify line contradicts the task body and the checkbox.
**Recommendation:** Replace "deferred" in Tasks 3.27/3.32 Verify lines with "left as-is per directive" to match the task body. The [x] checkmarks are correct — decisions were made, not postponed.

---

### FND-B08 (MIN) — Cross-phase false-positive [x] pattern is consistent but semantically misleading

**Evidence:** Across all 5 phase checklists, approximately 35+ tasks carry `[x]` + "(skipped — upstream project already deleted target file)" annotations. The `[x]` convention is used project-wide for both "work completed" and "work obsoleted by upstream deletion." The manifest was cleaned (FND-B03) but the checklists retain obsoleted entries with `[x]`. The Phase Completion Checklists at the bottom of each file claim "All task checkboxes above are checked" — which is technically true but misleading since ~20% of those checkboxes represent work that was never done.
**Recommendation:** Add a project-level note in plan.md documenting the `[x]` + "skipped" convention. Future projects should use distinct markers for genuinely completed vs. obsoleted-by-upstream tasks.

---

## Summary

| ID | Severity | Category | Title |
|----|----------|----------|-------|
| FND-A01 | CRIT | Coverage gap | SystemTreePanel has zero test coverage after 664 LOC unit test deletion |
| FND-A02 | MAJ | False claim | test_strategy_session_facade_public_api.py claimed whole-file deleted but EXISTS |
| FND-A06 | MAJ | Counting error | Prior review miscounted whole-file deletions (12 not 13) |
| FND-B01 | MAJ | Partial fix | Tasks 3.3/3.6: [x] not unmarked even after annotation (CRIT-001 partial) |
| FND-B02 | MAJ | Convention | 7 Phase 5 tasks carry [x] + "skipped" for GONE files |
| FND-B06 | MAJ | Stale annotation | Task 2.12: file GONE but annotated "no-op" instead of "skipped" |
| FND-B07 | MIN | Terminology | Tasks 3.27/3.32: "deferred" in Verify line contradicts leave-as-is body |
| FND-B08 | MIN | Convention | ~35 [x]+skipped checkmarks across all phases are semantically misleading |
| FND-A03 | INFO | Verified | test_bug_12_energy_gen.py relocation to regression/ confirmed |
| FND-A04 | INFO | Verified | test_event_log_window.py 6 surgical deletions correct |
| FND-A05 | INFO | Verified | test_app_integration.py 3 surgical deletions correct |
| FND-B03 | INFO | Verified | PROJ-323 manifest: 96/96 entries exist (FND-CC-004 fixed) |
| FND-B04 | INFO | Verified | Task 3.10 deferred annotation removed (FND-CC-005 fixed) |
| FND-B05 | INFO | Verified | Task 3.34 fleet_not_found parametrized (PROJ-325 Phase 2) |
