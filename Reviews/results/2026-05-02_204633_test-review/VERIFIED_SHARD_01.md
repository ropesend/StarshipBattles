# Shard 01 — Verified Findings

## Summary
- Shard: 01
- Claims reviewed: 22 (Phase 1: 20, Cross-shard: 2)
- CONFIRMED: 21 | DISPUTED: 1 | INCONCLUSIVE: 0
- Severity downgrades: 1

## Verified Findings (CONFIRMED only)

### tests/integration/strategy/production/test_queue.py

#### CAT-1: test_production_progress  [CRITICAL]
- **Location**: test_queue.py:61-76
- **Issue**: Test body is entirely comments and `pass`. Zero assertions executed. The setup creates a planet and adds a production item, but the test never validates any behavior — it ends with a `pass` after a comment block explaining the test infrastructure is insufficient.
- **Suggestion**: Remove or implement — either delete the dead test or add actual assertions. If the workaround comment indicates refactoring is still needed, convert to `pytest.skip("Not yet implemented")`.
- **LOC affected**: 16
- **Verified**: CONFIRMED (severity kept)

### tests/unit/ai/test_ai.py

#### CAT-1: test_navigate_to_rotates_ship  [CRITICAL]
- **Location**: test_ai.py:124-136
- **Issue**: Test sets up `initial_angle = 0`, calls `navigate_to(target_pos)`, then ends with `pass # Rotation logic verified visually in game`. No assertion is made on the ship's angle after the call. The test provides zero automated regression protection.
- **Suggestion**: Add concrete assertion on `ship.angle` change, or remove the test and mark with `@pytest.mark.skip(reason="Visual verification only")`.
- **LOC affected**: 13
- **Verified**: CONFIRMED (severity kept)

#### CAT-6: test_attack_run_transitions_to_retreat  [MINOR]
- **Location**: test_ai.py:228-237
- **Issue**: Test depends on hardcoded spatial coordinates — ship at `(0,0)` and target at `(150,0)` — to trigger the `retreat` state transition. These magic numbers are coupled to `AttackRunBehavior.approach_distance` calculation (`range * 0.3 * hysteresis`). Changes to the distance constant would silently break this test.
- **Suggestion**: Mock the weapon_range to a known value so the approach distance is deterministic, or explicitly set ship position relative to the calculated threshold.
- **LOC affected**: 10
- **Verified**: CONFIRMED (severity kept)

### tests/unit/ui/test_race_portrait_gallery.py

#### CAT-2: All tests use __new__ bypassing __init__ — tests nothing real  [CRITICAL]
- **Location**: test_race_portrait_gallery.py:57-320
- **Issue**: All tests that create `RacePortraitGallery` instances (every test except the 2 Constants tests at lines 307-319) use `patch.object(RacePortraitGallery, '__init__', lambda self, *args, **kwargs: None)` followed by `RacePortraitGallery.__new__(RacePortraitGallery)` with manual attribute wiring. The real constructor is NEVER exercised. Any bug in `__init__` (e.g., missing attribute initialization, missing pygame_gui element creation) would pass unnoticed. The 2 Constants tests (test_has_thumb_size_constant, test_has_preview_size_constant) are exceptions — they test class-level constants without creating instances.
- **Suggestion**: Rewrite tests to instantiate RacePortraitGallery through its normal constructor with mocked pygame_gui dependencies, or delete the class-level test file in favor of integration tests that exercise the real widget.
- **LOC affected**: 240
- **Verified**: CONFIRMED (severity kept). Note: 2 Constants tests (lines 307-319) do NOT use the `__new__` pattern — they test class-level constants. This does not affect the validity of the finding for the remaining ~10+ tests.

### tests/unit/ui/test_race_description_panel.py

#### CAT-2: All tests use __new__ bypassing __init__ — tests nothing real  [MAJOR]
- **Location**: test_race_description_panel.py:39-271
- **Issue**: Same `patch.object(RaceDescriptionPanel, '__init__', ...)` + `__new__` anti-pattern as test_race_portrait_gallery.py. The real constructor is never called. However, the tests do exercise business logic (char counting at lines 71-126, config read/write at lines 132-271) through manually-wired mocked text boxes, providing partial value via mock.assert_called_with assertions on `bio_text_box.set_text`, `socio_text_box.set_text`, etc. Constructor integrity and pygame_gui element creation are entirely untested.
- **Suggestion**: Rewrite tests to use real construction with mocked pygame_gui, or migrate to integration-level tests.
- **LOC affected**: 230
- **Verified**: CONFIRMED (severity kept — MAJOR is appropriate since business logic is partially validated)

### tests/unit/builder/test_builder_improvements.py

#### CAT-1: test_image_scale_factor  [MINOR]
- **Location**: test_builder_improvements.py:25-42
- **Issue**: The test wraps `builder.draw(window)` in try/except/fail, asserting only that draw() does not raise an exception. It exercises real production code (DesignWorkshopScreen with real UIManager, real pygame draw calls) but asserts nothing about correctness of the rendering output. Downgraded from MAJOR — this is a legitimate smoke test: crash detection for the draw path is a valid test concern, and the code comment acknowledges the limitation that internal variables cannot be easily inspected.
- **Suggestion**: Add post-draw assertions (e.g., verify surface pixel values) or document as a smoke test and pair with a proper behavioral test.
- **LOC affected**: 18
- **Verified**: CONFIRMED (downgraded MAJOR → MINOR — legitimate smoke test exercising real pygame rendering; crash-detection is a valid test concern for UI code)

#### CAT-8: test_loading_sync  [MAJOR]
- **Location**: test_builder_improvements.py:44-126
- **Issue**: The test constructs a mock ship with ~45 attribute assignments (lines 56-110, ~59 LOC) before exercising the load_ship flow (~10 LOC of verification). Mock setup comprises ~84% of the test body.
- **Suggestion**: Extract mock-ship creation into a shared helper function. Reduce the test to mocking only the attributes that the SUT (`load_ship` → `_ship_io_adapter.load_ship`) actually reads.
- **LOC affected**: 83
- **Verified**: CONFIRMED (severity kept)

### tests/unit/modifiers/test_seeker_multi_ability.py

#### CAT-2: test_seeker_does_not_use_direct_stats_access  [MAJOR]
- **Location**: test_seeker_multi_ability.py:66-82
- **Issue**: Uses `inspect.getsource(SeekerWeaponAbility.recalculate)` to assert that string patterns (`self.component.stats.get`, `stats.get(`, `self.component.stats[`) do NOT appear in the source code. Tests source text, not runtime behavior. A refactored implementation using equivalent logic with different variable names would fail this test despite being correct.
- **Suggestion**: Remove the source inspection test. The behavioral tests (test_seeker_endurance_applies_modifier_correctly at line 84+) already verify correct output values via `get_effective_stat` mocking — making this test redundant and brittle.
- **LOC affected**: 17
- **Verified**: CONFIRMED (severity kept)

### tests/unit/ui/screens/battle_setup/test_fleet_hierarchy_editor.py

#### CAT-6: test_clone_ship_calls_ship_instance_create  [MAJOR]
- **Location**: test_fleet_hierarchy_editor.py:81-98
- **Issue**: Mocks `ShipInstance.create` to assert it was called with specific kwargs (`design_data`, `owner_id`, `name`). This encodes the internal call chain (`_clone_ship` → `ShipInstance.create` → specific kwargs). If the clone implementation switches to a different constructor or factory, this test fails even if cloning still works correctly. This is a change-detector.
- **Suggestion**: Verify the output — assert the cloned ship has the expected name, design_data, and owner_id — rather than asserting on the internal call to `ShipInstance.create`.
- **LOC affected**: 18
- **Verified**: CONFIRMED (severity kept)

#### CAT-1: test_editor_has_no_instance_state  [MINOR]
- **Location**: test_fleet_hierarchy_editor.py:232-244
- **Issue**: Creates an `FleetHierarchyEditor()` instance and asserts its `__dict__` (excluding dunders) is empty. Tests nothing about correctness — it verifies that a freshly-constructed object has no attributes set outside `__init__`, which is inherent to a stateless static-method class. No regression value.
- **Suggestion**: Remove. Alternatively, rename to `TestEditorStatelessProperty` and add a docstring explaining why no instance attributes is the expected contract.
- **LOC affected**: 13
- **Verified**: CONFIRMED (severity kept)

### tests/unit/strategy/facade/test_system_dto.py

#### CAT-10: DTO creation + frozen tests cluster  [MINOR]
- **Location**: test_system_dto.py:26-38 (test_create_star_info), test_system_dto.py:44-54 (test_create_warp_point_info), test_system_dto.py:72-113 (test_create_basic_system_info + test_create_full_system_info), test_system_dto.py:272-306 (test_create_planet_info + test_create_colonized_planet)
- **Issue**: 6 tests across 3 classes follow the identical pattern: construct a DTO, assert that each field has the expected value. Could be one parametrized test per DTO class.
- **Suggestion**: Consolidate into `@pytest.mark.parametrize` with (field_name, expected_value) tuples.
- **LOC affected**: 80
- **Verified**: CONFIRMED (severity kept)

### tests/unit/strategy/data/test_design_metadata_validation.py

#### CAT-10: Missing-field defaults cluster  [MINOR]
- **Location**: test_design_metadata_validation.py:49-77
- **Issue**: 5 tests with identical structure (delete a key, call `from_dict`, assert default value). Only the deleted key and expected default differ.
- **Suggestion**: Parametrize into a single test: `@pytest.mark.parametrize("key,default", [("ship_class", "Unknown"), ("vehicle_type", "Ship"), ("mass", 0.0), ("combat_power", 0.0), ("construction_cost", {})])`.
- **LOC affected**: 30
- **Verified**: CONFIRMED (severity kept)

### tests/unit/strategy/planet/test_planet_validation.py

#### CAT-10: test_missing_key_raises_persistence_exception cluster  [MINOR]
- **Location**: test_planet_validation.py:64-78 (parametrized missing_key) and test_planet_validation.py:94-116 (two partially-parametrized blocks for negative values)
- **Issue**: The validation tests for "negative values raise" on positive-only vs non-negative fields are split across two `@pytest.mark.parametrize` blocks using identical assertion patterns. Could be one parametrize block.
- **Suggestion**: Merge the two parametrize blocks with additional `expected_field` info, or leave as-is since they are already parametrized (just split across decorators).
- **LOC affected**: 20
- **Verified**: CONFIRMED (severity kept)

### tests/unit/strategy/services/test_fleet_navigation_mutual_pursuit.py

#### CAT-2: test_get_destination_default_self_fleet_is_none  [MINOR]
- **Location**: test_fleet_navigation_mutual_pursuit.py:175-186
- **Issue**: Uses `inspect.signature()` to verify that `self_fleet` parameter has `default=None`. Tests the code's signature text, not its behavior. If the parameter is renamed or moved, this test fails without catching a real bug.
- **Suggestion**: Replace with the behavioral test `test_no_self_fleet_falls_back_to_intercept` (line 152) which already verifies correct fallback behavior when `self_fleet=None`.
- **LOC affected**: 12
- **Verified**: CONFIRMED (severity kept)

### tests/repro_issues/repro_warp_bug.py

#### CAT-3: Standalone repro script for bugs already covered by proper tests  [MAJOR]
- **Location**: repro_warp_bug.py:1-79
- **Issue**: Standalone script with `print()` calls inside test functions and an `if __name__ == "__main__"` entry point. Both test functions (`test_repro_warp_point_creation_failure`, `test_repro_warp_point_ui_order_display`) are pytest-discoverable by naming convention, but are structured as a standalone reproduction script with print-based diagnostic output. Verified: `process_open_warp_point` is already covered by `tests/unit/strategy/engine/test_superweapon_order_processor.py`, `tests/unit/strategy/engine/test_superweapon_edge_cases.py`, and `tests/integration/strategy/test_superweapon_integration.py`. `_format_orders` is already covered by `tests/unit/ui/screens/test_strategy_detail_fmt.py` (15+ dedicated tests).
- **Suggestion**: Delete the file. The bugs are covered by proper pytest tests elsewhere.
- **LOC affected**: 79
- **Verified**: CONFIRMED (severity kept)

### tests/unit/strategy/data/test_data_layer_boundaries.py

#### CAT-2: Architectural AST guard — no behavioral test  [MINOR]
- **Location**: test_data_layer_boundaries.py:1-67
- **Issue**: Tests parse Python source files with `ast` and check import patterns. No production code paths are exercised; no `game.*` imports. This is a static analysis check, not a behavioral unit test.
- **Suggestion**: Keep as-is; note in file docstring that this is an AST guard, not a behavioral test. Consider moving to a `Tools/` linter or pre-commit hook.
- **LOC affected**: 67
- **Verified**: CONFIRMED (severity kept)

### tests/unit/strategy/services/test_ability_sources_no_global_registry_access.py

#### CAT-2: AST static-analysis guard — no behavioral test  [MINOR]
- **Location**: test_ability_sources_no_global_registry_access.py:1-67
- **Issue**: Same AST-scan pattern as test_data_layer_boundaries.py. No production code paths exercised. Parametrized across adapter files. PROJ-300 enforcement of DI compliance.
- **Suggestion**: Keep as-is; note in file docstring that this is an AST guard.
- **LOC affected**: 67
- **Verified**: CONFIRMED (severity kept)

### tests/unit/simulation/entities/test_ship_component_manager_di.py

#### CAT-2: Source-code content scan — no behavioral test  [MINOR]
- **Location**: test_ship_component_manager_di.py:1-29
- **Issue**: Opens source files (`ship_component_manager.py`, `ship_validator_helper.py`) and checks for string absence of `get_default_registry_provider`. No behavioral test. Tiny file, targeted DI enforcement.
- **Suggestion**: Keep as-is. If the scan logic is duplicated across multiple files, consider a shared helper.
- **LOC affected**: 29
- **Verified**: CONFIRMED (severity kept)

### tests/unit/strategy/engine/test_colonize_mission_handler.py

#### CAT-11: make_component_registry has duplicate key  [MINOR]
- **Location**: test_colonize_mission_handler.py:107-123
- **Issue**: The `make_component_registry()` helper defines the `'colony_pod'` key twice — lines 108-117 and 113-117 contain identical dict entries. The second overwrite is harmless at runtime (same value), but the dead duplication indicates a copy-paste error that may have been intended for a different component (e.g., `ice_dwarf_colony_pod`).
- **Suggestion**: Remove the duplicate `'colony_pod'` entry (lines 113-117).
- **LOC affected**: 6
- **Verified**: CONFIRMED (severity kept)

## Cross-Shard Verified Findings (CONFIRMED, Shard 01 files only)

### APC-001: `__new__` bypass-init pattern — test_race_portrait_gallery.py and test_race_description_panel.py
- **Verified**: CONFIRMED. Both files use `patch.object(ClassName, '__init__', lambda ...)` + `ClassName.__new__(ClassName)` + manual attribute wiring for all tests that create widget instances. Real constructors never exercised. Files are correctly identified as part of the 16-file cluster across 10 shards.

### APC-002: `inspect.getsource()` / `inspect.signature()` source inspection — test_seeker_multi_ability.py:66-82 and test_fleet_navigation_mutual_pursuit.py:175-186
- **Verified**: CONFIRMED. Both use inspect to analyze source code/signatures rather than testing runtime behavior. test_seeker_multi_ability.py uses `inspect.getsource()` to assert string patterns absent; test_fleet_navigation_mutual_pursuit.py uses `inspect.signature()` to verify parameter defaults. Both files correctly identified in the 11-file cluster.

## Disputed & Inconclusive Claims

| Original ID | File | CAT | Original Severity | Verdict | Reason |
|-------------|------|-----|-------------------|---------|--------|
| CAT-4: test_ship_stats_cargo_storage duplicates coverage | tests/unit/strategy/services/test_ship_stats_cargo_storage.py | CAT-4 | MAJOR | DISPUTED | Report claims "Both tests verify that cargo_storage aggregation works through `calculate_design_stats` — a path already exercised by `tests/unit/simulation/abilities/test_cargo_storage.py`." This is false: `test_cargo_storage.py` does NOT call `calculate_design_stats` (confirmed by grep — zero matches). It tests the CargoStorage ability class directly (creation, sync_data, recalculate, UI rows, registry). `test_ship_stats_cargo_storage.py` tests the design-stats aggregation pipeline (`calculate_design_stats`). These are different code paths at different pipeline stages and are NOT duplicates. Downgrade from MAJOR to NO FINDING recommended; the two tests within test_ship_stats_cargo_storage.py could be parametrized (1 component vs 2) but that is a consolidation issue, not a duplication issue. |
