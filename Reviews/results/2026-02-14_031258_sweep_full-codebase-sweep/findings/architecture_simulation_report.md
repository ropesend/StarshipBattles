# Architecture Drift Sweep: Simulation

## Summary
- **Shard:** Simulation
- **Files Scanned:** 69
- **Total Issues Found:** 5
- **Critical:** 0 | **Major:** 2 | **Minor:** 2 | **Info:** 1

## Overview

The simulation layer (`game/simulation/`) demonstrates **excellent architectural compliance**. An exhaustive scan of all 69 Python files revealed:

- **No pygame imports**: The simulation layer is completely decoupled from the UI layer
- **No game.ui imports**: No direct dependencies on UI code
- **No game.ai imports**: AI layer properly abstracted via protocols
- **No game.strategy imports**: Strategy layer not imported
- **Proper core layer usage**: All imports from `game.core` are appropriate

The layer correctly depends on:
- `game.core.*` (constants, math, registry, logging, paths, config) - **ALLOWED**
- `game.engine.*` (physics, spatial, collision) - **ALLOWED** per CLAUDE.md ("thin orchestration layer")
- Self-references within `game.simulation.*` - **ALLOWED**

### Layer Dependency Pattern

The simulation layer uses **interface-based decoupling** for AI integration:
- `game.simulation.interfaces.ai_controller` defines `IAIController` and `IAIControllerFactory` protocols
- Concrete AI implementations in `game.ai` layer inject via these protocols
- TYPE_CHECKING blocks reference the protocols, not concrete implementations

## Findings

#### MAJOR: Ship Class is Approaching God Class Territory
**ID:** ADR-SIM-001
**Location:** `game/simulation/entities/ship.py:1-811`
**Issue:** The Ship class at ~800 lines is large, though it has been significantly decomposed with composition patterns
**Impact:** While functional, large classes can be harder to test, maintain, and understand. However, Ship has already been refactored with:
- `ShipStatsCalculator` for stat computation
- `ShipPhysicsMixin` for physics behavior
- `ShipFormation` for formation logic
- `ShipStatQuerier` for stat aggregation
- `ShipValidatorHelper` for validation
- `ShipCombatEngine` for combat logic
- `ShipSerializer` for serialization

**Recommendation:** The decomposition is already well underway. Consider extracting remaining concerns if they grow, but current size is manageable given the composition.
**Effort:** Simple (monitoring only - already decomposed)

#### MAJOR: Intentional Late Imports for Circular Dependency Avoidance
**ID:** ADR-SIM-002
**Location:** Multiple files with documented late imports
**Issue:** Several files use late imports with comments explaining circular dependency avoidance:
- `ship_stat_querier.py:119` - "INTENTIONAL LATE IMPORT: Avoid circular dependency with abilities module"
- `ship_stats.py:72` - "Import local to avoid circular dep"
- `ship.py:492,537` - Late imports of ModifierService

**Impact:** These are documented as intentional design decisions. The comments reference `docs/ARCHITECTURE.md "Intentional Late Imports" section`, indicating this is an approved pattern.
**Recommendation:** These are acceptable architectural decisions. The documentation of intent is good practice. Future refactoring could explore alternative designs (dependency injection, interface extraction) if the circular dependencies become problematic.
**Effort:** Medium (if restructuring desired)

#### MINOR: Component Module Contains Multiple Concerns
**ID:** ADR-SIM-003
**Location:** `game/simulation/components/component.py:1-723`
**Issue:** The component.py file contains both the Component class (~430 lines) and module-level functions for loading/caching components and modifiers (~290 lines). While not a violation, this mixes entity definition with registry/loader logic.
**Impact:** Slightly reduces cohesion. The loading functions (`load_components`, `load_modifiers`, etc.) could be in a separate module.
**Recommendation:** Consider extracting `load_components*` and `load_modifiers*` functions to a dedicated `component_loader.py` module in a future cleanup.
**Effort:** Simple

#### MINOR: TYPE_CHECKING Usage for Engine Layer
**ID:** ADR-SIM-004
**Location:**
- `game/simulation/projectile_manager.py:8` - `from game.engine.spatial import SpatialGrid`
- `game/simulation/interfaces/ai_controller.py:19` - `from game.engine.spatial import SpatialGrid`

**Issue:** The simulation layer references `game.engine.spatial.SpatialGrid` in TYPE_CHECKING blocks. Per CLAUDE.md, `game.engine` is a "thin orchestration layer" that simulation can depend on.
**Impact:** None - this is allowed per the documented architecture. The engine layer provides low-level physics, spatial indexing, and collision detection that simulation needs.
**Recommendation:** No action needed. The dependency direction is correct (simulation depends on engine for infrastructure).
**Effort:** N/A

#### INFO: Well-Structured Protocol-Based AI Decoupling
**ID:** ADR-SIM-005
**Location:** `game/simulation/interfaces/ai_controller.py:1-141`
**Issue:** Not a problem - positive observation. The simulation layer defines clean protocols (`IAIController`, `IAIControllerFactory`) that allow AI implementations to be injected without creating layer violations.
**Impact:** This pattern enables:
- Headless simulation testing without pygame
- Different AI implementations (mock, test, production)
- Clean layer boundaries between simulation and AI

**Recommendation:** This is an excellent example of proper architectural design. Document this pattern for future reference.
**Effort:** N/A

## Top 5 Priority Issues

1. **ADR-SIM-001 (MAJOR)** - Ship class size (~800 lines) - already well-decomposed, monitor for future growth
2. **ADR-SIM-002 (MAJOR)** - Intentional late imports for circular dependencies - documented and acceptable, but could be improved long-term
3. **ADR-SIM-003 (MINOR)** - Component module mixing entity and loader concerns - low priority cleanup opportunity
4. **ADR-SIM-004 (MINOR)** - Engine layer dependency in TYPE_CHECKING - not a violation per architecture docs
5. **ADR-SIM-005 (INFO)** - Positive pattern - protocol-based AI decoupling is exemplary

## Conclusion

The simulation layer is **architecturally clean**. No critical issues were found. The layer correctly:
- Avoids pygame/UI dependencies
- Uses protocols for AI integration instead of direct imports
- Properly depends on core and engine layers only
- Documents intentional design decisions (late imports)

The identified issues are either monitoring items (Ship class size), documented intentional patterns (late imports), or minor cleanup opportunities (component module cohesion).
