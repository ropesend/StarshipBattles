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

### Constants (game/core/constants.py)

Shared constants accessible by all layers:
- `PLANET_RESOURCES`: List of resource types
- `AttackType`: Enum for weapon types
- `GameState`: Enum for game states
- Directory paths and file locations

### Registry (game/core/registry.py)

Component definition registry accessible by all layers.

## Intentional Late Imports

Some circular dependencies are resolved through late imports within methods.
These are **intentional design patterns**, not workarounds:

1. **`game/app.py`**: Lazy imports for UI screens/services
   - Purpose: Avoid circular deps, improve startup performance

2. **`game/simulation/entities/ship_serialization.py:120`**:
   `from game.simulation.entities.ship import Ship`
   - Purpose: Ship imports ShipSerializer, ShipSerializer imports Ship

3. **`game/strategy/data/ship_instance.py:171`**:
   `from game.strategy.services.ship_stats_service import ShipStatsService`
   - Purpose: ShipInstance uses service, service may reference ShipInstance types

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

## Related Documentation

- [PROJ-11: Architecture Layer Separation](../Projects/active_projects/PROJ-11/plan.md)
- [PROJ-11 Design Document](../Projects/active_projects/PROJ-11/design.md)
