# PROJ-11: Design Document

## Target Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        UI LAYER                              │
│   game/ui/, ui/                                              │
│   - pygame dependency OK here                                │
│   - Uses ViewModels/DTOs, not raw simulation entities        │
├─────────────────────────────────────────────────────────────┤
│                     STRATEGY LAYER                           │
│   game/strategy/                                             │
│   - No pygame, no UI imports                                 │
│   - Uses interfaces to call simulation                       │
├─────────────────────────────────────────────────────────────┤
│                    SIMULATION LAYER                          │
│   game/simulation/, game/engine/                             │
│   - No pygame, no strategy imports                           │
│   - Pure game logic                                          │
├─────────────────────────────────────────────────────────────┤
│                       CORE LAYER                             │
│   game/core/                                                 │
│   - Shared utilities (math, logging, config)                 │
│   - No business logic                                        │
└─────────────────────────────────────────────────────────────┘
```

## Phase 1: Core Math Abstraction

### New File: `game/core/math.py`
```python
"""
Core math utilities for Starship Battles.
Provides framework-agnostic Vector2 implementation.
"""
from __future__ import annotations
import math
from typing import Tuple, Union

class Vector2:
    """2D vector class compatible with pygame.math.Vector2 API."""

    __slots__ = ('x', 'y')

    def __init__(self, x: float = 0, y: float = 0):
        self.x = float(x)
        self.y = float(y)

    def __add__(self, other: 'Vector2') -> 'Vector2':
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Vector2') -> 'Vector2':
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> 'Vector2':
        return Vector2(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> 'Vector2':
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float) -> 'Vector2':
        return Vector2(self.x / scalar, self.y / scalar)

    def __neg__(self) -> 'Vector2':
        return Vector2(-self.x, -self.y)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector2):
            return False
        return self.x == other.x and self.y == other.y

    def __repr__(self) -> str:
        return f"Vector2({self.x}, {self.y})"

    def length(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y)

    def length_squared(self) -> float:
        return self.x * self.x + self.y * self.y

    def normalize(self) -> 'Vector2':
        length = self.length()
        if length == 0:
            return Vector2(0, 0)
        return Vector2(self.x / length, self.y / length)

    def normalize_ip(self) -> None:
        """Normalize in place."""
        length = self.length()
        if length != 0:
            self.x /= length
            self.y /= length

    def dot(self, other: 'Vector2') -> float:
        return self.x * other.x + self.y * other.y

    def distance_to(self, other: 'Vector2') -> float:
        return (self - other).length()

    def distance_squared_to(self, other: 'Vector2') -> float:
        return (self - other).length_squared()

    def rotate(self, angle_degrees: float) -> 'Vector2':
        """Rotate vector by angle in degrees."""
        angle_rad = math.radians(angle_degrees)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        return Vector2(
            self.x * cos_a - self.y * sin_a,
            self.x * sin_a + self.y * cos_a
        )

    def angle_to(self, other: 'Vector2') -> float:
        """Return angle to other vector in degrees."""
        return math.degrees(math.atan2(other.y - self.y, other.x - self.x))

    def copy(self) -> 'Vector2':
        return Vector2(self.x, self.y)

    def as_tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)

    def as_int_tuple(self) -> Tuple[int, int]:
        return (int(self.x), int(self.y))
```

## Phase 2: Files to Modify

### Simulation Layer (Remove pygame)
| File | Current Usage | Replacement |
|------|---------------|-------------|
| `game/simulation/entities/ship.py` | `pygame.math.Vector2` | `game.core.math.Vector2` |
| `game/simulation/entities/ship_combat.py` | `pygame.math.Vector2` | `game.core.math.Vector2` |
| `game/simulation/entities/ship_formation.py` | `pygame.math.Vector2` | `game.core.math.Vector2` |
| `game/simulation/entities/ship_physics.py` | `pygame.math.Vector2` | `game.core.math.Vector2` |
| `game/simulation/entities/projectile.py` | `pygame.math.Vector2` | `game.core.math.Vector2` |
| `game/simulation/battle_state.py` | `pygame.math.Vector2` | `game.core.math.Vector2` |
| `game/simulation/systems/battle_engine.py` | `pygame.math.Vector2` | `game.core.math.Vector2` |
| `game/simulation/systems/persistence.py` | `pygame.math.Vector2` | `game.core.math.Vector2` |
| `game/simulation/projectile_manager.py` | `pygame.math.Vector2` | `game.core.math.Vector2` |
| `game/simulation/ship_theme.py` | `pygame` (if any) | Remove |
| `game/engine/physics.py` | `pygame.math.Vector2` | `game.core.math.Vector2` |
| `game/engine/collision.py` | `pygame.math.Vector2` | `game.core.math.Vector2` |
| `game/engine/spatial.py` | `pygame.math.Vector2` | `game.core.math.Vector2` |

## Phase 3: Strategy-UI Separation

### Move Functions to Strategy Services
| Current Location | Function | New Location |
|------------------|----------|--------------|
| `game/ui/screens/fleet_report_filters.py` | `has_warp_capability()` | `game/strategy/services/ship_stats_service.py` |
| `game/ui/screens/fleet_report_filters.py` | Other fleet filters | `game/strategy/services/fleet_query_service.py` |

### Update Imports
| File | Change |
|------|--------|
| `game/strategy/data/fleet.py` | Import from strategy services, not UI |

### Move Constants to Core
| Current Location | Constant | New Location |
|------------------|----------|--------------|
| `game/strategy/data/planet.py` | `PLANET_RESOURCES` | `game/core/constants.py` |

## Phase 4: Interface Contracts

### IBattleResolver Interface
```python
# game/strategy/interfaces/battle_resolver.py
from abc import ABC, abstractmethod
from typing import List, Tuple

class IBattleResolver(ABC):
    @abstractmethod
    def resolve_battle(
        self,
        attacker_ships: List[dict],
        defender_ships: List[dict],
        seed: int
    ) -> 'BattleResult':
        """Resolve a battle between two fleets."""
        pass

class BattleResult:
    """Data transfer object for battle results."""
    winner: str  # 'attacker', 'defender', 'draw'
    attacker_survivors: List[dict]
    defender_survivors: List[dict]
    attacker_losses: List[dict]
    defender_losses: List[dict]
```

### Simulation Adapter
```python
# game/strategy/adapters/simulation_adapter.py
from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult
from game.simulation.battle_controller import BattleController

class SimulationBattleResolver(IBattleResolver):
    """Adapter that uses simulation layer for battle resolution."""

    def resolve_battle(self, attacker_ships, defender_ships, seed) -> BattleResult:
        # Convert to simulation format, run battle, convert results back
        pass
```

## Testing Strategy
1. Create comprehensive Vector2 unit tests
2. Run all simulation tests with new Vector2
3. Test headless simulation execution
4. Test strategy layer without UI imports
5. Integration tests for layer boundaries
