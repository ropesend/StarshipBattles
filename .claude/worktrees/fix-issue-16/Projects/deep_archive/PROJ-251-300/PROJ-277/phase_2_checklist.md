# Phase 2: Implement ABBattleRunner

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-277 2`

**Status:** Complete
**Objective:** Implement the runner such that Phase 1 tests pass.

---

## Tasks

### Task 2.1: Implement `_run_one` [Medium]
**File:** `combat_lab/services/ab_battle_runner.py`
**Tests:** `pytest tests/unit/combat_lab/services/test_ab_battle_runner.py -v`

- [x] `_run_one` builds a kwargs dict forwarding the stored `ai_factory` + optional `ship_builder` / `pre_tick_loop_callback` / `per_tick_callback` to `run_battle`
- [x] Returns `(outcome, CombatLabTelemetry())` tuple
- [x] Deviation from design sketch: sketch used `per_tick_callback=telemetry.on_tick` but `CombatLabTelemetry` is frozen with no `on_tick` method. Minimal implementation returns an empty telemetry; Phase 3's `ComparisonScenario` integration wires actual role-tracking via a scenario-supplied `per_tick_callback` that closes over a `ships_by_role` dict (same pattern as `scenario_run_helper.py`).
- [x] All 5 mock-based `run()` tests pass

**Notes:** Chose explicit kwargs forwarding rather than passing `None` for unused callbacks — keeps `run_battle`'s defaults clean and makes the mock assertion `call.kwargs["ship_builder"] is ship_builder` pass only when actually forwarded.

### Task 2.2: Implement `run` [Simple]
**File:** `combat_lab/services/ab_battle_runner.py`
**Tests:** `pytest tests/unit/combat_lab/services/test_ab_battle_runner.py -v`

- [x] `run` calls `_run_one(baseline_spec)` then `_run_one(variant_spec)`
- [x] Constructs and returns `ABBattleOutcome(baseline_outcome=..., baseline_telemetry=..., variant_outcome=..., variant_telemetry=...)`
- [x] All 6 Phase-1 tests pass

**Notes:**

### Task 2.3: Parity test — manual two-run equivalence [Medium]
**File:** `tests/unit/combat_lab/services/test_ab_battle_runner.py`
**Tests:** `pytest tests/unit/combat_lab/services/test_ab_battle_runner.py::test_parity -v`

- [x] `test_parity_identical_specs_produce_identical_outcomes` constructs two structurally identical `BattleSpec`s with the same seed (4242), runs through `ABBattleRunner` with a real `ship_builder` that loads a minimal Escort design
- [x] Asserts `duration_ticks`, `end_reason`, and the set of ship `instance_id`s match between baseline and variant outcomes
- [x] Passes — confirms runner-level determinism; no seed bleed-through between baseline and variant runs

**Notes:** Telemetry-content assertion in the task description was skipped — `CombatLabTelemetry` only carries `in_flight_by_role` today, which is always empty under the Phase-2 minimal implementation. Phase 3 will add a proper telemetry-content parity check once role-tracking is wired.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update plan.md
- [x] Run `python Projects/scripts/validate_phase.py PROJ-277 2`
