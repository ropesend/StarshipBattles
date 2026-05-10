# Architecture Drift Sweep: Simulation

## Summary
- **Shard:** Simulation
- **Files Scanned:** 72
- **Total Issues Found:** 7
- **Critical:** 2 | **Major:** 2 | **Minor:** 2 | **Info:** 1

## Findings

#### CRITICAL: Pygame Import in Simulation Layer
**ID:** ADR-SIM-001
**Location:** `game/simulation/services/design_loader.py:69`
**Issue:** Direct pygame import: `import pygame; ship.position = pygame.math.Vector2(center_x, center_y)`. Simulation layer must not depend on pygame. game.core.math.Vector2 exists as framework-agnostic alternative.
**Impact:** Violates strict layer boundary (Simulation must not depend on UI/Pygame). Creates tight coupling to pygame implementation.
**Recommendation:** Replace pygame.math.Vector2 with game.core.math.Vector2.
**Effort:** Simple

#### CRITICAL: AI Layer Imports (Mitigated but Present)
**ID:** ADR-SIM-002
**Location:** `game/simulation/systems/battle_engine.py:73,278,348,508`, `game/simulation/factories/ai_factory.py:57-58`
**Issue:** Runtime imports from game.ai in factory methods and deprecated legacy paths. Uses TYPE_CHECKING blocks to minimize compile-time coupling. Factory pattern and PROJ-43/PROJ-17 comments acknowledge this as designed compromise.
**Impact:** Cross-layer dependency exists but is controlled. Deprecated paths still active with warnings.
**Recommendation:** Remove deprecated legacy import paths. Ensure all AI imports go through factory injection only.
**Effort:** Medium

#### MAJOR: God Class - Ship (804 lines, 46 methods)
**ID:** ADR-SIM-003
**Location:** `game/simulation/entities/ship.py`
**Issue:** 804 lines, 46 public/property methods. Mixed responsibilities: position/velocity, components, stats, combat, serialization, physics.
**Impact:** Difficult to test, maintain, and extend. Mixed concerns violate single responsibility.
**Recommendation:** Extract component management and stats calculation into delegate classes.
**Effort:** Complex

#### MAJOR: God Class - BattleEngine (674 lines, 20 methods)
**ID:** ADR-SIM-004
**Location:** `game/simulation/systems/battle_engine.py`
**Issue:** 674 lines orchestrating ship lifecycle, AI coordination, projectiles, collisions, and battle conditions.
**Impact:** Orchestrates multiple subsystems with insufficient delegation.
**Recommendation:** Extract AI coordination and battle state management into services.
**Effort:** Complex

#### MINOR: Private Attribute Access (_registries)
**ID:** ADR-SIM-005
**Location:** `game/simulation/systems/battle_engine.py:485`
**Issue:** Accessing source_ship._registries private attribute when creating new ship.
**Impact:** Violates encapsulation. Fragile if private implementation changes.
**Recommendation:** Add public property Ship.registries or Ship.get_registries().
**Effort:** Simple

#### MINOR: Private Attribute Modification (_hp_ratio_dirty)
**ID:** ADR-SIM-006
**Location:** `game/simulation/battle_state.py:301`
**Issue:** Directly modifying private cache flag: new_comp._hp_ratio_dirty = True.
**Impact:** Couples battle state to component internals.
**Recommendation:** Add public method Component.mark_cache_dirty().
**Effort:** Simple

#### INFO: Simulation-AI Coupling is Controlled
**ID:** ADR-SIM-007
**Location:** battle_engine.py, ai_factory.py
**Issue:** All AI imports use TYPE_CHECKING blocks or runtime factory injection. No compile-time dependency. This is an acknowledged architectural compromise.
**Impact:** Acceptable design trade-off documented in code.
**Recommendation:** Continue monitoring. Consider extracting AIControllerFactory to game.engine layer.
**Effort:** None (monitoring only)

## Top 5 Priority Issues
1. **ADR-SIM-001**: Pygame import in design_loader.py - quick fix, clear violation
2. **ADR-SIM-002**: Remove deprecated AI import paths in BattleEngine
3. **ADR-SIM-003**: Ship god class (804 lines) - needs delegate extraction
4. **ADR-SIM-004**: BattleEngine god class (674 lines) - needs service extraction
5. **ADR-SIM-005/006**: Private attribute access/modification - add public APIs
