# Architecture Review: Strategy Layer

**Date:** 2026-04-05
**Scope:** `game/strategy/` -- 131 Python files, ~30,600 lines
**Reviewer Focus:** Coupling, layer violations, dependency issues, missing abstractions, architectural antipatterns

---

### Summary
- Total issues found: 12
- Critical: 1, Major: 4, Minor: 5, Info: 2

---

### Findings

#### CRITICAL: AI Layer Import in Strategy Adapter (Late Import Masking Layer Violation)
**ID:** AR-001
**Location:** `game/strategy/adapters/simulation_adapter.py:127`
**Issue:** `SimulationBattleResolver` performs a runtime late import of `game.ai.ai_factory.AIControllerFactory` when no AI factory is injected. Per the architecture docs, Strategy is allowed to depend on Simulation and Core only -- AI is a forbidden dependency. The late import disguises this as optional but it is a hard runtime dependency in the default code path (no tests or production code injects the factory).
**Impact:** Violates the documented layer dependency rules. If AI layer changes its factory interface, strategy layer breaks. The late import hides this from static analysis tools. The comment on line 53 acknowledges this ("late import to avoid module-level AI layer dependency") but avoiding a module-level import does not fix the architectural violation -- it only hides it.
**Recommendation:** The AI factory should always be injected from the UI layer (which is allowed to depend on AI). Remove the fallback late import entirely. Make `ai_factory` a required parameter or have `GameSession`/`TurnEngine` always inject it from above. The `ConflictResolutionEngine` already receives a `battle_resolver` via DI -- extend this pattern so the resolver always receives its AI factory from the caller.
**Effort:** Medium

#### MAJOR: Widespread Facade Bypass -- UI Accesses GameSession Internals Directly
**ID:** AR-002
**Location:** `game/ui/screens/strategy_screen.py:134-156`, `game/ui/screens/strategy_build_queue_manager.py:94-265`, `game/ui/screens/strategy_detail_formatter.py:412-413`, `game/ui/screens/strategy_renderer.py`, `game/ui/screens/strategy_window_manager.py:134`, `game/ui/panels/build_queue_portraits.py`
**Issue:** `StrategyScreen` exposes `session.galaxy`, `session.empires`, `session.player_empire`, `session.enemy_empire`, `session.systems`, and `session.human_player_ids` as convenience properties. At least 6 UI files use these properties to directly access domain objects (Galaxy, Empire, Fleet, Planet) instead of going through `StrategySessionFacade` and receiving DTOs. The `StrategyBuildQueueManager` directly accesses `session.galaxy` for system lookups. The `StrategyDetailFormatter` calls `session.turn_engine.validate_colonize_order()` directly, bypassing the facade's `can_colonize()` method.
**Impact:** Undermines the CQRS-lite pattern entirely. Domain objects are mutable -- UI code could accidentally mutate strategy state. The facade boundary becomes advisory rather than enforced. Adding new query methods to the facade becomes pointless if UI code can just reach through.
**Recommendation:** Remove the convenience properties from `StrategyScreen`. All UI components should use `self._facade` exclusively. For cases where the facade lacks a needed query, add it to the facade rather than bypassing it. This is a significant refactor but is essential to the documented architecture.
**Effort:** Complex

#### MAJOR: data/ Subpackage Depends on engine/ (Upward Dependency)
**ID:** AR-003
**Location:** `game/strategy/data/build_queue_source.py:267`
**Issue:** `build_queue_source.py` (in the `data/` subpackage) imports `_colony_has_planetary_yard` from `game.strategy.engine.production_engine` (a private function from the `engine/` subpackage). The `data/` subpackage should be a lower-level layer containing domain entities and value objects. The `engine/` subpackage contains turn processing logic that depends on `data/`. This creates a bidirectional dependency: `data/ <-> engine/`.
**Impact:** Circular subpackage dependency makes it impossible to reason about either package in isolation. The late import masks the cycle from Python's import system but the logical coupling remains. Changes to `ProductionEngine` internals (a private function) can break `BuildQueueSource`.
**Recommendation:** Extract `_colony_has_planetary_yard` into a shared utility in `game/strategy/services/` (e.g., `component_inspector` or a new `facility_inspector` module). Both `data/build_queue_source.py` and `engine/production_engine.py` should import from that shared location. Alternatively, make it a method on `Planet` or `PlanetaryFacility` if it only needs facility data.
**Effort:** Simple

#### MAJOR: services/ Subpackage Depends on engine/ Commands
**ID:** AR-004
**Location:** `game/strategy/services/cargo_transfer_service.py:12`
**Issue:** `CargoTransferService` (in `services/`) has a top-level import of `IssueTransferCommand` from `game.strategy.engine.commands`. The `services/` subpackage should provide business logic that `engine/` consumes, not depend on engine-specific command types. This creates a `services/ -> engine/` dependency that inverts the expected direction (`engine/ -> services/`).
**Impact:** Makes it harder to test `CargoTransferService` without pulling in the entire engine command infrastructure. Creates a bidirectional dependency between `services/` and `engine/` since engine already depends heavily on services.
**Recommendation:** Either move the command construction into the engine layer (command handlers call cargo transfer service for logic, then construct commands themselves), or move `IssueTransferCommand` to a shared `commands.py` in a neutral location (e.g., `data/` since commands are essentially DTOs/value objects).
**Effort:** Medium

#### MAJOR: 8 of 12 Sub-Engines Do Not Implement Their Interfaces
**ID:** AR-005
**Location:** `game/strategy/engine/production_engine.py`, `game/strategy/engine/conflict_resolution_engine.py`, `game/strategy/engine/fleet_movement_engine.py`, `game/strategy/engine/order_processor.py`, `game/strategy/engine/planet_action_engine.py`, `game/strategy/engine/environmental_hazard_engine.py`, `game/strategy/engine/consumable_management_engine.py`, `game/strategy/engine/planet_energy_engine.py`
**Issue:** `game/strategy/interfaces/engines.py` defines 12 ABC interfaces (e.g., `IMovementEngine`, `IProductionEngine`, `IConflictEngine`). However, only 4 engines formally inherit from their interface: `HarvestingEngine(IHarvestingEngine)`, `PopulationEngine(IPopulationEngine)`, `ActionExecutionEngine(IActionExecutionEngine)`, `ResupplyEngine(IResupplyEngine)`. The remaining 8 engines (ProductionEngine, ConflictResolutionEngine, FleetMovementEngine, OrderProcessor, PlanetActionEngine, EnvironmentalHazardEngine, ConsumableManagementEngine, PlanetEnergyEngine) do not extend their corresponding interfaces.
**Impact:** The interfaces exist but are not enforced. If an engine drifts from its interface contract (e.g., a method signature changes), there is no compile-time or runtime check. TurnEngine's DI system types parameters as `Optional[IMovementEngine]` etc., but the concrete classes don't declare conformance. This makes mock-based testing fragile since mocks implement the interface but the real classes may not match.
**Effort:** Simple (add the base class to each engine's class declaration)

#### MINOR: Excessive Late Imports (334 instances) Suggest Structural Issues
**ID:** AR-006
**Location:** Throughout `game/strategy/` -- 334 function-level `from game.*` imports
**Issue:** The strategy layer contains 334 late (function-level) imports of `game.*` modules. While some are documented intentional late imports (4 listed in `docs/01_ARCHITECTURE.md`), the vast majority are undocumented. The most frequently late-imported modules are `game.strategy.data.planet` (27 times), `game.strategy.data.fleet` (26 times), and `game.strategy.data.galaxy` (18 times). Many of these are in TYPE_CHECKING blocks (which is correct), but a significant portion are runtime late imports inside functions.
**Impact:** Late imports add per-call overhead and obscure the true dependency graph. They often mask circular dependencies that should be resolved structurally. They make it harder for tools and developers to understand what depends on what.
**Recommendation:** Audit late imports and classify them as: (a) TYPE_CHECKING only (fine), (b) documented intentional (fine), (c) hiding a real circular dependency (fix the cycle). Focus on the highest-frequency ones first.
**Effort:** Medium

#### MINOR: RegistryManager.instance() Singleton Access Bypasses DI in data/ Layer
**ID:** AR-007
**Location:** `game/strategy/data/build_queue_source.py:268-269`
**Issue:** `build_queue_source.py` accesses the global `RegistryManager.instance()` singleton directly instead of receiving registries via dependency injection. This is the only place in the `data/` subpackage that does this. The `engine/` subpackage properly uses DI (registries are a required kwarg on TurnEngine and all sub-engines).
**Impact:** Makes `build_queue_source` functions harder to test in isolation since they require the global singleton to be initialized. Inconsistent with the DI pattern used everywhere else in the strategy layer.
**Recommendation:** Add a `registries` parameter to `_collect_planet_queues()` and propagate from the caller. The callers in `engine/` already have registries available.
**Effort:** Simple

#### MINOR: command_handlers.py Is a 1062-Line Monolith
**ID:** AR-008
**Location:** `game/strategy/engine/command_handlers.py` (1062 lines)
**Issue:** This file contains ~20 command handler classes, the `CommandHandlerRegistry`, `BaseCommandHandler` mixin, helper functions, and the `create_default_registry()` factory. While the superweapon and planet handlers have already been extracted to separate files (`superweapon_command_handlers.py`, `planet_command_handlers.py`), the core file is still large.
**Impact:** Large files are harder to navigate, review, and maintain. With 20+ classes, merge conflicts are more likely when multiple features touch command handling.
**Recommendation:** Group related handlers into separate modules (e.g., `fleet_order_handlers.py` for Move/Intercept/Join/Warp, `build_handlers.py` for Build/RemoveBuild/AddToQueue/RemoveFromQueue/Reorder, `fleet_management_handlers.py` for Split/Delete/Reorder). Keep `BaseCommandHandler` and `CommandHandlerRegistry` in the main file.
**Effort:** Medium

#### MINOR: PlanetaryFacility Has Top-Level Import from services/
**ID:** AR-009
**Location:** `game/strategy/data/planetary_facility.py:12`
**Issue:** `PlanetaryFacility` (a `data/` entity) has a top-level import of `get_component_abilities` from `game.strategy.services.component_inspector`. This means the data entity depends on a service at module load time, creating a `data/ -> services/` dependency for a data class.
**Impact:** Data classes should be self-contained value/entity objects. Depending on a service makes `PlanetaryFacility` harder to instantiate in test environments and creates coupling between the data layer and service layer.
**Recommendation:** Move the component abilities check to a method that lazy-imports, or restructure so `PlanetaryFacility` delegates ability checks to a service called by the engine rather than embedding the service call in the data class.
**Effort:** Simple

#### MINOR: data/ Subpackage Has Widespread Upward Dependencies to services/
**ID:** AR-010
**Location:** `game/strategy/data/fleet_capability_calculator.py` (7 imports from services/), `game/strategy/data/fleet.py` (1), `game/strategy/data/pathfinding.py` (3), `game/strategy/data/ship_instance.py` (1), `game/strategy/data/build_queue_source.py` (3), `game/strategy/data/planetary_facility.py` (1)
**Issue:** Multiple files in the `data/` subpackage import from `services/`. While most of these are late imports (reducing the import-time coupling), they represent a logical dependency direction issue: domain entities should not depend on services. The `FleetCapabilityCalculator` delegate is the worst offender with 7 service imports (component_inspector, ship_stats_calculator).
**Impact:** The `data/` subpackage cannot be understood or tested without the `services/` subpackage. This makes the dependency graph `data/ <-> services/ <-> engine/` rather than the cleaner `engine/ -> services/ -> data/`.
**Recommendation:** Consider inverting the dependency: instead of fleet capability calculator (on Fleet) calling services directly, have the engine or a higher-level coordinator call the service and pass results to the data objects. Alternatively, accept that delegates blur the data/service boundary and document this as an intentional pattern.
**Effort:** Complex

#### INFO: Facade Returns Domain Objects via Internal Helpers
**ID:** AR-011
**Location:** `game/strategy/facade/strategy_session_facade.py:83-94`
**Issue:** The facade's `_get_fleet_by_id()` and `_get_empire_by_id()` helpers return raw domain objects (Fleet, Empire). While these are private methods used internally by the facade to then convert to DTOs, the pattern means the facade holds references to mutable domain objects. The public methods correctly convert to DTOs before returning.
**Impact:** Minimal -- the pattern is correct since the private helpers are only used internally. However, if a future developer adds a public method that forgets the DTO conversion, domain objects would leak.
**Recommendation:** No immediate action needed. Consider adding a lint rule or comment convention to ensure all public methods convert to DTOs. The existing code is correct.
**Effort:** Simple

#### INFO: Documentation Lists Strategy as Forbidden from Importing Engine Layer
**ID:** AR-012
**Location:** `docs/01_ARCHITECTURE.md` dependency table vs actual code
**Issue:** The architecture docs show `Strategy -> Simulation, Core` as the allowed dependencies. However, the `game/engine/` layer (physics, collision, spatial) is not listed as an allowed dependency for Strategy. In practice, Strategy does not import from `game/engine/` directly (confirmed by grep), so there is no violation. The Simulation layer is the intermediary. This finding is purely informational -- the code is correct.
**Impact:** None. The code correctly avoids importing from `game/engine/`.
**Recommendation:** No action needed. The architecture is properly followed for engine layer separation.
**Effort:** N/A

---

### Top 5 Priority Issues

1. **AR-002 (MAJOR): Facade Bypass** -- The most architecturally damaging issue. Six UI files access GameSession internals directly, undermining the CQRS-lite pattern that is the documented primary interface boundary. This should be the top refactoring priority as it affects the entire UI-strategy contract.

2. **AR-001 (CRITICAL): AI Layer Violation** -- The only true cross-layer dependency violation. While masked by a late import, the strategy layer has a runtime dependency on the AI layer in its default code path. Fix by requiring AI factory injection from above.

3. **AR-005 (MAJOR): Engines Missing Interface Inheritance** -- 8 of 12 sub-engines don't formally implement their ABC interfaces. This is a quick win (simple effort) that would immediately improve type safety and catch contract drift.

4. **AR-003 (MAJOR): data/ -> engine/ Circular Dependency** -- `BuildQueueSource` importing a private function from `ProductionEngine` creates a bidirectional dependency between subpackages. Simple fix by extracting to shared services.

5. **AR-004 (MAJOR): services/ -> engine/ Dependency Inversion** -- `CargoTransferService` depending on engine command types inverts the expected dependency direction. Should be resolved to maintain clean layering within the strategy package.
