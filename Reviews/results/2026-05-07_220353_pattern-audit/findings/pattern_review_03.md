# Pattern Conformance Review: Shard 03

## Summary
- Shard: Shard 03
- Files in Scope: 185
- Files Actually Read: 185
- Total Findings: 8
- Critical: 0 | Major: 1 | Minor: 7

## Layer Dependency Violations

*Pre-computed: 0 violations. Spot-checked ~80 files across shard — confirmed no upward imports or forbidden layer crossings. TYPE_CHECKING imports correctly guarded; late-import sites match documented allowances (RegistryLoader, TurnEngineConfig.create_default, Ship.add_component, SimAdapter, etc.).*

No findings.

## Pattern Bypass Findings

### No Criticals Found

Confirmation checks performed across the shard:

- **Registry DI bypass (#3):** Sim layer (`game/simulation/`) files — battle_runner.py:725, ship_materializer.py, designs.py, ability_stat_registry.py, battle_state.py, ship_stats.py, tick_phase.py, modifiers.py — all receive `registries`/`registry_provider` via parameter injection or constructor DI. No call to `get_default_registry_provider()` found in any simulation-layer file. The sole `get_default_registry_provider()` call in the shard is at `game/strategy/adapters/simulation_adapter.py:52`, which is explicitly permitted (strategy layer, PROJ-306 documented boundary).

- **Facade bypass (#5):** All UI files checked (strategy_superweapons.py, strategy_game_state_manager.py, strategy_input_handler.py, event_log_window.py, transfer_dialogs.py, strategy_ui_action_router.py, fleet_report_ctrl.py, planet_abilities_ctrl.py, etc.) correctly use `StrategySessionFacade` (`self._facade`, `self.scene._facade`, or injected `facade` parameter) as their strategy access point. Strategy DTOs (`FleetInfo`, `SystemInfo`, `PlanetInfo`) are used for reads. No direct engine/simulation import found.

- **CQRS-lite (#6):** All DTOs in `game/strategy/facade/dto/` are `frozen=True` dataclasses. Command DTOs (e.g., `IssueBuildOrderCommand`, `IssueSelfDestructCommand`) are plain used for writes, DTOs for reads. No DTO mutation observed. Command handlers return `ValidationResult`, not data.

- **Protocol bypass (#2):** Cross-layer boundary checks use documented TypeGuard functions (`is_zone_occupant` at galaxy_spatial_index.py:104). Same-layer `isinstance` checks (e.g., `isinstance(obj, Planet)` at galaxy_spatial_index.py:37, `isinstance(proj_type, Enum)` at battle_state.py:521) are internal to their own layer — not a bypass of protocol layer boundaries.

- **CommandHandlerRegistry bypass (#7):** Files at `game/strategy/engine/handlers/build.py` use the `@command_spec` decorator + per-module `register(registry)` pattern per PROJ-371. Order handlers at `game/strategy/engine/order_handlers/` use `OrderHandlerRegistry` with `OrderType`-keyed dispatch. No `if/elif` chains or tuple literals found.

- **Ability aggregation bypass (#14):** Strategic ability aggregation goes through `aggregate_multipliers()` / `aggregate_rates()` in `strategic_ability_scanner.py`. Ship-level stat aggregation goes through `STAT_CONTRIBUTOR_REGISTRY.iter_for(comp)` in `ship_stats.py:260`. No local re-implementations of two-phase aggregation found.

- **Scope-Driven Team Routing bypass (#25):** `ability_stat_registry.py:90` imports `OPPONENT_SCOPES` as the single source of truth. `emit_entries_for_ability()` handles N-team fan-out. No local duplicate scope sets in compiler code.

- **Ability-Stat Registry bypass (#26):** `ModifierEntry` objects are constructed inside `emit_entries_for_ability()` (ability_stat_registry.py:223-228). No hand-constructed `ModifierEntry` objects found outside the registry's emit entry point.

- **Strategy Modal Window (#31):** `EventLogWindow` (event_log_window.py:75) correctly subclasses `StrategyModalWindow`. Transfer dialog uses the registrar clean-up pattern. No manual close-callback tracking observed for new modal windows.

---

#### MAJOR: LOC Ceiling Violation — battle_runner.py (730 lines)
**ID:** PAT-03-001
**Location:** game/simulation/battle_runner.py (entire file)
**Pattern:** AGENTS.md LOC ceiling (500 lines production code)
**Issue:** File is 730 lines. Contains `run_battle`, `extract_outcome`, `start_engine_from_spec`, `materialize_spec_ships`, `build_context_ship_builder`, `_apply_spec_components_to_ship`, `_extract_component_states`, `_build_ship_outcome`, `_derive_end_reason`, `_attach_telemetry`. The `_apply_spec_components_to_ship` function (72 lines with two-pass validation) and `_build_ship_outcome` (58 lines with multi-branch status resolution) are candidates for extraction into a post-battle or component-application sub-module.
**Recommendation:** Extract `_apply_spec_components_to_ship` + `_extract_component_states` into `game/simulation/post_battle/component_state_applicator.py`; extract `_build_ship_outcome` + `_derive_end_reason` into `game/simulation/post_battle/outcome_assembly.py`. Runner stays as the unified entry orchestrator.
**LOC affected:** ~230

---

### Minor Findings

#### MINOR: Potential `isinstance` on concrete class within same layer — galaxy_spatial_index.py
**ID:** PAT-03-002
**Location:** game/strategy/data/galaxy_spatial_index.py:37
**Pattern:** #2 Protocol + TypeGuard
**Issue:** Uses `isinstance(obj, Planet)` to route planet objects to a different lookup path. While same-layer (strategy, not cross-level), the codebase convention prefers duck-typed checks (`hasattr`) or TypeGuards. This is the lowest-priority form since it's internal to the strategy layer.
**Recommendation:** Consider using `is_planet(obj)` TypeGuard from `game.core.protocols.strategy_entities` if available, or a duck-typed `hasattr(obj, 'location') and hasattr(obj, 'owner_id')` check.
**LOC affected:** 1

#### MINOR: Potential `isinstance` on Enum — battle_state.py
**ID:** PAT-03-003
**Location:** game/simulation/battle_state.py:521
**Pattern:** #2 Protocol + TypeGuard
**Issue:** `isinstance(proj_type, Enum)` then reads `.value`. Same-layer check (simulation internal) and semantically sound, but a duck-typed `getattr(proj_type, 'value', proj_type)` would remove the dependency on the `Enum` base class for forward compat.
**Recommendation:** Replace with `proj_type = getattr(proj_type, 'value', proj_type)`. This handles both Enum and string types without isinstance.
**LOC affected:** 1

#### MINOR: `isinstance` on TelemetryLevel — battle_runner.py
**ID:** PAT-03-004
**Location:** game/simulation/battle_runner.py:388
**Pattern:** #2 Protocol + TypeGuard
**Issue:** `isinstance(level, TelemetryLevel)` guards against placeholder objects from early-phase tests. Same-layer check, but a duck-typed approach would be more robust for test mocks.
**Recommendation:** Use `getattr(level, 'value', None) is not None` or a duck-typed `hasattr` check.
**LOC affected:** 1

#### MINOR: Config class uses mutable dict defaults — star_generation_config.py
**ID:** PAT-03-005
**Location:** game/strategy/data/star_generation_config.py:23-88
**Pattern:** #12 Configuration Classes
**Issue:** `DEFAULT_TYPE_WEIGHTS`, `DEFAULT_MASS_GENERATION`, etc. are class-level dict attributes. These ARE mutable, but the `_use_defaults()` method correctly calls `dict(self.DEFAULT_TYPE_WEIGHTS)` to create copies before assigning to `self`. This follows the documented pattern correctly. However, `DEFAULT_STEFAN_BOLTZMANN_TYPES` (line 63) is a deeply nested dict — `_load_from_json` (line 151) correctly does `dict(self.DEFAULT_STEFAN_BOLTZMANN_TYPES)` to shallow-copy, but inner dict values (e.g., `"mass_range": (0.8, 5.0)`) are tuples (immutable), so safe. No actual defect — verified for completeness.
**LOC affected:** 0 (confirmed safe)

#### MINOR: `build_context.py` Protocol location — strategy/data vs core/protocols
**ID:** PAT-03-006
**Location:** game/strategy/data/build_context.py
**Pattern:** #2 Protocol + TypeGuard
**Issue:** `BuildContext` is a `@runtime_checkable Protocol` placed in `game/strategy/data/` rather than `game/core/protocols/`. However, it has no cross-layer consumer — it's only consumed by UI code which is a higher layer, and the architecture doc allows strategy-local protocols (similar to `galaxy_protocols.py`). This is an "opportunity to adopt documented pattern" rather than a violation.
**Recommendation:** If `BuildContext` becomes cross-layer (e.g., used by both simulation and UI), move it to `game/core/protocols/` with a TypeGuard. For now, location is acceptable given the single consumer pattern.
**LOC affected:** 0 (documentation note only)

#### MINOR: `get_default_design_role_registry` pattern — design_role_registry.py
**ID:** PAT-03-007
**Location:** game/strategy/data/design_role_registry.py:37-43
**Pattern:** #1 ApplicationContext
**Issue:** The `get_default_design_role_registry()` / `set_default_design_role_registry()` / `reset_default_design_role_registry()` accessor trio follows the documented `get_default_xxx` / `set_default_xxx` pattern. However, it is NOT managed by `ApplicationContext` — it's a standalone module-level singleton. This is a pattern **extension** (additional service with the same accessor shape) rather than a violation. The design role registry was not included in the ApplicationContext list because it's a strategy/data concern, not a cross-cutting infrastructure service.
**LOC affected:** 0 (documentation note — if this grows to multi-layer use, consider ApplicationContext management)

#### MINOR: `random.shuffle` at module level — naming.py
**ID:** PAT-03-008
**Location:** game/strategy/data/naming.py:42
**Pattern:** #18 Per-Battle RNG
**Issue:** `random.shuffle(self.available_names)` uses module-level `random` in `game/strategy/data/`. Pattern #18 restricts module-level `random.*` in simulation, engine, and AI layers, but not in strategy/data. This is acceptable since name shuffling is for galaxy generation (non-deterministic by design, not battle simulation). No violation — confirming for completeness.
**LOC affected:** 0 (confirmed safe)

## Naming Collisions

No naming collisions found across layers within Shard 03.

Verified:
- `EventBus` in `game/core/event_logging.py` vs `game/ui/screens/builder/event_bus.py::EventBus` — documented as distinct entities (patterns doc #10).
- `CommandRegistry` in `strategy/engine/commands/registry.py` vs `CommandHandlerRegistry` in `strategy/engine/handlers/base.py` — different names, different types.
- `StarSystem` defined in `game/strategy/data/star_system.py`, re-exported from `galaxy.py` — same class, not a collision.

## Configuration Conventions

All config classes in shard conform to Pattern #12:

| File | Pattern Check | Status |
|---|---|---|
| `game/core/config.py` | Plain classes (`DisplayConfig`, `AIConfig`, `PhysicsConfig`, `BattleTuning`, `LLMConfig`, `ImageConfig`), no `@dataclass` | Conformant |
| `game/strategy/data/star_generation_config.py` | `DEFAULT_*` dict constants + `_load_from_json()` method + `@lru_cache` accessor | Conformant |
| `game/strategy/config/__init__.py` | Empty — package marker | Conformant |
| `game/ui/config.py` (not in shard) | — | N/A |

## Undocumented Patterns Found

No undocumented patterns observed in Shard 03. All recurring patterns match documented ones:

- **Module-level `get_default_xxx` / `set_default_xxx` / `reset_default_xxx`** accessor trios (design_role_registry.py, ship_materializer.py) — documented as Pattern #1 extension.
- **`IAbilitySource` adapter pattern** (storm.py, planet_intrinsic.py, system_archetype.py, warp_point.py) — documented as Pattern #29.
- **`@runtime_checkable Protocol` + TypeGuard** for cross-layer contracts — documented as Pattern #2.
- **Provider registration pattern** (ability_iterator.py) — documented as Pattern #29 extension.
- **`_collect + _aggregate + _format` three-stage pipeline** (system_effects_collector.py) — this IS the documented Pattern #29 aggregation pipeline, not a new pattern.

## File Coverage Verification

| File | Status |
|------|--------|
| game/ui/screens/battle_setup/spec_compiler.py | Read |
| game/strategy/adapters/simulation_adapter.py | Read |
| game/ui/screens/star_list_presets.py | Read |
| game/simulation/designs.py | Read |
| game/strategy/engine/planet_action_engine.py | Read |
| game/ui/screens/star_list_sidebar.py | Read |
| game/strategy/systems/design_library.py | Read |
| game/strategy/systems/save_game_service.py | Read |
| game/strategy/engine/order_handlers/registry_factory.py | Read |
| game/ui/screens/battle_setup/screen.py | Read |
| game/ui/screens/battle_setup/renderer.py | Read |
| game/strategy/formulas/__init__.py | Read |
| game/ui/screens/strategy_fleet_command_router.py | Read |
| game/strategy/data/galaxy_warp_generator.py | Read |
| game/ui/screens/strategy_click_dispatcher.py | Read |
| game/strategy/data/build_context.py | Read |
| game/strategy/generation/__init__.py | Read |
| game/ui/screens/atmosphere_target_editor.py | Read |
| game/simulation/combat/families/_beam_common.py | Read |
| game/strategy/quickstart_builder.py | Read |
| game/ui/screens/fleet_selection_window.py | Read |
| game/ui/screens/planet_list_filters.py | Read |
| game/ui/screens/test_lab/details/propulsion_outcomes.py | Read |
| game/simulation/components/abilities/ui_colors.py | Read |
| game/ui/screens/strategy_game_state_manager.py | Read |
| game/ui/screens/event_log_sidebar.py | Read |
| game/simulation/components/component_health_manager.py | Read |
| game/simulation/replay/replay_record.py | Read |
| game/strategy/services/system_destroyer.py | Read |
| game/core/registry.py | Read |
| game/simulation/components/modifier_schema.py | Read |
| game/ui/screens/test_lab/formatting_utils.py | Read |
| game/simulation/combat/formation.py | Read |
| game/assets/component_derivatives.py | Read |
| game/strategy/generation/loaders/galaxy_layouts_loader.py | Read |
| game/ui/orchestration/__init__.py | Read |
| game/ui/screens/strategy_menu_panel.py | Read |
| game/ui/assets/ship_theme_manager.py | Read |
| game/strategy/data/galaxy.py | Read |
| game/simulation/combat/telemetry.py | Read |
| game/simulation/interfaces/ai_controller.py | Read |
| game/ui/screens/planet_list_window.py | Read |
| game/ui/screens/strategy_ui_action_router.py | Read |
| game/ui/screens/setup_renderer.py | Read |
| game/ui/panels/system_tree_panel.py | Read |
| game/simulation/entities/ship_stats.py | Read |
| game/ui/services/battle_ui_service.py | Read |
| game/simulation/combat/targeting_system.py | Read |
| game/ui/panels/race_theme_gallery.py | Read |
| game/ui/screens/battle_setup/panels/left_panel.py | Read |
| game/ui/screens/build_queue_viewmodel.py | Read |
| game/simulation/systems/tick_phase.py | Read |
| game/services/llm/types.py | Read |
| game/ui/screens/workshop_data_loader.py | Read |
| game/strategy/data/galaxy_state.py | Read |
| game/ui/widgets/ui_element_registry.py | Read |
| game/strategy/services/ability_iterator.py | Read |
| game/ui/screens/build_queue_list_window.py | Read |
| game/ui/services/image/provider.py | Read |
| game/simulation/services/__init__.py | Read |
| game/strategy/services/empire_economy_service.py | Read |
| game/ai/combat_utils.py | Read |
| game/ui/components/filters/tri_state_widget.py | Read |
| game/strategy/data/component_activation_state.py | Read |
| game/ui/screens/__init__.py | Read |
| game/strategy/data/fleet_battle_adapter.py | Read |
| game/ui/screens/strategy_superweapons.py | Read |
| game/core/state_machine.py | Read |
| game/ui/screens/test_lab/details/__init__.py | Read |
| game/ui/services/image/__init__.py | Read |
| game/strategy/facade/dto/__init__.py | Read |
| game/ui/screens/list_data_source_base.py | Read |
| game/ui/screens/test_lab/results_panel.py | Read |
| game/simulation/components/component_resource_manager.py | Read |
| game/simulation/battle_outcome.py | Read |
| game/strategy/combat/__init__.py | Read |
| game/ui/screens/strategy_windows/fleet_report_ctrl.py | Read |
| game/strategy/generation/density/primitives/spiral_arm.py | Read |
| game/ui/screens/strategy_detail_formatter.py | Read |
| game/strategy/generation/star_generator.py | Read |
| game/ui/services/tkinter_utils.py | Read |
| game/strategy/data/planet_atmosphere.py | Read |
| game/strategy/generation/density/primitives/linear.py | Read |
| game/research/data/tech_tree.py | Read |
| game/ui/screens/test_lab/test_run_card.py | Read |
| game/ui/screens/setup_data_io.py | Read |
| game/strategy/engine/planet_energy_engine.py | Read |
| game/ai/behaviors.py | Read |
| game/core/resources.py | Read |
| game/ui/panels/design_report_panel.py | Read |
| game/simulation/replay/replay_capture.py | Read |
| game/strategy/facade/dto/system_dto.py | Read |
| game/ui/screens/strategy_windows/planet_abilities_ctrl.py | Read |
| game/ui/screens/data_list_window_mixin.py | Read |
| game/strategy/engine/atmosphere_engine.py | Read |
| game/strategy/engine/fleet_movement_engine.py | Read |
| game/ui/filters/filter_state.py | Read |
| game/ui/screens/race_validator.py | Read |
| game/simulation/services/design_loader.py | Read |
| game/ui/screens/build_queue_helpers.py | Read |
| game/ui/screens/builder/right_panel.py | Read |
| game/simulation/entities/stat_contributors/defense.py | Read |
| game/simulation/interfaces/ability_protocols.py | Read |
| game/strategy/events/event_log.py | Read |
| game/ui/screens/strategy_windows/selection_prompts.py | Read |
| game/strategy/services/component_inspector.py | Read |
| game/strategy/data/design_role_registry.py | Read |
| game/ui/panels/race_environment_panel.py | Read |
| game/ui/screens/menu_scene.py | Read |
| game/ui/screens/strategy_windows/transfer_dialogs.py | Read |
| game/simulation/interfaces/entity_protocols.py | Read |
| game/simulation/entities/stat_contributors/__init__.py | Read |
| game/strategy/services/ability_sources/warp_point.py | Read |
| game/simulation/replay/__init__.py | Read |
| game/ui/screens/builder/modifier_row.py | Read |
| game/strategy/data/fleet_hierarchy.py | Read |
| game/strategy/services/design_validator.py | Read |
| game/core/protocols/boundary.py | Read |
| game/ui/screens/radiation_shield_editor.py | Read |
| game/strategy/engine/commands/registry.py | Read |
| game/simulation/systems/battle_end_conditions.py | Read |
| game/simulation/battle_runner.py | Read |
| game/ui/screens/event_log_data_source.py | Read |
| game/strategy/validation/transfer_validator.py | Read |
| game/ui/screens/workshop_data_reloader.py | Read |
| game/simulation/managers/battle_state_manager.py | Read |
| game/ui/renderer/camera.py | Read |
| game/ui/panels/ship_stats_renderer.py | Read |
| game/ui/screens/transfer_dialog.py | Read |
| game/ui/screens/empire_build_queue_filter_manager.py | Read |
| game/core/config.py | Read |
| game/strategy/engine/handlers/build.py | Read |
| game/ui/screens/test_lab/component_dropdown.py | Read |
| game/ui/fonts.py | Read |
| game/simulation/interfaces/component_protocols.py | Read |
| game/simulation/combat/ability_stat_registry.py | Read |
| game/run_loop.py | Read |
| game/ui/panels/race_portrait_gallery.py | Read |
| game/strategy/facade/slices/fleet_slice.py | Read |
| game/ui/screens/strategy_input_handler.py | Read |
| game/ui/screens/fleet_report_view_model.py | Read |
| game/simulation/replay/replay_serialization.py | Read |
| game/strategy/services/ability_sources/storm.py | Read |
| game/ui/screens/strategy_windows/empire_panel_ctrl.py | Read |
| game/ui/screens/builder/modifier_config.py | Read |
| game/ui/screens/empire_panel_window.py | Read |
| game/ui/screens/battle_setup/fleet_hierarchy_editor.py | Read |
| game/ui/screens/builder/modifier_utils.py | Read |
| game/ui/utils/resource_display.py | Read |
| game/core/event_logging.py | Read |
| game/ui/screens/planet_list_controller.py | Read |
| game/strategy/engine/order_handlers/join_fleet.py | Read |
| game/ui/screens/strategy_screen_assets.py | Read |
| game/ui/screens/builder_selection.py | Read |
| game/strategy/services/ability_sources/planet_intrinsic.py | Read |
| game/ui/screens/battle_results_screen.py | Read |
| game/ui/screens/save_selection_window.py | Read |
| game/strategy/services/ability_sources/system_archetype.py | Read |
| game/ui/screens/build_queue_selector.py | Read |
| game/strategy/data/star_generation_config.py | Read |
| game/strategy/data/naming.py | Read |
| game/strategy/generation/density/__init__.py | Read |
| game/strategy/engine/turn_engine.py | Read |
| game/strategy/engine/action_execution_engine.py | Read |
| game/simulation/combat/combat_events.py | Read |
| game/ui/panels/build_queue_drag_handler.py | Read |
| game/simulation/entities/ship_serialization.py | Read |
| game/ui/services/image/background.py | Read |
| game/strategy/engine/organics_consumption_engine.py | Read |
| game/ui/screens/strategy_screen_composition.py | Read |
| game/ui/screens/strategy_windows/__init__.py | Read |
| game/ui/screens/race_setup/panel_factory.py | Read |
| game/strategy/services/system_effects_collector.py | Read |
| game/strategy/generation/planet_image_registry.py | Read |
| game/strategy/generation/star_image_registry.py | Read |
| game/ui/screens/builder/schematic_view.py | Read |
| game/simulation/services/ship_materializer.py | Read |
| game/strategy/services/strategic_ability_scanner.py | Read |
| game/ui/effects/hit_effects.py | Read |
| game/simulation/combat/families/beam.py | Read |
| game/research/systems/research_service.py | Read |
| game/strategy/data/galaxy_spatial_index.py | Read |
| game/simulation/components/modifiers.py | Read |
| game/strategy/config/__init__.py | Read |
| game/simulation/battle_state.py | Read |
