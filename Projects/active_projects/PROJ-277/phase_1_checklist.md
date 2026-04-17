# Phase 1: Design A/B Runner + DTO + Failing Tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-277 1`
> 2. Only proceed if output shows PASSED

**Status:** Complete
**Objective:** Define `ABBattleOutcome` DTO and `ABBattleRunner` interface. Write comprehensive failing tests before implementation.

---

## Tasks

### Task 1.1: Create `ABBattleOutcome` DTO [Simple]
**File:** `combat_lab/scenarios/ab_outcome.py` (NEW)
**Tests:** N/A (scaffold)

- [x] Module created with docstring explaining the A/B pairing contract and why it replaces `_baseline_*` attribute stashing
- [x] `@dataclass(frozen=True) class ABBattleOutcome` defined with all 4 fields: `baseline_outcome`, `baseline_telemetry`, `variant_outcome`, `variant_telemetry`
- [x] `__all__ = ["ABBattleOutcome"]` exported

**Notes:** DTO is intentionally minimal — no computed properties yet. Convenience helpers (e.g. `ab.get_role_outcome("variant", "attacker")`) are deferred until Phase 3 shows a clear need.

### Task 1.2: Create `ABBattleRunner` skeleton [Simple]
**File:** `combat_lab/services/ab_battle_runner.py` (NEW)
**Tests:** N/A (scaffold)

- [x] Module created with docstring
- [x] `ABBattleRunner.__init__` accepts `ai_factory` + optional `ship_builder`, `pre_tick_loop_callback`, `per_tick_callback` — the full set of hooks `run_battle` exposes, so scenarios that need role-tracking can route through the runner unchanged
- [x] `run(baseline_spec, variant_spec) -> ABBattleOutcome` stub raises NotImplementedError
- [x] `_run_one(spec) -> Tuple[BattleOutcome, CombatLabTelemetry]` stub raises NotImplementedError
- [x] `run_battle` imported so Phase 1 tests can patch the module-level binding

**Notes:** Extended the design's 2-param constructor to include `pre_tick_loop_callback` + `per_tick_callback` after reading `scenario_run_helper.py`. ComparisonScenario's current ship_builder already relies on both hooks to populate `ships_by_role` and `in_flight_by_role`. Phase 3 will decide whether to inline that bookkeeping into the runner or keep it scenario-side.

### Task 1.3: Write failing tests [Medium]
**File:** `tests/unit/combat_lab/services/test_ab_battle_runner.py` (NEW)
**Tests:** `pytest tests/unit/combat_lab/services/test_ab_battle_runner.py -v`

- [x] `test_run_calls_run_battle_exactly_twice` — asserts 2 invocations
- [x] `test_run_order_is_baseline_then_variant` — asserts first call's spec is baseline, second's is variant
- [x] `test_run_returns_ab_battle_outcome_with_paired_results` — outcome identity is preserved into the DTO
- [x] `test_run_forwards_ai_factory_and_ship_builder_to_both_calls` — both runs get identical plumbing so telemetry role keys match
- [x] `test_run_captures_separate_telemetry_per_run` — baseline and variant telemetry are distinct `CombatLabTelemetry` instances
- [x] `test_ab_battle_outcome_is_frozen` — DTO is immutable
- [x] Run — 5 fail (`NotImplementedError: Phase 2 implements run()`), 1 passes (DTO frozen check)

**Notes:** TDD-red confirmed. The single passing test exercises only the DTO, not the runner stub.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update plan.md
- [x] Run `python Projects/scripts/validate_phase.py PROJ-277 1`
