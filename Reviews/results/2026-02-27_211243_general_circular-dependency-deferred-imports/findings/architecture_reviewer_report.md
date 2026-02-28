# Architecture Reviewer Report

## Summary

- **Total issues found:** 8
- **Critical:** 0, **Major:** 2, **Minor:** 4, **Info:** 2

The codebase demonstrates **strong architectural discipline** at the layer boundary level. There are **zero top-level upward layer violations** -- every cross-layer import at module scope flows correctly downward. The architecture docs (ARCHITECTURE.md) are well-maintained and accurately reflect the actual dependency structure.

The findings are concentrated in two areas:
1. **Within-layer circular dependencies** masked by deferred imports (3 chains found)
2. **Lateral cross-layer coupling** between strategy and AI layers (1 instance)

The high volume of deferred imports (272) and TYPE_CHECKING imports (285) across the codebase is a notable observation, though many are documented as intentional patterns.

---

## Layer Dependency Analysis

### Core (`game/core/`)
- **Expected dependencies:** Standard library only
- **Actual dependencies:** Standard library only
- **Status: CLEAN** -- No upward or lateral dependencies. Self-referencing imports within core are all within the same package.

### Engine (`game/engine/`)
- **Expected dependencies:** Core only (low-level physics, below simulation)
- **Actual dependencies:** `game.core.math`, `game.core.config`
- **Status: CLEAN** -- Correctly depends only on core.

### Simulation (`game/simulation/`)
- **Expected dependencies:** Core, Engine
- **Actual dependencies:** `game.core.*`, `game.engine.*`
- **Status: CLEAN** -- No upward dependencies to strategy, UI, or AI. All cross-layer imports are downward. The `game.simulation.interfaces.ai_controller` module defines the IAIController interface (dependency inversion pattern), which AI implements rather than simulation depending on AI.

### Research (`game/research/`)
- **Expected dependencies:** Core only
- **Actual dependencies:** `game.core.json_utils`, `game.core.paths`
- **Status: CLEAN** -- Self-contained module with only core dependencies.

### Strategy (`game/strategy/`)
- **Expected dependencies:** Core, Simulation (via interfaces)
- **Actual dependencies:** `game.core.*`, `game.simulation.*` (via interfaces and serialization), `game.ai.ai_factory` (1 deferred import)
- **Status: MINOR ISSUE** -- One lateral dependency on AI layer via deferred import in `simulation_adapter.py`. This is documented and uses dependency injection to make it optional.

### AI (`game/ai/`)
- **Expected dependencies:** Core, Simulation, Strategy
- **Actual dependencies:** `game.core.*`, `game.simulation.interfaces.*`, `game.simulation.entities.ship` (TYPE_CHECKING), `game.engine.spatial` (TYPE_CHECKING)
- **Status: CLEAN** -- No dependency on strategy or UI. Interestingly, AI does NOT depend on strategy at all, which is cleaner than the documented architecture suggests.

### UI (`game/ui/`)
- **Expected dependencies:** All lower layers
- **Actual dependencies:** `game.core.*`, `game.simulation.*`, `game.strategy.*`, `game.ai.*`, `game.research.*`, `game.assets.*`
- **Status: CLEAN** -- Top layer with expected downward dependencies.

---

## Circular Dependency Chains

Three genuine runtime circular dependency chains were identified through automated analysis. All are within the strategy layer and all are masked by deferred (late) imports.

### Chain 1: galaxy.py <-> galaxy_system_generator.py

- **Files involved:**
  - `game/strategy/data/galaxy.py` (line 21)
  - `game/strategy/data/galaxy_system_generator.py` (line 118)
- **Import direction:**
  - `galaxy.py` imports `GalaxySystemGenerator` from `galaxy_system_generator.py` at **top level** (line 21)
  - `galaxy_system_generator.py` imports `StarSystem` from `galaxy.py` at **deferred** scope (line 118, inside `generate_systems()` method)
- **Masked by deferred import?** Yes -- the return direction is deferred
- **Severity:** Minor
- **Impact:** Low. The `GalaxySystemGenerator` was explicitly extracted from `Galaxy` as part of PROJ-173 (delegation pattern). The deferred import of `StarSystem` is only used during system generation, which happens once during galaxy creation. If the deferred import were moved to top level, Python would raise an `ImportError` due to the circular dependency.
- **Note:** The TYPE_CHECKING block at line 10 of `galaxy_system_generator.py` already imports `Galaxy` and `StarSystem` for type hints, so the deferred runtime import at line 118 is purely for actual object instantiation.

### Chain 2: pathfinding.py <-> fleet_navigation_service.py

- **Files involved:**
  - `game/strategy/data/pathfinding.py` (lines 306, 344)
  - `game/strategy/services/fleet_navigation_service.py` (line 34)
- **Import direction:**
  - `fleet_navigation_service.py` imports `find_hybrid_path`, `strip_start_hex` from `pathfinding.py` at **top level** (line 34)
  - `pathfinding.py` imports `FleetNavigationService` and `NavigationState` from `fleet_navigation_service.py` at **deferred** scope (lines 306, 344)
- **Masked by deferred import?** Yes
- **Severity:** Minor
- **Impact:** Medium. The `pathfinding.py` module provides core pathfinding algorithms (A*, hex-based). The `FleetNavigationService` is a higher-level service that orchestrates navigation using pathfinding. The circular arises because `pathfinding.py` has convenience functions (`project_fleet_path`, `_extract_chaser_info`) that delegate back to `FleetNavigationService`. These convenience functions blur the boundary between the data layer and service layer.
- **Recommendation:** Consider moving `project_fleet_path()` and `_extract_chaser_info()` from `pathfinding.py` into `fleet_navigation_service.py` or a separate utility module, since they are service-level operations that happen to live in the data layer.

### Chain 3: command_handlers.py <-> superweapon_command_handlers.py

- **Files involved:**
  - `game/strategy/engine/command_handlers.py` (line 666)
  - `game/strategy/engine/superweapon_command_handlers.py` (line 15)
- **Import direction:**
  - `superweapon_command_handlers.py` imports `BaseCommandHandler` from `command_handlers.py` at **top level** (line 15)
  - `command_handlers.py` imports superweapon handler classes from `superweapon_command_handlers.py` at **deferred** scope (line 666, inside `create_default_registry()`)
- **Masked by deferred import?** Yes
- **Severity:** Minor
- **Impact:** Low. This is a classic plugin/registry pattern where the base module defines the interface and the plugin module extends it. The deferred import in `create_default_registry()` is the natural way to wire up concrete implementations without creating a hard circular dependency. This is a well-understood pattern.
- **Note:** This could be made slightly cleaner by having `create_default_registry()` accept the handler classes as parameters or by moving the registration to a separate wiring module, but the current approach is pragmatic and clear.

---

## Layer Violations

### Violation 1: Strategy -> AI (Lateral)

- **File:** `game/strategy/adapters/simulation_adapter.py:127`
- **Imports from:** `game.ai.ai_factory.AIControllerFactory`
- **Type:** Deferred (inside method body)
- **Severity:** Minor
- **Context:** The `SimulationBattleResolver` needs an AI controller factory to run headless battles. The import is deferred and only triggered when no factory is injected via constructor. The class supports dependency injection of the AI factory (PROJ-147), making this import a fallback for the default case.
- **Documented:** Yes, explicitly documented in the code comments and in ARCHITECTURE.md's "Intentional Late Imports" (implied by the adapter pattern).
- **Recommendation:** This is an acceptable pattern. The dependency injection path exists for testing and clean architecture. The deferred fallback import keeps the strategy layer usable without requiring explicit AI factory injection in production code.

---

## Findings

### MAJOR: High Volume of Deferred Imports Indicates Structural Coupling

**ID:** AR-001
**Location:** Across `game/strategy/` (108 deferred imports) and `game/ui/` (122 deferred imports)
**Issue:** The strategy and UI layers rely heavily on deferred imports to avoid circular dependencies and manage load order. While each individual deferred import may be justified, the aggregate count (272 total across the codebase) suggests that the module dependency graph has significant coupling within layers. Many deferred imports are repeated (e.g., `FleetOrder, OrderType` is imported inside 10+ different methods in `command_handlers.py`).
**Impact:** Each deferred import adds a small runtime cost (Python's import machinery must check `sys.modules` on each call). More importantly, deferred imports make the dependency graph harder to reason about -- static analysis tools cannot detect all dependencies, and IDE features like "find all references" or "rename symbol" may miss deferred import sites.
**Recommendation:** For repeated deferred imports of the same module within a single file (like `FleetOrder, OrderType` in `command_handlers.py`), consider whether the circular dependency can be broken by restructuring. Where a deferred import is used 5+ times in a single file, it often indicates that the module should be restructured to avoid the circular in the first place.
**Effort:** Complex (ongoing, incremental refactoring)

### MAJOR: Pathfinding Module Has Mixed Responsibilities

**ID:** AR-002
**Location:** `game/strategy/data/pathfinding.py`
**Issue:** The `pathfinding.py` module sits in the `data/` package but contains both pure algorithms (A* pathfinding, hex line drawing) and service-level convenience functions that delegate to `FleetNavigationService`. This mixed responsibility creates the circular dependency with `fleet_navigation_service.py` (Chain 2 above). Functions `project_fleet_path()` (line 306) and `_extract_chaser_info()` (line 344) are service-level orchestration that happen to be placed in the data layer.
**Impact:** The circular dependency between pathfinding and fleet_navigation_service means these modules cannot be imported independently. Changes to either module's interface require careful consideration of the other. The mixed responsibilities also make it harder to test pathfinding algorithms in isolation.
**Recommendation:** Move `project_fleet_path()` to `fleet_navigation_service.py` (it already delegates entirely to `FleetNavigationService.project_path_as_dicts()`). Move `_extract_chaser_info()` and `_ChaserProxy` to a shared utilities module or into `fleet_navigation_service.py` since they deal with `NavigationState` objects. This would break the circular chain entirely.
**Effort:** Medium

### MINOR: Galaxy <-> GalaxySystemGenerator Circular from Extraction

**ID:** AR-003
**Location:** `game/strategy/data/galaxy.py:21` and `game/strategy/data/galaxy_system_generator.py:118`
**Issue:** The `GalaxySystemGenerator` was extracted from `Galaxy` as part of PROJ-173, creating a mutual dependency: Galaxy owns the generator (top-level import), but the generator needs to instantiate `StarSystem` (defined in galaxy.py). This is a natural consequence of extracting a delegate class that creates objects of the parent's types.
**Impact:** Low. The deferred import is only called during galaxy generation (initialization). The circular is well-contained and unlikely to cause issues.
**Recommendation:** Consider whether `StarSystem` could be moved to its own module (e.g., `game/strategy/data/star_system.py`) separate from `Galaxy`. This would break the circular by having both `galaxy.py` and `galaxy_system_generator.py` import from a shared definition module. Alternatively, accept this as a known pattern from the delegation extraction.
**Effort:** Medium

### MINOR: Command Handler Registry Circular

**ID:** AR-004
**Location:** `game/strategy/engine/command_handlers.py:666` and `game/strategy/engine/superweapon_command_handlers.py:15`
**Issue:** The base `command_handlers.py` module defines `BaseCommandHandler` and `CommandHandlerRegistry`, while `superweapon_command_handlers.py` extends `BaseCommandHandler`. The `create_default_registry()` function in `command_handlers.py` then imports all concrete handlers (including superweapon handlers) to register them, creating a circular.
**Impact:** Very low. This is a standard plugin registration pattern. The deferred import in `create_default_registry()` is called once during `GameSession.__init__()`.
**Recommendation:** For maximum cleanliness, the `create_default_registry()` function could be moved to a separate `command_registry_setup.py` module that imports from both `command_handlers.py` and `superweapon_command_handlers.py`. However, this is a low-priority cosmetic improvement.
**Effort:** Simple

### MINOR: Strategy -> AI Lateral Dependency

**ID:** AR-005
**Location:** `game/strategy/adapters/simulation_adapter.py:127`
**Issue:** Strategy layer imports from AI layer (same architectural tier). The ARCHITECTURE.md docs list "Strategy -> Simulation (via interfaces), Core" as allowed dependencies, without mentioning AI. However, the adapter pattern with dependency injection makes this a soft dependency.
**Impact:** Low. The import is deferred, optional (DI fallback), and limited to a single adapter class. The strategy layer can run headless without AI if a mock factory is injected.
**Recommendation:** Consider documenting this lateral dependency explicitly in ARCHITECTURE.md under "Allowed Dependencies" for Strategy, or refactor so the default AI factory is injected at a higher level (e.g., in `game/app.py` or `TurnEngine` initialization) rather than being a fallback inside the adapter.
**Effort:** Simple

### INFO: game.engine Not Documented in Architecture Layer Hierarchy

**ID:** AR-006
**Location:** `docs/architecture/ARCHITECTURE.md`, `game/engine/`
**Issue:** The ARCHITECTURE.md layer diagram shows four layers (UI -> Strategy -> Simulation -> Core), but `game/engine/` is a fifth package that sits between Core and Simulation in the dependency hierarchy. The docs mention `game.engine` in the "Package API Summary" table but do not include it in the layer diagram or dependency rules table. Similarly, `game/research/` and `game/assets/` are not shown in the layer hierarchy.
**Impact:** Informational. New contributors may not understand where `game.engine`, `game.research`, and `game.assets` fit in the dependency hierarchy. The actual dependencies are clean, but the documentation is incomplete.
**Recommendation:** Update the ARCHITECTURE.md layer diagram to include all six packages: Core, Engine, Simulation, Research, Strategy/AI, UI. Show Engine as a sub-layer between Core and Simulation, Research as parallel to Simulation, and Assets as parallel to UI.
**Effort:** Simple

### INFO: Simulation Layer Well-Isolated via Interface Patterns

**ID:** AR-007
**Location:** `game/simulation/interfaces/`
**Issue:** This is a positive finding. The simulation layer defines clear interface contracts (`IAIController`, `IAIControllerFactory`) in `game/simulation/interfaces/ai_controller.py` that the AI layer implements. This dependency inversion pattern means simulation never imports from AI, even though AI behavioral code is tightly coupled to simulation's ship and weapon systems. This is excellent architectural practice.
**Impact:** Positive. The simulation layer can be tested and used completely independently of AI implementations.
**Recommendation:** No changes needed. Consider this as a model pattern for other cross-layer boundaries.
**Effort:** N/A

---

## Deferred Import Statistics

| Layer | Deferred Imports | TYPE_CHECKING Imports | Total Non-Toplevel |
|-------|------------------|-----------------------|--------------------|
| UI | 122 | 116 | 238 |
| Strategy | 108 | 118 | 226 |
| Simulation | 27 | 46 | 73 |
| App | 14 | 0 | 14 |
| Core | 1 | 1 | 2 |
| AI | 0 | 3 | 3 |
| Research | 0 | 1 | 1 |
| **Total** | **272** | **285** | **557** |

The strategy and UI layers account for 84% of all deferred imports, reflecting their position as the most interconnected layers in the codebase.

---

## Top 5 Priority Issues

1. **AR-002 (Major):** Pathfinding module mixed responsibilities creating circular with fleet_navigation_service. This is the most actionable finding -- moving 2-3 functions would eliminate a circular chain entirely.

2. **AR-001 (Major):** High volume of deferred imports across strategy and UI layers. This is a systemic issue that should be addressed incrementally during future refactoring projects, not as a standalone effort.

3. **AR-003 (Minor):** Galaxy <-> GalaxySystemGenerator circular from PROJ-173 extraction. Could be resolved by extracting `StarSystem` to its own module.

4. **AR-005 (Minor):** Strategy -> AI lateral dependency should be documented or restructured.

5. **AR-006 (Info):** Architecture documentation should be updated to include all package layers (engine, research, assets).
