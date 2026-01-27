# PROJ-17: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

This project is Phase 4 of the Legacy Code Cleanup initiative. The goal is to enforce strict layer boundaries to enable headless deployment of the simulation layer.

**Target Architecture:**
```
┌─────────────────────────────────────┐
│    UI Layer (game/ui/)              │  Depends on: Strategy, Simulation, AI, Core, pygame
└──────────────┬──────────────────────┘
┌──────────────▼──────────────────────┐
│  Strategy Layer (game/strategy/)    │  Depends on: Simulation (via interface), Core
└──────────────┬──────────────────────┘
┌──────────────▼──────────────────────┐
│  Simulation Layer (game/simulation/)│  Depends on: Core ONLY (NO pygame!)
└──────────────┬──────────────────────┘
┌──────────────▼──────────────────────┐
│  AI Layer (game/ai/)                │  Depends on: Simulation interfaces, Core
└──────────────┬──────────────────────┘
┌──────────────▼──────────────────────┐
│  Core Layer (game/core/)            │  Depends on: Nothing
└─────────────────────────────────────┘
```

## Swarm Findings Summary

Six specialist agents analyzed the codebase (Architecture, Dependency, Test Impact, Risk, Pattern, Data Flow).

### Architecture

**Current Violations Found:**
1. `game/simulation/entities/ship.py:1` - `import pygame` (UNUSED - trivial fix)
2. `game/simulation/ship_theme.py:2` - `import pygame` (ACTIVE - needs relocation)
3. `game/simulation/systems/battle_engine.py:60-61` - imports AIController from game.ai
4. `game/simulation/battle_controller.py:29` - TYPE_CHECKING import of Fleet from strategy
5. `game/ai/target_evaluator.py:7,85` - imports LayerType from simulation, uses pygame.Vector2
6. `game/ai/controller.py:45,370` - uses pygame.math.Vector2
7. `game/ai/behaviors.py` - uses pygame.math.Vector2

**Additional Discovery:**
- ShipThemeManager is in simulation layer but ONLY accessed by UI code
- Should be relocated to UI layer entirely

### Key Patterns to Reuse

- **IBattleResolver Pattern**: `game/strategy/interfaces/battle_resolver.py` - Clean interface-based DI
- **ShipControllableAdapter**: `game/ai/interfaces/controllable.py` - Excellent adapter pattern for Ship→IControllable
- **Singleton with Reset**: `game/ai/strategy_manager.py` - Thread-safe singleton with test isolation hooks
- **Optional DI**: `game/simulation/systems/battle_engine.py:149,165` - Logger injection pattern

### Dependencies & Risks

1. **LayerType Move (125+ files)** - Many files import this enum
   - Mitigation: Keep re-export in old location for backward compatibility

2. **ShipThemeManager Move (10+ files)** - UI files import from simulation
   - Mitigation: Keep re-export with deprecation warning

3. **BattleEngine AI Refactor** - Core battle system modification
   - Mitigation: Keep legacy path for backward compatibility
   - Risk: High - affects all battles

4. **Pre-existing Test Failures** - 2 tests already failing (not caused by this project)
   - `test_intercept_integration`
   - `test_component_color_coding`

### Opportunities Discovered

1. `game.core.math.Vector2` already exists - direct replacement for pygame.math.Vector2
2. Interface patterns already established - can follow existing IBattleResolver/IControllable patterns
3. BattleOrchestrator can centralize AI controller creation for better testability

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.

### Key Decisions Made:

| Decision | Choice | Rationale |
|----------|--------|-----------|
| ShipThemeManager location | Move to `game/ui/assets/` | Only UI accesses it; wrong layer for simulation |
| AI pygame replacement | Use `game.core.math.Vector2` | Already exists, API compatible |
| BattleEngine AI refactor | Full BattleOrchestrator in UI | Clean separation, user preference |
| LayerType location | Move to `game/core/constants.py` | Shared by all layers, fits with existing enums |
| Backward compatibility | Keep re-exports | Prevents breaking existing code |

## Files Modified

### New Files
- `game/ui/assets/__init__.py`
- `game/ui/assets/ship_theme_manager.py` (moved from simulation)
- `game/ui/orchestration/__init__.py`
- `game/ui/orchestration/battle_orchestrator.py`
- `tests/unit/ui/test_battle_orchestrator.py`

### Modified Files
- `game/simulation/entities/ship.py` - Remove unused import
- `game/ai/target_evaluator.py` - Fix Vector2 imports
- `game/ai/controller.py` - Fix Vector2 imports
- `game/ai/behaviors.py` - Fix Vector2 imports
- `game/core/constants.py` - Add LayerType enum
- `game/simulation/components/component_constants.py` - Re-export LayerType
- `game/simulation/ship_theme.py` - Become re-export stub
- `game/simulation/systems/battle_engine.py` - Accept pre-created AI controllers
- `game/simulation/battle_controller.py` - Remove Fleet TYPE_CHECKING import
- 10+ UI files - Update ShipThemeManager imports
