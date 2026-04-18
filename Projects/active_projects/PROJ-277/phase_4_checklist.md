# Phase 4: Update scenario_run_helper Dispatch

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-277 4`

**Status:** Deferred — filed as a follow-up project candidate
**Objective:** `scenario_run_helper` dispatches to ABBattleRunner when the scenario is a ComparisonScenario. Non-ComparisonScenario unchanged.

---

## Deferral rationale

Phase 4 would complete the architectural separation — scenario as passive input, runner as orchestrator. It requires:
- Rewiring `combat_lab/services/scenario_run_helper.py` headless dispatch
- Rewiring `combat_lab/services/test_execution_service.py::run_visual` + `game/ui/screens/test_lab/screen.py`
- Threading per-side pre-tick / per-tick hooks through `ABBattleRunner.run_one` so `configure_baseline` / `configure_variant` / `wire_ships` still fire
- Rewriting `ComparisonScenario.collect_results` to read from `ab.baseline_outcome` / `ab.variant_outcome` instead of live `self.target` / `self._baseline_*` state
- Manual visual-mode verification across three UI buttons (Visual Run, Visual Baseline, Headless Run)

**Phase 3 already delivers the user-facing contract** — `validate(self, ab: ABBattleOutcome)` is the first-class API every subclass now uses. The architectural remainder (who OWNS the `run_battle` calls) is cleanup, not a behavior change, and is better tackled as a dedicated project with isolated UI-regression testing.

Captured in memory at `memory/project_proj277_ab_runner.md`.

---

## Tasks

### Task 4.1: Update dispatch logic [Medium]
**File:** `combat_lab/services/scenario_run_helper.py`
**Tests:** `pytest tests/unit/combat_lab/services/test_scenario_run_helper.py -v`

- [ ] Deferred — see rationale above.

**Notes:** The surgery is straightforward in isolation but ripples through `collect_results` and the per-side hook plumbing. Best approached in a fresh session with ability to do visual smoke testing.

### Task 4.2: Update Combat Lab UI dispatch [Medium]
**File:** `game/ui/screens/test_lab/screen.py` + `combat_lab/services/test_execution_service.py`
**Tests:** Manual + unit tests

- [ ] Deferred — see rationale above.

**Notes:**

### Task 4.3: Regression sweep [Simple]
**File:** N/A
**Tests:** `python -m combat_lab.run_tests --fast`

- [ ] Deferred — see rationale above.

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update plan.md
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-277 4`
