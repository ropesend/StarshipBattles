# Architecture Drift Sweep: Strategy

## Summary
- **Shard:** Strategy
- **Files Scanned:** 92
- **Total Issues Found:** 6
- **Critical:** 1 | **Major:** 3 | **Minor:** 1 | **Info:** 1

## Findings

#### CRITICAL: AI Layer Dependency from Strategy Layer
**ID:** ADR-STR-001
**Location:** `game/strategy/adapters/simulation_adapter.py:29`
**Issue:** The strategy layer directly imports from the AI layer (`from game.ai.ai_factory import AIControllerFactory`). According to the architecture rules, Strategy should depend only on Core and Simulation - NOT on AI.
**Impact:** The architecture diagram shows AI depends on Strategy, not the other way around. This creates a potential circular dependency risk and violates layer separation. The strategy layer should not need to know about AI implementation details.
**Recommendation:** Extract an interface `IAIControllerFactory` in the strategy layer (or simulation layer) and inject the AI factory from a higher layer. The `SimulationBattleResolver` should receive the AI factory via dependency injection rather than importing it directly.
**Effort:** Medium

#### MAJOR: God Class - Galaxy (914 lines)
**ID:** ADR-STR-002
**Location:** `game/strategy/data/galaxy.py:1-914`
**Issue:** The Galaxy class exceeds 500 lines (914 lines) and handles multiple responsibilities: system storage, planet registration, fleet registration, zone management, warp lane generation, pathfinding support, and serialization.
**Impact:** Large classes are harder to test, maintain, and understand. Changes to one responsibility risk breaking others. The class has accumulated functionality that could be split into focused services.
**Recommendation:** Extract concerns into focused classes:
- `GalaxyRegistry` - Entity registration (planets, fleets, zones)
- `WarpLaneGenerator` - Warp lane generation logic (lines 523-847)
- `GalaxySpatialIndex` - Spatial lookup methods
Keep Galaxy as a thin orchestrator/facade.
**Effort:** Complex

#### MAJOR: Late Import to Avoid Circular Dependency
**ID:** ADR-STR-003
**Location:** `game/strategy/data/galaxy.py:468-469`
**Issue:** Comment explicitly states "Import here to avoid circular dependency" for `RandomPlacementStrategy` and `SpatialIndex`. This indicates a structural issue where the galaxy module has bidirectional dependencies with generation modules.
**Impact:** Circular dependencies indicate design issues where modules are too tightly coupled. Late imports mask the problem but don't solve it. They also add runtime overhead and make dependency graphs harder to reason about.
**Recommendation:** Consider:
1. Move placement strategy injection to a factory method in a separate module
2. Extract system generation into a dedicated `GalaxyGenerator` class that uses Galaxy as an output rather than being coupled to it
3. Use protocols/interfaces to break the cycle
**Effort:** Medium

#### MAJOR: Facade Accessing Private Members
**ID:** ADR-STR-004
**Location:** `game/strategy/facade/strategy_session_facade.py:90`
**Issue:** The facade calls `self._session._get_fleet_by_id(fleet_id)` - accessing a private method (prefixed with `_`) of GameSession. The facade should only use public interfaces.
**Impact:** Coupling to private implementation details means the facade will break if GameSession changes its internal methods. This violates encapsulation and the Facade pattern's purpose.
**Recommendation:** Either:
1. Make `get_fleet_by_id()` a public method on GameSession (rename without underscore prefix)
2. Have the facade use a public query method that internally delegates
**Effort:** Simple

#### MINOR: Late Imports for Cross-Layer Operations
**ID:** ADR-STR-005
**Location:** `game/strategy/data/ship_instance.py:170-172, 501-503`
**Issue:** ShipInstance uses late imports for `ShipSerializer` from the simulation layer. While documented as "INTENTIONAL LATE IMPORT: Cross-layer boundary", this pattern is repeated 3 times in the same file.
**Impact:** While these are documented and intentional, having multiple late imports to the same module suggests the class has tight coupling to simulation layer. This coupling is acceptable per architecture (strategy can depend on simulation), but the late-import pattern reduces IDE support and increases cognitive load.
**Recommendation:** Consider consolidating the imports at module level with TYPE_CHECKING guard for type hints, and lazy-load instances via a factory method that handles the import once.
**Effort:** Simple

#### INFO: TYPE_CHECKING Patterns Used Throughout
**ID:** ADR-STR-006
**Location:** Multiple files (26+ occurrences across strategy layer)
**Issue:** Extensive use of `TYPE_CHECKING` blocks throughout the strategy layer. Most are appropriate for forward references and avoiding import cycles, but some indicate tight coupling between modules.
**Impact:** N/A - This is an observation. The pattern is generally used correctly to provide type hints without runtime import costs. No action required.
**Recommendation:** No action needed. This is good practice when used appropriately.
**Effort:** N/A

## Top 5 Priority Issues

1. **ADR-STR-001 (CRITICAL):** AI Layer Dependency - Strategy importing from AI violates layer architecture and creates potential circular dependency. Should be addressed to maintain clean layer separation.

2. **ADR-STR-002 (MAJOR):** Galaxy God Class - At 914 lines, this class needs decomposition. It handles too many concerns including system storage, entity registration, warp lane generation, and serialization.

3. **ADR-STR-003 (MAJOR):** Late Import Circular Dependency - The explicit "avoid circular dependency" comment in galaxy.py indicates a structural issue that should be addressed through interface extraction or module reorganization.

4. **ADR-STR-004 (MAJOR):** Facade Private Access - The facade pattern should use public interfaces only. Accessing `_get_fleet_by_id` violates encapsulation.

5. **ADR-STR-005 (MINOR):** Repeated Late Imports - ShipInstance has 3 late imports to the same simulation module. Consider consolidating to a single factory pattern.

## Architecture Compliance Summary

**Layer Dependencies (Verified):**
- Strategy -> Core: COMPLIANT (many imports from game.core.*)
- Strategy -> Simulation: COMPLIANT (imports from game.simulation.* for cross-layer operations)
- Strategy -> UI: COMPLIANT (no pygame or UI imports found)
- Strategy -> AI: **NON-COMPLIANT** (one direct import in simulation_adapter.py)

**Pygame Usage:** None found in strategy layer - COMPLIANT

**Circular Dependencies:** One documented instance (galaxy.py) plus potential with AI layer

**God Classes:** One identified (Galaxy at 914 lines)
