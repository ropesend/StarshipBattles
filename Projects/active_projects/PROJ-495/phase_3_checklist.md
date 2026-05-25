# Phase 3: CAT-10 parametrize (core)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-495 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Parametrize structurally-identical clusters in core-mechanical tests. Inherited from PROJ-480 Phase 3 — the largest single phase (~20 tasks).

Line refs advisory — Phase 0 should have refreshed them. Re-grep before editing.

---

## Tasks

### Task 3.1: test_deprecated_code_removed.py — 4+4 deletion guards
**File:** `tests/regression/test_deprecated_code_removed.py`
**Tests:** `pytest tests/regression/test_deprecated_code_removed.py`
**Origin:** PROJ-480 T3.3

- [x] Parametrize the 4 identical hasattr-deletion-guard tests (PROJ-480 cited lines 12-34) and the 4 more (PROJ-480 cited lines 45-67).
- [x] Verify: passes (16 tests); LOC delta ≈ -30.

### Task 3.2: test_engine_event_emission.py — 9 event-emission tests
**File:** `tests/unit/strategy/test_engine_event_emission.py`
**Tests:** `pytest tests/unit/strategy/test_engine_event_emission.py`
**Origin:** PROJ-480 T3.6

- [~] **DROPPED (out of scope):** the 9 tests span 3 distinct spawn methods (`_spawn_ship`, `_spawn_fleet_ship`, `_create_and_place_facility`) with substantively different mock-setup (`patch.multiple` for ShipInstance+Fleet vs single patch vs no patch). Parametrize would require per-row setup-builder functions equivalent to the original bodies.

### Task 3.3: test_squadron_characterization.py — 5 roundtrip tests
**File:** `tests/unit/strategy/data/test_squadron_characterization.py`
**Tests:** `pytest tests/unit/strategy/data/test_squadron_characterization.py`
**Origin:** PROJ-480 T3.7

- [~] **DROPPED (out of scope):** each test asserts on a different attribute (battle_role enum, combat_policy fields, spatial_behavior strings, flagship_id, omitted-optional defaults). Parametrizing on `(squadron_kwargs, assert_fn)` would require 5 distinct lambdas roughly the size of the current test bodies.
- **Phase 5 follow-through (2026-05-23):** 3 of 5 single-attribute roundtrips parametrized (Phase 5); combat_policy (multi-level nested asserts) and default-fields (different contract) kept distinct.

### Task 3.4: test_ship_physics.py — 4 heading/velocity tests
**File:** `tests/unit/simulation/entities/test_ship_physics.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_physics.py`
**Origin:** PROJ-480 T3.8

- [x] Parametrize the 4 velocity-by-angle tests (PROJ-480 cited lines 344-387) on `(angle, expected_x, expected_y)`.
- [x] Verify: passes (41 tests); LOC delta ≈ -25.

### Task 3.5: test_cooldowns.py — 5 shield regen tests
**File:** `tests/unit/simulation/ship_combat_engine/test_cooldowns.py`
**Tests:** `pytest tests/unit/simulation/ship_combat_engine/test_cooldowns.py`
**Origin:** PROJ-480 T3.9

- [x] Parametrize the 5 shield-regen tests (PROJ-480 cited lines 58-145) on `(initial_shields, max, regen_rate, ticks, expected_shields)`.
- [x] Verify: passes (34 tests); LOC delta ≈ -50.

### Task 3.6: test_invalid_operation_handling.py — 4 multiply/add/set/add_to_mult bodies
**File:** `tests/unit/modifiers/test_invalid_operation_handling.py`
**Tests:** `pytest tests/unit/modifiers/test_invalid_operation_handling.py`
**Origin:** PROJ-480 T3.11

- [x] Parametrize the 4 identical bodies (PROJ-480 cited lines 77-103) on operation type.
- [x] Verify: passes (11 tests); LOC delta ≈ -18.

### Task 3.7: test_ship_fleet_attrs.py — 2 test pairs
**File:** `tests/unit/simulation/entities/test_ship_fleet_attrs.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_fleet_attrs.py`
**Origin:** PROJ-480 T3.17

- [x] Parametrize the 2 test pairs (PROJ-480 cited lines 16-56) on `(attr_name, expected_value)`.
- [x] Verify: passes (4 tests); LOC delta ≈ -18.

### Task 3.8: test_destination_path.py — 3 NavigationState tests
**File:** `tests/unit/strategy/fleet_navigation/test_destination_path.py`
**Tests:** `pytest tests/unit/strategy/fleet_navigation/test_destination_path.py`
**Origin:** PROJ-480 T3.18

- [x] Extract NavigationState construction (3 identical-except-orders setups, PROJ-480 cited lines 19-78) into a parametrized test on `(make_order, expected_factory, label)`.
- [x] Verify: passes (13 tests); LOC delta ≈ -25.

### Task 3.9: test_production_engine_queue.py — 2 resources_consumed tests
**File:** `tests/unit/strategy/engine/test_production_engine_queue.py`
**Tests:** `pytest tests/unit/strategy/engine/test_production_engine_queue.py`
**Origin:** PROJ-480 T3.24

- [~] **DROPPED (out of scope):** setup differs nontrivially (colony-pause vs fleet-pause paths); the task's own description acknowledged this. Parametrize would re-introduce both setups via builder functions equivalent to the originals.

### Task 3.10: test_planet_energy_engine.py — 4 generator/cap/no-gen/shield-drain
**File:** `tests/unit/strategy/engine/test_planet_energy_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_planet_energy_engine.py`
**Origin:** PROJ-480 T3.25

- [~] **DROPPED (out of scope):** each test has materially different setup (generator+battery, generator-only, battery-only, shield+battery+component_state). Parametrize would need per-case factory functions to reconstruct each fixture's shape.

### Task 3.11: test_fleet_dto.py — 2 immutable-tuple tests
**File:** `tests/unit/strategy/facade/test_fleet_dto.py`
**Tests:** `pytest tests/unit/strategy/facade/test_fleet_dto.py`
**Origin:** PROJ-480 T3.27

- [~] **DROPPED (out of scope):** the two tests use fundamentally different construction paths (direct kwargs vs `FleetInfo.from_fleet(fleet)`). A single parametrized test would obscure the two distinct construction surfaces being verified.

### Task 3.12: test_ship_serialization.py — 5 roundtrip tests
**File:** `tests/unit/simulation/entities/test_ship_serialization.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_serialization.py`
**Origin:** PROJ-480 T3.28

- [x] Parametrize the 5 simple roundtrip tests at lines 328-361 (name / ship_class / theme_id / team_id / color) on `(field, compare)`. The deeper roundtrip tests at lines 363+ (movement_policy, component_count, component_ids, hull, stats) have materially different bodies and are kept separate. The PROJ-479 DUP-003 helper `_assert_roundtrip_property` in `tests/conftest.py` is available; this task uses an inline `getattr`+lambda comparator pattern instead, since the helper signature would not accept the `tuple(color) == tuple(color)` comparison required for the color case.
- [x] Verify: passes (59 tests); LOC delta ≈ -35.

### Task 3.13: test_fleet_pursuer_tracker.py — 3 setup-shared tests
**File:** `tests/unit/strategy/fleet/test_fleet_pursuer_tracker.py` (retargeted from PROJ-480's `tests/unit/strategy/services/`)
**Tests:** `pytest tests/unit/strategy/fleet/test_fleet_pursuer_tracker.py`
**Origin:** PROJ-480 T3.35

- [~] **DROPPED (out of scope):** the 3 tests verify materially different facets (orders rewritten, return shape, pursuer registry). Sharing setup via a fixture would be fine, but parametrizing into a single test would obscure intent — each test currently documents a distinct invariant.

### Task 3.14: test_warp_resources.py — 3 warp_resource_costs tests
**File:** `tests/unit/strategy/fleet/test_warp_resources.py`
**Tests:** `pytest tests/unit/strategy/fleet/test_warp_resources.py`
**Origin:** PROJ-480 T3.39

- [x] Parametrize the 3 warp_resource_costs tests (PROJ-480 cited lines 41-71) on `(ship_configs, expected_costs)`.
- [x] Verify: passes (21 tests); LOC delta ≈ -25.

### Task 3.15: test_superweapon_order_processor_gaps.py — 5 TestStabilizerCancellation tests
**File:** `tests/unit/strategy/engine/test_superweapon_order_processor_gaps.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_order_processor_gaps.py`
**Origin:** PROJ-480 T3.42

- [~] **DROPPED (out of scope):** each handler test has 5-15 LOC of distinct setup (different processor methods, target shapes, patch needs). Parametrize would need per-case builder functions equivalent to the original test bodies.

### Task 3.16: test_tick_phases.py — 3 registry read tests
**File:** `tests/unit/simulation/systems/test_tick_phases.py`
**Tests:** `pytest tests/unit/simulation/systems/test_tick_phases.py`
**Origin:** PROJ-480 T3.44

- [~] **DROPPED (out of scope):** the candidate tests differ in registration count and assertion structure (sort order vs same-priority insertion order vs custom-phase placement). Sharing a parametrized fixture isn't clearly clearer than the current explicit set-up.

### Task 3.17: test_superweapon_command_handlers.py — 5 handler test cluster
**File:** `tests/unit/strategy/engine/test_superweapon_command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_command_handlers.py`
**Origin:** PROJ-480 T3.46

- [~] **DROPPED (out of scope):** each handler verifies a different target dict shape (None for STELLERATE / target_hex+name for OPEN_WARP_POINT / destination_id+target_hex for CLOSE_WARP_POINT / planet ref for IMPLODE_PLANET / mass-resource setup for DYSON). Parametrize would require per-handler target-assertion functions equivalent to the original bodies.

### Task 3.18: test_superweapon_validator.py — 5 validator-class clusters
**File:** `tests/unit/strategy/validation/test_superweapon_validator.py`
**Tests:** `pytest tests/unit/strategy/validation/test_superweapon_validator.py`
**Origin:** PROJ-480 T3.47

- [~] **DROPPED (out of scope):** the 5 validators (planet-implode, star-stellerate, warp-open, warp-close, dyson) have different signatures and setup requirements (e.g. `open_warp_point` needs a populated `galaxy.name_map`, dyson needs a different system setup). 5 × 3 = 15 cases each needing a setup_func makes the parametrize less readable than the originals.

### Task 3.19: test_empire_validation.py — 3 missing-field tests
**File:** `tests/unit/strategy/empire/test_empire_validation.py`
**Tests:** `pytest tests/unit/strategy/empire/test_empire_validation.py`
**Origin:** PROJ-480 T3.48

- [x] Parametrize the 3 missing-field PersistenceException tests (PROJ-480 cited lines 41-72) on `missing_key`.
- [x] Verify: passes (12 tests); LOC delta ≈ -25.

### Task 3.20: test_base_command_handler.py — 2 resolve_fleet tests
**File:** `tests/unit/strategy/engine/test_base_command_handler.py`
**Tests:** `pytest tests/unit/strategy/engine/test_base_command_handler.py`
**Origin:** PROJ-480 T3.49

- [x] Parametrize the 2 tests (PROJ-480 cited lines 44-68) on `(session_factory, resolve_kwargs, expected_substring)`.
- [x] Verify: passes (32 tests); LOC delta ≈ -10.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4 (CAT-11/12)
