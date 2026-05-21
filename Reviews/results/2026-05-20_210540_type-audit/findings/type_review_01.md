# Type Safety Review: Shard 01
## Summary
- Files in Scope: 184
- Files Actually Read: 184
- Total Findings: 111
- Critical: 1 | Major: 14 | Minor: 62 | Info: 34

---

## Narrowable Any Returns

### Pattern A: Protocols with `-> Any` (Unavoidable — INFO)
Protocol declarations use `-> Any` intentionally to accommodate multiple concrete implementations. These are not narrowable without breaking duck typing.

**INFO**: `game/core/protocols/strategy_entities.py` — 12 Protocol properties returning `Any`:
- `IStarSystem.global_location` (L30), `IStar.star_type` (L64), `IPlanet.planet_type` (L77), `IPlanet.location` (L104), `IPlanet.populations` (L115), `IPlanet.facilities` (L125), `IFleet.location` (L250), `IFleet.capabilities` (L290), `IFleet.resources` (L295), `IFleet.battle` (L300), `IWarpPoint.location` (L313), `ISectorEnvironment.local_hex` (L322), `ISectorEnvironment.system` (L327), `ISectorEnvironment.calculate_radiation` (L331)
- **Justification**: Protocols for duck typing across Strategy/Simulation/UI layers. Concrete types vary by layer context.

**INFO**: `game/core/protocols/ui.py` — 3 Protocol properties/methods returning `Any`:
- `ICamera.position` (L62), `ICamera.world_to_screen` (L66), `ICamera.screen_to_world` (L78)
- **Justification**: Camera protocol for cross-layer decoupling; returns Vector2-like objects.

**INFO**: `game/simulation/interfaces/entity_protocols.py` — 8 Protocol properties returning `Any`:
- `ICombatShip.position` (L88), `ICombatShip.velocity` (L93), `ICombatShip.resources` (L199), `ICombatShip.combat_engine` (L204), `IProjectile.position` (L265), `IProjectile.velocity` (L270), `IProjectile.type` (L304)
- **Justification**: Simulation entity protocols for duck typing.

### Pattern B: Registry/String-Key Dispatch (Unavoidable — INFO)

**TYP-01-001**: `game/core/registry.py:248,339` — `RegistryManager.get_validator()` and module-level `get_validator()` both `-> Any`
- **INFO / Unavoidable**: Validator stored as `Any` attribute; type depends on which validator implementation was cached. The field is intentionally generic because validators are lazily constructed from registries.

### Pattern C: Private Helper Methods with Concrete Returns (Narrowable — MINOR)

**TYP-01-002**: `game/strategy/engine/harvesting_engine.py:196,205` — `_get_planet_mutator() -> Any` and `_get_empire_mutator() -> Any`
- **MINOR**: Returns `PlanetWriteService` and `EmpireWriteService` respectively.
- **Suggested**: `-> PlanetWriteService` and `-> EmpireWriteService`

**TYP-01-003**: `game/strategy/engine/order_handlers/base.py:143,152` — `_get_planet_mutator() -> Any` and `_get_ship_mutator() -> Any`
- **MINOR**: Returns `PlanetWriteService` and `ShipInstanceWriteService` respectively.
- **Suggested**: `-> PlanetWriteService` and `-> ShipInstanceWriteService`

**TYP-01-004**: `game/strategy/engine/handlers/base.py:323` — `_resolve_build_entity() -> Any`
- **MINOR**: Returns `Planet | Fleet | None` depending on entity_type.
- **Suggested**: `-> Planet | Fleet | None`

**TYP-01-005**: `game/strategy/engine/handlers/base.py:377` — `_resolve_queue_owner() -> Any`
- **MINOR**: Returns `Planet | Fleet | PlanetaryFacility | None`.
- **Suggested**: Add concrete union type.

**TYP-01-006**: `game/strategy/engine/handlers/base.py:419` — `_build_colonize_target() -> Any`
- **MINOR**: Returns `Planet | dict[str, Any]`.
- **Suggested**: `-> Planet | dict[str, Any]`

**TYP-01-007**: `game/strategy/services/planet_write_service.py:125` — `pop_construction_item() -> Any`
- **MINOR**: Wraps `list.pop()` on construction queue; items are dicts.
- **Suggested**: `-> dict`

### Pattern D: `_time_phase` in TurnEngine (Unavoidable)

**TYP-01-008**: `game/strategy/engine/turn_engine.py:286` — `_time_phase() -> Any`
- **INFO / Unavoidable**: Returns result of any phase function callable. Result types vary across 15+ phase callbacks.
- **Justification**: Cross-cutting timing/decorator wrapper with polymorphic return.

### Pattern E: Dunder (Exempt)

**TYP-01-009**: `game/strategy/data/stars.py:161` — `__getattr__() -> Any`
- **Exempt**: Dunder method. Provides backward-compatible import of `StarGenerator` from legacy import path. Returns `StarGenerator` class.

### Pattern F: `ComponentStatsCalculator.evaluate_recursive` (Internal)

**TYP-01-010**: `game/simulation/components/component_stats_calculator.py:305` — `evaluate_recursive() -> Any`
- **MINOR**: Nested function returning `str | dict | list | float | int`.
- **Suggested**: `-> str | dict[str, Any] | list[Any] | float | int`

### Pattern G: UI List/Filter Modules (Narrowable — MAJOR)

These are public API functions at the module level with predictable return types. The `-> Any` annotation is unjustified.

**TYP-01-011**: `game/ui/screens/planet_list_filters.py:38` — `gather_planets() -> Any`
- **MAJOR**: Returns `list[Planet]`. Called by `PlanetListWindow`.
- **Suggested**: `-> list[Planet]`

**TYP-01-012**: `game/ui/screens/planet_list_filters.py:174` — `filter_planets() -> Any`
- **MAJOR**: Returns `list[Planet]`.
- **Suggested**: `-> list[Planet]`

**TYP-01-013**: `game/ui/screens/planet_list_filters.py:215` — `sort_planets() -> Any`
- **MAJOR**: Returns `list[Planet]`.
- **Suggested**: `-> list[Planet]`

**TYP-01-014**: `game/ui/screens/planet_list_filters.py:252` — `get_column_value() -> Any`
- **MAJOR**: Returns `str` in all paths.
- **Suggested**: `-> str`

**TYP-01-015**: `game/ui/screens/planet_list_filters.py:280` — `compute_planet_ranges() -> Any`
- **MAJOR**: Returns `dict[str, tuple[float, float]]`.
- **Suggested**: `-> dict[str, tuple[float, float]]`

**TYP-01-016**: `game/ui/screens/planet_list_filters.py:333` — `get_system_name() -> Any`
- **MAJOR**: Returns `str` (or `"?"` fallback).
- **Suggested**: `-> str`

**TYP-01-017**: `game/ui/screens/planet_list_filters.py:348` — `get_owner_name() -> Any`
- **MAJOR**: Returns `str`.
- **Suggested**: `-> str`

### Pattern H: `planet_list_window.py` Properties (Narrowable — MAJOR)

**TYP-01-018**: `game/ui/screens/planet_list_window.py:211,221,231,241` — `filter_types`, `filter_owner`, `filter_effects`, `filter_ranges` properties all `-> Any`
- **MAJOR**: Delegate to `PlanetListFilterManager` which has typed dicts.
- **Suggested**: `filter_types -> dict[str, bool]`, `filter_owner -> dict[str, bool]`, `filter_effects -> dict[str, FilterState]`, `filter_ranges -> dict[str, list[float]]`

**TYP-01-019**: `game/ui/screens/planet_list_window.py:292` — `_capture_current_state() -> Any`
- **MINOR**: Returns `dict` (preset snapshot).
- **Suggested**: `-> dict`

### Pattern I: `star_list_filters.py` (Narrowable — MAJOR)

**TYP-01-020**: `game/ui/screens/star_list_filters.py:20` — `gather_stars() -> Any`
- **MAJOR**: Returns `list[Star]`.
- **Suggested**: `-> list[Star]`

**TYP-01-021**: `game/ui/screens/star_list_filters.py:67` — `filter_stars() -> Any`
- **MAJOR**: Returns `list[Star]`.
- **Suggested**: `-> list[Star]`

**TYP-01-022**: `game/ui/screens/star_list_filters.py:121` — `sort_stars() -> Any`
- **MAJOR**: Returns `list[Star]`.
- **Suggested**: `-> list[Star]`

**TYP-01-023**: `game/ui/screens/star_list_filters.py:163` — `compute_star_ranges() -> Any`
- **MAJOR**: Returns `dict[str, tuple[float, float]]`.
- **Suggested**: `-> dict[str, tuple[float, float]]`

**TYP-01-024**: `game/ui/screens/star_list_filters.py:203` — `get_system_name() -> Any`
- **MAJOR**: Returns `str`.
- **Suggested**: `-> str`

**TYP-01-025**: `game/ui/screens/star_list_filters.py:217` — `get_star_type_display() -> Any`
- **MAJOR**: Returns `str`.
- **Suggested**: `-> str`

### Pattern J: `star_list_window.py` Properties (Narrowable — MAJOR)

**TYP-01-026**: `game/ui/screens/star_list_window.py:277,285` — `filter_types`, `filter_ranges` properties `-> Any`
- **MAJOR**: Delegate to `StarListFilterManager`.
- **Suggested**: Narrow to concrete dict types.

**TYP-01-027**: `game/ui/screens/star_list_window.py:448` — `_capture_current_state() -> Any`
- **MINOR**: Returns `dict`.
- **Suggested**: `-> dict`

### Pattern K: Battle Setup Data I/O (Narrowable — MAJOR)

**TYP-01-028**: `game/ui/screens/setup_data_io.py:34` — `get_base_path() -> Any`
- **MAJOR**: Returns `str` (delegates to `Paths.ROOT_DIR`).

**TYP-01-029**: `game/ui/screens/setup_data_io.py:39` — `scan_ship_designs() -> Any`
- **MAJOR**: Returns `list[dict]`.

**TYP-01-030**: `game/ui/screens/setup_data_io.py:65` — `load_ships_from_entries() -> Any`
- **MAJOR**: Returns `list[Ship]`.

**TYP-01-031**: `game/ui/screens/setup_data_io.py:171` — `load_battle_setup() -> Any`
- **MAJOR**: Returns `tuple[list[dict], list[dict]] | tuple[None, None]`.

**TYP-01-032**: `game/ui/screens/setup_data_io.py:185` — `find_design() -> Any` (nested inside `load_battle_setup`)
- **MINOR**: Returns `dict | None`.

### Pattern L: Setup Renderer/Screen (Narrowable — MAJOR)

**TYP-01-033**: `game/ui/screens/setup_renderer.py:35` — `draw_available_ships() -> Any`
- **MAJOR**: Returns `int` (ships end y coordinate).

**TYP-01-034**: `game/ui/screens/setup_screen.py:133` — `get_team_display_groups() -> Any`
- **MAJOR**: Returns `list[dict[str, Any]]`.

### Pattern M: Builder Stat Getters (Unavoidable — INFO)

**TYP-01-035**: `game/ui/screens/builder/stat_getters.py` — 47 functions returning `-> Any` (L12-389)
- **INFO / Unavoidable**: These are registry-dispatched getter/formatter functions referenced by name from `stats_layout.json`. The dispatch dictionary requires a uniform signature that returns `Any` for flexibility across numeric, string, and formatted values.
- **Justification**: Data-driven dispatch via JSON config; callers use untyped dict lookup. Narrowing would require refactoring the entire registry+JSON system.

**TYP-01-036**: `game/ui/screens/builder/stat_getters.py:456` — `mass_unit_func() -> Any`
- **INFO / Unavoidable**: Same registry pattern; lambda factory for unit display.

**TYP-01-037**: `game/ui/screens/builder/stats_config.py:46` — `load_stats_config() -> Any`
- **INFO / Unavoidable**: Returns JSON-loaded `dict` with stat group definitions. Shape is driven by JSON file.

### Pattern N: Click Dispatcher (Narrowable — MINOR)

**TYP-01-038**: `game/ui/screens/strategy_click_dispatcher.py:53` — `scene` property `-> Any`
- **MINOR**: Returns `StrategyScreen`. But uses circular import avoidance.
- **Suggested**: `-> StrategyScreen` (feasible if TYPE_CHECKING import added).

**TYP-01-039**: `game/ui/screens/strategy_click_dispatcher.py:517` — `_resolve_click_target() -> Any`
- **MINOR**: Returns `HexCoord`.
- **Suggested**: `-> HexCoord`

### Pattern O: ColonizationSystem (Narrowable — MINOR)

**TYP-01-040**: `game/ui/screens/strategy_colonization.py:40,44,48` — `systems`, `camera`, `hex_size` properties `-> Any`
- **MINOR**: Delegate to scene properties. Narrowable with concrete types.

**TYP-01-041**: `game/ui/screens/strategy_colonization.py:224` — `request_colonize_order() -> Any`
- **MINOR**: Returns `dict | None`.

**TYP-01-042**: `game/ui/screens/strategy_colonization.py:246,259` — `_get_system_at_hex() -> Any`, `_resolve_planet_global_hex() -> Any`
- **MINOR**: `_get_system_at_hex` returns `StarSystem | None`. `_resolve_planet_global_hex` returns `HexCoord | None`.

### Pattern P: Event Router (Narrowable — MINOR)

**TYP-01-043**: `game/ui/screens/strategy_event_router.py:336` — `resolve_race() -> Any` (nested callback)
- **MINOR**: Returns `RaceConfig | None`.

**TYP-01-044**: `game/ui/screens/strategy_event_router.py:363` — `_get_race_config() -> Any`
- **MINOR**: Returns `RaceConfig | None`.

### Pattern Q: Battle Setup Controller (Narrowable — MINOR)

**TYP-01-045**: `game/ui/screens/battle_setup/controller.py:411` — `_build_end_condition() -> Any`
- **MINOR**: Returns `IEndCondition` (specifically `AnyCondition`).
- **Suggested**: Import `IEndCondition` and annotate `-> IEndCondition`.

### Pattern R: Dyson Sphere (Narrowable — MINOR)

**TYP-01-046**: `game/ui/screens/strategy_render/dyson_spheres.py:116` — `load_dyson_sphere_image() -> Any`
- **MINOR**: Returns `pygame.Surface | None`.
- **Suggested**: `-> pygame.Surface | None`

### Pattern S: Test Lab (Narrowable — MINOR)

**TYP-01-047**: `game/ui/screens/test_lab/ship_panels.py:183` — `get_selected_ship_info() -> Any`
- **MINOR**: Returns `dict | None`.

### Pattern T: Window `process_event` (Unavoidable — INFO)

**TYP-01-048**: `game/ui/screens/build_queue_list_window.py:210` — `process_event() -> Any`
- **INFO / Unavoidable**: Overrides pygame_gui `UIWindow.process_event()` that returns `bool`. The `-> Any` matches the Pygame event handler pattern where the super call return type is `bool`.
- **Note**: Could be narrowed to `-> bool` since the method always returns `True/False/handled`.

**TYP-01-049**: `game/ui/screens/fleet_report_window.py:248` — `process_event() -> Any`
- **INFO**: Same pygame_gui override pattern. Returns `bool`.

**TYP-01-050**: `game/ui/screens/design_selector_window.py:388` — `_get_role_filter_options() -> Any`
- **MAJOR**: Returns `list[str]` clearly.
- **Suggested**: `-> list[str]`

---

## Missing Return Types (Public API)

### CRITICAL

**TYP-01-051**: `game/ui/screens/strategy_modal_window.py:273`
- **Function**: `check_clicked_inside_or_blocking()`
- **Class**: `StrategyModalWindow`
- **Severity**: **CRITICAL** — Public method overriding `UIWindow.check_clicked_inside_or_blocking()`; used in pygame_gui's event dispatch pipeline. Missing return type on a cross-layer public API override.
- **Suggested**: `-> bool`

### MINOR (Private closures in superweapon handlers)

Note: These are inner functions (closures) defined inside `process_open_warp_point()` and `process_stellerate_star()`. They are not importable module-level functions, so the severity is lower, but they participate in a spec-driven dispatch contract.

**TYP-01-052**: `game/strategy/engine/superweapon_handlers/open_warp_point.py:38`
- **Function**: `_precheck` (closure)
- **Missing**: Return type. Returns `SuperweaponResult | None`.
- **Suggested**: `-> SuperweaponResult | None`

**TYP-01-053**: `game/strategy/engine/superweapon_handlers/open_warp_point.py:54`
- **Function**: `_effect` (closure)
- **Missing**: Return type. Returns `dict[str, str]`.
- **Suggested**: `-> dict[str, str]`

**TYP-01-054**: `game/strategy/engine/superweapon_handlers/stellerate_star.py:47`
- **Function**: `_precheck` (closure)
- **Missing**: Return type.
- **Suggested**: `-> SuperweaponResult | None`

**TYP-01-055**: `game/strategy/engine/superweapon_handlers/stellerate_star.py:54`
- **Function**: `_effect` (closure)
- **Missing**: Return type.
- **Suggested**: `-> dict[str, str]`

### MINOR (Private method in construction_queue handler)

**TYP-01-056**: `game/strategy/engine/handlers/construction_queue.py:106`
- **Function**: `_resolve_design_data()`
- **Class**: `AddToConstructionQueueCommandHandler`
- **Missing**: Return type. Returns `dict | None`.
- **Suggested**: `-> dict | None`

---

## Type Ignore Audit

### Justified

**TYP-01-057**: `game/simulation/battle_runner.py:182,192`
- **Content**: `engine.replay_id: Optional[str] = None  # type: ignore[attr-defined]`
- **Justification**: `replay_id` is dynamically attached to `BattleEngine` at battle start; not a declared attribute on `BattleEngine`. This is intentional dynamic attribute injection for replay capture.

**TYP-01-058**: `game/strategy/systems/save_game_service.py:74,82`
- **Content**: `self._replay_store.set_save_root(...)  # type: ignore[attr-defined]`
- **Justification**: `_replay_store` is typed as `Optional[object]` (a generic duck-typed reference). The actual replay store object has `set_save_root()` and `clear_save_root()` methods that don't exist on `object`. Uses duck typing to avoid hard coupling to the replay module.

### Unjustified

**TYP-01-059**: `game/ui/screens/defeat_dialog.py:83`
- **Content**: `self._dismiss_button = None  # type: ignore[assignment]`
- **Severity**: **MAJOR**
- **Justification**: This is in the `_window_init_bypassed` test path where the real `UIButton` is not created. The field should be declared with an `Optional[UIButton]` type annotation (or initialized to `None` in the class body / `__init__` pre-bypass) instead of relying on `# type: ignore`.
- **Remediation**: Declare `self._dismiss_button: Optional[UIButton] = None` in the constructor before the bypass check.

---

## `cast()` Usage

No `cast()` usages found in this shard. Confirmed 0 across all 184 files.

---

## TYPE_CHECKING Hygiene

All `TYPE_CHECKING` blocks reviewed. No runtime uses of TYPE_CHECKING-only imports detected. The following files use TYPE_CHECKING correct:

- `game/core/registry.py` — `ResourceCatalog` import correct
- `game/core/protocols/strategy_entities.py` — No TYPE_CHECKING block (protocols use runtime imports for `runtime_checkable`)
- `game/strategy/engine/harvesting_engine.py` — `Empire`, `Planet`, `PlanetaryFacility` correct
- `game/strategy/engine/turn_engine.py` — All engine interface and data class imports correct
- `game/strategy/engine/handlers/base.py` — `Fleet`, `Planet`, `GameSession`, `Command` correct
- `game/strategy/engine/order_handlers/base.py` — `Empire`, `Fleet`, `Galaxy` correct
- `game/strategy/services/planet_write_service.py` — `DropPod`, `CarriedVehicle`, `Order`, `Planet` correct
- `game/ui/screens/build_queue_list_window.py` — `InputMapper`, `StrategyWindowManager` correct
- `game/ui/screens/design_selector_window.py` — `DesignMetadata`, `StrategyWindowManager` correct
- `game/ui/screens/fleet_report_window.py` — `StrategyWindowManager` correct
- `game/ui/screens/planet_list_window.py` — `StrategyWindowManager` correct
- `game/ui/screens/star_list_window.py` — `StrategyWindowManager` correct
- `game/ui/screens/star_list_filters.py` — `FacadeSessionState` correct
- `game/ui/screens/planet_list_filters.py` — `FacadeSessionState` correct
- `game/ui/screens/strategy_click_dispatcher.py` — `StrategyInputHandler` correct
- `game/ui/screens/strategy_colonization.py` — `StrategySessionFacade` correct
- `game/ui/screens/strategy_event_router.py` — `StrategyUI` correct
- `game/ui/screens/defeat_dialog.py` — `StrategyWindowManager` correct
- `game/strategy/engine/superweapon_handlers/open_warp_point.py` — `Empire`, `SuperweaponOrderProcessor`, `SuperweaponResult` correct
- `game/strategy/engine/superweapon_handlers/stellerate_star.py` — Same, correct
- `game/simulation/components/component_stats_calculator.py` — `Component`, `ApplicationModifier` correct
- `game/strategy/facade/slices/economy_slice.py` — `IRaceRegistry`, `EconomyConfig`, `FacadeSessionState` correct
- `game/ui/screens/fleet_data_source.py` — `FleetListViewModel`, `ShipInstance` correct
- `game/ui/screens/empire_build_queue_viewmodel.py` — No TYPE_CHECKING block (runtime only)

---

## Deferred Narrowings

No `# type: ignore[no-any-return]` comments or `# TODO: narrow` comments found in this shard.

---

## Protocol Conformance Checks

### `IScene` Protocol (`game/core/protocols/ui.py`)
- `BattleSetupScreen` (`game/ui/screens/setup_screen.py): Implements `handle_event`, `update`, `draw`, `handle_resize`. Conforms.

### `ICombatShip` Protocol (`game/simulation/interfaces/entity_protocols.py`)
- `Ship` (`game/simulation/entities/ship.py` — in this shard): Verified structure matches Protocol's properties: `name`, `team_id`, `vehicle_type`, `angle`, `position`, `velocity`, `radius`, `mass`, `hp`, `max_hp`, `is_alive`, `is_derelict`, `current_shields`, `max_shields`, etc. Conforms via duck typing.

### `IPlanetMutator` Protocol check
- `PlanetWriteService` (`game/strategy/services/planet_write_service.py`): 16 mutation methods covering populations, facilities, stockpile, staging yard, construction queue, orders, scalar fields. All return types are annotated (`-> None`, `-> bool`, etc.). Conforms.

---

## File Coverage Verification

| File | Status |
|------|--------|
| game/simulation/combat/attack_contract.py | Read ✓ |
| game/ui/screens/fleet_data_source.py | Read ✓ |
| game/ui/screens/defeat_dialog.py | Read ✓ |
| game/ui/screens/empire_build_queue_viewmodel.py | Read ✓ |
| game/ui/screens/fleet_report_window.py | Read ✓ |
| game/strategy/services/__init__.py | Read ✓ |
| game/strategy/services/component_abilities.py | Read ✓ |
| game/ui/components/table/header.py | Read ✓ |
| game/strategy/facade/slices/economy_slice.py | Read ✓ |
| game/ui/screens/strategy_event_router.py | Read ✓ |
| game/simulation/components/abilities/vehicle_bay.py | Read ✓ |
| game/strategy/services/replay_resolver.py | Read ✓ |
| game/strategy/services/ability_metadata.py | Read ✓ |
| game/strategy/engine/harvesting_engine.py | Read ✓ |
| game/ui/screens/setup_data_io.py | Read ✓ |
| game/strategy/engine/handlers/construction_queue.py | Read ✓ |
| game/strategy/services/fleet_speed_calculator.py | Read ✓ |
| game/strategy/engine/quality_engine.py | Read ✓ |
| game/core/roles.py | Read ✓ |
| game/ui/screens/builder/stat_getters.py | Read ✓ |
| game/ui/screens/planet_list_filter_manager.py | Read ✓ |
| game/ui/filters/__init__.py | Read ✓ |
| game/simulation/components/ability_manager.py | Read ✓ |
| game/strategy/data/stars.py | Read ✓ |
| game/ui/screens/star_list_sidebar.py | Read ✓ |
| game/ui/screens/planet_abilities_window.py | Read ✓ |
| game/simulation/components/abilities/harvester.py | Read ✓ |
| game/strategy/engine/game_config.py | Read ✓ |
| game/core/input_actions.py | Read ✓ |
| game/simulation/entities/ship_combat_manager.py | Read ✓ |
| game/ui/screens/battle_setup/panels/left_panel.py | Read ✓ |
| game/ui/screens/galaxy_test/__init__.py | Read ✓ |
| game/strategy/data/ship_display_formatter.py | Read ✓ |
| game/ui/screens/test_lab/ship_panels.py | Read ✓ |
| game/strategy/engine/planet_energy_engine.py | Read ✓ |
| game/ui/panels/ship_stats_renderer.py | Read ✓ |
| game/strategy/formulas/colony_output.py | Read ✓ |
| game/ui/screens/strategy_colonization.py | Read ✓ |
| game/strategy/engine/resupply_engine.py | Read ✓ |
| game/ai/spatial_behaviors/__init__.py | Read ✓ |
| game/strategy/facade/slices/fleet_slice.py | Read ✓ |
| game/simulation/entities/ship.py | Read ✓ |
| game/ui/screens/star_list_filters.py | Read ✓ |
| game/strategy/services/replay_store.py | Read ✓ |
| game/simulation/projectile_manager.py | Read ✓ |
| game/ui/screens/setup_renderer.py | Read ✓ |
| game/ui/screens/planet_list_controller.py | Read ✓ |
| game/ui/renderer/game_renderer.py | Read ✓ |
| game/strategy/combat/spec_compiler.py | Read ✓ |
| game/strategy/data/galaxy_warp_generator.py | Read ✓ |
| game/ui/screens/build_queue_input_router.py | Read ✓ |
| game/ui/screens/strategy_modal_window.py | Read ✓ |
| game/strategy/engine/population_engine.py | Read ✓ |
| game/simulation/components/component_stats_calculator.py | Read ✓ |
| game/ui/screens/test_lab/renderer/test_list_panel.py | Read ✓ |
| game/strategy/facade/slices/empire_slice.py | Read ✓ |
| game/strategy/generation/placement_strategies.py | Read ✓ |
| game/ai/fighter_controller.py | Read ✓ |
| game/simulation/battle_outcome.py | Read ✓ |
| game/ui/screens/strategy_build_queue_manager.py | Read ✓ |
| game/ui/colors.py | Read ✓ |
| game/ui/filters/filter_state.py | Read ✓ |
| game/ui/screens/transfer_container_rows.py | Read ✓ |
| game/exit_dialog.py | Read ✓ |
| game/strategy/generation/density/density_map.py | Read ✓ |
| game/ui/screens/build_queue_helpers.py | Read ✓ |
| game/ui/screens/builder/grouping_strategies.py | Read ✓ |
| game/ui/screens/test_lab/results_panel.py | Read ✓ |
| game/strategy/formulas/__init__.py | Read ✓ |
| game/ui/screens/battle_setup/renderer.py | Read ✓ |
| game/ui/screens/battle_setup/input_handler.py | Read ✓ |
| game/ui/services/image/provider.py | Read ✓ |
| game/strategy/data/component_activation_state.py | Read ✓ |
| game/strategy/engine/minefield_balance.py | Read ✓ |
| game/strategy/data/race_point_budget.py | Read ✓ |
| game/ai/ai_factory.py | Read ✓ |
| game/strategy/engine/handlers/transfer.py | Read ✓ |
| game/strategy/engine/order_handlers/base.py | Read ✓ |
| game/ui/screens/battle_setup/controller.py | Read ✓ |
| game/strategy/data/star_generation_config.py | Read ✓ |
| game/strategy/data/race_config.py | Read ✓ |
| game/simulation/systems/resource_manager.py | Read ✓ |
| game/ui/screens/star_list_window.py | Read ✓ |
| game/strategy/services/intercept_calculator.py | Read ✓ |
| game/strategy/engine/handlers/base.py | Read ✓ |
| game/ui/screens/strategy_render/dyson_spheres.py | Read ✓ |
| game/strategy/services/ability_iterator.py | Read ✓ |
| game/strategy/services/fleet_path_projection.py | Read ✓ |
| game/ui/services/ship_io_adapter.py | Read ✓ |
| game/simulation/components/component.py | Read ✓ |
| game/strategy/services/ship_instance_factory.py | Read ✓ |
| game/strategy/services/planet_economy_projector.py | Read ✓ |
| game/ui/screens/test_lab/dialogs.py | Read ✓ |
| game/core/registry.py | Read ✓ |
| game/strategy/systems/save_game_service.py | Read ✓ |
| game/strategy/data/galaxy_spatial_index.py | Read ✓ |
| game/ai/carrier_controller.py | Read ✓ |
| game/simulation/replay/replay_spec.py | Read ✓ |
| game/simulation/combat/modifier_stack.py | Read ✓ |
| game/strategy/data/design_role_registry.py | Read ✓ |
| game/strategy/services/action_time_resolver.py | Read ✓ |
| game/ui/screens/strategy_windows/list_windows.py | Read ✓ |
| game/simulation/entities/ship_design_stats.py | Read ✓ |
| game/simulation/systems/tech_preset_loader.py | Read ✓ |
| game/engine/spatial.py | Read ✓ |
| game/ai/spatial_behaviors/free_maneuver.py | Read ✓ |
| game/simulation/battle_runner.py | Read ✓ |
| game/simulation/replay/replay_serialization.py | Read ✓ |
| game/strategy/data/galaxy.py | Read ✓ |
| game/ui/screens/strategy_render/grid.py | Read ✓ |
| game/strategy/generation/__init__.py | Read ✓ |
| game/core/protocols/strategy_entities.py | Read ✓ |
| game/strategy/formulas/habitability.py | Read ✓ |
| game/ui/screens/design_selector_window.py | Read ✓ |
| game/ui/screens/strategy_click_dispatcher.py | Read ✓ |
| game/strategy/engine/turn_engine_config.py | Read ✓ |
| game/ui/screens/strategy_render/context.py | Read ✓ |
| game/simulation/systems/battle_engine.py | Read ✓ |
| game/strategy/data/race_caption_loader.py | Read ✓ |
| game/ui/screens/build_queue_list_window.py | Read ✓ |
| game/ui/screens/save_selection_window.py | Read ✓ |
| game/strategy/services/fleet_write_service.py | Read ✓ |
| game/ui/screens/planet_list_filters.py | Read ✓ |
| game/ui/services/vehicle_class_service.py | Read ✓ |
| game/ui/screens/planet_list_window.py | Read ✓ |
| game/strategy/engine/conflict_modifier_collection.py | Read ✓ |
| game/ui/screens/builder/weapons_renderer.py | Read ✓ |
| game/strategy/data/galaxy_system_generator.py | Read ✓ |
| game/simulation/components/component_health_manager.py | Read ✓ |
| game/simulation/components/abilities/planetary/resource_modifiers.py | Read ✓ |
| game/strategy/engine/superweapon_handlers/open_warp_point.py | Read ✓ |
| game/services/llm/deepseek.py | Read ✓ |
| game/strategy/services/combat_modifier_collector.py | Read ✓ |
| game/strategy/data/container.py | Read ✓ |
| game/core/__init__.py | Read ✓ |
| game/simulation/components/abilities/crew.py | Read ✓ |
| game/strategy/services/planet_write_service.py | Read ✓ |
| game/ui/screens/battle_results_data.py | Read ✓ |
| game/ui/services/tkinter_utils.py | Read ✓ |
| game/simulation/components/modifier_schema.py | Read ✓ |
| game/ui/components/table/column_manager.py | Read ✓ |
| game/strategy/engine/planet_command_handlers.py | Read ✓ |
| game/simulation/services/vehicle_design_service.py | Read ✓ |
| game/strategy/data/build_queue_source.py | Read ✓ |
| game/strategy/data/__init__.py | Read ✓ |
| game/strategy/systems/race_randomizer.py | Read ✓ |
| game/assets/asset_manager.py | Read ✓ |
| game/simulation/components/abilities/superweapons.py | Read ✓ |
| game/strategy/facade/dto/container_snapshot.py | Read ✓ |
| game/strategy/facade/dto/planet_dto.py | Read ✓ |
| game/simulation/combat/combat_events.py | Read ✓ |
| game/strategy/engine/commands/__init__.py | Read ✓ |
| game/ui/screens/build_queue_renderer.py | Read ✓ |
| game/ui/screens/race_setup/screen.py | Read ✓ |
| game/research/data/tech_tree.py | Read ✓ |
| game/ui/screens/builder/modifier_utils.py | Read ✓ |
| game/simulation/entities/projectile.py | Read ✓ |
| game/strategy/services/fleet_cargo_projector.py | Read ✓ |
| game/ui/screens/race_setup/ship_preview.py | Read ✓ |
| game/ui/screens/builder/stats_config.py | Read ✓ |
| game/ui/services/image/factory.py | Read ✓ |
| game/ui/services/image/defaults.py | Read ✓ |
| game/strategy/data/carried_vehicle.py | Read ✓ |
| game/ui/screens/setup_screen.py | Read ✓ |
| game/ui/screens/planet_selection_window.py | Read ✓ |
| game/ui/screens/race_setup/renderer.py | Read ✓ |
| game/strategy/engine/turn_engine.py | Read ✓ |
| game/strategy/combat/pre_tick_setup/__init__.py | Read ✓ |
| game/strategy/engine/superweapon_handlers/stellerate_star.py | Read ✓ |
| game/strategy/engine/order_handlers/launch_satellites.py | Read ✓ |
| game/ui/panels/component_modifier_grid_panel.py | Read ✓ |
| game/simulation/managers/__init__.py | Read ✓ |
| game/strategy/services/design_validator.py | Read ✓ |
| game/simulation/interfaces/entity_protocols.py | Read ✓ |
| game/strategy/data/carried_vehicle_deploy.py | Read ✓ |
| game/core/protocols/ui.py | Read ✓ |
| game/simulation/combat/__init__.py | Read ✓ |
| game/simulation/replay/replay_capture.py | Read ✓ |
| game/strategy/engine/session/runtime_services.py | Read ✓ |
| game/ui/config.py | Read ✓ |
| game/strategy/engine/order_handlers/superweapons.py | Read ✓ |
| game/engine/collision.py | Read ✓ |
| game/strategy/services/fleet_navigation_service.py | Read ✓ |
| game/ui/screens/transfer_dialog.py | Read ✓ |

---

## Severity Summary

| Severity | Count | Key Issues |
|----------|-------|------------|
| **CRITICAL** | 1 | Missing return type on `check_clicked_inside_or_blocking` override (pygame_gui public API) |
| **MAJOR** | 14 | Narrowable `-> Any` in planet/star list filters, setup_data_io, builder role options; unjustified `# type: ignore[assignment]` in defeat_dialog |
| **MINOR** | 62 | Narrowable `-> Any` in private helpers (harvesting, handlers), colonization system properties, click dispatcher, event router, battle setup controller, dyson sphere, test lab |
| **INFO** | 34 | Protocol `-> Any` (unavoidable duck typing); dunder exemption; registry dispatch chain; pygame_gui `process_event` override |

### Top 5 Remediation Priorities

1. **CRITICAL**: Add `-> bool` to `StrategyModalWindow.check_clicked_inside_or_blocking()` — `game/ui/screens/strategy_modal_window.py:273`
2. **MAJOR**: Remove `# type: ignore[assignment]` in defeat_dialog by typing `_dismiss_button: Optional[UIButton]` — `game/ui/screens/defeat_dialog.py:83`
3. **MAJOR**: Narrow `planet_list_filters.py` functions (7 functions): `gather_planets`, `filter_planets`, `sort_planets`, `get_column_value`, `compute_planet_ranges`, `get_system_name`, `get_owner_name` — `game/ui/screens/planet_list_filters.py`
4. **MAJOR**: Narrow `star_list_filters.py` functions (6 functions): `gather_stars`, `filter_stars`, `sort_stars`, `compute_star_ranges`, `get_system_name`, `get_star_type_display` — `game/ui/screens/star_list_filters.py`
5. **MAJOR**: Narrow `setup_data_io.py` functions (5 functions): `get_base_path`, `scan_ship_designs`, `load_ships_from_entries`, `load_battle_setup`, `find_design` — `game/ui/screens/setup_data_io.py`
