# Phase 3: Refactor ComparisonScenario

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-277 3`

**Status:** Not Started
**Objective:** Remove embedded `run_battle` call + telemetry role-remapping + visual-baseline validate bypass. Introduce clean `build_baseline_spec` / `build_variant_spec` hooks.

---

## Tasks

### Task 3.1: Inventory existing ComparisonScenario API [Simple]
**File:** `combat_lab/scenarios/templates.py`
**Tests:** N/A (read-only)

- [ ] Read `ComparisonScenario` class end-to-end (L827-920, L1120-1166)
- [ ] List all public/private methods and the attributes stashed on `self._baseline_*`
- [ ] Document in `findings/comparison_scenario_audit.md`: current method list, what they do, which subclasses override what
- [ ] Identify which methods are called by external code vs purely internal

**Notes:**

### Task 3.2: Write failing test for new API [Medium]
**File:** `tests/unit/combat_lab/scenarios/test_comparison_scenario.py`
**Tests:** `pytest tests/unit/combat_lab/scenarios/test_comparison_scenario.py -v`

- [ ] Test: subclass of ComparisonScenario overrides `build_baseline_spec(base_spec)` and `build_variant_spec(base_spec)`
- [ ] Test: `validate(ab_outcome: ABBattleOutcome)` receives a complete ABBattleOutcome object
- [ ] Test: `_run_validation` no longer bypasses on visual-baseline mode
- [ ] Test: `_baseline_outcome`, `_baseline_telemetry`, `_run_baseline_battle` attributes do NOT exist
- [ ] Run — all fail

**Notes:**

### Task 3.3: Add `build_baseline_spec` / `build_variant_spec` hooks [Medium]
**File:** `combat_lab/scenarios/templates.py`
**Tests:** `pytest tests/unit/combat_lab/scenarios/test_comparison_scenario.py -v`

- [ ] Add `build_baseline_spec(self, base_spec: BattleSpec) -> BattleSpec` — default returns `base_spec` unchanged
- [ ] Add `build_variant_spec(self, base_spec: BattleSpec) -> BattleSpec` — default returns `base_spec` unchanged
- [ ] Add a docstring explaining the pattern — subclasses override these to express the A/B contrast
- [ ] Run — hooks exist; tests still fail (validate signature wrong)

**Notes:**

### Task 3.4: Change `validate` signature [Complex]
**File:** `combat_lab/scenarios/templates.py`
**Tests:** `pytest tests/unit/combat_lab/scenarios/test_comparison_scenario.py -v`

- [ ] Change `validate` to accept `ab_outcome: ABBattleOutcome` (single argument)
- [ ] Remove the old signature accepting `(outcome, telemetry, baseline_outcome, baseline_telemetry)`
- [ ] Update ComparisonScenario's base `validate` to delegate if needed
- [ ] Run tests — validate accepts the new signature

**Notes:**

### Task 3.5: Delete `_run_baseline_battle` + `_run_validation` override [Complex]
**File:** `combat_lab/scenarios/templates.py`
**Tests:** `pytest tests/unit/combat_lab/ -n 12`

- [ ] Delete `_run_baseline_battle` method (L827)
- [ ] Delete `_run_validation` override (L1120-1166)
- [ ] Remove `self._baseline_*` attribute references throughout the class
- [ ] Remove role-remapping logic at L915-920
- [ ] Keep `ship_builder` with role tracking — that's orthogonal and not being removed here (PROJ-274 may address later)
- [ ] Run — some existing tests may FAIL (expected — Phase 5 migrates them)

**Notes:**

### Task 3.6: Visual-baseline mode reinstated [Medium]
**File:** `combat_lab/scenarios/templates.py`, `combat_lab/services/ab_battle_runner.py`
**Tests:** Manual

- [ ] Add `render_mode: Literal["both", "baseline_only", "variant_only", "none"] = "both"` parameter to `ABBattleRunner.run()`
- [ ] Plumb through to the UI caller (test_lab/screen.py or equivalent)
- [ ] Validation ALWAYS runs regardless of render mode
- [ ] Manual smoke: launch ComparisonScenario in UI; visual-baseline mode shows baseline rendering + post-battle validation output

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update plan.md
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-277 3`
