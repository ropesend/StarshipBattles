# PROJ-479 File Manifest

> Generated from `Reviews/results/2026-05-20_210550_test-review/` after independent verification.
> Every file appears in at least one `phase_N_checklist.md`; every checklist file appears here.

## Files

### Phase 1 — CAT-4 Duplicate Testing
| File | Type | Notes |
|------|------|-------|
| tests/unit/ui/test_battle_panels_characterization.py | Test | Parametrize 3 draw_battle_over tests |
| tests/unit/modifiers/test_propulsion_ability_bindings.py | Test | Parametrize 3 ability-class triplets |
| tests/unit/strategy/turn_engine/test_movement_phase_collaborator.py | Test | Consolidate with descriptor test |
| tests/unit/strategy/turn_engine/test_tick_phase_descriptors.py | Test | Reference canonical CaptureResolver test |
| tests/unit/builder/test_ship_component_manager_di.py | Test | Parametrize 2 source-check tests |
| tests/unit/simulation/components/test_modifier_manager.py | Test | Merge legacy + stateful classes (NEEDS_REWORK: verify recalc still covered) |
| tests/unit/strategy/engine/test_process_colonize_validation.py | Test | Parametrize on pod_type |
| tests/unit/strategy/data/test_group_policies.py | Test | Delete redundant registry-loads test |
| tests/unit/strategy/fleet_navigation/test_service_edge_cases.py | Test | Parametrize on speed |
| tests/unit/strategy/engine/test_planet_specific_colonization.py | Test | Consolidate 2 ColonizeValidator tests |
| tests/unit/ui/screens/test_strategy_game_state_manager.py | Test | Consolidate AdvanceTurn pair + Phase 3 mock-on-private |
| tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py | Test | Delete lazy-cache duplicate + Phase 3 inspect.getsource |
| tests/unit/strategy/engine/test_superweapon_command_handlers.py | Test | Extend parametrized test with SelfDestruct |
| tests/unit/ui/screens/test_strategy_build_queue_manager.py | Test | Merge issue17 pair |
| tests/unit/modifiers/test_modifier_loader_v2.py | Test | Delete subsumed test |
| tests/unit/simulation/test_component_health_manager.py | Test | Parametrize 3 invalid-input asserts |
| tests/unit/simulation/combat/test_fleet_aura_provider_identity.py | Test | Parametrize symmetric-mirror pair |
| tests/unit/strategy/engine/test_planet_command_handlers.py | Test | Parametrize 8 handler × 2 tests |
| tests/unit/strategy/data/test_tech_preset_loader.py | Test | Consolidate TestGetAvailable* twin classes |
| tests/unit/strategy/services/test_battle_service.py | Test | Parametrize service-error pairs |
| tests/unit/strategy/save_game_service/test_save_load_ops.py | Test | Delete local MockGameSession (also HLP-001) |
| tests/unit/strategy/fleet/test_warp_resources.py | Test | Extract shared mock-ship helper (NEEDS_REWORK: narrower scope) |

### Phase 2 — CAT-5 Fixture Bloat
| File | Type | Notes |
|------|------|-------|
| tests/unit/ui/test_theme_discovery.py | Test | Rescope 9 autouse pygame inits to class scope |
| tests/unit/ai/test_ai.py | Test | Class-scope ai_setup with deepcopy per test |
| tests/unit/strategy/test_combat.py | Test | Class-scope 3 setup fixtures |
| tests/unit/ui/test_weapons_report_layout.py | Test | Add pygame teardown |
| tests/unit/strategy/generation/density/conftest.py | Test | Keep mutable fixtures function-scoped (NEEDS_REWORK) |
| tests/integration/ui/test_event_log_replay_e2e.py | Test | Module-scope pygame_init |
| tests/integration/ui/test_build_queue_enhanced_planet_report.py | Test | Module/class-scope panel fixture |
| tests/integration/quickstart/test_quickstart_flow.py | Test | Module-scope full quickstart fixtures |
| tests/unit/simulation/test_battle_state_serialization.py | Test | Module-scope 9 read-only fixtures (NEEDS_REWORK: severity MINOR) |
| tests/unit/ui/screens/test_research_renderer.py | Test | scope=module not session (NEEDS_REWORK) |
| tests/unit/ui/test_utils.py | Test | Use cached root conftest UIManager |
| tests/unit/ui/screens/test_build_queue_design_report.py | Test | Module-scope design_report_panel fixture |
| tests/unit/simulation/entities/test_ship_serialization.py | Test | Class-scope equipped_ship |
| tests/unit/strategy/facade/test_strategy_session_facade_public_api.py | Test | Module-scope cheap fixture |
| tests/unit/ui/test_race_summary_panel.py | Test | Partial rescope (NEEDS_REWORK; also Phase 3 __new__) |
| tests/unit/ui/screens/test_fleet_orders_refresh.py | Test | Move to integration/ (NEEDS_REWORK) |
| tests/unit/ui/screens/test_transfer_dialog_enhanced.py | Test | Patch UIManager with MagicMock |
| tests/unit/ui/panels/test_empire_treasury_panel.py | Test | No-op (verification flagged but function scope correct) |

### Phase 3 — CAT-6 Mocking Brittleness
| File | Type | Notes |
|------|------|-------|
| tests/unit/ui/screens/test_build_queue_panel_factory.py | Test | Targeted per-group asserts |
| tests/unit/modifiers/test_invalid_operation_handling.py | Test | Real Modifier path |
| tests/unit/strategy/engine/test_transfer_handler_fleet_to_fleet.py | Test | Real Fleet + minimal session (NEEDS_REWORK) |
| tests/unit/ui/screens/test_strategy_input_handler_core.py | Test | Public handle_click + observable outcomes |
| tests/unit/builder/test_ship_component_manager.py | Test | Public Ship API |
| tests/unit/ui/screens/test_empire_build_queue_window.py | Test | bypass_init fixture |
| tests/unit/ui/screens/test_build_queue_list_window.py | Test | Wrap pygame_gui kill |
| tests/unit/strategy/engine/test_transfer_drop_pod.py | Test | spec MagicMock |
| tests/unit/strategy/engine/test_order_processor_fleet_merge.py | Test | Behavior-based merge speed assert |
| tests/unit/ui/screens/strategy_render/test_hex_outlines.py | Test | Tolerance-based hex asserts |
| tests/unit/ui/screens/test_fleet_report_sidebar.py | Test | make_ui_widget factory |
| tests/unit/strategy/consumable_management_engine/test_characterization.py | Test | Real auto_disable call |
| tests/unit/ui/screens/test_event_log_window.py | Test | bypass_init pattern |
| tests/unit/strategy/engine/test_superweapon_order_processor.py | Test | DI stub validator |
| tests/unit/simulation/combat/test_fleet_aura_cache.py | Test | Behavioral aggregation assert |
| tests/unit/ui/screens/test_orders_window.py | Test | Real construction |
| tests/unit/research/research_controls/test_reset_state.py | Test | Remove lambda shadow |
| tests/unit/strategy/engine/test_turn_engine_progress_callback.py | Test | assert_has_calls relaxed |
| tests/unit/ui/panels/test_ship_detail_panel.py | Test | Audit 23-test cluster vs PROJ-211 convention |
| tests/unit/strategy/engine/order_handlers/test_order_processor_facade.py | Test | Behavioral test or accept guard |
| tests/unit/ui/test_race_browser_dialog.py | Test | Migrate 12 tests to bypass_init |
| tests/unit/test_app_public_api.py | Test | Behavioral Game() test |
| tests/unit/ui/screens/test_strategy_fleet_command_router.py | Test | isinstance not type().__name__ |
| tests/unit/simulation/combat/test_weapon_firing_system.py | Test | Named kwargs not positional call_args |
| tests/unit/ui/screens/test_cargo_quick_dialog_controller_widget_purity.py | Test | assert_called_once_with |
| tests/unit/strategy/data/test_order_types_characterization.py | Test | Factory not monkeypatch |
| tests/unit/core/profiling/test_profiler_perf.py | Test | Patch json.dump/loads at call site |
| tests/unit/ui/test_battle_panels_extended.py | Test | Fixture wraps reload (also Phase 5 DUP-002) |
| tests/unit/strategy/engine/test_action_execution_engine.py | Test | DI ActionTimeResolver |
| tests/unit/ui/screens/test_strategy_screen.py | Test | Integration tests for 6 lifecycle methods |

### Phase 4 — CAT-7 Sleep/Latency
| File | Type | Notes |
|------|------|-------|
| tests/unit/services/llm/test_background.py | Test | 3 sleep → Event |
| tests/unit/services/replay/test_replay_verification_coordinator.py | Test | 5 sleep → Event/Barrier |
| tests/unit/strategy/services/test_race_description_llm_controller.py | Test | 3 sleep → _wait_until helper |

### Phase 5 — DUP cluster consolidation
| File | Type | Notes |
|------|------|-------|
| tests/conftest.py | Test | DUP-001 target: _make_mock_fleet; DUP-003 target: _assert_roundtrip_property |
| tests/integration/strategy/test_combat_round_budget.py | Test | DUP-001 delete local _make_fleet |
| tests/performance/test_contested_hex_round_budget.py | Test | DUP-001 delete local _make_fleet |
| tests/unit/strategy/engine/test_conflict_round_budget.py | Test | DUP-001 delete local _make_fleet |
| tests/fixtures/battle_panels.py | Test | DUP-002 new fixture file |
| tests/unit/ui/services/test_ship_io.py | Test | DUP-003 selective shared helper use (NEEDS_REWORK: keep separate) |
| tests/unit/simulation/entities/test_ship_serialization.py | Test | DUP-003 selective shared helper use (NEEDS_REWORK) |
| tests/unit/strategy/engine/conftest.py | Test | DUP-005 + HLP-006 extension target |
| tests/unit/strategy/engine/test_planet_action_engine.py | Test | DUP-005 delete local _make_empire |
| tests/unit/strategy/engine/test_harvesting_engine.py | Test | DUP-005 delete (extended variant via kwargs) |
| tests/unit/strategy/engine/test_planet_energy_engine.py | Test | DUP-005 delete local _make_empire |
| tests/unit/strategy/engine/test_resupply_engine.py | Test | DUP-005 delete local _make_empire |
| tests/unit/strategy/engine/test_component_activation_engine.py | Test | DUP-005 delete local _make_empire |
| tests/unit/strategy/engine/test_environmental_hazard_engine.py | Test | DUP-005 delete local _make_empire |
| tests/fixtures/modifier_stubs.py | Test | DUP-006 new fixture file (NEEDS_REWORK: narrowed scope) |
| tests/unit/ui/screens/builder/test_modifier_utils.py | Test | DUP-006 import from fixture |

### Phase 6 — HLP helper consolidation
| File | Type | Notes |
|------|------|-------|
| tests/unit/strategy/save_game_service/conftest.py | Test | HLP-001/005 canonical (extend with save_path kwarg + autouse) |
| tests/unit/strategy/save_game_service/test_error_handling.py | Test | HLP-001 delete copy; HLP-005 delete copy |
| tests/unit/ui/test_save_selection.py | Test | HLP-001 delete copy; HLP-005 _patched_saves_tmpdir variant |
| tests/unit/strategy/test_auto_save.py | Test | HLP-001 delete copy; HLP-005 chdir variant (NEEDS_REWORK reconcile) |
| tests/fixtures/colonization_fixtures.py | Test | HLP-002 new fixture file (4-field MockPlanetType) |
| (10+ HLP-002 consumer files) | Test | Replace inline MockPlanetType with import |
| tests/conftest.py | Test | HLP-003 extend canonical with has_yard kwarg; HLP-004 add _make_mock_fleet |
| tests/integration/ui/test_fleet_build_button.py | Test | HLP-003 delete local copy |
| tests/integration/ui/test_strategy_buttons.py | Test | HLP-003 delete local copy |
| tests/unit/strategy/test_advanced_fleet_orders.py | Test | HLP-003 delete local copy |
| tests/repro_issues/test_bug_27_ordertype.py | Test | HLP-003 delete local copy |
| (43+ HLP-004 consumer files) | Test | Replace local _make_fleet with conftest import |
| tests/unit/strategy/engine/test_empire.py | Test | HLP-006 real Empire constructor — keep or extract real_empire_factory |
