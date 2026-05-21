# Shard 08 — Verified Findings

## Summary
- Shard: 08
- Claims reviewed: 11 (Phase 1: 9, Cross-shard: 2)
- CONFIRMED: 10 | DISPUTED: 1 | INCONCLUSIVE: 0
- Severity downgrades: 0

## Verified Findings (CONFIRMED only)

### tests/unit/strategy/services/test_fleet_navigation_action_timing.py

#### CAT-8: Multiple 2-level nested with patch() blocks [MINOR]
- **Location**: test_fleet_navigation_action_timing.py:66-81, 124-137, 182-195, 258-270, 301-308
- **Issue**: Five test methods (`test_colonize_action_delays_movement`, `test_stellerate_star_shows_multi_tick_delay`, `test_in_progress_action_shows_remaining_ticks`, `test_consecutive_actions_accumulate_ticks`, `test_action_timing_respects_max_turns`) each contain 2-level nested `with patch(...)` blocks, patching `find_hybrid_path` inside `resolve_action_time`. The module docstring at line 18-20 explicitly acknowledges this is intentional (PROJ-323 Task 2.14) but the nesting remains a readability burden.
- **Suggestion**: Extract the double-patch into a helper context manager or fixture to reduce nesting per-test.
- **LOC affected**: ~60
- **Verified**: CONFIRMED

### tests/unit/ui/services/test_ship_io.py

#### CAT-10: 7 near-identical round-trip tests [MINOR]
- **Location**: test_ship_io.py:395-541
- **Issue**: `test_round_trip_preserves_ship_name`, `_ship_class`, `_team_id`, `_color`, `_component_count`, `_movement_policy`, `_recalculates_stats` all follow the identical pattern: `ship.to_dict()` → write to `tmp_path` → read back → `Ship.from_dict(data, registries=...)` → assert one property. Each method is ~15-20 lines with only the property name and assertion differing.
- **Suggestion**: Parametrize into one `test_round_trip_preserves_property` with `(property_name, expected_value_extractor)` pairs.
- **LOC affected**: ~150
- **Verified**: CONFIRMED

### tests/unit/simulation/test_battle_state_serialization.py

#### CAT-5: Function-scoped heavy fixtures [MAJOR]
- **Location**: test_battle_state_serialization.py:158-282, 620-755, 904-1006
- **Issue**: Nine fixtures (`minimal_ship_state`, `ship_state_with_components`, `destroyed_ship_state`, `retreating_ship_state`, `empty_battle_state`, `battle_state_with_ships`, `full_battle_state`, `minimal_results`, `full_results`) are function-scoped fixtures that construct ShipState/BattleState/BattleResults objects with 15-20+ fields each. These are read-only across all test methods — no test mutates any fixture instance. The full_results fixture alone is ~69 lines.
- **Suggestion**: Rescope to `scope="module"` or `scope="session"` for the read-only fixtures.
- **LOC affected**: ~200
- **Verified**: CONFIRMED

### tests/unit/strategy/engine/test_turn_engine_progress_callback.py

#### CAT-6: Asserts on MagicMock call_args_list exact format [MAJOR]
- **Location**: test_turn_engine_progress_callback.py:62-63
- **Issue**: `test_progress_callback_fires_on_cadence` asserts `cb.call_args_list == expected` with the full tuple format `[((tick, TICKS_PER_TURN), {}) for tick in _EXPECTED_CALLBACK_TICKS]`. This pins the internal call representation of MagicMock and will break if any call signature addition or reorder occurs.
- **Suggestion**: Assert `cb.call_count == len(_EXPECTED_CALLBACK_TICKS)` and verify individual call args via loop, or use `cb.assert_has_calls(...)` with relaxed matchers.
- **LOC affected**: 3
- **Verified**: CONFIRMED

### tests/unit/strategy/facade/test_fleet_dto.py

#### CAT-10: Duplicate tuple-immutability tests [MINOR]
- **Location**: test_fleet_dto.py:192-269
- **Issue**: `test_collection_fields_are_immutable_tuples` (lines 192-229) and `test_from_fleet_returns_tuples` (lines 231-269) verify the same invariant: that FleetInfo's `ships`, `orders`, and `projected_path` fields are tuples. The first tests direct construction, the second tests `from_fleet()`. Both assert `isinstance(field, tuple)` on the same three fields.
- **Suggestion**: Merge into one parametrized test covering both construction sources.
- **LOC affected**: ~80
- **Verified**: CONFIRMED

### tests/unit/ui/panels/test_ship_detail_panel.py

#### CAT-6: Bypasses __init__ via object.__new__ then manually sets attributes [MAJOR]
- **Location**: test_ship_detail_panel.py:131-521
- **Issue**: 23 test methods (count verified; original claim stated 16) across classes TestShipDetailPanelInit (4), TestLayerExpansion (4), TestUpdateShip (4), TestClearElements (3), TestImageScaling (3), TestProcessEvent (3), and TestPanelKill (2) each construct the panel via `ShipDetailPanel.__new__(ShipDetailPanel)` after `patch.object(ShipDetailPanel, '__init__', ...)` then manually set `panel.expanded_layers`, `panel.ui_elements`, `panel.layer_buttons`, etc. This tests the panel's internal state machine without exercising `__init__`, meaning an `__init__` refactor that changes attribute names would silently miss these tests (they would still set the pre-refactor names).
- **Suggestion**: At minimum, add a comment documenting the coupling to internal attribute names. The pattern already uses the recommended `patch.object(__init__)` + `__new__` approach.
- **LOC affected**: ~200
- **Verified**: CONFIRMED

### tests/unit/research/research_scene/test_interaction.py

#### CAT-2: test_detect_cycles_called_during_init tests nothing real [MAJOR]
- **Location**: test_interaction.py:214-239
- **Issue**: `test_detect_cycles_called_during_init` creates `scene = MagicMock(spec=ResearchTreeScene)` (a mock of the SUT itself) then manually calls `mock_tree.detect_cycles()` on a separate MagicMock tree. It never instantiates `ResearchTreeScene` or exercises any real code path. The assertion `mock_tree.detect_cycles.assert_called_once()` trivially passes because the test body itself called `mock_tree.detect_cycles()` at line 236.
- **Suggestion**: Replace with a test that instantiates the real `ResearchTreeScene` and verifies `detect_cycles()` is called as a side effect of initialization.
- **LOC affected**: 25
- **Verified**: CONFIRMED

### tests/unit/strategy/fleet_navigation/test_service_edge_cases.py

#### CAT-4: Duplicate edge case tests for zero/negative speed [MINOR]
- **Location**: test_service_edge_cases.py:414-424
- **Issue**: `test_project_path_zero_speed` and `test_project_path_negative_speed` are identical except input speed value (0.0 vs -5.0) and both assert `service.project_path(fleet, galaxy) == []`.
- **Suggestion**: Parametrize into `@pytest.mark.parametrize("speed", [0.0, -5.0]) def test_project_path_invalid_speed_returns_empty`.
- **LOC affected**: 11
- **Verified**: CONFIRMED

### Cross-Shard: DUP-003 — Ship serialization roundtrip test pattern duplicated

- **Shard 08**: `tests/unit/ui/services/test_ship_io.py:395-541` — 7 round-trip tests (name, ship_class, team_id, color, component_count, movement_policy, recalculates_stats)
- **Shard 11**: `tests/unit/simulation/entities/test_ship_serialization.py:328-419` — 10 round-trip tests (name, ship_class, theme_id, team_id, color, movement_policy, component_count, component_ids, hull, stats)
- **Overlap**: name, ship_class, team_id, color, movement_policy, component_count — 6 properties tested in both files with identical pattern: `to_dict()` → `from_dict(data, registries=...)` → assert single property.
- **Recommendation**: Keep `test_ship_serialization.py` for raw Ship serialization tests. Remove overlapping property-preservation tests from `test_ship_io.py`, keeping only IO-layer-specific tests (file read/write, tmp_path handling).
- **Estimated LOC savings**: ~80
- **Verified**: CONFIRMED

### Cross-Shard: HLP-003 — `make_mock_ship_instance` local copy in test_advanced_fleet_orders.py

- **Canonical**: `tests/conftest.py:350-384` — accepts `name`, `owner_id`, `registries`; creates ShipInstance with instance_id, design_id, design_data; sets `_registries` if provided.
- **Shard 08 local**: `tests/unit/strategy/test_advanced_fleet_orders.py:20-39` — same signature, same logic (creates ShipInstance with same fields, sets `_registries` if provided). Near-identical structure.
- **Recommendation**: Delete the local copy in `test_advanced_fleet_orders.py` and import from root conftest.
- **Estimated LOC savings**: ~15
- **Verified**: CONFIRMED

## Disputed & Inconclusive Claims (for transparency)

| Original ID | File | CAT | Original Severity | Verdict | Reason |
|-------------|------|-----|-------------------|---------|--------|
| CAT-12 | tests/unit/simulation/test_battle_state_serialization.py:1348-1394 | CAT-12 | MINOR | DISPUTED | Claim states "for loops with nested list comprehensions and assertions inside the setup." The code at lines 1348-1394 contains no list comprehensions at all — only standard for loops building ShipState and ProjectileState objects. No assertions appear inside the for loops; the only assertions are at lines 1393-1394 (after all setup) checking result lengths. The test does have verbose setup (~47 lines) that could benefit from extraction into helpers, but the characterization of "nested list comprehensions" and "assertions inside setup" is contradicted by the source code. |
