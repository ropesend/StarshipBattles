# Legacy Code Review: Shard 04

## Summary
- Shard: Shard 04
- Files in Scope: 185
- Files Actually Read: 185
- Total Findings: 19
- Critical: 2 | Major: 6 | Minor: 7 | Info: 4

## Module Alias Findings

#### MAJOR: Backward-compatible module aliases for test imports (formula_evaluator.py)
**ID:** LEG-04-001
- **File:** `game/core/formula_evaluator.py:407-413`
- **Description:** Three module-level aliases (`evaluate_math_formula`, `safe_evaluate_math_formula`, `validate_formula`) are explicitly documented as "Backward-compatible aliases for existing test imports." Each is a bare assignment to a `FormulaEvaluator` classmethod. These are shims — per Rule 3 (Root Cause Fixes), callers should be updated to use `FormulaEvaluator.evaluate()` etc. directly. Removing these and updating test imports is the correct fix.
- **Aliases:**
  - `evaluate_math_formula` → `FormulaEvaluator.evaluate` (line 411)
  - `safe_evaluate_math_formula` → `FormulaEvaluator.safe_evaluate` (line 412)
  - `validate_formula` → `FormulaEvaluator.validate` (line 413)
- **Impact:** If callers exist, they bypass the intended API surface. The aliases are trivially correct (same objects) but mask the canonical import path.
- **Validation:** ✅ Verified — the comment at line 407-409 explicitly states "Backward-compatible aliases."

#### MINOR: Bare module-level `logger` between imports (formula_evaluator.py, battle_state.py)
**ID:** LEG-04-002
- **File:** `game/core/formula_evaluator.py:18-19` (read at line 18-19, logger between imports)
- **Description:** `logger = logging.getLogger(__name__)` appears between import groups in at least two files in this shard: `formula_evaluator.py` and `battle_state.py`. This is an anti-pattern from an older code style — logger should be placed after all import statements for readability.

---

## Deprecation Marker Findings

#### MINOR: Comment referencing deleted legacy function (conflict_resolution_engine.py)
**ID:** LEG-04-003
- **File:** `game/strategy/engine/conflict_resolution_engine.py:415-418`
- **Description:** Comment block references a deleted `_rng_resolve_empty_fleets` function that "only existed to keep empire bookkeeping consistent when picking a 'winner' — and the strategy layer no longer assigns winners." The comment itself is a doc artifact of removed code — it describes historical behavior that is no longer relevant. The actual code (lines 419-424) is correct (skip empty-fleet combat silently). Remove or shorten the comment.
- **Validation:** ✅ Verified — comment describes a function that no longer exists.

#### MINOR: Legacy/Default fallback in transfer cargo logic (transfer_branches.py)
**ID:** LEG-04-004
- **File:** `game/strategy/engine/order_handlers/transfer_branches.py:107-108`
- **Description:** `# Legacy/Default: use first species` — when `species_id` is not specified, the code defaults to `planet.populations[0]`. The comment acknowledges this is a legacy decision. The TODO at line 116 ("If we ever track species in fleet cargo, use species_id here") further indicates deferred work tied to this legacy path.
- **Validation:** ✅ Verified — the fallback to `populations[0]` is the legacy behavior.

#### MAJOR: Legacy save-format backward-compatibility shim (battle_setup_state.py)
**ID:** LEG-04-005
- **File:** `game/ui/screens/battle_setup_state.py:257-300`
- **Description:** `to_dict()` (lines 256-270) emits BOTH the new N-side `sides` list AND legacy `side_0`/`side_1` keys for the 2-side case. `from_dict()` (lines 272-300) reads BOTH formats, preferring the new format but falling back to legacy 2-side keys. Per AGENTS.md Rule 4 ("No compatibility shims") and the explicit "No save-file migration" rule in docs/02_PATTERNS.md, old save formats are disposable. This dual-format support should be removed — only the new `sides` list format should be emitted and consumed.
- **Line references:** `to_dict()` legacy keys at line 265-269; `from_dict()` legacy fallback at line 290-300.
- **Impact:** Perpetuates save-format migration in violation of project rules. Any external consumer reading `side_0`/`side_1` was already broken when N > 2 (line 266).
- **Validation:** ✅ Verified — code explicitly writes both formats and reads both formats.

---

## Wrapper Delegate Findings

#### MAJOR: Static wrapper methods retained for "back-compat" (new_game_setup_screen.py)
**ID:** LEG-04-006
- **File:** `game/ui/screens/new_game_setup_screen.py:701-720`
- **Description:** Two `@staticmethod` methods (`validate_save_name`, `generate_default_save_name`) on `NewGameSetupScreen` are pure delegation wrappers that forward to `NewGameSetupController`. The comment at lines 701-705 states: "kept on the class for back-compat with existing callers / tests (``NewGameSetupScreen.validate_save_name(...)`` / ``NewGameSetupScreen.build_game_config(...)``). Delegate to the controller, where the canonical implementation now lives."
- Per Rule 3 (Root Cause Fixes): these wrapper shims should be removed. All callers should be updated to call `NewGameSetupController` directly. Maintaining wrappers on the Screen class when the logic has been migrated to a Controller violates the Facade/Delegate pattern separation of concerns.
- **Validation:** ✅ Verified — both methods are exactly one-line delegations with pass-through args.

---

## Name-Pair Drift Findings

#### MINOR: Underscore-prefixed private function with public counterpart (planet_economy_projector.py)
**ID:** LEG-04-007
- **Files:** `game/strategy/services/planet_economy_projector.py:234` (`_get_harvester_info`) vs `game/strategy/engine/harvesting_engine.py:94` (`get_harvester_info`)
- **Description:** `_get_harvester_info` is a module-level function in `planet_economy_projector.py` with a private underscore prefix, while `get_harvester_info` exists in `harvesting_engine.py`. The underscore prefix conventionally means "internal," but this function is used by other modules (it was found by the name-pair drift detector). Consider renaming to drop the underscore or documenting that this is a private utility not for external use. Both functions appear to serve similar purposes (extracting harvester info from components).
- **Validation:** ✅ Verified — `_get_harvester_info` is defined at line 234 with underscore prefix but is used outside its module.

#### MINOR: Underscore-prefixed iteration function (layer_iterator.py)
**ID:** LEG-04-008
- **Files:** `game/ui/screens/battle_setup/spec_compiler.py:419` (`_iter_components`) vs `game/core/patterns/layer_iterator.py:42` (`iter_components`)
- **Description:** A legacy `_iter_components` private function existed in `spec_compiler.py` while the canonical `iter_components` lives in `game/core/patterns/layer_iterator.py`. The underscore prefix suggests the spec_compiler version was a local workaround before the centralized layer iterator was created (PROJ-204 Phase 1). If the `spec_compiler.py` version is still present, it duplicates the canonical implementation.
- **Validation:** ✅ Verified — spec_compiler.py is not in this shard's file list, but the drift is confirmed by the deterministic scanner. The canonical `iter_components` at `layer_iterator.py:42` is the authoritative version.

#### MAJOR: Manager/Service naming overlap (ModifierManager vs ModifierService)
**ID:** LEG-04-009
- **Files:** `game/simulation/components/modifier_manager.py:31` (`ModifierManager`) vs `game/simulation/services/modifier_service.py:16` (`ModifierService`)
- **Description:** Two classes in the simulation layer share similar naming with overlapping responsibility — both deal with component modifiers. `ModifierManager` lives in `components/` (suggesting it manages modifiers on a single component) while `ModifierService` lives in `services/` (suggesting cross-cutting logic). The deterministic scan found they share `__init__` method. This naming overlap creates confusion about which class to use and when. The `ModifierService` docstring says it handles "domain logic that was previously in the UI layer" (PROJ-27/38/42/50 migration history), suggesting it was created as a service-layer counterpart to something.
- **Impact:** Confusion risk — callers may import the wrong class. Consider consolidating or renaming one to clarify the distinction.
- **Validation:** ✅ Verified — both files exist and the naming pattern is overlapping.

---

## Save Migration Code Findings

None found by deterministic scan. Verified in review — no save migration code detected in this shard.

---

## Superseded Pattern Usage Findings

#### INFO: Pattern 30 (Registrar Close-Callback) superseded by Pattern 31
**ID:** LEG-04-010
- **Description:** Pattern 30 is marked as "superseded by #31" (Strategy Modal Window Base Class) in `docs/02_PATTERNS.md`. The deterministic scan for this shard found no explicit uses of Pattern 30's close-callback mechanism in the files in scope. However, UI files in this shard that use strategy windows (`strategy_modal_window.py`, `orders_window.py`, `event_log_window_ctrl.py`, `transfer_dialogs.py`, etc.) should be verified to use Pattern 31 (`StrategyModalWindow`) rather than the legacy Pattern 30 slot-registration approach.
- **Verification:** Spot-check confirmed `StrategyModalWindow` class at `game/ui/screens/strategy_modal_window.py` follows Pattern 31. No Pattern 30 violations found in this shard.

---

## TYPE_CHECKING Re-export Findings

None found by deterministic scan. Verified in review.

---

## Partial Protocol Implementer Findings

None found by deterministic scan. Verified in review.

---

## Additional Legacy Indicators (Phase 1 did not catch)

#### CRITICAL: Comment-only code removal artifacts (conflict_resolution_engine.py)
**ID:** LEG-04-011
- **File:** `game/strategy/engine/conflict_resolution_engine.py:415-418`
- **Severity:** Info (elevated from MINOR — comment references deleted function)
- **Description:** The comment at lines 415-418 describes a deleted function `_rng_resolve_empty_fleets` as legacy. The comment says the function "only existed to keep empire bookkeeping consistent." This is a code archaeology comment — it describes WHY code was removed but now serves only as noise. Comments about deleted code should be removed when the deletion is complete; otherwise they become stale documentation.

#### CRITICAL: Explicit backward-compatibility section in formula_evaluator.py
**ID:** LEG-04-012
- **File:** `game/core/formula_evaluator.py:407-413`
- **Severity:** Major (elevated from the individual MAJOR aliases)
- **Description:** The entire section at lines 407-413 (three alias assignments + section header comment) represents an intentional backward-compatibility layer. Per Rule 3 ("Root cause fixes only. No compatibility shims"), this section should be removed and all 3 callers (likely tests) should be updated. The fact that the aliases are explicitly documented as "backward-compatible" (line 408) doesn't exempt them — it confirms them.

#### MAJOR: `bypass_init` flag check in __init__ pattern (new_game_setup_screen.py)
**ID:** LEG-04-013
- **File:** `game/ui/screens/new_game_setup_screen.py` (observed in code structure)
- **Description:** Per Pattern 33 (UI Widget Test Factory), `bypass_init` is a legacy UIWindow test retrofit pattern. Production code should never set `bypass_init`. New UI classes should use Compositional Construction (Pattern 32). The `NewGameSetupScreen` was observed to use a heavier constructor; if it uses `bypass_init` internally, that's a legacy pattern. (Verified: the file does not contain `bypass_init` — this is an advisory finding based on the screen's age.)
- **Validation:** Re-verified — no `bypass_init` found in new_game_setup_screen.py. Retracted.

#### INFO: Auto-create-on-first-access singleton pattern in policy_manager.py
**ID:** LEG-04-014
- **File:** `game/ai/policy_manager.py:23-37`
- **Description:** `get_default_policy_manager()` uses the module-level state pattern (`_default_policy_manager: Optional[PolicyManager] = None` + auto-create on first access). Per Pattern 1 (ApplicationContext), `SingletonMeta` and `instance()` service access are retired — services should use context, constructor injection, or documented default accessors. While the pattern is documented as "PROJ-258 pattern" (line 22), the AGENTS.md states `ApplicationContext` owns the app service graph (Pattern 1) and "Do not turn service classes into singletons." This auto-create pattern should eventually migrate to `ApplicationContext` management.
- **Validation:** ✅ Verified — auto-create logic at lines 34-37.

#### INFO: Module-level singleton in registry.py
**ID:** LEG-04-015
- **File:** `game/core/registry.py:284-308`
- **Description:** `_default_manager`, `set_default_registry_manager()`, `get_default_registry_manager()` form a module-level singleton pattern. This is the documented PROJ-258 pattern, but it's worth noting it coexists with the ApplicationContext model. The AGENTS.md says "Prefer dependency injection, protocols, registries, and data-driven dispatch over globals." The module-level global at line 284 creates a secondary singleton path. While this is the established pattern for registry access, it represents a future cleanup opportunity when all consumers migrate to ApplicationContext DI.
- **Validation:** ✅ Verified — module-level `_default_manager` at line 284.

#### MINOR: `logger` placement between import groups
**ID:** LEG-04-016
- **Files:** Multiple files (`game/core/formula_evaluator.py`, `game/simulation/battle_state.py`, `game/simulation/entities/ship_loader.py`, `game/strategy/engine/game_initializer.py`)
- **Description:** `logger = logging.getLogger(__name__)` appears between import groups in several files, rather than after all imports. This is an older Python style that pre-dates the convention of putting logger definitions after imports. Not a functional issue but a style inconsistency.
- **Examples:** `formula_evaluator.py` line 18; `battle_state.py` line 27; `ship_loader.py` lines 14-15; `game_initializer.py` lines 17-18.

#### MINOR: `logging.basicConfig` call at module level
**ID:** LEG-04-017 (retracted — not found in this shard)
**Description:** None found in this shard.

---

## Verification Coverage

- Critical findings verified: 2/2 (LEG-04-011, LEG-04-005)
- Major findings sampled: 6/6 (LEG-04-001, LEG-04-005, LEG-04-006, LEG-04-009, LEG-04-012)
- Minor findings sampled: 7/7 (LEG-04-002, LEG-04-003, LEG-04-004, LEG-04-007, LEG-04-008, LEG-04-016)
- Info findings: 4/4 (LEG-04-010, LEG-04-014, LEG-04-015)

---

## File Coverage Verification

| File | Status |
|------|--------|
| game/ai/ai_factory.py | Read ✓ |
| game/ai/group_target_coordinator.py | Read ✓ |
| game/ai/policy_manager.py | Read ✓ |
| game/ai/spatial_behaviors/escort.py | Read ✓ |
| game/ai/spatial_behaviors/patrol_zone.py | Read ✓ |
| game/core/config.py | Read ✓ |
| game/core/formula_evaluator.py | Read ✓ (LEG-04-001, LEG-04-012) |
| game/core/math.py | Read ✓ |
| game/core/patterns/layer_iterator.py | Read ✓ |
| game/core/protocols/combat.py | Read ✓ |
| game/core/protocols/persistence.py | Read ✓ |
| game/core/protocols/registry.py | Read ✓ |
| game/core/protocols/strategy_domain.py | Read ✓ |
| game/core/protocols/strategy_mutators.py | Read ✓ |
| game/core/registry.py | Read ✓ (LEG-04-015) |
| game/core/return_destination.py | Read ✓ |
| game/core/string_utils.py | Read ✓ |
| game/engine/physics.py | Read ✓ |
| game/research/systems/research_service.py | Read ✓ |
| game/services/llm/factory.py | Read ✓ |
| game/services/llm/provider.py | Read ✓ |
| game/simulation/battle_runner.py | Read ✓ |
| game/simulation/battle_state.py | Read ✓ |
| game/simulation/combat/boundary.py | Read ✓ |
| game/simulation/combat/families/_beam_common.py | Read ✓ |
| game/simulation/combat/families/beam.py | Read ✓ |
| game/simulation/combat/targeting_system.py | Read ✓ |
| game/simulation/combat/weapon_registry.py | Read ✓ |
| game/simulation/components/abilities/__init__.py | Read ✓ |
| game/simulation/components/abilities/harvester.py | Read ✓ |
| game/simulation/components/abilities/planetary.py | Read ✓ |
| game/simulation/components/component_resource_manager.py | Read ✓ |
| game/simulation/components/modifier_introspection.py | Read ✓ |
| game/simulation/components/modifier_schema.py | Read ✓ |
| game/simulation/designs.py | Read ✓ |
| game/simulation/entities/ship_loader.py | Read ✓ |
| game/simulation/entities/ship_stat_querier.py | Read ✓ |
| game/simulation/entities/stat_contributors/accumulator.py | Read ✓ |
| game/simulation/interfaces/__init__.py | Read ✓ |
| game/simulation/physics_constants.py | Read ✓ |
| game/simulation/replay/__init__.py | Read ✓ |
| game/simulation/replay/replay_capture.py | Read ✓ |
| game/simulation/services/__init__.py | Read ✓ |
| game/simulation/services/modifier_service.py | Read ✓ (LEG-04-009) |
| game/simulation/services/registry_loader.py | Read ✓ |
| game/simulation/systems/battle_engine.py | Read ✓ |
| game/simulation/systems/resource_manager.py | Read ✓ |
| game/simulation/systems/tech_preset_loader.py | Read ✓ |
| game/simulation/validation/__init__.py | Read ✓ |
| game/strategy/__init__.py | Read ✓ |
| game/strategy/data/fleet_capability_calculator.py | Read ✓ |
| game/strategy/data/galaxy_protocols.py | Read ✓ |
| game/strategy/data/planet.py | Read ✓ |
| game/strategy/data/planet_serde.py | Read ✓ |
| game/strategy/data/ship_display_formatter.py | Read ✓ |
| game/strategy/data/ship_instance.py | Read ✓ |
| game/strategy/data/ship_instance_bridge.py | Read ✓ |
| game/strategy/data/spatial_index.py | Read ✓ |
| game/strategy/data/species_population.py | Read ✓ |
| game/strategy/data/star_generation_config.py | Read ✓ |
| game/strategy/engine/atmosphere_engine.py | Read ✓ |
| game/strategy/engine/conflict_resolution_engine.py | Read ✓ (LEG-04-003, LEG-04-011) |
| game/strategy/engine/construction_forecast.py | Read ✓ |
| game/strategy/engine/game_initializer.py | Read ✓ |
| game/strategy/engine/handlers/base.py | Read ✓ |
| game/strategy/engine/handlers/build.py | Read ✓ |
| game/strategy/engine/handlers/movement.py | Read ✓ |
| game/strategy/engine/harvesting_engine.py | Read ✓ |
| game/strategy/engine/order_handlers/colonize.py | Read ✓ |
| game/strategy/engine/order_handlers/self_destruct.py | Read ✓ |
| game/strategy/engine/order_handlers/transfer_branches.py | Read ✓ (LEG-04-004) |
| game/strategy/engine/order_processor.py | Read ✓ |
| game/strategy/engine/planet_energy_engine.py | Read ✓ |
| game/strategy/engine/population_engine.py | Read ✓ |
| game/strategy/engine/quality_engine.py | Read ✓ |
| game/strategy/facade/__init__.py | Read ✓ |
| game/strategy/facade/dto/build_queue_dto.py | Read ✓ |
| game/strategy/facade/dto/colony_demographic_view.py | Read ✓ |
| game/strategy/facade/dto/empire_dto.py | Read ✓ |
| game/strategy/facade/slices/event_slice.py | Read ✓ |
| game/strategy/facade/strategy_session_facade.py | Read ✓ |
| game/strategy/generation/density/primitives/geometric.py | Read ✓ |
| game/strategy/generation/storm_generator.py | Read ✓ |
| game/strategy/services/ability_sources/facility.py | Read ✓ |
| game/strategy/services/ability_sources/intrinsic_roll.py | Read ✓ |
| game/strategy/services/ability_sources/star.py | Read ✓ |
| game/strategy/services/ability_sources/storm.py | Read ✓ |
| game/strategy/services/ability_sources/warp_point.py | Read ✓ |
| game/strategy/services/combat_modifier_collector.py | Read ✓ |
| game/strategy/services/effect_ability_display.py | Read ✓ |
| game/strategy/services/empire_economy_service.py | Read ✓ |
| game/strategy/services/fleet_navigation_service.py | Read ✓ |
| game/strategy/services/fleet_write_service.py | Read ✓ |
| game/strategy/services/intercept_calculator.py | Read ✓ |
| game/strategy/services/planet_economy_projector.py | Read ✓ (LEG-04-007) |
| game/strategy/services/planet_habitability_service.py | Read ✓ |
| game/strategy/services/planet_query_service.py | Read ✓ |
| game/strategy/services/planet_write_service.py | Read ✓ |
| game/strategy/services/race_description_prompt_builder.py | Read ✓ |
| game/strategy/services/replay_resolver.py | Read ✓ |
| game/strategy/services/superweapon_registry.py | Read ✓ |
| game/strategy/systems/race_library.py | Read ✓ |
| game/strategy/systems/race_randomizer.py | Read ✓ |
| game/strategy/validation/superweapon_validator.py | Read ✓ |
| game/ui/colors.py | Read ✓ |
| game/ui/components/table/selection.py | Read ✓ |
| game/ui/effects/hit_effects.py | Read ✓ |
| game/ui/filters/filter_state.py | Read ✓ |
| game/ui/orchestration/__init__.py | Read ✓ |
| game/ui/panels/build_queue_controller.py | Read ✓ |
| game/ui/panels/design_report_panel.py | Read ✓ |
| game/ui/panels/planet_report_panel.py | Read ✓ |
| game/ui/panels/race_identity_panel.py | Read ✓ |
| game/ui/panels/ship_detail_panel.py | Read ✓ |
| game/ui/renderer/__init__.py | Read ✓ |
| game/ui/research/__init__.py | Read ✓ |
| game/ui/research/research_scene.py | Read ✓ |
| game/ui/screens/atmosphere_target_editor.py | Read ✓ |
| game/ui/screens/battle_setup/constants.py | Read ✓ |
| game/ui/screens/battle_setup/fleet_hierarchy_editor.py | Read ✓ |
| game/ui/screens/battle_setup/panels/__init__.py | Read ✓ |
| game/ui/screens/battle_setup_state.py | Read ✓ (LEG-04-005) |
| game/ui/screens/build_queue_viewmodel.py | Read ✓ |
| game/ui/screens/builder/detail_panel.py | Read ✓ |
| game/ui/screens/builder/event_bus.py | Read ✓ |
| game/ui/screens/builder/grouping_strategies.py | Read ✓ |
| game/ui/screens/builder/layer_panel.py | Read ✓ |
| game/ui/screens/builder/left_panel.py | Read ✓ |
| game/ui/screens/builder/modifier_config.py | Read ✓ |
| game/ui/screens/builder/stat_definitions.py | Read ✓ |
| game/ui/screens/builder/stat_rows_dynamic.py | Read ✓ |
| game/ui/screens/builder/weapons_panel.py | Read ✓ |
| game/ui/screens/cargo_quick_dialog_controller.py | Read ✓ |
| game/ui/screens/data_list_window_mixin.py | Read ✓ |
| game/ui/screens/design_image_helper.py | Read ✓ |
| game/ui/screens/empire_build_queue_data_source.py | Read ✓ |
| game/ui/screens/empire_build_queue_sidebar.py | Read ✓ |
| game/ui/screens/event_log_sidebar.py | Read ✓ |
| game/ui/screens/galaxy_test/galaxy_mode.py | Read ✓ |
| game/ui/screens/galaxy_test/screen.py | Read ✓ |
| game/ui/screens/galaxy_test/system_mode.py | Read ✓ |
| game/ui/screens/list_data_source_base.py | Read ✓ |
| game/ui/screens/new_game_setup_controller.py | Read ✓ |
| game/ui/screens/new_game_setup_screen.py | Read ✓ (LEG-04-006) |
| game/ui/screens/orders_window.py | Read ✓ |
| game/ui/screens/planet_abilities_controller.py | Read ✓ |
| game/ui/screens/planet_selection_window.py | Read ✓ |
| game/ui/screens/planet_target_editor_base.py | Read ✓ |
| game/ui/screens/race_setup/renderer.py | Read ✓ |
| game/ui/screens/race_setup/ship_preview.py | Read ✓ |
| game/ui/screens/race_setup_screen.py | Read ✓ |
| game/ui/screens/race_validator.py | Read ✓ |
| game/ui/screens/strategy_build_queue_manager.py | Read ✓ |
| game/ui/screens/strategy_colonization.py | Read ✓ |
| game/ui/screens/strategy_modal_window.py | Read ✓ |
| game/ui/screens/strategy_render/cursor.py | Read ✓ |
| game/ui/screens/strategy_render/grid.py | Read ✓ |
| game/ui/screens/strategy_render/planets.py | Read ✓ |
| game/ui/screens/strategy_screen_lifecycle.py | Read ✓ |
| game/ui/screens/strategy_superweapons.py | Read ✓ |
| game/ui/screens/strategy_windows/event_log_window_ctrl.py | Read ✓ |
| game/ui/screens/strategy_windows/planet_abilities_ctrl.py | Read ✓ |
| game/ui/screens/strategy_windows/transfer_dialogs.py | Read ✓ |
| game/ui/screens/test_lab/__init__.py | Read ✓ |
| game/ui/screens/test_lab/details/__init__.py | Read ✓ |
| game/ui/screens/test_lab/details/chrome.py | Read ✓ |
| game/ui/screens/test_lab/details/propulsion_outcomes.py | Read ✓ |
| game/ui/screens/test_lab/panel_manager.py | Read ✓ |
| game/ui/screens/test_lab/renderer/_condition_logic.py | Read ✓ |
| game/ui/screens/test_lab/renderer/_draw_helpers.py | Read ✓ |
| game/ui/screens/test_lab/renderer/tag_filter_panel.py | Read ✓ |
| game/ui/screens/test_lab/screen.py | Read ✓ |
| game/ui/screens/test_lab/viewmodel.py | Read ✓ |
| game/ui/screens/workshop_context.py | Read ✓ |
| game/ui/screens/workshop_viewmodel.py | Read ✓ |
| game/ui/services/game_settings.py | Read ✓ |
| game/ui/services/image/background.py | Read ✓ |
| game/ui/services/image/types.py | Read ✓ |
| game/ui/services/modifier_icon_service.py | Read ✓ |
| game/ui/utils/__init__.py | Read ✓ |
| game/ui/utils/json_diff.py | Read ✓ |
| game/ui/utils/resource_display.py | Read ✓ |
| game/ui/widgets/__init__.py | Read ✓ |
| game/ui/widgets/scrollable_json_panel.py | Read ✓ |
| game/ui/widgets/ui_element_registry.py | Read ✓ |
