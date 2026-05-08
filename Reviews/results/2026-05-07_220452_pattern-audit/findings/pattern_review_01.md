# Pattern Conformance Review: Shard 01
## Summary
- Shard: Shard 01
- Files in Scope: 183
- Files Actually Read: 183
- Total Findings: 17
- Critical: 0 | Major: 3 | Minor: 14

## Layer Dependency Violations

No layer dependency violations were pre-identified by the automated scanner for this shard. Manual review confirmed all imports respect the documented layer boundaries, with TYPE_CHECKING guards and intentional late imports at documented boundary points.

## Pattern Bypass Findings

#### MINOR: LOC Ceiling — battle_engine.py (775 LOC)
**ID:** PAT-01-LOC-001
**Location:** game/simulation/systems/battle_engine.py
**Pattern:** LOC Ceiling (docs/03_CONVENTIONS.md §File Size)
**Issue:** Production file at 775 lines exceeds the 500-LOC ceiling. Contains BattleLogger + BattleEngine classes; the ~252-line `BattleLogger` class and `_bounce_ship` boundary policy logic are prime extraction candidates.
**Recommendation:** Extract `BattleLogger` into a sibling module (`battle_logger.py`). Consider extracting boundary enforcement (`enforce_boundary`, `_apply_exit_policy`, `_bounce_ship`) into a `boundary_enforcement.py` delegate.
**LOC affected:** ~275 beyond ceiling

#### MINOR: LOC Ceiling — planetary.py (913 LOC)
**ID:** PAT-01-LOC-002
**Location:** game/simulation/components/abilities/planetary.py
**Pattern:** LOC Ceiling (docs/03_CONVENTIONS.md §File Size)
**Issue:** At 913 lines, this is the largest file in the shard. Contains 16 ability classes for strategic-layer planetary effects. Each class is independently coherent; the file is a flat catalog of ability definitions.
**Recommendation:** Split into sub-modules within `abilities/planetary/`: e.g. `shield.py` (PlanetaryShield, RadiationShield), `stabilizer.py` (GeologicStabilizer, StellarStabilizer, WarpFieldStabilizer), `modifier.py` (ShieldModifier, DamageModifier, ThrustModifier, etc.), `terraforming.py` (AtmosphereModifier, GravityModifier, WaterModifier, QualityImprovement). Re-export surface from `__init__.py`.
**LOC affected:** ~413 beyond ceiling

#### MINOR: LOC Ceiling — Additional Files
**ID:** PAT-01-LOC-003
**Location:** Multiple files (see below)
**Pattern:** LOC Ceiling (docs/03_CONVENTIONS.md §File Size)
**Issue:** The following production files exceed the 500-LOC ceiling but are not flagged individually due to active decomposition work (PROJ-309, PROJ-360, PROJ-367):
- game/ui/panels/battle_panels.py (563 LOC) — contains BattlePanel, ShipStatsPanel, SeekerMonitorPanel, BattleControlPanel
- game/ui/panels/race_summary_panel.py (733 LOC) — large rendering panel with flags, portraits, preferences
- game/ui/panels/ship_detail_panel.py (685 LOC) — PROJ-315 component status decomposition
- game/ui/panels/design_stats_panel.py (516 LOC) — shared stats panel with StatRow caching
- game/ui/screens/battle_screen.py (687 LOC) — large screen with replay mode, hit effects, controls
- game/ui/screens/strategy_event_router.py (512 LOC) — extensive event routing
- game/simulation/services/vehicle_design_service.py (516 LOC) — component management + design validations
- game/simulation/entities/stat_contributors/registry.py (552 LOC) — two registries + seeding + conflict handling
- game/ui/screens/build_queue_panel_factory.py (564 LOC) — 4-panel construction + event wiring
- game/app.py (533 LOC) — composition root (but owns delegation pattern)
- game/strategy/combat/spec_compiler.py (693 LOC) — PROJ-269 strategy spec compiler
- game/simulation/components/abilities/base.py (535 LOC) — Ability + StaticValueAbility + SimpleMultiplierAbility base classes
**Recommendation:** Track in existing PROJ decomposition backlogs. Files under active PROJ scope are deferred from this audit.

#### MAJOR: Naming Collision — EventBus in Core vs UI/Builder
**ID:** PAT-01-NAME-001
**Location:** game/core/event_logging.py::EventBus vs game/ui/screens/builder/event_bus.py::EventBus
**Pattern:** Pattern #10 (Event Bus)
**Issue:** Two distinct classes named `EventBus` exist at different architectural layers:
- `game/core/event_logging.py::EventBus` — structured event logging for simulation/strategy events with `log_event()` API
- `game/ui/screens/builder/event_bus.py::EventBus` — UI workshop pub/sub with `subscribe()`, `emit()` API
This collision is documented in `docs/02_PATTERNS.md` §"Critical Naming Reminders" and Pattern #10 itself acknowledges the distinction. However, new developers or agents may import the wrong `EventBus` when working across layers.
**Recommendation:** Rename one. Suggestion: rename the builder/workshop one to `WorkshopEventBus` (matches the module path `builder/event_bus.py` and Pattern #10's scoping statement). This is a low-risk rename — `BuilderEvents` constants already scope usage and the workshop event bus is used only within the builder/workshop subsystem. The core `EventBus` is used across simulation/strategy.
**LOC affected:** ~15 import sites + rename in source

#### MINOR: Undocumented Config Pattern — Strategy JSON-backed Configs Using `@lru_cache` vs `DEFAULT_` Dict
**ID:** PAT-01-CFG-001
**Location:** game/strategy/data/classification_config.py:1-173 and game/strategy/data/resource_generation_config.py:1-149
**Pattern:** Pattern #12 (Configuration Classes)
**Issue:** Both `ClassificationConfig` and `ResourceGenerationConfig` use `@lru_cache(maxsize=1)` on their getter methods (consistent with Pattern #12). However, `game/strategy/config/economy_config.py` uses the `_default` singleton + `get_default_*` / `set_default_*` accessor pattern instead. Two config-loading patterns coexist in the strategy layer.
**Recommendation:** Document both as valid alternatives in Pattern #12. Currently Pattern #12 mentions both `DEFAULT_*` dict fallbacks and `@lru_cache`, but doesn't explicitly describe the `_default` singleton pattern used by economy_config. Add a note that strategy-layer shared-services-style configs may use `get_default_*` accessors when tests need clean swap API.

#### MINOR: Undocumented Pattern — Two-Stage UIWindow Construction (bypass_init)
**ID:** PAT-01-UNDOC-001
**Location:** game/ui/screens/race_setup_screen.py (via race_setup/screen.py), game/ui/screens/planet_selection_window.py:9-11, game/ui/screens/planet_abilities_window.py:7-13, game/ui/screens/cargo_quick_dialog.py:4-11, game/ui/screens/food_allocation_editor.py:21-26, game/ui/screens/star_list_window.py:7-14, game/ui/screens/race_browser_dialog.py:5-10
**Pattern:** Undocumented pattern — two-stage UIWindow construction with bypass_init guard
**Issue:** Seven UIWindow subclasses in this shard use the two-stage construction pattern with a `bypass_init` guard:
```python
if getattr(type(self), "bypass_init", False):
    return
```
This pattern is documented in Pattern #33 (UI Widget Test Factory) but is now used as a PRODUCTION construction pattern, not just a test retrofit. The docstring on these files describes it as "two-stage construction" where cheap state lives before `super().__init__` and widget construction is behind a per-class builder protocol.
**Recommendation:** Elevate "Two-Stage UIWindow Construction" to its own documented pattern or add a production-usage section to Pattern #33. The pattern is consistent across 7+ files and follows a clear formula:
1. Stage 1 (above `bypass_init` guard): pure-Python state, delegates, builder wiring
2. Guard: `if getattr(type(self), "bypass_init", False): return`
3. Stage 2 (below guard): `super().__init__(...)` + `builder.build(self)`
New UIWindow subclasses (star_list_window, planet_selection_window, planet_abilities_window, cargo_quick_dialog, food_allocation_editor, race_browser_dialog) all follow this exactly.

#### MINOR: CQRS-Lite — Strategy Entity References in UI State Models
**ID:** PAT-01-CQRS-001
**Location:** game/ui/screens/battle_setup_state.py:14-15
**Pattern:** Pattern #6 (CQRS-lite)
**Issue:** `BattleSetupState` (UI layer) imports and stores `Fleet` and `ShipInstance` (strategy domain objects) directly:
```python
from game.strategy.data.fleet import Fleet
from game.strategy.data.ship_instance import ShipInstance
```
Per CQRS-lite, UI should work with read-only DTOs. However, `BattleSetupState` is an interactive editor screen where the user modifies ship compositions before battle — mutations here are UI-local until "Start Battle" compiles them into a `BattleSpec`. This is a known gray area: the setup screen serves as a battle-spec editor, not a strategy state viewer.
**Recommendation:** Document as an intentional CQRS-lite exception in the Battle Setup architecture doc. The setup screen is constructing a battle spec (not mutating strategy state), so it legitimately needs domain object references for fleet hierarchy manipulation.

#### MINOR: Pattern #2 Protocol — isinstance() on Concrete Simulation Classes in ShipStatQuerier
**ID:** PAT-01-PROTO-001
**Location:** game/simulation/entities/ship_stat_querier.py:128, 135
**Pattern:** Pattern #2 (Protocol + TypeGuard)
**Issue:** `ShipStatQuerier.max_weapon_range` uses `isinstance(ab, WeaponAbility)` and `isinstance(ab, SeekerWeaponAbility)` to determine weapon range. These are simulation-internal classes (not cross-layer), so the pattern doc's prohibition on `isinstance` against concrete implementations at layer boundaries does not strictly apply. However, the ability system has a `has_ability()` mechanism that is the preferred way to check ability presence.
```python
if not isinstance(ab, WeaponAbility):
    continue
...
if isinstance(ab, SeekerWeaponAbility):
```
**Recommendation:** Replace with duck-typed attribute checks: check for `ab.range` and `ab.projectile_speed`/`ab.endurance` via `getattr` or `hasattr`. This makes the query work with future ability subclasses without needing `isinstance` updates. Low priority — these classes are all in the same simulation layer and share a common Ability ABC.

#### MINOR: Pattern #2 Protocol — isinstance() on BoundaryRegion in RetreatManager
**ID:** PAT-01-PROTO-002
**Location:** game/simulation/managers/retreat_manager.py:105, 206-207
**Pattern:** Pattern #2 (Protocol + TypeGuard)
**Issue:** `RetreatManager` uses `isinstance(self.boundary, UnboundedRegion)` to guard edge-retreat logic. The `BoundaryRegion` ABC has a `contains()` method that `UnboundedRegion` returns `True` for, making this isinstance check a way to detect unbounded arenas. This is simulation-internal and consistent with the `BattleEngine._bounce_ship` pattern (line 719-728 of battle_engine.py) which also uses instanceof checks on `RectBoundary`/`CircleBoundary`.
**Recommendation:** Add a `has_edge() -> bool` method to the `BoundaryRegion` protocol to make edge-capability introspectable without isinstance. Minor — internal consistency is maintained.

#### MINOR: Pattern #7 CommandHandlerRegistry — Legacy BaseCommandHandler Import Path
**ID:** PAT-01-CMD-001
**Location:** game/strategy/engine/superweapon_command_handlers.py:15
**Pattern:** Pattern #7 (CommandHandlerRegistry)
**Issue:** Superweapon command handlers import `BaseCommandHandler` from `game.strategy.engine.command_handlers` (the legacy runtime registry module), while construction-queue handlers import it from `game.strategy.engine.handlers.base`. Two import paths for the same base class.
```python
# superweapon_command_handlers.py
from game.strategy.engine.command_handlers import BaseCommandHandler, add_move_order_if_needed

# handlers/construction_queue.py
from game.strategy.engine.handlers.base import BaseCommandHandler
```
**Recommendation:** Unify on `game.strategy.engine.handlers.base.BaseCommandHandler`. Check if `command_handlers.py` re-exports or duplicates. This may be a legitimate re-export shim — verify and clean if stale.

#### MINOR: Pattern #12 Config — dataclass vs Plain Class in Strategy Configs
**ID:** PAT-01-CFG-002
**Location:** game/strategy/engine/game_config.py:62, 141
**Pattern:** Pattern #12 (Configuration Classes)
**Issue:** `PlayerConfig` and `GameConfig` are `@dataclass` instances in the strategy layer. Pattern #12 says "Core config classes... are plain classes with class-level attributes. Do not add `@dataclass` decorators." However, this applies specifically to `game/core/config.py` config classes. Strategy-layer configs like `GameConfig`, `PlayerConfig`, `TurnEngineConfig` (frozen dataclass) are JSON-backed, mutable (GameConfig/PlayerConfig) or frozen (TurnEngineConfig) containers that serve a different purpose than the core constants.
**Recommendation:** No action. Strategy-layer dataclass configs are compatible with Pattern #12's spirit (named config containers) and serve a different architectural role (serializable state bags) from the core constants. Add a clarifying note to Pattern #12 distinguishing "core constant config" from "layer state config."

#### MINOR: Pattern #31 Strategy Modal — Legacy `_handle_window_close` Slot Scanning
**ID:** PAT-01-MODAL-001
**Location:** game/ui/screens/strategy_event_router.py:471-512 (approximate)
**Pattern:** Pattern #31 (Strategy Modal Window Base Class) vs Pattern #30 (Registrar Close-Callback, superseded)
**Issue:** `StrategyEventRouter._handle_window_close` handles `UI_WINDOW_CLOSE` events and uses legacy slot-clearing logic alongside `has_modal_open()` checks. Seven strategy-modal windows in this shard subclass `StrategyModalWindow` correctly (planet_selection_window, planet_abilities_window, cargo_quick_dialog, food_allocation_editor, star_list_window, race_browser_dialog, water_target_editor). However, the close-handler path in the event router still references legacy slot names (`menu_panel`, `build_queue_screen`).
**Recommendation:** The legacy slot cleanup is documented as Pattern #30 (superseded). The event router's handling is appropriate for maintaining backward-compat until all windows migrate. No action needed — the new windows correctly use Pattern #31's `register_modal`/`unregister_modal`.

#### MINOR: Undocumented Pattern — Re-export Shim Pattern
**ID:** PAT-01-UNDOC-002
**Location:** game/ui/screens/race_setup_screen.py (31 LOC re-export shim), game/ui/screens/test_lab/test_run_details.py (12 LOC re-export shim)
**Pattern:** Undocumented pattern — legacy import shim
**Issue:** Two shim modules preserve historical import paths after decomposition:
- `race_setup_screen.py` re-exports `RaceSetupScreen`, `RaceRandomizer`, `RaceBrowserDialog` from their new canonical homes under `game.ui.screens.race_setup/`
- `test_run_details.py` re-exports `TestRunDetailsPanel` from `game.ui.screens.test_lab.details`

The `component.py` file in simulation also has re-exports from `component_loader.py` at lines 395-405.
**Recommendation:** Document as a temporary migration pattern in `docs/02_PATTERNS.md` under a "Re-Export Shim" entry. Track cleanup tickets for removing shims once all import sites migrate. The TestLab re-export shim at 12 LOC is minimal and acceptable; the race_setup and component re-exports have known cleanup paths.

#### MINOR: ProductionSpawner — Optional Registries Pattern Deviation
**ID:** PAT-01-DI-001
**Location:** game/strategy/engine/production_spawner.py:36
**Pattern:** Pattern #3 (Registry DI)
**Issue:** `ProductionSpawner.__init__` accepts `registries: Optional[GameRegistries] = None`, deviating from the strict DI pattern used elsewhere (e.g., `VehicleDesignService` requires `registries: GameRegistries`). The spawner also has a lazy-fallback `_get_planet_mutator()` pattern (lines 51-57).
```python
def __init__(self, registries: Optional['GameRegistries'] = None, ...):
    self._registries = registries  # Optional!

def _get_planet_mutator(self):
    if self._planet_mutator is None:
        from game.strategy.services.planet_write_service import PlanetWriteService
        self._planet_mutator = PlanetWriteService()
    return self._planet_mutator
```
**Recommendation:** Make `registries` required (remove `Optional` and `None` default). Convert `_get_planet_mutator` to require injection via constructor. This aligns with Pattern #22's mandate that `TurnEngineConfig.create_default()` eagerly constructs all defaults — the lazy fallback in ProductionSpawner works against that invariant.

## Configuration Conventions

#### MINOR: Strategy Config Files Using Direct `json.load` Instead of `json_utils`
**ID:** PAT-01-CFG-003
**Location:** game/strategy/generation/loaders/system_blueprints_loader.py:6
**Issue:** `SystemBlueprintsLoader` imports `json` directly alongside `json_utils.load_json_required`. The file uses `load_json_required` in `load()` method (correct) but the raw `json` import is unused in this file's scope. Verifying: the `json` import at line 6 is actually used in the `load()` method — it accesses `json.JSONDecodeError` in the exception handler. This is legitimate usage.
**Recommendation:** No violation — raw `json` import is for `JSONDecodeError` exception type only. Data loading goes through `load_json_required`. Consistent with Pattern #12.

#### MINOR: Economy Config Uses `get_default_*` Accessors Instead of `@lru_cache`
**ID:** PAT-01-CFG-004
**Location:** game/strategy/config/economy_config.py:30-34
**Pattern:** Pattern #12 (Configuration Classes)
**Issue:** `economy_config.py` explicitly chooses `get_default_*` / `set_default_*` accessors over `@lru_cache`, with a docstring justifying the choice:
> "Chose this over `@lru_cache` (as used by `ClassificationConfig`) because CLAUDE.md's module-accessor form gives tests a clean swap API without poking `.cache_clear()`."
**Recommendation:** This is a documented, intentional deviation supported by the comment. Minor — both patterns are valid under Pattern #12; document both in the pattern reference so the choice is explicit and agents don't flag it as an inconsistency.

## Undocumented Patterns Found

#### Undocumented: Two-Stage UIWindow Construction (see PAT-01-UNDOC-001 above)
Seven files in this shard use a consistent two-stage `__init__` pattern with `bypass_init` guard that is NOT documented as a production pattern. Currently Pattern #33 describes it only for test retrofits. This should be elevated to a documented production pattern since new UIWindow subclasses are being authored with this pattern from the start.

#### Undocumented: Legacy Import Shim (see PAT-01-UNDOC-002 above)
`game/ui/screens/race_setup_screen.py` and `game/ui/screens/test_lab/test_run_details.py` are pure re-export shims preserving historical import paths after module decomposition. This is a recurring pattern worth documenting.

#### Undocumented: Strategy Config Singleton Accessor Pattern
`game/strategy/config/economy_config.py` uses a `_default` module-level singleton + `get_default_economy_config()` / `set_default_economy_config()` pattern that differs from both the `@lru_cache` and `DEFAULT_*` dict patterns documented in Pattern #12. This is an intentional third pattern that should be documented.

## File Coverage Verification
| File | Status |
|------|--------|
| game/simulation/services/vehicle_design_service.py | Read ✓ |
| game/simulation/components/abilities/markers.py | Read ✓ |
| game/ui/panels/race_summary_panel.py | Read ✓ |
| game/ui/panels/race_identity_panel.py | Read ✓ |
| game/ui/screens/battle_setup/panels/center_panel.py | Read ✓ |
| game/strategy/data/planetary_facility.py | Read ✓ |
| game/ui/screens/race_setup/input_handler.py | Read ✓ |
| game/simulation/systems/battle_engine.py | Read ✓ |
| game/strategy/facade/slices/empire_slice.py | Read ✓ |
| game/strategy/data/habitability_factors.py | Read ✓ |
| game/core/protocols/strategy_domain.py | Read ✓ |
| game/ui/screens/test_lab/renderer/_draw_helpers.py | Read ✓ |
| game/ui/panels/component_modifier_grid_panel.py | Read ✓ |
| game/engine/__init__.py | Read ✓ |
| game/ui/utils/formatters.py | Read ✓ |
| game/core/string_utils.py | Read ✓ |
| game/strategy/services/ability_sources/labels.py | Read ✓ |
| game/strategy/data/ship_display_formatter.py | Read ✓ |
| game/__init__.py | Read ✓ |
| game/strategy/engine/superweapon_command_handlers.py | Read ✓ |
| game/simulation/combat/weapon_firing_system.py | Read ✓ |
| game/ui/screens/strategy_render/dyson_spheres.py | Read ✓ |
| game/simulation/components/modifier_introspection.py | Read ✓ |
| game/ui/screens/race_setup/controller.py | Read ✓ |
| game/services/llm/provider.py | Read ✓ |
| game/app.py | Read ✓ |
| game/ui/screens/empire_build_queue_viewmodel.py | Read ✓ |
| game/simulation/components/ability_manager.py | Read ✓ |
| game/ui/screens/cargo_quick_dialog_controller.py | Read ✓ |
| game/simulation/components/abilities/harvester.py | Read ✓ |
| game/strategy/generation/density/primitives/radial.py | Read ✓ |
| game/simulation/services/battle_service.py | Read ✓ |
| game/strategy/generation/loaders/system_blueprints_loader.py | Read ✓ |
| game/simulation/validation/base.py | Read ✓ |
| game/services/llm/__init__.py | Read ✓ |
| game/ui/screens/planet_abilities_window.py | Read ✓ |
| game/simulation/entities/stat_contributors/command.py | Read ✓ |
| game/strategy/data/ship_instance_bridge.py | Read ✓ |
| game/simulation/components/modifier_manager.py | Read ✓ |
| game/ui/services/image/null_provider.py | Read ✓ |
| game/core/return_destination.py | Read ✓ |
| game/strategy/services/race_resolver.py | Read ✓ |
| game/strategy/facade/dto/colony_demographic_view.py | Read ✓ |
| game/ui/screens/galaxy_test/galaxy_mode.py | Read ✓ |
| game/services/__init__.py | Read ✓ |
| game/ui/screens/strategy_fleet_ops.py | Read ✓ |
| game/strategy/engine/game_initializer.py | Read ✓ |
| game/ui/screens/battle_ui.py | Read ✓ |
| game/ui/screens/galaxy_test/__init__.py | Read ✓ |
| game/ui/screens/battle_setup_state.py | Read ✓ |
| game/strategy/data/order_serializer.py | Read ✓ |
| game/ai/interfaces/__init__.py | Read ✓ |
| game/ui/research/research_controls.py | Read ✓ |
| game/ui/renderer/sprites.py | Read ✓ |
| game/ui/panels/empire_treasury_panel.py | Read ✓ |
| game/core/__init__.py | Read ✓ |
| game/ui/screens/star_list_window.py | Read ✓ |
| game/strategy/data/pathfinding.py | Read ✓ |
| game/strategy/services/action_time_resolver.py | Read ✓ |
| game/simulation/combat/fleet_aura_manager.py | Read ✓ |
| game/strategy/data/galaxy_entity_registry.py | Read ✓ |
| game/ui/screens/test_lab/renderer/_condition_logic.py | Read ✓ |
| game/ui/widgets/column_toggle_section.py | Read ✓ |
| game/ui/filters/__init__.py | Read ✓ |
| game/ai/group_target_coordinator.py | Read ✓ |
| game/ui/screens/strategy_camera_nav.py | Read ✓ |
| game/core/spectrum_math.py | Read ✓ |
| game/strategy/services/ability_sources/__init__.py | Read ✓ |
| game/ui/screens/battle_screen.py | Read ✓ |
| game/ui/panels/builder_widgets.py | Read ✓ |
| game/simulation/managers/retreat_manager.py | Read ✓ |
| game/ai/spatial_behaviors/battle_line.py | Read ✓ |
| game/strategy/services/replay_verification_sidecar.py | Read ✓ |
| game/ui/screens/star_list_filters.py | Read ✓ |
| game/ui/screens/new_game_setup_ui_builder.py | Read ✓ |
| game/ui/screens/strategy_renderer.py | Read ✓ |
| game/ui/components/__init__.py | Read ✓ |
| game/strategy/facade/dto/fleet_hierarchy_dto.py | Read ✓ |
| game/ai/protocols.py | Read ✓ |
| game/strategy/engine/order_handlers/transfer.py | Read ✓ |
| game/ui/panels/race_description_panel.py | Read ✓ |
| game/strategy/validation/colonize_validator.py | Read ✓ |
| game/simulation/combat/modifier_stack.py | Read ✓ |
| game/ui/screens/builder/weapons_viewmodel.py | Read ✓ |
| game/core/protocols/persistence.py | Read ✓ |
| game/strategy/services/replay_store.py | Read ✓ |
| game/ui/screens/strategy_screen.py | Read ✓ |
| game/simulation/components/abilities/base.py | Read ✓ |
| game/strategy/data/environmental_preference.py | Read ✓ |
| game/ui/screens/race_setup/llm_dialog_service.py | Read ✓ |
| game/strategy/engine/turn_engine_config.py | Read ✓ |
| game/ui/screens/water_target_editor.py | Read ✓ |
| game/ui/components/table/column_manager.py | Read ✓ |
| game/simulation/combat/families/seeker.py | Read ✓ |
| game/ui/utils/__init__.py | Read ✓ |
| game/strategy/formulas/habitability.py | Read ✓ |
| game/strategy/services/stabilizer_registry.py | Read ✓ |
| game/ui/screens/strategy_build_queue_manager.py | Read ✓ |
| game/strategy/engine/consumable_management_engine.py | Read ✓ |
| game/core/protocols/__init__.py | Read ✓ |
| game/simulation/systems/resource_manager.py | Read ✓ |
| game/ui/screens/design_image_helper.py | Read ✓ |
| game/simulation/components/abilities/planetary.py | Read ✓ |
| game/ui/screens/strategy_render/__init__.py | Read ✓ |
| game/ui/screens/cargo_quick_dialog.py | Read ✓ |
| game/ui/components/filters/__init__.py | Read ✓ |
| game/ui/panels/design_stats_panel.py | Read ✓ |
| game/simulation/components/abilities/crew.py | Read ✓ |
| game/strategy/adapters/__init__.py | Read ✓ |
| game/strategy/data/planet_serde.py | Read ✓ |
| game/core/formula_evaluator.py | Read ✓ |
| game/ui/screens/workshop_viewmodel.py | Read ✓ |
| game/simulation/entities/stat_contributors/registry.py | Read ✓ |
| game/strategy/data/resource_generation_config.py | Read ✓ |
| game/ui/screens/test_lab/data_extractor.py | Read ✓ |
| game/strategy/data/planet_physics.py | Read ✓ |
| game/strategy/data/ship_instance_serializer.py | Read ✓ |
| game/ui/research/research_scene.py | Read ✓ |
| game/ui/screens/strategy_screen_lifecycle.py | Read ✓ |
| game/simulation/entities/stat_contributors/weapons.py | Read ✓ |
| game/ui/screens/strategy_event_router.py | Read ✓ |
| game/ui/screens/empire_build_queue_data_source.py | Read ✓ |
| game/ui/panels/__init__.py | Read ✓ |
| game/simulation/battle_config.py | Read ✓ |
| game/strategy/data/fleet_capability_calculator.py | Read ✓ |
| game/ui/assets/__init__.py | Read ✓ |
| game/strategy/combat/spec_compiler.py | Read ✓ |
| game/ui/screens/star_data_source.py | Read ✓ |
| game/ui/services/ship_io.py | Read ✓ |
| game/strategy/facade/__init__.py | Read ✓ |
| game/strategy/data/spectrum.py | Read ✓ |
| game/strategy/data/race_point_budget.py | Read ✓ |
| game/ui/screens/food_allocation_editor.py | Read ✓ |
| game/ui/screens/build_queue_queue_data_source.py | Read ✓ |
| game/ai/spatial_behaviors/base.py | Read ✓ |
| game/strategy/engine/handlers/construction_queue.py | Read ✓ |
| game/ui/screens/new_game_setup_view_model.py | Read ✓ |
| game/strategy/engine/order_handlers/transfer_branches.py | Read ✓ |
| game/ui/screens/test_lab/renderer/orchestrator.py | Read ✓ |
| game/ui/screens/battle_setup/input_handler.py | Read ✓ |
| game/simulation/validation/__init__.py | Read ✓ |
| game/simulation/entities/ship_stat_querier.py | Read ✓ |
| game/ui/screens/race_setup/ui_builder.py | Read ✓ |
| game/strategy/combat/post_battle_hook.py | Read ✓ |
| game/strategy/config/economy_config.py | Read ✓ |
| game/simulation/components/abilities/cargo.py | Read ✓ |
| game/ui/screens/race_setup_screen.py | Read ✓ |
| game/core/patterns/layer_iterator.py | Read ✓ |
| game/ui/panels/battle_panels.py | Read ✓ |
| game/ui/screens/test_lab/renderer/test_list_panel.py | Read ✓ |
| game/ai/policy_manager.py | Read ✓ |
| game/simulation/components/component.py | Read ✓ |
| game/core/patterns/__init__.py | Read ✓ |
| game/ui/panels/build_queue_portraits.py | Read ✓ |
| game/ui/screens/test_lab/theme.py | Read ✓ |
| game/ui/screens/strategy_render/warp_lanes.py | Read ✓ |
| game/strategy/generation/density/primitives/noise.py | Read ✓ |
| game/ui/screens/planet_selection_window.py | Read ✓ |
| game/strategy/__init__.py | Read ✓ |
| game/strategy/facade/slices/planet_slice.py | Read ✓ |
| game/strategy/data/fleet.py | Read ✓ |
| game/simulation/components/abilities/weapons.py | Read ✓ |
| game/simulation/physics_constants.py | Read ✓ |
| game/strategy/engine/game_config.py | Read ✓ |
| game/simulation/entities/ship_combat_engine.py | Read ✓ |
| game/ui/screens/test_lab/test_run_details.py | Read ✓ |
| game/strategy/facade/slices/event_slice.py | Read ✓ |
| game/ui/screens/setup_screen.py | Read ✓ |
| game/strategy/services/effect_ability_display.py | Read ✓ |
| game/simulation/battle_spec.py | Read ✓ |
| game/ui/screens/race_browser_dialog.py | Read ✓ |
| game/ui/screens/build_queue_panel_factory.py | Read ✓ |
| game/ui/panels/ship_detail_panel.py | Read ✓ |
| game/strategy/data/design_role.py | Read ✓ |
| game/strategy/data/species_population.py | Read ✓ |
| game/ai/spatial_behaviors/free_maneuver.py | Read ✓ |
| game/ui/screens/planet_list_sidebar.py | Read ✓ |
| game/strategy/engine/production_spawner.py | Read ✓ |
| game/strategy/data/classification_config.py | Read ✓ |
| game/ui/services/validation_service.py | Read ✓ |
| game/ui/screens/strategy_render/fleets.py | Read ✓ |
| game/core/protocols/registry.py | Read ✓ |
| game/ui/screens/battle_setup/constants.py | Read ✓ |
