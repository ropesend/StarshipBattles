# Architecture Review Report

**Date:** 2026-03-13
**Scope:** `game/` directory (429 Python files, ~95K lines)
**Reviewer:** Architecture Reviewer Agent

---

## Summary

- **Total issues found:** 15
- **Critical:** 1
- **Major:** 6
- **Minor:** 6
- **Info:** 2

The codebase demonstrates strong architectural discipline in its core layer separation -- zero import violations were found between the five primary layers (core, simulation, strategy, ai, ui). The DI infrastructure (IRegistryProvider protocol, DefaultRegistryProvider, TestRegistryProvider) is well-designed. However, several cross-cutting inconsistencies reduce the benefit of these patterns, and a few areas have accumulated design drift that warrants cleanup.

---

## Layer Dependency Map

### Expected Dependencies

```
core/        -> (no game.* deps)
engine/      -> core
simulation/  -> core, engine
strategy/    -> core, simulation
ai/          -> core, simulation, strategy
ui/          -> all layers
research/    -> core
assets/      -> core
```

### Actual Dependencies Found

```
core/        -> core only                      [CLEAN]
engine/      -> core only                      [CLEAN]
simulation/  -> core, engine                   [CLEAN]
strategy/    -> core, simulation               [CLEAN]
ai/          -> core, simulation, strategy     [CLEAN]
ui/          -> core, simulation, strategy, ai [CLEAN]
research/    -> core, research                 [CLEAN]
assets/      -> core                           [CLEAN]
```

**Layer separation is excellent.** No violations were found in any direction. The simulation layer correctly avoids importing from strategy/ui/ai. The strategy layer correctly avoids importing from ui. AI factory injection is properly done at runtime from higher layers.

### Additional Observations

- `game/exit_dialog.py` sits outside any layer (directly in `game/`), contains pygame imports (UI concern), and uses module-level global state.
- `game/app.py` sits outside any layer, which is acceptable as the composition root.
- `game/assets/` and `game/data/` are supplementary directories outside the core five layers. `assets/` depends only on `core/`.
- `game/research/` is a self-contained sixth layer depending only on `core/`.
- `game/engine/` is an infrastructure layer between `core/` and `simulation/`.

---

## Findings

### Critical

#### AR-001: Duplicate `ICombatShip` Protocol Definitions

**ID:** AR-001
**Severity:** Critical
**Location:** `game/core/protocols.py:601` and `game/simulation/interfaces/entity_protocols.py:43`
**Issue:** Two separate `ICombatShip` Protocol classes exist with different property sets. The `core/protocols.py` version has a smaller surface area (name, team_id, is_alive, is_derelict, hp, max_hp, position, layers, resources, current_target, secondary_targets, max_targets, total_defense_score, get_total_sensor_score). The `simulation/interfaces/entity_protocols.py` version is much richer (adds angle, velocity, radius, mass, current_shields, max_shields, emissive_armor, crystalline_armor, shield_regen_rate, repair_rate, combat_engine, get_all_components, iter_components, get_components_by_ability, recalculate_stats).

**Consumers:**
- `game/core/protocols.py::ICombatShip` is imported by: `ui/services/battle_ui_service.py`, `ui/panels/ship_stats_renderer.py`, `ui/screens/builder/weapons_viewmodel.py`
- `game/simulation/interfaces/entity_protocols.py::ICombatShip` appears only self-referenced in the interfaces `__init__.py`

**Impact:** Name collision creates confusion about which protocol to use. Consumers may pick the wrong one, leading to type errors or missing properties at runtime. This is a protocol identity ambiguity -- two interfaces with the same name but different contracts.

**Recommendation:** Unify into a single canonical definition. The richer simulation version should be the canonical `ICombatShip` in `simulation/interfaces/`. The core version should either be renamed (e.g., `ICombatShipSummary`) or removed, with UI consumers importing from the simulation interfaces.

**Effort:** Medium

---

### Major

#### AR-002: Facade Bypass -- UI Directly Accesses GameSession Internals

**ID:** AR-002
**Severity:** Major
**Location:** Multiple files in `game/ui/screens/`
**Issue:** The `StrategySessionFacade` was designed as the single point of UI-to-engine communication with CQRS-lite pattern. However, the UI layer extensively bypasses it:
- `strategy_screen.py` exposes `self.session` publicly and provides convenience properties (`galaxy`, `empires`, `player_empire`, `enemy_empire`, `systems`, `human_player_ids`) that directly delegate to the session.
- At least 27 occurrences of `.session.` access patterns found across UI files (`self.session.`, `self.scene.session.`, `self._screen.session.`).
- The facade's query path (`_facade.`) has 53 usages, but direct session access (27+) is also prevalent.

**Impact:** The facade boundary is porous. Changes to `GameSession` internals can break UI code directly. The CQRS pattern's "all reads return immutable DTOs" guarantee is violated when UI code reads mutable domain objects through the session reference.

**Recommendation:** Complete the facade migration: route all UI reads through `StrategySessionFacade` queries that return DTOs. Remove the public `session` attribute from `StrategyScreen` and replace convenience properties with facade calls.

**Effort:** Complex

---

#### AR-003: Mixed Interface Abstraction Mechanisms (Protocol vs ABC)

**ID:** AR-003
**Severity:** Major
**Location:** Across `game/core/protocols.py`, `game/simulation/interfaces/`, `game/strategy/interfaces/`, `game/ai/`
**Issue:** The codebase uses two different interface mechanisms inconsistently:

**Protocol (structural typing):** Used in `core/protocols.py` (24 protocols), `simulation/interfaces/` (14 protocols), `ai/protocols.py` (4 protocols), and scattered in `strategy/` and `ui/`.

**ABC (nominal typing):** Used in `strategy/interfaces/engines.py` (11 ABCs), `strategy/interfaces/battle_resolver.py` (1 ABC), `simulation/validation/base.py` (1 ABC), `simulation/combat/battle_mode_handler.py` (1 ABC), `ai/interfaces/controllable.py` (1 ABC), `ui/panels/base_gallery.py` (1 ABC).

The strategy engine interfaces (`IMovementEngine`, `IProductionEngine`, etc.) use ABCs, while nearly identical interface patterns in other layers use Protocols.

**Impact:** Developers must know which mechanism to use when creating new interfaces. ABCs enforce explicit subclassing; Protocols allow structural matching. The inconsistency creates confusion about the project's preferred approach.

**Recommendation:** Standardize on Protocol for cross-layer boundaries (consistent with `core/protocols.py` conventions) and ABC only for within-layer inheritance hierarchies where shared implementation is needed (like `BaseCommandHandler`, `BattleModeHandler`).

**Effort:** Medium

---

#### AR-004: Incomplete DI Migration -- Optional `registries` Parameters

**ID:** AR-004
**Severity:** Major
**Location:** 14+ signatures across `game/simulation/`, `game/strategy/`, `game/ui/`
**Issue:** Many `from_dict()` methods and constructors still accept `registries: Optional[GameRegistries] = None`, despite PROJ-50 mandating strict DI where registries is required. Examples:
- `Ship.from_dict()` -- `registries: Optional['GameRegistries'] = None`
- `ShipInstance.__init__()` -- `registries: Optional['GameRegistries'] = None`
- `ShipInstance.from_dict()` -- `registries: Optional['GameRegistries'] = None`
- `Empire.from_dict()` -- `registries: Optional['GameRegistries'] = None`
- `Fleet.from_dict()` -- `registries: Optional['GameRegistries'] = None`
- `ProductionEngine.__init__()` -- `registries=None`
- `HarvestingEngine.__init__()` -- `registries: Optional[GameRegistries] = None`
- `ConflictResolutionEngine.__init__()` -- `registries: Optional['GameRegistries'] = None`

Meanwhile, `Ship.__init__()` properly requires `*, registries: GameRegistries` with a validation check.

**Impact:** The "optional registries" pattern creates a two-tier DI system. Code that forgets to pass registries silently gets `None`, then fails at runtime (or falls back to the global singleton). This undermines the testability benefits of DI.

**Recommendation:** Complete the PROJ-50 migration: make `registries` a required keyword-only parameter on all remaining signatures. Update all call sites.

**Effort:** Medium

---

#### AR-005: Simulation Layer Uses Global Registry Access Internally

**ID:** AR-005
**Severity:** Major
**Location:** `game/simulation/entities/ship.py:509`, `ship_validator_helper.py:44,55,64`, `ship_stats.py:48`
**Issue:** Within the simulation layer, several methods call `get_default_registry_provider()` directly instead of using the injected `self._registries`:
- `Ship.add_component()` calls `get_or_create_validator(registry_provider=get_default_registry_provider())` despite having `self._registries` available.
- `ShipValidatorHelper` calls `get_default_registry_provider()` on every validation method.
- `ship_stats.py` example in docstring uses `get_default_registry_provider()` directly.

**Impact:** These call sites bypass DI, making the simulation layer harder to test in isolation. The Ship class accepted injected registries via its constructor but then ignores them for validation.

**Recommendation:** Thread the `self._registries` through to `ShipValidatorHelper` and validation calls. The Ship should use its own injected registries for all operations, not reach back to the global provider.

**Effort:** Simple

---

#### AR-006: Duplicate `_get_registries()` Lazy-Init Pattern

**ID:** AR-006
**Severity:** Major
**Location:** `game/ui/services/ship_io.py:41`, `game/ui/screens/strategy_build_queue_manager.py:37`
**Issue:** Two identical module-level `_get_registries()` functions exist that lazily create `GameRegistries` from the default provider, caching in a module-level `_cached_registries` global:

```python
_cached_registries = None

def _get_registries() -> 'GameRegistries':
    global _cached_registries
    if _cached_registries is None:
        from game.core.registry import get_default_registry_provider, GameRegistries
        provider = get_default_registry_provider()
        _cached_registries = GameRegistries(
            components=provider.get_components(),
            ...
        )
    return _cached_registries
```

Additionally, `game/ui/screens/setup_screen.py:36` and `game/ui/screens/setup_data_io.py:24` have a similar pattern for `_ship_factory = None` with lazy init.

**Impact:** Code duplication; module-level global state that's hard to reset in tests; inconsistent with the DI pattern used elsewhere.

**Recommendation:** Extract a shared utility or inject registries via constructor, eliminating the lazy-init pattern.

**Effort:** Simple

---

#### AR-007: Event System Fragmentation

**ID:** AR-007
**Severity:** Major
**Location:** `game/ui/screens/builder/event_bus.py`, `game/strategy/events/`, `game/core/event_logging.py`
**Issue:** Three separate event/messaging systems exist with different designs:

1. **Builder EventBus** (`ui/screens/builder/event_bus.py`): Pub/sub with string event types. Used only within the Design Workshop UI. Subscribers receive `(data)` argument.

2. **Strategy EventLog** (`strategy/events/`): Data-oriented event recording system using `Event` dataclass with `EventType` enum. Used for turn processing events (ship built, combat resolved). Not pub/sub -- it's an append-only log with query methods.

3. **Core event_logging** (`core/event_logging.py`): Module-level global handler with `set_event_handler()`/`log_event()`. Used for simulation-to-strategy event forwarding. Single handler, no subscription list.

**Impact:** Three different patterns for the same general concept (communicating events between components). New developers must understand which system to use in each context. There's no unifying event abstraction.

**Recommendation:** This may be acceptable as-is since each system serves a different purpose (UI component communication, turn event recording, simulation callbacks). However, consider documenting the three systems in the architecture docs with clear guidance on when to use each.

**Effort:** Simple (documentation) / Complex (unification)

---

### Minor

#### AR-008: `exit_dialog.py` Violates Layer Architecture

**ID:** AR-008
**Severity:** Minor
**Location:** `game/exit_dialog.py`
**Issue:** This file sits directly in `game/` (outside any layer), contains pygame imports (UI concern), and uses module-level global variables (`_exit_yes_rect`, `_exit_no_rect`) with functions that mutate them. All other pygame-dependent code lives in `game/ui/`.

**Impact:** Inconsistent placement. The file is small (102 lines) and tightly coupled to `app.py`, but its location breaks the convention that UI code lives in `game/ui/`.

**Recommendation:** Move to `game/ui/dialogs/exit_dialog.py` or convert to a proper class.

**Effort:** Simple

---

#### AR-009: Legacy `handle_input()` Methods Coexist with IScene Protocol

**ID:** AR-009
**Severity:** Minor
**Location:** `game/ui/research/research_scene.py:386`, `game/ui/screens/galaxy_test/screen.py:279`, `game/ui/screens/test_lab/screen.py:573`
**Issue:** Three scenes still have a `handle_input(self, dt, events)` method alongside the IScene-compliant `handle_event(self, event)`. The `app.py` main loop has special-case code to call `handle_input()` for ResearchTree and GalaxyTest scenes (lines 678-681):

```python
elif self.state == GameState.RESEARCH_TREE and hasattr(self.active_scene, 'handle_input'):
    self.active_scene.handle_input(frame_time, events)
elif self.state == GameState.GALAXY_TEST and hasattr(self.active_scene, 'handle_input'):
    self.active_scene.handle_input(frame_time, events)
```

TestLabScreen bridges the gap via `handle_event()` delegating to `handle_input()`.

**Impact:** The `hasattr` checks in `app.py` are workarounds for scenes that haven't fully migrated to the IScene protocol. This creates special-case handling that could grow.

**Recommendation:** Complete the IScene migration for ResearchTreeScene and GalaxyTestScreen. Move per-frame keyboard polling to `update()` and single-event handling to `handle_event()`.

**Effort:** Simple

---

#### AR-010: `hasattr` Usage Despite Protocol Infrastructure

**ID:** AR-010
**Severity:** Minor
**Location:** 80 occurrences across 41 files
**Issue:** Despite having extensive Protocol infrastructure (24+ protocols in `core/protocols.py`, 14+ in `simulation/interfaces/`), the codebase still uses raw `hasattr()` checks in 80 places across 41 files. Some notable examples in `app.py`:
- `hasattr(self, 'builder_scene')` -- checking own attributes
- `hasattr(self.strategy_scene, 'handle_resize')` -- IScene guarantees this
- `hasattr(empire, 'empire_theme_id')` -- IEmpire protocol has this
- `hasattr(empire, 'built_ship_designs')` -- IEmpire protocol has this

**Impact:** Undermines the type safety that the Protocol system was designed to provide. Some `hasattr` checks are for attributes that the Protocol already guarantees.

**Recommendation:** Audit the 80 `hasattr` sites. Replace with Protocol-based TypeGuard checks where appropriate. Remove checks for attributes guaranteed by protocols. Keep `hasattr` only for genuinely optional features not covered by protocols.

**Effort:** Medium

---

#### AR-011: `systems/` vs `services/` Naming Inconsistency in Strategy Layer

**ID:** AR-011
**Severity:** Minor
**Location:** `game/strategy/systems/` and `game/strategy/services/`
**Issue:** The strategy layer has both `systems/` (4 files) and `services/` (9 files) subdirectories. The distinction is unclear:
- `systems/save_game_service.py` -- named "service" but lives in "systems"
- `systems/design_library.py` -- could be a "service"
- `services/cargo_transfer_service.py` -- clearly a service

The simulation layer has the same dual directories:
- `systems/` contains BattleEngine, resource_manager, tech_preset_loader
- `services/` contains BattleService, design_loader, modifier_service

**Impact:** Naming confusion. Developers must guess whether a new file goes in `systems/` or `services/`.

**Recommendation:** Define a clear convention. Suggestion: `systems/` for stateful runtime systems (engines, managers), `services/` for stateless operations (calculators, validators, I/O). Move `save_game_service.py` to `services/`.

**Effort:** Simple

---

#### AR-012: Strategy Data Entities Have Inconsistent Serialization Patterns

**ID:** AR-012
**Severity:** Minor
**Location:** `game/strategy/data/` and `game/simulation/entities/`
**Issue:** Serialization patterns vary across entities:
- Most entities use `to_dict()`/`from_dict()` as instance method and classmethod respectively -- consistent.
- `Ship` has both `to_dict()`/`from_dict()` on the class AND a separate `ShipSerializer` static class with `to_dict(ship)`/`from_dict(data)`. The Ship methods delegate to ShipSerializer.
- `FleetOrder` has `to_dict()` but no `from_dict()` -- deserialization appears to be handled externally.
- `PlanetaryFacility` has `from_dict()` but I didn't find a corresponding `to_dict()`.
- `SpeciesPopulation` has `from_dict()` but appears to lack `to_dict()`.

**Impact:** Minor inconsistency. The delegation pattern (Ship -> ShipSerializer) is reasonable for complex serialization, but the missing `to_dict()`/`from_dict()` pairs on some entities could lead to serialization bugs.

**Recommendation:** Ensure all persistable entities have paired `to_dict()`/`from_dict()` methods. Document the ShipSerializer extraction pattern as the standard for complex serialization.

**Effort:** Simple

---

#### AR-013: `app.py` Scene Management Has Grown Beyond Simple Coordination

**ID:** AR-013
**Severity:** Minor
**Location:** `game/app.py` (735 lines, 42 methods)
**Issue:** The `Game` class in `app.py` handles:
- Window management and display setup
- Scene lifecycle (creation, switching, cleanup)
- All scene callback handling (battle actions, strategy actions, test lab actions, etc.)
- Load/save game coordination
- Quickstart game setup
- Workshop context creation
- Exit dialog management
- Overlay dialog state tracking (showing_load_menu, showing_race_setup, showing_new_game_setup)

At 735 lines with 42 methods, it acts as a god class for scene orchestration.

**Impact:** Changes to any scene's interaction pattern require modifying `app.py`. The overlay dialog state management (three boolean flags) suggests UI concerns that could be delegated to the menu scene.

**Recommendation:** Extract a `SceneManager` that handles scene switching, callback routing, and overlay state. Keep `Game` focused on the main loop, input processing, and top-level initialization.

**Effort:** Medium

---

### Info

#### AR-014: Well-Structured Command Handler Registry Pattern

**ID:** AR-014
**Severity:** Info
**Location:** `game/strategy/engine/command_handlers.py`
**Issue:** The `CommandHandlerRegistry` pattern with `BaseCommandHandler`, `ICommandHandler` Protocol, and `create_default_registry()` factory is well-designed. Each command type has a dedicated handler class. The registry supports dynamic registration. This is a clean application of the Strategy pattern that could serve as a template for other similar dispatch needs in the codebase.

**Impact:** Positive -- this pattern is well-structured and maintainable.

**Recommendation:** Document this as the canonical dispatch pattern. Consider using it as a reference when designing future dispatch systems.

**Effort:** N/A

---

#### AR-015: Singleton Usage Is Disciplined and Centralized

**ID:** AR-015
**Severity:** Info
**Location:** `game/core/singleton.py` and 7 singleton classes
**Issue:** All singletons use the same `SingletonMeta` metaclass with consistent patterns:
- `RegistryManager` (core)
- `StrategyMetadataService` (core)
- `Profiler` (core)
- `SpriteManager` (ui)
- `ScreenshotManager` (ui)
- `ShipThemeManager` (ui)
- `StrategyManager` (ai)
- `AssetManager` (assets)

Each has thread-safe creation, `reset()` for testing, and consistent documentation.

**Impact:** Positive -- singleton usage is controlled and consistent.

**Recommendation:** Continue using `SingletonMeta` for any new singletons. Consider reducing singleton count over time via constructor injection.

**Effort:** N/A

---

## Top 5 Priority Issues

### 1. AR-001: Duplicate `ICombatShip` Protocol (Critical)
**Why:** Two Protocol classes with the same name but different contracts is a source of bugs. UI code importing from `core/protocols.py` gets a subset of properties; simulation code gets the full set. This must be resolved to prevent type confusion.

### 2. AR-004 + AR-005: Incomplete DI Migration (Major)
**Why:** 14+ signatures still accept optional registries, and the simulation layer bypasses its own injected registries to call the global provider. This creates a two-tier DI system that undermines testability. These two issues should be addressed together as they represent the same root cause: incomplete DI adoption.

### 3. AR-002: Facade Bypass (Major)
**Why:** The StrategySessionFacade was designed to protect the UI from GameSession internals, but ~27 direct session accesses bypass it. This couples the UI to domain internals and defeats the CQRS-lite pattern. Until the facade is the sole access path, it provides false confidence about encapsulation.

### 4. AR-003: Mixed Protocol/ABC for Interfaces (Major)
**Why:** The inconsistency between Protocol and ABC for interfaces creates cognitive overhead. New developers must make a choice without clear guidance. Standardizing on Protocol for cross-layer boundaries (where structural typing shines) and ABC for within-layer inheritance hierarchies would establish a clear rule.

### 5. AR-009 + AR-010: IScene Migration + hasattr Cleanup (Minor, High Volume)
**Why:** 80 `hasattr` checks and 3 legacy `handle_input()` scenes represent incomplete pattern adoption. The Protocol infrastructure is well-built but not fully leveraged. Cleaning these up would demonstrate the value of the Protocol investment and improve type safety.

---

## Architectural Strengths

The codebase demonstrates several strong architectural qualities:

1. **Layer Separation:** Zero import violations across all layers. This is rare and commendable at 429 files.

2. **DI Infrastructure:** The `IRegistryProvider` Protocol + `DefaultRegistryProvider` + `TestRegistryProvider` pattern is well-designed for both production and testing.

3. **Command Handler Pattern:** The `CommandHandlerRegistry` in the strategy engine is a clean, extensible dispatch mechanism.

4. **Protocol-based Type Safety:** The `core/protocols.py` system with TypeGuard functions provides a modern Python approach to duck typing with type checking.

5. **Singleton Discipline:** All singletons use a single, well-documented metaclass with consistent reset/testing support.

6. **No Pygame in Non-UI Layers:** The simulation and strategy layers are completely free of pygame imports, enabling headless testing and potential engine reuse.
