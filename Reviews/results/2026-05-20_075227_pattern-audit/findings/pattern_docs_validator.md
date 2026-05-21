# Pattern Documentation Validation Report

> Generated: 2026-05-20 | Source: `docs/02_PATTERNS.md` vs `game/` codebase

## Summary

| Metric | Count |
|--------|-------|
| Patterns Documented | 43 |
| Patterns Verified (code read) | 43 |
| Accurate | 40 |
| Minor Diff | 3 |
| Stale | 0 |
| Wrong | 0 |
| Undocumented Patterns Found | 6 |

---

## Pattern Accuracy Assessment

| # | Pattern Name | Accuracy | Issues |
|---|-------------|----------|--------|
| 1 | ApplicationContext | ACCURATE | `game/context.py` matches all contracts: `create_production()`, `create_test()`, 10 managed services, `get_default_*`/`set_default_*` accessors. `SingletonMeta` confirmed retired — zero hits under `game/`. Code at `game/context.py:70-100` matches doc. |
| 2 | Protocol + TypeGuard | ACCURATE | `game/core/protocols/` contains all 9 listed files (`boundary.py`, `combat.py`, `common.py`, `persistence.py`, `registry.py`, `strategy_domain.py`, `strategy_entities.py`, `strategy_mutators.py`, `ui.py`). `__init__.py` re-exports confirmed. Mutator protocols at `strategy_mutators.py` match doc. |
| 3 | Registry DI | ACCURATE | `DefaultRegistryProvider` and `TestRegistryProvider` at `game/core/registry.py:369,407`. `Ship(..., *, registries: GameRegistries)` requires registries and raises on `None` (`game/simulation/entities/ship.py:73-78`). `calculate_ability_totals()` does not need resource_catalog. |
| 4 | Registry Pattern | ACCURATE | `RegistryManager` at `game/core/registry.py:114`, `GameRegistries` is frozen DI container + implements `IRegistryProvider`. `ResourceCatalog`/`ResourceDefinition` exist. JSON lifecycle: load -> freeze -> inject. |
| 5 | Facade / Delegate | ACCURATE | All named delegates confirmed exist: `FleetCapabilityCalculator` (`game/strategy/data/fleet_capability_calculator.py:35`), `FleetConsumableAggregator` (`game/strategy/data/fleet_consumable_aggregator.py:13`), `FleetBattleAdapter` (`game/strategy/data/fleet_battle_adapter.py:33`), `ShipInstanceBridge` (`game/strategy/data/ship_instance_bridge.py:25`), `ShipInstanceSerializer`, `ShipConsumableManager`, `ShipCargoManager`, `ShipDisplayFormatter` (`game/strategy/data/ship_display_formatter.py:27`), `ComponentHealthManager` (`game/simulation/components/component_health_manager.py:21`), `ComponentResourceManager` (`game/simulation/components/component_resource_manager.py:20`), `ModifierManager` (`game/simulation/components/modifier_manager.py:30`), `AbilityManager` (`game/simulation/components/ability_manager.py:31`), `ComponentStatsCalculator` (`game/simulation/components/component_stats_calculator.py:69`). `StrategySessionFacade` wraps `GameSession`; UI never touches `GameSession` directly. |
| 6 | CQRS-lite Strategy Session | ACCURATE | DTOs in `game/strategy/facade/dto/` are `@dataclass(frozen=True)` (confirmed: `fleet_dto.py:18,35`, `planet_dto.py` uses frozen dataclasses). Writes route through `facade.handle_command()` and `facade.commands.<verb>(...)`. Commands under `game/strategy/engine/commands.py`. |
| 7 | CommandHandlerRegistry | ACCURATE | `BaseCommandHandler` + `CommandHandlerRegistry` at `game/strategy/engine/handlers/base.py`. `CommandRegistry` + `@command_spec` at `game/strategy/engine/commands/registry.py`. `seed_default_commands()` populates. AST guard `test_no_specs_tuple_literal.py` confirmed referenced. |
| 8 | MVVM | ACCURATE | Workshop screens (`workshop_*`), build queue (`build_queue_*`), test lab, battle setup use MVVM. BuildQueue collaborators (`BuildQueueController`, `BuildQueueRenderer`, `BuildQueuePanelFactory`, `BuildQueueDragHandler`) all exist at documented locations. |
| 9 | Template Method Validation | ACCURATE | `ValidationRule` at `game/simulation/validation/base.py:21` implements `validate()` calling `_should_validate()` before `_do_validate()`. `DesignValidationRule` always runs; `AdditionValidationRule` runs for additions. Matches doc skeleton exactly. |
| 10 | Event Bus | MINOR_DIFF | `WorkshopEventBus` at `game/ui/screens/builder/event_bus.py:19` — class was renamed from `EventBus` to avoid collision with `game/core/event_logging.py::EventBus`. Doc still correctly references the file location and `BuilderEvents` constants (`builder_utils.py:87-91` with `SHIP_UPDATED`, `SELECTION_CHANGED`, `REGISTRY_RELOADED`). The rename is not reflected in doc. Strategy `EventBus` at `game/core/event_logging.py:40` is separate and matches its doc description. |
| 11 | Surface Caching | ACCURATE | Very long, detailed doc (lines 269-350) — all sub-sections verified: `SpriteManager`, asset managers, `invalidate_widget_caches()`, `PerPlayerUiState`, `PerTurnUiState` caches on `FacadeSessionState`, window reuse via `hide()`/`show()`, `StarshipUIAppearanceTheme` subclass. `FacadeSessionState` at `game/strategy/facade/slices/_facade_state.py:34`. `StarshipUIAppearanceTheme` at `game/ui/pygame_gui_patch.py`. |
| 12 | Configuration Classes | ACCURATE | Core config classes at `game/core/config.py` are plain classes (not dataclasses). JSON-backed configs with `@lru_cache(maxsize=1)`. Economy config module-accessor pair (`get_default_*`/`set_default_*`) at `game/strategy/config/economy_config.py:136-149` — confirmed matches doc's three-flavor description. |
| 13 | Spec Compiler + `run_battle` | ACCURATE | `BattleSpec` is `@dataclass(frozen=True)` at `game/simulation/battle_spec.py:55`. `run_battle` at `game/simulation/battle_runner.py`. Three compilers exist at documented locations (`combat_lab/spec_compiler.py`, `game/ui/screens/battle_setup/spec_compiler.py`, `game/strategy/combat/spec_compiler.py`). `BattleOutcome`, `BattleController.start_from_spec()` all confirm. |
| 14 | Two-Phase Ability Aggregation | ACCURATE | `_aggregate_ability_groups()` at `game/simulation/entities/ability_aggregator.py:19` — Phase 1: MAX within `stack_group`, Phase 2: SUM across groups. Marker abilities (`CommandAndControl`, `Armor`, `RequiresCommandAndControl`) use boolean True (lines 15-16). `FleetAuraManager._recalculate()` delegates to this. |
| 15 | Factory | ACCURATE | Factories exist at all documented locations: `game/ai/ai_factory.py`, `game/ui/services/ship_factory.py`, `game/ui/widgets/panel_factory.py`, LLM/image provider factories, registry factory modules. |
| 16 | ScrollState | ACCURATE | `ScrollState` at `game/ui/widgets/scroll_state.py:9` with `offset`, `content_height`, `viewport_height`, `step`, `clamp()`, `handle_mousewheel()`. Tests at `tests/unit/ui/widgets/test_scroll_state.py`. |
| 17 | Serializable Protocol | ACCURATE | `ISerializable` protocol in `game/core/protocols/persistence.py`. `ShipInstance` uses `game/strategy/data/ship_instance_serializer.py`. Tests at `tests/unit/core/test_serializable_protocol.py`. |
| 18 | Per-Battle RNG | ACCURATE | `BattleEngine.start_teams(..., seed=N, ...)` initializes `self.rng = random.Random(seed)`. Injected into `CollisionSystem`, `DamageCalculator`, `AIControllerFactory`, `AIController`, `ErraticBehavior`. Strategy conflict resolution owns separate `self._rng = random.Random()`. Guard test `test_no_unseeded_random.py` confirmed. |
| 19 | Error Boundary | ACCURATE | `TurnStateSnapshot.capture()` at `game/strategy/engine/turn_state_snapshot.py:39` serializes empires+galaxy via `to_dict()`. `_time_phase()` wraps failures as `EnginePhaseError`. `process_turn()` catches, restores snapshot, writes crash diagnostic, re-raises. |
| 20 | Precondition Validation | ACCURATE | `_validate_tick_inputs(empires)` pattern in sub-engines under `game/strategy/engine/`. Raises `ValidationException` with `context={...}`. Skeleton in doc matches code pattern. |
| 21 | Screen State Machine | ACCURATE | `ScreenStateMachine` at `game/core/state_machine.py:41` with declarative transition table, guards, `enter`/`exit` callbacks, `push_and_transition()`/`pop_and_return()`. `_switch_scene()` in `app.py` delegates to it. |
| 22 | TurnEngineConfig | ACCURATE | `TurnEngineConfig` at `game/strategy/engine/turn_engine_config.py:51` — `@dataclass(frozen=True)` with 22 fields (18 engines + 4 mutator protocols). `create_default(registries, *, ai_factory=None, race_registry=None, event_bus=None)` exists. Tests use `dataclasses.replace()`. AST guard `test_no_lazy_fallback_init.py` confirmed. |
| 23 | Tick Phase Registry | ACCURATE | `ITickPhase` protocol at `game/simulation/systems/tick_phase.py:37` with `name`, `priority`, `execute(engine)`. `TickPhaseRegistry` executes by ascending priority. Default 6 phases match doc names exactly. `BattleEngine.update()` delegates to registry. |
| 24 | External-Stats Bridge | ACCURATE | `ship.external_stats: dict[str, float]` filled by `FleetAuraManager._apply_bonuses()`. `Ability.get_effective_stat(stat_key)` handles `_mult`/`_add`. Ship-level virtual stats consumed in `_apply_aggregated_stats()`. Battle-scoped, never serialized. |
| 25 | Scope-Driven Team Routing | ACCURATE | `ABILITY_STAT_REGISTRY` with `OPPONENT_SCOPES`. `emit_entries_for_ability(..., owner_team, num_teams, ...)` returns `(team_id, ModifierEntry)` pairs. `enemy_sector`/`enemy_system` fan out to all non-owner teams. Suppressor/booster distinguished by value, not scope. |
| 26 | Ability-Stat Registry | ACCURATE | `ABILITY_STAT_REGISTRY` at `game/simulation/combat/ability_stat_registry.py:56` maps ability class names to `AbilityStatMapping`. Three mappings confirmed: `ShieldProjection`, `ShieldModifier`, `DamageModifier`. `KNOWN_EXTERNAL_STAT_KEYS` checked by `FleetAuraManager`. |
| 27 | Budget-Aware Randomization | ACCURATE | `RacePointBudget` at `game/strategy/data/race_point_budget.py`. `randomize_all` splits 100-point budget. Exponential cost formula `2**steps - 1`. Environment presets from `homeworld_presets.json`. |
| 28 | Background Service Call | ACCURATE | `LLMBackgroundCall` at `game/services/llm/background.py`. Non-daemon worker thread, status/result/error tracking, cancellation event, instance lock, `LLMConfig.MAX_CONCURRENT_CALLS`. `RaceDescriptionLLMController` at documented location. |
| 29 | Universal Ability Source | ACCURATE | `IAbilitySource` protocol at `game/core/protocols/strategy_entities.py`. Adapters confirmed in `game/strategy/services/ability_sources/` (11 files: `facility.py`, `fleet.py`, `intrinsic_roll.py`, `labels.py`, `planet_intrinsic.py`, `star.py`, `storm.py`, `system_archetype.py`, `warp_point.py`). Collector, iterator, scanner all exist. Static guard against `get_default_registry_provider()` confirmed. |
| 30 | Registrar Close-Callback | ACCURATE | Doc correctly marks this as legacy, superseded by #31. Close-callback pattern still actively used (94 references across `game/ui/`) for slot cleanup. `StrategyWindowManager._handle_window_close` event-driven cleanup also active. No staleness — doc accurately describes its legacy status. |
| 31 | Strategy Modal Window Base Class | ACCURATE | `StrategyModalWindow(UIWindow)` at `game/ui/screens/strategy_modal_window.py:27`. 20 production subclasses confirmed: `TransferDialog`, `OrdersWindow`, `EventLogWindow`, `PlanetSelectionWindow`, `EmpireBuildQueueWindow`, `DesignSelectorWindow`, `FleetReportWindow`, `SystemSelectionWindow`, `FleetSelectionWindow`, `EmpirePanelWindow`, `DefeatDialog`, `BuildQueueListWindow`, `TurnFailedDialog`, `SaveSelectionWindow`, `PlanetAbilitiesWindow`, `CargoQuickDialog`, `FoodAllocationEditor`, `MoveChoiceWindow`. Constructor requires keyword-only `window_manager`. `__init_subclass__` populates `_registered_subclasses`. `is_blocking = True` set after `super().__init__()`. `kill()` unregisters before `super().kill()`. |
| 32 | Compositional Construction | MINOR_DIFF | `StrategyScreenComposition` Protocol at `game/ui/screens/strategy_screen_composition.py:47` with 8 `make_*` methods. `StrategyScreenCompositionFactory` at line 77. Doc says "Use for classes that construct three or more stable, heavy collaborators." Only one production implementation found (`StrategyScreen`). The `RaceSetupScreen` delegate factory (`DefaultRaceSetupDelegateFactory`) is referenced in code but uses a delegate factory pattern, not the composition protocol. Pattern is used as documented but adoption is limited to one class. |
| 33 | UI Widget Test Factory | ACCURATE | `make_ui_widget`, `bypass_init` at `tests/fixtures/ui_widget_factory.py`. Two-stage UIWindow `__init__` with bypass guard. Null/mock UI builder conventions documented. Production never sets `bypass_init`. |
| 34 | Weapon Family Registry | ACCURATE | `WeaponRegistry` at `game/simulation/combat/weapon_registry.py:32`. `WeaponFamily` + `WeaponHandler` at `game/simulation/combat/attack_contract.py`. Handlers at `game/simulation/combat/families/`. `detect_family()`, `dispatch()`, `FAMILY_METADATA`. Acceptance test `TestExtensibilityAcceptance` confirmed. |
| 35 | Stat Contributor Registry | ACCURATE | `STAT_CONTRIBUTOR_REGISTRY` at `game/simulation/entities/stat_contributors/`. `StatAccumulator` with 10 scalar fields + 4 named map fields. `RegistrationHandle` for unregister. Defaults cannot be unregistered. `CREW_PRIORITY_REGISTRY` separate. Phase order: movement=10, defense=20, hangar=40, command=50. |
| 36 | Re-Export Shim | ACCURATE | Remaining shim at `game/simulation/components/component.py:392-405` re-exports from `component_loader.py` — matches doc "395-405" (off by a few lines due to header comment). Deleted shims correctly noted: `race_setup_screen.py` (PROJ-416), `test_run_details.py` (PROJ-417), `command_handlers.py` (PROJ-383). |
| 37 | Typed DeployedGroup Family | ACCURATE | `DeployedGroup` abstract base at `game/strategy/data/deployed_group.py:60`. `MineGroup`, `FighterWing`, `SatelliteConstellation` in `__all__`. `Empire.deployed_groups`, `deployed_groups_of()`. `Fleet.group_kind` string discriminator confirmed deleted. ID namespaces: 100000+/200000+/300000+. `_ShipBearingDeployedGroup` internal base for `FighterWing`/`SatelliteConstellation`. |
| 38 | CarriedVehicle Substrate | ACCURATE | `CarriedVehicle` at `game/strategy/data/carried_vehicle.py:26` with `design_id`, `design_data`, `current_hp`, `component_states`, `vehicle_type`. `VehicleBayAbility` at `game/simulation/components/abilities/vehicle_bay.py:34` with `capacity_mass`, `allowed_types`, `accepts()`. `carried_vehicle_to_ship_instance()` at `game/strategy/data/carried_vehicle_deploy.py:33`. `BayInventory.bay: list[CarriedVehicle]` exists. `_CarriedItemsProxy` confirmed deleted. `VALID_VEHICLE_TYPES = frozenset({"mine", "fighter", "satellite"})`. |
| 39 | Typed-Sidecar Extensions | ACCURATE | `BattleSpecExtensions` at `game/strategy/combat/battle_assembly.py:52` — typed extensions dataclass. `StrategyBattleAssembly` bundling `spec` + `extensions` + `pre_tick_setup`. `StrategyBattleAssembler.assemble()` is single orchestrator. `BattleSpec` is `@dataclass(frozen=True)` at `game/simulation/battle_spec.py:55`. `object.__setattr__(frozen_dto, ...)` anti-pattern eliminated. |
| 40 | Named Pre-Tick Setup Registry | ACCURATE | `PreTickBattleSetupRegistry` at `game/strategy/combat/pre_tick_setup_registry.py:36`. `register(name, setup)` — duplicate names raise `ValueError`. `composed_callback()` returns single ordered callback or `None` for empty. `mine_setup.py` + `reboard_setup.py` in `game/strategy/combat/pre_tick_setup/`. `StrategyBattleAssembler` populates registry; adapter passes to `run_battle(pre_tick_loop_callback=...)`. |
| 41 | Polymorphic Order Issuer | ACCURATE | `IIssuerAdapter` at `game/strategy/engine/issuer_adapter.py:46` — `@runtime_checkable` Protocol. `FleetShipIssuerAdapter` wraps `(Fleet, ShipInstance)`. `PlanetStagingYardIssuerAdapter` wraps `Planet`. Five FMS order handlers consume adapters. `ActionExecutionEngine` ticks both `fleet.orders` and `planet.orders`. |
| 42 | Bootstrap-State Single Assignment Path | ACCURATE | `SessionBootstrapState` + `SessionRuntimeServices` at `game/strategy/engine/session/runtime_services.py`. `SessionBootstrap._build_services()` at `game/strategy/engine/session/bootstrap.py`. `GameSession.__init__` and `GameSession.from_dict()` both route through `_apply_bootstrap_state()`. Anti-drift regression test confirmed. |
| 43 | Unified Container Substrate | ACCURATE | `Container` at `game/strategy/data/container.py:64` — `@dataclass(frozen=True)` with `capacity_mass`, `policy`, three internal slices. `ContainerPolicy` at line 51 with `allowed_kinds` + `allowed_type_ids`. `BayInventory` at `game/strategy/data/bay_inventory.py:45` with 4 slots (`bay`, `pods`, `resources`, `population`). `IProductionResourceSource` Protocol for production engine. `ResourceStorage`/`CargoStorage`/`VehicleBay` abilities deleted per PROJ-436. Eight legacy entity-level storage fields deleted. |

---

## Undocumented Patterns

The following recurring patterns exist in `game/` code but have no dedicated entry in `docs/02_PATTERNS.md`. Several could be classified as instances of Pattern #4 (Registry Pattern) or Pattern #12 (Configuration Classes), but each has a distinct enough contract, scope, and consumption surface to warrant independent documentation.

### UP1: HabitabilityFactor Registry

| Attribute | Detail |
|-----------|--------|
| **Location** | `game/strategy/data/habitability_factors.py` |
| **Registry key** | `FACTOR_REGISTRY: Dict[str, HabitabilityFactor]` (line 360) |
| **Why it matters** | Called out in `AGENTS.md` as a "Key pattern" — "Habitability Factor Registry (single-source-of-truth for all habitability axes)." Not documented in `02_PATTERNS.md`. |
| **Contract** | Declares 7 scalar factors (`gravity`, `temperature`, `water`, `pressure`, `tectonic`, `magnetic`, `radiation`) + 10 gas factors (`gas.O2` through `gas.SO2`) as frozen `HabitabilityFactor` dataclasses. Each factor owns `id`, `display_name`, `unit`, `weight`, `default_setpoint`, `default_tolerance`, `range`, `step`. Consumed by `habitability.py` formula engine and `preference_row.py` UI widget. Adding a new factor is a single dataclass entry. |
| **Consumer count** | 24 references across `game/strategy/data/`, `game/strategy/formulas/`, `game/ui/widgets/` |
| **Suggested doc** | Add as Pattern #44 or fold into Pattern #12 (Configuration Classes) as a distinct sub-variant. |

### UP2: AbilityMetadataRegistry

| Attribute | Detail |
|-----------|--------|
| **Location** | `game/strategy/services/ability_metadata.py` |
| **Why it matters** | 566+ LOC dedicated registry that replaced 11 scattered hardcoded ability-name literal sets across the codebase (PROJ-429 / TD-07). Far more complex than Pattern #4's "simple key-value registry." |
| **Contract** | Frozen `AbilityMetadata` dataclass with `EffectFacet` (display name, kind, owner-aware scopes, value fields) and `EnergyFacet` (activatable, drains_energy, activation time fields). Enums: `RoleTag` (7 tags: WEAPON, SEEKER, BEAM_PROJECTILE, SENSOR, SUPPORT, CARRIER, COMMAND) and `StrategicKind` (9 tags: COMBAT_MODIFIER, COMBAT_FLAT_BONUS, STABILIZER, SUPERWEAPON, ENVIRONMENTAL, RESOURCE_BOOSTER, BUILD_RATE_BOOSTER, PLANETARY_SHIELD, ENERGY_DRAINING). Public API: `get_ability_metadata(name)`, `ability_has_role_tag(name, tag)`, `abilities_with_kind_tag(tag)`, `ability_action_time_field(name)`, `ability_drains_energy(name)`. Cycle-safe: must NOT import from simulation — enforced by AST guard test. |
| **Consumer count** | Formerly 11 scattered sources; now 1 canonical table. |
| **Suggested doc** | Add as Pattern #44 alongside HabitabilityFactor. Distinguishes itself from Pattern #4 (Registry) by the faceted/enumerated metadata shape and cycle-safety guard. |

### UP3: PerPlayerUiState

| Attribute | Detail |
|-----------|--------|
| **Location** | `game/ui/screens/per_player_ui_state.py` |
| **Why it matters** | Distinct view-state partitioning pattern for hot-seat multiplayer. Referenced in Pattern #11 (Surface Caching) as a sub-feature but has its own independent contract, test coverage, and lifecycle semantics. |
| **Contract** | `PerPlayerUiState` stores `dict[int, dict[str, dict]]` — outer key is `empire.id`, inner dict keyed by window slot name (`"planet_list"`, `"star_list"`, `"empire_build_queue"`, `"empire_panel"`, `"fleet_report"`, `"event_log"`). Windows opt in via `SNAPSHOT_SLOT: str`, `capture_view_state() -> dict`, `apply_view_state(state | None)`. Capture runs BEFORE `_next_live_player_index` mutates `current_player_index`. Restore runs at top of `_apply_turn_start_state`. Session-scoped, not serialised. Defeated empire snapshots persist indefinitely. |
| **Consumer count** | Used by `StrategyGameStateManager`, `StrategyWindowManager.iter_snapshot_windows()`, and 6 strategy modal windows. |
| **Suggested doc** | Document as sub-pattern under Pattern #31 (Strategy Modal Window) or as a standalone mini-pattern. The capture/restore sequencing and empire_id keying are non-trivial and easy to get wrong. |

### UP4: Declarative Dispatch Table (Frozen Spec + Immutable Tuple + Lookup)

| Attribute | Detail |
|-----------|--------|
| **Location** | `game/strategy/services/superweapon_registry.py` (131 LOC), `game/strategy/services/stabilizer_registry.py` (119 LOC) |
| **Why it matters** | Recurring sub-pattern used by at least 2 registries. More specific than Pattern #4 — it prescribes a uniform frozen-dataclass spec shape, an immutable module-level tuple, and a single `find_*()` lookup function with no mutation API. |
| **Contract** | Each spec is `@dataclass(frozen=True)` with enum/string/boolean fields. Registry is `Tuple[Spec, ...]` (immutable). Public API: one `find_*(..., spec_field=value) -> Spec | None` function. Adding an entry is a one-row edit to the tuple. `SuperweaponSpec` carries `order_type`, `ability_name`, `target_type`, `consume_ship`, `event_type`. `StabilizerSpec` carries `ability_name`, `scopes`, `blocks` (set of `OrderType`). No code changes in dispatch consumers when entries are added. |
| **Consumer count** | `SuperweaponOrderProcessor` and planet-order scanning code. |
| **Suggested doc** | Document as a variant of Pattern #4 with the specific frozen-spec + immutable-tuple shape. Or note it in Pattern #4's "Extensions" section. |

### UP5: FacadeSessionState (Per-Turn Slice Cache)

| Attribute | Detail |
|-----------|--------|
| **Location** | `game/strategy/facade/slices/_facade_state.py` |
| **Why it matters** | Documented within Pattern #11 (Surface Caching) as "Per-turn UI caches on `FacadeSessionState`" but is a distinct architectural pattern: shared mutable cache state visible to all facade slices but hidden from callers. Has its own lifecycle (`invalidate_all()`), test injection API (`seed_*` helpers), and cross-slice sharing contract. |
| **Contract** | `FacadeSessionState` holds session reference + 4 per-turn caches: `designs_by_empire`, `planets_for_empire_cache`, `stars_cache_new`, `empire_economy_snapshot`. `invalidate_all()` clears every slot, called from `StrategySessionFacade.process_turn()`. Functions check cache first, fall back to fresh gather. Tests use `seed_*` helpers (`seed_planet_index`, `seed_race_registry`, etc.) — the `seed_` prefix distinguishes test injection from production paths. Slices receive `FacadeSessionState` at construction and never reach across to each other. |
| **Consumer count** | 7 facade slices (`command_dispatch_slice`, `economy_slice`, `empire_slice`, `event_slice`, `fleet_slice`, `planet_slice`, `system_slice`). |
| **Suggested doc** | Split out from Pattern #11 into its own short mini-pattern, or keep as a sub-section but elevate its heading level so it's easier to find. |

### UP6: RoleRegistry (Layered-Loading Registry with Invalidation)

| Attribute | Detail |
|-----------|--------|
| **Location** | `game/core/roles.py` (generic machinery) + `game/strategy/data/design_role_registry.py` (instance accessor) |
| **Why it matters** | A generic two-instance registry pattern with layered JSON loading (base → mods → user overlay), runtime `add_user_role()`, and invalidation callbacks. Used with distinct semantics by design roles and Combat Lab scenario roles. |
| **Contract** | `Role` is `@dataclass(frozen=True, slots=True)` with `id`, `display_name`, `description`, `vehicle_type_filter`. `RoleRegistry` loads `{"roles": [...]}` JSON files with precedence: later sources override earlier for same `id`. `allow_runtime_add` flag gates `add_user_role()`. `register_invalidation_callback(cb)` lets caching subsystems refresh. Two instances: `design_role_registry` (allow_runtime_add=True) and `combat_lab_role_registry` (allow_runtime_add=False). Module-level accessor follows `get_default_*`/`set_default_*`/`reset_default_*` convention. |
| **Consumer count** | Design role classification, UI role picker, Combat Lab scenario wiring. |
| **Suggested doc** | Add as a sub-pattern under Pattern #4 (Registry Pattern) showing the layered-loading + invalidation-callback extension. |

---

## Dead Pattern Documentation

No patterns in `docs/02_PATTERNS.md` have zero current usage. All 43 patterns have active implementation in the codebase.

- **Pattern #30 (Registrar Close-Callback):** Correctly marked as "legacy" and "superseded by pattern #31." Still has active usage (94 references) for non-modal slot cleanup, so it is not "dead" — just not the recommended path for new modal tracking.

---

## Documented Patterns Referencing Deleted PROJ Phases

All PROJ references in `02_PATTERNS.md` refer to completed phases that produced the current code shape. No pattern documents PROJ phases that were abandoned without implementation. The doc's "Last verified" timestamps (2026-05-18 for the header, various dates for individual patterns) are consistent with the current code state.

---

## Documentation Update Recommendations

### Priority 1 — Fix Inaccuracies (3 items)

1. **Pattern #10 (Event Bus):** Update doc to note the class was renamed from `EventBus` to `WorkshopEventBus` in `game/ui/screens/builder/event_bus.py`. This avoids ambiguity with the strategy-layer `EventBus` in `game/core/event_logging.py`. Both are described correctly in context — just the class name should be explicit.
   - *File:* `docs/02_PATTERNS.md` ~line 252
   - *Change:* Add `WorkshopEventBus` class name next to the file reference.

2. **Pattern #32 (Compositional Construction):** Note that only `StrategyScreen` uses this pattern in production. Consider adding a second production consumer or documenting that single-consumer status is intentional (the pattern is available for new classes but not yet widely adopted).
   - *File:* `docs/02_PATTERNS.md` ~line 686
   - *Change:* Add a usage-note: "Current production consumer: `StrategyScreen` only."

3. **Pattern #36 (Re-Export Shim):** Line numbers in doc say "395-405" but the re-export block is at lines 392-405 of `component.py`. Trivial offset — no functional mismatch.
   - *File:* `docs/02_PATTERNS.md` ~line 819
   - *Change:* Update to "392-405."

### Priority 2 — Add Missing Patterns (2 items)

4. **HabitabilityFactor Registry (UP1):** Called out in `AGENTS.md` as a key pattern. Add as Pattern #44 or as a documented sub-section under Pattern #4.
   - *Priority reason:* `AGENTS.md` already references it; agents need to know it's the single-source-of-truth for habitability axes.
   - *Location:* `game/strategy/data/habitability_factors.py`
   - *Suggested section:* ~1 paragraph describing the `HabitabilityFactor` dataclass, `FACTOR_REGISTRY`, `get_factor()`, `iter_scalar_factors()`, `iter_gas_factors()`, and the weight allocation table.

5. **AbilityMetadataRegistry (UP2):** 566+ LOC registry consolidating 11 scattered hardcoded sources. Far more complex than a simple registry.
   - *Priority reason:* Large, recently added (PROJ-429), with specific cycle-safety invariants and AST guards. Agents encountering it for the first time need to understand its role-tag/kind-tag API.
   - *Location:* `game/strategy/services/ability_metadata.py`
   - *Suggested section:* ~2 paragraphs describing `RoleTag`/`StrategicKind` enums, `EffectFacet`/`EnergyFacet`, the cycle-safety invariant, and the `ability_has_role_tag()` / `abilities_with_kind_tag()` query API.

### Priority 3 — Document Optional Mini-Patterns (4 items)

6. **PerPlayerUiState (UP3):** Document as sub-section under Pattern #31 (Strategy Modal Window) or Pattern #11 (Surface Caching). The snapshot slot protocol (`SNAPSHOT_SLOT`, `capture_view_state`, `apply_view_state`) and capture/restore sequencing are non-obvious.

7. **Declarative Dispatch Table (UP4):** Document as a variant under Pattern #4 (Registry Pattern). The frozen-dataclass + immutable-tuple shape is recurring and has a specific "one-row-edit" extension contract worth codifying.

8. **FacadeSessionState (UP5):** The current sub-section under Pattern #11 is good but buried. Consider adding a cross-reference from Pattern #6 (CQRS-lite) since the cache state lives on the facade and interacts with DTO reads.

9. **RoleRegistry (UP6):** Document as a sub-section under Pattern #4 showing the layered-loading + invalidation-callback extension recipe.

### Priority 4 — Housekeeping (1 item)

10. **Pattern #30 (Registrar Close-Callback):** The `_handle_window_close` event-driven cleanup path is referenced in the doc but the code at `game/ui/screens/strategy_window_manager.py:421` references it indirectly. Consider adding a note that while #30 is legacy for modal tracking, the close-callback pattern itself is still the standard way to handle registrar slot cleanup across all strategy windows.
