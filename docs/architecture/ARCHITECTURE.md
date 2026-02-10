# Starship Battles - Architecture Overview

## Layer Structure

The codebase is organized into distinct layers with clear dependency rules.

```
┌─────────────────────────────────────────────────────────────────┐
│                         UI Layer                                 │
│         (game/ui/, game/app.py - display, input)                │
├─────────────────────────────────────────────────────────────────┤
│                      Strategy Layer                              │
│    (game/strategy/ - galaxy, fleets, turns, empire logic)       │
├─────────────────────────────────────────────────────────────────┤
│                     Simulation Layer                             │
│      (game/simulation/ - battles, physics, AI behavior)         │
├─────────────────────────────────────────────────────────────────┤
│                       Core Layer                                 │
│   (game/core/ - math, config, constants, registry, logger)      │
└─────────────────────────────────────────────────────────────────┘
```

## Dependency Rules

Dependencies should flow **downward** only:

```
UI → Strategy → Simulation → Core
 ↓       ↓           ↓
 └───────┴───────────┴─────> Core
```

### Allowed Dependencies

| Layer      | Can Depend On                           |
|------------|----------------------------------------|
| UI         | Strategy, Simulation, Core             |
| Strategy   | Simulation (via interfaces), Core      |
| Simulation | Core                                   |
| Core       | Standard library only                  |

### Forbidden Dependencies

- **Core → Any game layer**: Core must remain independent
- **Simulation → Strategy**: Would create bidirectional dependency
- **Simulation → UI**: Simulation runs headless
- **Strategy → UI**: Would prevent headless strategy execution

## Interface Contracts (PROJ-11)

### IBattleResolver

The strategy layer defines `IBattleResolver` interface to decouple from
the simulation layer's battle implementation.

```python
# game/strategy/interfaces/battle_resolver.py

class IBattleResolver(ABC):
    @abstractmethod
    def resolve_battle(self, fleet1, fleet2, seed=None) -> BattleResult:
        """Resolve a battle between two fleets."""
        pass

@dataclass
class BattleResult:
    winner: Optional[int]  # 0, 1, or None for draw
    tick_count: int
    team0_survivors: List[Any]
    team1_survivors: List[Any]
```

### Implementations

- **SimulationBattleResolver** (`game/strategy/adapters/simulation_adapter.py`):
  Default implementation using the full battle simulation.

- **Mock implementations** can be created for testing strategy logic
  without running the simulation.

### Usage Example

```python
from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.adapters.simulation_adapter import SimulationBattleResolver

# Default: uses SimulationBattleResolver
engine = TurnEngine()

# For testing: inject mock resolver
from game.strategy.interfaces import IBattleResolver, BattleResult

class MockResolver(IBattleResolver):
    def resolve_battle(self, fleet1, fleet2, seed=None):
        return BattleResult(winner=0, tick_count=1, team0_survivors=[], team1_survivors=[])

test_engine = TurnEngine(battle_resolver=MockResolver())
```

## Core Layer Components

### Vector2 (game/core/math.py)

Custom 2D vector class replacing pygame.math.Vector2 for simulation layer.
Provides full duck-typing compatibility with pygame vectors.

### HexCoord (game/core/hex_math.py)

Hexagonal grid mathematics for the strategy layer galaxy map. Provides:
- `HexCoord` class for axial coordinates (q, r)
- Distance, pixel conversion, ring generation, line drawing
- Serialization helpers (hex_to_dict, hex_from_dict)

PROJ-92 moved this from `game/strategy/data/` to `game/core/` to fix a layer
violation where `game/core/protocols.py` imported from the strategy layer.
The module has no dependencies beyond stdlib `math`, making it appropriate
for the core layer.

### Constants (game/core/constants.py)

Shared constants accessible by all layers:
- `PLANET_RESOURCES`: List of resource types
- `AttackType`: Enum for weapon types
- `GameState`: Enum for game states
- Directory paths and file locations

### Registry (game/core/registry.py)

Component definition registry accessible by all layers.

## Intentional Late Imports

Some late imports within methods are **intentional design patterns** for specific purposes.
PROJ-90 cleaned up several unnecessary late imports in ship.py (WeaponAbility, ShipCombatEngine,
ShipSerializer are now module-level imports). The remaining late imports are documented below:

### Ship Module (game/simulation/entities/ship.py)

1. **Lines 487, 532: `from game.simulation.services.modifier_service import ModifierService`**
   - Location: `add_component()`, `add_components_bulk()`
   - Purpose: ModifierService has transitive dependencies through Ship
   - Rationale: Only called during component addition (edge operation, not hot path)
   - Note: This is a real import cycle that cannot be moved to module level

### App Module (game/app.py)

2. **Lazy imports for UI screens/services**
   - Purpose: Avoid circular deps, improve startup performance

### Fleet Module (game/strategy/data/fleet.py)

3. **Line 133: `from game.strategy.services.fleet_speed_calculator import FleetSpeedCalculator`**
   - Location: `_trigger_speed_recalculation()`
   - Purpose: FleetSpeedCalculator may have transitive dependencies
   - Rationale: Edge operation (only called when ships added/removed)

### ShipInstance Module (game/strategy/data/ship_instance.py)

4. **Lines 157, 562: `from game.simulation.entities.ship_serialization import ShipSerializer`**
   - Location: `from_ship()`, `to_ship()`
   - Purpose: Cross-layer boundary import (strategy -> simulation)
   - Rationale: Maintains layer separation; deferred to avoid load-time coupling

5. **Lines 222-223: ShipStatsCalculator and GameRegistries**
   - Location: `get_calculated_stats()`
   - Purpose: Lazy initialization pattern for cached stats
   - Rationale: Stats only calculated when first accessed

## Strategy-Simulation Boundary Protocol (PROJ-90)

The strategy layer communicates with the simulation layer across the battle boundary using the
`IPostBattleShip` protocol defined in `game/core/protocols.py`.

### IPostBattleShip Protocol

```python
# game/core/protocols.py

@runtime_checkable
class IPostBattleShip(Protocol):
    """Protocol for ships returned from battle simulation."""
    @property
    def serial(self) -> str: ...
    @property
    def hp(self) -> int: ...
    @property
    def layers(self) -> Dict[str, Any]: ...
    @property
    def resource_levels(self) -> Dict[str, float]: ...
    @property
    def cargo_contents(self) -> Dict[str, int]: ...
```

### Usage

- **BattleResult.team0_survivors / team1_survivors**: `List[IPostBattleShip]`
- **ShipInstance.update_from_ship(ship: IPostBattleShip)**: Updates from battle survivor
- **Fleet.update_from_battle_results(survivors: List[IPostBattleShip])**: Batch update

This protocol decouples the strategy layer from the simulation layer's Ship class while still
allowing type-safe data transfer across the boundary.

## Configuration Extraction (PROJ-90)

### BattleConfig (game/simulation/battle_config.py)

`BattleConfig` and `BattleMode` were extracted from `battle_controller.py` to eliminate a
circular import workaround. This module has no dependencies on other simulation modules.

### Registry Loader (game/simulation/services/registry_loader.py)

The `RegistryLoader` class was extracted from `game/core/registry.py` to fix a Core → Simulation
layer violation. The loader handles all component/design JSON loading while the registry remains
in core with no simulation dependencies.

## Testing Without Display

Both simulation and strategy layers can run without a display:

```python
# Strategy tests: 592 tests run without UI initialization
pytest tests/unit/strategy/

# Simulation headless mode
config = BattleConfig(headless=True, ...)
controller.configure(config)
results = controller.run_headless()
```

## Package Public APIs (PROJ-43)

Each major package defines an explicit public API via `__all__` in its `__init__.py`.
This establishes clear contracts for what is safe to import directly.

### Recommended Import Patterns

```python
# GOOD: Import from package public API
from game.core import Vector2, LayerType, ValidationResult
from game.simulation import Ship, BattleEngine, Component
from game.strategy import Fleet, TurnEngine, GameSession
from game.engine import PhysicsBody, SpatialGrid
from game.ai import AIController, KiteBehavior

# ACCEPTABLE: Import from specific module (for less common items)
from game.core.config import DisplayConfig, AIConfig
from game.simulation.services.battle_service import BattleService

# AVOID: Deep implementation imports (may change)
from game.simulation.entities.ship_physics import ShipPhysicsMixin  # internal
```

### Package API Summary

| Package | Public Exports | Description |
|---------|----------------|-------------|
| `game.core` | 35 exports | Math, registry, constants, logging, validation, config, paths, protocols |
| `game.simulation` | 12 exports | Ship, Component, BattleEngine, BattleService, validators |
| `game.strategy` | 15 exports | Fleet, TurnEngine, GameSession, Facade, DTOs, interfaces |
| `game.ui` | 7 modules | Renderer, screens, panels (module-level exports for race condition prevention) |
| `game.engine` | 3 exports | PhysicsBody, CollisionSystem, SpatialGrid |
| `game.ai` | 11 exports | AIController, behaviors, StrategyManager, TargetEvaluator |
| `game.research` | - | Tech tree research system: fuzzy requirements, leaky bucket mechanics, tech tree visualization |

### Public vs. Private Modules

- **Public**: Listed in `__all__` - stable API, safe to import
- **Private**: Not in `__all__` - implementation details, may change

When a module is not exported in `__all__`, prefer importing via the public API:

```python
# Instead of this (private module):
from game.simulation.entities.ship_serialization import ShipSerializer

# Use this (public API):
from game.simulation import ShipSerializer
```

## Related Documentation

- [NAMING_CONVENTIONS.md](NAMING_CONVENTIONS.md) - Naming patterns and conventions
- [PATTERNS.md](PATTERNS.md) - Design patterns used in codebase
- [SERVICES.md](SERVICES.md) - Service layer API documentation
- [ERROR_HANDLING_GUIDELINES.md](ERROR_HANDLING_GUIDELINES.md) - Error handling patterns
- [UI_STYLE_GUIDE.md](UI_STYLE_GUIDE.md) - UI color and theme guide
- [Component System](../guides/component_system.md) - Ship components, abilities, and modifiers
- [Modifier System](../guides/modifier_system.md) - Detailed modifier documentation
