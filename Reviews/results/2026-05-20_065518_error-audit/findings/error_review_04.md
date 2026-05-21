# Error Handling Review: Shard 04

## Summary
- Shard: Shard 04
- Files in Scope: 211
- Files Actually Read: 211
- Total Findings: 2
- Critical: 0 | Major: 0 | Minor: 2

## Background

All 128 broad-except sites flagged by the deterministic scanner carry valid `# Intentional broad catch:` comments — per instructions, these are not reported as violations. This review focuses on issues the scanner cannot detect: exception swallowing, lost exception chaining, missing domain-specific exceptions, inconsistent logging, missing error boundaries, and resource cleanup issues.

The shard covers files across all layers: Core (exceptions, paths, formula_evaluator, protocols), Strategy (turn_engine, game_session, fleet, ship_instance, engines, services, combat), Simulation (ship, combat, abilities, replay), AI (behaviors, controllable, policy_manager), and UI (screens, panels, renderer, services).

## Findings

### Finding 1 — MINOR: `from_dict()` raises bare `KeyError` instead of `PersistenceException`

**File:** `game/strategy/data/component_activation_state.py:136-144`

**Issue:** `ComponentActivationState.from_dict()` accesses `data['phase']` directly, which raises `KeyError` when the key is missing. Per `docs/05_ERROR_HANDLING.md` (line 302-305), all `from_dict()` methods must use `require_keys()` and raise `PersistenceException(P003)` for corrupt external data. The docstring even acknowledges this: "Requires `phase` field; raises KeyError if missing."

**Context:** While `ComponentActivationState` is a lightweight nested dataclass composited inside `ShipInstance` and `PlanetaryFacility`, the convention applies uniformly to all `from_dict()` methods. The upstream callers (`ShipInstance.from_dict`, `ShipInstanceSerializer.from_dict`) already raise `PersistenceException` — this inner class should follow the same contract.

**Suggested fix:**
```python
from game.core.validation_helpers import require_keys

@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'ComponentActivationState':
    require_keys(data, ['phase'], 'ComponentActivationState')
    return cls(
        phase=ActivationPhase(data['phase']),
        progress_ticks=data.get('progress_ticks', 0),
        required_ticks=data.get('required_ticks', 0),
        ability_name=data.get('ability_name', ''),
        energy_drain_rate=data.get('energy_drain_rate', 0.0),
    )
```

### Finding 2 — MINOR: `start_activating` and `start_deactivating` raise generic `ValueError` instead of domain-specific `StateException`

**File:** `game/strategy/data/component_activation_state.py:77-101`

**Issue:** The `start_activating()` and `start_deactivating()` methods raise `ValueError` when called from an invalid phase (not INACTIVE / not ACTIVE respectively). Per the exception hierarchy in `game/core/exceptions.py`, this is a state-transition error that should be `StateException` or a subclass. `ValueError` is a generic Python built-in — callers cannot programmatically discriminate a phase-transition error from other numeric/type validation failures.

**Suggested fix:**
```python
from game.core.exceptions import StateException
# In start_activating():
raise StateException(
    f"Cannot start activating from {self.phase.value} phase (must be inactive)",
    context={"current_phase": self.phase.value, "expected_phase": "inactive"}
)
```

## Additional Issues Found

None. All other error-handling patterns reviewed across the 211 files conform to project conventions.

### Confirmed Clean Areas

- **Critical runtime files** (`turn_engine.py`, `game_session.py`, `minefield_resolver.py`, `background.py`, `ship.py`, `exceptions.py`, `formula_evaluator.py`): All have proper error boundaries, chained exceptions, and documented broad catches.
- **`game/core/exceptions.py`**: Comprehensive, well-structured hierarchy with 26 exception classes.
- **`game/core/formula_evaluator.py`**: Properly catches and converts exceptions to `FormulaException` with full chain preservation.
- **`game/strategy/engine/turn_engine.py`**: Exemplary error handling — snapshot rollback, cache invalidation on failure, per-phase timing, proper `EnginePhaseError` chaining.
- **`game/services/llm/background.py`**: Thread-safe state management, proper `LLMUnexpectedError` wrapping for non-LLM exceptions, correct `_done_event` signaling.
- **`game/strategy/engine/minefield_resolver.py`**: Three broad catches all carry explicit Intentional comments documenting the fallback rationale.
- **`game/simulation/replay/replay_verifier.py`**: Pure diff walker with no I/O — no error handling needed.
- **`game/ui/screens/transfer_dialog.py`**: `try/finally` wrapping for modal teardown on facade exceptions.
- **`game/strategy/data/bay_inventory.py`**: Proper `TypeError`/`ValueError` for type violations on mutation methods.
- **`game/strategy/systems/design_repository.py`**: Uses `DesignLoadResult` result-object pattern for non-critical file loads.
- **Enum `from_dict()` consistency**: `game/research/data/research_tracker.py:31-38` (`NodeState.from_dict`), `game/strategy/data/bay_inventory.py:309-333` (`BayInventory.from_dict`), and `game/ui/screens/battle_setup_state.py:113-141` (`BattleSetupSide.from_dict`) all properly use `require_keys()` or handle missing data with safe `.get()` defaults.

## File Coverage Verification

| File | Status |
|------|--------|
| game/ai/spatial_behaviors/_formation_utils.py | Read — clean |
| game/strategy/data/build_queue_source.py | Read — clean |
| game/strategy/data/component_activation_state.py | Read — 2 MINOR findings |
| game/strategy/engine/game_session.py | Read — clean |
| game/ui/screens/test_lab/screen_actions.py | Read — clean |
| game/simulation/systems/resource_manager.py | Read — clean |
| game/strategy/services/ability_metadata.py | Read — clean |
| game/simulation/replay/replay_verifier.py | Read — clean |
| game/strategy/services/replay_verification_coordinator.py | Read — clean |
| game/ui/screens/strategy_windows/dispatch.py | Read — clean |
| game/strategy/data/ship_display_formatter.py | Read — clean |
| game/ui/screens/test_lab/details/draw_context.py | Read — clean |
| game/ui/screens/cargo_quick_dialog.py | Read — clean |
| game/ui/screens/planet_target_editor_base.py | Read — clean |
| game/strategy/data/ship_instance.py | Read — clean |
| game/ui/research/research_renderer.py | Read — clean |
| game/strategy/quickstart_builder.py | Read — clean |
| game/strategy/engine/superweapon_handlers/__init__.py | Read — clean |
| game/ui/renderer/sprites.py | Read — clean |
| game/ui/screens/orders_window.py | Read — clean |
| game/ui/filters/filter_state.py | Read — clean |
| game/simulation/entities/stat_contributors/weapons.py | Read — clean |
| game/strategy/services/fleet_warp_resolution.py | Read — clean |
| game/ui/screens/battle_setup_state.py | Read — clean |
| game/ui/components/table/selection.py | Read — clean |
| game/ui/screens/race_setup/panel_factory.py | Read — clean |
| game/strategy/generation/density/primitives/noise.py | Read — clean |
| game/strategy/engine/handlers/order_queue.py | Read — clean |
| game/simulation/replay/replay_capture.py | Read — clean |
| game/simulation/entities/layer_data.py | Read — clean |
| game/strategy/interfaces/engines/movement.py | Read — clean |
| game/core/protocols/boundary.py | Read — clean |
| game/ui/screens/strategy_ui_action_router.py | Read — clean |
| game/strategy/facade/dto/container_snapshot.py | Read — clean |
| game/ui/components/filters/tri_state_widget.py | Read — clean |
| game/ui/panels/system_tree_panel.py | Read — clean |
| game/research/data/research_tracker.py | Read — clean |
| game/ui/services/image/types.py | Read — clean |
| game/strategy/generation/density/density_map.py | Read — clean |
| game/ui/screens/design_image_helper.py | Read — clean |
| game/ai/interfaces/controllable.py | Read — clean |
| game/ui/screens/atmosphere_target_editor.py | Read — clean |
| game/strategy/engine/order_handlers/launch_fighters.py | Read — clean |
| game/ui/screens/strategy_screen_selection.py | Read — clean |
| game/ui/screens/empire_build_queue_data_source.py | Read — clean |
| game/strategy/facade/dto/__init__.py | Read — clean |
| game/research/systems/__init__.py | Read — clean |
| game/ui/screens/race_setup/ui_builder.py | Read — clean |
| game/ui/screens/battle_setup/view_model.py | Read — clean |
| game/ui/screens/builder/structure_list_items.py | Read — clean |
| game/strategy/combat/strategy_modifier_stack_builder.py | Read — clean |
| game/ui/screens/transfer_dialog.py | Read — clean |
| game/ui/panels/race_description_panel.py | Read — clean |
| game/simulation/components/abilities/planetary/shields.py | Read — clean |
| game/ui/renderer/game_renderer.py | Read — clean |
| game/core/paths.py | Read — clean |
| game/ui/screens/star_list_sidebar.py | Read — clean |
| game/simulation/interfaces/__init__.py | Read — clean |
| game/simulation/entities/ship_loader.py | Read — clean |
| game/simulation/components/abilities/planetary/_shared.py | Read — clean |
| game/strategy/engine/turn_engine_config.py | Read — clean |
| game/strategy/services/strategic_ability_scanner.py | Read — clean |
| game/strategy/engine/construction_forecast.py | Read — clean |
| game/strategy/data/fleet.py | Read — clean |
| game/strategy/engine/turn_engine.py | Read — clean |
| game/strategy/validation/planet_order_validator.py | Read — clean |
| game/strategy/combat/pre_tick_setup/reboard_setup.py | Read — clean |
| game/strategy/combat/battle_assembly.py | Read — clean |
| game/ai/policy_manager.py | Read — clean |
| game/strategy/data/resource_generation_config.py | Read — clean |
| game/ui/research/research_scene.py | Read — clean |
| game/ui/renderer/camera.py | Read — clean |
| game/ui/screens/test_lab/renderer/_draw_helpers.py | Read — clean |
| game/simulation/components/modifier_schema.py | Read — clean |
| game/core/protocols/registry.py | Read — clean |
| game/ui/pygame_gui_patch.py | Read — clean |
| game/ui/screens/star_data_source.py | Read — clean |
| game/ui/screens/test_lab/panel_manager.py | Read — clean |
| game/strategy/engine/empire_economy_calculator.py | Read — clean |
| game/ui/screens/builder/modifier_row.py | Read — clean |
| game/simulation/components/abilities/planetary/resource_modifiers.py | Read — clean |
| game/strategy/facade/dto/fleet_hierarchy_dto.py | Read — clean |
| game/simulation/components/abilities/container.py | Read — clean |
| game/ui/screens/test_lab/data_extractor.py | Read — clean |
| game/ui/components/table/data_source.py | Read — clean |
| game/ui/screens/strategy_render/context.py | Read — clean |
| game/ui/interfaces/battle_ui.py | Read — clean |
| game/ui/screens/strategy_colonization.py | Read — clean |
| game/ui/screens/battle_setup/renderer.py | Read — clean |
| game/ui/config.py | Read — clean |
| game/ui/screens/test_lab/details/__init__.py | Read — clean |
| game/ui/screens/test_lab/renderer/__init__.py | Read — clean |
| game/ui/panels/race_theme_gallery.py | Read — clean |
| game/services/llm/background.py | Read — clean |
| game/simulation/services/vehicle_design_service.py | Read — clean |
| game/ui/screens/builder/layer_panel.py | Read — clean |
| game/ui/panels/race_summary_panel.py | Read — clean |
| game/strategy/services/fleet_cargo_projector.py | Read — clean |
| game/ui/services/ship_io.py | Read — clean |
| game/simulation/entities/combat_endurance.py | Read — clean |
| game/strategy/facade/slices/command_dispatch_slice.py | Read — clean |
| game/ui/renderer/__init__.py | Read — clean |
| game/simulation/components/abilities/planetary/stat_modifiers.py | Read — clean |
| game/core/exceptions.py | Read — clean |
| game/ui/screens/test_lab/renderer/tag_filter_panel.py | Read — clean |
| game/simulation/entities/ship_serialization.py | Read — clean |
| game/strategy/data/habitability_factors.py | Read — clean |
| game/simulation/components/__init__.py | Read — clean |
| game/ui/screens/galaxy_test/galaxy_mode.py | Read — clean |
| game/ui/screens/strategy_render/grid.py | Read — clean |
| game/ui/screens/battle_setup/screen.py | Read — clean |
| game/ui/screens/list_filter_utils.py | Read — clean |
| game/strategy/engine/superweapon_handlers/create_dyson_sphere.py | Read — clean |
| game/strategy/data/squadron.py | Read — clean |
| game/ui/screens/test_lab/renderer/orchestrator.py | Read — clean |
| game/ui/utils/formatters.py | Read — clean |
| game/ui/screens/star_list_filter_manager.py | Read — clean |
| game/simulation/battle_spec.py | Read — clean |
| game/strategy/generation/density/primitives/density_primitive.py | Read — clean |
| game/ui/screens/strategy_render/warp_lanes.py | Read — clean |
| game/ui/screens/strategy_camera_nav.py | Read — clean |
| game/ui/screens/strategy_windows/event_log_window_ctrl.py | Read — clean |
| game/strategy/services/stabilizer_registry.py | Read — clean |
| game/ui/screens/strategy_render/storms.py | Read — clean |
| game/strategy/generation/density/primitives/ring.py | Read — clean |
| game/simulation/entities/stat_contributors/__init__.py | Read — clean |
| game/simulation/entities/ship_design_stats.py | Read — clean |
| game/simulation/components/abilities/stat_keys.py | Read — clean |
| game/strategy/data/planet_gen_surface.py | Read — clean |
| game/ui/screens/empire_panel_window.py | Read — clean |
| game/ui/screens/strategy_windows/fleet_report_ctrl.py | Read — clean |
| game/app_bootstrap.py | Read — clean |
| game/strategy/engine/organics_consumption_engine.py | Read — clean |
| game/ui/screens/new_game_setup_view_model.py | Read — clean |
| game/strategy/engine/planet_energy_engine.py | Read — clean |
| game/ui/screens/strategy_windows/planet_abilities_ctrl.py | Read — clean |
| game/ui/panels/build_queue_controller.py | Read — clean |
| game/ui/effects/__init__.py | Read — clean |
| game/ui/screens/workshop_event_router.py | Read — clean |
| game/engine/spatial.py | Read — clean |
| game/ui/screens/test_lab/details/panel.py | Read — clean |
| game/ui/screens/planet_abilities_window.py | Read — clean |
| game/ui/utils/pygame_utils.py | Read — clean |
| game/strategy/services/galaxy_pathfinding_service.py | Read — clean |
| game/core/formula_evaluator.py | Read — clean |
| game/simulation/components/abilities/launch.py | Read — clean |
| game/strategy/interfaces/engines/production.py | Read — clean |
| game/ui/screens/workshop_viewmodel_layer_ops.py | Read — clean |
| game/simulation/services/ship_materializer.py | Read — clean |
| game/ui/screens/planet_list_filters.py | Read — clean |
| game/strategy/engine/game_initializer.py | Read — clean |
| game/ui/screens/battle_ui.py | Read — clean |
| game/strategy/services/planet_economy_projector.py | Read — clean |
| game/ui/utils/resource_display.py | Read — clean |
| game/strategy/data/ship_consumable_manager.py | Read — clean |
| game/ui/screens/test_lab/test_executor.py | Read — clean |
| game/ui/components/__init__.py | Read — clean |
| game/ai/target_evaluator.py | Read — clean |
| game/ui/screens/strategy_build_queue_manager.py | Read — clean |
| game/simulation/components/abilities/harvester.py | Read — clean |
| game/ui/services/battle_ui_service.py | Read — clean |
| game/ui/screens/strategy_windows/list_windows.py | Read — clean |
| game/simulation/validation/base.py | Read — clean |
| game/simulation/components/component_resource_manager.py | Read — clean |
| game/simulation/combat/modifier_stack.py | Read — clean |
| game/strategy/systems/design_repository.py | Read — clean |
| game/strategy/data/bay_inventory.py | Read — clean |
| game/assets/component_derivatives.py | Read — clean |
| game/strategy/events/event_log.py | Read — clean |
| game/ai/spatial_behaviors/patrol_zone.py | Read — clean |
| game/strategy/services/ability_sources/__init__.py | Read — clean |
| game/engine/collision.py | Read — clean |
| game/ui/screens/defeat_dialog.py | Read — clean |
| game/strategy/data/storm.py | Read — clean |
| game/simulation/combat/attack_contract.py | Read — clean |
| game/ui/screens/build_queue_panel_factory.py | Read — clean |
| game/ui/widgets/range_slider_builder.py | Read — clean |
| game/ui/components/table/column_manager.py | Read — clean |
| game/ui/screens/test_lab/details/propulsion_outcomes.py | Read — clean |
| game/strategy/engine/session/__init__.py | Read — clean |
| game/ui/widgets/column_toggle_section.py | Read — clean |
| game/strategy/data/classification_config.py | Read — clean |
| game/ui/screens/builder_selection.py | Read — clean |
| game/ui/screens/test_lab/results_panel.py | Read — clean |
| game/strategy/engine/handlers/__init__.py | Read — clean |
| game/core/state_machine.py | Read — clean |
| game/simulation/entities/stat_contributors/movement.py | Read — clean |
| game/ui/screens/test_lab/renderer/_condition_logic.py | Read — clean |
| game/ui/screens/workshop_viewmodel_selection.py | Read — clean |
| game/ai/behaviors.py | Read — clean |
| game/simulation/replay/replay_outcome.py | Read — clean |
| game/simulation/components/abilities/resources.py | Read — clean |
| game/strategy/services/ship_instance_factory.py | Read — clean |
| game/ui/screens/builder/__init__.py | Read — clean |
| game/strategy/config/economy_config.py | Read — clean |
| game/simulation/entities/ship_physics.py | Read — clean |
| game/ui/screens/strategy_windows/__init__.py | Read — clean |
| game/simulation/entities/stat_contributors/accumulator.py | Read — clean |
| game/ui/screens/transfer_mass_preview.py | Read — clean |
| game/strategy/engine/conflict_resolution_engine.py | Read — clean |
| game/strategy/engine/minefield_resolver.py | Read — clean |
| game/strategy/engine/atmosphere_engine.py | Read — clean |
| game/ui/screens/strategy_render/planets.py | Read — clean |
| game/ui/utils/json_diff.py | Read — clean |
| game/research/data/__init__.py | Read — clean |
| game/ui/panels/design_stats_panel.py | Read — clean |
| game/ui/screens/strategy_windows/transfer_dialogs.py | Read — clean |
| game/ui/screens/battle_setup/input_handler.py | Read — clean |
| game/ui/screens/galaxy_test/screen.py | Read — clean |
| game/strategy/interfaces/engines/planet_ops.py | Read — clean |
| game/simulation/entities/ship.py | Read — clean |
