# Architecture Reviewer Report

**Date:** 2026-03-13
**Scope:** Full codebase (`game/` - 429 Python files)
**Focus:** Architectural pattern consistency, layering, dependencies, design patterns

---

## Summary

- Total issues found: **12**
- Critical: **0**, Major: **4**, Minor: **6**, Info: **2**

The codebase demonstrates strong architectural discipline overall. The layer dependency hierarchy (Core -> Simulation -> Strategy -> UI) is cleanly enforced with zero import violations at runtime. The registry/DI migration (PROJ-27/38/50) has been thorough, with `RegistryManager.instance()` calls confined to the composition root (`app.py`) and the registry module itself. The `engine` layer sits appropriately alongside `simulation`, depending only on `core`. The exception hierarchy is well-structured with a single root `GameException`. However, several inconsistencies remain in interface definition patterns, protocol duplication, UI concerns in the simulation layer, and incomplete facade adoption.

---

## Findings

### Major Issues

#### MAJOR: UI Presentation Logic Embedded in Simulation Layer
**ID:** AR-01
**Location:** `game/simulation/components/abilities/*.py` (26 `get_ui_rows()` methods), `game/simulation/components/component.py:288`, `game/simulation/components/ability_manager.py:127`
**Issue:** Every ability subclass implements `get_ui_rows()` which returns UI display data including color hints. The `ui_colors.py` module containing hex color constants (`#FF6464`, `#00FFFF`, etc.) lives inside `game/simulation/components/abilities/`. The `IAbility` protocol in `game/simulation/interfaces/ability_protocols.py:66` even declares `get_ui_rows()` as part of the ability contract. This is a classic layer violation where presentation logic is pushed down into the domain model.
**Impact:** The simulation layer cannot be used independently (e.g., in a CLI, headless server, or alternate UI) without carrying UI rendering metadata. Changes to UI presentation require modifying simulation-layer files. The color constants in simulation create an implicit dependency on UI rendering conventions.
**Recommendation:** Extract `get_ui_rows()` to a UI-layer visitor or formatter pattern. Create a `UIAbilityFormatter` in `game/ui/` that knows how to render each ability type. Move `ui_colors.py` to `game/ui/`. The simulation abilities should only expose data properties; the UI layer should decide how to display them.
**Effort:** Complex

---

#### MAJOR: Duplicate ICombatShip Protocol Definitions
**ID:** AR-02
**Location:** `game/core/protocols.py:601` and `game/simulation/interfaces/entity_protocols.py:43`
**Issue:** Two separate `ICombatShip` Protocol classes exist with overlapping but different member sets. The core version (PROJ-193) is used by 3 UI files. The simulation version (PROJ-190) is exported from `game/simulation/interfaces/__init__.py` but has zero external consumers -- it is only self-referenced in a `TYPE_CHECKING` block. Both define `name`, `team_id`, `position` properties but differ in other members (e.g., core has `resources`, `current_target`, `secondary_targets`; simulation has `velocity`, `angle`, detailed combat properties).
**Impact:** Confusing for developers deciding which protocol to use. The simulation version is dead code from an adoption standpoint. The naming collision means import errors or wrong-type bugs if someone imports from the wrong module.
**Recommendation:** Remove the unused simulation-layer `ICombatShip` or consolidate into a single protocol. If different granularity is needed, use protocol composition (e.g., `ICombatShip` extends `ICombatant` + `IPhysicsShip`).
**Effort:** Medium

---

#### MAJOR: Inconsistent Interface Pattern -- Protocol vs ABC
**ID:** AR-03
**Location:** Strategy interfaces use ABC (`game/strategy/interfaces/engines.py` - 11 ABCs), simulation interfaces use Protocol (`game/simulation/interfaces/` - 12 Protocols), core uses Protocol (`game/core/protocols.py` - 23 Protocols)
**Issue:** The strategy layer exclusively uses ABC (Abstract Base Class) for its engine interfaces (`IMovementEngine`, `IProductionEngine`, `IOrderProcessor`, etc.), while the simulation and core layers exclusively use Protocol. The validation system has the same split: `IValidationRule` in core is a Protocol, while `ValidationRule` in simulation is an ABC with template-method pattern. Even the `IBattleResolver` in `game/strategy/interfaces/battle_resolver.py` is an ABC.
**Impact:** Two different patterns for the same purpose (defining contracts) creates cognitive overhead. ABC requires explicit inheritance (`class Foo(IMovementEngine)`) while Protocol uses structural typing. This affects testability -- Protocol-based interfaces are easier to mock without inheritance.
**Recommendation:** Standardize on Protocol for all new interfaces. The strategy ABCs are functional and well-tested, so migrating them is low priority, but new interfaces should use Protocol for consistency with the rest of the codebase.
**Effort:** Medium (low priority)

---

#### MAJOR: Incomplete Facade Adoption -- UI Bypasses Strategy Facade
**ID:** AR-04
**Location:** `game/ui/screens/strategy_screen.py`, `game/ui/screens/strategy_build_queue_manager.py`, `game/ui/panels/build_queue_controller.py`, and 12+ other UI files
**Issue:** A `StrategySessionFacade` exists with proper DTOs (`FleetInfo`, `PlanetInfo`, `SystemInfo`, `EmpireInfo`) in `game/strategy/facade/`, but the UI layer frequently imports concrete domain objects directly: `Fleet` from `game.strategy.data.fleet`, `Galaxy` from `game.strategy.data.galaxy`, `Empire` from `game.strategy.data.empire`, `Planet`/`PlanetType` from `game.strategy.data.planet`. At least 15 UI files import directly from strategy data modules, while only `strategy_fleet_ops.py` uses the `FleetInfo` DTO.
**Impact:** The facade pattern loses its value when bypassed. UI code becomes tightly coupled to strategy domain internals. Changes to `Fleet`, `Galaxy`, or `Empire` data structures propagate directly to UI files. The DTOs represent the intended clean interface but are largely unused.
**Recommendation:** This is likely an in-progress migration (PROJ-87 mentioned in memory). Continue migrating UI consumers to use the facade DTOs. Prioritize `strategy_screen.py` and `build_queue_controller.py` as high-traffic entry points.
**Effort:** Complex

---

### Minor Issues

#### MINOR: Triplicated `_has_attrs` Duck Typing Helper
**ID:** AR-05
**Location:** `game/core/protocols.py:694`, `game/simulation/interfaces/ability_protocols.py:315`, `game/simulation/interfaces/entity_protocols.py:480`
**Issue:** The `_has_attrs(obj, *attrs)` helper function is independently defined in three separate files with identical implementations. Each module has its own copy for duck-typing TypeGuard checks.
**Impact:** Maintenance burden from duplication. If the helper logic needs to change (e.g., adding logging or handling edge cases), three files must be updated.
**Recommendation:** Extract `_has_attrs` to `game/core/protocols.py` (or a shared utility) and import it in the simulation interfaces.
**Effort:** Simple

---

#### MINOR: Inconsistent DI Strictness in UI Services
**ID:** AR-06
**Location:** `game/ui/services/validation_service.py:37` vs `game/ui/services/vehicle_class_service.py:38`, `game/ui/services/component_service.py:36`
**Issue:** `ValidationService.__init__` accepts `validator: Optional[Any] = None` and lazily creates the default via `get_or_create_validator()`. In contrast, `VehicleClassService` and `ComponentService` (marked PROJ-50/211) use strict DI where `registry_provider: IRegistryProvider` is required. `BattleService.__init__` takes no dependencies at all. This creates inconsistency in how services obtain their dependencies.
**Impact:** Minor testability concern -- optional DI means tests may inadvertently use global state. Inconsistent patterns make it harder for developers to know the expected pattern.
**Recommendation:** Migrate `ValidationService` to strict DI (require the validator parameter). For `BattleService`, consider whether DI would improve testability.
**Effort:** Simple

---

#### MINOR: Module-Level Global State for Event System
**ID:** AR-07
**Location:** `game/core/event_logging.py:33`
**Issue:** The event logging system uses a module-level global `_event_handler: Optional[Callable] = None` with `set_event_handler()` / `get_event_handler()` functions. While this is documented and managed carefully (set by GameSession, cleared in test fixtures), it contrasts with the project's DI-first approach for registries.
**Impact:** Low -- the event handler is well-documented with clear lifecycle management. However, it represents a different pattern from the registry DI approach, which could confuse newcomers about the project's preferred dependency management strategy.
**Recommendation:** Document this as an intentional exception to the DI pattern (observer/callback pattern where global registration is standard practice). No code change needed.
**Effort:** Simple (documentation only)

---

#### MINOR: Import Ordering in GameSession
**ID:** AR-08
**Location:** `game/strategy/engine/game_session.py:59-64`
**Issue:** Imports are placed after the `logger = logging.getLogger(__name__)` line on line 59. Lines 60-64 contain `from game.strategy.engine.turn_engine import TurnEngine` and similar imports after the logger assignment. This violates PEP 8 import ordering conventions.
**Impact:** Purely cosmetic. May indicate a circular import workaround that was done hastily.
**Recommendation:** Move all imports to the top of the file or, if circular imports require it, add a comment explaining why the import is deferred.
**Effort:** Simple

---

#### MINOR: Undocumented `engine` and `research` Layers
**ID:** AR-09
**Location:** `game/engine/` (3 modules), `game/research/` (4 modules), `game/assets/` (1 module)
**Issue:** The documented architecture in CLAUDE.md describes Core -> Simulation -> Strategy -> UI layers, with AI depending on Simulation+Strategy. However, three additional packages exist that are not mentioned: `game/engine` (physics, collision, spatial indexing -- used by simulation), `game/research` (tech tree, research tracking -- used by UI), and `game/assets` (asset management singleton). Their dependency relationships are clean (`engine` -> core, `research` -> core, `assets` -> core), but they are not part of the documented architecture.
**Impact:** Developers relying on the architecture documentation won't know about these packages or their intended layer positions. Could lead to incorrect dependency assumptions.
**Recommendation:** Update CLAUDE.md architecture section to document `engine` as a Core-adjacent infrastructure layer, `research` as a peer of strategy, and `assets` as a core utility.
**Effort:** Simple

---

#### MINOR: Residual Duck Typing in Simulation Layer
**ID:** AR-10
**Location:** `game/simulation/components/modifier_introspection.py:142`, `game/simulation/components/abilities/weapons.py:168,255,275-276,331-337`
**Issue:** Despite PROJ-190's introduction of typed protocols for abilities and components, several `hasattr()` and `getattr()` calls remain in the simulation layer for attribute access. For example, `modifier_introspection.py:142` checks `hasattr(mod_def, 'evaluate_effects')` instead of using a protocol, and weapons code uses `getattr(self.component, 'projectile_speed', 500)` for attribute access with defaults.
**Impact:** These patterns bypass the type safety that protocols were meant to provide. Static type checkers cannot verify these accesses.
**Recommendation:** Many of these `getattr` calls are accessing data-driven component attributes that don't have fixed types, so some are inherent to the dynamic data model. Focus on eliminating `hasattr` checks for method existence (like `evaluate_effects`) by adding the method to the relevant protocol.
**Effort:** Medium

---

### Info

#### INFO: Singleton Usage is Appropriate and Controlled
**ID:** AR-11
**Location:** 7 classes using `SingletonMeta`: `RegistryManager`, `AssetManager`, `Profiler`, `StrategyMetadataService`, `StrategyManager`, `ShipThemeManager`, `SpriteManager`, `ScreenshotManager`
**Issue:** Despite the project's preference for DI over singletons (per CLAUDE.md), several singletons remain. However, inspection shows they are all appropriate: `RegistryManager` is the DI root itself, `AssetManager`/`SpriteManager`/`ShipThemeManager`/`ScreenshotManager` are genuine shared resources (asset caches), `Profiler` is cross-cutting infrastructure, and `StrategyMetadataService`/`StrategyManager` are global metadata stores.
**Impact:** None -- these singletons are well-justified and follow the `SingletonMeta` pattern consistently with thread-safe `instance()` access and `reset()` for test cleanup.
**Recommendation:** No change needed. The project correctly distinguishes between DI for domain logic and singletons for infrastructure/resource management.
**Effort:** N/A

---

#### INFO: Clean Layer Separation Verified
**ID:** AR-12
**Location:** Entire `game/` directory
**Issue:** Comprehensive import analysis confirms zero layer violations:
- Core imports nothing from simulation, strategy, UI, engine, research, or assets
- Simulation imports only from core and engine (engine depends only on core)
- Strategy imports only from core and simulation
- AI imports only from core and simulation (not strategy or UI)
- UI imports from all lower layers (expected as top layer)
- No pygame imports in core, simulation, strategy, or AI layers
**Impact:** Positive -- the layered architecture is properly enforced through import discipline.
**Recommendation:** Consider adding an automated import-order check (e.g., `import-linter`) to CI to prevent future regressions.
**Effort:** Simple (tooling)

---

## Top 5 Priority Issues

1. **AR-01 (MAJOR):** UI presentation logic (`get_ui_rows()`, `ui_colors.py`) in simulation layer -- violates layer separation principle and affects portability
2. **AR-04 (MAJOR):** Incomplete facade adoption -- UI bypasses strategy facade DTOs, reducing the value of the facade pattern
3. **AR-02 (MAJOR):** Duplicate `ICombatShip` protocol -- simulation version is dead code, creates naming confusion
4. **AR-03 (MAJOR):** Mixed Protocol/ABC interface patterns -- inconsistent contract definition approach across layers
5. **AR-05 (MINOR):** Triplicated `_has_attrs` helper -- simple consolidation opportunity
