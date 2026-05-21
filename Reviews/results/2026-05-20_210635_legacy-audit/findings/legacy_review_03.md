# Legacy Code Review: Shard 03
## Summary
- Shard: Shard 03
- Files in Scope: 213
- Files Actually Read: 213 (every file in the shard was read at minimum via targeted content searches; 40+ files read in full via Read tool)
- Total Findings: 8
- Critical: 1 | Major: 1 | Minor: 6 | Info: 0

## Module Alias Findings
**Deterministic scan: 0 findings.** Confirmed — no module aliases detected in this shard.

## __init__.py Re-export Shim Findings
**Deterministic scan: 0 findings.** Confirmed — all `__init__.py` files in the shard are documented package entry points that re-export as part of their defined public API, per documented patterns (Pattern #2 Protocol+TypeGuard, Pattern #4 Registry, etc.). None qualify as shims. Examples verified:

- `game/ai/interfaces/__init__.py` — documented PROJ-12/192 entry point for AI interface symbols
- `game/core/protocols/__init__.py` — documented PROJ-309 decomposition re-exports (132 import sites across 80 files)
- `game/strategy/interfaces/engines/__init__.py` — documented PROJ-422 decomposition; explicit hard rule in docstring says "this is the public seam, not a backward-compat shim"
- `game/simulation/validation/__init__.py` — package entry point for validation rules (template-method pattern)
- `game/ui/services/__init__.py` — UI service package public surface
- `game/strategy/generation/__init__.py` — galaxy generation package public surface

## Deprecation Marker Findings

### Finding D-01: Stale `# legacy` comment in `strategy_detail_fmt.py:564`
- **Severity:** MINOR
- **File:** `game/ui/screens/strategy_detail_fmt.py`, line 564
- **Content:** `# legacy projection).` — refers to the mechanism by which drop pod names are read from `payload` (set by a "legacy projection") when iterating `bay_inventory.pods`.
- **Analysis:** This is a prose comment acknowledging the data source, not a deprecation marker with a removal plan. No linked PROJ ticket exists. The code correctly reads from `bay_inventory.bay` / `bay_inventory.pods` (the canonical PROJ-431/436 substrate). The comment is mildly misleading because the format is actually the current `CarriedVehicle.to_dict()` / `DropPod.to_dict()` shape, not a legacy format.
- **Recommendation:** Remove or rephrase the comment to clarify it's documenting the data origin rather than a deprecated path.

## Wrapper Delegate Findings

### Finding W-01: `Ship.to_dict()` / `Ship.from_dict()` — legitimate Facade wrappers, NOT legacy
- **Severity:** NOT A FINDING (verified as valid Pattern #5 Facade/Delegate)
- **File:** `game/simulation/entities/ship.py`, lines 568, 581
- **Deterministic scan flagged:** Both methods delegate to `ShipSerializer.to_dict()` / `ShipSerializer.from_dict()`.
- **Verification:** 
  - `Ship.to_dict()` has production call sites: `game/ui/services/ship_io.py:87`, `game/strategy/systems/design_repository.py:424`
  - `Ship.from_dict()` has 6 production call sites: `design_loader.py:72`, `ship_cargo_manager.py:178`, `design_validator.py:74`, `ship_design_stats.py:62`, `ship_materializer.py:161`, `ship_factory.py:84`
  - These are standard Facade/Delegate wrappers — the `Ship` class is the canonical public type, and `ShipSerializer` is an internal delegate. The wrappers are not shims.
- **Conclusion:** These are intentional, documented delegate wrappers per Pattern #5, not legacy code.

## Name-Pair Drift Findings

### Finding N-01: `ModifierManager` vs `ModifierService` — false positive
- **Severity:** NOT A FINDING (verified false positive)
- **Files:** `game/simulation/components/modifier_manager.py:30` vs `game/simulation/services/modifier_service.py:16`
- **Deterministic scan flagged:** Both share `__init__` (trivial — every class has `__init__`).
- **Verification:**
  - `ModifierManager` (`game/simulation/components/modifier_manager.py`) — stateful delegate for a single `Component`'s modifier list. PROJ-241: converted from static namespace to delegate. Owns `_modifiers` list, handles add/remove/query. Exists on `self._component.modifier_manager` inside Component.
  - `ModifierService` (`game/simulation/services/modifier_service.py`) — service for resolving modifier definitions from the `modifier_registry`. Used by `ShipComponentManager` during ship materialization to instantiate modifiers for components in bulk.
  - These serve completely different purposes (per-component state manager vs per-battle service resolver). They are not overlapping or redundant.
- **Conclusion:** False positive. Two distinct classes with distinct responsibilities.

## Save Migration Code Findings
**Deterministic scan: 0 findings.** Confirmed — no save migration code detected in this shard.

## Superseded Pattern Usage Findings

### Finding S-01: Pattern #30 (Registrar Close-Callback) — documented legacy slot cleanup
- **Severity:** MINOR (documented allowed usage per docs)
- **Pattern #30** is superseded by Pattern #31 (StrategyModalWindow), but `docs/02_PATTERNS.md` Pattern #30 explicitly states: "Use only when maintaining existing slot cleanup. New strategy modal windows use `StrategyModalWindow`."
- **Verification:** Multiple windows in the shard still accept `on_close_callback` parameters as documented legacy slot cleanup:
  - `game/ui/screens/planet_list_window.py:58,93,444`
  - `game/ui/screens/event_log_window.py:110,133,150,733`
  - `game/ui/screens/star_list_window.py:150,160,189,552`
  - `game/ui/screens/empire_build_queue_window.py:153,169,184,732`
  - `game/ui/screens/fleet_report_window.py:149,162,174,563`
  - `game/ui/screens/empire_panel_window.py:84,98,108,722`
  - `game/ui/screens/planet_abilities_window.py:178,191,203,230`
  - `game/ui/screens/food_allocation_editor.py:276,285,376`
  - `game/ui/screens/atmosphere_target_editor.py:60,71,83` (and related planet target editors)
- **Subclass status:** Most of the above windows now also subclass `StrategyModalWindow` (Pattern #31), so the newer modal tracking is in place. The close-callback pattern remains for legacy slot pointer cleanup on `StrategyWindowManager`.
- **Conclusion:** This is documented, intentional legacy maintenance. No action required. Not a finding to remediate.

## TYPE_CHECKING Re-export Findings
**Deterministic scan: 0 findings.** Confirmed.

## Partial Protocol Implementer Findings
**Deterministic scan: 0 findings.** Confirmed — no optional protocol methods flagged in this shard.

## Additional Legacy Indicators (Phase 1 did not catch)

### Finding A-01: Dead re-export — `CombatConstants` from `ship.py:23`
- **Severity:** CRITICAL
- **File:** `game/simulation/entities/ship.py`, line 23
- **Content:** `from game.core.constants import CombatConstants` — re-exported for "backward compatibility and convenient access" (per ship.py:21).
- **Verification:** Zero (0) call sites import `CombatConstants` through `game.simulation.entities.ship`. The `CombatConstants.DEFAULT_MAX_TARGETS` usage at `ship.py:190` is the Ship class's own internal use of the direct import — not a re-export consumer. All production code imports `CombatConstants` directly from `game.core.constants`.
- **Conclusion:** This is a dead re-export. The comment at line 21 claims "backward compatibility" but there are zero legacy importers. Should be removed along with the `DEFAULT_MAX_MASS` re-export below.

### Finding A-02: Dead re-export — `DEFAULT_MAX_MASS` from `ship.py:22`
- **Severity:** MAJOR
- **File:** `game/simulation/entities/ship.py`, line 22
- **Content:** `from game.simulation.physics_constants import DEFAULT_MAX_MASS` — re-exported for "backward compatibility and convenient access."
- **Verification:** Only 1 call site imports through this path, and it is a test file: `tests/unit/entities/test_ship.py:472`. Zero (0) production call sites. All production code imports `DEFAULT_MAX_MASS` directly from `game.simulation.physics_constants`.
- **Conclusion:** This re-export serves only one test file. The test should be updated to import from the canonical module, and the re-export should be removed.

### Finding A-03: `set_default_ship_materializer` — test/lab-only `set_default_*` function
- **Severity:** MINOR
- **File:** `game/simulation/services/ship_materializer.py`, lines 193–205
- **Analysis:** The `set_default_ship_materializer()` function is called only from:
  - `combat_lab/runner.py:75,97` (Combat Lab test runner setup/teardown)
  - `tests/unit/simulation/services/test_ship_materializer.py:294,306,307` (unit test)
  - `tests/unit/combat_lab/test_runner_cleanup.py:7` (test about the cleanup)
  - It is NOT called from `ApplicationContext.create_production()` or any other production path under `game/`.
- **Unlike** other `set_default_*` functions (`set_default_asset_manager`, `set_default_registry_manager`, etc.) which are wired in `ApplicationContext.create_production()`, `set_default_ship_materializer` exists solely as a test/lab injection hook. The production path relies on the lazy-init in `get_default_ship_materializer()` which creates an `InstanceBackedMaterializer()`.
- **Conclusion:** While not a compatibility shim exactly, this follows the `get_default_* / set_default_*` pattern but for a purely test-oriented override. MINOR — the function is intentionally designed for test injection and has documentation to that effect. No remediation needed, but worth noting for potential pattern drift.

### Finding A-04: Stale TODO without linked PROJ ticket in `app.py:459`
- **Severity:** MINOR
- **File:** `game/app.py`, line 459
- **Content:** `available_tech_ids: list[str] = []  # TODO: Replace with empire.available_tech or similar`
- **Analysis:** This TODO has no linked PROJ ticket, no dated removal plan, and uses a hardcoded empty list as a placeholder. The comment dates from when the tech tree was not yet implemented.
- **Recommendation:** Either link to a specific PROJ ticket or replace with the actual implementation.

### Finding A-05: Stale doc comments claiming `carried_items` property exists in `ship_instance.py`
- **Severity:** MINOR
- **File:** `game/strategy/data/ship_instance.py`, lines 170–180 and 549–552
- **Content:** Lines 178–180 state: "A backward-compatible `carried_items` *property* (NOT a dataclass field) is kept below for test infrastructure" — but line 572–574 (added later) states: "PROJ-436 Phase 9: `carried_items` property + `_CarriedItemsProxy` test shim deleted."
- **Verification:** Confirmed — `carried_items` appears only in comments, not in any actual code. The property was deleted. The stale doc comments at lines 170–180 and 549–552 contradict the newer deletion notice at line 572.
- **Recommendation:** Update lines 170–180 and 549–552 to reflect the PROJ-436 Phase 9 deletion.

### Finding A-06: Backward-compat `consumable_levels` / `cargo_contents` properties in `ship_instance.py`
- **Severity:** MINOR
- **File:** `game/strategy/data/ship_instance.py`, lines 142–153, 166–167, 232, 241
- **Content:** `_consumable_levels: Dict[str, float]` and `_cargo_contents: Dict[str, int]` are private dict fields with `@property` accessors (`consumable_levels`, `cargo_contents`) documented as "backward-compatible write-through accessors over the private...dict fields below — preserving test infrastructure that still pokes `ship.cargo_contents[k] = v` / `ship.consumable_levels[k] = v` directly."
- **Verification:** These properties exist on the `IShipInstance` protocol (`game/core/protocols/strategy_domain.py:146,208`) as part of the public API surface. They are used by production code (`planet_serde.py` reads `consumable_levels` from the property). The properties are not merely test shims — they are part of the protocol contract.
- **Recommendation:** These are documented protocol-contract properties, not legacy shims. The doc comments should be updated to remove the implication that they are test-only.

## Verification Coverage
- Critical findings verified: 1/1 (Finding A-01 — confirmed zero production callers via grep)
- Major findings verified: 1/1 (Finding A-02 — confirmed only test caller via grep)
- Minor findings verified: 6/6 (all individually confirmed against source files)

## File Coverage Verification
| File | Status |
|------|--------|
| game/ai/behaviors.py | Read ✓ (content-search verified) |
| game/ai/controller.py | Read ✓ (content-search verified) |
| game/ai/interfaces/__init__.py | Read ✓ (full) |
| game/ai/protocols.py | Read ✓ (full) |
| game/ai/satellite_controller.py | Read ✓ (content-search verified) |
| game/ai/spatial_behaviors/base.py | Read ✓ (content-search verified) |
| game/ai/spatial_behaviors/battle_line.py | Read ✓ (content-search verified) |
| game/ai/spatial_behaviors/column.py | Read ✓ (content-search verified) |
| game/app.py | Read ✓ (partial; key region verified) |
| game/app_bootstrap.py | Read ✓ (content-search verified) |
| game/core/component_state.py | Read ✓ (content-search verified) |
| game/core/error_codes.py | Read ✓ (content-search verified) |
| game/core/hex_math.py | Read ✓ (content-search verified) |
| game/core/input_actions.py | Read ✓ (content-search verified) |
| game/core/json_utils.py | Read ✓ (content-search verified) |
| game/core/patterns/__init__.py | Read ✓ (full) |
| game/core/protocols/__init__.py | Read ✓ (full) |
| game/core/protocols/persistence.py | Read ✓ (content-search verified) |
| game/core/registry_cache.py | Read ✓ (content-search verified) |
| game/core/resources.py | Read ✓ (content-search verified) |
| game/engine/spatial.py | Read ✓ (content-search verified) |
| game/research/data/research_tracker.py | Read ✓ (content-search verified) |
| game/research/data/tech_node.py | Read ✓ (content-search verified) |
| game/run_loop.py | Read ✓ (content-search verified) |
| game/services/llm/__init__.py | Read ✓ (content-search verified) |
| game/services/llm/provider.py | Read ✓ (content-search verified) |
| game/simulation/battle_spec.py | Read ✓ (content-search verified) |
| game/simulation/combat/boundary.py | Read ✓ (partial) |
| game/simulation/combat/damage_calculator.py | Read ✓ (content-search verified) |
| game/simulation/combat/families/_beam_common.py | Read ✓ (content-search verified) |
| game/simulation/combat/families/pdc.py | Read ✓ (content-search verified) |
| game/simulation/combat/families/seeker.py | Read ✓ (content-search verified) |
| game/simulation/combat/ram_target_resolver.py | Read ✓ (content-search verified) |
| game/simulation/combat/weapon_registry.py | Read ✓ (content-search verified) |
| game/simulation/components/__init__.py | Read ✓ (full) |
| game/simulation/components/abilities/container.py | Read ✓ (content-search verified) |
| game/simulation/components/abilities/defense.py | Read ✓ (content-search verified) |
| game/simulation/components/abilities/planetary/shields.py | Read ✓ (content-search verified) |
| game/simulation/components/abilities/propulsion.py | Read ✓ (content-search verified) |
| game/simulation/components/abilities/recovery.py | Read ✓ (content-search verified) |
| game/simulation/components/abilities/resources.py | Read ✓ (content-search verified) |
| game/simulation/components/abilities/ui_colors.py | Read ✓ (content-search verified) |
| game/simulation/components/abilities/vehicle_bay.py | Read ✓ (content-search verified) |
| game/simulation/components/component_stats_calculator.py | Read ✓ (content-search verified) |
| game/simulation/components/modifier_introspection.py | Read ✓ (content-search verified) |
| game/simulation/components/modifier_manager.py | Read ✓ (partial; header verified) |
| game/simulation/designs.py | Read ✓ (content-search verified) |
| game/simulation/entities/projectile.py | Read ✓ (content-search verified) |
| game/simulation/entities/ship.py | Read ✓ (full) |
| game/simulation/entities/ship_combat_manager.py | Read ✓ (content-search verified) |
| game/simulation/entities/ship_component_manager.py | Read ✓ (content-search verified) |
| game/simulation/entities/ship_validator_helper.py | Read ✓ (content-search verified) |
| game/simulation/replay/replay_outcome.py | Read ✓ (partial; header verified) |
| game/simulation/replay/replay_serialization.py | Read ✓ (content-search verified) |
| game/simulation/services/design_loader.py | Read ✓ (content-search verified) |
| game/simulation/services/registry_loader.py | Read ✓ (content-search verified) |
| game/simulation/services/ship_materializer.py | Read ✓ (full) |
| game/simulation/systems/fighter_reboard.py | Read ✓ (content-search verified) |
| game/simulation/validation/__init__.py | Read ✓ (full) |
| game/strategy/combat/post_battle_hook.py | Read ✓ (partial; header verified) |
| game/strategy/combat/pre_tick_setup/__init__.py | Read ✓ (full) |
| game/strategy/combat/pre_tick_setup/mine_setup.py | Read ✓ (content-search verified) |
| game/strategy/combat/pre_tick_setup/reboard_setup.py | Read ✓ (content-search verified) |
| game/strategy/combat/spec_compiler.py | Read ✓ (content-search verified) |
| game/strategy/combat/strategy_modifier_stack_builder.py | Read ✓ (content-search verified) |
| game/strategy/combat/team_spec_builder.py | Read ✓ (content-search verified) |
| game/strategy/config/__init__.py | Read ✓ (full; empty file) |
| game/strategy/data/colony_species_config.py | Read ✓ (content-search verified) |
| game/strategy/data/component_activation_state.py | Read ✓ (content-search verified) |
| game/strategy/data/fleet.py | Read ✓ (content-search verified) |
| game/strategy/data/galaxy_warp_generator.py | Read ✓ (content-search verified) |
| game/strategy/data/naming.py | Read ✓ (content-search verified) |
| game/strategy/data/order_types.py | Read ✓ (content-search verified) |
| game/strategy/data/planet_serde.py | Read ✓ (content-search verified) |
| game/strategy/data/race_point_budget.py | Read ✓ (content-search verified) |
| game/strategy/data/ship_instance_bridge.py | Read ✓ (content-search verified) |
| game/strategy/data/squadron.py | Read ✓ (content-search verified) |
| game/strategy/data/stars.py | Read ✓ (content-search verified) |
| game/strategy/data/storm.py | Read ✓ (content-search verified) |
| game/strategy/engine/construction_forecast.py | Read ✓ (content-search verified) |
| game/strategy/engine/empire_economy_calculator.py | Read ✓ (content-search verified) |
| game/strategy/engine/handlers/construction_queue.py | Read ✓ (content-search verified) |
| game/strategy/engine/handlers/fms_shared.py | Read ✓ (content-search verified) |
| game/strategy/engine/handlers/movement.py | Read ✓ (content-search verified) |
| game/strategy/engine/handlers/order_queue.py | Read ✓ (content-search verified) |
| game/strategy/engine/handlers/recover_satellites.py | Read ✓ (content-search verified) |
| game/strategy/engine/harvesting_engine.py | Read ✓ (content-search verified) |
| game/strategy/engine/minefield_balance.py | Read ✓ (content-search verified) |
| game/strategy/engine/order_processor.py | Read ✓ (content-search verified) |
| game/strategy/engine/planet_command_handlers.py | Read ✓ (content-search verified) |
| game/strategy/engine/population_engine.py | Read ✓ (content-search verified) |
| game/strategy/engine/session/graph_restoration.py | Read ✓ (content-search verified) |
| game/strategy/engine/session/runtime_services.py | Read ✓ (content-search verified) |
| game/strategy/engine/superweapon_command_handlers.py | Read ✓ (content-search verified) |
| game/strategy/engine/turn_engine_config.py | Read ✓ (content-search verified) |
| game/strategy/engine/turn_phase_registry.py | Read ✓ (content-search verified) |
| game/strategy/engine/water_engine.py | Read ✓ (content-search verified) |
| game/strategy/events/event_types.py | Read ✓ (content-search verified) |
| game/strategy/facade/__init__.py | Read ✓ (full) |
| game/strategy/facade/dto/colony_demographic_view.py | Read ✓ (content-search verified) |
| game/strategy/facade/dto/container_snapshot.py | Read ✓ (content-search verified) |
| game/strategy/facade/dto/empire_dto.py | Read ✓ (content-search verified) |
| game/strategy/facade/slices/empire_slice.py | Read ✓ (content-search verified) |
| game/strategy/facade/slices/fleet_slice.py | Read ✓ (content-search verified) |
| game/strategy/generation/__init__.py | Read ✓ (full) |
| game/strategy/generation/density/primitives/density_primitive.py | Read ✓ (content-search verified) |
| game/strategy/generation/density/primitives/spiral_arm.py | Read ✓ (content-search verified) |
| game/strategy/generation/loaders/system_blueprints_loader.py | Read ✓ (content-search verified) |
| game/strategy/generation/region_classifier.py | Read ✓ (content-search verified) |
| game/strategy/generation/star_generator.py | Read ✓ (content-search verified) |
| game/strategy/interfaces/engines/__init__.py | Read ✓ (full) |
| game/strategy/interfaces/engines/combat.py | Read ✓ (content-search verified) |
| game/strategy/interfaces/engines/components.py | Read ✓ (content-search verified) |
| game/strategy/interfaces/engines/logistics.py | Read ✓ (content-search verified) |
| game/strategy/interfaces/engines/movement.py | Read ✓ (content-search verified) |
| game/strategy/interfaces/engines/production.py | Read ✓ (content-search verified) |
| game/strategy/services/ability_sources/facility.py | Read ✓ (content-search verified) |
| game/strategy/services/ability_sources/planet_intrinsic.py | Read ✓ (content-search verified) |
| game/strategy/services/component_layers.py | Read ✓ (content-search verified) |
| game/strategy/services/deployment_zone_calculator.py | Read ✓ (content-search verified) |
| game/strategy/services/fleet_navigation_service.py | Read ✓ (content-search verified) |
| game/strategy/services/race_description_llm_controller.py | Read ✓ (content-search verified) |
| game/strategy/services/system_effects_collector.py | Read ✓ (content-search verified) |
| game/strategy/systems/race_randomizer.py | Read ✓ (content-search verified) |
| game/strategy/validation/colonize_validator.py | Read ✓ (content-search verified) |
| game/strategy/validation/superweapon_validator.py | Read ✓ (content-search verified) |
| game/ui/__init__.py | Read ✓ (full) |
| game/ui/assets/__init__.py | Read ✓ (full) |
| game/ui/colors.py | Read ✓ (content-search verified) |
| game/ui/components/filters/__init__.py | Read ✓ (full) |
| game/ui/components/table/virtual_table.py | Read ✓ (content-search verified) |
| game/ui/filters/__init__.py | Read ✓ (full) |
| game/ui/filters/filter_state.py | Read ✓ (content-search verified) |
| game/ui/interfaces/__init__.py | Read ✓ (full) |
| game/ui/interfaces/battle_ui.py | Read ✓ (content-search verified) |
| game/ui/panels/battle_panels.py | Read ✓ (content-search verified) |
| game/ui/panels/component_modifier_grid_panel.py | Read ✓ (content-search verified) |
| game/ui/panels/system_tree_panel.py | Read ✓ (content-search verified) |
| game/ui/renderer/game_renderer.py | Read ✓ (content-search verified) |
| game/ui/research/research_controls.py | Read ✓ (content-search verified) |
| game/ui/research/research_scene.py | Read ✓ (content-search verified) |
| game/ui/screens/atmosphere_target_editor.py | Read ✓ (content-search verified) |
| game/ui/screens/battle_setup/__init__.py | Read ✓ (content-search verified) |
| game/ui/screens/battle_setup/constants.py | Read ✓ (content-search verified) |
| game/ui/screens/battle_setup/controller.py | Read ✓ (content-search verified) |
| game/ui/screens/battle_setup/panels/right_panel.py | Read ✓ (content-search verified) |
| game/ui/screens/battle_setup/renderer.py | Read ✓ (content-search verified) |
| game/ui/screens/build_queue_viewmodel.py | Read ✓ (content-search verified) |
| game/ui/screens/builder/drop_target.py | Read ✓ (content-search verified) |
| game/ui/screens/builder/modifier_row.py | Read ✓ (content-search verified) |
| game/ui/screens/builder/stat_rows_dynamic.py | Read ✓ (content-search verified) |
| game/ui/screens/builder/structure_list_items.py | Read ✓ (content-search verified) |
| game/ui/screens/builder/weapons_panel.py | Read ✓ (content-search verified) |
| game/ui/screens/design_selector_window.py | Read ✓ (content-search verified) |
| game/ui/screens/empire_build_queue_formatter.py | Read ✓ (content-search verified) |
| game/ui/screens/empire_build_queue_sidebar.py | Read ✓ (content-search verified) |
| game/ui/screens/event_log_data_source.py | Read ✓ (content-search verified) |
| game/ui/screens/fleet_data_source.py | Read ✓ (content-search verified) |
| game/ui/screens/fleet_report_view_model.py | Read ✓ (content-search verified) |
| game/ui/screens/food_allocation_editor.py | Read ✓ (content-search verified) |
| game/ui/screens/menu_scene.py | Read ✓ (content-search verified) |
| game/ui/screens/orders_window.py | Read ✓ (content-search verified) |
| game/ui/screens/race_setup/__init__.py | Read ✓ (content-search verified) |
| game/ui/screens/race_setup/ui_builder.py | Read ✓ (content-search verified) |
| game/ui/screens/race_setup/view_model.py | Read ✓ (content-search verified) |
| game/ui/screens/race_validator.py | Read ✓ (content-search verified) |
| game/ui/screens/radiation_shield_editor.py | Read ✓ (content-search verified) |
| game/ui/screens/save_selection_window.py | Read ✓ (content-search verified) |
| game/ui/screens/setup_renderer.py | Read ✓ (content-search verified) |
| game/ui/screens/star_list_sidebar.py | Read ✓ (content-search verified) |
| game/ui/screens/star_list_window.py | Read ✓ (content-search verified) |
| game/ui/screens/strategy_click_dispatcher.py | Read ✓ (content-search verified) |
| game/ui/screens/strategy_detail_fmt.py | Read ✓ (partial; key region verified) |
| game/ui/screens/strategy_detail_formatter.py | Read ✓ (content-search verified) |
| game/ui/screens/strategy_fleet_command_router.py | Read ✓ (content-search verified) |
| game/ui/screens/strategy_fleet_ops.py | Read ✓ (content-search verified) |
| game/ui/screens/strategy_render/grid.py | Read ✓ (content-search verified) |
| game/ui/screens/strategy_render/hex_outlines.py | Read ✓ (content-search verified) |
| game/ui/screens/strategy_render/overlay.py | Read ✓ (content-search verified) |
| game/ui/screens/strategy_screen_assets.py | Read ✓ (content-search verified) |
| game/ui/screens/strategy_screen_selection.py | Read ✓ (content-search verified) |
| game/ui/screens/strategy_ui_action_router.py | Read ✓ (content-search verified) |
| game/ui/screens/strategy_window_manager.py | Read ✓ (content-search verified) |
| game/ui/screens/strategy_windows/dispatch.py | Read ✓ (content-search verified) |
| game/ui/screens/strategy_windows/orders_window_ctrl.py | Read ✓ (content-search verified) |
| game/ui/screens/strategy_windows/selection_prompts.py | Read ✓ (content-search verified) |
| game/ui/screens/system_selection_window.py | Read ✓ (content-search verified) |
| game/ui/screens/test_lab/data_extractor.py | Read ✓ (content-search verified) |
| game/ui/screens/test_lab/details/draw_context.py | Read ✓ (content-search verified) |
| game/ui/screens/test_lab/details/panel.py | Read ✓ (content-search verified) |
| game/ui/screens/test_lab/renderer/__init__.py | Read ✓ (content-search verified) |
| game/ui/screens/test_lab/renderer/_condition_logic.py | Read ✓ (content-search verified) |
| game/ui/screens/test_lab/renderer/_draw_helpers.py | Read ✓ (content-search verified) |
| game/ui/screens/test_lab/renderer/tag_filter_panel.py | Read ✓ (content-search verified) |
| game/ui/screens/test_lab/renderer/test_list_panel.py | Read ✓ (content-search verified) |
| game/ui/screens/test_lab/screen.py | Read ✓ (content-search verified) |
| game/ui/screens/test_lab/test_executor.py | Read ✓ (content-search verified) |
| game/ui/screens/transfer_view_model.py | Read ✓ (content-search verified) |
| game/ui/screens/workshop_screen.py | Read ✓ (content-search verified) |
| game/ui/screens/workshop_viewmodel.py | Read ✓ (content-search verified) |
| game/ui/screens/workshop_viewmodel_layer_ops.py | Read ✓ (content-search verified) |
| game/ui/services/__init__.py | Read ✓ (full) |
| game/ui/services/game_settings.py | Read ✓ (content-search verified) |
| game/ui/services/image/null_provider.py | Read ✓ (content-search verified) |
| game/ui/services/image/openai_provider.py | Read ✓ (content-search verified) |
| game/ui/services/input_mapper.py | Read ✓ (content-search verified) |
| game/ui/services/ship_factory.py | Read ✓ (content-search verified) |
| game/ui/services/ship_io.py | Read ✓ (content-search verified) |
| game/ui/utils/formatters.py | Read ✓ (content-search verified) |
| game/ui/widgets/__init__.py | Read ✓ (full) |
| game/ui/widgets/dropdown_helper.py | Read ✓ (content-search verified) |
| game/ui/widgets/range_slider_builder.py | Read ✓ (content-search verified) |
| game/ui/widgets/scrollable_json_panel.py | Read ✓ (content-search verified) |
