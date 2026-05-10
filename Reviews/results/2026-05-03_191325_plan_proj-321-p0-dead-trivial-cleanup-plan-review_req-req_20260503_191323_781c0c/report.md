# Plan Review: PROJ-321 P0 Dead-Trivial Cleanup Plan

**Review Type:** plan
**Request ID:** req_20260503_191323_781c0c
**Completed:** 2026-05-03T19:35:00Z

## Summary

The plan correctly partitions 80 P0 items (46 CAT-1, 26 CAT-2, 8 CAT-3) across three phases and all APC-001 boundaries are properly drawn. No rejected or out-of-scope items leaked into checklists. However, **12 file paths in the manifest and checklists are incorrect** — they do not match actual disk locations. Implementation agents will be unable to find 12 of the target files. One checklist task (`test_commands.py`) spans two different files. These path errors propagate from the verification report through the manifest into every checklist.

---

## Findings

### CRITICAL

**CRIT-001: 12 file path mismatches between manifest/checklists and filesystem**

The manifest, all three phase checklists, and the verification report share the same incorrect file paths. Affected files:

| Manifest path (wrong) | Actual path |
|---|---|
| `tests/integration/test_main_integration.py` | `tests/unit/systems/test_main_integration.py` |
| `tests/unit/ai/interfaces/test_controllable_adapter.py` | `tests/unit/ai/test_controllable_adapter.py` |
| `tests/unit/ai/interfaces/test_controllable_adapter_edge_cases.py` | `tests/unit/ai/test_controllable_adapter_edge_cases.py` |
| `tests/unit/qa/test_testruncard_propulsion.py` | `tests/unit/test_lab/test_testruncard_propulsion.py` |
| `tests/unit/simulation/test_simulation_constants.py` | `tests/unit/core/test_simulation_constants.py` |
| `tests/unit/strategy/services/test_intercept_edge_cases.py` | `tests/unit/strategy/pathfinding/test_intercept_edge_cases.py` |
| `tests/unit/strategy/test_ship_stat_querier.py` | `tests/unit/entities/test_ship_stat_querier.py` |
| `tests/unit/ui/panels/test_strategy_menu_panel.py` | `tests/unit/ui/screens/test_strategy_menu_panel.py` |
| `tests/unit/ui/test_app_public_api.py` | `tests/unit/test_app_public_api.py` |
| `tests/unit/ui/test_unified_entry_guard.py` | `tests/unit/simulation/test_unified_entry_guard.py` |
| `tests/unit/ui/utils/test_race_asset_loader.py` | `tests/unit/ui/test_race_asset_loader.py` |
| `tests/unit/strategy/test_commands.py` | Two different files (see CRIT-002) |

**Recommendation:** Update the manifest.md and all three phase_N_checklist.md files with corrected paths before beginning implementation. The verification report should also be corrected, but since it reflects the original review's output, add an errata addendum rather than rewriting it.

---

**CRIT-002: test_commands.py resolves to two different files**

The manifest lists `tests/unit/strategy/test_commands.py` (does not exist) with two items:
- CAT-2 `test_command_name_property` (lines 41-44) → actually at `tests/unit/strategy/engine/test_commands.py`
- CAT-3 `test_handle_command` (lines 191-198) → actually at `tests/integration/strategy/test_commands.py`

These are in different test files in different directories. The checklist treats them as a single file (Tasks 2.10 and 3.7 both point to the same non-existent path). An implementation agent who finds one will not find the other.

**Recommendation:** Split into two separate tasks: Task 2.10 → `tests/unit/strategy/engine/test_commands.py`, Task 3.7 → `tests/integration/strategy/test_commands.py`. Update manifest to list both paths.

---

### MAJOR

**MAJ-001: Task 1.26 (event_log_window.py) has overlapping line ranges from double-counted findings**

The checklist lists "4 constant/hasattr tests (lines 475-478, 488-491, 381-385, 387-390, 24 LOC)" and separately "2 facade hasattr tests (lines 381-390, 10 LOC)." These overlap — lines 381-390 appear in both subtasks. This is a known double-count from the Shard 06 verified report (F07↔F08 overlap). If the implementation agent deletes both line ranges as separate tasks, they will attempt to delete the same tests twice.

**Recommendation:** Merge the overlapping facade hasattr items (lines 381-390) into a single subtask. Remove the separate "2 facade hasattr tests" subtask since lines 381-385 and 387-390 are already covered under "4 constant/hasattr tests."

---

**MAJ-002: Task 2.2 (test_controllable_adapter.py) lacks precise scope for partial deletion**

The action is "Keep ~20 LOC contract checks; delete the two 30-method mock classes." The checklist does not specify which test methods constitute the "~20 LOC contract checks" to keep. The verification report (Shard 11, F-4) identifies `test_cannot_instantiate_icontrollable` (line 16) and `test_all_abstract_methods_present` (line 25) as the legitimate contract checks. The two mock classes at lines 66-213 should be deleted.

**Recommendation:** Add explicit line ranges for the tests to keep (`test_cannot_instantiate_icontrollable`, `test_all_abstract_methods_present`) and the mock classes to delete (`MockControllable` lines 66-172, `FullMockControllable` lines 173-213).

---

**MAJ-003: Task 1.16 (test_intercept_edge_cases.py) path mismatch (also in CRIT-001)**

The checklist instructs "Delete entire file" at `tests/unit/strategy/services/test_intercept_edge_cases.py`. This file does not exist at that path. The actual file is at `tests/unit/strategy/pathfinding/test_intercept_edge_cases.py`. An implementation agent that does not correct the path would fail to complete the task.

**Recommendation:** Fix path per CRIT-001. The deletion decision is correct — the file (27 LOC, 3 import-existence checks only) should be deleted.

---

**MAJ-004: Task 2.23 (test_unified_entry_guard.py) path and scope mismatch**

The manifest says `tests/unit/ui/test_unified_entry_guard.py` but the file is at `tests/unit/simulation/test_unified_entry_guard.py`. The SUMMARY.md top-20 table uses yet a third path: `tests/unit/simulation/battle_setup/test_unified_entry_guard.py`. The action "Move scan-based tests to a CI/lint step; keep only runtime behavioral tests" is correct in intent, but the wrong path means the implementation agent will look in the wrong directory.

**Recommendation:** Correct path to `tests/unit/simulation/test_unified_entry_guard.py`.

---

### MINOR

**MIN-001: Task 1.1 (test_production_progress) has three-way ambiguous action**

The checklist offers "Remove or implement — delete the dead test or add actual assertions; convert to pytest.skip if refactoring still needed." This gives three mutually exclusive options with no priority signal. For a P0 cleanup project, deletion should be the default unless there is evidence the production path lacks coverage.

**Recommendation:** Choose one primary action. Given the verification report says the test body is "all comments" with no assertions, deletion is appropriate. Add a note: "If production path is uncovered, add a real test in a follow-up project, not here."

---

**MIN-002: Task 1.14 (test_strategy_session_facade_public_api.py) conflicts with P0 objective**

The action "Keep as a contract guard but rename and document; consider moving to a lint step" preserves 33 LOC of trivial contract assertions in a project whose stated goal is to delete trivial-pass tests. The S08-CAT1-003 verification calls this "CRITICAL" and suggests "Keep as a contract guard but rename and document." The checklist chose the least-aggressive option.

**Recommendation:** Either commit to deletion (consistent with P0 objective) or move the task to PROJ-322/323. A P0 cleanup that keeps "trivial-pass" tests under a different name undermines the project's purpose.

---

**MIN-003: Task 2.3 (test_test_infrastructure.py) exceeds P0 scope**

The action "Move to a Tools/ linter or pre-commit hook; remove from pytest suite" requires creating new tooling infrastructure. This is not a "trivial cleanup" action — it is a migration that requires designing and implementing a linter. The 8 `test_no_duplicate_*` methods could simply be deleted (no production code tested) or converted to `@pytest.mark.skip`.

**Recommendation:** If the scan is valuable, skip the tests with a reference to the future linter. If not valuable, delete. Do not block P0 completion on building a linter.

---

**MIN-004: Task 3.5 (test_bug_12_energy_gen.py) action is a move, not a delete**

CAT-3 is "Dead Test Code" — the project objective says "Delete the 8 verified CAT-3 dead-test-code files / sections." But Task 3.5 says "Move to tests/regression/ with rename; keep as design-intent regression guard." This is a relocation, not a deletion. The verification report (S08-CAT3-001) explicitly says "Move to tests/regression/ with rename; keep," so the action is consistent with the source, but it sits oddly in a "delete" phase.

**Recommendation:** Either move this task to PROJ-322 (which handles CAT-4..CAT-7 refactors) or explicitly note in the checklist that this is a move (not delete) and update the phase objective.

---

**MIN-005: LOC totals not validated against per-task sums**

The plan.md overview claims ~5,038 LOC reclaimable. The per-task LOC deltas in the checklists should sum to approximately this value, but no cross-check has been performed. Spot-checking: Summing the approximate LOC deltas from the checklist tasks yields roughly 4,800-5,200 — within range, but the imprecision means the impact estimate is unverified.

**Recommendation:** Add a verification step to confirm that the sum of individual task LOC deltas matches the plan's total claim.

---

## Verification Report Sanity (Instruction 4)

**Result: CLEAN.** All 3 rejected items (S08-CAT2-R01, S08-CAT2-R02, S08-CAT2-R03) are absent from the manifest and all checklists. The file `test_controllable_adapter_edge_cases.py` appears in the manifest only under its CAT-3 verified classification (S08-CAT3-002), not the rejected CAT-2 claim. All 3 out-of-scope items (S01-CAT2-OOS01, S01-CAT2-OOS02, S05-CAT2-OOS01) are absent from all checklists.

## APC-001 Boundary (Instruction 3)

**Result: CLEAN.** All 6 APC-001 cluster member tasks (2.13, 2.14, 2.18, 2.21, 2.22) correctly scope to "rewrite" or "migrate" rather than "delete." No whole-file deletes overlap with PROJ-322's APC-001 rewrite scope. Task 2.18 (`test_build_queue_screen.py`) says "Entire file uses bypass-init" but the action is migration to integration tests, not deletion. The boundary is correctly drawn.

## Pytest.skip vs Delete (Instruction 6)

**Result: MOSTLY OK.** The only questionable skip recommendation is Task 1.1 (test_production_progress) flagged as MIN-001. Other skip recommendations are defensible:
- Task 1.5 (visual verification only) — rotation angle requires visual confirmation
- Task 1.3 (narrow to ImportError, skip on other errors) — improves an existing broad-except test rather than leaving it broken

## Manifest Consistency (Instruction 5)

**Result: PASS — with 12 path errors.** Every file in the manifest has a corresponding checklist task, and every checklist task's file is in the manifest. However, 12 files have incorrect paths that make the manifest internally inconsistent with the filesystem. Once paths are corrected (per CRIT-001), consistency holds.

## Action Correctness Spot-Checks (Instruction 1)

Spot-checked against verified shard reports:

- Task 1.15 (`test_layout_scaling.py` → delete entire file): Correct. Shard 06 confirms 22 LOC of import checks only.
- Task 1.7 (`test_import_path` → remove): Correct. `assert DC is DamageContext` — identity check.
- Task 1.10 (5 existence tests → remove): Correct. Shard 06 confirms all 5 cannot fail if imports succeed.
- Task 2.11 (`test_modifier_logic.py` → remove entire file): Correct. Shard 02 confirms 0 game.* imports, production coverage at `test_modifier_logic_service.py:198-218`.
- Task 2.7 (`test_production_rates.py` → rewrite): Correct. Shard 09 F-04 confirms 3 classes reimplement turn-calculation locally. Valid tests in the same file call real production functions.
- Task 3.1 (`test_deprecated_code_removed.py` → remove one test): Correct. Shard 02 confirms the removed module is long-gone.

All spot-checks confirm the proposed actions match the source findings.

## Coverage Loss Risk (Instruction 2)

For tasks proposing full-file or test deletions, verified that independent behavioral coverage exists:

- `test_layout_scaling.py` → zero production logic exercised. No gap.
- `test_intercept_edge_cases.py` → 3 import-existence checks only. No gap.
- `test_modifier_logic.py` → production coverage at `tests/unit/ui/screens/builder/test_modifier_logic_service.py:198-218`. No gap.
- `test_testruncard_propulsion.py` → zero game.* imports. No gap.
- `repro_warp_bug.py` → bugs covered by proper pytest tests elsewhere. No gap.
- 5 existence tests in `test_ai_factory.py` → behavioral tests cover factory methods. No gap.

**No coverage gaps identified.**

---

## Findings Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 2 |
| MAJOR | 4 |
| MINOR | 5 |
| INFO | 0 |

**Bottom line:** The plan is architecturally sound — task partitioning, APC-001 boundaries, verification-report filtering, and coverage-risk analysis are all correct. The one blocking issue is the 12 file-path mismatches (CRIT-001 + CRIT-002), which must be fixed before implementation can proceed. All other findings are advisory refinements.
