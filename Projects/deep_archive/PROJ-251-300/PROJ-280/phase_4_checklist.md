# Phase 4: Migrate 5 templates to use new helpers

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-280 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (verified 2026-04-18)
**Objective:** Migrate the 5 canonical templates to use the new base helpers — both for preconditions and for the wire_ships snapshot phase.

---

## Tasks

### Task 4.1: Migrate `_template_preconditions` in all 5 templates [Medium]
**File:** `combat_lab/scenarios/templates.py`
**Tests:** `python -m combat_lab.run_tests --fast`

- [x] `StaticTargetScenario`: replaced body with `return self._common_preconditions()` (simple delegation)
- [x] `DuelScenario`: same simple delegation
- [x] `ResourceScenario`: same simple delegation
- [x] `PropulsionScenario`: changed first line to `checks = self._common_preconditions()`; retained conditional movement/rotation checks
- [x] `ComparisonScenario`: prepended `checks = self._common_preconditions()`; kept existing A/B validation logic
- [x] Combat Lab simulation suite: 162 passed / 0 failed / 0 skipped

**Notes:** ComparisonScenario's addition is semantically redundant with its "Baseline Ticks" check (both imply the sim ran) but satisfies the sentinel uniformly. The `"Simulation Ran"` check reads `results['ticks_run']`; ComparisonScenario populates that in `collect_results`.

### Task 4.2: Migrate `wire_ships` to use `_snapshot_initial_state` in all 5 templates [Medium]
**File:** `combat_lab/scenarios/templates.py`
**Tests:** `python -m combat_lab.run_tests --fast` + full Combat Lab scope tests

- [x] `StaticTargetScenario`: split into `_snapshot_initial_state` (cache attacker/target + initial_hp) + `wire_ships` (force_fire policy)
- [x] `DuelScenario`: split into snapshot (cache ship1/ship2 + both initial_hp) + policy
- [x] `PropulsionScenario`: split into snapshot (cache ship + start pose) + policy (physics calc stays in wire_ships, followed by thrust/turn policy)
- [x] `ResourceScenario`: split into snapshot (cache ship/target + initial_value/initial_hp) + policy
- [x] `ComparisonScenario`: split into snapshot (A/B role resolution + initial_hp) + policy (force_fire + configure hooks)
- [x] Combat Lab simulation suite: 162 passed
- [x] PROJ-280 scope tests: 3627 passed

**Notes:** The 2 concrete overrides that bypass template logic (`PropThrustMassRatioScenario`, `ExternalBattleConditionApplied`) remain opt-in — they don't call `_snapshot_initial_state` and are unaffected.

### Task 4.3: Fix test that didn't populate `ticks_run` [Simple]
**File:** `tests/unit/combat_lab/test_comparison_visual_baseline.py`
**Tests:** `pytest tests/unit/combat_lab/test_comparison_visual_baseline.py`

- [x] Updated `_make_scenario` helper in `TestTemplatePreconditions` to populate `scenario.results['ticks_run'] = 10`
- [x] Fix needed because PROJ-280 added the universal "Simulation Ran" check to ComparisonScenario, which reads `results['ticks_run']`
- [x] Test passes after fix

**Notes:** Single test-only adjustment. Production behavior is unchanged — `ComparisonScenario.collect_results` already populates `ticks_run`.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Combat Lab simulation suite: 162 passed / 0 failed / 0 skipped
- [x] PROJ-280 scope tests: 3627 passed
- [x] No template re-introduces duplicated boilerplate (each follows the canonical pattern)
- [x] Sentinel enforcement is effectively active (5 templates override `_template_preconditions`; all call `_common_preconditions`)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5 (docs)
