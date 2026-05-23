# Phase 3: CAT-10 parametrize (core)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-495 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Parametrize structurally-identical clusters in core-mechanical tests. Inherited from PROJ-480 Phase 3 — the largest single phase (~20 tasks).

Line refs advisory — Phase 0 should have refreshed them. Re-grep before editing.

---

## Tasks

### Task 3.1: test_deprecated_code_removed.py — 4+4 deletion guards
**File:** `tests/regression/test_deprecated_code_removed.py`
**Tests:** `pytest tests/regression/test_deprecated_code_removed.py`
**Origin:** PROJ-480 T3.3

- [ ] Parametrize the 4 identical hasattr-deletion-guard tests (PROJ-480 cited lines 12-34) and the 4 more (PROJ-480 cited lines 45-67).
- [ ] Verify: passes; LOC delta ≈ -30.

### Task 3.2: test_engine_event_emission.py — 9 event-emission tests
**File:** `tests/unit/strategy/test_engine_event_emission.py`
**Tests:** `pytest tests/unit/strategy/test_engine_event_emission.py`
**Origin:** PROJ-480 T3.6

- [ ] Parametrize the 9 event-emission tests across 3 classes (4 spawn_ship variants + 2 fleet variants + 3 complex variants, PROJ-480 cited lines 108-339) on `(spawn_method, input_params, expected_event_kwargs)`.
- [ ] Verify: passes; LOC delta ≈ -100.

### Task 3.3: test_squadron_characterization.py — 5 roundtrip tests
**File:** `tests/unit/strategy/data/test_squadron_characterization.py`
**Tests:** `pytest tests/unit/strategy/data/test_squadron_characterization.py`
**Origin:** PROJ-480 T3.7

- [ ] Parametrize the 5 `test_round_trip_*` methods (PROJ-480 cited lines 113-172) on `(squadron_kwargs, assert_fn)`.
- [ ] Verify: passes; LOC delta ≈ -45.

### Task 3.4: test_ship_physics.py — 4 heading/velocity tests
**File:** `tests/unit/simulation/entities/test_ship_physics.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_physics.py`
**Origin:** PROJ-480 T3.8

- [ ] Parametrize the 4 velocity-by-angle tests (PROJ-480 cited lines 344-387) on `(angle, expected_x, expected_y)`.
- [ ] Verify: passes; LOC delta ≈ -25.

### Task 3.5: test_cooldowns.py — 5 shield regen tests
**File:** `tests/unit/simulation/ship_combat_engine/test_cooldowns.py`
**Tests:** `pytest tests/unit/simulation/ship_combat_engine/test_cooldowns.py`
**Origin:** PROJ-480 T3.9

- [ ] Parametrize the 5 shield-regen tests (PROJ-480 cited lines 58-145) on `(initial_shields, max, regen_rate, ticks, expected_shields)`.
- [ ] Verify: passes; LOC delta ≈ -50.

### Task 3.6: test_invalid_operation_handling.py — 4 multiply/add/set/add_to_mult bodies
**File:** `tests/unit/modifiers/test_invalid_operation_handling.py`
**Tests:** `pytest tests/unit/modifiers/test_invalid_operation_handling.py`
**Origin:** PROJ-480 T3.11

- [ ] Parametrize the 4 identical bodies (PROJ-480 cited lines 77-103) on operation type.
- [ ] Verify: passes; LOC delta ≈ -18.

### Task 3.7: test_ship_fleet_attrs.py — 2 test pairs
**File:** `tests/unit/simulation/entities/test_ship_fleet_attrs.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_fleet_attrs.py`
**Origin:** PROJ-480 T3.17

- [ ] Parametrize the 2 test pairs (PROJ-480 cited lines 16-56) on `(attr_name, expected_value)`.
- [ ] Verify: passes; LOC delta ≈ -18.

### Task 3.8: test_destination_path.py — 3 NavigationState tests
**File:** `tests/unit/strategy/fleet_navigation/test_destination_path.py`
**Tests:** `pytest tests/unit/strategy/fleet_navigation/test_destination_path.py`
**Origin:** PROJ-480 T3.18

- [ ] Extract NavigationState construction (3 identical-except-orders setups, PROJ-480 cited lines 19-78) into a parametrized fixture.
- [ ] Verify: passes; LOC delta ≈ -25.

### Task 3.9: test_production_engine_queue.py — 2 resources_consumed tests
**File:** `tests/unit/strategy/engine/test_production_engine_queue.py`
**Tests:** `pytest tests/unit/strategy/engine/test_production_engine_queue.py`
**Origin:** PROJ-480 T3.24

- [ ] Parametrize the 2 tests (colony+fleet, PROJ-480 cited lines 125-259) asserting `item["resources_consumed"]["A"] == 0.0` — note setup differs nontrivially; document.
- [ ] Verify: passes; LOC delta ≈ -15.

### Task 3.10: test_planet_energy_engine.py — 4 generator/cap/no-gen/shield-drain
**File:** `tests/unit/strategy/engine/test_planet_energy_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_planet_energy_engine.py`
**Origin:** PROJ-480 T3.25

- [ ] Parametrize the 4 tests at PROJ-480-cited lines 211-269.
- [ ] Verify: passes; LOC delta ≈ -40.

### Task 3.11: test_fleet_dto.py — 2 immutable-tuple tests
**File:** `tests/unit/strategy/facade/test_fleet_dto.py`
**Tests:** `pytest tests/unit/strategy/facade/test_fleet_dto.py`
**Origin:** PROJ-480 T3.27

- [ ] Merge the 2 tests (PROJ-480 cited lines 192-269) into one parametrized test covering both construction sources.
- [ ] Verify: passes; LOC delta ≈ -25.

### Task 3.12: test_ship_serialization.py — 5 roundtrip tests
**File:** `tests/unit/simulation/entities/test_ship_serialization.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_serialization.py`
**Origin:** PROJ-480 T3.28

- [ ] Parametrize the 5 roundtrip tests (PROJ-480 cited lines 328-419) on field name. _(coordination note: tied to DUP-003 cross-shard in PROJ-479 Phase 5; do P1's narrowed plan first.)_
- [ ] Verify: passes; LOC delta ≈ -35.

### Task 3.13: test_fleet_pursuer_tracker.py — 3 setup-shared tests
**File:** `tests/unit/strategy/fleet/test_fleet_pursuer_tracker.py` (retargeted from PROJ-480's `tests/unit/strategy/services/`)
**Tests:** `pytest tests/unit/strategy/fleet/test_fleet_pursuer_tracker.py`
**Origin:** PROJ-480 T3.35

- [ ] Parametrize the 3 tests (PROJ-480 cited lines 387-445; Codex spot-check 2026-05-23 saw cluster at `:398, :418, :440`) — same setup, assertion target varies.
- [ ] Verify: passes; LOC delta ≈ -20.

### Task 3.14: test_warp_resources.py — 3 warp_resource_costs tests
**File:** `tests/unit/strategy/fleet/test_warp_resources.py`
**Tests:** `pytest tests/unit/strategy/fleet/test_warp_resources.py`
**Origin:** PROJ-480 T3.39

- [ ] Parametrize the 3 warp_resource_costs tests (PROJ-480 cited lines 41-71) on `(ship_config, expected_costs)`.
- [ ] Verify: passes; LOC delta ≈ -25.

### Task 3.15: test_superweapon_order_processor_gaps.py — 5 TestStabilizerCancellation tests
**File:** `tests/unit/strategy/engine/test_superweapon_order_processor_gaps.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_order_processor_gaps.py`
**Origin:** PROJ-480 T3.42

- [ ] Parametrize the 5 tests (PROJ-480 cited lines 118-272) on `(processor_method, expected_order_type, target_setup)`.
- [ ] Verify: passes; LOC delta ≈ -60.

### Task 3.16: test_tick_phases.py — 3 registry read tests
**File:** `tests/unit/simulation/systems/test_tick_phases.py`
**Tests:** `pytest tests/unit/simulation/systems/test_tick_phases.py`
**Origin:** PROJ-480 T3.44

- [ ] Parametrize the 3 structurally identical registry read tests (PROJ-480 cited lines 74-124).
- [ ] Verify: passes; LOC delta ≈ -20.

### Task 3.17: test_superweapon_command_handlers.py — 5 handler test cluster
**File:** `tests/unit/strategy/engine/test_superweapon_command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_command_handlers.py`
**Origin:** PROJ-480 T3.46

- [ ] Parametrize the 5 handler-class `test_execute_adds_correct_order_type` tests (PROJ-480 cited lines 163-331) on `(handler_cls, expected_order_type, expected_target_shape)`.
- [ ] Verify: passes; LOC delta ≈ -60.

### Task 3.18: test_superweapon_validator.py — 5 validator-class clusters
**File:** `tests/unit/strategy/validation/test_superweapon_validator.py`
**Tests:** `pytest tests/unit/strategy/validation/test_superweapon_validator.py`
**Origin:** PROJ-480 T3.47

- [ ] Parametrize the 5 validator-class valid/invalid-no-ability/invalid-bad-location patterns (PROJ-480 cited lines 228-651) on `(validator_method, setup_func, valid_assertion, invalid_assertions)`.
- [ ] Verify: passes; LOC delta ≈ -150.

### Task 3.19: test_empire_validation.py — 3 missing-field tests
**File:** `tests/unit/strategy/empire/test_empire_validation.py`
**Tests:** `pytest tests/unit/strategy/empire/test_empire_validation.py`
**Origin:** PROJ-480 T3.48

- [ ] Parametrize the 3 missing-field PersistenceException tests (PROJ-480 cited lines 41-72) on `missing_key`.
- [ ] Verify: passes; LOC delta ≈ -25.

### Task 3.20: test_base_command_handler.py — 2 resolve_fleet tests
**File:** `tests/unit/strategy/engine/test_base_command_handler.py`
**Tests:** `pytest tests/unit/strategy/engine/test_base_command_handler.py`
**Origin:** PROJ-480 T3.49

- [ ] Parametrize the 2 tests (PROJ-480 cited lines 44-68) on `(fleet_setup_func, expected_error_substring)`.
- [ ] Verify: passes; LOC delta ≈ -10.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4 (CAT-11/12)
