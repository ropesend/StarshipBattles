# PROJ-398 Implementation Review

**Date:** 2026-05-09  
**Reviewer:** Codex  
**Protocol:** Skeptical post-implementation review using Protocol 04 principles  
**Scope:** PROJ-398 remediation of five MAJOR PROJ-380 review findings

## Verdict

**Not audit-ready.** The implementation commits appear to address the five named MAJOR remediation goals, and focused tests passed, but the project cannot pass audit because its own phase checklist remains unchecked while the phase and plan claim completion. The project artifacts also remain skeletal (`design.md`, `manifest.md`, and `decisions.md`), so the literal project-system execution is not clean.

Protocol 04 says not to proceed with a full audit after `validate_audit_ready.py` fails. Per the requested workflow, I still performed a bounded implementation inspection and focused test run, but this should be treated as a blocker report, not an audit pass.

## Validation Result

Command:

```powershell
python Projects/scripts/validate_audit_ready.py PROJ-398
```

Result: **FAILED** with 4 errors and 1 warning.

- Phase 1 is marked complete, but Task 1.1 has 1 unchecked subtask.
- Task 1.2 has 3 unchecked subtasks.
- Task 1.3 has 3 unchecked subtasks.
- Task completion check reports 3 tasks with incomplete subtasks.
- Warning: `Projects/projects_index.md` still lists PROJ-398 as `Planning`.

Additional phase check:

```powershell
python Projects/scripts/validate_phase.py PROJ-398 1
```

Result: **FAILED** with 4 errors. It confirms all three phase tasks are incomplete and Phase 1 is marked `Complete` despite unchecked work.

## Tests Run

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; pytest tests/unit/ui/test_camera.py tests/unit/ui/screens/test_strategy_colonization.py tests/unit/ui/screens/test_strategy_click_dispatcher.py tests/unit/strategy/services/ability_sources/test_star.py -q -p no:cacheprovider
```

Result: **78 passed**.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; pytest tests/unit/strategy/services/test_ability_iterator.py -q -p no:cacheprovider
```

Result: **17 passed**.

I did not run the full sharded suite. The project checklist names it as required, but the audit-readiness gate failed before full audit; the missing full-suite receipt remains one of the validation blockers.

## Plan Goals vs Actual Implementation

The plan goal was narrow: address five MAJOR follow-up findings from the PROJ-380 review (`plan.md:16-22`). The source review identifies these five items at `Reviews/results/2026-05-09_015904_code_proj-380-audit-shrink-cleanup-3-phases-11-verified_req-req_20260509_015902_916201/report.md:20-66`.

Implementation evidence:

- **FND-012, Camera.hex_at_screen test coverage:** Met. `tests/unit/ui/test_camera.py:117-164` adds real `screen_to_world -> pixel_to_hex` coverage. Focused test file passed.
- **FND-017, handle_colonize_designation coverage:** Met. `tests/unit/ui/screens/test_strategy_colonization.py:106-184` adds the requested no-fleet, no-system, no-candidate, and prompt-path cases. Focused test file passed.
- **FND-031/FND-032, TRANSFER/DROP_CARGO/LOAD_CARGO consolidation:** Met. `game/ui/screens/strategy_click_dispatcher.py:228-305` introduces `_handle_dialog_mode_click` and reduces the three handlers to delegations. `tests/unit/ui/screens/test_strategy_click_dispatcher.py:326-381` covers the three left-click paths and shared right-click cancellation. Focused test file passed.
- **FND-041, `_star_provider` consolidation:** Met at the code level. `game/strategy/services/ability_iterator.py:121-158` documents the shared skeleton, and `_star_provider` delegates through it at `game/strategy/services/ability_iterator.py:230-245`. `StarAbilitySource.affects_hex` owns the system-scope fallback at `game/strategy/services/ability_sources/star.py:45-91`. `tests/unit/strategy/services/ability_sources/test_star.py:120-190` and `tests/unit/strategy/services/test_ability_iterator.py:216-235` cover this behavior. Focused tests passed.

I did not find a confirmed implementation defect in the remediation code during this bounded pass.

## Literal Checklist Execution

Literal execution is not clean.

- `phase_1_checklist.md:3` says Phase 1 status is `Complete`, and lines 7-11 list all five findings as closed.
- The actual task checkboxes are still unchecked at `phase_1_checklist.md:20`, `phase_1_checklist.md:29-31`, and `phase_1_checklist.md:36`.
- The phase completion checklist is also unchecked at `phase_1_checklist.md:41-42`.
- `plan.md:6` marks the phase `Complete`, `plan.md:9-11` says closeout/user verification, but `plan.md:24-27` still leaves all verification boxes unchecked.
- `Projects/projects_index.md:8` still lists PROJ-398 as `Planning`.

This is enough to block audit even if the code changes are functionally correct.

## Plan Gaps and Missed Assumptions

- The plan did not convert the five MAJOR findings into independently checkable subtasks. It named themes in Task 1.1 but left Task 1.2 as broad instructions, which made it easy for the closeout text to claim completion without checking the task boxes.
- The plan assumed three commits and a narrative "Closed Findings" section were sufficient evidence, but audit tooling requires checked subtasks and phase completion metadata.
- The plan did not account for project-system hygiene: `design.md` remains a template (`design.md:7-23`), `manifest.md` still contains placeholder rows (`manifest.md:8-11`), and `decisions.md` only records initialization (`decisions.md:7-9`).
- The plan specified the full sharded suite in Task 1.3 (`phase_1_checklist.md:33-36`) but left no recorded receipt in the project artifacts and did not check the task.

## Findings

### BLOCKER: Phase is marked complete while required tasks remain unchecked

**Evidence:** `Projects/active_projects/PROJ-398/phase_1_checklist.md:3`, `Projects/active_projects/PROJ-398/phase_1_checklist.md:20`, `Projects/active_projects/PROJ-398/phase_1_checklist.md:29-31`, `Projects/active_projects/PROJ-398/phase_1_checklist.md:36`, `Projects/active_projects/PROJ-398/phase_1_checklist.md:41-42`, `Projects/active_projects/PROJ-398/plan.md:6`, `Projects/active_projects/PROJ-398/plan.md:24-27`.

The implementation claims Phase 1 is complete, but every task checkbox and phase completion checkbox remains open. Both `validate_audit_ready.py` and `validate_phase.py` fail on this mismatch, so the project cannot be considered audit-ready.

### MAJOR: Project artifacts are still skeleton placeholders

**Evidence:** `Projects/active_projects/PROJ-398/design.md:7-23`, `Projects/active_projects/PROJ-398/manifest.md:8-11`, `Projects/active_projects/PROJ-398/decisions.md:7-9`.

The design document still contains template placeholders, the manifest lists `path/to/file.py` and `tests/path/to/test_file.py` instead of the touched production/test files, and the decisions log has no implementation decisions after project initialization. This fails the literal project-system expectation that plan, design, decisions, and manifest stay synchronized with implementation.

### MINOR: Project index status contradicts local closeout state

**Evidence:** `Projects/projects_index.md:8`, `Projects/active_projects/PROJ-398/plan.md:8-11`.

The project index still says `Planning` while the plan says `Closeout` and "User verification." This is reported as a validation warning rather than an error, but it is still stale bookkeeping and should be corrected before close/archive.

## Residual Risks

- The full sharded suite was not run in this review. The project itself required it, and there is no checked project receipt showing it passed.
- The bounded code inspection supports the five MAJOR closures, but it did not re-review the 8 MINOR and 30 INFO source-review items because PROJ-398 explicitly scoped them out.
- The star-provider change relies on callers passing the relevant system when querying a hex; current tests cover that contract, but there is no broader audit here of all call sites that construct `(system, hex_coord)` pairs.

## Files Changed by This Review

- `Reviews/results/2026-05-09_proj-380-399-implementation-review/PROJ-398_report.md`
