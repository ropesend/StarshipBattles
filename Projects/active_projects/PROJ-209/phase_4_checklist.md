# Phase 4: Decompose ShipStatsCalculator.calculate_stats (CC=26 → ~8)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-209 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract per-ability accumulator methods, targeting WarpJump block first
**Risk Level:** HIGH — many ability types, formula evaluation, damage model, most test coverage to validate against
**File:** `game/strategy/services/ship_stats_calculator.py`
**Existing Tests:** ~71 tests across 6 test files (excellent coverage)

## Review Findings Addressed
- CX-001: Warp Jump Handling is Highest CC Driver (Critical) — 31% of function CC
- CQ-011: Monolithic Accumulation Loop (Major, downgraded from Critical)
- DS-005: `_accumulate_component_stats` Does Not Decompose (Major, downgraded from Critical)
- CQ-012: Open/Closed Violation (Major)
- CQ-013: DRY Violation - Repeated Ability Processing (Major)
- CQ-014: Nested Conditional Complexity in WarpJump (Major)
- AR-07: Warp Jump Logic Embedded in Stats Calculator (Major)
- CX-006: ResourceConsumption Iterated Twice (Major)
- DS-006: WarpJump Block Highest-CC With No Targeted Extraction (Major)
- DS-007: Policy Pattern is Overengineered (Minor, downgraded) — use simple methods instead
- CQ-015: Data Clump - Formula Context (Major)
- TC-004: WarpJump Non-Dict Value Branch Untested (Critical)
- TC-010: vehicle_classes Context Never Tested (Major)

## Key Design Decision
**DO NOT** use the Policy/Registry pattern (DS-007). Extract simple private methods instead — achieves same CC reduction with zero architectural overhead. The ability set is fixed and known.

**DO NOT** extract `_accumulate_component_stats` as a single method (DS-005). This just relocates CC~20 without decomposing it.

**DO** extract per-ability accumulator methods that each handle one ability type.

---

## Tasks

### Task 4.1: Fill Test Gaps Before Decomposing [Simple]
- [ ] TC-004: Add tests for WarpJump ability as formula string `"=ship_class_mass"` and raw integer `5000`, verify tonnage calculated correctly
- [ ] TC-010: Add test with non-empty `vehicle_classes` dict and component using formula referencing `ship_class_mass`
- [ ] TC-013: Add test with modifier that sets `consumption_mult`, verify consumption values are scaled
- [ ] Run: `pytest tests/unit/strategy/ship_stats/ -v`
- [ ] Verify all new + existing tests pass

### Task 4.2: Extract `_accumulate_warp_stats` [Medium]
Lines 252-284: the single biggest CC driver (CC~7, 31% of total). **Do this first.**

- [ ] Create `_accumulate_warp_stats(abilities, comp_id, comp_def, component_damage, formula_context, effectiveness) -> Tuple[int, Dict[str, float]]`
- [ ] Returns `(warp_tonnage_contribution, warp_cost_contribution)`
- [ ] Move warp_effectiveness check, tonnage evaluation (dict + non-dict paths), and warp ResourceConsumption iteration inside
- [ ] Refactor the ternary chain (CX-008/CQ-014): replace with `_parse_warp_tonnage(warp_data, formula_context)` or use `_evaluate_value` directly
- [ ] Estimated CC: ~5
- [ ] Add targeted unit tests for warp accumulation
- [ ] Verify: all 71 existing tests still pass

### Task 4.3: Extract `_accumulate_resource_storage` [Simple]
Lines 200-210: ResourceStorage ability loop.

- [ ] Create `_accumulate_resource_storage(abilities, effectiveness, capacity_mult, formula_context, storage_dict) -> None`
- [ ] Mutates `storage_dict` in-place (accumulates values)
- [ ] Estimated CC: ~3
- [ ] Verify: all tests still pass

### Task 4.4: Extract `_accumulate_cargo_storage` [Simple]
Lines 213-222: CargoStorage ability loop. Nearly identical pattern to ResourceStorage.

- [ ] Create `_accumulate_cargo_storage(abilities, effectiveness, capacity_mult, formula_context, cargo_dict) -> None`
- [ ] Estimated CC: ~3
- [ ] Verify: all tests still pass

### Task 4.5: Extract `_accumulate_consumption` [Simple]
Lines 234-249: ResourceConsumption with trigger dispatch. Unifies the per_hex/per_turn triggers.

- [ ] Create `_accumulate_consumption(abilities, effectiveness, consumption_mult, formula_context, per_hex_dict, per_turn_dict) -> None`
- [ ] Handles both `strategic_per_hex` and `per_turn` triggers
- [ ] Does NOT handle `warp_jump` trigger (that's in `_accumulate_warp_stats`)
- [ ] Estimated CC: ~3
- [ ] Verify: all tests still pass

### Task 4.6: Extract `_accumulate_movement` [Simple]
Lines 225-228: StrategicMovement ability.

- [ ] Create `_accumulate_movement(abilities, effectiveness, formula_context, multipliers) -> float`
- [ ] Returns movement value
- [ ] Estimated CC: ~2
- [ ] Verify: all tests still pass

### Task 4.7: Simplify `calculate_stats` Main Loop [Medium]
Rewrite the per-component loop body to call extracted accumulators.

- [ ] Main loop becomes: for each component → get abilities → call each accumulator
- [ ] Toggle-off shortcut (mass only) stays inline (simple, 2 lines)
- [ ] HP/mass accumulation stays inline (simple, no branching)
- [ ] Verify orchestrator CC <= 8
- [ ] Consider introducing a `StatsAccumulator` dataclass to bundle the 8 accumulator variables (CX-013) — optional, only if it improves readability
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Verify: all 7353+ tests pass, 0 failures

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `calculate_stats` orchestrator CC <= 8
- [ ] All extracted accumulators CC <= 5
- [ ] WarpJump non-dict path tested (TC-004)
- [ ] vehicle_classes formula context tested (TC-010)
- [ ] All 71+ ship stats tests pass
- [ ] All tests pass (full suite)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "All phases complete — ready for audit"
