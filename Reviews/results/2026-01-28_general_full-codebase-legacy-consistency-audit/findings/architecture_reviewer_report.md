# Architecture Reviewer Report

## Summary
- **Total issues found:** 16
- **Critical:** 4, **Major:** 6, **Minor:** 4, **Info:** 2

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

### AR-009: Constructor Parameter Overload - UI Components
**ID:** AR-009
**Location:** `game/ui/screens/builder/structure_list_items.py`
**Issue:** Multiple UI component classes have excessive constructor parameters (9+ params):
- `IndividualComponentItem.__init__` (9 params)
- `LayerHeaderItem.__init__` (9 params)
- `ComponentGroupItem.__init__` (10+ params)

**Impact:** Difficult to instantiate, violates Single Responsibility Principle
**Recommendation:** Use builder pattern or configuration objects.
**Effort:** Simple

---

### AR-010: Deferred Imports in Strategy Layer - Structural Issue
**ID:** AR-010
**Location:** `game/strategy/engine/turn_engine.py:37-42,72,92,100,108,116,124,165`
**Issue:** TurnEngine imports core engines at module level but then re-imports them inside methods. This indicates circular dependency or initialization order sensitivity.
**Impact:** Fragile initialization, performance degradation, maintainability
**Recommendation:** Ensure all imports are at module level. If circular, restructure to break cycle.
**Effort:** Medium

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

### AR-012: Deprecated API Still in Heavy Use
**ID:** AR-012
**Location:** `game/core/registry.py:298-365`
**Issue:** Deprecated functions are marked with DeprecationWarning but still widely used. No actual removal deadline.
**Impact:** Legacy code paths difficult to refactor, PROJ-38 migration stalled
**Recommendation:** Set removal date (3-6 months), actively migrate consumers to GameRegistries DI pattern
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
        ├─> game/strategy/ (direct imports of data models)
        ├─> game/simulation/ (direct imports of entities & services)
        └─> game/core/

    game/strategy/
        ├─> game/simulation/ (via adapter layer - OK)
        ├─> game/core/ (direct imports - VIOLATION)
        └─> game/engine/ (via collision.py - VIOLATION)

    game/simulation/
        └─> game/core/ (OK)

    game/engine/
        └─> game/simulation/ (TYPE_CHECKING - VIOLATION)

    game/core/
        └─> game/strategy/ (CRITICAL VIOLATION)

Expected Dependency Flow (Top to Bottom):
1. UI (game/ui/) - depends on Strategy, Core
2. Strategy (game/strategy/) - depends on Simulation, Core, via Adapters
3. Simulation (game/simulation/) - depends on Core, Engine
4. Engine (game/engine/) - depends on Core only
5. Core (game/core/) - standalone
```

---

## Top 5 Priority Issues

1. **AR-001: Core Layer Dependency on Strategy** - Fix registry.py imports to break circular dependency chain
2. **AR-004: Excessive Deferred Imports** - Systematic refactoring needed to eliminate 20+ late imports
3. **AR-005: UI Layer Direct Simulation Import** - Decouple UI from simulation via adapter/facade pattern
4. **AR-007: UI Importing Strategy Data Models** - Implement DTO layer between UI and domain layers
5. **AR-006: Circular Import in UI Package** - Refactor workshop_screen/builder relationship
