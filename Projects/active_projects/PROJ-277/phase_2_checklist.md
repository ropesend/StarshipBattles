# Phase 2: Implement ABBattleRunner

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-277 2`

**Status:** Not Started
**Objective:** Implement the runner such that Phase 1 tests pass.

---

## Tasks

### Task 2.1: Implement `_run_one` [Medium]
**File:** `combat_lab/services/ab_battle_runner.py`
**Tests:** `pytest tests/unit/combat_lab/services/test_ab_battle_runner.py -v`

- [ ] Create a `CombatLabTelemetry()` instance
- [ ] Call `run_battle(spec, ai_factory=self._ai_factory, ship_builder=self._ship_builder, per_tick_callback=telemetry.on_tick)`
- [ ] Return `(outcome, telemetry)` tuple
- [ ] Run tests — some pass

**Notes:**

### Task 2.2: Implement `run` [Simple]
**File:** `combat_lab/services/ab_battle_runner.py`
**Tests:** `pytest tests/unit/combat_lab/services/test_ab_battle_runner.py -v`

- [ ] Call `_run_one(baseline_spec)` → `(baseline_outcome, baseline_telemetry)`
- [ ] Call `_run_one(variant_spec)` → `(variant_outcome, variant_telemetry)`
- [ ] Construct and return `ABBattleOutcome(baseline_outcome, baseline_telemetry, variant_outcome, variant_telemetry)`
- [ ] Run tests — all pass

**Notes:**

### Task 2.3: Parity test — manual two-run equivalence [Medium]
**File:** `tests/unit/combat_lab/services/test_ab_battle_runner.py`
**Tests:** `pytest tests/unit/combat_lab/services/test_ab_battle_runner.py::test_parity -v`

- [ ] Construct identical baseline and variant specs (same seed)
- [ ] Run through ABBattleRunner
- [ ] Assert `baseline_outcome.duration_ticks == variant_outcome.duration_ticks` (deterministic)
- [ ] Assert `baseline_telemetry.ship_stats` matches `variant_telemetry.ship_stats` (no role remapping; same role keys)
- [ ] Run — passes

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update plan.md
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-277 2`
