# Phase 4: Update scenario_run_helper Dispatch

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-277 4`

**Status:** Not Started
**Objective:** `scenario_run_helper` dispatches to ABBattleRunner when the scenario is a ComparisonScenario. Non-ComparisonScenario unchanged.

---

## Tasks

### Task 4.1: Update dispatch logic [Medium]
**File:** `combat_lab/services/scenario_run_helper.py`
**Tests:** `pytest tests/unit/combat_lab/services/test_scenario_run_helper.py -v`

- [ ] Add import: `from combat_lab.services.ab_battle_runner import ABBattleRunner`
- [ ] In the main run function, add a branch: `if isinstance(scenario, ComparisonScenario): ...` → dispatch to ABBattleRunner
- [ ] Non-ComparisonScenario path stays identical
- [ ] ComparisonScenario path: build base_spec → call `build_baseline_spec` / `build_variant_spec` → run via `ABBattleRunner.run(...)` → pass `ABBattleOutcome` to `scenario.validate`
- [ ] Run tests — pass

**Notes:**

### Task 4.2: Update Combat Lab UI dispatch [Medium]
**File:** `game/ui/screens/test_lab/screen.py` + `combat_lab/services/test_execution_service.py`
**Tests:** Manual + unit tests

- [ ] For visual mode: if scenario is a ComparisonScenario, use ABBattleRunner with `render_mode` parameter
- [ ] Otherwise: existing single-battle visual path
- [ ] Verify visual-baseline button in UI passes `render_mode="baseline_only"` when pressed

**Notes:**

### Task 4.3: Regression sweep [Simple]
**File:** N/A
**Tests:** `python -m combat_lab.run_tests --fast`

- [ ] Combat Lab fast suite passes
- [ ] Visual-mode smoke: launch any non-comparison test, works as before
- [ ] Visual-mode smoke: launch a comparison test, shows both battles
- [ ] Visual-baseline smoke: launch a comparison test with baseline-only render, shows baseline + validation output

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update plan.md
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-277 4`
