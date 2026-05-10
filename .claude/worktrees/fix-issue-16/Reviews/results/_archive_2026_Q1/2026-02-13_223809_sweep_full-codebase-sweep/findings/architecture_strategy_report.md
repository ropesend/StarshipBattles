# Architecture Drift Sweep: Strategy

## Summary
- **Shard:** Strategy (game/strategy/)
- **Files Scanned:** 95
- **Total Issues Found:** 5
- **Critical:** 0 | **Major:** 2 | **Minor:** 2 | **Info:** 1

## Findings

#### MAJOR: Strategy Layer Imports AI Layer (Permitted but Documented)
**ID:** ADR-STR-001
**Location:** `game/strategy/adapters/simulation_adapter.py:29`
**Issue:** Strategy layer directly imports from game.ai layer. Per architecture rules, Strategy should depend on Core and Simulation only. However, the code includes a comment "PROJ-126: Import AI factory from AI layer (strategy can depend on AI)" suggesting this was an intentional decision.
**Impact:** Creates coupling between strategy and AI layers. If AI layer needs strategy objects, could lead to circular dependencies. The current usage (injecting AIControllerFactory into BattleController) is reasonable for headless battle resolution.
**Recommendation:** Document this exception formally in architecture docs. The dependency direction is reasonable (strategy orchestrates AI for battles), but should be noted as an architectural exception.
**Effort:** Simple

#### MAJOR: Galaxy Class Approaching God Class Territory
**ID:** ADR-STR-002
**Location:** `game/strategy/data/galaxy.py:1-915`
**Issue:** Galaxy class is 915 lines with approximately 40+ methods covering multiple responsibilities: system management, planet registry, fleet registry, zone registry, warp link generation, spatial indexing, serialization, and planet generation.
**Impact:** Difficult to test individual responsibilities in isolation. Changes to one subsystem (e.g., zone registry) risk breaking others. High cognitive load for developers navigating the class.
**Recommendation:** Consider extracting responsibilities into focused classes:
  - `GalaxyRegistry` - Planet, fleet, and zone registries with O(1) lookups
  - `GalaxyGenerator` - System and warp lane generation
  - `GalaxySpatialIndex` - Spatial queries and index maintenance
  The Galaxy class could then compose these as delegates.
**Effort:** Complex

#### MINOR: Production Engine Approaching 500+ LOC
**ID:** ADR-STR-003
**Location:** `game/strategy/engine/production_engine.py:1-731`
**Issue:** ProductionEngine is 731 lines. While not a full god class, it handles multiple concerns: base queue processing, facility queue processing, fleet production, construction tick processing, resource consumption, mid-turn completion, and spawning of ships/complexes/fleet items.
**Impact:** Growing complexity makes the class harder to extend. Adding new production types requires understanding the entire file.
**Recommendation:** Consider extracting spawn logic into a separate `ProductionSpawner` class that handles `_spawn_ship`, `_spawn_complex`, `_spawn_fleet_ship`, `_spawn_fleet_complex`. This would reduce ProductionEngine to queue processing concerns only.
**Effort:** Medium

#### MINOR: FleetOrderProcessor Approaching 500+ LOC
**ID:** ADR-STR-004
**Location:** `game/strategy/engine/fleet_order_processor.py:1-630`
**Issue:** FleetOrderProcessor is 630 lines handling diverse order types: COLONIZE, JOIN_FLEET, MOVE_TO_FLEET, TRANSFER, and all superweapon orders (via delegation). Each order type has different validation and execution logic.
**Impact:** Adding new order types requires understanding the full file. The mix of instant and end-turn order processing adds complexity.
**Recommendation:** The current delegation to SuperweaponOrderProcessor is the right pattern. Consider similar extraction for COLONIZE order processing (ColonizeOrderHandler) which has significant logic for population transfer and pod consumption.
**Effort:** Medium

#### INFO: Cross-Layer Imports via TYPE_CHECKING (Good Practice)
**ID:** ADR-STR-005
**Location:** Multiple files (26 TYPE_CHECKING blocks found)
**Issue:** Strategy layer files appropriately use TYPE_CHECKING blocks for simulation layer type hints.
**Impact:** None - this is the correct pattern for type hints that don't require runtime imports.
**Recommendation:** Continue using this pattern. Files like `fleet_battle_adapter.py` correctly import `game.simulation.entities.ship.Ship` under TYPE_CHECKING.
**Effort:** N/A

## Top 5 Priority Issues

1. **ADR-STR-002 (Major):** Galaxy class at 915 LOC is the largest architectural concern. Decomposition would significantly improve maintainability and testability.

2. **ADR-STR-001 (Major):** Strategy->AI dependency should be formally documented as an architectural exception. The current comment (PROJ-126) is insufficient for long-term understanding.

3. **ADR-STR-003 (Minor):** ProductionEngine at 731 LOC. Not critical yet but should be monitored. Extracting spawner logic would prevent future growth.

4. **ADR-STR-004 (Minor):** FleetOrderProcessor at 630 LOC. The delegation pattern already used for superweapons could be extended to other order types.

5. **ADR-STR-005 (Info):** TYPE_CHECKING usage is exemplary - 26 files correctly use this pattern for cross-layer type hints without runtime coupling.

## Architecture Health Assessment

The strategy layer is well-architected overall:

**Strengths:**
- Clean separation from UI (no pygame imports found)
- Proper use of TYPE_CHECKING for type hints
- Simulation layer imports are appropriate (strategy depends on simulation)
- Good use of delegation pattern (FleetBattleAdapter, FleetResourceAggregator, FleetCapabilityCalculator)
- Event system cleanly isolates event handling

**Areas for Improvement:**
- Galaxy class decomposition is the main structural debt
- Strategy->AI dependency needs formal documentation
- Some engine classes trending toward complexity (monitor at 500+ LOC)

**No Critical Issues Found:**
- No pygame imports in strategy layer
- No UI layer imports in strategy layer
- No circular import workarounds detected
- No inappropriate cross-layer coupling
