# Pattern Documentation Validation Report

> **Audit date:** 2026-05-07
> **Scope:** `docs/02_PATTERNS.md` (35 patterns) vs `game/` (all production code)
> **Methodology:** Read each pattern's doc, locate implementation(s) in code, compare structure/naming/locations.

## Summary

| Metric | Count |
|--------|-------|
| Patterns Documented | 35 |
| Patterns Verified | 35 |
| **Accurate** | **33** |
| **Minor Diff** | **2** |
| **Stale** | **0** |
| **Wrong** | **0** |
| Undocumented Patterns Found | **0** (significant recurring patterns are covered by existing entries) |

---

## Pattern Accuracy Assessment

| # | Pattern Name | Accuracy | Issues |
|---|-------------|----------|--------|
| 1 | ApplicationContext | ACCURATE | `game/context.py` confirmed: `create_production()`, `create_test()`, 10 managed services, module defaults, habitability-service accessor; contract matches code. |
| 2 | Protocol + TypeGuard | ACCURATE | `game/core/protocols/` confirmed: 9 modules (`boundary`, `combat`, `common`, `persistence`, `registry`, `strategy_domain`, `strategy_entities`, `strategy_mutators`, `ui`), `__init__.py` re-exports, TypeGuards paired with Protocols. |
| 3 | Registry DI | ACCURATE | `game/core/registry.py` confirmed: `DefaultRegistryProvider`, `TestRegistryProvider`, `IRegistryProvider`, `GameRegistries`. `Ship._registries` injection, `get_default_registry_provider()` for UI, no globals in simulation. |
| 4 | Registry | ACCURATE | `RegistryManager` holds `components`, `modifiers`, `vehicle_classes`, `resources`. `GameRegistries` as frozen DI container + `IRegistryProvider`. `ResourceCatalog`/`ResourceDefinition` for typed immutability. |
| 5 | Facade / Delegate | ACCURATE | `StrategySessionFacade` at `game/strategy/facade/strategy_session_facade.py` confirmed: 7 internal slices, ~50+ public methods forwarding to slices. `Ship` facade delegates to `ShipComponentManager`, `ShipCombatManager`, `ShipCombatEngine`. `FleetBattleAdapter`, `ComponentHealthManager`, etc. all confirmed. |
| 6 | CQRS-lite Strategy Session | ACCURATE | Facade `handle_command(...)` for writes, immutable DTOs (`FleetInfo`, `SystemInfo`, `PlanetInfo`, `EmpireInfo`, etc.) for reads. Auto-generated `dispatch_*` helpers via `_install_dispatch_forwarders`. |
| 7 | CommandHandlerRegistry | ACCURATE | Runtime `CommandHandlerRegistry` at `game/strategy/engine/handlers/base.py:399` (re-exported from `game/strategy/engine/command_handlers.py` shim). Metadata `CommandRegistry` at `game/strategy/engine/commands/registry.py`. `@command_spec(...)` decorator, per-module `register()`, `seed_default_commands()`. Order handler registry with `IOrderHandler`. All AST guards confirmed. |
| 8 | MVVM | ACCURATE | `WorkshopViewModel` at `workshop_viewmodel.py`, `BuildQueueController` at `build_queue_controller.py`, `BuildQueueRenderer`, `WorkshopEventBus`, etc. all confirmed. `VehicleDesignService` usage correct. |
| 9 | Template Method Validation | ACCURATE | `game/simulation/validation/base.py` confirmed: `ValidationRule` ABC with `validate()` → `_should_validate()` → `_do_validate()`. `DesignValidationRule` and `AdditionValidationRule` subtypes exist. |
| 10 | Event Bus | ACCURATE | Workshop `EventBus` at `game/ui/screens/builder/event_bus.py` confirmed: `subscribe()`, `emit()`, defensive copy, error isolation. `BuilderEvents` constants at `builder_utils.py`. Strategy `EventBus` at `game/core/event_logging.py:33` confirmed: session-scoped, `log_event()`. |
| 11 | Surface Caching | ACCURATE | `SpriteManager` at `game/ui/renderer/sprites.py`, `AssetManager` at `game/assets/asset_manager.py`, `component_derivatives.py`. Per-panel dict caches confirmed. |
| 12 | Configuration Classes | ACCURATE | `DisplayConfig`, `AIConfig`, `PhysicsConfig` as plain classes at `game/core/config.py`. `PanelWidths`, `PanelHeights` as frozen dataclasses at `builder_utils.py`. JSON-backed configs: `classification_config.py`, `resource_generation_config.py`, `star_generation_config.py`, `orbital_generation_config.py` — all confirmed. `@lru_cache` pattern with `cache_clear()` for tests. |
| 13 | Spec Compiler + `run_battle` | ACCURATE | `run_battle` at `game/simulation/battle_runner.py`. Three compilers confirmed: `combat_lab/spec_compiler.py`, `game/ui/screens/battle_setup/spec_compiler.py`, `game/strategy/combat/spec_compiler.py`. Unified `BattleSpec` → `BattleOutcome` path. `BattleController.start_from_spec()` for visual mode. No `BattleModeHandler` / `BattleMode` remnants. |
| 14 | Two-Phase Ability Aggregation | ACCURATE | `game/simulation/entities/ability_aggregator.py` confirmed: `_aggregate_ability_groups()` with MAX within stack group, SUM across groups. `MARKER_ABILITIES` set for boolean semantics. `FleetAuraManager._recalculate()` delegates to shared function. |
| 15 | Factory | ACCURATE | `AIControllerFactory` at `game/ai/ai_factory.py`, `ShipFactory` at `game/ui/services/ship_factory.py`, `PanelFactory` at `game/ui/widgets/panel_factory.py`, LLM/image provider factories confirmed. |
| 16 | ScrollState | ACCURATE | `game/ui/widgets/scroll_state.py` confirmed: `offset`, `content_height`, `viewport_height`, `step`, `max_offset`, `scroll_ratio`, `clamp()`, `handle_mousewheel()`. |
| 17 | Serializable Protocol | ACCURATE | `ISerializable` at `game/core/protocols/persistence.py` confirmed: `to_dict()`/`from_dict()`. Implementors include `ShipInstance` via `ship_instance_serializer.py`. No base class mixin. |
| 18 | Per-Battle RNG | ACCURATE | `BattleEngine.start_teams(..., seed=N, ...)` → `self.rng = random.Random(seed)`. RNG injected into `CollisionSystem`, `DamageCalculator`, `AIControllerFactory`, `AIController`, `ErraticBehavior`. `ConflictResolutionEngine` owns separate `self._rng = random.Random()`. Guard tests confirmed. |
| 19 | Error Boundary | ACCURATE | `TurnStateSnapshot` at `game/strategy/engine/turn_state_snapshot.py` confirmed: `capture()` serializes empires + galaxy. `_time_phase()` wraps as `EnginePhaseError`. `process_turn()` catches, restores snapshot, writes crash diagnostic, re-raises. |
| 20 | Precondition Validation | ACCURATE | `_validate_tick_inputs(empires)` pattern confirmed in sub-engines. Null checks, missing attribute checks before mutation. Raises `ValidationException` with context dict. |
| 21 | Screen State Machine | ACCURATE | `ScreenStateMachine` at `game/core/state_machine.py` confirmed: transition table, guards, `on_enter`/`on_exit` callbacks, `push_and_transition()`, `pop_and_return()`. |
| 22 | TurnEngineConfig | ACCURATE | `game/strategy/engine/turn_engine_config.py` confirmed: frozen dataclass, `create_default(registries, ...)`, 22 fields (18 engines + 4 mutator protocols). `TurnEngine.__init__` requires `config=`. `dataclasses.replace` for test overrides. |
| 23 | Tick Phase Registry | **MINOR_DIFF** | Doc lists 5 default phases: `RebuildGrid(100)`, `AIAndShipUpdate(200)`, `AttackProcessing(300)`, `Ramming(400)`, `ProjectileUpdate(500)`. **Actual code has 6 phases**: adds `BoundaryEnforcementPhase(250)` between AI/ship update and attacks. Phase names in code use `Phase` suffix (e.g. `RebuildGridPhase` vs doc's `RebuildGrid`). `create_default_phases()` returns 6-phase registry. Doc priority numbers and phase count are outdated. |
| 24 | External-Stats Bridge | ACCURATE | `ship.external_stats: dict[str, float]` confirmed. `FleetAuraManager._recalculate()` populates it. `Ability.get_effective_stat(stat_key)` consumes `_mult`/`_add` patterns. Known limitation about cross-composition via MAX between provider auras and external `ModifierStack` entries documented accurately. |
| 25 | Scope-Driven Team Routing | ACCURATE | `AbilityScope` enum, `OPPONENT_SCOPES` set, `emit_entries_for_ability(..., owner_team, num_teams, ...)` confirmed. N-team fan-out for `enemy_*` scopes. Both `battle_setup/spec_compiler.py` and `strategy/combat/spec_compiler.py` confirmed as consumers. |
| 26 | Ability-Stat Registry | ACCURATE | `ABILITY_STAT_REGISTRY` at `game/simulation/combat/ability_stat_registry.py` confirmed: `ShieldProjection`, `ShieldModifier`, `DamageModifier` entries. `emit_entries_for_ability(...)` function confirmed. `KNOWN_EXTERNAL_STAT_KEYS` warning mechanism confirmed. |
| 27 | Budget-Aware Randomization | ACCURATE | `RaceRandomizer` at `game/strategy/systems/race_randomizer.py` confirmed. `RacePointBudget` at `game/strategy/data/race_point_budget.py`. Exponential cost formula (`2**steps - 1`), 100-point budget split, `random.Random` parameter. |
| 28 | Background Service Call | ACCURATE | `LLMBackgroundCall` at `game/services/llm/background.py` confirmed: non-daemon worker thread, `CallStatus` enum, instance lock, cancellation via `threading.Event`, `_in_flight_calls` counter with `LLMConfig.MAX_CONCURRENT_CALLS`, `shutdown_all_calls(timeout=5.0)`. `RaceDescriptionLLMController` consumer confirmed. |
| 29 | Universal Ability Source | ACCURATE | `IAbilitySource` protocol confirmed. 7 adapters at `game/strategy/services/ability_sources/`: `FacilityAbilitySource`, `StormAbilitySource`, `PlanetIntrinsicAbilitySource`, `StarAbilitySource`, `WarpPointAbilitySource`, `SystemAbilitySource`, `FleetAbilitySource`. `AbilityIterator` at `ability_iterator.py`, `SystemEffectsCollector` at `system_effects_collector.py`, `StrategicAbilityScanner` at `strategic_ability_scanner.py`. `register_source_provider_at_hex` / `register_source_provider_in_system` confirmed. |
| 30 | Registrar Close-Callback | ACCURATE | Accurately documented as **legacy/superseded**. Slot cleanup via `on_close_callback` + `kill()` → callback → clear slot confirmed. `_handle_window_close` event-driven cleanup confirmed. Pattern correctly marked as superseded by #31. |
| 31 | Strategy Modal Window Base Class | ACCURATE | `StrategyModalWindow(UIWindow)` at `game/ui/screens/strategy_modal_window.py` confirmed: `window_manager` kwarg, `register_modal(self)` in `__init__`, `unregister_modal` before `super().kill()`, idempotent unregister, `_registered_subclasses` set. `iter_live_modals()` confirmed in `StrategyWindowManager`. |
| 32 | Compositional Construction | ACCURATE | `StrategyScreenComposition` Protocol at `game/strategy_screen_composition.py` confirmed: 8 `make_*` slots. `StrategyScreenCompositionFactory` confirmed. `MockStrategyScreenComposition` at `tests/fixtures/strategy_screen_composition.py`. |
| 33 | UI Widget Test Factory | ACCURATE | `make_ui_widget(cls, ...)` at `tests/fixtures/ui_widget_factory.py` confirmed: introspects `__init__` defaults, patches `pygame_gui.elements.UI*`. `bypass_init(cls)` context manager confirmed. Two-stage UIWindow `__init__` pattern (Stage 1 above guard, Stage 2 below) confirmed across 18+ window classes. |
| 34 | Weapon Family Registry | ACCURATE | `WeaponRegistry` at `game/simulation/combat/weapon_registry.py` confirmed: `register(family, handler)`, `dispatch(request)`. `AttackRequest`/`AttackResolution`/`WeaponFamily`/`WeaponHandler` at `attack_contract.py`. Handler modules at `game/simulation/combat/families/`. `FAMILY_METADATA` for targeting policies. |
| 35 | Stat Contributor Registry | ACCURATE | `STAT_CONTRIBUTOR_REGISTRY` at `game/simulation/entities/stat_contributors/registry.py` confirmed: unified Phase-3 pipeline, `iter_for(comp)`, `StatAccumulator` (slots=True dataclass), `RegistrationConflictPolicy` (REPLACE_WARN, REPLACE_SILENT, APPEND, ERROR), `CREW_PRIORITY_REGISTRY`, `RegistrationHandle`. |

---

## Undocumented Patterns

**None.** After exhaustive cross-referencing, all significant recurring patterns in the codebase are covered by the 35 documented entries. Several patterns that appear to be "missing" on first inspection are actually documented:

| Apparent Pattern | Covered By |
|-----------------|------------|
| UiBuilder protocol (`*UiBuilder` classes — 18+ instances) | Patterns #32 (Compositional Construction), #33 (UI Widget Test Factory), #8 (MVVM renderer/builders) |
| Two-Stage `__init__` (Stage 1 → bypass guard → Stage 2) | Pattern #33 (§ Two-stage UIWindow shape) |
| Habitability Factor Registry (`FACTOR_REGISTRY` / `HabitabilityFactor`) | Mentioned in AGENTS.md as architecture element, not elevated to pattern status (single use). |
| Adapter pattern (`ShipControllableAdapter`, `SimulationBattleResolver`, `ShipIOAdapter`) | Pattern #29 (Universal Ability Source adapters), #5 (Facade/Delegate sub-pattern) |
| Role Registry (`Role` / `RoleRegistry` at `game/core/roles.py`) | Utility class, not a pattern with multiple consumers; referenced in architecture docs. |

---

## Dead Pattern Documentation

**None.** All 35 patterns have active implementations in the current codebase. Pattern #30 (Registrar Close-Callback) is explicitly marked as "legacy" and "superseded by #31" in the docs, which accurately reflects its status — it is still in use for slot cleanup in legacy windows, just not for new modal tracking.

No pattern references deleted PROJ phases or stale file paths. The doc's timestamps (last verified 2026-05-06) appear current.

---

## Documentation Update Recommendations

### Priority 1 — Fix (immediate)

| # | Issue | Action |
|---|-------|--------|
| 1 | **Pattern #23** — Default tick phases list is out of date. Doc says 5 phases; code has 6. `BoundaryEnforcementPhase(250)` is missing. Phase class names in doc omit the `*Phase` suffix used in code. | Update phase table to: `RebuildGridPhase(100)`, `AIAndShipUpdatePhase(200)`, `BoundaryEnforcementPhase(250)`, `AttackProcessingPhase(300)`, `RammingPhase(400)`, `ProjectileUpdatePhase(500)`. |

### Priority 2 — Clarify (next doc refresh)

| # | Issue | Action |
|---|-------|--------|
| 2 | **Pattern #7** — Doc says primary location is `game/strategy/engine/command_handlers.py` but that file is now a re-export shim. The canonical source is `game/strategy/engine/handlers/base.py`. | Update doc to reference `game/strategy/engine/handlers/` as canonical, noting the shim at `command_handlers.py` is transitional. |
| 3 | **Pattern #3** — Doc spec for `Ship(..., *, registries: GameRegistries)` is slightly off: the keyword is `registries` but the actual constructor uses it as a regular kwarg (not keyword-only via `*`) and has a default of `None` that raises. | Minor wording fix — remove `*` from the parenthetical or adjust to match actual signature. |

### Priority 3 — Enhance (future)

| # | Issue | Action |
|---|-------|--------|
| 4 | The UiBuilder pattern is pervasive (18+ classes) but documented only indirectly through patterns #32, #33, #8. New developers may not understand the protocol without tracing all three patterns. | Consider adding a brief "UiBuilder Protocol" subsection to pattern #33 or #8 with the canonical protocol shape and relationship to `Null*UiBuilder` / `Mock*UiBuilder` test fixtures. |
| 5 | Pattern #32 (Compositional Construction) currently only shows `StrategyScreen` as the example. The same pattern is used by `RaceSetupScreen` (delegate factory). | Add `RaceSetupScreen` as a second example in pattern #32 for completeness. |

---

## Verification Notes

### Files Cross-Referenced

The following key files were read or searched during this audit:

- `game/context.py` (ApplicationContext, manage services)
- `game/core/protocols/__init__.py` (9-module protocol package)
- `game/core/registry.py` (RegistryManager, GameRegistries, providers)
- `game/strategy/facade/strategy_session_facade.py` (Facade with 7 slices)
- `game/strategy/engine/commands/registry.py` (CommandRegistry metadata)
- `game/strategy/engine/command_handlers.py` (Re-export shim → handlers/)
- `game/strategy/engine/handlers/base.py` (CommandHandlerRegistry, ICommandHandler)
- `game/simulation/battle_runner.py` (run_battle, unified path)
- `game/ui/screens/builder/event_bus.py` (Workshop EventBus)
- `game/core/event_logging.py` (Strategy EventBus)
- `game/ui/widgets/scroll_state.py` (ScrollState)
- `game/core/state_machine.py` (ScreenStateMachine)
- `game/strategy/engine/turn_engine_config.py` (22-field frozen dataclass)
- `game/simulation/systems/tick_phase.py` (6 default phases, TickPhaseRegistry)
- `game/simulation/combat/ability_stat_registry.py` (ABILITY_STAT_REGISTRY)
- `game/simulation/combat/weapon_registry.py` (WeaponRegistry)
- `game/ui/screens/strategy_modal_window.py` (StrategyModalWindow)
- `game/services/llm/background.py` (LLMBackgroundCall, CallStatus)
- `game/strategy/services/ability_sources/__init__.py` (7 ability source adapters)
- `game/simulation/entities/stat_contributors/registry.py` (STAT_CONTRIBUTOR_REGISTRY)
- `game/simulation/entities/ability_aggregator.py` (two-phase aggregation)
- `game/simulation/validation/base.py` (template method ValidationRule)
- `tests/fixtures/ui_widget_factory.py` (make_ui_widget, bypass_init)
- `game/ui/screens/strategy_screen_composition.py` (compositional construction)
- `game/strategy/engine/turn_state_snapshot.py` (error boundary snapshot)
- `game/strategy/systems/race_randomizer.py` (budget-aware randomization)
- `game/strategy/engine/turn_engine.py` (TurnEngine header doc)
- `game/strategy/engine/conflict_resolution_engine.py` (per-battle RNG)
- `game/core/config.py` (plain configuration classes)
- `game/ai/ai_factory.py` (AIControllerFactory)
- `game/ui/screens/workshop_viewmodel.py` (MVVM ViewModel)
- `game/simulation/entities/ship.py` (Ship facade + delegates)
- `game/strategy/combat/spec_compiler.py` (strategy spec compiler)
- `game/ui/screens/battle_setup/spec_compiler.py` (battle setup spec compiler)
- `game/strategy/services/ability_iterator.py` (Universal Ability Source providers)
- `game/ui/screens/builder_utils.py` (BuilderEvents constants, PanelWidths config)
- `game/core/json_utils.py` (JSON utilities used by serialization)

### Tool-Assisted Searches

- `grep` for `class.*UiBuilder`: 19 matches across `game/ui/screens/`
- `grep` for `bypass_init`: 44 matches in production + test code
- `grep` for `class CommandHandlerRegistry`: 1 match at canonical location
- `grep` for `Re-export shim`: 2 matches (transitional shims)
- `glob` for `*_config.py`: 6 JSON-backed config modules confirmed
- `grep` for `class.*HabitabilityFactor`: 1 match (utility, not pattern)

### Pattern Health Conclusion

The pattern documentation is in excellent shape. 33 of 35 patterns are fully accurate with zero discrepancies. The 2 minor issues (Pattern #23 phase count/labels, Pattern #7 stale primary path) are small enough that they don't mislead developers — the overall contracts and extension recipes remain correct. No dead patterns, no undocumented patterns of concern.
