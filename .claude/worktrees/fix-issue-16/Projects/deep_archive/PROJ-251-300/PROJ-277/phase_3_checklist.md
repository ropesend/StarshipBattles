# Phase 3: Refactor ComparisonScenario

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-277 3`

**Status:** Partial (validate signature migrated; _run_baseline_battle scaffolding deletion + render_mode deferred to Phase 4)
**Objective:** Remove embedded `run_battle` call + telemetry role-remapping + visual-baseline validate bypass. Introduce clean `build_baseline_spec` / `build_variant_spec` hooks.

---

## Tasks

### Task 3.1: Inventory existing ComparisonScenario API [Simple]
**File:** `combat_lab/scenarios/templates.py`
**Tests:** N/A (read-only)

- [x] Read `ComparisonScenario` class end-to-end (L736-1210 actually, plus `_compile_comparison` at `spec_compiler.py:394-446`)
- [x] Listed all methods + `self._baseline_*` stashed attributes
- [x] Documented in `findings/comparison_scenario_audit.md`
- [x] Identified external callers: `_run_validation` is called from base `TestScenario` → all 98 `ComparisonScenario` subclasses override `validate(self, outcome, telemetry=None)` with the legacy signature.

**Notes:** Key finding: baseline vs variant is expressed as DIFFERENT SHIP DESIGNS (`baseline_*_ship` vs `variant_*_ship` class attrs), not "strip a modifier from a common spec". So the design.md sketch `build_baseline_spec(base_spec)` signature is misaligned with reality. The hooks must take NO argument and each produce a complete spec. 98 subclasses all reference `self.baseline_*` / `self.variant_*` attrs in `validate()` — Phase 5 will migrate them.

### Task 3.3: Add `build_baseline_spec` / `build_variant_spec` hooks [Medium]
**File:** `combat_lab/scenarios/templates.py`
**Tests:** `pytest tests/unit/combat_lab/scenarios/test_comparison_scenario.py -v`

- [x] Added `build_baseline_spec(self) -> BattleSpec` — default delegates to `_build_baseline_battle_spec()`
- [x] Added `build_variant_spec(self) -> BattleSpec` — default calls `to_spec()` with `_visual_baseline` temporarily forced False, then restores the prior flag value
- [x] Added docstrings explaining: hooks are the target API for Phase 4's `ABBattleRunner`; defaults preserve current behavior; subclasses can override to express contrasts as spec transformations
- [x] Non-breaking: 288 existing combat_lab unit tests still pass

**Notes:** Hook signature deviates from design.md sketch (which took a `base_spec` param). Reality: each hook produces a full spec from scenario config. Phase 4's `ABBattleRunner.run()` will invoke these hooks directly; Phase 5 deletes `_run_baseline_battle` + `_build_baseline_battle_spec` once subclasses are migrated.

### Task 3.2: Write failing test for new API [Medium]
**File:** `tests/unit/combat_lab/scenarios/test_comparison_scenario.py`
**Tests:** `pytest tests/unit/combat_lab/scenarios/test_comparison_scenario.py -v`

- [x] 7 tests covering the new hooks only (not validate signature — that's Task 3.4 territory):
  - `test_returns_battle_spec` ×2 (baseline, variant)
  - `test_default_uses_baseline_ship_designs` / `test_default_uses_variant_ship_designs` — assert the right `design_id` appears in the spec's ships
  - `test_restores_visual_baseline_flag_after_call` — hook's internal flag toggling must not leak
  - `test_subclass_can_override` ×2
- [x] All 7 pass after hooks implemented in 3.3
- [x] Scoped narrowly to new API; didn't exercise the validate-signature change or legacy-method deletion (those are Tasks 3.4 / 3.5)

**Notes:** Tests use a real `TestMetadata` (not MagicMock) because `_build_baseline_battle_spec` and `_compile_comparison` reach into metadata for `test_id`, `max_ticks`, and `end_condition`.

### Task 3.4: Change `validate` signature [Complex]
**File:** `combat_lab/scenarios/templates.py`
**Tests:** `pytest tests/unit/combat_lab/scenarios/test_comparison_scenario.py -v`

- [x] Added a new default `ComparisonScenario.validate(self, ab)` that returns `self._template_preconditions()`. Subclasses override with their specific checks.
- [x] Rewrote `_run_validation` to build an `ABBattleOutcome` from stashed baseline + current (outcome, telemetry) and call `validate(ab)`. Normal-mode path now matches the PROJ-277 contract.
- [x] Visual-baseline bypass kept (preconditions only) pending Task 3.6 — noted in-line so future readers see it's a scaffolding decision, not a silent bypass.
- [x] Bulk-migrated all 102 ComparisonScenario descendant classes via AST-aware script; 103 validate signatures rewritten.
- [x] Updated the `test_comparison_visual_baseline.py` regression test's dummy subclass + added `_baseline_outcome` stash expectation for the normal-mode test.
- [x] All 288 combat_lab unit tests pass; all 170 Combat Lab scenario-runner tests pass.

**Notes:** Migration script was a one-off (deleted after use). Grep confirms no remaining `def validate(self, outcome, telemetry=None)` inside ComparisonScenario subclasses — every override now takes `(self, ab)`.

### Task 3.5: Delete `_run_baseline_battle` + `_run_validation` override [Complex]
**File:** `combat_lab/scenarios/templates.py`
**Tests:** `pytest tests/unit/combat_lab/ -n 12`

- [x] `_run_validation` override REWRITTEN (not deleted) — it now builds an `ABBattleOutcome` instead of bypassing validate in VB mode. This is the PROJ-277 contract and lives on the base ComparisonScenario.
- [ ] `_run_baseline_battle` KEPT for now — it's the stepping stone that produces `self._baseline_outcome` / `self._baseline_telemetry` that `_run_validation` reads. Deletion is blocked on Phase 4 (runner dispatch calls `ABBattleRunner.run(baseline_spec, variant_spec)` directly, eliminating the scenario-driven baseline run).
- [x] Role-remapping logic (`"baseline_attacker"` telemetry keys) stays inside `_run_baseline_battle` for now — same reason; Phase 4 eliminates it.
- [x] Visual-baseline bypass still present in `_run_validation`; proper fix is Task 3.6.

**Notes:** The CLEAN-SHEET deletion of `_run_baseline_battle` + `_build_baseline_battle_spec` is a Phase 4 concern, not Phase 3. Keeping them scaffolds the migration: today's production path still works; Phase 4 just switches who calls `run_battle` (scenario → runner).

### Task 3.6: Visual-baseline mode reinstated [Medium]
**File:** `combat_lab/scenarios/templates.py`, `combat_lab/services/ab_battle_runner.py`
**Tests:** Manual

- [ ] **DEFERRED to Phase 4** — depends on runner dispatch landing. The `render_mode` flag routes which battle is rendered visually; both battles always run + validate. No scaffold possible today because the runner is not yet driving the two runs.

**Notes:**

---

## Phase Completion Checklist
- [x] All SAFE task checkboxes above are checked (3.1, 3.2, 3.3)
- [x] Update plan.md — mark phase as Partial with clear handoff
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-277 3`  — will report partial; deferred tasks 3.4/3.5/3.6 remain unchecked by design

---

## Handoff: how to resume (next session)

**Atomic swap plan for Tasks 3.4 + 3.5 + Phase 5 subclass migration:**

1. Change `ComparisonScenario.validate` signature to `validate(self, ab: ABBattleOutcome) -> list`.
2. Keep `collect_results` populating `self.baseline_*` / `self.variant_*` attrs — but drive them from `ab.baseline_outcome` / `ab.variant_outcome` instead of the `_baseline_*` stash.
3. Migrate all 98 subclasses: change their `def validate(self, outcome, telemetry=None)` → `def validate(self, ab)`. Bodies reference `self.baseline_*` / `self.variant_*` which keep working. Only the signature changes in most cases.
4. Delete `_run_baseline_battle`, `_run_validation` override, `_build_baseline_battle_spec` (or rename to `_default_baseline_spec` if kept as the default-hook backing), `_baseline_*` attribute refs.
5. Delete role-remapping (`"baseline_attacker"` keys) — the new `collect_results(ab)` uses `ab.baseline_telemetry` / `ab.variant_telemetry` which have their own role-key spaces.

Phase 4 (runner dispatch) can proceed in parallel but lands AFTER this atomic swap: `run_scenario` checks `isinstance(scenario, ComparisonScenario)`, calls `scenario.build_baseline_spec()` / `build_variant_spec()`, feeds to `ABBattleRunner.run()`, then `scenario.validate(ab)`.
