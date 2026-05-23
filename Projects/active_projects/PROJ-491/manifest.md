# PROJ-491 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| tests/fixtures/ui_widget_factory.py | Test fixture | READ — canonical `bypass_init` lives at lines 254-328 (line 20-28 is `make_ui_widget`) |
| game/strategy/engine/action_execution_engine.py | Production READ | Phase 3 — verify DI seam still exists at lines 55-68 / 183-192 |
| tests/unit/ui/screens/test_build_queue_panel_factory.py | Test | Task 3.1 — blanket @fast_panel assertion |
| tests/unit/modifiers/test_invalid_operation_handling.py | Test | Task 3.2 — MagicMock-only modifier path |
| tests/unit/strategy/engine/test_transfer_handler_fleet_to_fleet.py | Test | Task 3.3 — closure stubs (may need real Fleet; verify on entry). Also touched by PROJ-492 Phase 2 (_make_fleet sweep). |
| tests/unit/ui/screens/test_strategy_input_handler_core.py | Test | Task 3.4 — private _click_dispatch mocks |
| tests/unit/builder/test_ship_component_manager.py | Test | Task 3.5 — private cache invalidation calls |
| tests/unit/ui/screens/test_empire_build_queue_window.py | Test | Task 3.6 — __init__ no-op + manual wiring |
| tests/unit/ui/screens/test_build_queue_list_window.py | Test | Task 3.7 — pygame_gui kill patches (file already uses bypass_init for some tests) |
| tests/unit/strategy/validation/test_transfer_drop_pod.py | Test | Task 3.8 — del planet.ships/.orders hack (PROJ-479 listed engine/ path; actual is validation/) |
| tests/unit/strategy/engine/test_turn_engine_progress_callback.py | Test | Task 1.3 — verify-only (already done in PROJ-479) |
| tests/unit/strategy/engine/test_order_processor_fleet_merge.py | Test | Task 3.9 — internal recalc patch |
| tests/unit/ui/screens/strategy_render/test_hex_outlines.py | Test | Task 3.10 — exact float literal asserts |
| tests/unit/ui/screens/test_fleet_report_sidebar.py | Test | Task 3.11 — 4-patch nested stack |
| tests/unit/strategy/consumable_management_engine/test_characterization.py | Test | Task 3.12 — private passthrough |
| tests/unit/ui/screens/test_event_log_window.py | Test | Task 3.13 — _make_window no-op lambda |
| tests/unit/simulation/combat/test_fleet_aura_cache.py | Test | Task 3.15 — module-private function patch |
| tests/unit/ui/screens/test_orders_window.py | Test | Task 3.16 — bypass_init smoke test (real construction) |
| tests/unit/ui/screens/test_strategy_game_state_manager.py | Test | Task 3.20 — patch.object on private methods + Task 3.20b investigation |
| tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py | Test | Task 3.21 — inspect.getsource asserts |
| tests/unit/strategy/engine/order_handlers/test_order_processor_facade.py | Test | Task 3.22 — AST attribute counting |
| tests/unit/ui/test_race_browser_dialog.py | Test | Task 3.23 — 12 bypass-init tests |
| tests/unit/test_app_public_api.py | Test | Task 3.24 — inspect.signature asserts |
| tests/unit/ui/test_race_summary_panel.py | Test | Task 3.25 — __new__ + 12 private attrs |
| tests/unit/strategy/data/test_order_types_characterization.py | Test | Task 3.29 — module-level monkeypatch |
| tests/unit/performance/test_profiler_perf.py | Test | Task 3.30 — inspect.getsource forbidden-string asserts (PROJ-479 originally listed core/profiling/ path; actual is performance/) |
| tests/unit/ui/test_battle_panels_extended.py | Test | Task 3.31 — sys.modules patch + importlib.reload |
| tests/unit/strategy/engine/test_action_execution_engine.py | Test | Task 3.32 — 3 methods rewrite (lines 145-148, 199-202, 442-445 per Codex consult). Also touched by PROJ-492 Phase 2 (_make_fleet sweep). |
| tests/unit/ui/screens/test_strategy_screen.py | Test | Task 3.33 — 6 mock-only delegation tests. Also touched by PROJ-492 Phase 2 (_make_fleet sweep). |
