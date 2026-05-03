# Architecture Drift Sweep: Strategy

## Summary
- **Shard:** Strategy
- **Files Scanned:** 94
- **Total Issues Found:** 4
- **Critical:** 0 | **Major:** 4 | **Minor:** 0 | **Info:** 0

## Findings

#### MAJOR: God Class - ProductionEngine (731 lines, 14 methods)
**ID:** ADR-STR-001
**Location:** `game/strategy/engine/production_engine.py`
**Issue:** 731 lines handling all production-related logic. While method count (14) is within threshold, total line count exceeds 500-line god class indicator.
**Impact:** Complex production logic in single file. Difficult to test individual production aspects.
**Recommendation:** Extract resource validation, queue management, and completion logic into separate services.
**Effort:** Medium

#### MAJOR: God Class - Galaxy (707 lines, 33 methods)
**ID:** ADR-STR-002
**Location:** `game/strategy/data/galaxy.py`
**Issue:** 707 lines and 33 methods (exceeds 30 threshold). Core data structure handling systems, spatial queries, pathfinding, and serialization.
**Impact:** Many responsibilities in single class. Changes to one aspect risk affecting others.
**Recommendation:** Extract spatial queries to GalaxySpatialIndex. Extract serialization to GalaxySerializer.
**Effort:** Medium

#### MAJOR: God Class - ShipInstance (688 lines, 44 methods)
**ID:** ADR-STR-003
**Location:** `game/strategy/data/ship_instance.py`
**Issue:** 688 lines and 44 methods (exceeds 30 threshold). Handles ship state, resources, components, stats, and serialization.
**Impact:** Large but focused class. High method count suggests opportunity for extraction.
**Recommendation:** Extract resource management to ShipResourceManager (if not already). Extract serialization.
**Effort:** Medium

#### MAJOR: God Class - Stars (560 lines, 17 methods)
**ID:** ADR-STR-004
**Location:** `game/strategy/data/stars.py`
**Issue:** 560 lines handling star generation and data. While method count is within threshold, line count exceeds 500.
**Impact:** Generation and data mixed in single file.
**Recommendation:** Consider extracting star generation logic from star data model.
**Effort:** Simple

## Positive Findings

The strategy layer maintains **clean architectural boundaries**:
- **Zero UI/Pygame violations** - No imports from game.ui or pygame
- **Zero AI layer coupling** - No imports from game.ai
- **Correct dependency direction** - Only depends on core (80 imports) and simulation (5 imports)
- **Facade pattern correctly applied** - StrategySessionFacade provides clean UI boundary
- **DTOs properly used** - Immutable frozen dataclasses prevent inappropriate data flow
- **No circular dependencies detected**

## Top 5 Priority Issues
1. **ADR-STR-002**: Galaxy god class (707 lines, 33 methods) - highest method count
2. **ADR-STR-003**: ShipInstance god class (688 lines, 44 methods) - highest method count
3. **ADR-STR-001**: ProductionEngine god class (731 lines) - highest line count
4. **ADR-STR-004**: Stars module (560 lines) - mixed generation/data concerns
5. (No 5th issue - strategy layer is architecturally clean)
