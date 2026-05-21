# Shard 01 — Verified Findings

## Summary
- Shard: 01
- Claims reviewed: 26 (Phase 1: 23, Cross-shard: 3)
- CONFIRMED: 22 | DISPUTED: 2 | INCONCLUSIVE: 2
- Severity downgrades: 0
- Coverage overlap notes: 1 (informational, not a claim)

---

## Verified Findings (CONFIRMED only)

### tests/unit/ui/screens/test_workshop_screen.py

#### CAT-2: test_handle_event_delegates_to_event_router  [CRITICAL]
- **Location**: test_workshop_screen.py:236-247
- **Issue**: Installs `screen.handle_event = lambda e: screen.event_router.handle_event(e)` on a `__new__`-bypass instance, then calls it. Production `handle_event` (workshop_screen.py:409-415) is `return self.event_router.handle_event(event)` — functionally identical but the test never imports or executes the real method. A refactor of the production method would pass this test silently.
- **Suggestion**: Construct via real `__init__` or a bypass-init that retains real method implementations.
- **LOC affected**: 12
- **Verified**: CONFIRMED (severity kept — production method same shape but untested)

#### CAT-2: test_save_ship_delegates_to_ship_io  [CRITICAL]
- **Location**: test_workshop_screen.py:300-309
- **Issue**: Defines `screen._save_ship = lambda: screen.ship_io.save_ship()` and calls it. **Production class has `save_ship` (no underscore)** at workshop_screen.py:548-550. The test invents a phantom `_save_ship` method. Neither the name nor the body match production. Zero production code exercised.
- **Suggestion**: Remove or rewrite to call the real `save_ship` method.
- **LOC affected**: 10
- **Verified**: CONFIRMED (severity kept — tests phantom method, production method name differs)

#### CAT-2: test_load_ship_delegates_to_ship_io  [CRITICAL]
- **Location**: test_workshop_screen.py:311-320
- **Issue**: Same phantom-method pattern: invents `_load_ship` lambda; production is `load_ship` (workshop_screen.py:552-554).
- **Suggestion**: Remove or rewrite to exercise the real method.
- **LOC affected**: 10
- **Verified**: CONFIRMED (severity kept)

#### CAT-2: test_select_target_delegates_to_ship_io  [CRITICAL]
- **Location**: test_workshop_screen.py:322-331
- **Issue**: Invents `_on_select_target_pressed` lambda; production is `on_select_target_pressed` (workshop_screen.py:631-633). Phantom method.
- **Suggestion**: Remove or rewrite to exercise the real method.
- **LOC affected**: 10
- **Verified**: CONFIRMED (severity kept)

#### CAT-2: test_ship_property_returns_viewmodel_ship  [CRITICAL]
- **Location**: test_workshop_screen.py:264-272
- **Issue**: `type(screen).ship = property(lambda self: self.viewmodel.ship)` dynamically installs a property descriptor. Production `ship` property (workshop_screen.py:385-387) returns `self.viewmodel.ship` — identical logic but the test never touches the production descriptor. A future rename/removal of the property would not be detected.
- **Suggestion**: Exercise the real `ship` property as defined on the production class.
- **LOC affected**: 9
- **Verified**: CONFIRMED (severity kept — lambda mirrors production exactly, but still not production code)

#### CAT-2: test_selected_components_returns_viewmodel_selection  [CRITICAL]
- **Location**: test_workshop_screen.py:274-281
- **Issue**: Same dynamic-property-install pattern. Production property at workshop_screen.py:389-395.
- **Suggestion**: Exercise the real property.
- **LOC affected**: 8
- **Verified**: CONFIRMED (severity kept)

#### CAT-2: test_available_components_returns_viewmodel_available  [CRITICAL]
- **Location**: test_workshop_screen.py:283-290
- **Issue**: Same dynamic-property-install pattern. Production property at workshop_screen.py:397-403.
- **Suggestion**: Exercise the real property.
- **LOC affected**: 8
- **Verified**: CONFIRMED (severity kept)

#### CAT-2: test_selected_component_property_delegates_to_controller  [CRITICAL]
- **Location**: test_workshop_screen.py:396-410
- **Issue**: Same dynamic-property-install pattern. Production property at workshop_screen.py:368-374.
- **Suggestion**: Exercise the real property.
- **LOC affected**: 15
- **Verified**: CONFIRMED (severity kept)

#### CAT-2: test_dragged_item_property_delegates_to_controller  [CRITICAL]
- **Location**: test_workshop_screen.py:412-425
- **Issue**: Same dynamic-property-install pattern. Production property at workshop_screen.py:376-382.
- **Suggestion**: Exercise the real property.
- **LOC affected**: 14
- **Verified**: CONFIRMED (severity kept)

#### CAT-2: test_cleanup_clears_ui_manager  [CRITICAL]
- **Location**: test_workshop_screen.py:435-449
- **Issue**: Locally-defined `mock_cleanup` function replaces `screen.cleanup`. Production `cleanup` (workshop_screen.py:635-644) checks `if self.ui_manager: self.ui_manager.clear_and_reset()`. The mock does `if hasattr(screen, 'ui_manager') and screen.ui_manager: screen.ui_manager.clear_and_reset()` — similar intent but uses `hasattr` guard instead of truthiness check. Production code path never entered.
- **Suggestion**: Call the real `cleanup` method.
- **LOC affected**: 15
- **Verified**: CONFIRMED (severity kept)

#### CAT-2: test_handle_resize_updates_dimensions  [CRITICAL]
- **Location**: test_workshop_screen.py:451-467
- **Issue**: Locally-defined `mock_handle_resize` replaces `screen.handle_resize`. Production `handle_resize` (workshop_screen.py:417-428) sets width/height, calls `set_window_resolution`, and also recalculates `layer_panel_width`. The mock omits the `layer_panel_width` recalculation and any future-added logic. Production code not exercised.
- **Suggestion**: Call the real `handle_resize` method.
- **LOC affected**: 17
- **Verified**: CONFIRMED (severity kept — mock omits production logic)

#### CAT-2: test_clear_design_delegates_to_viewmodel  [CRITICAL]
- **Location**: test_workshop_screen.py:581-594
- **Issue**: Locally-defined `mock_clear_design` replaces `screen._clear_design`. Production `_clear_design` (workshop_screen.py:618-630) does 7 operations: `clear_design()`, `refresh_controls()`, `update_stats()`, `rebuild_modifier_ui()`, `selected_component = None`, `on_selection_changed(None)`, `clear_target()`. The mock does only 3 operations, omitting `update_stats()`, `rebuild_modifier_ui()`, `on_selection_changed(None)`, and `clear_target()`. Mock is not faithful to production behavior.
- **Suggestion**: Call the real `_clear_design` method.
- **LOC affected**: 14
- **Verified**: CONFIRMED (severity kept — mock diverges significantly from production)

#### CAT-2: test_apply_loaded_ship_updates_viewmodel  [CRITICAL]
- **Location**: test_workshop_screen.py:616-634
- **Issue**: Locally-defined `mock_apply_loaded_ship` replaces `screen._apply_loaded_ship`. Production `_apply_loaded_ship` (workshop_screen.py:556-567) does 7 operations including `update_stats()`, `rebuild_modifier_ui()`, and `logger.info(message)`. The mock does 4 operations, omitting `update_stats()`, `rebuild_modifier_ui()`, and logging. Mock is not faithful.
- **Suggestion**: Call the real `_apply_loaded_ship` method.
- **LOC affected**: 19
- **Verified**: CONFIRMED (severity kept — mock diverges from production)

---

### tests/unit/ui/screens/test_workshop_screen.py

#### CAT-8: test_init_standalone_mode_stores_context  [MINOR]
- **Location**: test_workshop_screen.py:185-191
- **Issue**: Helper `_make_context_standalone()` creates a `MagicMock()` and sets `is_standalone.return_value = True` + `mode = WorkshopMode.STANDALONE`. The assertions `screen.context.is_standalone()` and `screen.context.mode.value == "standalone"` both validate values set by the test helper itself — never exercises production `__init__` (which is patched to no-op at line 75). Tests the helper, not the SUT.
- **Suggestion**: Either construct via real `__init__` or delete.
- **LOC affected**: 7
- **Verified**: CONFIRMED (severity kept — pure self-referential assertion)

#### CAT-8: test_data_reloader_initialized  [MINOR]
- **Location**: test_workshop_screen.py:341-345
- **Issue**: Helper sets `screen.data_reloader = MagicMock()` at line 139. Test asserts `screen.data_reloader is not None`. `MagicMock()` is always truthy — assertion can never fail. Validates nothing about production behavior.
- **Suggestion**: Remove — tests nothing real.
- **LOC affected**: 5
- **Verified**: CONFIRMED (severity kept — tautological assertion)

#### CAT-9: Repeated mock/lambda definitions across TestWorkshopShipIO and TestWorkshopViewModelIntegration  [MINOR]
- **Location**: test_workshop_screen.py:297-331, 260-290
- **Issue**: Each test in `TestWorkshopShipIO` (lines 300-331) re-defines a lambda on `screen` to replace production methods. Each test in `TestWorkshopViewModelIntegration` (lines 264-290) dynamically installs a property descriptor. The `_make_workshop_screen` helper at line 68 already wires all mock dependencies; the per-test method-override boilerplate exists only because the bypass-init pattern strips production methods. Post-CAT-2 fixes, this boilerplate disappears.
- **Suggestion**: Restructure to use real methods — boilerplate vanishes.
- **LOC affected**: ~80
- **Verified**: CONFIRMED (severity kept — derivative of CAT-2 problems; verified pattern at cited lines)

---

### tests/unit/ui/screens/test_build_queue_helpers.py

#### CAT-10: TestFormatEmpireResources — cluster of 5 same-pattern tests  [MINOR]
- **Location**: test_build_queue_helpers.py:42-115
- **Issue**: `test_formats_resources_with_capacity`, `test_formats_resources_without_capacity`, `test_empty_empire_returns_no_resources`, `test_zero_values_not_shown`, `test_truncates_to_integers` — all follow identical structure: create `MagicMock()` empire, set `resource_pool` / `max_storage` on it, call `format_empire_resources(empire)`, assert on result string. Note: `test_uses_pipe_separator` (lines 65-73) also follows the same pattern but was not included in the claim — the cluster is actually 6 tests.
- **Suggestion**: Parameterize with `@pytest.mark.parametrize`.
- **LOC affected**: ~75
- **Verified**: CONFIRMED (severity kept — verified identical structure; actual cluster size is 6, not 5)

#### CAT-10: TestFormatResourceCost — cluster of 4 same-pattern tests  [MINOR]
- **Location**: test_build_queue_helpers.py:118-181
- **Issue**: `test_formats_single_resource`, `test_formats_multiple_resources`, `test_skips_zero_cost_resources`, `test_empty_cost_returns_empty_string` — identical structure: create cost dict, call `format_resource_cost(cost)`, assert on result. Note: `test_all_zero_costs_returns_empty_string` (lines 157-163), `test_truncates_to_integers` (165-171), and `test_uses_space_separator` (173-181) also follow the same pattern — the cluster is actually 7 tests.
- **Suggestion**: Parameterize.
- **LOC affected**: ~60
- **Verified**: CONFIRMED (severity kept — verified identical structure; actual cluster size is 7, not 4)

---

### tests/unit/ui/screens/test_fleet_report_window_multi_select.py

#### CAT-10: TestShipRemoval null-guard cluster  [MINOR]
- **Location**: test_fleet_report_window_multi_select.py:241-265
- **Issue**: `test_remove_does_nothing_without_empire` (sets `window.empire = None`), `test_remove_does_nothing_without_callback` (sets `window._split_fleet_callback = None`), `test_remove_does_nothing_with_empty_selection` (clears selection) — all three call `_on_remove_selected_ships()` and assert `callback.assert_not_called()`. Identical 4-line body with one varying precondition.
- **Suggestion**: Parameterize the null-condition.
- **LOC affected**: ~25
- **Verified**: CONFIRMED (severity kept)

---

### tests/regression/test_deprecated_code_removed.py

#### CAT-10: TestDeprecatedRegistryFunctionsRemoved — 4 identical-structure hasattr checks  [MINOR]
- **Location**: test_deprecated_code_removed.py:12-34
- **Issue**: `test_get_component_registry_removed`, `test_get_modifier_registry_removed`, `test_get_vehicle_classes_removed`, `test_get_resource_registry_removed` — all `import game.core.registry`, then `assert not hasattr(registry, <name>)` with a descriptive message. Identical 4-line bodies.
- **Suggestion**: Parameterize with function name strings.
- **LOC affected**: ~22
- **Verified**: CONFIRMED (severity kept)

#### CAT-10: TestGameStateAliasesRemoved — 4 identical-structure hasattr checks  [MINOR]
- **Location**: test_deprecated_code_removed.py:45-67
- **Issue**: `test_menu_alias_removed`, `test_builder_alias_removed`, `test_battle_alias_removed`, `test_settings_alias_removed` — all `import game.app`, then `assert not hasattr(app, <ALIAS>)` with descriptive message. Identical 4-line bodies (different module and names from the above cluster).
- **Suggestion**: Parameterize with alias name strings.
- **LOC affected**: ~22
- **Verified**: CONFIRMED (severity kept — separate module from the registry cluster above, warranting separate parameterization)

---

### tests/unit/systems/test_event_bus.py

#### CAT-10: TestEventBusValidation — cluster of 3 same-pattern tests for invalid subscribe inputs  [MINOR]
- **Location**: test_event_bus.py:43-65
- **Issue**: `test_subscribe_non_callable_raises_validation_exception` (string "not a callback"), `test_subscribe_none_raises_validation_exception` (None), `test_subscribe_integer_raises_validation_exception` (42) — identical pattern: create `WorkshopEventBus()`, subscribe with bad value, assert `ValidationException` raised. Note: the first test also asserts on `exc_info.value` message content; the other two do not.
- **Suggestion**: Parameterize with `@pytest.mark.parametrize("bad_value", [...])`.
- **LOC affected**: ~22
- **Verified**: CONFIRMED (severity kept — same structure despite minor assertion-count difference)

---

### tests/integration/resource_system/test_resource_pipeline.py

#### CAT-8: TestCustomResourceTypeFullPipeline — large fixture setup for narrow assertion  [MINOR]
- **Location**: test_resource_pipeline.py:22-95
- **Issue**: Single test `test_custom_resource_type_full_pipeline` spans 73 lines with 6 logical steps (JSON creation, resource loading, component creation, ship design creation, ship instantiation, consumption verification). Intermediate assertions exist at lines 48 and 80-81, contradicting the claim "only final asserts exist." However, the monolithic shape is real — a failure at step 1 would require debugging which sub-step failed rather than seeing a dedicated test name.
- **Suggestion**: Split into smaller unit-focused tests with explicit failure isolation.
- **LOC affected**: 73
- **Verified**: CONFIRMED (severity kept — monolithic shape verified; note intermediate assertions exist contrary to "only final asserts" claim in report)

---

## Cross-Shard Verified Findings

### DUP-001: `_make_fleet` / `_make_empire` helpers in combat round budget tests
- **Shard 01 file**: `tests/integration/strategy/test_combat_round_budget.py:75-91`
- **Verified**: CONFIRMED — `_make_fleet` (lines 75-84) creates `MagicMock()` with id, owner_id, location, speed, ships, task_forces, orders. `_make_empire` (lines 87-91) creates `MagicMock()` with id, fleets. Both match the described pattern of ~10-line MagicMock constructors. Cross-shard similarity to Shard 16/11 could not be independently verified (those files outside this shard) but the Shard 01 definition is exactly as described.
- **Note**: The "90% shared code" similarity claim across shards is accepted on the cross-shard reviewer's authority but not independently re-verified.

### DUP-004: ShipInstance serialization roundtrip duplication — DISPUTED (see Disputed table)

### HLP-004: `_make_fleet` — 43+ definitions
- **Shard 01 instance**: `tests/integration/strategy/test_combat_round_budget.py:75-84`
- **Verified**: CONFIRMED (for the Shard 01 instance). This file's `_make_fleet` creates `MagicMock()` with 7 fields (id, owner_id, location, speed, ships, task_forces, orders). Matches the described pattern. The claim of 43+ total definitions is a cross-shard aggregate that cannot be verified from this shard alone. The prevalence assessment is accepted on authority but unverified.

---

## Disputed & Inconclusive Claims

| Original ID | File | CAT | Original Severity | Verdict | Reason |
|-------------|------|-----|-------------------|---------|--------|
| DUP-004 | tests/unit/strategy/fleets/test_ship_instance_roundtrip.py | DUP | — | **DISPUTED** | Cross-shard report claims this file tests `ShipInstance.to_dict()` / `ShipInstance.from_dict()` dict serialization roundtrip. Actual file content (verified at lines 1-165) tests `to_ship()` / `update_from_ship()` — the bidirectional conversion between `ShipInstance` (strategy layer) and engine `Ship` (simulation layer) for component HP round-trip. This is **not** JSON/dict serialization; it's a distinct concern. Not a duplicate of Shard 16's `test_serialization.py` / `test_ship_instance_serializer.py`. |
| DUP-001 (cross-shard similarity) | tests/integration/strategy/test_combat_round_budget.py | DUP | — | **INCONCLUSIVE** | The Shard 01 file's `_make_fleet`/`_make_empire` helpers exist as described, but similarity to Shard 11 and Shard 16 counterparts could not be verified (those files are outside this shard). |
| HLP-004 (43+ count) | tests/integration/strategy/test_combat_round_budget.py | HLP | — | **INCONCLUSIVE** | The Shard 01 instance of `_make_fleet` is confirmed, but the aggregate claim of 43+ definitions with cross-shard similarity is unverifiable from this shard alone. |
| Coverage Overlap: Ship.stats/ShipStatsStrategy | tests/unit/simulation/systems/test_ship_stats_strategy_attributes.py | — | Informational | **Not a claim** | The cross-shard report's Coverage Overlap table is informational only and explicitly states "not duplicates." No verification needed. |

---

## Additional Observations (Non-Findings, Verification Notes)

### Pattern Prevalence in test_workshop_screen.py
Several additional tests in the same file also use the local-mock-override pattern but were not flagged by the Phase 1 reviewer:
- `test_show_error_sets_message_and_timer` (lines 371-386)
- `test_standalone_mode_includes_debug_buttons` (lines 477-504)
- `test_integrated_mode_excludes_debug_buttons` (lines 506-530)
- `test_update_decrements_error_timer` (lines 540-552)
- `test_update_calls_panel_updates` (lines 554-571)
- `test_get_vehicle_classes_returns_from_registries` (lines 216-226)
- `test_show_clear_confirmation_sets_pending_action` (lines 596-606)
- `test_update_stats_rebuilds_layer_panel` (lines 347-361)

These follow the identical pattern of defining a local function/lambda and assigning it to `screen.<method>`. The CAT-2 problem is more pervasive than the 13 flagged tests — approximately 20 of the ~30 tests in this file use the pattern. This does not require new claims (per instructions) but documents the scope for remediation planning.

### Verifier Note on "Phantom Method" Severity
Three CAT-2 claims (test_save_ship_delegates_to_ship_io, test_load_ship_delegates_to_ship_io, test_select_target_delegates_to_ship_io) test method names (`_save_ship`, `_load_ship`, `_on_select_target_pressed`) that do not exist in production at all. The production methods are `save_ship`, `load_ship`, `on_select_target_pressed` (no leading underscore). This is arguably MORE severe than CAT-2 (testing a replacement mock for a real method) — these tests are testing entirely fictional code. The CRITICAL severity is maintained but the underlying problem is a method-name mismatch, not merely a mock substitution.

### test_workshop_screen.py Line 75 `__init__` Patch
```python
with patch.object(DesignWorkshopScreen, '__init__', lambda self, *a, **kw: None):
    screen = DesignWorkshopScreen.__new__(DesignWorkshopScreen)
```
The `@patch.object` context manager restores `__init__` after the `with` block exits, meaning the class is not permanently damaged. However, the screen instance created inside this block has no production initialization at all — every attribute is manually assigned by `_make_workshop_screen` (lines 76-173). This is the root cause of all 13 CAT-2 findings.

