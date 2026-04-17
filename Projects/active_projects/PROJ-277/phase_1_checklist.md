# Phase 1: Design A/B Runner + DTO + Failing Tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-277 1`
> 2. Only proceed if output shows PASSED

**Status:** Not Started
**Objective:** Define `ABBattleOutcome` DTO and `ABBattleRunner` interface. Write comprehensive failing tests before implementation.

---

## Tasks

### Task 1.1: Create `ABBattleOutcome` DTO [Simple]
**File:** `combat_lab/scenarios/ab_outcome.py` (NEW)
**Tests:** N/A (scaffold)

- [ ] Create module with docstring explaining A/B pairing
- [ ] Define `@dataclass(frozen=True) class ABBattleOutcome` with fields: `baseline_outcome: BattleOutcome`, `baseline_telemetry: CombatLabTelemetry`, `variant_outcome: BattleOutcome`, `variant_telemetry: CombatLabTelemetry`
- [ ] Exports: add to module `__init__.py` if relevant

**Notes:**

### Task 1.2: Create `ABBattleRunner` skeleton [Simple]
**File:** `combat_lab/services/ab_battle_runner.py` (NEW)
**Tests:** N/A (scaffold)

- [ ] Create module with docstring
- [ ] Define class `ABBattleRunner` with constructor accepting `ai_factory, ship_builder=None`
- [ ] Define `run(baseline_spec, variant_spec) -> ABBattleOutcome` method — stub raises NotImplementedError
- [ ] Define private helper `_run_one(spec) -> Tuple[BattleOutcome, CombatLabTelemetry]` — stub

**Notes:**

### Task 1.3: Write failing tests [Medium]
**File:** `tests/unit/combat_lab/services/test_ab_battle_runner.py` (NEW)
**Tests:** `pytest tests/unit/combat_lab/services/test_ab_battle_runner.py -v`

- [ ] Test: `ABBattleRunner.run(baseline, variant)` calls `run_battle` exactly twice
- [ ] Test: returned `ABBattleOutcome` has matching outcomes (baseline first, variant second)
- [ ] Test: each `run_battle` call uses the provided `ai_factory` and `ship_builder`
- [ ] Test: telemetry captured separately for each run (no remapping; use identical role keys in both)
- [ ] Test: a `ship_builder` override is forwarded to both calls
- [ ] Test: `ABBattleOutcome` is frozen (mutation raises FrozenInstanceError)
- [ ] Run — all fail (stub returns nothing)

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update plan.md
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-277 1`
