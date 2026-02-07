# Architecture & Layer Violations

**Theme:** Cross-layer dependencies, circular imports, dependency injection issues, and architectural boundary violations.

---

## Critical Issues

### AR-001: Core Layer Dependency on Strategy Layer
**ID:** AR-001
**Location:** `game/core/registry.py:10` -> `game/strategy/services/ship_stats_service.py`
**Issue:** The core layer (game/core) imports from the strategy layer (game/strategy), violating the dependency hierarchy. Specifically, registry.py uses ShipStatsService in its module docstring example code.
**Impact:** Creates circular dependency risk, violates layering principle, core becomes less reusable
**Recommendation:** Move registry-strategy integration to a higher layer adapter. Keep core independent of all application layers.
**Effort:** Medium

---

### AR-002: Core Layer Dependency on Strategy Layer - Type Hints
**ID:** AR-002
**Location:** `game/core/protocols.py:37` -> `game/strategy/data/hex_math.py`
**Issue:** Core protocols module imports HexCoord type from strategy layer inside TYPE_CHECKING block. While this uses TYPE_CHECKING, it still creates a hard dependency on strategy layer internals.
**Impact:** Makes core aware of strategy implementation details, violates separation of concerns
**Recommendation:** Move HexCoord to a shared data types module or core layer
**Effort:** Medium

---

### AR-003: Engine Layer Dependency on Simulation Layer
**ID:** AR-003
**Location:** `game/engine/collision.py:56` (TYPE_CHECKING) -> `game/simulation/entities/ship.py`
**Issue:** Engine layer (core infrastructure) depends on simulation layer's Ship class, even if only in TYPE_CHECKING. Engine should be simulation-agnostic.
**Impact:** Engine cannot be reused for different simulation implementations
**Recommendation:** Use protocol-based type hints instead of concrete Ship class. Define IShip protocol in core/protocols.py
**Effort:** Medium

---

### AR-004: Excessive Deferred Imports Indicating Circular Dependencies
**ID:** AR-004
**Location:** Multiple files across strategy and simulation layers
**Issue:** 20+ late imports (inside function bodies) detected in files like:
- `game/strategy/data/fleet.py:88,110,128,573` (FleetMobilityService, ShipStatsService, ShipInstance)
- `game/strategy/engine/turn_engine.py:72,92,100,108,116,124,165` (SimulationBattleResolver, validation)
- `game/simulation/entities/ship.py:262,517,558` (Abilities, ModifierService)
- `game/simulation/systems/stats.py:20,172,173,337,429` (ResourceManager, Abilities, WeaponAbility)

**Impact:** Runtime import overhead, harder to detect import errors at startup, maintainability issues
**Recommendation:** Restructure modules to eliminate circular dependency chains. Use dependency injection to pass dependencies rather than importing them.
**Effort:** Complex

---

### AR-01 (Duplicate Report): UI Layer Directly Instantiates Simulation Objects
**ID:** AR-01
**Location:** `game/ui/screens/setup.py:94-128`, `game/ui/screens/builder/main.py:90`, `game/ui/screens/workshop_screen.py:18-38`
**Issue:** UI code directly creates `Ship` objects and accesses/modifies their internal attributes. UI layer imports directly from `game.simulation.entities.ship`.
**Impact:** Violates layered architecture. Changes to ship internals break UI code. Cannot swap simulation implementations.
**Recommendation:** Create UI-facing Ship DTO/Command pattern. UI should issue commands rather than directly mutating ships.
**Effort:** Complex

---

### AR-02: Global Mutable State in Core Registries
**ID:** AR-02
**Location:** `game/simulation/components/component.py:74-75`, `game/core/registry.py:92-93`
**Issue:** Shared global state (`COMPONENT_REGISTRY`, `MODIFIER_REGISTRY`, `VEHICLE_CLASSES`) exposed as module-level variables. 77 files import from `game.core.config`.
**Impact:** Cannot safely run tests in parallel. Registry state persists between tests/scenes. Hidden dependencies.
**Recommendation:** Migrate to dependency injection via `GameRegistries` container. Use constructor injection.
**Effort:** Complex

---

## Major Issues

### AR-005: UI Layer Importing Directly from Simulation Layer
**ID:** AR-005
**Location:** Multiple UI files importing simulation components
**Issue:** UI screens directly import from simulation layer:
- `game/ui/screens/battle_scene.py:23,26-27` imports BattleService, BattleController, Ship
- `game/ui/screens/build_queue_screen.py:21` imports SimulationDesignLoader
- `game/ui/hud/panels.py:15` imports ComponentStatus

**Impact:** UI tightly coupled to simulation implementation, violates MVC/MVVM principles, UI cannot be tested without simulation
**Recommendation:** Create UI adapter layer. Use facade pattern (like StrategySessionFacade) for simulation access. Pass data objects instead of domain objects.
**Effort:** Complex

---

### AR-006: Circular Import in UI Package
**ID:** AR-006
**Location:** `game/ui/__init__.py:4` (comment) and workshop_screen.py
**Issue:** Documentation explicitly states "workshop_screen is NOT eagerly imported here to avoid circular dependency with ui.builder package"
**Impact:** Forces lazy imports, complicates module initialization, test discovery issues
**Recommendation:** Refactor builder and workshop_screen to remove circular dependency. Extract shared interfaces to separate module.
**Effort:** Complex

---

### AR-007: UI Layer Importing from Strategy Layer Too Directly
**ID:** AR-007
**Location:** Multiple UI screens importing strategy data models directly
**Issue:** UI screens import strategy data structures directly:
- `game/ui/screens/build_queue_screen.py:19-20` imports Planet, DesignLibrary
- `game/ui/screens/race_setup_screen.py:23-24` imports RaceConfig, RaceLibrary
- `game/ui/screens/builder/component_ref.py:31-32` imports LayerType, Component

**Impact:** UI tightly coupled to strategy/simulation data models, API fragility, testing difficulty
**Recommendation:** Create data transfer objects (DTOs) layer. UI should work with UI-specific models, not domain models.
**Effort:** Complex

---

### AR-008: God Module - BuilderSceneGUI
**ID:** AR-008
**Location:** `game/ui/screens/builder/main.py`
**Issue:** BuilderSceneGUI class (lines 72-1200+) imports from:
- Simulation layer: Ship, VEHICLE_CLASSES, components, ShipIO, MODIFIER_REGISTRY
- AI layer: StrategyManager
- 12 distinct game module imports

**Impact:** Difficult to test, maintain, or refactor independently
**Recommendation:** Refactor to use dependency injection and facade pattern.
**Effort:** Medium

---

### AR-04: Circular Dependency Risk - Strategy <-> Simulation
**ID:** AR-04
**Location:** `game/strategy/adapters/simulation_adapter.py:24-27`, `game/strategy/services/ship_stats_service.py:27-28`
**Issue:** Strategy layer imports directly from simulation layer. While currently one-directional, tight coupling creates risk.
**Impact:** Strategy layer cannot be tested independently. Changes to simulation break strategy layer.
**Recommendation:** Strategy layer should only depend on `IBattleResolver` interface and DTOs.
**Effort:** Medium

---

### STR-004: Tight Coupling Between Strategy and Simulation Layers
**ID:** STR-004
**Location:** `game/strategy/adapters/simulation_adapter.py:24-142`, `game/strategy/data/fleet.py:425-508`
**Issue:** Direct imports of simulation layer in strategy:
- `fleet.to_battle_ships()` creates simulation `Ship` objects directly
- `SimulationBattleResolver` imports `BattleController`, `BattleService` directly
- `ShipInstance.to_ship()` directly calls `ShipSerializer.from_dict()`
**Impact:** Cannot swap simulation implementations; circular dependency risk
**Recommendation:**
1. Create strategy-layer `IBattleEntity` interface
2. Move `to_battle_ships()` logic behind an adapter
3. Use dependency injection to provide the builder
**Effort:** Complex

---

### SIM-002: Circular Import Prevention Using Late Binding and Type Hints
**ID:** SIM-002
**Location:** `game/simulation/entities/ship_combat.py:26-37`, `game/simulation/managers/battle_state_manager.py:76`, `game/simulation/entities/ship_stats.py:71`
**Issue:** Multiple instances of deferred imports inside methods to avoid circular dependencies. Pattern: `from module import Class` inside method bodies rather than at module level.
**Impact:** Hides circular dependency problems, makes code harder to follow, performance penalty on method calls, difficult to understand true dependencies.
**Recommendation:** Resolve circular imports properly using dependency injection or reorganizing module structure. Document explicit interfaces between modules.
**Effort:** Complex

---

### SIM-008: Tight Coupling Between BattleEngine and AIController
**ID:** SIM-008
**Location:** `game/simulation/systems/battle_engine.py:212-236, 272-284, 433-435`
**Issue:** BattleEngine creates AIController internally with hardcoded imports when not provided. Creates circular dependency risk.
**Impact:** Engine cannot be tested without AI layer, difficult to swap implementations, violates single responsibility.
**Recommendation:** Require AIControllers to be passed at initialization. Remove internal creation. Make proper interface/protocol definition.
**Effort:** Medium

---

### CQ-036: Unclear Layering
**ID:** CQ-036
**Location:** Throughout codebase
**Issue:** Cross-imports between UI, Strategy, and Simulation layers; no clear boundaries
**Impact:** Circular dependencies possible; hard to reason about data flow
**Recommendation:** Enforce strict layer boundaries; create explicit Adapter/Facade layer
**Effort:** Complex

---

### UI-024: Layer Violations - UI Directly Using Simulation Components
**ID:** UI-024
**Location:** Multiple files with cross-layer imports
**Issue:** UI layer imports directly from simulation layer.
**Recommendation:** Create UI-layer facades/services.
**Effort:** Complex

---

## Minor Issues

### AR-011: Global Singletons Overuse
**ID:** AR-011
**Location:** 30+ files using .instance() pattern
**Issue:** Extensive use of singletons for RegistryManager, SpriteManager, StrategyManager, AIController. Testing challenges and prevents proper DI migration.
**Impact:** Hard to test, violates DI principles, state sharing issues
**Recommendation:** Complete PROJ-38 migration to DI. Make .instance() private/deprecated.
**Effort:** Medium

---

### AR-013: AI Layer Cross-Cutting Concerns
**ID:** AR-013
**Location:** `game/ai/target_evaluator.py` -> `game/simulation/components/component_constants.py`
**Issue:** AI layer imports from simulation to use LayerType constant. This couples AI to simulation implementation details.
**Impact:** AI cannot be evolved independently, component changes break AI
**Recommendation:** Extract shared constants to core/constants.py or create AI-specific enum
**Effort:** Simple

---

### AR-014: Missing Public API Definition
**ID:** AR-014
**Location:** Most packages lack coherent __init__.py exports
**Issue:** Packages have inconsistent __init__.py organization. No clear public vs. private module distinction.
**Impact:** Unclear package contracts, encourages implementation import, refactoring harder
**Recommendation:** Create explicit public API in each package's __init__.py with __all__
**Effort:** Simple

---

### AR-05: LayerType Constant Duplication
**ID:** AR-05
**Location:** Multiple files reference `LayerType` from different import paths
**Issue:** `LayerType` defined in `game.simulation.components.component_constants` but imported from `game.core.constants` in UI files.
**Impact:** Confusing and error-prone. Layering violation.
**Recommendation:** Move `LayerType` to single canonical location. Update all files.
**Effort:** Medium

---

### AR-06: No Clean Interface Between UI and Battle Layers
**ID:** AR-06
**Location:** `game/ui/screens/battle_scene.py:23-26`, `game/ui/hud/panels.py:3-17`
**Issue:** UI battle code imports directly from simulation. Battle panels directly access ship objects.
**Impact:** Battle UI tightly coupled to simulation internals. Cannot mock for UI testing.
**Recommendation:** Create `IBattleUI` service interface exposing only what UI needs.
**Effort:** Medium

---

### AR-09: Missing Abstraction for Component System Access
**ID:** AR-09
**Location:** `game/ui/screens/builder/modifier_logic.py:8`, `game/simulation/components/component.py:74-75`
**Issue:** Direct access to `MODIFIER_REGISTRY` and `COMPONENT_REGISTRY` globals from UI code.
**Impact:** UI tightly coupled to registry structure. Cannot change registry implementation.
**Recommendation:** Create `ComponentService` interface with get_components(), get_modifiers() methods.
**Effort:** Simple

---

### AR-10: Validation Logic Scattered Across Layers
**ID:** AR-10
**Location:** `game/simulation/systems/validator.py`, `game/ui/screens/race_validator.py`, `game/strategy/validation/base.py`
**Issue:** Validation rules scattered across simulation, UI, and strategy layers.
**Impact:** Consistency issues. UI might allow invalid state that simulation rejects.
**Recommendation:** Create unified `ValidationEngine` in core layer.
**Effort:** Medium

---

## Info Issues

### AR-015: TYPE_CHECKING Pattern Correctly Used
**ID:** AR-015
**Location:** Various files
**Issue:** Positive finding - proper use of TYPE_CHECKING to avoid circular import issues at runtime
**Impact:** Good practice
**Recommendation:** Continue this pattern
**Effort:** N/A

---

### AR-016: Facade Pattern Implemented
**ID:** AR-016
**Location:** `game/strategy/facade/strategy_session_facade.py`
**Issue:** Positive finding - StrategySessionFacade properly encapsulates strategy layer for UI consumption
**Impact:** Reduces coupling, good separation
**Recommendation:** Expand facade pattern to other layers (SimulationFacade, AiFacade)
**Effort:** N/A

---

## Architecture Diagram

```
Current State (PROBLEMATIC):

    game/ui/
        +-> game/strategy/ (direct imports of data models)
        +-> game/simulation/ (direct imports of entities & services)
        +-> game/core/

    game/strategy/
        +-> game/simulation/ (via adapter layer - OK)
        +-> game/core/ (direct imports - VIOLATION)
        +-> game/engine/ (via collision.py - VIOLATION)

    game/simulation/
        +-> game/core/ (OK)

    game/engine/
        +-> game/simulation/ (TYPE_CHECKING - VIOLATION)

    game/core/
        +-> game/strategy/ (CRITICAL VIOLATION)

Expected Dependency Flow (Top to Bottom):
1. UI (game/ui/) - depends on Strategy, Core
2. Strategy (game/strategy/) - depends on Simulation, Core, via Adapters
3. Simulation (game/simulation/) - depends on Core, Engine
4. Engine (game/engine/) - depends on Core only
5. Core (game/core/) - standalone
```

---

## Top Priority Issues

1. **AR-001/AR-002: Core Layer Dependencies on Strategy** - Fix registry.py and protocols.py imports to break circular dependency chain
2. **AR-004: Excessive Deferred Imports** - Systematic refactoring needed to eliminate 20+ late imports
3. **AR-005/AR-007: UI Layer Direct Imports** - Decouple UI from simulation/strategy via adapter/facade pattern
4. **AR-006: Circular Import in UI Package** - Refactor workshop_screen/builder relationship
5. **AR-02: Global Mutable State** - Complete PROJ-38 migration to dependency injection
