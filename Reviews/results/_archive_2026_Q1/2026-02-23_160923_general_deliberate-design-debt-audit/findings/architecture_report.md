# Architecture Reviewer Report

## Summary
- Total issues found: 23
- Critical: 2, Major: 10, Minor: 8, Info: 3

## Findings

### CRITICAL: game.engine Layer Ambiguity
**ID:** AR-001
**Location:** `game/engine/` (physics.py, collision.py, spatial.py)
**Issue:** The game.engine package sits outside the documented layer architecture (Core, Simulation, Strategy, UI, AI). PhysicsBody is imported by simulation layer (Ship), creating unclear ownership.
**Impact:** Unclear which layer owns physics concerns. Ship inherits from PhysicsBody but engine's tier is undefined.
**Deliberate?:** Likely accidental - CLAUDE.md doesn't mention engine layer.
**Recommendation:** Move engine contents into simulation layer as game/simulation/physics/ or elevate to documented layer.
**Effort:** Medium

### CRITICAL: RegistryManager Singleton God Object
**ID:** AR-002
**Location:** `game/core/registry.py:122-230`
**Issue:** RegistryManager is a singleton holding all game data plus validator and freeze state. Single point of mutation for the entire game.
**Impact:** Global mutable state makes testing harder, creates hidden dependencies, violates SRP.
**Deliberate?:** Likely deliberate for pragmatic reasons (centralized data management, test reset convenience).
**Recommendation:** Split into DataRegistry (immutable data), RegistryLifecycle (freeze/clear), RegistryHydration (loading).
**Effort:** Complex

### MAJOR: Ship God Class
**ID:** AR-003
**Location:** `game/simulation/entities/ship.py` (810 lines, 41 methods)
**Issue:** Massive god class handling physics, combat, stats, components, serialization, formation, validation, and resources. Mixins extracted but class still coordinates all behavior.
**Impact:** High coupling, difficult to test individual responsibilities.
**Deliberate?:** Partially - PROJ-88 documents this. Facade/delegate pattern chosen to preserve Ship as public API.
**Recommendation:** Complete PROJ-88 decomposition.
**Effort:** Complex

### MAJOR: GameSession Command Handler Registry Not Injected
**ID:** AR-004
**Location:** `game/strategy/engine/game_session.py:82`, `game/strategy/engine/command_handlers.py`
**Issue:** CommandHandlerRegistry created internally rather than injected, coupling GameSession to specific implementations.
**Impact:** Cannot easily swap handlers for testing.
**Deliberate?:** Likely deliberate pragmatism.
**Recommendation:** Accept command_registry as optional constructor parameter.
**Effort:** Simple

### MAJOR: Singleton Overuse for Cross-Cutting Concerns
**ID:** AR-005
**Location:** Logger, Profiler, SpriteManager, ScreenshotManager, ShipThemeManager, AssetManager, RegistryManager, StrategyManager
**Issue:** All use singleton pattern creating hidden dependencies.
**Impact:** Tests must call .reset() to isolate state.
**Deliberate?:** Likely deliberate - convenient global access.
**Recommendation:** Consider lazy singleton via DI container. For stateful managers prefer injection.
**Effort:** Medium per manager

### MAJOR: TestLabScreen God Class
**ID:** AR-006
**Location:** `game/ui/screens/test_lab/screen.py` (1906 lines)
**Issue:** Largest file in codebase. Despite helper extraction, main class still coordinates everything.
**Impact:** Difficult to understand control flow.
**Deliberate?:** Partially - extraction shows awareness, but coordinator too large.
**Recommendation:** Extract TestLabController, TestLabRenderer, TestLabEventRouter.
**Effort:** Complex

### MAJOR: StrategyScreen Decomposition Incomplete
**ID:** AR-007
**Location:** `game/ui/screens/strategy_screen.py` (823 lines, 46 methods)
**Issue:** Despite extraction of renderer, input handler, etc., still coordinates all strategy UI and bypasses StrategySessionFacade via convenience properties.
**Impact:** Too many responsibilities, facade pattern undermined.
**Deliberate?:** Likely deliberate pragmatism.
**Recommendation:** Remove convenience properties, force all access through facade.
**Effort:** Medium

### MAJOR: Galaxy Data + Behavior God Class
**ID:** AR-008
**Location:** `game/strategy/data/galaxy.py` (928 lines)
**Issue:** Handles data storage, spatial queries, generation logic, pathfinding, serialization, and fleet queries.
**Impact:** High coupling between data model and algorithms.
**Deliberate?:** Likely accidental growth.
**Recommendation:** Split into GalaxyData, GalaxySpatialIndex, GalaxyGenerator. Keep Galaxy as facade.
**Effort:** Medium

### MAJOR: BattleController God Class
**ID:** AR-009
**Location:** `game/simulation/battle_controller.py` (659 lines)
**Issue:** Handles config, state, retreat, reinforcement, results, save/load, and mode dispatch. Despite extraction of helpers, still too central.
**Impact:** Complex control flow, many responsibilities.
**Deliberate?:** Partially.
**Recommendation:** Extract BattleSetup, BattleResultsCollector, BattlePersistence.
**Effort:** Medium

### MAJOR: Component Lifecycle Complexity
**ID:** AR-010
**Location:** `game/simulation/components/component.py` (723 lines)
**Issue:** Despite helper extraction, Component still coordinates abilities, modifiers, stats, resources, health, serialization, and layer assignment. 4-phase initialization.
**Impact:** Complex initialization, hard to understand state transitions.
**Deliberate?:** Partially.
**Recommendation:** ComponentBuilder pattern for initialization.
**Effort:** Medium

### MAJOR: app.py Scene Management Coupling
**ID:** AR-011
**Location:** `game/app.py` (705 lines)
**Issue:** Game class directly instantiates all scenes and manages lifecycle. Tight coupling to concrete implementations.
**Impact:** Cannot easily mock scenes for testing.
**Deliberate?:** Likely deliberate.
**Recommendation:** Extract SceneFactory and SceneManager.
**Effort:** Medium

### MAJOR: TYPE_CHECKING Pattern (130 files)
**ID:** AR-012
**Location:** 130 files use `if TYPE_CHECKING:` guards
**Issue:** Heavy use suggests many circular dependency risks. Guards prevent runtime issues but indicate tight coupling.
**Impact:** Masks underlying coupling problems.
**Deliberate?:** Deliberate workaround for bi-directional relationships.
**Recommendation:** Accept as necessary evil. Focus on breaking unnecessary cycles.
**Effort:** Complex

### MINOR: PhysicsBody Lacks Abstraction
**ID:** AR-013
**Location:** `game/engine/physics.py:55-113`
**Issue:** Concrete class with hardcoded drag model, no interface.
**Deliberate?:** Likely deliberate simplicity.
**Recommendation:** Extract IPhysicsBody protocol if physics variations needed.
**Effort:** Simple

### MINOR: StrategySessionFacade Underutilized
**ID:** AR-014
**Location:** `game/strategy/facade/strategy_session_facade.py`
**Issue:** Created for clean UI-to-engine communication but StrategyScreen still accesses GameSession directly.
**Deliberate?:** Likely deliberate pragmatism.
**Recommendation:** Remove direct property access, force facade usage.
**Effort:** Simple

### MINOR: Singleton Reset Pattern for Testing
**ID:** AR-015
**Location:** All SingletonMeta classes
**Issue:** Tests must manually call .reset(). Error-prone.
**Deliberate?:** Deliberate pattern.
**Recommendation:** Auto-reset fixture in conftest.py.
**Effort:** Simple

### MINOR: Missing Abstraction for Battle Result
**ID:** AR-016
**Location:** strategy/interfaces/battle_resolver.py, simulation/battle_state.py
**Issue:** BattleResult (strategy) and BattleResults (simulation) are separate with conversion.
**Deliberate?:** Deliberately separate for layer independence.
**Recommendation:** Accept as correct layer isolation.
**Effort:** N/A

### MINOR: InputMapper Global State
**ID:** AR-017
**Location:** `game/ui/services/input_mapper.py`
**Issue:** Stateful, passed around but could desync if multiple instances.
**Deliberate?:** Likely deliberate - one instance per app lifetime.
**Recommendation:** Make singleton or inject via DI container.
**Effort:** Simple

### MINOR: ResourceManager in simulation.systems
**ID:** AR-018
**Location:** `game/simulation/systems/resource_manager.py`
**Issue:** Resources are core concepts but placed in simulation. Strategy imports from simulation for core data.
**Deliberate?:** Likely accidental placement.
**Recommendation:** Move to game/core/resources.py and consolidate.
**Effort:** Simple

### MINOR: BattleConfig vs BattleSetup Ambiguity
**ID:** AR-019
**Location:** simulation/battle_config.py, ui/screens/setup_screen.py
**Issue:** Similar names in different layers cause confusion.
**Deliberate?:** Likely accidental.
**Recommendation:** Rename BattleSetupScreen to BattlePreparationScreen.
**Effort:** Simple

### MINOR: Protocol Pattern Proliferation
**ID:** AR-020
**Location:** `game/core/protocols.py` (18 interfaces)
**Issue:** Many small protocol definitions to maintain.
**Deliberate?:** Deliberate from PROJ-40.
**Recommendation:** Accept. Consider grouping related protocols.
**Effort:** N/A

### INFO: God Class Decomposition Active
**ID:** AR-021
**Issue:** PROJ-86/87/88/89 actively decomposing god classes with facade/delegate pattern.
**Deliberate?:** Yes.

### INFO: Strong Layer Separation
**ID:** AR-022
**Issue:** ZERO layer violations found. No UI imports in simulation, no pygame in simulation/core/strategy.
**Deliberate?:** Yes - deliberately enforced.
**Recommendation:** Maintain. Consider automated linting.

### INFO: DI Pattern Adoption
**ID:** AR-023
**Issue:** Strong DI with GameRegistries container, strict DI enforcement, TestRegistryProvider.
**Deliberate?:** Yes - PROJ-38, PROJ-50.
**Recommendation:** Continue. Consider GameServices container for non-registry dependencies.

## Top 5 Priority Issues

1. **AR-001 (CRITICAL):** game.engine Layer Ambiguity — foundational question
2. **AR-002 (CRITICAL):** RegistryManager Singleton God Object — central mutable state
3. **AR-003 (MAJOR):** Ship God Class — planned in PROJ-88
4. **AR-005 (MAJOR):** Singleton Overuse — affects testability
5. **AR-007 (MAJOR):** StrategyScreen Direct Session Access — quick win
