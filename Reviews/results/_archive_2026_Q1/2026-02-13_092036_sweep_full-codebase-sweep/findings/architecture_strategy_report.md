# Architecture Drift Sweep: Strategy

## Summary
- **Shard:** Strategy
- **Files Scanned:** 95
- **Total Issues Found:** 8
- **Critical:** 0 | **Major:** 2 | **Minor:** 3 | **Info:** 3

## Findings

#### MAJOR: Galaxy Class Exceeds Size Threshold (God Class Indicator)
**ID:** ADR-STR-001
**Location:** `game/strategy/data/galaxy.py:1-837`
**Issue:** Galaxy class is 837 lines, significantly exceeding the 500-line threshold for god class indicators. The class handles galaxy data storage, system generation, warp lane generation (MST algorithm), planet registration, fleet registration, and spatial indexing.
**Impact:** High cognitive load, difficult to test in isolation, high change coupling. Changes to warp lane logic could inadvertently affect planet registration.
**Recommendation:** Extract cohesive responsibilities into separate classes:
  - `WarpLaneGenerator` - lines 449-774 (warp lane generation algorithms)
  - `GalaxySystemGenerator` - lines 373-447 (system generation logic)
  - Keep `Galaxy` as pure data container with registries
**Effort:** Medium

#### MAJOR: ProductionEngine Exceeds Size Threshold (God Class Indicator)
**ID:** ADR-STR-002
**Location:** `game/strategy/engine/production_engine.py:1-732`
**Issue:** ProductionEngine class is 732 lines, exceeding the 500-line threshold. Handles colony production, fleet production, facility production, resource consumption per tick, mid-turn completion, and spawning logic for ships and complexes.
**Impact:** Complex testing, intertwined responsibilities for different production contexts (colony vs fleet vs facility).
**Recommendation:** Extract into focused engines:
  - `ColonyProductionEngine` - colony base queue + facility queue processing
  - `FleetProductionEngine` - fleet space yard production
  - `ProductionSpawner` - ship/complex instantiation logic
**Effort:** Medium

#### MINOR: Circular Import Workaround in galaxy.py
**ID:** ADR-STR-003
**Location:** `game/strategy/data/galaxy.py:394-396`
**Issue:** Late import inside `generate_systems()` method with comment "# Import here to avoid circular dependency". Imports `RandomPlacementStrategy` and `SpatialIndex` at runtime.
**Impact:** Indicates potential design issue where Galaxy depends on generation strategies that may depend back on Galaxy. Runtime imports add slight overhead.
**Recommendation:** Consider extracting system generation into a separate `GalaxyGenerator` class that can be imported without circular dependency. Or use interface/protocol to invert the dependency.
**Effort:** Simple

#### MINOR: ShipInstance Cross-Layer Late Imports
**ID:** ADR-STR-004
**Location:** `game/strategy/data/ship_instance.py:170-172, 501-503`
**Issue:** Multiple late imports from simulation layer (`from game.simulation.entities.ship_serialization import ShipSerializer`) inside methods `from_ship()` and `to_ship()`. While documented as "INTENTIONAL LATE IMPORT", indicates tight coupling across the strategy-simulation boundary.
**Impact:** The dependency is valid per architecture rules (strategy can depend on simulation), but the pattern of runtime imports increases method overhead and can mask dependency issues.
**Recommendation:** Consider if a protocol/interface could be defined in core layer to abstract the serialization. Low priority since the dependency direction is correct.
**Effort:** Complex

#### MINOR: ShipStatsCalculator Imports from Simulation Layer
**ID:** ADR-STR-005
**Location:** `game/strategy/services/ship_stats_calculator.py:25-27`
**Issue:** Direct imports from simulation layer:
  - `from game.simulation.formula_system import safe_evaluate_math_formula`
  - `from game.simulation.components.modifiers import calculate_stat_multipliers`
**Impact:** This is a valid dependency per architecture rules (strategy can depend on simulation), but it creates coupling to simulation internals. If formula evaluation or modifier calculation changes, ShipStatsCalculator must be updated.
**Recommendation:** Consider whether these utility functions should be moved to core layer since they are used by both simulation and strategy. Low priority as dependency direction is correct.
**Effort:** Medium

#### INFO: Well-Implemented Facade Pattern
**ID:** ADR-STR-006
**Location:** `game/strategy/facade/strategy_session_facade.py:1-449`
**Issue:** N/A - This is a positive observation.
**Impact:** Positive. The StrategySessionFacade correctly implements CQRS-lite pattern with:
  - All mutations through `handle_command()`
  - All reads returning immutable DTOs (FleetInfo, SystemInfo, etc.)
  - Clear separation between facade and underlying GameSession
**Recommendation:** Maintain this pattern. It provides proper UI-engine isolation.
**Effort:** N/A

#### INFO: Well-Implemented Battle Resolver Interface
**ID:** ADR-STR-007
**Location:** `game/strategy/interfaces/battle_resolver.py`, `game/strategy/adapters/simulation_adapter.py`
**Issue:** N/A - This is a positive observation.
**Impact:** Positive. The IBattleResolver interface and SimulationBattleResolver adapter correctly isolate the strategy layer from simulation layer details. Strategy code only depends on the interface, not simulation implementation.
**Recommendation:** Good pattern to follow for other cross-layer boundaries.
**Effort:** N/A

#### INFO: Intentional AI Layer Dependency
**ID:** ADR-STR-008
**Location:** `game/strategy/adapters/simulation_adapter.py:29`
**Issue:** Import of `from game.ai.ai_factory import AIControllerFactory` in the simulation adapter.
**Impact:** This is valid per architecture rules - strategy layer can depend on AI layer. The import is used to inject AI controllers into battle simulation.
**Recommendation:** No action needed. Dependency is architecturally correct.
**Effort:** N/A

## Top 5 Priority Issues

1. **ADR-STR-001 (MAJOR)**: Galaxy god class (837 lines) - Extract warp generation and system generation into separate classes to improve testability and reduce change coupling.

2. **ADR-STR-002 (MAJOR)**: ProductionEngine god class (732 lines) - Extract colony, fleet, and facility production into separate engines to clarify responsibilities.

3. **ADR-STR-003 (MINOR)**: Circular import in galaxy.py - Consider refactoring generation logic to avoid runtime imports.

4. **ADR-STR-004 (MINOR)**: ShipInstance cross-layer coupling - Low priority, but consider abstracting serialization interface in core layer.

5. **ADR-STR-005 (MINOR)**: Formula/modifier utilities in simulation - Consider moving to core layer for cleaner dependency graph.

## Architecture Compliance Summary

**No pygame imports found** - Strategy layer correctly avoids pygame dependencies.

**No UI layer imports found** - Strategy layer correctly avoids UI dependencies.

**AI layer import is valid** - The single AI import follows the allowed dependency direction (strategy can depend on AI).

**Simulation layer imports are valid** - ShipInstance and ShipStatsCalculator correctly depend on simulation layer (allowed by architecture rules).

**TYPE_CHECKING blocks** - Used appropriately for type hints without creating runtime dependencies.

The strategy layer is architecturally compliant with the defined layer boundaries. The main concerns are internal complexity (god classes) rather than improper external dependencies.
