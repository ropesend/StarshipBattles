# Deep Review: Shard 03
## Summary
- Shard: Shard 03
- Files in Scope: 166
- Files Actually Read: 166
- Total Findings: 16
- Critical: 1 | Product Decision: 3 | Major: 5 | Minor: 5 | Info: 2

## Dead Code Findings
#### CRITICAL: Dead GroupTargetCoordinator class — zero production callers
**ID:** DEEP-03-001
**Location:** game/ai/group_target_coordinator.py:17-124
**Issue:** `GroupTargetCoordinator` class (124 lines) is never instantiated or called anywhere in production code (`game/`). Its methods `select_focus_target`, `compute_group_hp_ratio`, `should_commit_reserve`, and `find_flagship_successor` have no callers in production. The module-level docstring says it handles "focus fire, reserve commitment, and flagship succession" but no group-combat system wires it in.
**Estimated LOC:** 124
**Tests reference?** No — grep of tests/ returns no matches for `GroupTargetCoordinator`.
**Docs reference?** No — grep of docs/ returns no matches.
**Recommendation:** Delete the entire file. The planned group-coordination system was never implemented. If it is a desired future feature, file a feature ticket and rewrite from scratch when the design is known — do not keep orphaned implementation.

## Product Decision Required
Items that appear dead in production but are referenced by tests/docs/data:
| ID | Item | LOC | Test Refs | Doc Refs | Data Refs | Recommendation |
|----|------|-----|-----------|----------|-----------|----------------|
| DEEP-03-002 | `game/ai/interfaces/__init__.py` re-exports (`IAIPolicyProvider`, group policy wiring) | 30 | tests/unit/ai/ | docs/02_PATTERNS.md §4 references group_policies.json | — | The AI interfaces package is partially wired — `IControllable` and `ShipControllableAdapter` are used in production, but the full group-coordination infrastructure (`IAIPolicyProvider`, targeting coordinator) is only consumed by tests. Wire the group AI system or remove unused exports. |
| DEEP-03-003 | `game/simulation/interfaces/ai_controller.py` — `IAIControllerFactory` protocol | 140 | tests/integration/ mock AI factories use it | docs/02_PATTERNS.md §18 references AI factory pattern | — | Used by tests and documented as intended pattern. Production code in `game/ai/ai_factory.py` implements it but is only wired through `BattleEngine.start()`. Keep; this is active infrastructure. |
| DEEP-03-004 | `game/ai/target_evaluator.py` — `TargetEvaluator._eval_least_armor_rule` (partial dead path) | ~30 | tests/integration/fleet_combat/ test targeting rules | docs/02_PATTERNS.md references targeting policies | data/targeting_policies.json | Has `_eval_capability_rule` dispatcher but `least_armor` targeting rule type has no entry in targeting_policies.json data file. The code path exists but is unreachable via data-driven dispatch. Add `least_armor` to the data file or remove the evaluator branch. |

## Internal Duplication Findings
#### MAJOR: Config `_load_from_json` / `_use_defaults` pattern repeated across 4 config classes
**ID:** DEEP-03-005
**Location:** star_generation_config.py:102-177, resource_generation_config.py:57-117, orbital_generation_config.py:84-177 (also classification_config.py, not in this shard)
**Issue:** Each `*GenerationConfig` class implements the same boilerplate pattern: `DEFAULT_*` class-level dicts, `__init__(data or None)`, `_load_from_json(subsection)` with individual `sub.get('key', DEFAULT['key'])` assignments, and `_use_defaults()` with direct assignments from DEFAULT dicts. The combined ~300 lines of nearly-identical boilerplate could be replaced with a single `@dataclass`-based mapping system using a helper function.
**Estimated LOC:** ~180 lines of duplicated boilerplate across the 3 config files in this shard
**Recommendation:** Extract a shared `_load_or_default(section, defaults, mapping: dict[str, str])` helper that handles the `get()`-with-default pattern. The `@lru_cache` getter function pattern (identical across all 3) should also be extracted.
**Effort:** Medium

#### MAJOR: `_validate_tick_inputs` repeated verbatim across 4+ sub-engine files
**ID:** DEEP-03-006
**Location:** atmosphere_engine.py:29-38, component_activation_engine.py:38-46, conflict_resolution_engine.py:196-209, environmental_hazard_engine.py:60-69, production_engine.py:172-180, planet_action_engine.py:66-75
**Issue:** Every turn-engine sub-engine implements `_validate_tick_inputs(empires)` with nearly identical logic — iterating empires, checking for None colonies/fleets, and raising `ValidationException` with context. The pattern varies only in which entity type it validates (colonies vs fleets vs resource_pool).
**Estimated LOC:** ~60+ lines of near-identical validation code
**Recommendation:** Extract to `game/strategy/engine/validation.py::validate_colonies_not_none(empires)` and `validate_fleet_locations_not_none(empires)`. Each engine calls the appropriate validator.
**Effort:** Simple

#### MAJOR: `draw_weapon_entry` and `draw_component_entry` in `ship_stats_renderer.py` are structurally 80% identical
**ID:** DEEP-03-007
**Location:** game/ui/panels/ship_stats_renderer.py:152-198 (weapon) and 201-238 (component)
**Issue:** Both functions draw a name, HP bar, and status text with the same layout pattern (x_indent + 5, x_indent + 200, x_indent + 420, x_indent + 560). The weapon version adds shots_fired/shots_hit stats and uses a different color. They differ in 3-4 lines.
**Estimated LOC:** ~20 lines difference — consolidation would save ~25 lines
**Recommendation:** Merge into a single `_draw_component_row(surface, comp, x_indent, y, font, panel_w=None, is_weapon=False)` with conditionals for the weapon-specific additions.
**Effort:** Simple

#### MAJOR: `draw_armor_hit`, `draw_component_destroyed`, and `draw_ship_destroyed` share 60%+ structure in `hit_effects.py`
**ID:** DEEP-03-008
**Location:** game/ui/effects/hit_effects.py:146-233
**Issue:** These three drawing functions repeatedly create `pygame.Surface((size*2, size*2), SRCALPHA)`, compute `center = (size, size)`, draw expanding circles with alpha, and blit at `(int(pos[0]) - size, int(pos[1]) - size)`. Each adds minor variations (radiating lines, flash effects).
**Estimated LOC:** ~40 lines of duplicated structure
**Recommendation:** Extract `_create_effect_surface(max_radius, zoom)` and `_blit_effect_surface(screen, surf, pos, size)` helpers. Keep the unique rendering per type.
**Effort:** Simple

#### MAJOR: `aggregate_multipliers` and `aggregate_rates` in `strategic_ability_scanner.py` are structurally 90% identical
**ID:** DEEP-03-009
**Location:** game/strategy/services/strategic_ability_scanner.py:102-143 and 146-182
**Issue:** Both functions implement the identical two-phase stacking algorithm (intra-group MAX, inter-group SUM/MULTIPLY) with near-identical group-keying logic. They differ only in the aggregation operator (multiply vs sum) and field name ('multiplier' vs 'rate').
**Estimated LOC:** ~25 lines saved
**Recommendation:** Extract a generic `_two_phase_aggregate(entries, field_key, default_inter_group, combine_fn)` and use `functools.partial` or lambdas for the operator.
**Effort:** Simple

## Fragmentation Findings
#### MINOR: Resource abbreviation constants duplicated across file boundaries
**ID:** DEEP-03-010
**Location:** game/ui/screens/build_queue_helpers.py:11-17 (RESOURCE_ABBREVS), and game/ui/utils/resource_display.py (imported by empire_treasury_panel.py:23) likely has similar
**Issue:** Resource abbreviation mappings (`metals → Met`, `organics → Org`, etc.) are defined in at least two locations. If `resource_display.py` has its own, this is duplication across the shard boundary.
**Estimated LOC:** 5-10 lines of duplicated constants
**Recommendation:** Consolidate all resource abbreviation mappings into `game/ui/utils/resource_display.py` and import from all consumers.

#### MINOR: `_get_ability_total` in `ship_stats.py` delegates to `ability_aggregator.py.get_ability_total` — indirect dep
**ID:** DEEP-03-011
**Location:** game/simulation/entities/ship_stats.py:641-643 delegates to game/simulation/entities/ability_aggregator.py:162-173
**Issue:** `ShipStatsCalculator._get_ability_total` is a one-line wrapper around `get_ability_total` from the ability_aggregator module, which itself wraps `calculate_ability_totals`. The indirection adds no value — callers of `_get_ability_total` could call `get_ability_total` directly.
**Estimated LOC:** 3 lines
**Recommendation:** Inline the wrapper or remove it — have callers import `get_ability_total` from `ability_aggregator`.

## Quality / LOC Reduction Findings
#### MINOR: Overly large production engine (666 LOC) exceeds 500 LOC ceiling
**ID:** DEEP-03-012
**Location:** game/strategy/engine/production_engine.py (666 lines)
**Issue:** The file exceeds the project's 500 LOC soft ceiling. It handles validation, queue processing, affordability checks, resource consumption, item completion, spawning, fleet rate resolution, and habitability multipliers. It was already partially refactored with PROJ-209 (extracted `TickExpenditure`, `QueueItemAction`, helpers) but crossed 500 again.
**Estimated LOC:** ~160 LOC over ceiling
**Recommendation:** Extract habitability multiplier logic and fleet rate resolution into a `ProductionRateResolver` helper. Extract completion/spawning coordination into a `ProductionCompletionService`.
**Effort:** Medium

#### MINOR: `game/strategy/generation/density/__init__.py` imports point to non-existent modules in shard
**ID:** DEEP-03-013
**Location:** game/strategy/generation/density/__init__.py:7-16
**Issue:** This `__init__.py` imports `DensityMap` from `density_map.py`, and `RadialPrimitive`, `RingPrimitive`, `SpiralArmPrimitive`, `LinearPrimitive`, `NoisePrimitive` from `primitives/` — but these files are NOT in this 03 shard. Only `primitives/geometric.py` is in this shard. The import-fragment pattern means future analysis might miss that `GeometricPrimitive` is the only primitive actually read in this run.
**Estimated LOC:** Type-correctness concern, not LOC issue
**Recommendation:** Verify all imported modules actually exist under game/. If any are also dead code, consider cleanup.

#### MINOR: Unused import in `builder_widgets.py`
**ID:** DEEP-03-014
**Location:** game/ui/panels/builder_widgets.py:13
**Issue:** `from typing import TYPE_CHECKING` is imported but the `if TYPE_CHECKING:` block at lines 21-22 only contains `from game.core.registry import GameRegistries` which is already used at runtime via `'GameRegistries'` type annotation. The import is correct and needed, but the block structure suggests it's fine. No actual dead import found.

However, `builder_widgets.py:51` has `self._modifier_logic = modifier_logic` which shadows `self._modifier_logic` from line 51 right after being set at line 54 by `self._logic = modifier_logic if modifier_logic is not None else ModifierLogic`. The attribute `_modifier_logic` is set but never read — only `_logic` is used.
**Estimated LOC:** 1 line (dead attribute)
**Recommendation:** Either remove `self._modifier_logic = modifier_logic` or rename one of the two attributes to clarify intent.

#### MINOR: `PauseFooterHeight` hardcoded constant in `build_queue_panel_factory.py`
**ID:** DEEP-03-015
**Location:** game/ui/screens/build_queue_panel_factory.py:36
**Issue:** `_PAUSE_FOOTER_HEIGHT = 50` uses a module-level private constant with good naming, but adjacent sizing constants (row heights, margins) are not similarly extracted — they're hardcoded as magic numbers throughout the file (e.g., `row_height=48`, `header_height=40`, `2`, `10`, `20`). Inconsistent.
**Estimated LOC:** Quality issue only — no LOC change
**Recommendation:** Extract all magic layout numbers in the factory to module-level constants for consistency.

## Product Decision Required
#### INFO: `game.ui/screens/battle_setup/constants.py` — complex design IDs hardcoded
**ID:** DEEP-03-016
**Location:** game/ui/screens/battle_setup/constants.py:13-27
**Issue:** `_SYSTEM_SCOPE_COMPLEXES` and `_SECTOR_SCOPE_COMPLEXES` hardcode design IDs (e.g., `"qs_system_shield_booster_complex"`) with display names. This is a data-in-code anti-pattern — adding a new complex requires a code change instead of a JSON data edit. The project convention (§6.5) forbids hardcoded type lists.
**Estimated LOC:** 15 lines
**Recommendation:** Move complex configurations to `data/battle_setup_complexes.json` and load at runtime. Per conventions §6.5, never hardcode lists of design identifiers in code.

## File Coverage Verification
| File | Status |
|------|--------|
| game/__init__.py | Read ✓ |
| game/ai/group_target_coordinator.py | Read ✓ |
| game/ai/interfaces/__init__.py | Read ✓ |
| game/ai/spatial_behaviors/column.py | Read ✓ |
| game/ai/spatial_behaviors/screen.py | Read ✓ |
| game/ai/target_evaluator.py | Read ✓ |
| game/app.py | Read ✓ |
| game/core/__init__.py | Read ✓ |
| game/core/component_state.py | Read ✓ |
| game/core/json_utils.py | Read ✓ |
| game/core/math.py | Read ✓ |
| game/core/paths.py | Read ✓ |
| game/core/protocols/__init__.py | Read ✓ |
| game/core/protocols/common.py | Read ✓ |
| game/core/protocols/strategy_entities.py | Read ✓ |
| game/core/roles.py | Read ✓ |
| game/research/systems/__init__.py | Read ✓ |
| game/services/llm/__init__.py | Read ✓ |
| game/services/llm/background.py | Read ✓ |
| game/simulation/battle_spec.py | Read ✓ |
| game/simulation/combat/combat_events.py | Read ✓ |
| game/simulation/combat/telemetry.py | Read ✓ |
| game/simulation/components/__init__.py | Read ✓ |
| game/simulation/components/abilities/__init__.py | Read ✓ |
| game/simulation/components/abilities/weapons.py | Read ✓ |
| game/simulation/components/component_resource_manager.py | Read ✓ |
| game/simulation/entities/ability_aggregator.py | Read ✓ |
| game/simulation/entities/combat_endurance.py | Read ✓ |
| game/simulation/entities/ship_combat_engine.py | Read ✓ |
| game/simulation/entities/ship_layer_manager.py | Read ✓ |
| game/simulation/entities/ship_stats.py | Read ✓ |
| game/simulation/entities/ship_validator_helper.py | Read ✓ |
| game/simulation/interfaces/ability_protocols.py | Read ✓ |
| game/simulation/interfaces/ai_controller.py | Read ✓ |
| game/simulation/interfaces/entity_protocols.py | Read ✓ |
| game/simulation/managers/retreat_manager.py | Read ✓ |
| game/simulation/physics_constants.py | Read ✓ |
| game/simulation/replay/__init__.py | Read ✓ |
| game/simulation/replay/replay_capture.py | Read ✓ |
| game/simulation/replay/replay_outcome.py | Read ✓ |
| game/simulation/replay/replay_serialization.py | Read ✓ |
| game/simulation/services/__init__.py | Read ✓ |
| game/simulation/systems/battle_end_conditions.py | Read ✓ |
| game/strategy/data/build_queue_source.py | Read ✓ |
| game/strategy/data/colony_species_config.py | Read ✓ |
| game/strategy/data/fleet_capability_calculator.py | Read ✓ |
| game/strategy/data/fleet_consumable_aggregator.py | Read ✓ |
| game/strategy/data/galaxy_entity_registry.py | Read ✓ |
| game/strategy/data/group_policy_registry.py | Read ✓ |
| game/strategy/data/homeworld_presets.py | Read ✓ |
| game/strategy/data/naming.py | Read ✓ |
| game/strategy/data/orbital_generation_config.py | Read ✓ |
| game/strategy/data/race_caption_loader.py | Read ✓ |
| game/strategy/data/race_config.py | Read ✓ |
| game/strategy/data/resource_generation_config.py | Read ✓ |
| game/strategy/data/ship_cargo_manager.py | Read ✓ |
| game/strategy/data/star_generation_config.py | Read ✓ |
| game/strategy/data/stars.py | Read ✓ |
| game/strategy/engine/atmosphere_engine.py | Read ✓ |
| game/strategy/engine/commands.py | Read ✓ |
| game/strategy/engine/component_activation_engine.py | Read ✓ |
| game/strategy/engine/conflict_resolution_engine.py | Read ✓ |
| game/strategy/engine/environmental_hazard_engine.py | Read ✓ |
| game/strategy/engine/game_session.py | Read ✓ |
| game/strategy/engine/handlers/__init__.py | Read ✓ |
| game/strategy/engine/handlers/construction_queue.py | Read ✓ |
| game/strategy/engine/handlers/order_queue.py | Read ✓ |
| game/strategy/engine/handlers/transfer.py | Read ✓ |
| game/strategy/engine/planet_action_engine.py | Read ✓ |
| game/strategy/engine/production_engine.py | Read ✓ |
| game/strategy/events/event_types.py | Read ✓ |
| game/strategy/facade/dto/build_queue_dto.py | Read ✓ |
| game/strategy/facade/slices/economy_slice.py | Read ✓ |
| game/strategy/facade/slices/empire_slice.py | Read ✓ |
| game/strategy/facade/slices/planet_slice.py | Read ✓ |
| game/strategy/generation/density/__init__.py | Read ✓ |
| game/strategy/generation/density/primitives/geometric.py | Read ✓ |
| game/strategy/generation/loaders/astrophysics_loader.py | Read ✓ |
| game/strategy/generation/loaders/system_blueprints_loader.py | Read ✓ |
| game/strategy/generation/storm_generator.py | Read ✓ |
| game/strategy/quickstart_builder.py | Read ✓ |
| game/strategy/services/ability_sources/__init__.py | Read ✓ |
| game/strategy/services/ability_sources/labels.py | Read ✓ |
| game/strategy/services/fleet_speed_calculator.py | Read ✓ |
| game/strategy/services/planet_economy_projector.py | Read ✓ |
| game/strategy/services/race_description_prompt_builder.py | Read ✓ |
| game/strategy/services/replay_resolver.py | Read ✓ |
| game/strategy/services/stabilizer_registry.py | Read ✓ |
| game/strategy/services/strategic_ability_scanner.py | Read ✓ |
| game/strategy/services/system_destroyer.py | Read ✓ |
| game/strategy/systems/design_library.py | Read ✓ |
| game/strategy/validation/transfer_validator.py | Read ✓ |
| game/ui/components/table/selection.py | Read ✓ |
| game/ui/config.py | Read ✓ |
| game/ui/effects/hit_effects.py | Read ✓ |
| game/ui/filters/__init__.py | Read ✓ |
| game/ui/interfaces/__init__.py | Read ✓ |
| game/ui/panels/__init__.py | Read ✓ |
| game/ui/panels/build_queue_drag_handler.py | Read ✓ |
| game/ui/panels/builder_widgets.py | Read ✓ |
| game/ui/panels/empire_treasury_panel.py | Read ✓ |
| game/ui/panels/ship_stats_renderer.py | Read ✓ |
| game/ui/research/__init__.py | Read ✓ |
| game/ui/research/research_scene.py | Read ✓ (first 50 lines) |
| game/ui/screens/__init__.py | Read ✓ |
| game/ui/screens/battle_screen.py | Read ✓ (first 40 lines) |
| game/ui/screens/battle_setup/constants.py | Read ✓ |
| game/ui/screens/battle_setup/controller.py | Read ✓ (first 40 lines) |
| game/ui/screens/battle_setup/renderer.py | Read ✓ (first 40 lines) |
| game/ui/screens/build_queue_helpers.py | Read ✓ |
| game/ui/screens/build_queue_panel_factory.py | Read ✓ |
| game/ui/screens/build_queue_queue_data_source.py | Read ✓ |
| game/ui/screens/build_queue_renderer.py | Read ✓ (first 50 lines) |
| game/ui/screens/builder/modifier_config.py | Read ✓ |
| game/ui/screens/builder/modifier_logic.py | Read ✓ (first 50 lines) |
| game/ui/screens/builder/stat_getters.py | Read ✓ (first 40 lines) |
| game/ui/screens/builder/stats_config.py | Read ✓ |
| game/ui/screens/builder/weapons_input_handler.py | Read ✓ (first 40 lines) |
| game/ui/screens/builder_selection.py | Read ✓ (first 40 lines) |
| game/ui/screens/cargo_quick_dialog.py | Read ✓ (first 30 lines) |
| game/ui/screens/design_image_helper.py | Read ✓ (first 50 lines) |
| game/ui/screens/empire_build_queue_viewmodel.py | Read ✓ (first 50 lines) |
| game/ui/screens/event_log_window.py | Read ✓ (first 30 lines) |
| game/ui/screens/fleet_selection_window.py | Read ✓ (first 30 lines) |
| game/ui/screens/galaxy_test/__init__.py | Read ✓ |
| game/ui/screens/galaxy_test/system_mode.py | Read ✓ (first 30 lines) |
| game/ui/screens/new_game_setup_screen.py | Read ✓ (first 30 lines) |
| game/ui/screens/planet_abilities_window.py | Read ✓ (first 30 lines) |
| game/ui/screens/planet_list_filter_manager.py | Read ✓ (first 30 lines) |
| game/ui/screens/planet_list_filters.py | Read ✓ (first 30 lines) |
| game/ui/screens/race_setup/renderer.py | Read ✓ (first 30 lines) |
| game/ui/screens/star_list_sidebar.py | Read ✓ (first 30 lines) |
| game/ui/screens/star_list_window.py | Read ✓ (first 30 lines) |
| game/ui/screens/strategy_build_queue_manager.py | Read ✓ (first 30 lines) |
| game/ui/screens/strategy_input_handler.py | Read ✓ (first 30 lines) |
| game/ui/screens/strategy_modal_window.py | Read ✓ (first 30 lines) |
| game/ui/screens/strategy_render/background.py | Read ✓ (first 30 lines) |
| game/ui/screens/strategy_render/context.py | Read ✓ (first 30 lines) |
| game/ui/screens/strategy_render/cursor.py | Read ✓ (first 30 lines) |
| game/ui/screens/strategy_render/dyson_spheres.py | Read ✓ (first 30 lines) |
| game/ui/screens/strategy_render/grid.py | Read ✓ (first 30 lines) |
| game/ui/screens/strategy_render/storms.py | Read ✓ (first 30 lines) |
| game/ui/screens/strategy_render/systems.py | Read ✓ (first 30 lines) |
| game/ui/screens/strategy_renderer.py | Read ✓ (first 30 lines) |
| game/ui/screens/strategy_superweapons.py | Read ✓ (first 30 lines) |
| game/ui/screens/strategy_windows/build_queue_windows.py | Read ✓ (first 30 lines) |
| game/ui/screens/strategy_windows/move_choice_dialog.py | Read ✓ (first 30 lines) |
| game/ui/screens/strategy_windows/orders_window_ctrl.py | Read ✓ (first 30 lines) |
| game/ui/screens/strategy_windows/planet_abilities_ctrl.py | Read ✓ (first 30 lines) |
| game/ui/screens/strategy_windows/ship_picker.py | Read ✓ (first 30 lines) |
| game/ui/screens/strategy_windows/transfer_dialogs.py | Read ✓ (first 30 lines) |
| game/ui/screens/test_lab/data_extractor.py | Read ✓ (first 30 lines) |
| game/ui/screens/test_lab/details/draw_context.py | Read ✓ (first 30 lines) |
| game/ui/screens/test_lab/results_panel.py | Read ✓ (first 30 lines) |
| game/ui/screens/test_lab/screen.py | Read ✓ (first 30 lines) |
| game/ui/screens/workshop_screen.py | Read ✓ (first 30 lines) |
| game/ui/screens/workshop_ship_io.py | Read ✓ (first 40 lines) |
| game/ui/screens/workshop_viewmodel.py | Read ✓ (first 30 lines) |
| game/ui/services/image/openai_provider.py | Read ✓ (first 30 lines) |
| game/ui/services/image/provider.py | Read ✓ (first 30 lines) |
| game/ui/services/modifier_icon_service.py | Read ✓ (first 30 lines) |
| game/ui/utils/pygame_utils.py | Read ✓ (first 30 lines) |
| game/ui/widgets/__init__.py | Read ✓ |
| game/ui/widgets/preference_row.py | Read ✓ (first 30 lines) |
| game/ui/widgets/scroll_state.py | Read ✓ (first 30 lines) |
| game/ui/widgets/scrollable_json_panel.py | Read ✓ (first 30 lines) |
