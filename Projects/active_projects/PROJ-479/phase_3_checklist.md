# Phase 3: CAT-6 Mocking Brittleness

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-479 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace the 35 verified CAT-6 brittle-mock findings from review `2026-05-20_210550_test-review`. Each finding patches a private method/symbol or asserts on internal call chains, causing test breakage on legitimate refactors. Replace with public-boundary or behavioral assertions; for documented `__new__` bypass patterns (PROJ-322 / PROJ-347), accept the coupling per existing convention.

---

## Tasks

### Task 3.1: test_build_queue_panel_factory.py — blanket @fast_panel assertion
**File:** `tests/unit/ui/screens/test_build_queue_panel_factory.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_panel_factory.py`

- [ ] Replace blanket "every UIPanel uses @fast_panel" assertion (lines 170-206) with targeted per-logical-panel-group assertions, or downgrade to a warning rather than hard failure.
- [ ] Verify: `pytest tests/unit/ui/screens/test_build_queue_panel_factory.py` passes.

### Task 3.2: test_invalid_operation_handling.py — MagicMock-only modifier path
**File:** `tests/unit/modifiers/test_invalid_operation_handling.py`
**Tests:** `pytest tests/unit/modifiers/test_invalid_operation_handling.py`

- [ ] Replace MagicMock fleets/effects (lines 38-58) with real Modifier objects exercising the real path.
- [ ] Verify: `pytest tests/unit/modifiers/test_invalid_operation_handling.py` passes.

### Task 3.3: test_transfer_handler_fleet_to_fleet.py — closure stubs
**File:** `tests/unit/strategy/engine/test_transfer_handler_fleet_to_fleet.py`
**Tests:** `pytest tests/unit/strategy/engine/test_transfer_handler_fleet_to_fleet.py`

- [ ] Replace the MagicMock + lambda add_order + closure `_get_fleet_by_id` (lines 44-109) with a real Fleet and a minimal GameSession. _(verification adjusted from review's plain "use real Fleet" — adds the explicit guidance to drop the closure stubs. See verification_report.md.)_
- [ ] Verify: `pytest tests/unit/strategy/engine/test_transfer_handler_fleet_to_fleet.py` passes.

### Task 3.4: test_strategy_input_handler_core.py — private _click_dispatch mocks
**File:** `tests/unit/ui/screens/test_strategy_input_handler_core.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_input_handler_core.py`

- [ ] Replace `handler._click_dispatch._handle_picking = MagicMock()` pattern (lines 186-704) with `handle_click()` plus observable outcomes (mode changes, callbacks).
- [ ] Verify: `pytest tests/unit/ui/screens/test_strategy_input_handler_core.py` passes.

### Task 3.5: test_ship_component_manager.py — private cache invalidation calls
**File:** `tests/unit/builder/test_ship_component_manager.py`
**Tests:** `pytest tests/unit/builder/test_ship_component_manager.py`

- [ ] Replace direct `_invalidate_components_cache` call (line 441) + `_components_dirty` / `_weapons_cache_dirty` reads (444-445) with public Ship API: `add_component` / `remove_component` and verify via `get_all_components()` / `get_weapon_components_cached()`.
- [ ] Verify: `pytest tests/unit/builder/test_ship_component_manager.py` passes.

### Task 3.6: test_empire_build_queue_window.py — __init__ no-op + manual wiring
**File:** `tests/unit/ui/screens/test_empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [ ] Use the `bypass_init` pattern from `tests/fixtures/ui_widget_factory.py` instead of patching `__init__` with no-op lambda + manually wiring 30+ attrs (lines 63-100).
- [ ] Verify: `pytest tests/unit/ui/screens/test_empire_build_queue_window.py` passes.

### Task 3.7: test_build_queue_list_window.py — pygame_gui kill patches
**File:** `tests/unit/ui/screens/test_build_queue_list_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_list_window.py`

- [ ] Wrap pygame_gui UIWindow.kill behind an overridable method or extend bypass_init pattern (lines 264-280).
- [ ] Verify: `pytest tests/unit/ui/screens/test_build_queue_list_window.py` passes.

### Task 3.8: test_transfer_drop_pod.py — del planet.ships/.orders hack
**File:** `tests/unit/strategy/engine/test_transfer_drop_pod.py`
**Tests:** `pytest tests/unit/strategy/engine/test_transfer_drop_pod.py`

- [ ] Replace `del planet.ships` / `del planet.orders` (lines 22-23) with `MagicMock(spec=...)` that excludes those attributes (or use proper duck-typing).
- [ ] Verify: `pytest tests/unit/strategy/engine/test_transfer_drop_pod.py` passes.

### Task 3.9: test_order_processor_fleet_merge.py — internal recalc patch
**File:** `tests/unit/strategy/engine/test_order_processor_fleet_merge.py`
**Tests:** `pytest tests/unit/strategy/engine/test_order_processor_fleet_merge.py`

- [ ] Replace `trigger_speed_recalculation` patch (lines 31-62) with a behavior-based assertion on merged fleet speed (set speeds, verify merged is slowest).
- [ ] Verify: `pytest tests/unit/strategy/engine/test_order_processor_fleet_merge.py` passes.

### Task 3.10: test_hex_outlines.py — exact float literal asserts
**File:** `tests/unit/ui/screens/strategy_render/test_hex_outlines.py`
**Tests:** `pytest tests/unit/ui/screens/strategy_render/test_hex_outlines.py`

- [ ] Replace exact float literal assertions on `renderer._draw_inner_hex.call_args_list` (lines 101-106) with tolerance-based checks or property assertions. Test public API rather than private call list.
- [ ] Verify: `pytest tests/unit/ui/screens/strategy_render/test_hex_outlines.py` passes.

### Task 3.11: test_fleet_report_sidebar.py — 4-patch nested stack
**File:** `tests/unit/ui/screens/test_fleet_report_sidebar.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_sidebar.py`

- [ ] Replace the 4-patch nested stack (UILabel + UIButton ×2 + TriStateFilterWidget, lines 38-48) with a `make_ui_widget` factory or constructor DI.
- [ ] Verify: `pytest tests/unit/ui/screens/test_fleet_report_sidebar.py` passes.

### Task 3.12: test_characterization.py (consumable mgmt) — private passthrough
**File:** `tests/unit/strategy/consumable_management_engine/test_characterization.py`
**Tests:** `pytest tests/unit/strategy/consumable_management_engine/test_characterization.py`

- [ ] Remove the `_auto_disable_components_for_resource` mock (lines 92-101) and call the real method with real component definitions; assert correct disabling behavior.
- [ ] Verify: `pytest tests/unit/strategy/consumable_management_engine/test_characterization.py` passes.

### Task 3.13: test_event_log_window.py — _make_window no-op lambda
**File:** `tests/unit/ui/screens/test_event_log_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_event_log_window.py`

- [ ] Replace `_make_window` no-op `__init__` lambda + 10+ manually-wired attrs (lines 44-88) with real construction + bypass_init pattern.
- [ ] Verify: `pytest tests/unit/ui/screens/test_event_log_window.py` passes.

### Task 3.14: test_superweapon_order_processor.py — SuperweaponValidator patches (10+ tests)
**File:** `tests/unit/strategy/engine/test_superweapon_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_order_processor.py`

- [ ] Replace deep patching of `SuperweaponValidator.find_ship_with_ability` across 10+ tests (lines 131, 166, 201, 622, 669, 708, 748, 909, 1049, 1132) with dependency-injected stub validator at constructor level.
- [ ] Verify: `pytest tests/unit/strategy/engine/test_superweapon_order_processor.py` passes.

### Task 3.15: test_fleet_aura_cache.py — module-private function patch
**File:** `tests/unit/simulation/combat/test_fleet_aura_cache.py`
**Tests:** `pytest tests/unit/simulation/combat/test_fleet_aura_cache.py`

- [ ] Replace `_aggregate_ability_groups` private-function patch + call-count assertion (lines 83-88) with behavioral assertion on aggregation output.
- [ ] Verify: `pytest tests/unit/simulation/combat/test_fleet_aura_cache.py` passes.

### Task 3.16: test_orders_window.py — bypass_init smoke test
**File:** `tests/unit/ui/screens/test_orders_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_orders_window.py`

- [ ] Replace `_make_window` bypass_init + MagicMock ui_manager (lines 48-59) with real construction so constructor regressions are catchable.
- [ ] Verify: `pytest tests/unit/ui/screens/test_orders_window.py` passes.

### Task 3.17: test_reset_state.py — lambda shadows production method
**File:** `tests/unit/research/research_controls/test_reset_state.py`
**Tests:** `pytest tests/unit/research/research_controls/test_reset_state.py`

- [ ] Remove `panel.reset = lambda t, tt: rc.ResearchControlPanel.reset(panel, t, tt)` (line 30) — call real method directly.
- [ ] Verify: `pytest tests/unit/research/research_controls/test_reset_state.py` passes.

### Task 3.18: test_turn_engine_progress_callback.py — call_args_list exact equality
**File:** `tests/unit/strategy/engine/test_turn_engine_progress_callback.py`
**Tests:** `pytest tests/unit/strategy/engine/test_turn_engine_progress_callback.py`

- [ ] Replace `cb.call_args_list == expected` (lines 62-63) with `assert_has_calls()` + relaxed matchers, or loop over `call_args` extracting only stable fields.
- [ ] Verify: `pytest tests/unit/strategy/engine/test_turn_engine_progress_callback.py` passes.

### Task 3.19: test_ship_detail_panel.py — 23-test __init__ patch cluster
**File:** `tests/unit/ui/panels/test_ship_detail_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_ship_detail_panel.py`

- [ ] Audit the 23-test cluster (lines 131-521) using `patch.object(ShipDetailPanel, '__init__', ...)` + `__new__` + manual attrs. If PROJ-211/DI-compliance notes accept the pattern with a coupling comment, keep as-is; otherwise migrate to real construction. _(verification flagged as VERIFIED and acceptable per existing convention; this task confirms the convention.)_
- [ ] Verify: `pytest tests/unit/ui/panels/test_ship_detail_panel.py` passes; coupling comment present.

### Task 3.20: test_strategy_game_state_manager.py — patch.object on private methods
**File:** `tests/unit/ui/screens/test_strategy_game_state_manager.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_game_state_manager.py`

- [ ] Replace `patch.object(manager, ...)` on private `_apply_turn_start_state` / `_sync_active_empire` / `_capture_outgoing_player_state` (lines 521-648) with behavioral assertions on the public turn-advance path.
- [ ] Replace `_per_player_ui_state.load(...)` private-attr access (lines 1189-1231) with public state-restore API.
- [ ] Verify: `pytest tests/unit/ui/screens/test_strategy_game_state_manager.py` passes.

### Task 3.21: test_turn_engine_lazy_properties.py — inspect.getsource asserts
**File:** `tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py`

- [ ] Replace `inspect.getsource(...)` source-text containment asserts (lines 219-251) with a behavioral test (construct with `battle_resolver=None`, verify ValueError raised).
- [ ] Replace AST-parsing import-absence test (lines 262-288) with a static-guard test in `tests/static_guards/` or convert to a linter rule.
- [ ] Verify: `pytest tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py` passes.

### Task 3.22: test_order_processor_facade.py — AST attribute counting
**File:** `tests/unit/strategy/engine/order_handlers/test_order_processor_facade.py`
**Tests:** `pytest tests/unit/strategy/engine/order_handlers/test_order_processor_facade.py`

- [ ] Replace `ast.Attribute`-counting OrderType reference test (lines 32-57) with a behavioral test, or accept as architectural guard with a comment about false-positive risk.
- [ ] Verify: `pytest tests/unit/strategy/engine/order_handlers/test_order_processor_facade.py` passes.

### Task 3.23: test_race_browser_dialog.py — 12 bypass-init tests
**File:** `tests/unit/ui/test_race_browser_dialog.py`
**Tests:** `pytest tests/unit/ui/test_race_browser_dialog.py`

- [ ] Migrate the 12 `patch.object(__init__, no-op) + __new__ + manual attrs` tests (lines 78, 106, 132, 158, 172, 208, 233, 267, 290, 315, 333, 373) to the `bypass_init` fixture from `tests/fixtures/ui_widget_factory.py` (pattern already in use per PROJ-327).
- [ ] Verify: `pytest tests/unit/ui/test_race_browser_dialog.py` passes.

### Task 3.24: test_app_public_api.py — inspect.signature asserts
**File:** `tests/unit/test_app_public_api.py`
**Tests:** `pytest tests/unit/test_app_public_api.py`

- [ ] Replace `inspect.signature(Game.__init__)` param-name/default assertions (lines 39-47) with a behavioral test (call `Game()` with no args, verify no exception).
- [ ] Verify: `pytest tests/unit/test_app_public_api.py` passes.

### Task 3.25: test_race_summary_panel.py — __new__ + 12 private attrs
**File:** `tests/unit/ui/test_race_summary_panel.py`
**Tests:** `pytest tests/unit/ui/test_race_summary_panel.py`

- [ ] Replace `RaceSummaryPanel.__new__()` + 12+ private attr wirings (lines 391-411) with real `__init__` by providing all required pygame_gui fixtures to the constructor.
- [ ] Verify: `pytest tests/unit/ui/test_race_summary_panel.py` passes.

### Task 3.26: test_strategy_fleet_command_router.py — type().__name__ comparison
**File:** `tests/unit/ui/screens/test_strategy_fleet_command_router.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_fleet_command_router.py`

- [ ] Replace `type(command).__name__ == expected_cmd_class_name` (line 430) with `isinstance(command, ExpectedClass)` or `assert type(command) is ExpectedClass`.
- [ ] Verify: `pytest tests/unit/ui/screens/test_strategy_fleet_command_router.py` passes.

### Task 3.27: test_weapon_firing_system.py — positional call_args access
**File:** `tests/unit/simulation/combat/test_weapon_firing_system.py`
**Tests:** `pytest tests/unit/simulation/combat/test_weapon_firing_system.py`

- [ ] Replace `targeting.find_valid_target.call_args.args[2]` positional access (line 804) with `call_args.kwargs['secondary_targets']` or named extraction.
- [ ] Verify: `pytest tests/unit/simulation/combat/test_weapon_firing_system.py` passes.

### Task 3.28: test_cargo_quick_dialog_controller_widget_purity.py — call_args[0][0]
**File:** `tests/unit/ui/screens/test_cargo_quick_dialog_controller_widget_purity.py`
**Tests:** `pytest tests/unit/ui/screens/test_cargo_quick_dialog_controller_widget_purity.py`

- [ ] Replace `facade.handle_command.call_args[0][0]` (line 57) with `assert_called_once_with(cmd_instance)` or `call_args.args[0]` with explicit naming.
- [ ] Verify: `pytest tests/unit/ui/screens/test_cargo_quick_dialog_controller_widget_purity.py` passes.

### Task 3.29: test_order_types_characterization.py — module-level monkeypatch
**File:** `tests/unit/strategy/data/test_order_types_characterization.py`
**Tests:** `pytest tests/unit/strategy/data/test_order_types_characterization.py`

- [ ] Replace the module-level Planet/Fleet monkeypatch (lines 49-57) with a factory returning stubbed instances. Enables per-test customization.
- [ ] Verify: `pytest tests/unit/strategy/data/test_order_types_characterization.py` passes.

### Task 3.30: test_profiler_perf.py — inspect.getsource forbidden-string asserts
**File:** `tests/unit/core/profiling/test_profiler_perf.py`
**Tests:** `pytest tests/unit/core/profiling/test_profiler_perf.py`

- [ ] Replace `inspect.getsource` + "json.dump(" / "json.loads(" substring asserts (lines 53-61) with patching `json.dump` / `json.loads` at call site and asserting they're not called.
- [ ] Verify: `pytest tests/unit/core/profiling/test_profiler_perf.py` passes.

### Task 3.31: test_battle_panels_extended.py — sys.modules patch + importlib.reload
**File:** `tests/unit/ui/test_battle_panels_extended.py`
**Tests:** `pytest tests/unit/ui/test_battle_panels_extended.py`

- [ ] Factor `patch.dict(sys.modules, {'pygame': mock_pygame})` + `importlib.reload(battle_panels)` (lines 36-69) into a module-level fixture or context manager. Document reload hazards. Limit scope.
- [ ] Verify: `pytest tests/unit/ui/test_battle_panels_extended.py` passes.

### Task 3.32: test_action_execution_engine.py — ActionTimeResolver patch
**File:** `tests/unit/strategy/engine/test_action_execution_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_action_execution_engine.py`

- [ ] Add an injectable `ActionTimeResolver` parameter to `ActionExecutionEngine.__init__` with a sensible default. Update the 3 affected tests (lines 133-134, 187-189, 430-431) to pass a stub via constructor instead of patching internal path.
- [ ] Verify: `pytest tests/unit/strategy/engine/test_action_execution_engine.py` passes.

### Task 3.33: test_strategy_screen.py — 6 mock-only delegation tests
**File:** `tests/unit/ui/screens/test_strategy_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_screen.py`

- [ ] Replace 6 TestScreenLifecycle tests (lines 433-482) asserting only mock method calls with integration-level tests that assert observable state changes.
- [ ] Verify: `pytest tests/unit/ui/screens/test_strategy_screen.py` passes.

### Task 3.34: post-merge additions — verify canonical bypass_init use (6 files)
**Files:**
- `tests/unit/ui/screens/test_settings_window.py`
- `tests/unit/ui/screens/test_settings_window_modal.py`
- `tests/unit/ui/screens/test_atmosphere_target_editor.py`
- `tests/unit/ui/screens/test_gravity_target_editor.py`
- `tests/unit/ui/screens/test_radiation_shield_editor.py`
- `tests/unit/ui/screens/test_water_target_editor.py`

**Background:** Added to the audit set 2026-05-22 after merge `67116932d` landed PROJ-458 (Pattern #33 retrofit for 5 windows) and PROJ-470 (SettingsWindow StrategyModalWindow conformance). Each file already uses `tests/fixtures/ui_widget_factory.py:bypass_init` plus real assertions, so the expected outcome is no-op (verify only). If a file uses ad-hoc `__new__` wiring or shadows the canonical fixture, fix it under the existing CAT-6 contract.

**Tests:** `pytest tests/unit/ui/screens/test_settings_window.py tests/unit/ui/screens/test_settings_window_modal.py tests/unit/ui/screens/test_atmosphere_target_editor.py tests/unit/ui/screens/test_gravity_target_editor.py tests/unit/ui/screens/test_radiation_shield_editor.py tests/unit/ui/screens/test_water_target_editor.py`

- [ ] For each of the 6 files: confirm it imports `bypass_init` from `tests/fixtures/ui_widget_factory.py` (not a local `__new__` shim).
- [ ] For each: confirm Stage-1 cheap-state assertions exist under bypass (e.g. `_settings`, `_ui_builder` populated; widget handles NOT populated).
- [ ] For each: confirm Stage-2 production-path assertions exist (real widget construction observable via injected builder mock, not via patching widget element classes).
- [ ] If any violation is found, file a remediation task under the matching CAT-6 entry above. Otherwise mark complete with note "canonical pattern confirmed".
- [ ] Verify: pytest above all passes.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 4 — CAT-7 Sleep/Latency)

_Source review: `Reviews/results/2026-05-20_210550_test-review/`. See [findings/source_review.md](findings/source_review.md) for the link._
