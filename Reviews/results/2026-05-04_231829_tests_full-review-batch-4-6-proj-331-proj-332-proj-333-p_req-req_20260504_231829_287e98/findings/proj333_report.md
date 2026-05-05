# PROJ-333 Test Quality Review — Findings Report

**Review date:** 2026-05-04
**Reviewer:** OpenCode (automated)
**Scope:** 8 test files, 5 production files

---

## 1. Behavior Accuracy — Design.md Observation Pinning

### Observation coverage matrix

| # | Observation | Test exists? | Status |
|---|------------|-------------|--------|
| 1 | `production_engine`: MAX_QUEUE_ITERATIONS=10 silent cap | `test_max_queue_iterations_limits_inner_loop_to_10` (queue:283) | PASS (see finding 1.1) |
| 2 | `production_engine`: is_complex_only queue STOPs (not SKIPs) | `test_complex_only_queue_stops_on_non_complex_item` (queue:211) | PASS |
| 3 | `production_engine`: _calculate_tick_expenditure returns None when ANY required resource rate is 0 | `test_calculate_tick_expenditure_returns_none_for_zero_rate_required_resource` (consumption:216) | PASS |
| 4 | `production_spawner`: _load_design returns {} on failure | `test_load_design_returns_empty_dict_when_no_save_path` (spawner:109), `test_load_design_returns_empty_dict_when_load_fails` (spawner:116) | PASS |
| 5 | `production_spawner`: _spawn_to_staging_yard reaches into simulation | `test_spawn_to_staging_yard_reaches_into_simulation_for_mass_calculation` (spawner:214) | PASS |
| 6 | `production_spawner`: _spawn_fleet_complex falls back to planets_at_hex[0] | `test_spawn_fleet_complex_falls_back_to_first_planet_when_target_id_missing` (spawner:301) | PASS |
| 7 | `consumable_management`: Hard-coded /100.0 divisor | `test_per_tick_consumption_is_one_hundredth_of_per_turn_total` (consumable_char:66) | PASS |
| 8 | `consumable_management`: Auto-disable iterates ALL components matching depleted resource | No multi-match test exists | FAIL (see finding 1.2) |
| 9 | `consumable_management`: is_combat_capable() gates ALL consumption | `test_non_combat_capable_ship_is_skipped` (consumable_char:49) | PASS |
| 10 | `fleet_movement`: _get_effective_fleet_speed floors via int() | `test_get_effective_speed_floors_via_int_truncation_after_multiplier` (fm_char:80) | PASS |
| 11 | `fleet_movement`: _filter_jump_past_collisions only handles distance-1 swap parity | `test_filter_jump_past_drops_larger_fleet_on_swap_parity_with_id_tiebreak` (fm_char:238) | PASS |
| 12 | `fleet_movement`: warp pop_order() logs same blocked=False as non-warp | `test_warp_no_resources_returns_warp_blocked_false` (fm_char:184) | PASS |
| 13 | `order_processor`: getattr(galaxy, 'empires', []) silently empty fallback | `test_process_transfer_target_fleet_falls_back_to_owner_empire_when_galaxy_lacks_empires_attr` (transfer:171) | PASS |
| 14 | `order_processor`: process_join_fleet pops vs process_instant_orders skips | `test_process_join_fleet_pops_order_when_not_at_same_location` (instant:249), `test_process_instant_orders_collects_only_co_located_join_fleet_candidates` (instant:79) | PASS |
| 15 | `order_processor`: _load_pod_from_staging_yard reverse iteration (LIFO) | `test_load_pod_from_staging_yard_iterates_in_reverse` (transfer:377) | PASS |

**Coverage: 13/15 PASS, 2 observations with weakness** (findings below).

---

### Finding 1.1 — CRITICAL

- **File:line:** `tests/unit/strategy/engine/test_production_engine_queue.py:293`
- **Test name:** `test_max_queue_iterations_limits_inner_loop_to_10`
- **Description:** The assertion uses `call_count <= MAX_QUEUE_ITERATIONS` (i.e. `<= 10`) rather than `== 10`. With 20 zero-cost items and abundant production rate, exactly 10 items should be processed and 10 should remain. A `<=` assertion would pass even if only 2 items were processed, which would mean the cap is not forcing the loop exit.
- **Recommendation:** Change to `assert engine._spawner.spawn_completed_item.call_count == MAX_QUEUE_ITERATIONS` and add `assert len(queue) == 10` to verify the cap leaves remaining items in the queue.

---

### Finding 1.2 — CRITICAL

- **File:line:** `tests/unit/strategy/consumable_management_engine/test_characterization.py:83-102` and surrounding tests
- **Test name:** `test_failed_consume_resource_triggers_auto_disable_and_returns_depletion` and all `_auto_disable_components_for_resource` tests
- **Description:** Observation 8 states "Auto-disable iterates ALL components matching the depleted resource." The existing `_auto_disable_components_for_resource` tests only ever have one matching component. No test verifies that when two or more components consume the same resource, ALL are disabled (not just the first match). Additionally, the "repeated depletions on the same tick re-disable the same components and re-log" behavior has no pinning test — `test_failed_consume_resource_triggers_auto_disable_and_returns_depletion` mocks out `_auto_disable_components_for_resource` entirely, bypassing the multi-disable path.
- **Recommendation:** Add a test with two components both consuming the same resource, verify both component IDs appear in the disabled list. Add a separate test where a ship has two depletable resources (e.g. "power" and "fuel"), verify auto-disable is called for each, and verify the re-disable count.

---

## 2. Vacuous Tests

**No vacuous tests found across the 8 files.** All tests instantiate the real production class under test (`ProductionEngine`, `ProductionSpawner`, `ConsumableManagementEngine`, `FleetMovementEngine`, `OrderProcessor`) with real registries or appropriate constructor arguments. Mock objects are used exclusively at the boundary layer (Empire, Planet, Fleet, Galaxy) per D-002. Assertions verify behavior rather than mock-call tautologies.

---

## 3. Mocking Discipline

**No egregious violations found.** The production engines themselves are never mocked — every test creates a real engine instance. Boundary objects (Empire, Planet, Fleet, registries) are appropriately mocked per D-002.

### Finding 3.1 — MAJOR

- **File:line:** `tests/unit/strategy/engine/test_production_engine_queue.py:98-118`, `121-156`, and sibling patterns
- **Test name:** `test_construction_queue_paused_skips_colony_base_queue`, `test_per_facility_pause_skips_only_that_shipyard`
- **Description:** These tests use `monkeypatch.setattr` to replace `_colony_has_planetary_yard` and `_get_facility_production_rates` — internal module-level functions — with lambdas rather than using mock colonies/fleets with appropriate attributes. While this works, the approach is fragile: if these functions are refactored, the monkeypatch paths break without a test compilation failure. The D-002 guideline suggests mocking at the boundary (Planet, Fleet), and these colonies already have enough mock surface to support the test without monkeypatching internals.
- **Recommendation:** Set `colony.facilities` attributes to make `_colony_has_planetary_yard` return True naturally, rather than monkeypatching the function. This makes the test resilient to internal refactors.

---

### Finding 3.2 — MAJOR

- **File:line:** `tests/unit/strategy/engine/test_production_engine_queue.py:47-53`, fixture `colony`
- **Test name:** `colony` fixture
- **Description:** The `colony` fixture sets `context_type = None` with a comment "falls back to empire pool". Per design.md "Testability Blockers": `context_type='planet' or 'fleet' must be set explicitly`. While the `None` fallback is a legitimate code path, the fixture is used in tests that exercise `_check_affordability`, `_log_resource_shortage`, and `_apply_resource_consumption` — all of which dispatch on `context_type`. Using `None` means these tests exercise only the empire-pool fallback, not the planet/fleet-specific branches. The docstring for the test-split boundary says `_consumption.py` covers the planet-vs-fleet branch, and the consumption file indeed sets context_type explicitly. However, the queue file's tests also enter `_check_affordability` via `_process_queue_tick_dynamic` — and when they use the `colony` fixture with `context_type=None`, they silently skip planet-specific affordability checks.
- **Recommendation:** Either rename fixture to make its `None`-context intent explicit (e.g. `colony_fallback_context`) or add a comment noting that this fixture only exercises the empire-pool fallback.

---

## 4. Test Names

**No issues found.** All ~90 test names across the 8 files are behavior-descriptive. No instances of `test_basic`, `test_default`, `test_simple`, or generic names. Names follow the `test_<subject>_<condition>_<expected_behavior>` pattern consistently.

---

## 5. Missing Surfaces

### Finding 5.1 — CRITICAL

- **File:line:** `game/strategy/engine/fleet_movement_engine.py:73`
- **Test name:** (none)
- **Description:** `FleetMovementEngine.calculate_next_hex()`, a public method, has zero test coverage in the PROJ-333 characterization file. This method delegates to `FleetNavigationService.calculate_fleet_next_hex()` and also manages lazy initialization of the nav service. Neither the delegation behavior nor the lazy-init path is tested.
- **Recommendation:** Add a test verifying `calculate_next_hex` delegates to `FleetNavigationService.calculate_fleet_next_hex` and uses `self._nav_service = FleetNavigationService()` on first call when `_nav_service` is `None`.

---

### Finding 5.2 — CRITICAL

- **File:line:** `game/strategy/engine/production_spawner.py:132-170`, `174-223`, `331-367`
- **Test names:** (none)
- **Description:** Three production-spawner methods have zero direct characterization:
  - `_load_and_create_ship` (line 132): Handles design loading, ship creation, and built-count increment. The dispatch test for `spawn_completed_item` patches `_spawn_ship` and `_spawn_fleet_ship` entirely, so `_load_and_create_ship` is never exercised by any current PROJ-333 test.
  - `_create_and_place_facility` (line 174): Creates a `PlanetaryFacility` from a design, appends to planet, and emits a `COMPLEX_BUILT` event. All dispatch tests patch this method out, so facility creation and event emission are untested.
  - `_spawn_fleet_ship` (line 331): Loads a ship via `_load_and_create_ship` and adds it to the building fleet while emitting `SHIP_BUILT`. Only the dispatch routing to it is tested (via mock assertion), not the method's body.
- **Recommendation:** Add characterization tests for each of these three methods: verify `_load_and_create_ship` returns `None` on failure and a `ShipInstance` on success; verify `_create_and_place_facility` appends a `PlanetaryFacility` to `planet.facilities` and emits `COMPLEX_BUILT`; verify `_spawn_fleet_ship` calls `fleet.add_ship` and emits `SHIP_BUILT`.

---

### Finding 5.3 — CRITICAL

- **File:line:** `game/strategy/engine/production_engine.py:539-556` (fleet context branch), `599-610` (fleet context branch)
- **Test names:** (none)
- **Description:** `_log_resource_shortage` (line 516) and `_apply_resource_consumption` (line 581) both dispatch on `context_type` with three branches: `'planet'`, `'fleet'`, and empire-fallback. The existing tests only cover the planet context (`test_log_resource_shortage_picks_largest_shortfall_ratio_as_limiting`, `test_log_resource_shortage_emitted_once_per_item_per_turn`, `test_apply_resource_consumption_updates_resources_consumed_dict`) and the empire-fallback (`test_check_affordability_falls_back_to_empire_pool_when_no_context_type` for affordability only). The fleet context branch — calling `fleet.get_cargo_resource()` / `fleet.consume_cargo_resource()` — has zero test coverage.
- **Recommendation:** Add tests with `context_type='fleet'` for `_log_resource_shortage` (verifying `get_cargo_resource` is called) and `_apply_resource_consumption` (verifying `consume_cargo_resource` is called).

---

### Finding 5.4 — MAJOR

- **File:line:** `game/strategy/engine/order_processor.py:366-396`
- **Test name:** (none)
- **Description:** `_execute_fleet_transfer` — fleet-to-fleet cargo transfer — is only tested indirectly through `process_transfer` integration tests that all use `amount=0` (no actual transfer). The `test_process_transfer_target_fleet_lookup_searches_galaxy_empires` at `transfer:140` and `test_process_transfer_target_fleet_falls_back_to_owner_empire_when_galaxy_lacks_empires_attr` at `transfer:171` both set `"amount": 0` in the transfer params, leaving `_execute_fleet_transfer`'s min-capacity capping logic and actual `unload_cargo_from_fleet`/`load_cargo_to_fleet` calls untested.
- **Recommendation:** Add a test with `amount > 0`, non-zero fleet cargo, and verify `actual_transferred` > 0, the `unload_cargo_from_fleet` and `load_cargo_to_fleet` calls fire with correct values.

---

### Finding 5.5 — MAJOR

- **File:line:** `game/strategy/engine/order_processor.py:469-530` (resource unload path, line 519-530), `398-467` (passenger load path when `amount=0`, line 420)
- **Test names:** (none)
- **Description:** Two `process_transfer` paths are untested:
  - Resource **unloading** (fleet → planet, `_execute_unload` lines 519-530): only resource **loading** is tested (`test_process_transfer_load_resource_caps_by_planet_stockpile`).
  - Passenger loading with `amount=0` ("load all" semantics at `_execute_load` line 420): only `amount > 0` is tested.
- **Recommendation:** Add a test for resource unloading verifying `planet.add_to_stockpile` is called. Add a test for passenger loading with `amount=0` verifying `to_load = min(available_space, pop.count)` is used.

---

### Finding 5.6 — MAJOR

- **File:line:** `game/strategy/engine/order_processor.py:706-731`
- **Test name:** (none)
- **Description:** `execute_action_order` has a superweapon handler dispatch via `superweapon_handlers` dict (6 order types: IMPLODE_PLANET, STELLERATE_STAR, OPEN_WARP_POINT, CLOSE_WARP_POINT, CREATE_DYSON_SPHERE, SELF_DESTRUCT). None of these handler paths have characterization tests in the PROJ-333 files.
- **Recommendation:** While superweapon processing is outside the primary PROJ-333 scope, at least one characterization test verifying dispatch routing to `SuperweaponOrderProcessor` (e.g., `execute_action_order` dispatches IMPLODE_PLANET to the superweapon processor) would complete the surface coverage.

---

### Finding 5.7 — MAJOR

- **File:line:** `game/strategy/engine/fleet_movement_engine.py:339-360`
- **Test name:** (none)
- **Description:** `FleetMovementEngine.apply_movements()` (plural) — the loop that iterates `move_queue` and calls `apply_movement()` (singular) for each entry and accumulates `MovementResult` objects — has no direct test. While `apply_movement` is well-tested, the accumulator loop behavior (multiple fleets moving in sequence, results list construction) is untested.
- **Recommendation:** Add a test with two fleets in the move queue and verify both get `MovementResult` entries in the accumulated list.

---

### Finding 5.8 — MAJOR

- **File:line:** `game/strategy/engine/production_engine.py:436-490`
- **Test name:** (existing coverage of main branches)
- **Description:** `_calculate_tick_expenditure` has a subtle edge case: when `production_rate` lacks a key for a resource that's still required, `production_rate.get(res, 0.0) / TICKS_PER_TURN` yields `0.0`, which causes `find_limiting_resource_ticks` to return `None`. The existing test covers the explicit-zero-rate case but not the missing-key case. Additionally, `_update_turns_remaining` is only tested for `max_ticks_needed == 0`; the `max_ticks_needed > 0` path that actually computes turns is covered only through integration.
- **Recommendation:** Add a test for missing production-rate key causing `None` return. Add a focused test for `_update_turns_remaining` with `max_ticks_needed > 0`, verifying `turns_remaining = current_est_ticks / TICKS_PER_TURN`.

---

## Overall Verdict

| Category | Count |
|----------|-------|
| **CRITICAL findings** | 5 (findings 1.1, 1.2, 5.1, 5.2, 5.3) |
| **MAJOR findings** | 7 (findings 3.1, 3.2, 5.4, 5.5, 5.6, 5.7, 5.8) |
| **Observations pinned** | 13/15 (87%) with pinning tests; 2 with weakness (see 1.1, 1.2) |

**Coverage is NOT adequate.** Five critical gaps remain:
1. `FleetMovementEngine.calculate_next_hex` — zero coverage (public method)
2. `ProductionSpawner._load_and_create_ship`, `_create_and_place_facility`, `_spawn_fleet_ship` — zero direct coverage (pasted out in dispatch tests)
3. Fleet context branches in `_log_resource_shortage` / `_apply_resource_consumption` — zero coverage
4. MAX_QUEUE_ITERATIONS test uses `<=` (weak assertion, CRITICAL for pinning)
5. Auto-disable multi-component match — zero coverage (core observation from design.md)

These should be addressed before PROJ-333 can be considered complete.
