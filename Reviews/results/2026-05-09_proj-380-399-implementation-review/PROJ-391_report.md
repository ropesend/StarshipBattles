# PROJ-391 Implementation Review

**Project:** Legacy removal - Underscore-prefixed legacy pair consolidations  
**Review date:** 2026-05-09  
**Reviewer:** Codex  

## Verdict

**Pass with reservations.** The three stated code consolidation goals are substantially met: the local harvester helper, local component iterator, and duplicated formation serializer functions are no longer active production helpers, and focused tests pass. I would not call the project fully audit-clean until the formation type contract and checklist/audit-evidence drift below are addressed.

No production, test, or project-plan files were modified during this review.

## Validation Result

`python Projects/scripts/validate_audit_ready.py PROJ-391` **passed**:

- Phase 1 complete.
- All 4 tasks complete.
- No blockers reported.
- Warning: `Projects/projects_index.md:15` still lists PROJ-391 as `Planning`.

`python Projects/scripts/validate_phase.py PROJ-391 1` also **passed** with 0 errors and 4 warnings for empty task notes.

## Tests And Checks Run

| Command | Result |
|---|---|
| `git status --short` | Pre-existing modified skill-usage counter and untracked review-results directory observed; left untouched. |
| `python Projects/scripts/validate_audit_ready.py PROJ-391` | Passed, with index status warning. |
| `python Projects/scripts/validate_phase.py PROJ-391 1` | Passed, 4 warnings for empty notes. |
| `python Projects/scripts/current_task.py PROJ-391` | No tasks remaining; project 100% complete. |
| `pytest tests/ -k planet_economy_projector` | 13 passed. |
| `pytest tests/ -k spec_compiler` | 80 passed. |
| `pytest tests/ -k formation` | 65 passed. |
| `rg -n "_get_harvester_info\|_iter_components\|_formation_to_dict\|_formation_from_dict" game --glob "*.py"` | No active helper definitions/call sites found; two production comments still mention removed helper names. |

I did not rerun the full sharded suite. The project plan records a prior sharded run with 19733 / 19742 passed, 3 failures, 2 errors, and 4 skipped, with the failures/errors described as pre-existing.

## Plan Goals Vs Actual Implementation

| Goal | Actual implementation | Assessment |
|---|---|---|
| Replace local `_get_harvester_info` in `planet_economy_projector.py` with canonical `get_harvester_info`. | `compute_planet_production` imports and calls `get_harvester_info` at `game/strategy/services/planet_economy_projector.py:50` and `:221`; it normalizes dict/list returns at `:228`. | Met. |
| Replace local `_iter_components` in `spec_compiler.py` and manual iteration in `planet_economy_projector.py` with canonical `iter_components`. | `spec_compiler.py:41` imports the canonical iterator and uses it at `:360`; `planet_economy_projector.py:49` imports it and uses it at `:220`. | Met. |
| Move duplicated `_formation_to_dict/_formation_from_dict` helpers onto `FormationSpec`. | `FormationSpec.to_dict/from_dict` exist at `game/simulation/combat/formation.py:71` and `:82`; `TaskForce` uses them at `game/strategy/data/task_force.py:90` and `:105`; replay serialization uses them at `game/simulation/replay/replay_serialization.py:297` and `:310`. | Mostly met, with a type-contract caveat in Finding 1. |

## Literal Checklist Execution

- The phase checklist is checked complete, and both project validators pass.
- Task 1.4 records the full sharded suite as not fully green: `Projects/active_projects/PROJ-391/phase_1_checklist.md:46-54` lists 3 failures and 2 errors as pre-existing. That is compatible with "baseline preserved," but not with the same checklist line's "pytest passes" wording at `:55`.
- The plan-level verification checklist remains unchecked for "All tests passing" and "No remaining references" at `Projects/active_projects/PROJ-391/plan.md:57-58`.
- The literal broad grep claims in the checklist are over-broad: helper-name references remain in project docs, tests, and production comments. The active production helper definitions/call sites are gone, but the documented `grep ... . returns zero hits` standard was not literally met.
- `Projects/projects_index.md:15` still marks PROJ-391 as `Planning`, matching the audit-readiness warning.

## Findings

### 1. Medium - Formation serialization still preserves the loose `object` slot and silently drops invalid formations

**Evidence:** `game/simulation/battle_spec.py:168`, `game/simulation/replay/replay_serialization.py:296-301`, `tests/unit/simulation/replay/test_serialization.py:340-351`

PROJ-391 moved formation serialization onto `FormationSpec`, but the plan did not account for the upstream `TaskForceSpec.formation: object` vestige. Replay serialization now calls `formation.to_dict()` only when `isinstance(formation, FormationSpec)` and otherwise serializes `None`. The test suite explicitly blesses non-`FormationSpec` objects being converted to `None`.

That avoids the old synthetic placeholder fallback, but it still leaves a silent fallback path instead of making the contract explicit. If a future compiler accidentally emits a non-`FormationSpec`, replay capture loses the formation rather than failing at the boundary. The more complete root fix is to tighten `TaskForceSpec.formation` to `FormationSpec | None` (or otherwise enforce the contract) and make replay serialization call the canonical method without an invalid-object escape hatch.

### 2. Low - New public `FormationSpec` methods use legacy typing style

**Evidence:** `game/simulation/combat/formation.py:23`, `game/simulation/combat/formation.py:71`, `game/simulation/combat/formation.py:82`

The new public `to_dict` / `from_dict` methods use `Dict[str, Any]` and an unnecessary quoted return type. Current conventions require modern PEP 604 / built-in generic style for new or touched public signatures. This is not a runtime bug, but it is a convention miss in the only newly added public API surface for this project.

### 3. Low - Completion evidence overstates literal grep and test status

**Evidence:** `Projects/active_projects/PROJ-391/phase_1_checklist.md:55`, `Projects/active_projects/PROJ-391/plan.md:21`, `Projects/active_projects/PROJ-391/plan.md:57-58`, `Projects/projects_index.md:15`

The implementation appears to meet the intended production cleanup, but the recorded checklist evidence is not literally true. The full suite did not pass; it preserved a branch baseline with known failures/errors. Broad helper-name grep is also not zero across the repo, and even `game/**/*.py` still has production comments mentioning removed helper names. The index also remains `Planning`. This matters for audit because later agents may rely on checklist statements instead of rerunning the checks.

## Plan Gaps / Missed Assumptions

- The initial plan did not include `game/simulation/battle_spec.py`, even though moving formation serialization onto `FormationSpec` exposed the stale `TaskForceSpec.formation: object` contract.
- The plan required an `isinstance` guard for `get_harvester_info` returning `dict | list | None`, and the implementation added one, but the focused project tests I found still primarily cover single-dict harvesters. Multiple harvester entries are a residual coverage risk rather than a confirmed bug.
- The plan did not include a convention/static-style check for new public annotations, which let the legacy `Dict` signature through.
- The plan mixed "baseline preserved" and "pytest passes" language. For audit, those should be distinct states.

## Residual Risks

- Full-suite status was not independently rechecked in this review; the project records existing branch failures/errors.
- The formation serialization behavior is green because tests accept the `object -> None` path, not because the type contract is fully enforced.
- Remaining helper-name comments are low-risk, but they make broad grep-based audit checks noisy.
