# PROJ-384 Implementation Review

**Date:** 2026-05-09
**Reviewer:** Codex
**Project:** PROJ-384 - Legacy removal: PROJ-241 deprecated `*_static` methods

## Verdict

**Code goals appear met, but the project is not audit-ready.**

The implementation deleted the targeted `AbilityManager` and `ModifierManager` deprecated static wrappers, migrated the three direct ability-manager tests to the instance API, and the focused regression passed. However, `validate_audit_ready.py` fails because project-state artifacts still mark Task 1.3 incomplete and report a blocker. This review therefore cannot certify PROJ-384 as passing Protocol 04 audit.

## Validation Result

Command: `python Projects/scripts/validate_audit_ready.py PROJ-384`

**Result:** FAILED

- Phase completion check failed: Phase 1 > Task 1.3 has 1 unchecked item.
- Task completion check failed: Task 1.3 has an incomplete subtask.
- Blocker check failed: `plan.md` still reports `Pre-existing unresolved merge in working tree blocks git commit`.
- Warning: `Projects/projects_index.md` still lists PROJ-384 as `Planning`.

Additional command: `python Projects/scripts/validate_phase.py PROJ-384 1`

**Result:** FAILED

- Task 1.3 is 5/6 complete; missing the full sharded suite checkbox.
- Phase 1 status is `Complete` despite incomplete tasks.
- Warnings for empty notes on Tasks 1.1 and 1.2.

## Tests And Checks Run

- `git status --short` -> one unrelated pre-existing modified file: `AgentCoordination/generated/skill_usage/by_install/21f3651f7ffa42f8acdab05bd0a3c1bf.json`.
- `python Projects/scripts/validate_audit_ready.py PROJ-384` -> failed as above.
- `python Projects/scripts/validate_phase.py PROJ-384 1` -> failed as above.
- `python Projects/scripts/current_task.py PROJ-384` -> next task is Phase 1 > Task 1.3 final regression.
- `pytest tests/ -k "ability_manager or modifier_manager"` -> 63 passed.
- `rg` for all 12 deleted method names under `game/`, `tests/`, `combat_lab/`, and `Tools/` -> no live code references; remaining hits are test comments in `tests/unit/simulation/components/test_modifier_manager.py`.
- `git diff --name-only --diff-filter=U` -> no unresolved merge-conflicted files in the current worktree.

I did not run `python Tools/test_sharded/test_sharded.py`: audit readiness failed before formal audit, and the bounded review used the focused regression the project itself recorded.

## Plan Goals Vs Actual Implementation

### Goal: Delete 6 `AbilityManager.*_static` methods

**Met.** The original plan targeted `get_abilities_static`, `get_ability_static`, `has_ability_static`, `has_pdc_ability_static`, `get_ui_rows_static`, and `instantiate_abilities_static` (`Projects/active_projects/PROJ-384/phase_1_checklist.md:19`). Current `game/simulation/components/ability_manager.py` exposes the instance methods and private helpers only: `get_abilities` at line 93, `get_ability` at line 114, `has_ability` at line 134, `has_pdc_ability` at line 171, `get_ui_rows` at line 179, `_instantiate` at line 196, and `_get_abilities_polymorphic` at line 251.

### Goal: Delete 6 `ModifierManager.*_static` methods

**Met.** The original plan targeted `add_modifier_static`, `remove_modifier_static`, `get_modifier_static`, `get_all_effects_static`, `get_stat_summary_static`, and `remove_modifier_inplace` (`Projects/active_projects/PROJ-384/phase_1_checklist.md:27`). Current `game/simulation/components/modifier_manager.py` exposes the instance methods only: `add_modifier` at line 87, `remove_modifier` at line 126, `get_modifier` at line 139, `get_all_effects` at line 153, and `get_stat_summary` at line 165.

### Goal: Migrate 3 ability-manager tests to instance API

**Met.** `tests/unit/simulation/components/test_ability_manager.py:130` defines `TestAbilityManagerStandalone` as direct delegate tests. The three migrated tests are `test_manager_get_abilities` at line 138, `test_manager_has_ability` at line 147, and `test_manager_get_ui_rows` at line 156. The focused regression passed all 63 selected tests.

## Literal Checklist Execution

- Task 1.1 is supported by the current production file and focused tests.
- Task 1.2 is supported by the current production file and focused tests.
- Task 1.3 is not complete: the full sharded suite checkbox is still unchecked at `Projects/active_projects/PROJ-384/phase_1_checklist.md:34`.
- The checklist marks the phase `Complete` at `Projects/active_projects/PROJ-384/phase_1_checklist.md:8` despite the incomplete Task 1.3 checkbox.
- The phase completion checklist claims all task checkboxes are checked at `Projects/active_projects/PROJ-384/phase_1_checklist.md:41`, but line 34 is unchecked.
- The plan-level verification checklist is also still unchecked at `Projects/active_projects/PROJ-384/plan.md:52` and `Projects/active_projects/PROJ-384/plan.md:53`.
- The Task 1.3 claim of no remaining references "anywhere in the repo" is too broad if read literally: `tests/unit/simulation/components/test_modifier_manager.py:140` through `tests/unit/simulation/components/test_modifier_manager.py:142` still mention the deleted method names in explanatory comments. This is not a live-code regression, but it means the literal wording was not satisfied.

## Findings

### MAJOR-001: Phase marked complete while the final regression task remains incomplete

**Evidence:** `Projects/active_projects/PROJ-384/phase_1_checklist.md:8`, `Projects/active_projects/PROJ-384/phase_1_checklist.md:34`, `Projects/active_projects/PROJ-384/phase_1_checklist.md:41`, `Projects/active_projects/PROJ-384/plan.md:16`, `Projects/active_projects/PROJ-384/plan.md:52`, `Projects/active_projects/PROJ-384/plan.md:53`

Phase 1 and the plan phase table are marked complete, but the required full sharded suite task is still unchecked and the plan-level verification checklist is still open. Both `validate_audit_ready.py` and `validate_phase.py` fail on this mismatch. This blocks Protocol 04 audit readiness even though focused tests pass.

### MAJOR-002: Stale blocker text still blocks audit readiness

**Evidence:** `Projects/active_projects/PROJ-384/plan.md:22`, `Projects/active_projects/PROJ-384/plan.md:23`

The current state says commit is blocked by six unresolved merge-conflicted files. That blocker is now stale: `git log --grep=PROJ-384` shows commit `6398bb1da` landed, `git diff --name-only --diff-filter=U` returns no conflicted files, and current `git status --short` does not list those six files. Because the stale blocker remains in `plan.md`, `validate_audit_ready.py` reports a blocker and fails.

### MINOR-001: Project index still says PROJ-384 is Planning

**Evidence:** `Projects/projects_index.md:22`

The active project index lists PROJ-384 as `Planning` even though the plan and checklist mark Phase 1 complete and commit `6398bb1da` closed out the implementation. `validate_audit_ready.py` reports this as a warning. It should be synchronized before a final audit/closeout pass.

### MINOR-002: Literal "no remaining references anywhere" check is overbroad and not literally true

**Evidence:** `Projects/active_projects/PROJ-384/phase_1_checklist.md:35`, `tests/unit/simulation/components/test_modifier_manager.py:140`, `tests/unit/simulation/components/test_modifier_manager.py:141`, `tests/unit/simulation/components/test_modifier_manager.py:142`

The codebase no longer has live references to the deleted static APIs, but the checklist says no references remain anywhere in the repo. Test comments still name several deleted methods. This is harmless for runtime behavior, but the checklist wording should have been "no live code references" or the comments should have been excluded explicitly.

## Plan Gaps And Missed Assumptions

- The plan did not define an intermediate state for "code complete but audit blocked", so execution marked the phase complete while deferring the full suite.
- The plan assumed full-suite validation could be delegated to an orchestrator, but did not provide a checklist state that keeps Phase 1 incomplete until that external step is done.
- The plan did not account for post-commit synchronization of `plan.md`, `projects_index.md`, and validation checkboxes. That left stale blockers and status values after the implementation commit landed.
- The plan's "no remaining references anywhere" acceptance criterion was not precise enough to distinguish live call sites from explanatory comments and project documentation.

## Residual Risks

- Full-suite regression remains unproven in this review because Task 1.3 is still open.
- Audit readiness remains blocked until project-state metadata is corrected and the full sharded suite requirement is either completed or explicitly revised.
- The implementation is narrow and low-risk, but comments and stale project metadata can mislead later agents into redoing work or treating a completed code deletion as still blocked.

