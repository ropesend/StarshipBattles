# PROJ-333 Characterization Test Review — Findings Report

**Date:** 2026-05-04
**Reviewer:** OpenCode
**Scope:** 8 test files + 5 production files + design.md

---

## 1. Behavior Accuracy

### CRITICAL: Behavior accuracy verified for 6 traced tests — all match production code

The following 6 tests were traced end-to-end through production code paths. All correctly pin current production behavior.

**Test A:** `test_complex_only_queue_stops_on_non_complex_item`
**File:** tests/unit/strategy/engine/test_production_engine_queue.py (line 211)
**Production path:** `_process_queue_tick_dynamic` → `_validate_queue_item` (line 402: `is_complex_only and vehicle_type != 'complex'` → `QueueItemAction.STOP`) → `return` at line 330
**Verdict:** ✓ Correct. Queue unchanged, spawner not called.

**Test B:** `test_max_queue_iterations_limits_inner_loop_to_10`
**File:** tests/unit/strategy/engine/test_production_engine_queue.py (line 283)
**Production path:** `_process_queue_tick_dynamic` loop guard at line 318: `iterations < MAX_QUEUE_ITERATIONS` (10). After 10 completions, loop exits, item 11+ remains.
**Verdict:** ✓ Correct. Uses `<= MAX_QUEUE_ITERATIONS` (slightly lenient; `==` would be stricter but `<=` still valid).

**Test C:** `test_spawn_fleet_complex_falls_back_to_first_planet_when_target_id_missing`
**File:** tests/unit/strategy/engine/test_production_spawner.py (line 252)
**Production path:** `_spawn_fleet_complex` line 402-405: `next(..., planets_at_hex[0])` default fallback.
**Verdict:** ✓ Correct. Pins silent-wrong-planet behavior.

**Test D:** `test_load_design_returns_empty_dict_when_no_save_path`
**File:** tests/unit/strategy/engine/test_production_spawner.py (line 109)
**Production path:** `_load_design` line 122-124: `if not save_path: return {}`
**Verdict:** ✓ Correct.

**Test E:** `test_process_transfer_target_fleet_falls_back_to_owner_empire_when_galaxy_lacks_empires_attr`
**File:** tests/unit/strategy/engine/test_order_processor_transfer.py (line 171)
**Production path:** `process_transfer` line 314: `getattr(galaxy, 'empires', [])` → `[]` → falls through to owner empire scan lines 322-326.
**Verdict:** ✓ Correct. Galaxy = `object()` accurately models no-empires-attrib path.

**Test F:** `test_get_effective_speed_floors_via_int_truncation_after_multiplier`
**File:** tests/unit/strategy/fleet_movement_engine/test_characterization.py (line 80)
**Production path:** `_get_effective_fleet_speed` lines 129-130: `int(0.6) = 0`, `max(0.0, 0.0) = 0.0`
**Verdict:** ✓ Correct. Immobile at speed 1 × 0.6.

**Test G:** `test_load_pod_from_staging_yard_iterates_in_reverse`
**File:** tests/unit/strategy/engine/test_order_processor_transfer.py (line 377)
**Production path:** `_load_pod_from_staging_yard` line 552: `for i in range(len(planet.staging_yard) - 1, -1, -1)`
**Verdict:** ✓ Correct. Pod C loaded first (LIFO).

---

## 2. Bug Pin Verification

All 7 surprising behaviors from design.md § "Bug Pin Verification" are tested:

| ID | Behavior | Pinned By | Status |
|---|---|---|---|
| (a) | MAX_QUEUE_ITERATIONS=10 silent cap | `test_max_queue_iterations_limits_inner_loop_to_10` (queue.py:283) | ✓ |
| (b) | is_complex_only STOP-not-SKIP | `test_complex_only_queue_stops_on_non_complex_item` (queue.py:211) | ✓ |
| (c) | _load_design returns {} silent fallback | `test_load_design_returns_empty_dict_when_no_save_path` + `_when_load_fails` (spawner.py:109, 116) | ✓ |
| (d) | int() truncation flooring | `test_get_effective_speed_floors_via_int_truncation_after_multiplier` (fleet characterization.py:80) | ✓ |
| (e) | Hard-coded /100.0 divisor | `test_per_tick_consumption_is_one_hundredth_of_per_turn_total` (consumable characterization.py:66) | ✓ |
| (f) | staging-yard reverse iteration | `test_load_pod_from_staging_yard_iterates_in_reverse` (transfer.py:377) | ✓ |
| (g) | getattr(galaxy, 'empires', []) silent fallback | `test_process_transfer_target_fleet_falls_back_to_owner_empire_when_galaxy_lacks_empires_attr` (transfer.py:171) | ✓ |

**No missing bug pins.**

---

## 3. Mocking Discipline

### MAJOR: `test_phase_c_skips_when_source_no_longer_in_empire_emits_absorbed_by_other_merge` has confusing setup
**File:** tests/unit/strategy/engine/test_order_processor_instant.py (lines 142-169)
**Category:** mocking
**Finding:** The test does `empire.fleets.append(src); empire.fleets.remove(src)` with an inline comment "so Phase A collection works" — but `_elect_canonical_merges` is fully patched, bypassing both Phase A collection AND canonical merge election. The `append` is a no-op noise line. The comment misleads: Phase A does NOT need to "work" because the patch provides the canonical merge result directly. The test only exercises Phase C (aliveness check).
**Recommendation:** Remove the `empire.fleets.append(src)` line and clarify the comment to state that Phase A is bypassed via the patch and only Phase C is under test.

### MINOR: Direct internal attribute monkey-patching of `engine._spawner.spawn_completed_item`
**File:** tests/unit/strategy/engine/test_production_engine_queue.py (line 151, 221, 229, 256, 272, 288)
**Category:** mocking
**Finding:** Multiple tests set `engine._spawner.spawn_completed_item = MagicMock()` directly on the private `_spawner` attribute. This couples tests to internal structure and bypasses the spawner's DI constructor.
**Recommendation:** Consider injecting a mock spawner via `ProductionEngine(registries=..., ...)` if a constructor parameter exists, or document the monkey-patch as a deliberate characterization pattern.

### MINOR: Inline `GameRegistries(...)` construction instead of `mock_registries` fixture
**File:** tests/unit/strategy/engine/test_production_engine_consumption.py (lines 113, 147)
**Category:** mocking
**Finding:** Two tests construct `GameRegistries(components={}, modifiers={}, vehicle_classes={}, resources={})` inline rather than using the `mock_registries` fixture. This is inconsistent with the consumable management engine test file which uses shared conftest fixtures.
**Recommendation:** Use the `mock_registries` fixture from parent conftest for consistency, or define a local fixture.

### MINOR: `test_failed_consume_resource_triggers_auto_disable_and_returns_depletion` patches engine's own internal method
**File:** tests/unit/strategy/consumable_management_engine/test_characterization.py (line 92)
**Category:** mocking
**Finding:** Uses `patch.object(engine, "_auto_disable_components_for_resource", return_value=["engine_1"])` to stub the engine's own method under test. The integration aspect (consumption-failure → auto-disable call) is tested, but the actual auto-disable logic is separately tested. Acceptable split, but the mock means the full call chain is not exercised in any single test.
**Recommendation:** Acceptable as-is; this is a valid test decomposition. No action needed.

### MINOR: Non-deterministic `next(iter(ACTION_ORDER_TYPES))` in test setup
**File:** tests/unit/strategy/fleet_movement_engine/test_characterization.py (line 108)
**Category:** mocking
**Finding:** `action_type = next(iter(ACTION_ORDER_TYPES))` iterates a set, which is non-deterministic in Python. While any ACTION type correctly triggers the skip behavior, the test's expected output depends on a random set element. If a future change to ACTION_ORDER_TYPES removes the set, the iterator semantics change silently.
**Recommendation:** Hard-code a specific order type (e.g., `OrderType.COLONIZE`) for deterministic, readable test setup.

### MINOR: Module-level monkeypatch of `_colony_has_planetary_yard` bypasses real facility check
**File:** tests/unit/strategy/engine/test_production_engine_queue.py (lines 111-113, 148-150)
**Category:** mocking
**Finding:** Uses `monkeypatch.setattr("game.strategy.engine.production_engine._colony_has_planetary_yard", lambda: True)`. This is necessary for characterization tests that don't have real facility data, but the production code's facility-matching logic is never tested alongside the queue iteration.
**Recommendation:** Acceptable for characterization tests. Consider a conftest fixture for repeated use.

---

## 4. Test Naming

No vague test names (`test_basic`, `test_default`, `test_simple`) were found across any of the 8 test files. All tests have descriptive, behavior-focused names.

### MINOR: `test_habitability_multiplier_scales_production_rate_for_colony_only` name is slightly misleading
**File:** tests/unit/strategy/engine/test_production_engine_queue.py (line 326)
**Category:** naming
**Finding:** The test name says "for colony only" but the function also tests fleet multiplier behavior (returns 1.0) and no-race_registry fallback. Test covers three distinct scenarios in one function.
**Recommendation:** Split into three focused tests or broaden the name (e.g., `test_habitability_multiplier_by_context`).

---

## 5. Missing Coverage — Top 3 Surprising Behaviors per File (15 total)

### MAJOR: Missing pin for production_spawner surprise #2 — simulation reach-in for mass calculation
**File:** tests/unit/strategy/engine/test_production_spawner.py
**Category:** missing-coverage
**Design.md reference:** production_spawner #2: "`_spawn_to_staging_yard` calculates mass via `simulation.entities.ship_design_stats.calculate_design_stats` with the production registries — a strategy-layer engine reaching into simulation for cost math."
**Finding:** No test verifies that `calculate_design_stats` is called to compute pod mass when `self._registries` is non-None. The existing `test_spawn_to_staging_yard_uses_design_data_from_item_when_present` test creates `ProductionSpawner()` with no registries (registries=None), so the mass calculation branch is never entered. The staged item's `mass` field is not asserted. This surprising architectural coupling (strategy→simulation import) is unpinned.
**Recommendation:** Add a test with `ProductionSpawner(registries=mock_registries)` that verifies a pod with design_data containing components gets a non-zero mass from `calculate_design_stats`. Mock `calculate_design_stats` to return a known mass value and assert the staged item contains it.

### MAJOR: Missing pin for fleet_movement_engine surprise #3 — warp-no-resources returns warp_blocked=False
**File:** tests/unit/strategy/fleet_movement_engine/test_characterization.py
**Category:** missing-coverage
**Design.md reference:** fleet_movement_engine #3: "`apply_movement` for warp `pop_order()` on warp-blocked-no-capability AND warp-blocked-no-resources, but warp-no-resources logs the SAME `warp_blocked=False` field as the non-warp path — caller can't distinguish 'warp resource shortage' from 'ordinary movement complete-with-no-move'."
**Finding:** `test_apply_movement_warp_blocked_when_no_capability_pops_one_order` (line 170) tests the warp-blocked-no-capability path (returns `warp_blocked=True`). No test verifies the warp-blocked-no-resources path where `warp_blocked=False`. The production code at line 169-172: when `can_use_warp()` returns True but `has_resources_for_warp()` returns False, the result is `moved=False, warp_blocked=False` — indistinguishable from a successful non-warp movement with no movement. This behavioral surprise is unpinned.
**Recommendation:** Add a test where `fleet.location = HexCoord(0, 0)`, target hex is `HexCoord(10, 0)` (distance > 1, triggers warp), `capabilities.can_use_warp()` returns True, but `resources.has_resources_for_warp()` returns False. Assert `result.warp_blocked is False` and `fleet.pop_order` is called. Document this as the surprising behavior.

### MINOR: consumable_management_engine surprise #2 — "ALL matching components" and "re-disable/re-log" not fully tested
**File:** tests/unit/strategy/consumable_management_engine/test_characterization.py
**Category:** missing-coverage
**Design.md reference:** consumable_management_engine #2: "Auto-disable iterates ALL components matching the depleted resource per ship per tick — repeated depletions on the same tick re-disable the same components and re-log."
**Finding:** Existing tests verify single-component disable and filter precision (trigger mismatch, resource mismatch). No test has multiple components matching the same depleted resource across different layers. No test verifies that a ship with multiple depleted resources in one tick triggers `_auto_disable_components_for_resource` twice, potentially re-disabling already-disabled components and re-logging. The "ALL components" and "repeated depletions" aspects are unpinned.
**Recommendation:** Add a test with 3+ components spread across 2+ layers all consuming the same resource, asserting all 3 are disabled. Add a second test where `get_all_resource_costs_per_turn` returns two depleted resources ({fuel: 100, power: 50}), asserting `_auto_disable_components_for_resource` is called twice (once per resource).

### MINOR: production_engine surprise #3 indirectly tested through affordability path
**File:** tests/unit/strategy/engine/test_production_engine_consumption.py (line 216)
**Category:** missing-coverage (borderline)
**Finding:** Design.md surprise #3: "`_calculate_tick_expenditure` returns `None` when ANY required resource has rate 0 — the entire item halts even if other resources have abundant rate." This IS tested by `test_calculate_tick_expenditure_returns_none_for_zero_rate_required_resource`. However, the test only verifies the `None` return. It does NOT verify that `_process_queue_tick_dynamic` subsequently returns (line 338-340) without spawning, leaving remaining items unprocessed — the queue-halt consequence. The COMPLETION_EPSILON test correctly verifies the epsilon math. **Findings:** The pin is marginally incomplete — the method-level behavior is pinned, but the queue-level consequence (items after a zero-rate item are starved) is not directly tested.
**Recommendation:** Add an integration-level test where a queue has [zero_rate_item, good_item] — verify that the good_item is never processed because the zero-rate item returns None → STOP on the preceding item.

---

## Summary

| Severity | Count | Description |
|---|---|---|
| **CRITICAL** | 0 | — |
| **MAJOR** | 2 | Missing pins: spawner simulation reach-in, warp-no-resources warp_blocked=False |
| **MINOR** | 8 | Confusing test setup, internal monkey-patching, non-deterministic setup, naming, incomplete coverage edges |

### All findings by file:

| File | Issues |
|---|---|
| `test_production_engine_queue.py` | Minor: internal _spawner monkey-patching (line 151), naming (line 326) |
| `test_production_engine_consumption.py` | Minor: inconsistent registry fixture (lines 113, 147) |
| `test_production_spawner.py` | **Major:** missing simulation reach-in pin; (needs new test) |
| `test_characterization.py` (consumable) | Minor: partial internal patch (line 92); Minor: incomplete "ALL components" coverage |
| `test_characterization.py` (fleet movement) | **Major:** missing warp-no-resources pin; Minor: non-deterministic set iter (line 108) |
| `test_order_processor_colonize.py` | No issues found |
| `test_order_processor_transfer.py` | No issues found |
| `test_order_processor_instant.py` | Minor: confusing test setup (lines 142-169) |

### Overall assessment:

The PROJ-333 characterization test suite is thorough and well-structured. All 7 bug-pin behaviors from the design document are covered. The 6 traced behavior accuracy checks all passed. The two MAJOR gaps (spawner simulation reach-in and warp-no-resources behavior) should be addressed to achieve full design.md coverage of the 15 surprising behaviors. The MINOR issues are low-risk and do not compromise the characterization quality.
