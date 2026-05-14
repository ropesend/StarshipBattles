# Legacy Code Review: Shard 03

## Summary
- Shard: Shard 03
- Files in Scope: 163
- Files Actually Read: 163
- Total Findings: 7
- Critical: 0 | Major: 0 | Minor: 7 | Info: 0

---

## Minor Findings

### MIN-03-001: Stale legacy comment in conflict_resolution_engine.py
- **File:** `game/strategy/engine/conflict_resolution_engine.py:379`
- **Type:** Deprecation marker / stale comment
- **Detail:** Comment block references the deleted `_rng_resolve_empty_fleets` function: `# BUG-126: every-fleet-empty case is not a real combat. The legacy '_rng_resolve_empty_fleets' only existed to keep empire bookkeeping consistent when picking a "winner"...`
- **Severity:** MINOR — purely documentary, no dead code path remains. The function referenced was already removed. The comment serves as historical context but could be shortened to just the first sentence.
- **Recommendation:** Trim the comment to remove stale reference to deleted function.

### MIN-03-002: "Old route" comment in open_warp_point.py
- **File:** `game/strategy/engine/superweapon_handlers/open_warp_point.py:89`
- **Type:** Deprecation marker / stale comment
- **Detail:** `# old route would otherwise walk the entire stale path to completion.` — comment refers to pre-Issue-#31 behavior.
- **Severity:** MINOR — the Issue #31 fix is in place (path invalidation via `invalidate_paths_for_graph_change`). The comment documents WHY the invalidation is needed but uses a temporal "old" marker.
- **Recommendation:** Replace "old route" with a factual statement like "without this invalidation, the old route..."

### MIN-03-003: `create_modifier` wrapper delegate in component_constants.py
- **File:** `game/simulation/components/component_constants.py:45`
- **Type:** Wrapper delegate
- **Detail:** `Modifier.create_modifier(value=None)` delegates directly to `ApplicationModifier(self, value)` with passthrough args. This is a thin factory/convenience method rather than a full legacy wrapper.
- **Severity:** MINOR — 1-line body, zero-argument passthrough. The `Modifier` class is the canonical definition owner, and `create_modifier` reads as idiomatic factory method. No callers need migration — `ApplicationModifier` is a sibling class in the same file. This is not a "wrapper delegate" in the legacy sense (no separate module, no different API surface).
- **Recommendation:** Keep as-is; pattern is conventional factory method on definition class.

### MIN-03-004: "Historical import retained for parity" comments in screen_router.py
- **File:** `game/screen_router.py:182`, `:304`, `:429`
- **Type:** Stale comments / code parity artifacts
- **Detail:** Three locations have `import pygame_gui  # noqa: F401 — historical import retained for parity.` These import statements serve no functional purpose — pygame_gui is already imported via the `from pygame_gui.windows import ...` pattern in other methods, and the `menu_ui_manager` already references pygame_gui in its type. The "for parity" justification is weak.
- **Severity:** MINOR — no runtime impact. Clutters the file with unused imports.
- **Recommendation:** Remove the three dead imports and their comments.

### MIN-03-005: Re-export shim: spectrum.py re-exported from stars.py for backward compat
- **File:** `game/strategy/data/spectrum.py:7-8`
- **Type:** Re-export shim (backward-compat)
- **Detail:** Module docstring states: `stars.py re-exports the symbol for backwards-compat with the 15+ existing import sites.` This is a canonical Pattern #36 re-export shim — the `Spectrum` class was moved from `stars.py` to its own file for LOC budget, and `stars.py` re-exports for backward compat. The import sites should migrate to import from `spectrum.py` directly, then the re-export in `stars.py` removed.
- **Severity:** MINOR — documented Pattern #36 shim with a clear migration path (update ~15+ call sites).
- **Recommendation:** Migrate the ~15 call sites to import from `game.strategy.data.spectrum`, then remove the re-export from `stars.py`. This is a PROJ-372 vestige.

### MIN-03-006: Re-export shim: star_system.py re-exported from galaxy.py for backward compat
- **File:** `game/strategy/data/star_system.py:3-5`
- **Type:** Re-export shim (backward-compat)
- **Detail:** Module docstring states: `galaxy.py re-exports both classes for the 7+ external import sites.` Same pattern as MIN-03-005 — `WarpPoint` and `StarSystem` were moved from `galaxy.py` to their own file, and `galaxy.py` re-exports for backward compat.
- **Severity:** MINOR — documented Pattern #36 shim (PROJ-372 vestige).
- **Recommendation:** Migrate ~7 call sites, remove re-export from galaxy.py.

### MIN-03-007: Init `__init__.py` as-alias import for side-effect registration
- **File:** `game/ui/services/image/__init__.py:37`
- **Type:** Init re-export
- **Detail:** `from game.ui.services.image import null_provider as _null_provider  # noqa: F401` — this imports the `null_provider` module with an alias to trigger its import-time registration. This is a documented Pattern #4 (Registry) convention for provider registration — `openai_provider` on line 38 does the same thing. The `as _null_provider` alias prevents the module name from leaking into the package namespace while still running its side effects.
- **Severity:** MINOR — this is intentional side-effect import for provider registration, not a legacy artifact. The `# noqa: F401` is necessary.
- **Recommendation:** No action needed. This is a standard provider-registration pattern. Remove from the legacy tracking ledger.

---

## Additional Legacy Indicators (Phase 1 did not catch)

None detected. All files in this shard appeared clean of additional legacy indicators beyond what Phase 1 deterministic scans flagged. Specifically:

- **No shim files** (files that exist solely to re-export) — all `__init__.py` re-exports are documented public API surface.
- **No stale PROJ comments** — all PROJ references found are to active or recently-completed projects; none reference long-finished work without actionable content.
- **No test-only callers** for any public production API.
- **No unused `set_default_*` shim functions** — all `get_default_*`/`set_default_*` pairs found have active production callers.
- **No save-migration code** — confirmed by manual review and Phase 1 JSON.
- **No TYPE_CHECKING-only re-exports** going beyond circular-import resolution.
- **No optional protocol methods** with missing implementations in production.

---

## Verification Coverage
- Critical findings verified: 0/0 (no critical findings)
- Major findings sampled: 0/0 (no major findings)
- All 7 minor findings source-verified against actual files
- Superseded Pattern #30 (Registrar Close-Callback): no files in this shard use pattern #30 directly. Strategy modal windows in this shard (e.g., `planet_target_editor_base.py`, `atmosphere_target_editor.py`, `build_queue_list_window.py`) all use Pattern #31 (`StrategyModalWindow`).

---

## File Coverage Verification
| File | Status |
|------|--------|
| game/ai/ai_factory.py | Read ✓ |
| game/ai/group_target_coordinator.py | Read ✓ |
| game/ai/interfaces/__init__.py | Read ✓ |
| game/ai/protocols.py | Read ✓ |
| game/ai/spatial_behaviors/__init__.py | Read ✓ |
| game/ai/spatial_behaviors/battle_line.py | Read ✓ |
| game/ai/spatial_behaviors/escort.py | Read ✓ |
| game/assets/asset_manager.py | Read ✓ |
| game/core/combat_types.py | Read ✓ |
| game/core/config.py | Read ✓ |
| game/core/error_codes.py | Read ✓ |
| game/core/patterns/__init__.py | Read ✓ |
| game/core/protocols/common.py | Read ✓ |
| game/core/protocols/strategy_entities.py | Read ✓ |
| game/core/return_destination.py | Read ✓ |
| game/core/state_machine.py | Read ✓ |
| game/core/validation.py | Read ✓ |
| game/screen_router.py | Read ✓ |
| game/services/llm/__init__.py | Read ✓ |
| game/services/llm/defaults.py | Read ✓ |
| game/services/llm/provider.py | Read ✓ |
| game/services/provider_factory.py | Read ✓ |
| game/simulation/battle_state.py | Read ✓ |
| game/simulation/combat/ability_stat_registry.py | Read ✓ |
| game/simulation/combat/damage_calculator.py | Read ✓ |
| game/simulation/combat/families/beam.py | Read ✓ |
| game/simulation/combat/modifier_stack.py | Read ✓ |
| game/simulation/combat/weapon_registry.py | Read ✓ |
| game/simulation/components/abilities/__init__.py | Read ✓ |
| game/simulation/components/abilities/harvester.py | Read ✓ |
| game/simulation/components/abilities/planetary/__init__.py | Read ✓ |
| game/simulation/components/abilities/planetary/_shared.py | Read ✓ |
| game/simulation/components/abilities/resources.py | Read ✓ |
| game/simulation/components/component_constants.py | Read ✓ |
| game/simulation/entities/layer_data.py | Read ✓ |
| game/simulation/entities/ship_combat_engine.py | Read ✓ |
| game/simulation/entities/ship_design_stats.py | Read ✓ |
| game/simulation/entities/ship_physics.py | Read ✓ |
| game/simulation/entities/ship_serialization.py | Read ✓ |
| game/simulation/entities/stat_contributors/defense.py | Read ✓ |
| game/simulation/entities/stat_contributors/movement.py | Read ✓ |
| game/simulation/entities/stat_contributors/registry.py | Read ✓ |
| game/simulation/interfaces/ability_protocols.py | Read ✓ |
| game/simulation/interfaces/component_protocols.py | Read ✓ |
| game/simulation/interfaces/entity_protocols.py | Read ✓ |
| game/simulation/replay/replay_record.py | Read ✓ |
| game/simulation/replay/replay_spec.py | Read ✓ |
| game/simulation/replay/replay_verifier.py | Read ✓ |
| game/simulation/services/__init__.py | Read ✓ |
| game/simulation/services/vehicle_design_service.py | Read ✓ |
| game/simulation/validation/__init__.py | Read ✓ |
| game/simulation/validation/ship_validator.py | Read ✓ |
| game/strategy/data/fleet_consumable_aggregator.py | Read ✓ |
| game/strategy/data/galaxy_entity_registry.py | Read ✓ |
| game/strategy/data/galaxy_state.py | Read ✓ |
| game/strategy/data/group_policy_registry.py | Read ✓ |
| game/strategy/data/homeworld_presets.py | Read ✓ |
| game/strategy/data/order_serializer.py | Read ✓ |
| game/strategy/data/physics.py | Read ✓ |
| game/strategy/data/planet_atmosphere.py | Read ✓ |
| game/strategy/data/planet_gen.py | Read ✓ |
| game/strategy/data/planet_serde.py | Read ✓ |
| game/strategy/data/planetary_facility.py | Read ✓ |
| game/strategy/data/ship_cargo_manager.py | Read ✓ |
| game/strategy/data/ship_instance.py | Read ✓ |
| game/strategy/data/spectrum.py | Read ✓ |
| game/strategy/data/star_system.py | Read ✓ |
| game/strategy/engine/conflict_resolution_engine.py | Read ✓ |
| game/strategy/engine/game_config.py | Read ✓ |
| game/strategy/engine/game_initializer.py | Read ✓ |
| game/strategy/engine/game_session.py | Read ✓ |
| game/strategy/engine/handlers/__init__.py | Read ✓ |
| game/strategy/engine/handlers/order_queue.py | Read ✓ |
| game/strategy/engine/order_handlers/transfer_branches.py | Read ✓ |
| game/strategy/engine/organics_consumption_engine.py | Read ✓ |
| game/strategy/engine/planet_energy_engine.py | Read ✓ |
| game/strategy/engine/population_engine.py | Read ✓ |
| game/strategy/engine/production_spawner.py | Read ✓ |
| game/strategy/engine/superweapon_handlers/open_warp_point.py | Read ✓ |
| game/strategy/engine/turn_engine.py | Read ✓ |
| game/strategy/facade/slices/_facade_state.py | Read ✓ |
| game/strategy/facade/slices/event_slice.py | Read ✓ |
| game/strategy/facade/slices/planet_slice.py | Read ✓ |
| game/strategy/generation/density/density_map.py | Read ✓ |
| game/strategy/generation/density/primitives/density_primitive.py | Read ✓ |
| game/strategy/generation/density/primitives/noise.py | Read ✓ |
| game/strategy/generation/planet_image_registry.py | Read ✓ |
| game/strategy/generation/star_image_registry.py | Read ✓ |
| game/strategy/generation/storm_generator.py | Read ✓ |
| game/strategy/services/__init__.py | Read ✓ |
| game/strategy/services/ability_sources/fleet.py | Read ✓ |
| game/strategy/services/ability_sources/intrinsic_roll.py | Read ✓ |
| game/strategy/services/ability_sources/star.py | Read ✓ |
| game/strategy/services/ability_sources/storm.py | Read ✓ |
| game/strategy/services/cargo_transfer_service.py | Read ✓ |
| game/strategy/services/combat_modifier_collector.py | Read ✓ |
| game/strategy/services/design_cost_calculator.py | Read ✓ |
| game/strategy/services/fleet_write_service.py | Read ✓ |
| game/strategy/services/planet_economy_projector.py | Read ✓ |
| game/strategy/services/race_resolver.py | Read ✓ |
| game/strategy/services/replay_resolver.py | Read ✓ |
| game/strategy/services/replay_ship_builder.py | Read ✓ |
| game/strategy/services/replay_verification_sidecar.py | Read ✓ |
| game/strategy/services/stabilizer_registry.py | Read ✓ |
| game/strategy/systems/design_library.py | Read ✓ |
| game/strategy/systems/race_randomizer.py | Read ✓ |
| game/ui/colors.py | Read ✓ |
| game/ui/components/filters/tri_state_widget.py | Read ✓ |
| game/ui/components/table/header.py | Read ✓ |
| game/ui/filters/filter_state.py | Read ✓ |
| game/ui/interfaces/__init__.py | Read ✓ |
| game/ui/interfaces/battle_ui.py | Read ✓ |
| game/ui/panels/design_stats_panel.py | Read ✓ |
| game/ui/panels/race_theme_gallery.py | Read ✓ |
| game/ui/panels/strategy_widgets.py | Read ✓ |
| game/ui/panels/system_tree_panel.py | Read ✓ |
| game/ui/screens/atmosphere_target_editor.py | Read ✓ |
| game/ui/screens/battle_results_screen.py | Read ✓ |
| game/ui/screens/battle_setup/__init__.py | Read ✓ |
| game/ui/screens/battle_setup/controller.py | Read ✓ |
| game/ui/screens/battle_setup/panels/center_panel.py | Read ✓ |
| game/ui/screens/battle_setup/screen.py | Read ✓ |
| game/ui/screens/build_queue_helpers.py | Read ✓ |
| game/ui/screens/build_queue_list_window.py | Read ✓ |
| game/ui/screens/build_queue_screen.py | Read ✓ |
| game/ui/screens/build_queue_selector.py | Read ✓ |
| game/ui/screens/builder/detail_panel.py | Read ✓ |
| game/ui/screens/builder/event_bus.py | Read ✓ |
| game/ui/screens/builder/left_panel.py | Read ✓ |
| game/ui/screens/builder/modifier_utils.py | Read ✓ |
| game/ui/screens/builder/weapons_panel.py | Read ✓ |
| game/ui/screens/builder_utils.py | Read ✓ |
| game/ui/screens/data_list_window_mixin.py | Read ✓ |
| game/ui/screens/design_selector_window.py | Read ✓ |
| game/ui/screens/empire_build_queue_filter_manager.py | Read ✓ |
| game/ui/screens/empire_panel_window.py | Read ✓ |
| game/ui/screens/event_log_sidebar.py | Read ✓ |
| game/ui/screens/food_allocation_editor.py | Read ✓ |
| game/ui/screens/galaxy_test/__init__.py | Read ✓ |
| game/ui/screens/galaxy_test/constants.py | Read ✓ |
| game/ui/screens/galaxy_test/system_mode.py | Read ✓ |
| game/ui/screens/gravity_target_editor.py | Read ✓ |
| game/ui/screens/new_game_setup_screen.py | Read ✓ |
| game/ui/screens/new_game_setup_ui_builder.py | Read ✓ |
| game/ui/screens/new_game_setup_view_model.py | Read ✓ |
| game/ui/screens/orders_window.py | Read ✓ |
| game/ui/screens/planet_abilities_controller.py | Read ✓ |
| game/ui/screens/planet_target_editor_base.py | Read ✓ |
| game/ui/screens/race_setup/controller.py | Read ✓ |
| game/ui/screens/race_setup/panel_factory.py | Read ✓ |
| game/ui/screens/race_setup/ship_preview.py | Read ✓ |
| game/ui/screens/radiation_shield_editor.py | Read ✓ |
| game/ui/screens/settings_window.py | Read ✓ |
| game/ui/screens/setup_renderer.py | Read ✓ |
| game/ui/screens/star_list_sidebar.py | Read ✓ |
| game/ui/screens/strategy_detail_formatter.py | Read ✓ |
| game/ui/screens/strategy_fleet_command_router.py | Read ✓ |
| game/ui/screens/strategy_game_state_manager.py | Read ✓ |
| game/ui/screens/strategy_render/dyson_spheres.py | Read ✓ |
| game/ui/screens/strategy_render/fleets.py | Read ✓ |
| game/ui/screens/strategy_render/grid.py | Read ✓ |
| game/ui/screens/strategy_render/storms.py | Read ✓ |
| game/ui/screens/strategy_screen_composition.py | Read ✓ |
| game/ui/screens/strategy_screen_selection.py | Read ✓ |
| game/ui/screens/strategy_windows/event_log_window_ctrl.py | Read ✓ |
| game/ui/screens/strategy_windows/orders_window_ctrl.py | Read ✓ |
| game/ui/screens/strategy_windows/transfer_dialogs.py | Read ✓ |
| game/ui/screens/test_lab/renderer/_draw_helpers.py | Read ✓ |
| game/ui/screens/test_lab/renderer/category_panel.py | Read ✓ |
| game/ui/screens/test_lab/renderer/header_panel.py | Read ✓ |
| game/ui/screens/test_lab/results_panel.py | Read ✓ |
| game/ui/screens/workshop_data_loader.py | Read ✓ |
| game/ui/screens/workshop_event_router.py | Read ✓ |
| game/ui/screens/workshop_screen.py | Read ✓ |
| game/ui/screens/workshop_viewmodel_layer_ops.py | Read ✓ |
| game/ui/screens/workshop_viewmodel_selection.py | Read ✓ |
| game/ui/services/battle_ui_service.py | Read ✓ |
| game/ui/services/image/__init__.py | Read ✓ |
| game/ui/services/image/null_provider.py | Read ✓ |
| game/ui/services/image/provider.py | Read ✓ |
| game/ui/services/modifier_icon_service.py | Read ✓ |
| game/ui/services/ship_factory.py | Read ✓ |
| game/ui/widgets/__init__.py | Read ✓ |
| game/ui/widgets/dropdown_helper.py | Read ✓ |
| game/ui/widgets/range_slider_builder.py | Read ✓ |
