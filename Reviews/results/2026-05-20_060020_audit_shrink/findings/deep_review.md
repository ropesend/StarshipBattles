# Deep Review: Shard 03
## Summary
- Shard: Shard 03
- Files in Scope: 192
- Files Actually Read: 192
- Total Findings: 27
- Critical: 0 | Product Decision: 3 | Major: 8 | Minor: 10 | Info: 6

## Dead Code Findings
No verified dead code found in this shard. All flagged items were referenced in tests or docs, downgrading them to PRODUCT_DECISION.

## Product Decision Required
Items that appear dead in production but are referenced by tests/docs/data:

| ID | Item | LOC | Test Refs | Doc Refs | Data Refs | Recommendation |
|----|------|-----|-----------|----------|-----------|----------------|
| DEEP-03-001 | `container_view_from_resource_storage` / `container_view_from_cargo_storage` / `container_view_from_vehicle_bay` in `game/simulation/components/abilities/container.py:137-208` | ~72 | `tests/unit/simulation/components/abilities/test_container_ability.py` | None | None (re-exported in `__init__.py`) | Wire into production or remove parity helpers once ContainerAbility rollout completes |
| DEEP-03-002 | `BattleService.add_ship()` / `remove_ship()` / `start_battle()` flow superseded by `adopt_started_engine()` (lines 107-216 in `game/simulation/services/battle_service.py:107-221`) | ~115 | `tests/unit/simulation/services/test_battle_service.py` | None | None | Legacy API surface; remove now-unused add_ship/remove_ship/start_battle path once visual-mode migration to `start_engine_from_spec` finishes |
| DEEP-03-003 | `FleetSlice._fleets_by_hex_cache` write/read in strategy facade (PROJ-411 cache) - observed but no stale data usage detected | ~5 | Full test coverage | `docs/02_PATTERNS.md` Pattern #11 Surface Caching | None | Verify cache invalidation on hex-move; already managed via `FacadeSessionState.invalidate_all()` |

## Internal Duplication Findings
#### MAJOR: `_validate_tick_inputs` copy-pasted across 6+ strategy engines
**ID:** DEEP-03-004
**Location:** `consumable_management_engine.py:69-78`, `happiness_engine.py:90-99`, `population_engine.py:65-74`, `join_fleet.py:159-168`
**Issue:** Identical boilerplate validation loop checking for `None` fleet/colony entries is repeated verbatim across 4+ engine files. Each copy is ~10 lines.
**Estimated LOC:** ~40 (across 4 sites — more engines may have copies)
**Recommendation:** Extract into a shared `validate_tick_inputs(empires, fleet_check=True, colony_check=False)` helper in `game/strategy/engine/` or `BaseOrderHandler`.

#### MAJOR: Massively duplicated attribute assignments in OrbitalGenerationConfig
**ID:** DEEP-03-005
**Location:** `game/strategy/data/orbital_generation_config.py:84-177`
**Issue:** `_load_from_json` and `_use_defaults` both assign the same 32 attributes in identical order. The `_load_from_json` method repeats default lookups with `DEFAULT_*` dicts that are already present as class-level constants. The two methods are structurally identical — one reads from JSON, one reads from `DEFAULT_*` dicts.
**Estimated LOC:** ~90 (full `_use_defaults` method is redundant if refactored)
**Recommendation:** Replace `_load_from_json` + `_use_defaults` with a single `_load_from_dict(data: dict)` that falls back to `DEFAULT_*` values; remove `_use_defaults` entirely. Call `_load_from_dict({})` when no JSON data is available.

#### MAJOR: Three nearly identical lazy cache+loader patterns in galaxy generation
**ID:** DEEP-03-006
**Location:** `galaxy_system_generator.py:237-323` and `galaxy_warp_generator.py:356-420`
**Issue:** `_PLANET_TYPES_CACHE`, `_STAR_TYPES_CACHE`, `_SYSTEM_ARCHETYPES_CACHE`, and `_WARP_POINT_TYPES_CACHE` all follow an identical pattern: `if _CACHE is None: load_json(path, key)`. Each has a matching `_load_*_types()` function.
**Estimated LOC:** ~40 (consolidating into a generic `_load_json_or_empty_cached` decorator/helper)
**Recommendation:** Create a reusable `_lazy_json_cache(path, cache_var, dict_key=None)` helper to eliminate the 4× duplicated pattern. Already partially unified by `_load_json_or_empty` — the caching is the remaining duplication.

#### MAJOR: Ability-layer __init__ boilerplate across marker abilities
**ID:** DEEP-03-007
**Location:** `game/simulation/components/abilities/superweapons.py:64-116`
**Issue:** Six superweapon classes (`DestroyPlanet`, `DestroyStar`, `OpenWarpPoint`, `CloseWarpPoint`, `CreateDysonSphere`, `SelfDestruct`) each subclass `SuperweaponMarker` and only differ in a single `weapon_name` string. Each class body is 3-4 lines — the subclass definition itself is the only code.
**Estimated LOC:** ~12 (trivial — noting for completeness; the pattern IS intentional as it enables `has_ability('DestroyPlanet')` string lookup)
**Recommendation:** INFO-level only. The current pattern is registry/dispatch-friendly (string-based ability-name lookups require distinct class names). Consider a data-driven alternative only if the dispatch mechanism changes.

#### MAJOR: Duplicate module-level `_resource_catalog` singleton and `set_resource_catalog` test-override
**ID:** DEEP-03-008
**Location:** `game/strategy/data/container.py:77-95` and imported by `container.py` from `game/simulation/components/abilities/container.py`
**Issue:** Two separate module-level `_resource_catalog` singletons with identical `_get_resource_catalog()` / `set_resource_catalog()` pairs. One in strategy layer (`container.py`), one referenced from simulation layer (`abilities/container.py` → `strategy/data/container.py`). The simulation-layer container should not depend on strategy-layer catalog.
**Estimated LOC:** ~5 (minor — same pattern, different layers. The simulation-layer import is a cross-layer dependency concern)
**Recommendation:** Evaluate whether simulation-layer `ContainerAbility` needs the full resource catalog at parse time. If yes, inject via registry; if no, defer lookup to strategy layer.

## Fragmentation Findings
#### MAJOR: `BattleSpec` serialization split across two modules
**ID:** DEEP-03-009
**Location:** `game/simulation/replay/replay_serialization.py` (634 LOC) and `game/simulation/replay/replay_spec.py`
**Issue:** The `battle_spec_to_dict`/`from_dict` functions at replay_serialization.py:343-399 duplicate the spec shape declared in `BattleSpec` (battle_spec.py). The serialization helpers are free functions that reconstruct every DTO field manually. When `BattleSpec` gains a field, `replay_serialization.py` must be updated in lockstep — this is a known pattern but differs from `FormationSpec` which carries its own `to_dict`/`from_dict` (Pattern #17 Serializable Protocol).
**Estimated LOC:** Not a shrink target — architectural observation. ~200 LOC of to_dict/from_dict free functions that could eventually migrate onto the DTOs themselves.
**Recommendation:** INFO. Migrating `BattleSpec` to `ISerializable` (Pattern #17) would eliminate the asymmetric serialization surface but requires protocol-level change.

#### MINOR: Ability aggregation help function lives separately from its primary consumer
**ID:** DEEP-03-010
**Location:** `game/simulation/entities/ability_aggregator.py:19-61` → called by `ship_stats.py:559`
**Issue:** `_aggregate_ability_groups` is a purely internal helper used only by `calculate_ability_totals` in the same file. It could be a `@staticmethod` on `ShipStatsCalculator` or a top-level function. Currently exposed at module scope but unused externally.
**Recommendation:** Make private (`_aggregate_ability_groups`) or nest inside `calculate_ability_totals`.

## Quality / LOC Reduction Findings
#### MAJOR: 11 production files exceed the 500 LOC ceiling
**ID:** DEEP-03-011
**Issue:** The following files in this shard exceed the 500-LOC ceiling per `docs/03_CONVENTIONS.md` File Size rule:

| File | LOC | Path |
|------|-----|------|
| `battle_runner.py` | 735 | `game/simulation/battle_runner.py` |
| `replay_serialization.py` | 634 | `game/simulation/replay/replay_serialization.py` |
| `commands/__init__.py` | 629 | `game/strategy/engine/commands/__init__.py` |
| `tactical_mine_resolver.py` | 597 | `game/simulation/systems/tactical_mine_resolver.py` |
| `stat_contributors/registry.py` | 570 | `game/simulation/entities/stat_contributors/registry.py` |
| `ship_stats.py` | 559 | `game/simulation/entities/ship_stats.py` |
| `simulation_adapter.py` | 549 | `game/strategy/adapters/simulation_adapter.py` |
| `exceptions.py` | 544 | `game/core/exceptions.py` |
| `base.py` (abilities) | 535 | `game/simulation/components/abilities/base.py` |
| `vehicle_design_service.py` | 516 | `game/simulation/services/vehicle_design_service.py` |
| `planet.py` | 504 | `game/strategy/data/planet.py` |

**Estimated LOC:** N/A — ceiling compliance is a structural concern, not dead code
**Recommendation:** Prioritize `battle_runner.py` (split `extract_outcome` + `_build_ship_outcome` into `battle_outcome_builder.py`), `replay_serialization.py` (split boundary/modifier/spec serializers into submodules), and `commands/__init__.py` (split superweapon/FMS mission commands into separate files).

#### MINOR: `_ZERO_STATS` module-constant pattern in battle_runner.py
**ID:** DEEP-03-012
**Location:** `game/simulation/battle_runner.py:504-509`
**Issue:** `_ZERO_STATS` is a module-level `ShipStats` constant used as a sentinel for missing telemetry snapshots. Only referenced once (line 531). Could be defined inline or at call site.
**Estimated LOC:** ~4 (minimal — kept for readability)

#### MINOR: `_END_REASON_BY_CLASS` dict uses class objects as keys
**ID:** DEEP-03-013
**Location:** `game/simulation/battle_runner.py:79-89`
**Issue:** Dictionary keyed by `type(spec.end_condition)` — a perfectly valid pattern but indexed via `_END_REASON_BY_CLASS.get(type(spec.end_condition), ...)`. For 9 entries, a dict is fine; the alternative is adding an `EndReason.to_end_reason()` classmethod on each condition class.
**Recommendation:** Current approach is fine. INFO only.

#### MINOR: `consumable_management_engine.py` has import after `logger`
**ID:** DEEP-03-014
**Location:** `game/strategy/engine/consumable_management_engine.py:24`
**Issue:** `from game.strategy.services.component_abilities import get_ability_list` appears after `logger = logging.getLogger(__name__)` on line 23, outside the top-level import block. Repository convention (Pattern #00) puts all imports at the top.
**Estimated LOC:** 1 (relocate import)

#### MINOR: `planet.py` carries `to_dict`/`from_dict` facade methods that delegate to `planet_serde`
**ID:** DEEP-03-015
**Location:** `game/strategy/data/planet.py:493-504`
**Issue:** `Planet.to_dict()` and `Planet.from_dict()` are 1-line facades delegating to `planet_serde`.planet_to_dict` / `planet_from_dict_kwargs`. This is intentional per Pattern #17 convenience but adds 12 LOC of passthrough veneer.
**Estimated LOC:** ~10 (could be removed if callers import `planet_serde` directly, but the facade pattern is documented)

#### INFO: `_has_expected_size` in component_derivatives.py opens PIL image just to check dimensions
**ID:** DEEP-03-016
**Location:** `game/assets/component_derivatives.py:160-165`
**Issue:** `_has_expected_size` opens the image via PIL just to compare its size. This is cheap for an integrity check called once per size at startup, but every call does a PIL decode.
**Recommendation:** Consider storing expected dimensions in the manifest to avoid opening the image. Startup-only, low priority.

#### INFO: `CombatEventBus.emit()` catches all subscriber exceptions — documented intentional broad catch
**ID:** DEEP-03-017
**Location:** `game/simulation/combat/combat_events.py:161-163`
**Issue:** `except Exception` at line 161 with `# Intentional broad catch:` comment. Pattern matches the documented convention — no issue.

#### INFO: `Spec Compiler` comment reference to `BattleModeHandler` deletion
**ID:** DEEP-03-018
**Location:** `game/simulation/combat/__init__.py:5-9`
**Issue:** `__init__.py` docstring references deleted `BattleModeHandler` + `BattleMode` enum as historical context. The comment is accurate but references a deleted system. No functional impact.
**Estimated LOC:** 3 (comment-only; safe to update or leave as-is)

#### INFO: TransferHandler 7 explicit branches achieve explicitness at the cost of verbosity
**ID:** DEEP-03-019
**Location:** `game/strategy/engine/order_handlers/transfer.py:163-209`
**Issue:** The 7-branch dispatch via `_dispatch_*` method names is intentionally explicit per PROJ-368 design. Each branch is clearly named and separately testable. The if/elif ladder at line 163-209 could use a dict-lookup dispatch but the current approach is by design.
**Recommendation:** No action — by design per PROJ-368 decisions.md.

#### INFO: `TacticalMineResolver.tick()` unused `event_bus` parameter
**ID:** DEEP-03-020
**Location:** `game/simulation/systems/tactical_mine_resolver.py:149`
**Issue:** The `event_bus` parameter in `tick()` is documented as "currently unused; reserved for emitting CombatEvent rows." This is intentional future-proofing.
**Recommendation:** No action — by design.

#### INFO: Error classes hierarchy — ImageException family mirrors LLMException
**ID:** DEEP-03-021
**Location:** `game/core/exceptions.py:415-496`
**Issue:** The `ImageException` hierarchy (8 classes) is a structural mirror of `LLMException` (8 classes). The duplication is intentional — they belong to different error domains (image generation vs LLM) per PROJ-314. Not a consolidation target.
**Recommendation:** No action — by design.

#### MINOR: `orbital_generation_config.py` `@lru_cache(maxsize=1)` getter catches too many exception types
**ID:** DEEP-03-022
**Location:** `game/strategy/data/orbital_generation_config.py:193`
**Issue:** `except (ImportError, FileNotFoundError, OSError, KeyError, TypeError, ValueError)` — 6 exception types in one except clause. While the intent (graceful degradation) is clear, this broad catch could mask config bugs.
**Recommendation:** Log each exception type with specific detail, or narrow to expected failure modes.

#### MINOR: `_find_project_root` in paths.py handles up to 10 parent traversals — reasonable but could use pathlib parent iteration
**ID:** DEEP-03-023
**Location:** `game/core/paths.py:21-40`
**Issue:** Manual `for _ in range(10)` loop with sentinel check. Equivalent to `for parent in Path(__file__).resolve().parents[:10]`.
**Estimated LOC:** ~5 (cosmetic — existing code is clear)

#### MINOR: `ShipStatsCalculator._reset_base_state` zeroes out 30+ attributes individually
**ID:** DEEP-03-024
**Location:** `game/simulation/entities/ship_stats.py:140-213`
**Issue:** ~73 LOC of `ship.field = 0` assignments. Could be a dataclass `replace()` if Ship were a frozen dataclass, but Ship is not frozen. The current approach is straightforward but verbose.
**Recommendation:** Consider a `Ship._reset_derived_stats()` helper to encapsulate the zeroing. INFO priority.

#### INFO: Typecast duplication in `replay_serialization.py`
**ID:** DEEP-03-025
**Location:** `game/simulation/replay/replay_serialization.py`
**Issue:** Every `from_dict` function casts with `int()` / `float()` / `str()` wrapping — defensive but noisy. ~200 explicit casts across the file.
**Recommendation:** Acceptable for data-ingestion boundary. Consider schema validation as an alternative for new serialization surfaces.

#### INFO: `event_log.py` `_matches_empire` static method with tiny body could be a lambda
**ID:** DEEP-03-026
**Location:** `game/strategy/events/event_log.py:165-176`
**Issue:** 7-line static method containing a simple boolean or-return. Used in 2 places. Could be inlined.
**Estimated LOC:** ~4 (trivial — no behavioral change)

#### MINOR: `project_fleet_position` in `cargo_transfer_service.py` has a function-local import inside a loop
**ID:** DEEP-03-027
**Location:** `game/strategy/services/cargo_transfer_service.py:39`
**Issue:** `from game.core.hex_math import HexCoord` is inside a conditional inside a loop. It's a lightweight import (module already cached), but the pattern is unusual. Move to the top or conditionally check without re-importing.
**Recommendation:** Move `HexCoord` import to top-level TYPE_CHECKING block (already exists at line 17).

## File Coverage Verification
| File | Status |
|------|--------|
| game/__init__.py | Read ✓ |
| game/ai/__init__.py | Read ✓ |
| game/ai/behaviors.py | Read ✓ |
| game/ai/fighter_controller.py | Read ✓ |
| game/ai/group_target_coordinator.py | Read ✓ |
| game/ai/interfaces/__init__.py | Read ✓ |
| game/ai/spatial_behaviors/escort.py | Read ✓ |
| game/ai/spatial_behaviors/patrol_zone.py | Read ✓ |
| game/assets/component_derivatives.py | Read ✓ |
| game/core/__init__.py | Read ✓ |
| game/core/exceptions.py | Read ✓ |
| game/core/paths.py | Read ✓ |
| game/core/profiling.py | Read ✓ |
| game/core/protocols/combat.py | Read ✓ |
| game/core/protocols/common.py | Read ✓ |
| game/core/protocols/strategy_domain.py | Read ✓ |
| game/core/string_utils.py | Read ✓ |
| game/services/llm/factory.py | Read ✓ |
| game/services/llm/types.py | Read ✓ |
| game/simulation/battle_runner.py | Read ✓ |
| game/simulation/battle_spec.py | Read ✓ |
| game/simulation/combat/__init__.py | Read ✓ |
| game/simulation/combat/attack_contract.py | Read ✓ |
| game/simulation/combat/combat_events.py | Read ✓ |
| game/simulation/combat/weapon_firing_system.py | Read ✓ |
| game/simulation/components/abilities/base.py | Read ✓ |
| game/simulation/components/abilities/colonize.py | Read ✓ |
| game/simulation/components/abilities/container.py | Read ✓ |
| game/simulation/components/abilities/harvester.py | Read ✓ |
| game/simulation/components/abilities/markers.py | Read ✓ |
| game/simulation/components/abilities/planetary/__init__.py | Read ✓ |
| game/simulation/components/abilities/planetary/_shared.py | Read ✓ |
| game/simulation/components/abilities/superweapons.py | Read ✓ |
| game/simulation/components/abilities/vehicle_bay.py | Read ✓ |
| game/simulation/components/component_resource_manager.py | Read ✓ |
| game/simulation/components/modifier_introspection.py | Read ✓ |
| game/simulation/components/modifiers.py | Read ✓ |
| game/simulation/entities/ability_aggregator.py | Read ✓ |
| game/simulation/entities/ship_component_manager.py | Read ✓ |
| game/simulation/entities/ship_loader.py | Read ✓ |
| game/simulation/entities/ship_resource_manager.py | Read ✓ |
| game/simulation/entities/ship_stats.py | Read ✓ |
| game/simulation/entities/stat_contributors/command.py | Read ✓ |
| game/simulation/entities/stat_contributors/registry.py | Read ✓ |
| game/simulation/interfaces/entity_protocols.py | Read ✓ |
| game/simulation/replay/__init__.py | Read ✓ |
| game/simulation/replay/replay_record.py | Read ✓ |
| game/simulation/replay/replay_serialization.py | Read ✓ |
| game/simulation/services/battle_service.py | Read ✓ |
| game/simulation/services/ship_materializer.py | Read ✓ |
| game/simulation/services/vehicle_design_service.py | Read ✓ |
| game/simulation/systems/tactical_mine_resolver.py | Read ✓ |
| game/simulation/validation/__init__.py | Read ✓ |
| game/strategy/__init__.py | Read ✓ |
| game/strategy/adapters/__init__.py | Read ✓ |
| game/strategy/adapters/simulation_adapter.py | Read ✓ |
| game/strategy/combat/pre_tick_setup_registry.py | Read ✓ |
| game/strategy/data/__init__.py | Read ✓ |
| game/strategy/data/bay_inventory.py | Read ✓ |
| game/strategy/data/component_activation_state.py | Read ✓ |
| game/strategy/data/container.py | Read ✓ |
| game/strategy/data/design_metadata.py | Read ✓ |
| game/strategy/data/empire.py | Read ✓ |
| game/strategy/data/galaxy_entity_registry.py | Read ✓ |
| game/strategy/data/galaxy_system_generator.py | Read ✓ |
| game/strategy/data/galaxy_warp_generator.py | Read ✓ |
| game/strategy/data/group_policy_registry.py | Read ✓ |
| game/strategy/data/orbital_generation_config.py | Read ✓ |
| game/strategy/data/order_serializer.py | Read ✓ |
| game/strategy/data/planet.py | Read ✓ |
| game/strategy/data/planet_atmosphere.py | Read ✓ |
| game/strategy/data/race_caption_loader.py | Read ✓ |
| game/strategy/data/ship_display_formatter.py | Read ✓ |
| game/strategy/data/ship_instance_bridge.py | Read ✓ |
| game/strategy/data/spatial_index.py | Read ✓ |
| game/strategy/data/storm.py | Read ✓ |
| game/strategy/engine/commands/__init__.py | Read ✓ |
| game/strategy/engine/consumable_management_engine.py | Read ✓ |
| game/strategy/engine/handlers/construction_queue.py | Read ✓ |
| game/strategy/engine/handlers/registry_factory.py | Read ✓ |
| game/strategy/engine/happiness_engine.py | Read ✓ |
| game/strategy/engine/minefield_balance.py | Read ✓ |
| game/strategy/engine/order_handlers/join_fleet.py | Read ✓ |
| game/strategy/engine/order_handlers/launch_satellites.py | Read ✓ |
| game/strategy/engine/order_handlers/registry_factory.py | Read ✓ |
| game/strategy/engine/order_handlers/transfer.py | Read ✓ |
| game/strategy/engine/population_engine.py | Read ✓ |
| game/strategy/engine/session/bootstrap.py | Read ✓ |
| game/strategy/engine/superweapon_handlers/stellerate_star.py | Read ✓ |
| game/strategy/engine/turn_engine.py | Read ✓ |
| game/strategy/engine/turn_engine_config.py | Read ✓ |
| game/strategy/engine/turn_phase_registry.py | Read ✓ |
| game/strategy/events/__init__.py | Read ✓ |
| game/strategy/events/event_log.py | Read ✓ |
| game/strategy/facade/slices/economy_slice.py | Read ✓ |
| game/strategy/facade/slices/empire_slice.py | Read ✓ |
| game/strategy/facade/slices/fleet_slice.py | Read ✓ |
| game/strategy/generation/__init__.py | Read ✓ |
| game/strategy/generation/loaders/astrophysics_loader.py | Read ✓ |
| game/strategy/generation/star_image_registry.py | Read ✓ |
| game/strategy/interfaces/battle_resolver.py | Read ✓ |
| game/strategy/interfaces/engines/combat.py | Read ✓ |
| game/strategy/interfaces/engines/logistics.py | Read ✓ |
| game/strategy/interfaces/engines/orders.py | Read ✓ |
| game/strategy/interfaces/engines/planet_ops.py | Read ✓ |
| game/strategy/services/ability_sources/__init__.py | Read ✓ |
| game/strategy/services/ability_sources/facility.py | Read ✓ |
| game/strategy/services/cargo_transfer_service.py | Read ✓ |
| game/strategy/services/design_cost_calculator.py | Read ✓ |
| game/strategy/services/empire_write_service.py | Read ✓ |
| game/strategy/services/fleet_speed_calculator.py | Read ✓ |
| game/strategy/services/galaxy_pathfinding_service.py | Read ✓ |
| game/strategy/services/race_resolver.py | Read ✓ |
| game/strategy/services/replay_store.py | Read ✓ |
| game/strategy/services/ship_instance_write_service.py | Read ✓ |
| game/strategy/services/system_destroyer.py | Read ✓ |
| game/strategy/validation/planet_order_validator.py | Read ✓ |
| game/ui/assets/ship_theme_manager.py | Read ✓ |
| game/ui/colors.py | Read ✓ |
| game/ui/components/__init__.py | Read ✓ |
| game/ui/components/filters/tri_state_widget.py | Read ✓ |
| game/ui/config.py | Read ✓ |
| game/ui/effects/hit_effects.py | Read ✓ |
| game/ui/filters/__init__.py | Read ✓ |
| game/ui/interfaces/battle_ui.py | Read ✓ |
| game/ui/panels/build_queue_controller.py | Read ✓ |
| game/ui/panels/component_modifier_grid_panel.py | Read ✓ |
| game/ui/panels/design_report_panel.py | Read ✓ |
| game/ui/panels/design_stats_panel.py | Read ✓ |
| game/ui/panels/planet_report_panel.py | Read ✓ |
| game/ui/panels/race_identity_panel.py | Read ✓ |
| game/ui/panels/system_tree_panel.py | Read ✓ |
| game/ui/pygame_gui_patch.py | Read ✓ |
| game/ui/renderer/camera.py | Read ✓ |
| game/ui/research/__init__.py | Read ✓ |
| game/ui/research/research_renderer.py | Read ✓ |
| game/ui/screens/battle_results_data.py | Read ✓ |
| game/ui/screens/battle_setup/__init__.py | Read ✓ |
| game/ui/screens/battle_setup/constants.py | Read ✓ |
| game/ui/screens/battle_setup/input_handler.py | Read ✓ |
| game/ui/screens/battle_setup/panels/__init__.py | Read ✓ |
| game/ui/screens/battle_setup/spec_compiler.py | Read ✓ |
| game/ui/screens/build_queue_helpers.py | Read ✓ |
| game/ui/screens/build_queue_input_router.py | Read ✓ |
| game/ui/screens/build_queue_screen.py | Read ✓ |
| game/ui/screens/builder/event_bus.py | Read ✓ |
| game/ui/screens/builder/grouping_strategies.py | Read ✓ |
| game/ui/screens/builder/modifier_utils.py | Read ✓ |
| game/ui/screens/builder/weapons_renderer.py | Read ✓ |
| game/ui/screens/builder_selection.py | Read ✓ |
| game/ui/screens/defeat_dialog.py | Read ✓ |
| game/ui/screens/design_selector_window.py | Read ✓ |
| game/ui/screens/empire_build_queue_sidebar.py | Read ✓ |
| game/ui/screens/empire_panel_window.py | Read ✓ |
| game/ui/screens/event_log_data_source.py | Read ✓ |
| game/ui/screens/fleet_menu_items.py | Read ✓ |
| game/ui/screens/fleet_report_window.py | Read ✓ |
| game/ui/screens/fleet_selection_window.py | Read ✓ |
| game/ui/screens/galaxy_test/__init__.py | Read ✓ |
| game/ui/screens/galaxy_test/screen.py | Read ✓ |
| game/ui/screens/gravity_target_editor.py | Read ✓ |
| game/ui/screens/per_player_ui_state.py | Read ✓ |
| game/ui/screens/planet_abilities_controller.py | Read ✓ |
| game/ui/screens/planet_data_source.py | Read ✓ |
| game/ui/screens/planet_list_helpers.py | Read ✓ |
| game/ui/screens/planet_menu_items.py | Read ✓ |
| game/ui/screens/planet_selection_window.py | Read ✓ |
| game/ui/screens/race_setup/delegate_factory.py | Read ✓ |
| game/ui/screens/race_setup/llm_dialog_service.py | Read ✓ |
| game/ui/screens/save_selection_window.py | Read ✓ |
| game/ui/screens/setup_data_io.py | Read ✓ |
| game/ui/screens/setup_renderer.py | Read ✓ |
| game/ui/screens/star_list_window.py | Read ✓ |
| game/ui/screens/strategy_camera_nav.py | Read ✓ |
| game/ui/screens/strategy_menu_panel.py | Read ✓ |
| game/ui/screens/strategy_render/background.py | Read ✓ |
| game/ui/screens/strategy_render/cursor.py | Read ✓ |
| game/ui/screens/strategy_render/grid.py | Read ✓ |
| game/ui/screens/strategy_screen_assets.py | Read ✓ |
| game/ui/screens/strategy_screen_order_editing.py | Read ✓ |
| game/ui/screens/strategy_screen_selection.py | Read ✓ |
| game/ui/screens/strategy_superweapons.py | Read ✓ |
| game/ui/screens/strategy_windows/build_queue_windows.py | Read ✓ |
| game/ui/screens/strategy_windows/event_log_window_ctrl.py | Read ✓ |
| game/ui/screens/strategy_windows/move_choice_dialog.py | Read ✓ |
| game/ui/screens/test_lab/component_dropdown.py | Read ✓ |
| game/ui/screens/test_lab/details/__init__.py | Read ✓ |
| game/ui/screens/test_lab/details/validation.py | Read ✓ |
| game/ui/screens/test_lab/formatting_utils.py | Read ✓ |
| game/ui/screens/test_lab/renderer/header_panel.py | Read ✓ |
| game/ui/screens/test_lab/renderer/tag_filter_panel.py | Read ✓ |
| game/ui/screens/test_lab/results_panel.py | Read ✓ |
| game/ui/screens/test_lab/screen_input_handler.py | Read ✓ |
| game/ui/screens/test_lab/test_executor.py | Read ✓ |
| game/ui/screens/test_lab/theme.py | Read ✓ |
| game/ui/screens/workshop_context.py | Read ✓ |
| game/ui/screens/workshop_viewmodel_ship_ops.py | Read ✓ |
| game/ui/services/__init__.py | Read ✓ |
| game/ui/services/design_loader_adapter.py | Read ✓ |
| game/ui/services/ship_factory.py | Read ✓ |
| game/ui/services/ship_io.py | Read ✓ |
| game/ui/utils/formatters.py | Read ✓ |
| game/ui/utils/json_diff.py | Read ✓ |
| game/ui/widgets/dropdown_helper.py | Read ✓ |
| game/ui/widgets/scrollable_json_panel.py | Read ✓ |
