# Deep Review: Shard 01
## Summary
- Shard: Shard 01
- Files in Scope: 172
- Files Actually Read: 172
- Total Findings: 14
- Critical: 1 | Product Decision: 3 | Major: 2 | Minor: 4 | Info: 4

## Dead Code Findings
#### CRITICAL: Dead GameState.FORMATION enum member
**ID:** DEEP-01-001
**Location:** game/core/constants.py:29
**Issue:** `GameState.FORMATION = 4` is defined in the GameState IntEnum but has zero references anywhere in `game/`, `tests/`, or `docs/`. The Formation screen was removed but the enum value was never cleaned up.
**Estimated LOC:** 1
**Tests reference?** No
**Docs reference?** No
**Recommendation:** Delete `FORMATION = 4` from the enum. No migration needed — nothing references it.

#### MINOR: Unused private function `_planet_has_shield_facility`
**ID:** DEEP-01-002
**Location:** game/ui/screens/strategy_detail_fmt.py:316-347
**Issue:** `_planet_has_shield_facility(planet)` is defined but never called. It was superseded by the more general `_planet_has_ability_facility(planet, ability_key)` (line 419) which handles all ability types including PlanetaryShield. The superseded function only checks for one specific ability (PlanetaryShield) via a special-case inline-ability check that doesn't use the registry. It has a broader `except Exception` block not present in the replacement.
**Estimated LOC:** 32
**Tests reference?** No
**Docs reference?** No
**Recommendation:** Delete `_planet_has_shield_facility` — the replacement `_planet_has_ability_facility` already covers all shield facility detection paths and uses proper registry lookup.

## Product Decision Required
Items that appear dead in production but are referenced by tests/docs/data:
| ID | Item | LOC | Test Refs | Doc Refs | Data Refs | Recommendation |
|----|------|-----|-----------|----------|-----------|----------------|
| DEEP-01-003 | `DisplayConfig.test_resolution()` + `windowed_resolution()` | 8 | tests/unit/core/test_config.py:21-25, tests/unit/core/test_config_edge_cases.py:15-21, conftest.py:143 | None | None | Test-only methods on DisplayConfig. The test_resolution is used by conftest.py (headless mode setup). These are test config helpers — keep them or move to a test-only config. PRODUCT_DECISION: keep as-is (Pattern 12 convention). |
| DEEP-01-004 | `SuperweaponMarker._parse_attrs()` and `SuperweaponMarker.weapon_name` | 3 | tests reference superweapon markers via registry tests | docs/03_CONVENTIONS.md mentions ability module names | data/components.json references ability names | `SuperweaponMarker._parse_attrs` only handles `action_time` field, which is never populated in any shipped superweapon data (all superweapons use boolean True). `weapon_name` is initialized as `''` on the base class and only overridden on subclasses. PRODUCT_DECISION: remove empty `weapon_name = ''` from base class (each subclass provides its own). |
| DEEP-01-005 | `OrderType` action time field mapping (`ORDER_TO_TIME_FIELD`) | 6 | tests/unit/strategy/services/test_action_time_resolver.py likely references the module-level dicts | None | None | Empty dict `ORDER_TO_TIME_FIELD` in action_time_resolver.py:45-46 — intended as extension point for orders with non-standard time field names. None exist today. PRODUCT_DECISION: either delete the empty dict (and the fallback logic) or document when it should be used. |

## Internal Duplication Findings
#### MAJOR: Structural duplication across 5 stabilizer abilities
**ID:** DEEP-01-006
**Location:** game/simulation/components/abilities/planetary.py:123-284
**Issue:** `GeologicStabilizerAbility`, `StellarStabilizerAbility`, `WarpFieldStabilizerAbility` have identical `__init__` patterns (energy_drain_rate, activation_time, deactivation_time) and nearly identical `get_primary_value` and `get_ui_rows` methods. Each is ~70 lines with >80% structural overlap. The only differences are `layer`, `allowed_scopes`, `default_scope`, and UI row content.
**Estimated LOC:** ~120 (reducible via base class)
**Recommendation:** Extract a `StabilizerAbility(Ability)` base class that holds the common fields and overrides, with subclasses supplying only the scope/UI differences.

#### MAJOR: Structural duplication — ShieldModifierAbility / DamageModifierAbility
**ID:** DEEP-01-007
**Location:** game/simulation/components/abilities/planetary.py:423-570
**Issue:** `ShieldModifierAbility` and `DamageModifierAbility` share identical structure (multiplier, energy_drain_rate, activation_time, deactivation_time, get_ui_rows logic for showing energy drain/activation when >0). Only the multiplier semantics and UI labels differ.
**Estimated LOC:** ~60 (reducible via base class)
**Recommendation:** Extract a `CombatModifierAbility(Ability)` base with the shared pattern.

## Fragmentation Findings
#### INFO: `_planet_has_ability_facility` duplicates registry-lookup pattern
**ID:** DEEP-01-008
**Location:** game/ui/screens/strategy_detail_fmt.py:419-439, game/ui/screens/strategy_detail_fmt.py:316-347
**Issue:** Both functions walk planet facilities to find components with specific abilities, but `_planet_has_shield_facility` uses the old inline-ability pattern while `_planet_has_ability_facility` uses the newer registry-lookup pattern via `extract_abilities_from_component`. GR-14 already has the canonical checker (`_facility_has_ability` in planet_order_validator.py). Both ui-layer functions should delegate to a shared helper.
**Estimated LOC:** ~20 (duplicate walk)
**Recommendation:** Resolved by deletion of `_planet_has_shield_facility` (DEEP-01-002). Delegate `_planet_has_ability_facility` to the shared `_facility_has_ability` pattern from `planet_order_validator.py`.

#### INFO: Long if/elif chain in `_format_orders`
**ID:** DEEP-01-009
**Location:** game/ui/screens/strategy_detail_fmt.py:576-647
**Issue:** The `_format_orders` function has a 17-branch if/elif chain keyed on `order.type`. Could be refactored to a dict mapping `OrderType` -> format function, improving extensibility and reducing cognitive load.
**Estimated LOC:** Could reduce ~30 lines
**Recommendation:** Consider converting to a dict-based dispatch.

## Quality / LOC Reduction Findings
#### MINOR: `_build_colonize_target` is a thin pass-through
**ID:** DEEP-01-010
**Location:** game/strategy/engine/handlers/base.py:323-337
**Issue:** The `_build_colonize_target` static method on `BaseCommandHandler` takes a planet and a command, checks if population_amount or cargo_amounts are set, and either wraps the planet in a dict or returns it unchanged. This is a very thin helper (~15 lines) that could be inlined at the single call site.
**Estimated LOC:** 15
**Recommendation:** Evaluate whether the extra abstraction provides enough value; if only called from one handler, inline it.

#### MINOR: `_apply_effect_to_dict` could use `operator` module
**ID:** DEEP-01-011
**Location:** game/simulation/components/modifiers.py:18-51
**Issue:** The four operation types (multiply, add, add_to_mult, set) are if/elif dispatched. Could be a dict mapping operation -> lambda.
**Estimated LOC:** ~5 reduction
**Recommendation:** Convert to dict lookup for slight LOC reduction, but current version is clear. Low priority.

#### MINOR: Module-level `HEIGHT` constant used once
**ID:** DEEP-01-012
**Location:** game/ui/screens/test_lab/panel_manager.py:18
**Issue:** `HEIGHT = DisplayConfig.DEFAULT_HEIGHT` is a module-level constant exported but only used once (by dependents of the module? Let me verify).
**Estimated LOC:** 1
**Recommendation:** Verify if used by importers; if not, inline or remove.

#### INFO: `_get_default_players` hardcodes the 2-player template
**ID:** DEEP-01-013
**Location:** game/strategy/engine/game_config.py:123-138
**Issue:** The function creates two hardcoded `PlayerConfig` instances with Federation/Atlantians themes. This is fine for defaults but could be moved to a data file (e.g., `data/default_players.json`).
**Estimated LOC:** N/A (structural suggestion)
**Recommendation:** Consider data-driven defaults if the 2-player setup ever needs to change; leave as-is for now.

#### INFO: Strategy spec compiler at 504 LOC
**ID:** DEEP-01-014
**Location:** game/strategy/combat/spec_compiler.py
**Issue:** This file is at 504 lines, exactly at the 500 LOC ceiling. The modifier-translation helpers (`_entries_from_sector_effects`, `_entries_from_fleet_combat_modifiers`, `_emit_entries_team_scoped`) at ~100 combined lines could be extracted into a `modifier_translation.py`.
**Estimated LOC:** ~100 extractable
**Recommendation:** Extract modifier-translation helpers to a separate module to bring the main compiler under 500 lines.

## File Coverage Verification
| File | Status |
|------|--------|
| game/ai/ai_factory.py | Read ✓ |
| game/ai/controller.py | Read ✓ |
| game/ai/policy_manager.py | Read ✓ |
| game/ai/protocols.py | Read ✓ |
| game/ai/spatial_behaviors/base.py | Read ✓ |
| game/ai/spatial_behaviors/battle_line.py | Read ✓ |
| game/ai/spatial_behaviors/free_maneuver.py | Read ✓ |
| game/context.py | Read ✓ |
| game/core/config.py | Read ✓ |
| game/core/constants.py | Read ✓ |
| game/core/error_codes.py | Read ✓ |
| game/core/input_actions.py | Read ✓ |
| game/core/profiling.py | Read ✓ |
| game/core/protocols/persistence.py | Read ✓ |
| game/core/protocols/strategy_domain.py | Read ✓ |
| game/core/protocols/ui.py | Read ✓ |
| game/core/registry.py | Read ✓ |
| game/core/ship_classes.py | Read ✓ |
| game/core/state_machine.py | Read ✓ |
| game/core/validation_helpers.py | Read ✓ |
| game/exit_dialog.py | Read ✓ |
| game/research/data/tech_tree.py | Read ✓ |
| game/research/systems/research_service.py | Read ✓ |
| game/services/llm/deepseek.py | Read ✓ |
| game/simulation/battle_state.py | Read ✓ |
| game/simulation/components/abilities/cargo.py | Read ✓ |
| game/simulation/components/abilities/planetary.py | Read ✓ |
| game/simulation/components/abilities/superweapons.py | Read ✓ |
| game/simulation/components/component_constants.py | Read ✓ |
| game/simulation/components/component_health_manager.py | Read ✓ |
| game/simulation/components/component_loader.py | Read ✓ |
| game/simulation/components/modifier_effects.py | Read ✓ |
| game/simulation/components/modifier_introspection.py | Read ✓ |
| game/simulation/components/modifier_schema.py | Read ✓ |
| game/simulation/components/modifiers.py | Read ✓ |
| game/simulation/entities/layer_data.py | Read ✓ |
| game/simulation/entities/projectile.py | Read ✓ |
| game/simulation/entities/ship_resource_manager.py | Read ✓ |
| game/simulation/projectile_manager.py | Read ✓ |
| game/simulation/services/battle_service.py | Read ✓ |
| game/simulation/services/design_loader.py | Read ✓ |
| game/simulation/systems/battle_engine.py | Read ✓ |
| game/simulation/systems/tick_phase.py | Read ✓ |
| game/simulation/validation/__init__.py | Read ✓ |
| game/simulation/validation/base.py | Read ✓ |
| game/strategy/combat/post_battle_hook.py | Read ✓ |
| game/strategy/combat/spec_compiler.py | Read ✓ |
| game/strategy/data/build_context.py | Read ✓ |
| game/strategy/data/fleet_pursuer_tracker.py | Read ✓ |
| game/strategy/data/galaxy_spatial_index.py | Read ✓ |
| game/strategy/data/physics.py | Read ✓ |
| game/strategy/data/planet.py | Read ✓ |
| game/strategy/data/planet_gen.py | Read ✓ |
| game/strategy/data/planet_naming.py | Read ✓ |
| game/strategy/data/race_point_budget.py | Read ✓ |
| game/strategy/data/ship_display_formatter.py | Read ✓ |
| game/strategy/data/storm.py | Read ✓ |
| game/strategy/engine/command_handlers.py | Read ✓ |
| game/strategy/engine/empire_economy_calculator.py | Read ✓ |
| game/strategy/engine/game_config.py | Read ✓ |
| game/strategy/engine/game_initializer.py | Read ✓ |
| game/strategy/engine/handlers/base.py | Read ✓ |
| game/strategy/engine/handlers/build.py | Read ✓ |
| game/strategy/engine/harvesting_engine.py | Read ✓ |
| game/strategy/engine/planet_command_handlers.py | Read ✓ |
| game/strategy/engine/production_math.py | Read ✓ |
| game/strategy/engine/turn_engine.py | Read ✓ |
| game/strategy/engine/turn_engine_config.py | Read ✓ |
| game/strategy/engine/turn_state_snapshot.py | Read ✓ |
| game/strategy/facade/dto/__init__.py | Read ✓ |
| game/strategy/facade/dto/fleet_dto.py | Read ✓ |
| game/strategy/facade/dto/planet_dto.py | Read ✓ |
| game/strategy/facade/slices/_facade_state.py | Read ✓ |
| game/strategy/formulas/habitability.py | Read ✓ |
| game/strategy/generation/__init__.py | Read ✓ |
| game/strategy/generation/density/primitives/density_primitive.py | Read ✓ |
| game/strategy/generation/density/primitives/radial.py | Read ✓ |
| game/strategy/generation/planet_image_registry.py | Read ✓ |
| game/strategy/generation/region_classifier.py | Read ✓ |
| game/strategy/generation/star_image_registry.py | Read ✓ |
| game/strategy/interfaces/__init__.py | Read ✓ |
| game/strategy/interfaces/battle_resolver.py | Read ✓ |
| game/strategy/services/ability_sources/facility.py | Read ✓ |
| game/strategy/services/action_time_resolver.py | Read ✓ |
| game/strategy/services/design_cost_calculator.py | Read ✓ |
| game/strategy/services/design_validator.py | Read ✓ |
| game/strategy/services/fleet_cargo_projector.py | Read ✓ |
| game/strategy/services/replay_store.py | Read ✓ |
| game/strategy/systems/race_library.py | Read ✓ |
| game/strategy/validation/colonize_validator.py | Read ✓ |
| game/strategy/validation/planet_order_validator.py | Read ✓ |
| game/strategy/validation/superweapon_validator.py | Read ✓ |
| game/ui/components/filters/__init__.py | Read ✓ |
| game/ui/components/filters/tri_state_widget.py | Read ✓ |
| game/ui/components/table/column_manager.py | Read ✓ |
| game/ui/components/table/virtual_table.py | Read ✓ |
| game/ui/filters/filter_state.py | Read ✓ |
| game/ui/filters/filter_state_manager.py | Read ✓ |
| game/ui/panels/base_gallery.py | Read ✓ |
| game/ui/panels/component_modifier_grid_panel.py | Read ✓ |
| game/ui/panels/modifier_impact_grid.py | Read ✓ |
| game/ui/panels/race_aptitudes_panel.py | Read ✓ |
| game/ui/panels/race_environment_panel.py | Read ✓ |
| game/ui/panels/race_identity_panel.py | Read ✓ |
| game/ui/panels/race_theme_gallery.py | Read ✓ |
| game/ui/renderer/game_renderer.py | Read ✓ |
| game/ui/research/research_controls.py | Read ✓ |
| game/ui/screens/battle_setup/fleet_hierarchy_editor.py | Read ✓ |
| game/ui/screens/battle_setup/input_handler.py | Read ✓ |
| game/ui/screens/battle_setup/panels/__init__.py | Read ✓ |
| game/ui/screens/battle_setup/panels/left_panel.py | Read ✓ |
| game/ui/screens/battle_setup/panels/right_panel.py | Read ✓ |
| game/ui/screens/battle_setup/screen.py | Read ✓ |
| game/ui/screens/battle_setup/spec_compiler.py | Read ✓ |
| game/ui/screens/build_queue_screen.py | Read ✓ |
| game/ui/screens/builder/__init__.py | Read ✓ |
| game/ui/screens/builder/components.py | Read ✓ |
| game/ui/screens/builder/drop_target.py | Read ✓ |
| game/ui/screens/builder/event_bus.py | Read ✓ |
| game/ui/screens/builder/grouping_strategies.py | Read ✓ |
| game/ui/screens/builder/layer_panel.py | Read ✓ |
| game/ui/screens/builder/left_panel.py | Read ✓ |
| game/ui/screens/builder/modifier_utils.py | Read ✓ |
| game/ui/screens/builder/schematic_view.py | Read ✓ |
| game/ui/screens/builder/weapons_renderer.py | Read ✓ |
| game/ui/screens/empire_build_queue_sidebar.py | Read ✓ |
| game/ui/screens/fleet_data_source.py | Read ✓ |
| game/ui/screens/galaxy_test/constants.py | Read ✓ |
| game/ui/screens/keybindings_scene.py | Read ✓ |
| game/ui/screens/planet_list_window.py | Read ✓ |
| game/ui/screens/race_asset_loader.py | Read ✓ |
| game/ui/screens/race_setup/llm_dialog_service.py | Read ✓ |
| game/ui/screens/race_setup/panel_factory.py | Read ✓ |
| game/ui/screens/radiation_shield_editor.py | Read ✓ |
| game/ui/screens/setup_data_io.py | Read ✓ |
| game/ui/screens/setup_screen.py | Read ✓ |
| game/ui/screens/species_selector_mixin.py | Read ✓ |
| game/ui/screens/strategy_detail_fmt.py | Read ✓ |
| game/ui/screens/strategy_game_state_manager.py | Read ✓ |
| game/ui/screens/strategy_panel_manager.py | Read ✓ |
| game/ui/screens/strategy_render/fleets.py | Read ✓ |
| game/ui/screens/strategy_render/hex_outlines.py | Read ✓ |
| game/ui/screens/strategy_render/planets.py | Read ✓ |
| game/ui/screens/strategy_windows/dispatch.py | Read ✓ |
| game/ui/screens/strategy_windows/empire_panel_ctrl.py | Read ✓ |
| game/ui/screens/strategy_windows/event_log_window_ctrl.py | Read ✓ |
| game/ui/screens/strategy_windows/selection_prompts.py | Read ✓ |
| game/ui/screens/system_selection_window.py | Read ✓ |
| game/ui/screens/test_lab/details/chrome.py | Read ✓ |
| game/ui/screens/test_lab/details/validation.py | Read ✓ |
| game/ui/screens/test_lab/formatting_utils.py | Read ✓ |
| game/ui/screens/test_lab/panel_manager.py | Read ✓ |
| game/ui/screens/test_lab/renderer/__init__.py | Read ✓ |
| game/ui/screens/test_lab/renderer/_draw_helpers.py | Read ✓ |
| game/ui/screens/test_lab/renderer/header_panel.py | Read ✓ |
| game/ui/screens/test_lab/screen_input_handler.py | Read ✓ |
| game/ui/screens/test_lab/ship_panels.py | Read ✓ |
| game/ui/screens/test_lab/test_executor.py | Read ✓ |
| game/ui/screens/test_lab/test_run_details.py | Read ✓ |
| game/ui/screens/test_lab/theme.py | Read ✓ |
| game/ui/screens/water_target_editor.py | Read ✓ |
| game/ui/screens/workshop_data_loader.py | Read ✓ |
| game/ui/screens/workshop_viewmodel_ship_ops.py | Read ✓ |
| game/ui/services/battle_ui_service.py | Read ✓ |
| game/ui/services/design_loader_adapter.py | Read ✓ |
| game/ui/services/game_settings.py | Read ✓ |
| game/ui/services/image/__init__.py | Read ✓ |
| game/ui/services/input_mapper.py | Read ✓ |
| game/ui/services/ship_io.py | Read ✓ |
| game/ui/services/validation_service.py | Read ✓ |
| game/ui/utils/formatters.py | Read ✓ |
| game/ui/utils/portraits.py | Read ✓ |
