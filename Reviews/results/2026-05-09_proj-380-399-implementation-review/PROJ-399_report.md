# PROJ-399 Implementation Review

**Date:** 2026-05-09  
**Reviewer:** Codex  
**Scope:** Skeptical post-implementation review of PROJ-399 against Protocol 04 principles and the requested plan/execution criteria.

## Verdict

**FAIL - not audit-ready.** The focused implementation goals appear to be met: the three targeted failing test areas pass, the UI/workshop collection selector no longer errors, and related pathfinding shim tests pass. However, `validate_audit_ready.py PROJ-399` fails because every Phase 1 task still has unchecked subtasks, `validate_phase.py` also fails, and `Projects/projects_index.md` still reports PROJ-399 as `Planning`.

This cannot be claimed as an audit pass until the project-system artifacts are corrected and the full-suite claim is revalidated under a workflow allowed to update its baseline receipt files.

## Validation Result

`python Projects/scripts/validate_audit_ready.py PROJ-399` failed:

- Phase completion: Phase 1 is marked complete, but Tasks 1.1-1.5 have unchecked subtasks.
- Task completion: 5 tasks have incomplete subtasks.
- Blockers/status: no blockers, but index status is `Planning`.
- Result: **FAILED**, 6 errors, 1 warning.

Additional check:

- `python Projects/scripts/validate_phase.py PROJ-399 1` failed with 6 errors: Tasks 1.1-1.5 are all `0/N` complete, and Phase 1 status says complete while tasks are incomplete.

## Tests Run

- `pytest tests/integration/strategy/test_save_round_trip_phase4.py -v` - **3 passed**
- `pytest tests/unit/tools/test_testcoverage_audit.py -v` - **5 passed**
- `pytest tests/unit/tools/test_scalene_profiling_workflow.py -v` - **2 passed**
- `pytest tests/unit/ui/ tests/unit/workshop/ --collect-only -q` - **4798 collected**, 0 collection errors
- `pytest tests/unit/strategy/pathfinding tests/unit/strategy/data/test_pathfinding_shim_scope.py -q` - **79 passed**
- `python Tools/test_sharded/test_sharded.py --help` - checked options; there is no no-baseline-write mode

I did not rerun `python Tools/test_sharded/test_sharded.py` because this review was restricted to one write target, and the sharded runner help states that green whole-suite runs always refresh per-install verification. The testing docs also state green runs write tracked baseline artifacts.

## Plan Goals vs Actual Implementation

PROJ-399's goal was branch hygiene: close 3 pre-existing failures and 4 pytest collection errors so the sharded suite reaches zero failures and zero collection errors.

| Goal | Evidence | Assessment |
|------|----------|------------|
| Resolve `test_pathfinder_attached_after_init` failure | `tests/integration/strategy/test_save_round_trip_phase4.py:31-39` now treats `Galaxy._intercept` as intentionally removed; `game/strategy/data/pathfinding.py:62-69` constructs fresh intercept calculators. Focused save round-trip and pathfinding tests pass. | Met for focused behavior. |
| Reconcile testcoverage skill canary | `tests/unit/tools/test_testcoverage_audit.py:75-86` now asserts the shipped `--coverage-json` flag is documented; `.opencode/skills/ocode-testcoverage-audit/SKILL.md:57-58` documents the flag. Focused test passes. | Met. |
| Restore Scalene discoverability canary | `docs/README.md:50` restores the profiling guide link; `tests/unit/tools/test_scalene_profiling_workflow.py:20-39` checks the docs/tool/skill surfaces. Focused test passes. | Met. |
| Fix pytest basename collection errors | Commit `570d7a2ba` added package markers for the six affected directories, including `tests/unit/entities/__init__.py`, `tests/unit/ui/screens/__init__.py`, `tests/unit/ui/screens/builder/__init__.py`, `tests/unit/ui/screens/race_setup/__init__.py`, `tests/unit/ui/widgets/__init__.py`, and `tests/unit/workshop/__init__.py`. Collection passes. | Met. |
| Prove full sharded suite is clean | `Projects/active_projects/PROJ-399/plan.md:26-28` records a green full sharded run. I did not rerun it due the write restriction noted above. | Claimed by project, not independently revalidated in this review. |

## Literal Checklist Execution

The literal checklist execution is not acceptable. `Projects/active_projects/PROJ-399/phase_1_checklist.md:14-17`, `23-26`, `32-35`, `41-44`, and `49-50` leave every task subitem unchecked, and `phase_1_checklist.md:55-57` leaves the phase completion checklist unchecked. This directly contradicts `Projects/active_projects/PROJ-399/plan.md:6` and `plan.md:10`, which claim completion and a clean sharded run.

`Projects/projects_index.md:7` also still marks PROJ-399 as `Planning`, matching the audit-readiness warning.

## Plan Gaps / Missed Assumptions

- `design.md` was never filled in. `Projects/active_projects/PROJ-399/design.md:7-23` is still scaffold text, so the project lacks recorded analysis, architecture context, reusable patterns, and risks.
- `manifest.md` was never updated. `Projects/active_projects/PROJ-399/manifest.md:8-11` still contains placeholder rows, despite the implementation touching tests, docs, skill-facing tests, package marker files, project files, and baseline receipts.
- The collection-error plan under-scoped one collision path. `phase_1_checklist.md:37-42` describes `tests/unit/{ui,workshop}/`, but the actual fix also required `tests/unit/entities/__init__.py` for the `test_components.py` collision.
- The plan treats a full sharded run as final proof but does not account for the runner's tracked baseline writes. That matters for read-only or restricted-write review workflows like this one.

## Findings

### BLOCKER: Audit readiness fails because checklist/index state contradicts completion

**Evidence:** `Projects/active_projects/PROJ-399/phase_1_checklist.md:14-57`, `Projects/projects_index.md:7`, validator output from `validate_audit_ready.py PROJ-399`.

The project claims Phase 1 is complete, but all task subtasks and phase completion items are unchecked. The project index still says `Planning`. Protocol 04 requires pre-audit validation to pass before an audit can proceed, so this blocks audit completion regardless of the focused test results.

### MAJOR: Project traceability artifacts were left as placeholders

**Evidence:** `Projects/active_projects/PROJ-399/design.md:7-23`, `Projects/active_projects/PROJ-399/manifest.md:8-11`.

The implementation changed multiple real files, but the manifest still contains `path/to/file.py` placeholders and the design document is empty scaffold text. This prevents reliable conflict/scope review and weakens the audit trail for why test-only changes were chosen over production changes.

### MINOR: Initial collection-error scope was incomplete

**Evidence:** `Projects/active_projects/PROJ-399/phase_1_checklist.md:37-42`; actual implementation added `tests/unit/entities/__init__.py` in commit `570d7a2ba`.

The plan described the collection issue as confined to `tests/unit/{ui,workshop}/`, but one of the four collisions involved `tests/unit/entities/test_components.py`. The implementation compensated correctly, so this is a planning gap rather than a remaining code defect.

## Residual Risks

- Full-suite cleanliness is not independently confirmed in this review. The project records a clean sharded run, but rerunning it would update tracked baseline artifacts outside the allowed write target.
- The `Galaxy._intercept` resolution relies on the previous architectural decision that the attribute is intentionally gone. Current pathfinding tests support that, but the PROJ-399 design document does not record the decision.
- Project metadata drift is systemic across nearby projects in `Projects/projects_index.md`; fixing only PROJ-399 may require a broader index sync decision.
