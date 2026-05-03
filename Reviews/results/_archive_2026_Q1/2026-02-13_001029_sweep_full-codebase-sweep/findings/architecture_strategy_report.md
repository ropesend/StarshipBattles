# Architecture Drift Sweep: Strategy

## Summary
- **Shard:** Strategy
- **Files Scanned:** 89
- **Total Issues Found:** 7
- **Critical:** 0 | **Major:** 3 | **Minor:** 3 | **Info:** 1

## Methodology Notes

This sweep analyzed all 89 Python files in `game/strategy/`. The analysis checked:

1. **Import graph analysis** - All imports verified against layered architecture rules
2. **Pygame boundary violations** - No pygame imports found (PASS)
3. **UI layer dependencies** - No `game.ui` imports found (PASS)
4. **AI layer dependencies** - No `game.ai` imports found (PASS)
5. **Simulation layer usage** - Appropriate via adapters/late imports
6. **Circular dependencies** - TYPE_CHECKING blocks reviewed
7. **God classes** - Line count analysis performed
8. **Data flow violations** - Design reviewed

## Findings

#### MAJOR: Simulation Layer Coupling via Direct Import
**ID:** ADR-STR-001
**Location:** `game/strategy/services/ship_stats_calculator.py:25-26`
**Issue:** Direct top-level imports from simulation layer violate strict layering:
```python
from game.simulation.formula_system import safe_evaluate_math_formula
from game.simulation.components.modifiers import calculate_stat_multipliers
```
These are used for stat calculation but create a hard dependency on simulation internals.
**Impact:** Strategy layer cannot be tested or used without simulation layer. Prevents headless operation of strategy logic if simulation has pygame dependencies.
**Recommendation:** Extract these pure functions to `game.core` (they are stateless math utilities) or create a strategy-layer duplicate.
**Effort:** Medium

#### MAJOR: Simulation Adapter Has Top-Level Simulation Imports
**ID:** ADR-STR-002
**Location:** `game/strategy/adapters/simulation_adapter.py:25-27`
**Issue:** The adapter file has top-level simulation imports:
```python
from game.simulation.battle_controller import BattleController
from game.simulation.battle_config import BattleConfig, BattleMode
from game.simulation.services.battle_service import BattleService
```
While this file IS the designated adapter, top-level imports mean importing ANY module that transitively imports SimulationBattleResolver will pull in the simulation layer.
**Impact:** Even though the adapter pattern is correct, the top-level import means any code importing strategy modules that lazily create SimulationBattleResolver will have an import-time dependency on simulation.
**Recommendation:** Move these imports inside the `resolve_battle` method to make them truly lazy. This follows the pattern used elsewhere in the codebase (see ShipInstance.to_ship).
**Effort:** Simple

#### MAJOR: Galaxy Class Approaching God Class Status
**ID:** ADR-STR-003
**Location:** `game/strategy/data/galaxy.py` (836 lines)
**Issue:** Galaxy class at 836 lines is approaching problematic size with many responsibilities:
- System registry and lookup
- Planet registry with spatial indexing
- Fleet registry
- Naming registry
- Star and planet generation
- Warp lane generation
- MST algorithm for connectivity
- Density-based edge generation
- Serialization/deserialization
**Impact:** The class is becoming difficult to maintain and test. Changes to one responsibility risk affecting others.
**Recommendation:** Extract generation logic to a separate `GalaxyGenerator` class. Extract warp lane logic to `WarpLaneBuilder`. Keep Galaxy as a pure data container with registries.
**Effort:** Complex

#### MINOR: TYPE_CHECKING Block Indicates Tight Coupling
**ID:** ADR-STR-004
**Location:** `game/strategy/data/fleet_battle_adapter.py:14-16`
**Issue:** TYPE_CHECKING block references simulation layer:
```python
if TYPE_CHECKING:
    from game.strategy.data.fleet import Fleet
    from game.simulation.entities.ship import Ship
    from game.core.registry import GameRegistries
```
While TYPE_CHECKING prevents runtime import, it indicates the strategy layer is aware of simulation internals.
**Impact:** Type annotations reference simulation-layer types, creating cognitive coupling even if not runtime coupling.
**Recommendation:** Use `IPostBattleShip` protocol (already defined in game.core.protocols) in return type annotations instead of concrete `Ship` type.
**Effort:** Simple

#### MINOR: Late Import Pattern Inconsistency
**ID:** ADR-STR-005
**Location:** Multiple files using different patterns
**Issue:** The codebase uses both patterns inconsistently:
1. Late imports with comments explaining why (good pattern, e.g., `ship_instance.py:170-172`)
2. Top-level imports that could be late (e.g., `simulation_adapter.py:25-27`)
3. Some late imports lack the explanatory comment convention
**Impact:** Developers may not understand when late imports are intentional vs. accidental, leading to inconsistent architecture enforcement.
**Recommendation:** Standardize on the pattern documented in `docs/ARCHITECTURE.md` "Intentional Late Imports" section. All cross-layer imports should be late with the standard comment block.
**Effort:** Simple

#### MINOR: Potential Circular Dependency Risk in FleetBattleAdapter
**ID:** ADR-STR-006
**Location:** `game/strategy/data/fleet_battle_adapter.py`
**Issue:** The adapter imports from `game.core.protocols` but the to_battle_ships method calls `instance.to_ship()` which internally imports simulation layer code. If any simulation code imports from strategy, this creates a potential circular dependency risk.
**Impact:** While currently functional, adding imports in simulation that reference strategy could break the build.
**Recommendation:** Document this boundary clearly. Consider adding import cycle detection to CI.
**Effort:** Simple

#### INFO: Well-Architected Adapter Pattern in Place
**ID:** ADR-STR-007
**Location:** `game/strategy/adapters/simulation_adapter.py`, `game/strategy/interfaces/battle_resolver.py`
**Issue:** This is an observation, not a problem. The IBattleResolver interface and SimulationBattleResolver adapter demonstrate proper boundary management:
- Abstract interface in `interfaces/` folder
- Concrete adapter in `adapters/` folder
- TurnEngine uses only the interface
- Simulation details hidden behind adapter
**Impact:** Positive - enables testing with mock resolvers and keeps strategy layer testable in isolation.
**Recommendation:** Use this pattern as the template for any future cross-layer integrations.
**Effort:** N/A

## Top 5 Priority Issues

1. **ADR-STR-001 (MAJOR)** - Direct simulation imports in ShipStatsCalculator - breaks headless operation
2. **ADR-STR-002 (MAJOR)** - Top-level simulation imports in adapter should be lazy
3. **ADR-STR-003 (MAJOR)** - Galaxy god class - extract generation and warp lane logic
4. **ADR-STR-004 (MINOR)** - Use protocols instead of concrete simulation types in TYPE_CHECKING
5. **ADR-STR-005 (MINOR)** - Standardize late import pattern with consistent documentation

## Summary of Architecture Health

**Overall Assessment: GOOD with Minor Concerns**

The strategy layer demonstrates well-designed architecture overall:

**Strengths:**
- No pygame imports (clean UI separation)
- No AI layer imports (correct dependency direction)
- Proper use of IBattleResolver interface for simulation boundary
- Clean CQRS-lite pattern in StrategySessionFacade
- Effective use of delegation (FleetResourceAggregator, FleetCapabilityCalculator, etc.)
- Well-documented intentional late imports in several files

**Areas for Improvement:**
- ShipStatsCalculator needs refactoring to eliminate direct simulation imports
- Galaxy class should be decomposed before it grows further
- Simulation adapter should use lazy imports for consistency
- TYPE_CHECKING blocks should prefer protocols over concrete types

The architecture largely respects the layered design documented in CLAUDE.md. The identified issues are maintenance concerns rather than fundamental violations.
