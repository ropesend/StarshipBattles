# Skeptical Audit of PROJ-321/322/323/324 — Report

**Review Type:** consistency (skeptical audit)
**Request ID:** req_20260504_132454_ba99d6
**Completed:** 2026-05-04T14:30:00Z
**Reviewer:** OpenCode (ocode-review-request)
**Review Mode:** full
**Scope:** PROJ-321, PROJ-322, PROJ-323, PROJ-324 as-shipped state (post-continuation)

## Prior Reviews Considered
- PROJ-321: `Reviews/results/2026-05-04_015902_*proj-321*/report.md`
- PROJ-322: `Reviews/results/2026-05-04_015938_*proj-322*/report.md`
- PROJ-323: `Reviews/results/2026-05-04_020005_*proj-323*/report.md`

---

## Executive Summary

The 4 projects accomplished real work but the "ALL COMPLETE" claims have genuine gaps:

1. **PROJ-321:** One 664 LOC deletion (SystemTreePanel tests) left production code with **zero test coverage**. A prior review re-finding (test_strategy_session_facade_public_api.py "whole file deleted") was falsified — the file exists as a contract guard.

2. **PROJ-322 deferrals:** The Continuation Guide's claim that "ALL 25 deferrals are now dispositioned" is **mostly true but has two genuine gaps**: (a) Task 5.10 (workshop_screen) is still `[ ]` unchecked with no resolution project assigned; (b) Task 2.15 was subsumed under HLP-001 (RE-CONFIRMED DEFERRED) but the Final summary Row 3 labels it RESOLVED. Two additional deferrals (2.8, 2.9) have no explicit Final disposition row.

3. **PROJ-323:** CRIT-001 (false-positive `[x]` checkmarks on deleted files) was only **partially fixed** — the `[x]` markings remain even after annotations were added. The prior review's findings were otherwise addressed.

4. **PROJ-324:** The bypass_init guards are correctly placed on all 7 production classes. One **verified bug** exists in LLMBackgroundCall: an unexpected exception in `_provider.complete()` sets `_done_event` but leaves `_status=RUNNING`, violating the `wait()` contract. Documentation has internal contradictions and tally errors.

---

## CRITICAL (3)

### CRIT-001 — SystemTreePanel production code has zero test coverage after 664 LOC unit test deletion

**File:** `game/ui/panels/system_tree_panel.py` (32,417 bytes)
**Severity:** CRITICAL
**Agent:** A (FND-A01)

**Evidence:** Production file `game/ui/panels/system_tree_panel.py` exists (32KB). `tests/unit/ui/panels/test_system_tree_panel.py` (664 LOC) was deleted by PROJ-321 Phase 2 as CAT-2. A search of all `tests/` found **zero references** to `SystemTreePanel` — no integration tests, no unit tests, no smoke tests cover this production code. The prior PROJ-321 review flagged MAJ-001 about this; the concern is now confirmed critical.

**Recommendation:** Create integration tests for SystemTreePanel at `tests/integration/ui/` with minimum coverage of initialization, tree building, expand/collapse, and selection change.

---

### CRIT-002 — Task 5.10 (workshop_screen) is genuinely unresolved; included among "RESOLVED" 14 deferrals

**File:** `Projects/active_projects/PROJ-322/phase_5_checklist.md:122-125`
**Severity:** CRITICAL
**Agent:** B (FND-B01)

**Evidence:** Task 5.10 has 3 sub-tasks (5.10a, 5.10b, 5.10c) all `[ ]` unchecked with annotation "deferred." PROJ-328 explicitly out-scoped WorkshopScreen: "separate 'all UI consistency' project later." The Final disposition summary Row 1 counts 14 UIWindow/LLM deferrals as RESOLVED — but only 13 of 14 have on-disk resolution evidence. Task 5.10 is an orphan deferral with no resolution project assigned and no integration tests to replace the unit tests.

**Recommendation:** Either (a) open a new PROJ for workshop_screen testable construction, (b) mark Task 5.10 as ACCEPTED-DEFERRED with rationale, or (c) verify whether `tests/integration/ui/workshop_screen/` has integration coverage (the manifest claim is stale per PROJ-324 systemic finding) and, if absent, create integration tests.

---

### CRIT-003 — Task 2.15 marked RESOLVED but was subsumed into a RE-CONFIRMED DEFERRED item

**File:** `Projects/active_projects/PROJ-322/plan.md:52` vs `Projects/active_projects/PROJ-327/findings/phase_2_runtime_delta.md:13`
**Severity:** CRITICAL
**Agent:** B (FND-B02)

**Evidence:** Row 3 of the Final disposition summary says "Tasks 2.11 + 2.19 + 2.15 — RESOLVED." But PROJ-327 Phase 2 explicitly subsumed Task 2.15 under Phase 3 Task 3.2 (HLP-001 re-judgment), which was RE-CONFIRMED DEFERRED. A "subsumed under deferred" is not "resolved." The `phase_2_runtime_delta.md` is honest about this but the Final summary is not.

**Recommendation:** Correct Row 3 to: "Tasks 2.11 + 2.19 → RESOLVED; Task 2.15 → subsumed under HLP-001 (RE-CONFIRMED DEFERRED)."

---

## MAJOR (10)

### MAJ-001 — Prior review falsified: test_strategy_session_facade_public_api.py claimed whole-file deleted but EXISTS

**File:** `tests/unit/strategy/facade/test_strategy_session_facade_public_api.py` (77 LOC)
**Agent:** A (FND-A02)

The PROJ-321 review incorrectly listed this file as a whole-file deletion. It was a surgical deletion — 77 LOC of PROJ-309 contract guard content exists. The prior review's MIN-002 concern about "missing contract guard" is moot.

**Recommendation:** Correct PROJ-321 review table: remove from whole-file deletion list; note as surgical deletion.

---

### MAJ-002 — PROJ-321 manifest vs. prior review whole-file deletion count mismatch

**Agent:** A (FND-A06)

The prior review claimed 13 whole-file deletions. Actual: 12 (PROJ-321) + 1 (PROJ-322 for test_build_queue_screen.py), but test_strategy_session_facade_public_api.py should NOT be counted. Effective count: 12 whole-file deletes.

---

### MAJ-003 — PROJ-323 Tasks 3.3 and 3.6: [x] checkmarks remain despite annotation (CRIT-001 partial fix)

**File:** `Projects/active_projects/PROJ-323/phase_3_checklist.md`
**Agent:** A (FND-B01)

PROJ-325 Phase 1 Task 1.1 added explanatory notes documenting the false-positive but did NOT change the `[x]` markings. The prior review's CRITICAL FND-CC-001 was only partially addressed — the annotations document the problem but the checkmarks still falsely claim completion.

**Recommendation:** Change `[x]` on Tasks 3.3/3.6 to `[s]` (skipped) or `[~]` (obsoleted).

---

### MAJ-004 — 7 PROJ-323 Phase 5 tasks carry [x] + "skipped" for GONE files

**Agent:** A (FND-B02)

Seven files referenced in Phase 5 tasks are GONE from disk (deleted by upstream projects). All carry `[x]` + "(skipped)" annotation. The `[x]` convention is used for both "completed" and "obsoleted-by-upstream" — semantically misleading. A distinct marker should be adopted.

---

### MAJ-005 — PROJ-323 Task 2.12: file GONE but annotated "no-op" instead of "skipped"

**File:** `tests/unit/simulation/services/test_ship_stats_calculator_phases.py` — GONE from disk
**Agent:** A (FND-B06)

File is gone but the task carries "no-op" annotation implying the work was evaluated and consciously not done. The file was deleted by an upstream project; the annotation should say "skipped — upstream project already deleted target file."

---

### MAJ-006 — Task 3.15 RE-CONFIRMED DEFERRED without measurement evidence

**File:** `Projects/active_projects/PROJ-327/findings/phase_2_runtime_delta.md:15`
**Agent:** B (FND-B04)

Row 4 says RE-CONFIRMED DEFERRED "with measurement evidence." For Task 3.15, no measurement was cited — just a re-assertion of the original PROJ-322 deferral rationale. The Phase 2 measurement work applied to fixture-rescope items (2.6, 2.11, 2.19), not this single CAT-6 test. The deferral itself is defensible, but labeling it as measurement-backed is inaccurate.

---

### MAJ-007 — Tasks 2.8 and 2.9 have no explicit Final disposition row

**File:** `Projects/active_projects/PROJ-322/plan.md:47-57`
**Agent:** B (FND-B05)

These Phase 2 deferrals were gated by HLP-001 (Task 6.4). HLP-001 is now RE-CONFIRMED DEFERRED. But 2.8 and 2.9 are NOT mentioned in any of the 7 Final disposition summary rows. Their dependency is closed but their own disposition is implicit.

**Recommendation:** Add Tasks 2.8 + 2.9 to the Final disposition summary as "RE-CONFIRMED DEFERRED — blocked by HLP-001."

---

### MAJ-008 — Task 3.25 LOC outcome contradicts original estimate by 581 LOC

**File:** `Projects/active_projects/PROJ-327/plan.md:27`
**Agent:** B (FND-B06)

Original PROJ-322 estimate: -200 LOC. Actual: +381 LOC across 5 new files. The plan authorizes this tradeoff on readability/maintainability grounds. Not hand-wavy — the work was genuinely done and the pattern is documented — but the delta direction flipped entirely.

---

### MAJ-009 — LLMBackgroundCall: Unexpected exception in _provider.complete() sets _done_event but leaves _status=RUNNING

**File:** `game/services/llm/background.py:240,267`
**Severity:** MAJOR (verified bug)
**Agent:** C (FND-L02)

**Evidence:** If `self._provider.complete(...)` raises a non-LLM exception:
1. `_status` is set to `RUNNING` (line 237)
2. Exception escapes the `try` but the inner `finally` runs `_done_event.set()` (line 267)
3. `_done_event` is set → `wait()` returns `True` → caller checks `status` expecting DONE/ERROR/CANCELLED but gets RUNNING

This violates the `wait()` API contract: "Returns True if a terminal state was reached."

**Recommendation:** In the inner `finally` block, capture any unhandled `Exception` (NOT `BaseException` — let `KeyboardInterrupt`/`SystemExit` propagate), transition `_status` to `ERROR`, store the exception in `self._error`, then set `_done_event`.

---

### MAJ-010 — Pattern doc §33 "MUST be first statement" rule contradicted by its own two-stage example

**File:** `docs/02_PATTERNS.md:1831-1832`
**Agent:** C (FND-C01)

The Migration notes say "The guard MUST be the first executable statement in `__init__`" but the canonical code example in the same section shows ~25 lines of Stage 1 setup (cheap state + delegate construction) running BEFORE the guard — by design. This is an internal contradiction within a single section. The actual on-disk implementations (`RaceSetupScreen`, `NewGameSetupScreen`) correctly follow the two-stage pattern.

**Recommendation:** Reword to: "The guard SHOULD be the first point where `UIWindow.__init__` is avoided. Code above the guard runs in both production and test modes and MUST be pure-Python (no pygame_gui widgets, no `self.get_container()`)."

---

## MINOR (6)

### MIN-001 — PROJ-323 Tasks 3.27/3.32: "deferred" in Verify line contradicts leave-as-is body

**File:** `Projects/active_projects/PROJ-323/phase_3_checklist.md`
**Agent:** A (FND-B07)

The task body says "Leave as-is" (correct decision) but the Verify line says "(deferred)." Replace "deferred" with "left as-is per directive."

---

### MIN-002 — PROJ-323 ~35 [x]+"skipped" checkmarks across all phases are semantically misleading

**Agent:** A (FND-B08)

The `[x]` convention is used for both "work completed" and "work obsoleted by upstream deletion." ~20% of checkboxes represent work never done. Adopt distinct markers in future projects.

---

### MIN-003 — PROJ-322 Task 5.29 verify checkbox is `[ ]` despite being claimed RESOLVED

**File:** `Projects/active_projects/PROJ-322/phase_5_checklist.md:314`
**Agent:** B (FND-B03)

The task body documents the resolution (PROJ-328 A.2, commit 7859d652c) but the verify checkbox was never updated from its stale "(deferred-out-of-scope)" annotation.

---

### MIN-004 — PROJ-322 plan.md tally math doesn't sum from phase totals

**File:** `Projects/active_projects/PROJ-322/plan.md:33`
**Agent:** C (FND-D06)

The Final tally "71 substantive done, 17 obsolete-skipped, 25 deferred" doesn't sum from phase disposition summaries: 67 substantive, 26 obsolete, 24 deferred per phase-level counts. Largest discrepancy in obsolete-skipped column.

---

### MIN-005 — PROJ-324 phase_3_checklist.md marked Complete but all tasks unchecked

**File:** `Projects/active_projects/PROJ-324/phase_3_checklist.md`
**Agent:** C (FND-D07)

Phase status is "Complete" but 8 of 9 tasks have `[ ]` unchecked and empty Notes. The phase was closed as a GO/NO-GO decision (reroute to PROJ-325/328), not as task execution. The status is misleading.

---

### MIN-006 — Pattern doc §33 references systemic finding but doesn't state zero-LOC conclusion

**Agent:** C (FND-D02)

§33 mentions "PROJ-324 systemic finding 2026-05-04" but does not explicitly state the key takeaway: the Phase 1 bypass_init guard alone delivered zero test-side LOC reduction.

---

## INFO (9)

- **INFO-001:** test_bug_12_energy_gen.py relocation to `tests/regression/` confirmed correct (Agent A)
- **INFO-002:** test_event_log_window.py 6 surgical deletions confirmed targeted and correct (Agent A)
- **INFO-003:** test_app_integration.py 3 surgical deletions confirmed correct (Agent A)
- **INFO-004:** PROJ-323 manifest cleanup verified: 96/96 entries exist on disk (Agent A)
- **INFO-005:** PROJ-323 Task 3.10 deferred annotation removed correctly (Agent A)
- **INFO-006:** PROJ-323 Task 3.34 fleet_not_found parametrization resolved by PROJ-325 Phase 2 (Agent A)
- **INFO-007:** LLMBackgroundCall `wait()` before `start()` blocks forever — undocumented (Agent C)
- **INFO-008:** No runtime warning when `make_ui_widget` used on UIWindow subclass without `bypass_init` (Agent C)
- **INFO-009:** `_window_init_bypassed` check pattern (used by 4 subclasses) is undocumented in §33 (Agent C)

---

## Verification Summary: bypass_init Guard Placement

All 7 production classes verified on disk:

| Class | File | Guard Type | Guard Position | Status |
|-------|------|-----------|----------------|--------|
| StrategyModalWindow | `strategy_modal_window.py:118` | Own guard | First executable statement | CORRECT |
| RaceSetupScreen | `race_setup/screen.py:151` | Own guard | After Stage 1 (two-stage) | CORRECT |
| NewGameSetupScreen | `new_game_setup_screen.py:177` | Own guard | After Stage 1 (two-stage) | CORRECT |
| BuildQueueListWindow | `build_queue_list_window.py:165` | Transitive + `_window_init_bypassed` check | Safe | CORRECT |
| FleetReportWindow | `fleet_report_window.py:192` | Transitive + `_window_init_bypassed` check | Safe | CORRECT |
| OrdersWindow | `orders_window.py:340` | Transitive + `_window_init_bypassed` check | Safe | CORRECT |
| TransferDialog | `transfer_dialog.py:147` | Transitive + `_window_init_bypassed` check | Safe | CORRECT |

All guards use `getattr(type(self), 'bypass_init', False)` — correct per design.md Risk #1.

---

## Agent Reports

Detailed findings from 3 specialized audit agents:
- [Agent A: PROJ-321 deletions + PROJ-323 corrections](findings/agent_a_proj321_323.md)
- [Agent B: PROJ-322 deferral disposition verification](findings/agent_b_proj322_deferrals.md)
- [Agent C: PROJ-324 code quality + factory + docs drift](findings/agent_c_proj324_code_docs.md)

---

## Remediation Needed (Priority-Ordered)

### Priority 1 — Must Fix

1. **SystemTreePanel zero coverage** (CRIT-001): Create integration tests. Without coverage, a regression in tree rendering, selection, or collapse/expand behavior could ship undetected.

2. **LLMBackgroundCall unexpected-exception path** (MAJ-009): Fix `_run()` to catch `Exception` (not `BaseException`) in the inner `finally`, transition `_status` to `ERROR`, and store the exception before setting `_done_event`. Current behavior violates the `wait()` contract.

3. **Task 5.10 orphan deferral** (CRIT-002): Either assign a resolution project or officially mark as ACCEPTED-DEFERRED with rationale.

### Priority 2 — Should Fix

4. **PROJ-322 Final disposition summary errors** (CRIT-003, MAJ-007): Correct Row 3 (2.15 is deferred, not resolved), add Rows for 2.8 + 2.9, fix tally math (MAJ-004).

5. **PROJ-323 false-positive [x] checkmarks** (MAJ-003): Unmark Tasks 3.3 and 3.6 per prior review CRIT-001.

6. **Pattern doc §33 contradiction** (MAJ-010): Reword "MUST be first statement" to acknowledge the two-stage pattern.

### Priority 3 — Improve

7. **Prior review factual corrections** (MAJ-001, MAJ-002): Correct the PROJ-321 review's whole-file deletion table.
8. **Checklist convention** (MAJ-004, MAJ-005, MIN-002, MIN-003, MIN-005): Adopt distinct markers for obsoleted-by-upstream vs. genuinely-completed tasks.
9. **Documentation fill-in** (INFO-007, INFO-008, INFO-009): Document `wait()`-before-`start()` behavior, factory UIWindow warning, and `_window_init_bypassed` pattern.

### Priority 4 — Consider

10. **Task 3.15 measurement evidence** (MAJ-006): Either add a measurement note or re-label as "re-audit confirmed (no measurement applicable)."
11. **Task 3.25 LOC disclosure** (MAJ-008): The +381 LOC outcome is acceptable per authorization but should be explicitly noted in the Final summary for audit completeness.
