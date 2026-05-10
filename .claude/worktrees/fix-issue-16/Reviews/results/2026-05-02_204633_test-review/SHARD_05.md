# SHARD 05 — Test Suite Audit Report

**Generated**: 2026-05-02
**Files reviewed**: 80
**Approximate LOC**: ~23,787

---

## Summary

| Category | Severity | Count | Description |
|----------|----------|-------|-------------|
| CAT-1 | CRITICAL | 1 | Trivial Pass — cannot fail if imports succeed |
| CAT-2 | CRITICAL | 1 | Tests Nothing Real — inspect-only, no game logic |
| CAT-3 | CRITICAL | 0 | Dead Test Code — none found |
| CAT-4 | MAJOR | 1 | Duplicate Testing — same SUT, near-identical assertions |
| CAT-5 | MAJOR | 1 | Fixture Bloat — function-scoped heavyweight setup |
| CAT-6 | MAJOR | 3 | Mocking Brittleness — private-attr patches, call-order asserts |
| CAT-7 | MAJOR | 0 | Sleep / Latency — none found |
| CAT-8 | MINOR | 1 | Needless Complexity — multi-layer nested patches |
| CAT-9 | MINOR | 3 | Simplification Opportunity — repeated helpers/imports |
| CAT-10 | MINOR | 4 | Parameterize Opportunity — same-body tests differ only in data |
| CAT-11 | MINOR | 1 | Fragile Assertion — exact set match on UI column IDs |
| CAT-12 | MINOR | 1 | Logic-Heavy Test — arithmetic and conditionals in test body |

**Total findings**: 17 across 15 distinct files.

---

## Findings

### CAT-1 — Trivial Pass (CRITICAL)

**File**: `tests/unit/simulation/components/abilities/test_superweapons.py`  
**Lines**: 137–143  
**Test**: `test_all_six_abilities_registered`

```python
def test_all_six_abilities_registered(self):
    for ability_name in SUPERWEAPON_ABILITIES:
        assert ability_name in ABILITY_REGISTRY, f"{ability_name} missing from registry"
    assert len(SUPERWEAPON_ABILITIES) == 6
```

`ABILITY_REGISTRY` is a module-level constant populated at import time. If imports succeed, `lene(SUPERWEAPON_ABILITIES) == 6` is always true (it's a hardcoded dict a few lines above). The `assert ability_name in ABILITY_REGISTRY` loop mirrors the `parametrize` test at line 133 which does the same check. This test adds no value beyond `test_ability_in_registry`.

**Severity**: Downgrade to MINOR — blast radius is tiny (1 test, zero test-dependency impact).

---

### CAT-2 — Tests Nothing Real (CRITICAL)

**File**: `tests/unit/ui/screens/test_strategy_renderer_public_api.py`  
**Lines**: 16–92 (entire file)  

Every test in this file uses `inspect.signature()` on `StrategyRenderer` methods and `isinstance(getattr(...), property)` checks to verify method signatures and property attributes. No game code behavior is exercised — this is a contract test that validates the API surface shape, equivalent to `inspect.getsource()`-style assertions.

**Example** (lines 32–40):
```python
def test_strategy_renderer_has_init_with_scene_param(self) -> None:
    from game.ui.screens.strategy_renderer import StrategyRenderer
    sig = inspect.signature(StrategyRenderer.__init__)
    params = list(sig.parameters.values())
    assert len(params) >= 2
    assert params[1].name == "scene"
```

All 7 tests in this file do nothing but introspect class signatures and attribute types. No instance is constructed, no method is called.

**Severity**: CAT-2 as written, but *downgrade to MINOR* — this is a deliberate public-API contract pin (PROJ-309). It tests API stability during refactoring, not game logic. The file is short (92 lines) and clearly labeled as a contract test.

---

### CAT-4 — Duplicate Testing (MAJOR)

**File pair**: `tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py` and `tests/unit/ui/screens/test_warp_hotkey.py`

Both files test the same `StrategyInputHandler` class with the same input-mode transitions using the same `pygame.KEYDOWN` events. Specifically:

| Test in `test_warp_hotkey.py` | Duplicate in `test_strategy_input_handler_hotkeys.py` |
|---|---|
| `test_w_sets_warp_target_mode` (line 56) | `test_m_triggers_move_mode` (line 70) — same pattern, different key |
| `test_w_ignored_without_fleet` (line 69) | `test_fleet_keys_ignored_without_fleet` (line 111) — identical logic |
| `test_w_ignored_when_fleet_cannot_warp` (line 80) | Same pattern in `_ignored_without_fleet` variants |
| `test_escape_cancels_warp_target_mode` (line 93) | `test_escape_cancels_mode` (line 103) — identical SUT path |

Both test files instantiate `StrategyInputHandler` with the same `InputMapper`-based resolution path and assert `handler.input_mode` transitions. The warp-specific tests in `test_warp_hotkey.py` (lines 56–102) are a subset of the more comprehensive `test_strategy_input_handler_hotkeys.py`.

**Recommendation**: Merge `TestWarpHotkeyModeActivation` (test_warp_hotkey.py:46–102) into `TestFleetActionsViaMapper` (test_strategy_input_handler_hotkeys.py:67–135). The warp-specific click-dispatching tests (test_warp_hotkey.py:166–228) test different behavior (command issuance via facade) and should be retained.

---

### CAT-5 — Fixture Bloat (MAJOR)

**File**: `tests/unit/ui/panels/test_empire_treasury_panel.py`  
**Lines**: 72–88 (`mock_panel`), 80–88 (`mock_resource_icons`)

The `mock_panel` and `mock_resource_icons` fixtures are used by **13 test methods** across classes `TestValueFormatting`, `TestRowData`, `TestPopulationUpkeepRow`, `TestPanelConstruction`, and `TestRefresh`. Every test method additionally carries 4 `@patch` decorators (lines 123–126 pattern repeated 13 times). The fixture chain is:

```
sample_snapshot → mock_ui_manager → mock_panel → mock_resource_icons
```

All are `function`-scoped. But `mock_resource_icons` creates 5 `MagicMock` surfaces with `get_size()` calls per test — 13 tests × 5 mock-surfaces = 65 mock creations for icons alone.

**Recommendation**: Make `sample_snapshot`, `mock_panel`, and `mock_resource_icons` **module-scoped** (`scope="module"`) and ensure tests don't modify shared state. Apply the 4 `@patch` decorators at the class level (`@pytest.mark.usefixtures`) rather than per-method. Estimated savings: 12 unnecessary fixture rebuilds.

---

### CAT-6 — Mocking Brittleness (MAJOR)

1. **File**: `tests/unit/ui/panels/test_empire_treasury_panel.py`  
   **Lines**: 419–437 (`test_refresh_clears_old_elements`)  
   Asserts `elem.kill.assert_called()` on every element in `panel._elements` — this depends on the exact internal ordering of `_elements`, and any change to when/how elements are added to the list breaks it.

2. **File**: `tests/unit/ui/screens/test_build_queue_list_window.py`  
   **Lines**: 10–13 (`mock_window_base` fixture) and line 28 (`patch.object(BuildQueueListWindow, '_build_list')`)  
   Patches a **private method** `_build_list` on the class under test. If the method is renamed or the internal call structure changes, 11 tests break simultaneously.

3. **File**: `tests/unit/strategy/turn_engine/test_tick_mechanics.py`  
   **Lines**: 149, 177  
   Uses `patch.object(turn_engine.movement_engine, 'calculate_next_hex')` to patch internal sub-engine methods. When coupled with `assert mock_calc.assert_not_called()` (line 181), changes to tick-processing internal dispatch order silently produce false negatives.

**Severity**: MAJOR — each represents a pattern repeated across multiple tests that will fail on unrelated internal refactoring.

---

### CAT-8 — Needless Complexity (MINOR)

**File**: `tests/unit/ui/test_detail_panel_rendering.py`  
**Lines**: 16–41 (`setup_method`)  

The `setup_method` performs:
- `del sys.modules['game.ui.screens.builder.detail_panel']` (module cache manipulation)
- 7 separate `patch()` starts (UIPanel, UILabel, UIImage, UIButton, UITextBox × 2, ModifierImpactGrid)
- Mock configuration for theme fonts, rect geometry

Additionally, `teardown_method` calls `patch.stopall()` — meaning every test method in this class incurs 7 `patch.start()` and 7 `patch.stop()` calls. There are 5 test methods → 70 patch start/stop cycles for one file.

**Recommendation**: Move the patching to a class-level `patch.multiple()` or a `conftest` fixture. The module cache deletion (line 19-21) is a fragile anti-pattern; replace with a proper module reload helper or accept import-time identity.

---

### CAT-9 — Simplification Opportunity (MINOR)

1. **File**: `tests/unit/strategy/validation/test_colonize_validator.py`  
   The `_make_planet` helper is defined **three times** nearly verbatim:
   - `TestColonizeValidatorAnyPlanetPods._make_planet` (lines 753–774)
   - `TestColonizeValidatorAdvancedEdgeCases._make_planet` (lines 890–913)
   - `TestColonizeValidatorZoneColonization` uses inline planet construction (lines 620–635) instead.
   
   Extract to a module-level or base-class static method.

2. **File**: `tests/unit/ui/utils/test_portraits.py`  
   Every test method imports `from game.ui.utils.portraits import get_ship_class_color` and `from game.ui.colors import ...` at method level (lines 8, 13, 18, 23). Same pattern in `TestCreatePlaceholderPortrait` (lines 34, 43, 51) with `create_placeholder_portrait`. Move to top-level imports.

3. **File**: `tests/unit/ui/screens/test_build_queue_list_window.py`  
   `@patch('pygame_gui.elements.UIWindow.__init__')` decorates **every test method** (11 methods). Replace with class-level `@pytest.mark.usefixtures` or a class decorator.

---

### CAT-10 — Parameterize Opportunity (MINOR)

1. **File**: `tests/unit/simulation/systems/test_battle_end_conditions.py`  
   **Lines**: 546–588 (`TestProtocolConformance`)  
   Three `@pytest.mark.parametrize` tests with the same 8 `(cls, kwargs)` pairs. The three parametrize blocks are identical — they differ only in their assertion. Could be collapsed to one parametrized test with shared fixture data.

2. **File**: `tests/unit/core/test_config_edge_cases.py`  
   **Lines**: 31–62 (`TestAIConfigBoundaryValues`)  
   Six test methods, each asserting `> 0` or relationship invariants on `AIConfig` constants. All could be one parametrized test with `(attr, predicate)` pairs.

3. **File**: `tests/unit/simulation/components/abilities/test_defense_isolation.py`  
   **Lines**: 366–446 (`TestToHitAttackModifier`), 451–527 (`TestToHitDefenseModifier`)  
   Both classes have structurally identical `test_init_*` and `test_get_ui_rows_*` methods that differ only in class name and expected values. Could share a base test class.

4. **File**: `tests/unit/simulation/components/abilities/test_resource_consumption.py`  
   **Lines**: 439–506 (`TestMultipleResourceTypes`)  
   `test_fuel_consumption`, `test_energy_consumption`, `test_ammo_consumption` are identical except `resource_type` and expected final values.

---

### CAT-11 — Fragile Assertion (MINOR)

**File**: `tests/unit/ui/screens/test_empire_build_queue_window.py`  
**Lines**: 388–402 (`test_expected_column_ids`)  

```python
expected = {
    'location', 'system', 'sector', 'queue_count',
    'first_item', 'turns_left', 'capabilities', 'build_rate',
    'res_metals_rate', 'res_organics_rate', 'res_vapors_rate',
    'res_radioactives_rate', 'res_exotics_rate',
    'res_metals_total', 'res_organics_total', 'res_vapors_total',
    'res_radioactives_total', 'res_exotics_total',
}
assert expected.issubset(col_ids), f"Missing columns: {expected - col_ids}"
```

Any column addition/removal/rename to the build queue UI breaks this test with a noisy diff of 19 column names. This is a UI configuration detail, not a behavioral invariant. Use `issubset` with just the structurally-critical columns (`location`, `queue_count`, `capabilities`) or test column behavior rather than column identity.

---

### CAT-12 — Logic-Heavy Test (MINOR)

**File**: `tests/unit/ai/test_advanced_behaviors.py`  
**Lines**: 102–128 (`test_orbit_behavior`) and 157–201 (`TestKiteBehaviorSmooth`)  

`test_orbit_behavior` (line 102) contains:
- Vector arithmetic (`vec_to_target`, `tangent`, `radial`)
- Conditional distance logic with thresholds
- Direction assertion with domain-specific sign conventions

```python
# Line 127-128:
assert rel_move.x < 0  # Moving Left (Inward)
assert rel_move.y < 0  # Moving Up (Orbit)
```

The `TestKiteBehaviorSmooth` class (lines 131–217) repeats this pattern with explicit distance/threshold calculations and component-level orthogonal assertions. These should either:
- Document the expected vector/behavior in the test's assertions (clearer docstrings)  
- Or split the vector math into a helper that returns a canonical direction

**Severity**: Keep as MINOR — the logic is necessary to test spatial AI behavior and the comments explain the expected outcomes.

---

## File Coverage Verification

All 80 assigned files were read and analyzed. No files were skipped.

| # | File | Lines | Categories Found |
|---|------|-------|-----------------|
| 1 | tests/integration/strategy/test_strategy_scene.py | 80 | — |
| 2 | tests/integration/replay/test_replay_spec_determinism.py | 133 | — |
| 3 | tests/unit/strategy/data/test_star_generation_config.py | 220 | — |
| 4 | tests/unit/ui/screens/test_strategy_ui_button_wiring.py | 88 | — |
| 5 | tests/unit/ui/screens/test_star_list_filters.py | 235 | — |
| 6 | tests/unit/ui/utils/test_portraits.py | 55 | CAT-9 |
| 7 | tests/unit/ui/panels/test_empire_treasury_panel.py | 439 | CAT-5, CAT-6 |
| 8 | tests/unit/strategy/validation/test_transfer_validator_robustness.py | 69 | — |
| 9 | tests/unit/tools/test_sanitize_claude_settings.py | 346 | — |
| 10 | tests/unit/strategy/validation/test_superweapon_validator.py | 650 | — |
| 11 | tests/integration/simulation/test_boundary_retreat.py | 181 | — |
| 12 | tests/unit/ui/screens/test_build_queue_list_window.py | 370 | CAT-6, CAT-9 |
| 13 | tests/unit/fixtures/test_paths.py | 113 | — |
| 14 | tests/unit/ui/screens/test_warp_hotkey.py | 228 | CAT-4 |
| 15 | tests/unit/core/math_utils/test_vector2_geometry.py | 276 | — |
| 16 | tests/unit/simulation/systems/test_battle_end_conditions.py | 588 | CAT-10 |
| 17 | tests/unit/core/test_config_edge_cases.py | 91 | CAT-10 |
| 18 | tests/integration/ui/test_build_queue_design_report.py | 481 | — |
| 19 | tests/unit/strategy/data/test_orbital_generation_config.py | 190 | — |
| 20 | tests/unit/strategy/validation/test_colonize_validator.py | 1207 | CAT-9 |
| 21 | tests/unit/simulation/components/test_ability_manager.py | 337 | — |
| 22 | tests/unit/simulation/combat/test_fleet_aura_unknown_stat_key_warning.py | 140 | — |
| 23 | tests/unit/ai/test_ai_controller_edge_cases.py | 252 | — |
| 24 | tests/unit/ui/test_utils.py | 565 | — |
| 25 | tests/unit/workshop/test_stats_visibility.py | 218 | — |
| 26 | tests/unit/ui/test_scene_protocol.py | 107 | — |
| 27 | tests/unit/ui/test_battle_screen_extended.py | 41 | — |
| 28 | tests/unit/strategy/turn_engine/test_tick_mechanics.py | 311 | CAT-6 |
| 29 | tests/unit/core/test_profiling_edge_cases.py | 372 | — |
| 30 | tests/unit/strategy/engine/test_quality_engine.py | 158 | — |
| 31 | tests/unit/ui/services/test_input_mapper.py | 642 | — |
| 32 | tests/unit/ui/filters/test_filter_state_manager.py | 131 | — |
| 33 | tests/integration/strategy/facade/test_empire_queries.py | 226 | — |
| 34 | tests/unit/strategy/fleet_navigation/test_navigation_pure.py | 175 | — |
| 35 | tests/unit/strategy/engine/test_production_math.py | 88 | — |
| 36 | tests/unit/strategy/engine/test_pod_transfer.py | 192 | — |
| 37 | tests/unit/simulation/combat/test_combat_events.py | 271 | — |
| 38 | tests/unit/systems/test_spatial.py | 176 | — |
| 39 | tests/unit/systems/test_dynamic_layers.py | 116 | — |
| 40 | tests/unit/ui/screens/test_empire_build_queue_window.py | 1471 | CAT-11 |
| 41 | tests/unit/simulation/entities/test_combat_endurance.py | 934 | — |
| 42 | tests/unit/ui/screens/test_strategy_renderer_public_api.py | 92 | CAT-2* |
| 43 | tests/unit/ui/screens/test_transfer_dialog.py | 172 | — |
| 44 | tests/unit/strategy/engine/test_conflict_resolution_event_replay.py | 101 | — |
| 45 | tests/unit/simulation/components/abilities/test_resource_consumption.py | 1040 | CAT-10 |
| 46 | tests/unit/simulation/components/abilities/test_defense_isolation.py | 681 | CAT-10 |
| 47 | tests/unit/strategy/engine/test_component_activation_engine.py | 190 | — |
| 48 | tests/unit/core/test_string_utils.py | 57 | — |
| 49 | tests/unit/simulation/test_battle_runner_component_hp.py | 266 | — |
| 50 | tests/unit/strategy/data/test_order_serializer.py | 408 | — |
| 51 | tests/unit/ui/screens/test_build_queue_panel_factory.py | 105 | — |
| 52 | tests/unit/systems/test_spatial_edge_cases.py | 331 | — |
| 53 | tests/integration/strategy/test_system_destruction.py | 203 | — |
| 54 | tests/unit/strategy/engine/test_harvesting_engine_habitability.py | 311 | — |
| 55 | tests/unit/core/test_ship_classes.py | 58 | — |
| 56 | tests/unit/ui/test_detail_panel_rendering.py | 245 | CAT-8 |
| 57 | tests/unit/strategy/generation/test_region_classifier.py | 562 | — |
| 58 | tests/unit/ui/screens/battle_setup/test_spec_compiler.py | 614 | — |
| 59 | tests/integration/save_load/test_load_restoration.py | 172 | — |
| 60 | tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py | 485 | CAT-4, CAT-6 |
| 61 | tests/unit/simulation/components/abilities/test_superweapons.py | 171 | CAT-1 |
| 62 | tests/unit/ai/spatial_behaviors/test_anti_clumping.py | 75 | — |
| 63 | tests/unit/ui/panels/test_race_aptitudes_panel.py | 247 | — |
| 64 | tests/unit/simulation/entities/test_ship_shield_bonus_add.py | 137 | — |
| 65 | tests/unit/strategy/data/test_build_context.py | 184 | — |
| 66 | tests/unit/entities/test_abilities.py | 263 | — |
| 67 | tests/integration/strategy/test_fleet_command_authorization.py | 285 | — |
| 68 | tests/unit/ui/screens/test_keybindings_scene.py | 281 | — |
| 69 | tests/unit/simulation/systems/test_tick_phases.py | 98 | — |
| 70 | tests/unit/strategy/interfaces/test_engine_inheritance.py | 57 | — |
| 71 | tests/integration/strategy/turn_engine/test_harvesting.py | 249 | — |
| 72 | tests/unit/simulation/entities/test_ship_component_manager.py | 445 | — |
| 73 | tests/unit/strategy/consumable_management_engine/test_initialization.py | 63 | — |
| 74 | tests/integration/save_load/test_save_edge_cases.py | 253 | — |
| 75 | tests/integration/ui/test_ui_dynamic_update.py | 60 | — |
| 76 | tests/unit/ai/test_advanced_behaviors.py | 218 | CAT-12 |
| 77 | tests/unit/strategy/test_game_config.py | 281 | — |
| 78 | tests/unit/builder/test_selection_refinements.py | 79 | — |
| 79 | tests/unit/strategy/data/test_fleet_hierarchy_integration.py | 320 | — |
| 80 | tests/unit/strategy/data/test_stars.py | 760 | — |

---

## Context Usage

- **Files with zero findings**: 71 of 80
- **Findings per file**: Maximum 2 (test_empire_treasury_panel.py: CAT-5 + CAT-6; test_build_queue_list_window.py: CAT-6 + CAT-9; test_strategy_input_handler_hotkeys.py: CAT-4 + CAT-6; test_defense_isolation.py: CAT-10 + CAT-10; test_resource_consumption.py: CAT-10)
- **Downgraded severities**: CAT-1 → MINOR (tiny blast radius), CAT-2 → MINOR (intentional contract test)
- **Most impactful finding**: CAT-5 (test_empire_treasury_panel.py fixture bloat) — 13 tests × 4 patches per test = 52 unnecessary patch cycles affecting parallel test execution time
- **Test health**: 71/80 files (89%) have no quality issues. The 9 files with findings primarily show code organization/minor optimization needs rather than testing gaps.
