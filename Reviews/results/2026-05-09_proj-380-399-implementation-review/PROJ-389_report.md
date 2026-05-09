# PROJ-389 Implementation Review

**Date:** 2026-05-09
**Reviewer:** Codex
**Scope:** Skeptical post-implementation review of PROJ-389, using Protocol 04 principles and the requested extra checks for plan goals, literal checklist execution, and initial plan gaps.

## Verdict

**Not audit-ready.** The implementation goals appear met in code: all live production/test/doc references to `score_planet_for_race` are gone, the wrapper is deleted, the public re-export is removed, and focused tests pass.

The project still fails audit-readiness because project metadata says Phase 1 is complete while Task 1.6 has four unchecked completion subtasks, `Projects/projects_index.md` still marks PROJ-389 as `Planning`, and the project verification checklist remains unchecked.

## Validation Result

`python Projects/scripts/validate_audit_ready.py PROJ-389` failed:

- Phase completion: **FAIL** - Phase 1 > Task 1.6 has 4 unchecked subtasks.
- Task completion: **FAIL** - 1 task has incomplete subtasks.
- Blockers/status: **PASS** - no blockers reported.
- Index status: **WARN** - index status is `Planning`.

I also ran `python Projects/scripts/validate_phase.py PROJ-389 1`, which failed:

- Task 1.6 is 7/11 complete.
- Phase 1 status is `Complete` while it has incomplete tasks.
- Warnings for empty Notes on Tasks 1.1 through 1.5.

`python Projects/scripts/current_task.py PROJ-389` confirms the next task is still Phase 1 > Task 1.6, with the same four remaining subtasks.

## Tests And Checks Run

- `git status --short`
  - Existing unrelated modified file: `AgentCoordination/generated/skill_usage/by_install/21f3651f7ffa42f8acdab05bd0a3c1bf.json`
  - Existing untracked review directory: `Reviews/results/2026-05-09_proj-380-399-implementation-review/`
- `python Projects/scripts/validate_audit_ready.py PROJ-389`
  - Failed, as described above.
- `python Projects/scripts/validate_phase.py PROJ-389 1`
  - Failed, as described above.
- `python Projects/scripts/current_task.py PROJ-389`
  - Reports Task 1.6 still has four remaining subtasks.
- `rg -n "score_planet_for_race" game tests docs combat_lab Tools --glob '!docs/_ignore/**'`
  - No matches.
- `python -c "import game.strategy.formulas as formulas; import game.strategy.formulas.habitability as h; assert hasattr(formulas, 'calculate_habitability'); assert not hasattr(formulas, 'score_planet_for_race'); assert not hasattr(h, 'score_planet_for_race')"`
  - Passed.
- `pytest -p no:cacheprovider tests/unit/strategy/engine/test_population_engine.py tests/unit/strategy/engine/test_happiness_engine.py tests/unit/strategy/formulas/test_colony_output.py tests/unit/strategy/engine/test_harvesting_engine_habitability.py tests/unit/ui/screens/test_strategy_detail_fmt.py -q`
  - 172 passed.
- `pytest -p no:cacheprovider tests/unit/strategy/facade/test_colony_demographic_view.py -q`
  - 17 passed.
- `pytest -p no:cacheprovider tests/ -k economy_slice -q`
  - No tests ran; exit code 1.

I did not run `python Tools/test_sharded/test_sharded.py` because the runner writes timing/cache/baseline artifacts such as `.test_durations.json`, `.pytest_cache/shard_results`, and `AgentCoordination/generated/test_baseline/...`, which conflicts with this task's sole-write-target constraint.

## Plan Goals Vs Actual Implementation

Goal: migrate six production callers to `calculate_habitability`.

- Met. Current call sites use `calculate_habitability`:
  - `game/strategy/engine/population_engine.py:139`
  - `game/strategy/engine/happiness_engine.py:117`
  - `game/strategy/facade/slices/economy_slice.py:157`
  - `game/strategy/formulas/colony_output.py:95` and `:152`, with the doc formula at `:47`
  - `game/ui/screens/strategy_detail_fmt.py:129`

Goal: remove `score_planet_for_race` from public formula re-exports.

- Met. `game/strategy/formulas/__init__.py:7-11` imports and exports only `calculate_habitability`.

Goal: delete the wrapper from `habitability.py`.

- Met. `game/strategy/formulas/habitability.py:48-92` contains `calculate_habitability`; no `score_planet_for_race` symbol remains.

Goal: keep code and live docs/tests consistent.

- Mostly met in implementation. The phase checklist records out-of-band doc/test cleanup at `Projects/active_projects/PROJ-389/phase_1_checklist.md:59-68`, and the live grep over `game`, `tests`, `docs`, `combat_lab`, and `Tools` finds no wrapper references.

## Literal Checklist Execution

The task checkboxes for the migration work are checked, but the project is not literally complete by its own workflow files:

- `Projects/active_projects/PROJ-389/phase_1_checklist.md:74-77` leaves all four Phase Completion Checklist items unchecked.
- `Projects/active_projects/PROJ-389/plan.md:56-59` leaves all Verification checklist items unchecked.
- `Projects/projects_index.md:17` still marks PROJ-389 as `Planning`.
- `Projects/active_projects/PROJ-389/phase_1_checklist.md:53` names the full sharded runner as Task 1.6's test command, but `:57` records only a focused suite passing. The project files do not record a full sharded run.
- `Projects/active_projects/PROJ-389/phase_1_checklist.md:31` names `pytest tests/ -k economy_slice`, but that command currently selects no tests.

## Plan Gaps And Missed Assumptions

- The initial `plan.md` and `manifest.md` treated this as a seven-production-file migration. They did not account up front for the test monkeypatch targets or live docs that also referenced the wrapper. The phase checklist later captured those updates at `phase_1_checklist.md:59-68`, but `manifest.md:7-13` still omits those touched docs/test files.
- The plan's verification command at `plan.md:58` says no remaining references via `grep -rn "score_planet_for_race" .`. Taken literally, that is too broad: history-preserving `Projects/`, `Reviews/`, and archive artifacts intentionally retain references. The phase checklist narrows the intended live-code scope at `phase_1_checklist.md:57`, but the plan-level completion criterion remains imprecise.
- The plan/checklist did not identify the actual facade coverage target for `economy_slice.py`. The named command `pytest tests/ -k economy_slice` runs zero tests; the relevant current facade coverage appears to be `tests/unit/strategy/facade/test_colony_demographic_view.py`, which passed in this review.

## Findings

### Major: Audit readiness is blocked by incomplete project metadata

The code migration may be complete, but audit-readiness validation fails because Task 1.6 still has four unchecked completion subtasks. The phase file also says `Status: Complete`, creating an internal contradiction. Evidence: `Projects/active_projects/PROJ-389/phase_1_checklist.md:8` says complete, while `:74-77` leaves the phase completion checklist unchecked. The project index also remains `Planning` at `Projects/projects_index.md:17`.

### Minor: Verification evidence does not match the literal checklist

Task 1.6 names `python Tools/test_sharded/test_sharded.py` as the test command at `Projects/active_projects/PROJ-389/phase_1_checklist.md:53`, but the recorded verification line at `:57` says a focused suite passed. Separately, Task 1.3 names `pytest tests/ -k economy_slice` at `:31`, and that command currently selects no tests. This does not show a production bug, but it weakens the literal execution trail.

### Minor: Manifest was not updated for actual touched support files

The manifest lists only the original production files at `Projects/active_projects/PROJ-389/manifest.md:7-13`, while the phase checklist records additional docs and tests updated at `Projects/active_projects/PROJ-389/phase_1_checklist.md:61-68`. This is a plan/manifest synchronization gap, especially because the project explicitly cites code/docs consistency as part of the same change.

## Residual Risks

- Full-suite health is not established by this review because the sharded runner was not run under the sole-write-target constraint.
- No direct test is selected by the checklist's `economy_slice` command; current coverage exists under the colony demographic facade test, but the checklist should name it directly.
- Historical docs and archive references remain by design. Future global greps must exclude `Projects/deep_archive`, historical `Reviews`, and sibling project bundles, or they will produce expected false positives.
