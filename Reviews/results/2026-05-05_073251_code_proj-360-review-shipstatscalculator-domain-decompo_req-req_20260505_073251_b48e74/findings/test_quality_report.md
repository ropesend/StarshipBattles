# Test Quality Report: PROJ-360 ShipStatsCalculator Domain Decomposition

**Review type:** Test quality & coverage audit
**Author:** OpenCode (ocode-test-review)
**Date:** 2026-05-05

---

## Summary

| Severity | Count |
|----------|-------|
| CRIT     | 0     |
| MAJ      | 4     |
| MIN      | 5     |
| NIT      | 1     |

---

### FIND-001: [MAJ] Launch/hangar domain not exercised by any golden design
**File:** tests/unit/simulation/entities/test_ship_stats_golden.py:46-54
**Description:** None of the 7 parametrized golden designs (`qs_escort`, `qs_general_purpose`, `qs_frigate_gc`, `qs_heavy_cruiser`, `qs_battleship`, `qs_missile_cruiser`, `qs_warp_gate_opener`) have `fighter_capacity > 0`, meaning the `VehicleLaunch`/`VehicleStorage` code path in `game/simulation/entities/stat_contributors/launch.py:aggregate_hangar()` is completely untested by the golden snapshot. All snapshot entries show `fighter_capacity: 0`, `fighters_per_wave: 0`, `fighter_size_cap: 0`, `launch_cycle: 0`. The documented goal is "a representative cross-section of quickstart ship designs" that covers "diverse contributor domains" (line 15-16), yet launch/hangar is entirely absent.
**Remediation:** Add a carrier-type design to `GOLDEN_DESIGNS` (e.g., `qs_carrier` if available, or create a minimal carrier fixture) that exercises the hangar aggregation path with non-zero `VehicleStorage` and `VehicleLaunch` abilities. Alternatively, add a dedicated unit test that builds a ship with mock components carrying hangar abilities and runs the full `calculate()` pipeline, asserting non-zero golden values.

---

### FIND-002: [MAJ] Combat endurance fields not captured by `_capture_stats`
**File:** tests/unit/simulation/entities/test_ship_stats_golden.py:94-177
**Description:** `calculate_combat_endurance()` is called at the end of `ShipStatsCalculator.calculate()` (ship_stats.py:448) and writes at least 12 fields onto the ship: `fuel_consumption`, `ammo_consumption`, `energy_consumption`, `potential_fuel_consumption`, `potential_ammo_consumption`, `potential_energy_consumption`, `fuel_endurance`, `ammo_endurance`, `energy_net`, `energy_endurance`, `energy_recharge`, and `_cached_summary`. None of these are captured by `_capture_stats()`. The function's docstring claims to "Mirrors every assignment the calculator performs against `ship`" (line 98), which is untrue for these endurance fields. A regression in the endurance calculation would not be caught by the golden test.
**Remediation:** Extend `_capture_stats()` to snapshot the endurance fields (excluding `_cached_summary` if it's purely a derived cache) and regenerate the golden snapshot. At minimum, add a comment documenting that endurance fields are intentionally excluded and rely on separate tests.

---

### FIND-003: [MAJ] No dedicated unit test for `_phase_damage_check_and_supply` edge cases
**File:** game/simulation/entities/ship_stats.py:187-220
**Description:** The damage-check phase has several edge cases that are only tested indirectly through golden snapshots (which use pristine fresh-load designs with no damage state):
- `hp_ratio <= damage_threshold` exactly at the boundary (should deactivate)
- `damage_threshold == 1.0` (component never damaged regardless of hp_ratio)
- Dead armor: `current_hp == 0` for armor components (should deactivate)
- Armor components with `hp_ratio` below threshold but `current_hp > 0` (armor uses HP pool, not per-component threshold — this branch exists but edge case interaction with the `not comp.abilities.get("Armor", False)` guard is untested)
- Components already damaged at calculate-time (the `mark_hp_cache_dirty()` call and `hp_ratio` computation on damaged components)
**Remediation:** Add a `TestPhaseDamageCheck` class in a new test file (or in golden tests) that constructs a ship with components in specific damage states and verifies `is_active`/`status` values after `_phase_damage_check_and_supply` runs.

---

### FIND-004: [MAJ] No unit test for `_initialize_resources` delta-update path (second recalculation)
**File:** game/simulation/entities/ship_stats.py:450-483
**Description:** The `_initialize_resources` method has two branches:
1. **First load** (`_resources_initialized == False`): fills all resources to max capacity, sets `current_shields = max_shields`.
2. **Delta update** (`_resources_initialized == True`): adds capacity deltas (preserving current usage), increments `current_shields` by the difference.

The golden test calls `calculate()` once per design (via `_build_and_calculate`, line 182-184). The delta-update path is never exercised. The `test_construction_cost_is_deterministic` test (line 284-298) calls `recalculate_stats()` twice but only asserts `construction_cost` stability, not resource delta behavior. A bug in the delta path (e.g., double-counting capacity, incorrect `prev_max` tracking) would not be caught.
**Remediation:** Add a test that builds and calculates a ship, then adds/removes components (or changes abilities) and calls `recalculate_stats()` again, asserting that resource values increase only by the delta.

---

### FIND-005: [MIN] MultiplexTracking (command domain) not exercised by any golden design
**File:** tests/unit/simulation/entities/test_ship_stats_golden.py:46-54, snapshot
**Description:** All 7 golden designs have `max_targets: 1` in the snapshot. The `track_multiplex` function (command.py:43-51) which implements the `MultiplexTracking` ability is never exercised by golden tests. The `TestTrackMultiplex` unit tests (test_command.py:50-77) cover this in isolation with mocks, but no integrated test confirms the full pipeline from design data through `calculate()`.
**Remediation:** Either add a design that includes a `MultiplexTracking` ability component, or note explicitly in the golden test docstring which contributor domains are exercised and which rely on unit tests alone.

---

### FIND-006: [MIN] Acceptance test docstring/code/assertion message mismatch
**File:** tests/unit/simulation/entities/test_stat_contributor_extension.py:110-150
**Description:** Three inconsistencies in `test_fake_contributor_runs_for_a_ship_with_matching_ability`:
1. **Line 115-118 (docstring):** "We use `ShieldProjection` as the gating ability since the battleship's `shield_generator` carries it" — but `ShieldProjection` is a shield projection ability, not a "shield regenerator" as implied in context.
2. **Line 133-135 (comment):** "it has shield regenerators. Recalculate stats." — the component has `ShieldProjection`, not `ShieldRegeneration`.
3. **Line 143 (assert message):** "Fake contributor was registered for ShieldRegeneration but never invoked" — the contributor was registered for `ShieldProjection`, not `ShieldRegeneration`.

These mismatches suggest the code was copy-pasted or renamed without updating all references. If a developer reads this test as documentation for the extension point, they may register the wrong ability name.
**Remediation:** Change the assertion error message from `ShieldRegeneration` to `ShieldProjection`, and update the comment on line 134 from "shield regenerators" to "shield projection components" (or similar).

---

### FIND-007: [MIN] `test_registry.py` `test_unregister_returns_to_default` leaks on assertion failure
**File:** tests/unit/simulation/entities/stat_contributors/test_registry.py:61-68
**Description:** This test calls `register_crew_priority("FakeRoundtrip", 2)` at line 65 but never appends to the `crew_added` list tracked by the `cleanup` fixture. If the assertion on line 66 (`assert lookup_crew_priority(comp) == 2`) fails, `unregister_crew_priority("FakeRoundtrip")` on line 67 never executes, and `"FakeRoundtrip"` remains in `CREW_PRIORITY_REGISTRY` — a global module-level list — potentially affecting subsequent tests that use `lookup_crew_priority`.
**Remediation:** Add `crew_added.append("FakeRoundtrip")` immediately after `register_crew_priority(...)` on line 65 so the `cleanup` fixture's teardown always removes it, even on assertion failure.

---

### FIND-008: [MIN] No isolated unit test for `_aggregate_cargo_and_pod_abilities`
**File:** game/simulation/entities/ship_stats.py:299-316
**Description:** This method aggregates `CargoStorage` and `PodStorage` abilities. The golden snapshot covers it indirectly (`qs_general_purpose` has `cargo_storage: {"passengers": 5000.0}` and `pod_storage_mass: 5000.0`), and the `test_ship_design_stats.py` integration test may exercise it, but there is no unit test that isolates this function and tests edge cases:
- `CargoStorage` with `capacity == 0` (should be filtered out)
- `PodStorage` with non-dict value (the `isinstance(pod_data, dict)` guard)
- `PodStorage` with `capacity_mass == 0` (should be filtered out)
- Multiple `CargoStorage` abilities with same `cargo_type` (summation)
**Remediation:** Add a `TestCargoAndPodAggregation` class to the golden test suite or a new test file, testing the private method via a mock component with varying ability shapes.

---

### FIND-009: [MIN] No unit test for `_phase_physics_and_limits` zero-mass branch
**File:** game/simulation/entities/ship_stats.py:361-383
**Description:** The `_phase_physics_and_limits` method has an `if ship.mass > 0` branch (line 363) and an `else` branch (line 372-373) that sets `acceleration_rate = 0` and `max_speed = 0`. All 7 golden designs have `mass > 0`, so the zero-mass branch is never exercised. While a zero-mass ship is arguably invalid, defensive code that exists should be tested. The `compute_max_speed(ship.total_thrust, ship.mass)` call also has a `ship.total_thrust > 0` guard (line 369) — zero-thrust is exercised (e.g., `qs_escort` has `total_thrust: 150` so it computes, but designs with zero thrust aren't in the golden set).
**Remediation:** Add a test with a mock ship having `mass = 0` and verify `acceleration_rate == 0` and `max_speed == 0`. Similarly, add a zero-thrust test case.

---

### FIND-010: [NIT] ECM sensor offense exercised by only one golden design
**File:** tests/unit/simulation/entities/test_ship_stats_golden_snapshot.json
**Description:** `baseline_to_hit_offense` is `0` for 6 of 7 golden designs. Only `qs_frigate_gc` has `baseline_to_hit_offense: 1.0`, exercising the `ToHitAttackModifier` aggregation path. The weapons contributor (`weapons.py:aggregate_targeting_scores`) computes both ECM defense (`ToHitDefenseModifier`) and sensor offense (`ToHitAttackModifier`). The golden snapshot provides weak coverage for the offense path — a regression that zeroes out `baseline_to_hit_offense` would only be caught because `qs_frigate_gc` happens to have the value. The ECM defense path is exercised more broadly because `total_defense_score` varies across all designs (due to the size and maneuver components, not necessarily ECM).
**Remediation:** Consider adding a design with non-trivial sensor/ECM components, or note this coverage gap explicitly. Given that `aggregate_targeting_scores` is unit-tested in isolation, this is a minor gap in integration coverage.

---

## Cross-Cutting Observations

### Float normalization is adequate
The `_round_for_snapshot(value, 12)` function (test_ship_stats_golden.py:73-91) and `_assert_equal` with `FLOAT_TOL=1e-9` (test_ship_stats_golden.py:217-242) are well-designed. Twelve decimal places provides sufficient precision for all snapshot values (range ~0 to 400000), and the `math.isclose` tolerance of 1e-9 is tight enough to catch regressions while accommodating JSON round-trip noise. The `rel_tol=1e-12` is appropriate for relative comparisons.

### Shield energy cost "first match wins" is properly documented and tested
The test `test_shield_energy_cost_only_counts_once_first_match_wins` (test_defense.py:124-135) correctly documents and verifies the legacy behavior where `break` exits the inner loop after the first energy ResourceConsumption. The production code (defense.py:53-57) uses `+= ab.amount` then `break`, which differs from a plain assignment — the `+=` means multiple shield-regen components each contribute their own first energy cost to the shared accumulator. This nuance is correctly manifested in the test which uses a single component.

### No `random.seed()` violations in reviewed tests
None of the 9 test files under review call `random.seed()`. Pattern #18 compliance is maintained.

### Test isolation is generally sound but has minor gaps
- `clean_extension_registry` fixture (test_stat_contributor_extension.py:36-60): Wraps `register_*` calls in tracking closures. If a test bypasses the closures and calls the registry functions directly, that registration leaks. Current tests all use the wrappers.
- `cleanup` fixture (test_registry.py:26-35): Same pattern, but `test_unregister_returns_to_default` (line 61-68) bypasses tracking (see FIND-007).
- The `STAT_CONTRIBUTOR_REGISTRY` is a module-level list in `registry.py` — adding a contributor in one test module would persist across test modules, but the `clean_extension_registry` fixture properly cleans up its additions. The registry starts empty (line 146: `[]`), so state from one test file does not leak into another test file.
- `_resources_initialized` flag on `Ship` instances: The golden test creates a new Ship for each parametrized case, so no cross-test pollution.

### Acceptance test properly exercises the registry extension point
`test_fake_contributor_runs_for_a_ship_with_matching_ability` (test_stat_contributor_extension.py:110-150) registers a contributor via `register_stat_contributor`, runs `ship.recalculate_stats()`, and verifies invocation. It cleans up via the `clean_extension_registry` fixture. The `test_contributor_only_runs_on_operational_components` test (line 167-218) correctly verifies the `is_operational` gating by marking shield components damaged and confirming fewer invocations on second recalc.

### Golden snapshot captures all calculator-written ship fields except endurance
`_capture_stats()` (test_ship_stats_golden.py:94-177) captures: mass, HP, movement fields, defense fields, hangar/launch fields, command fields, mass budget, geometry, targeting/EW scores, resources (max/value/regen), construction costs, warp costs, cargo/pod storage, ammo gen, layer status, and armor pool. The only fields written by `calculate()` that are NOT captured are the combat endurance fields (12 fields from `combat_endurance.py:calculate_combat_endurance`, see FIND-002).

### 46 unit tests across domain files + registry (not 37 as stated in scope)
The scope document states "37 contributor tests + acceptance" but the actual count is higher:
- test_registry.py: 9 tests (TestLookupCrewPriority: 2, TestRegisterCrewPriority: 3, TestStatContributorRegistration: 4)
- test_defense.py: 11 tests (TestArmorPoolAggregation: 2, TestShieldAggregation: 5, TestArmorAndRepairPostAggregation: 1, TestArmorPoolInit: 3)
- test_command.py: 12 tests (TestPrioritySortKey: 4, TestTrackMultiplex: 4, TestAllocateCrewAndLifeSupport: 4)
- test_movement.py: 7 tests
- test_weapons.py: 3 tests
- test_launch.py: 6 tests
**Total: 48 domain + registry unit tests.** (The scope may have counted only test_* function count before parametrization, or used a stale baseline.)
