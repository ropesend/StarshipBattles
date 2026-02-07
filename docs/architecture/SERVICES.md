# Service Layer Architecture

## Overview

The Starship Battles codebase uses a service layer pattern to provide clean abstractions between UI components and domain logic. Services act as facades that encapsulate complex operations and provide stable APIs for UI consumption.

Services exist in two layers:
- **Simulation services** (`game/simulation/services/`) -- battle lifecycle, ship design, component modifiers
- **Strategy services** (`game/strategy/services/`) -- fleet navigation, fleet speed, ship stats calculation

---

## Service Directory

```
game/simulation/services/
    __init__.py
    battle_service.py           # Battle creation and simulation control
    modifier_service.py         # Component modifier handling
    vehicle_design_service.py   # Ship creation and modification

game/strategy/services/
    __init__.py
    fleet_navigation_service.py # Fleet pathfinding and movement
    fleet_speed_calculator.py   # Strategic movement speed calculation
    ship_stats_calculator.py    # Ship stats from component definitions
```

---

## Simulation Layer Services

### BattleService

**Location:** `game/simulation/services/battle_service.py`

**Purpose:** Abstraction layer between UI and BattleEngine. Manages the full battle lifecycle: creation, ship assignment, simulation execution, and state queries.

**Dependencies:** None (no constructor args). Internally creates `BattleEngine`, `BattleLogger`, and `AIControllerFactory`.

**Result Object:**
```python
@dataclass
class BattleResult:
    success: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    engine: Optional[BattleEngine] = None
```

**Key Methods:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `create_battle` | `(seed: Optional[int], enable_logging: bool) -> BattleResult` | Create a new battle instance with optional seed and logging |
| `add_ship` | `(ship: Ship, team_id: int) -> BattleResult` | Add a ship to team 0 or 1 (before start only) |
| `remove_ship` | `(ship: Ship) -> BattleResult` | Remove a ship from the battle (before start only) |
| `start_battle` | `(end_mode: BattleEndMode, max_ticks: Optional[int]) -> BattleResult` | Start the simulation with the given end condition |
| `update` | `() -> BattleResult` | Run one simulation tick |
| `run_ticks` | `(count: int) -> BattleResult` | Run multiple ticks (stops early if battle ends) |
| `is_battle_over` | `() -> bool` | Check if the battle has ended |
| `get_winner` | `() -> Optional[int]` | Get winning team ID (0, 1, -1 for draw, None if no engine) |
| `get_battle_state` | `() -> Dict[str, Any]` | Get full state dict (tick count, ships, projectiles, etc.) |
| `get_all_ships` | `() -> List[Ship]` | Get all ships in battle |
| `get_alive_ships` | `() -> List[Ship]` | Get only living ships |
| `get_engine` | `() -> Optional[BattleEngine]` | Get the underlying BattleEngine directly |
| `reset` | `() -> None` | Clear all battle state, close logger |

**Usage:**
```python
from game.simulation.services.battle_service import BattleService
from game.simulation.systems.battle_end_conditions import BattleEndMode

service = BattleService()
result = service.create_battle(seed=42, enable_logging=True)

service.add_ship(ship1, team_id=0)
service.add_ship(ship2, team_id=1)

service.start_battle(end_mode=BattleEndMode.HP_BASED)

while not service.is_battle_over():
    service.update()
    state = service.get_battle_state()
    print(f"Tick {state['tick_count']}: {len(state['team_0_ships'])} vs {len(state['team_1_ships'])}")

winner = service.get_winner()
service.reset()
```

---

### VehicleDesignService

**Location:** `game/simulation/services/vehicle_design_service.py`

**Purpose:** High-level operations for ship creation and modification. Abstracts layer management, component validation, class changes, and stat recalculation.

**Dependencies:** Requires `GameRegistries` via constructor injection (strict DI, no fallback).

**Result Object:**
```python
@dataclass
class DesignResult:
    success: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    ship: Optional[Ship] = None
    removed_component: Optional[Component] = None
```

**Key Methods:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `create_ship` | `(name: str, ship_class: str, theme_id: str, x: float, y: float, color: tuple, team_id: int) -> DesignResult` | Create a new ship with given parameters |
| `add_component` | `(ship: Ship, component_id: str, layer: LayerType) -> DesignResult` | Create component from registry ID and add to ship |
| `add_component_instance` | `(ship: Ship, component: Component, layer: LayerType) -> DesignResult` | Add a pre-constructed component instance to ship |
| `add_component_bulk` | `(ship: Ship, component_id: str, layer: LayerType, count: int) -> DesignResult` | Add multiple copies of a component |
| `remove_component` | `(ship: Ship, layer: LayerType, index: int) -> DesignResult` | Remove component by layer and index |
| `change_class` | `(ship: Ship, new_class: str, migrate_components: bool) -> DesignResult` | Change vehicle class, optionally migrating components |
| `validate_design` | `(ship: Ship) -> ValidationResult` | Full design validation |
| `get_available_components` | `(ship: Ship, layer: LayerType) -> List[str]` | Get component IDs valid for the given layer |
| `get_layer_info` | `(ship: Ship, layer: LayerType) -> dict` | Get layer details (components, restrictions, radius_pct) |
| `get_ship_summary` | `(ship: Ship) -> dict` | Get summary of ship stats (mass, hp, speed, validity, etc.) |

**Usage:**
```python
from game.simulation.services.vehicle_design_service import VehicleDesignService
from game.core.constants import LayerType
from game.core.registry import GameRegistries

registries = GameRegistries.from_data_files()
service = VehicleDesignService(registries=registries)

# Create a ship
result = service.create_ship(name="USS Enterprise", ship_class="Cruiser", theme_id="Federation")
if result.success:
    ship = result.ship

    # Add components
    result = service.add_component(ship, "laser_cannon", LayerType.OUTER)
    result = service.add_component_bulk(ship, "standard_armor", LayerType.OUTER, count=4)

    # Validate
    validation = service.validate_design(ship)
    if not validation.is_valid:
        print(validation.errors)

    # Get summary
    summary = service.get_ship_summary(ship)
    print(f"{summary['name']}: {summary['mass']}/{summary['max_mass']}kg")
```

---

### ModifierService

**Location:** `game/simulation/services/modifier_service.py`

**Purpose:** Manages component modifier logic -- which modifiers are allowed, which are mandatory, value constraints, and automatic application of required modifiers.

**Dependencies:** Requires `modifier_registry: Dict[str, Any]` via constructor (strict DI, no fallback). Typically pass `registries.modifiers`.

**Class Constant:**
```python
MANDATORY_MODIFIERS = ['simple_size_mount', 'range_mount', 'facing', 'turret_mount']
```

**Key Methods:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `is_modifier_allowed` | `(mod_id: str, component) -> bool` | Check if modifier is valid for this component (type/ability restrictions) |
| `get_mandatory_modifiers` | `(component) -> list` | Get list of mandatory modifier IDs for this component |
| `is_modifier_mandatory` | `(mod_id: str, component) -> bool` | Check if a specific modifier is mandatory |
| `get_initial_value` | `(mod_id: str, component) -> float` | Get the default value for a newly applied modifier |
| `ensure_mandatory_modifiers` | `(component) -> None` | Auto-apply all required modifiers with default values |
| `get_local_min_max` | `(mod_id: str, component) -> tuple` | Get (min, max) value range, accounting for component constraints |

**Usage:**
```python
from game.simulation.services.modifier_service import ModifierService

service = ModifierService(modifier_registry=registries.modifiers)

# Check allowance and mandatory status
if service.is_modifier_allowed('turret_mount', weapon):
    print("Turret mount available")

# Get mandatory modifiers for a weapon
mandatory = service.get_mandatory_modifiers(weapon)
# e.g. ['simple_size_mount', 'range_mount', 'facing', 'turret_mount', 'rapid_fire']

# Auto-apply all mandatory modifiers
service.ensure_mandatory_modifiers(weapon)

# Get valid range for turret arc
min_val, max_val = service.get_local_min_max('turret_mount', weapon)
print(f"Turret arc: {min_val} to {max_val} degrees")
```

---

## Strategy Layer Services

### FleetNavigationService

**Location:** `game/strategy/services/fleet_navigation_service.py`

**Purpose:** Single source of truth for all fleet navigation calculations. Both UI path projection and turn execution use the same logic through this service, ensuring consistency.

**Dependencies:** None (stateless service, no constructor args).

**Data Types:**

```python
@dataclass(frozen=True)
class NavigationState:
    """Immutable snapshot of fleet state for pure-function navigation."""
    location: HexCoord
    path: tuple           # tuple[HexCoord, ...]
    orders: tuple         # tuple[FleetOrder, ...]
    speed: float
    can_warp: bool

    @classmethod
    def from_fleet(cls, fleet: Fleet) -> NavigationState: ...

@dataclass(frozen=True)
class PathSegment:
    """One step in a projected path (for UI visualization)."""
    start: HexCoord
    end: HexCoord
    turn: int
    is_warp: bool

    def to_dict(self) -> dict: ...

@dataclass(frozen=True)
class NavigationStep:
    """Result of computing one navigation step."""
    next_hex: Optional[HexCoord]
    new_state: NavigationState
    order_complete: bool = False
```

**Key Methods:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `get_destination` | `(state: NavigationState, order: FleetOrder, galaxy) -> Optional[HexCoord]` | Determine target hex for a given order (MOVE, MOVE_TO_FLEET, etc.) |
| `compute_path` | `(state: NavigationState, destination: HexCoord, galaxy) -> list` | Calculate path from current location to destination |
| `compute_next_step` | `(state: NavigationState, galaxy) -> NavigationStep` | Pure function: compute next hex and new state without mutation |
| `project_path` | `(fleet: Fleet, galaxy, max_turns: int = 10) -> list[PathSegment]` | Project fleet movement over multiple turns (for UI visualization) |
| `project_path_as_dicts` | `(fleet: Fleet, galaxy, max_turns: int = 10) -> list[dict]` | Same as project_path but returns list of dicts |
| `calculate_fleet_next_hex` | `(fleet: Fleet, galaxy) -> Optional[HexCoord]` | Mutation bridge: compute next hex AND apply state changes to Fleet object |

**Architecture:**
- **Core (pure, stateless):** `get_destination`, `compute_path`, `compute_next_step` -- operate on immutable `NavigationState`, no side effects
- **Projection (for UI):** `project_path`, `project_path_as_dicts` -- simulate future movement for visualization
- **Execution (for TurnEngine):** `calculate_fleet_next_hex` -- wraps pure functions and mutates Fleet object

**Usage:**
```python
from game.strategy.services.fleet_navigation_service import FleetNavigationService

nav_service = FleetNavigationService()

# UI: project path for visualization
segments = nav_service.project_path(fleet, galaxy, max_turns=10)
for seg in segments:
    print(f"Turn {seg.turn}: {seg.start} -> {seg.end} (warp={seg.is_warp})")

# Turn execution: get next hex and mutate fleet
next_hex = nav_service.calculate_fleet_next_hex(fleet, galaxy)
if next_hex:
    fleet.location = next_hex

# Pure function usage with NavigationState
from game.strategy.services.fleet_navigation_service import NavigationState
state = NavigationState.from_fleet(fleet)
step = nav_service.compute_next_step(state, galaxy)
print(f"Next: {step.next_hex}, order_complete={step.order_complete}")
```

---

### FleetSpeedCalculator

**Location:** `game/strategy/services/fleet_speed_calculator.py`

**Purpose:** Calculates strategic movement speed (hexes per turn) for individual ships and fleets. Fleet speed is determined by its slowest combat-capable ship (convoy behavior).

**Dependencies:** None (all methods are `@staticmethod`).

**Constants:**
```python
K_STRATEGIC = 25           # Movement point to hex conversion factor
MAX_HEXES_PER_TURN = 10
MIN_HEXES_PER_TURN = 0
IMMOBILE_VEHICLE_TYPES = {'Planetary Complex', 'Satellite', 'Station'}
CARRIER_BASED_TYPES = {'Fighter'}
```

**Formula:** `hexes = floor((strategic_movement * K_STRATEGIC) / mass)`, clamped to [0, 10].

**Key Methods:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `calculate_ship_speed` | `(ship_instance: ShipInstance) -> int` | Calculate hexes/turn for a single ship from design data |
| `calculate_fleet_speed` | `(fleet: Fleet) -> float` | Calculate fleet speed as slowest combat-capable ship's speed |
| `update_fleet_speed` | `(fleet: Fleet) -> None` | Update `fleet.speed` in-place from current ship composition |

**Special cases for `calculate_ship_speed`:**
- Planetary complexes, satellites, stations: always 0 (immobile)
- Fighters: always 0 (carrier-based, no independent strategic movement)
- Ships with no `StrategicMovement` ability: 0

**Usage:**
```python
from game.strategy.services.fleet_speed_calculator import FleetSpeedCalculator

# Single ship speed
speed = FleetSpeedCalculator.calculate_ship_speed(ship_instance)
print(f"Ship speed: {speed} hexes/turn")

# Fleet speed (slowest ship)
fleet_speed = FleetSpeedCalculator.calculate_fleet_speed(fleet)

# Update fleet object in-place (call after adding/removing/damaging ships)
FleetSpeedCalculator.update_fleet_speed(fleet)
```

---

### ShipStatsCalculator

**Location:** `game/strategy/services/ship_stats_calculator.py`

**Purpose:** Calculates ship statistics dynamically from component definitions and damage state. Replaces reading from cached `expected_stats` to ensure stats accurately reflect component damage, toggles, and modifier effects.

**Dependencies:** Requires `GameRegistries` via constructor (strict DI, no fallback).

**Constants:**
```python
DEFAULT_DAMAGE_THRESHOLD = 0.5    # Components become inactive below 50% HP
NON_DEGRADING_TYPES = {'Armor'}   # Always 100% effective
FULL_HP_REQUIRED_ABILITIES = {'WarpJump'}  # Must be undamaged to function
```

**Key Methods:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `calculate_stats` | `(design_data: Dict, component_damage: Optional[Dict], component_toggles: Optional[Dict]) -> Dict[str, Any]` | Calculate all ship stats from design data, respecting damage and toggles |
| `get_component_effectiveness` | `(comp_id: str, comp_def, component_damage: Optional[Dict]) -> float` | Static. Calculate component effectiveness (0.0-1.0) based on damage |
| `has_warp_capability` | `(ship) -> bool` | Static. Check if a ship has functional warp (tonnage, storage, undamaged drive) |

**`calculate_stats` return dict:**
```python
{
    'max_hp': int,                            # Total HP from all components
    'mass': float,                            # Total mass (never degrades with damage)
    'resource_storage': Dict[str, float],     # resource_type -> capacity
    'resource_consumption_per_hex': Dict[str, float],   # per-hex costs
    'resource_consumption_per_turn': Dict[str, float],  # per-turn costs
    'warp_resource_costs': Dict[str, float],  # per-warp-jump costs
    'strategic_movement': float,              # Movement points for strategic map
    'warp_max_tonnage': int,                  # Max ship mass for warp (0 if damaged)
}
```

**Damage model:**
- Above threshold (50% HP): gradual linear degradation
- At or below threshold: component inactive (0% effectiveness)
- Armor: never degrades (always 100%)
- Warp drives: binary -- 100% HP required, any damage disables

**Usage:**
```python
from game.strategy.services.ship_stats_calculator import ShipStatsCalculator
from game.core.registry import GameRegistries

registries = GameRegistries.from_data_files()
calculator = ShipStatsCalculator(registries=registries)

# Calculate stats for undamaged ship
stats = calculator.calculate_stats(design_data)
print(f"HP: {stats['max_hp']}, Mass: {stats['mass']}")

# Calculate with damage
damage = {'bridge_0': 50, 'engine_0': 30}
stats = calculator.calculate_stats(design_data, component_damage=damage)

# Check warp capability
if ShipStatsCalculator.has_warp_capability(ship_instance):
    print("Ship can use warp points")
```

---

## Design Principles

### 1. Strict Dependency Injection

All services that need registries use **constructor injection with no fallback**:

```python
# Correct
service = VehicleDesignService(registries=game_registries)
service = ModifierService(modifier_registry=registries.modifiers)
service = ShipStatsCalculator(registries=game_registries)

# Raises TypeError
service = VehicleDesignService(registries=None)
```

Stateless services require no constructor args:
```python
service = BattleService()
nav_service = FleetNavigationService()
# FleetSpeedCalculator uses only static methods
```

### 2. Result Objects

Services return result objects for operations that can fail, rather than raising exceptions:

```python
@dataclass
class ServiceResult:
    success: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
```

**Handling results:**
```python
result = service.some_operation()
if result.success:
    process(result.data)
else:
    for error in result.errors:
        log_error(error)

for warning in result.warnings:
    log_warning(warning)
```

### 3. Pure Functions Where Possible

`FleetNavigationService` demonstrates the pattern of separating pure computation from mutation:
- **Pure core:** `compute_next_step(state, galaxy) -> NavigationStep` -- no side effects
- **Mutation bridge:** `calculate_fleet_next_hex(fleet, galaxy)` -- wraps pure function, applies changes to Fleet

### 4. Static Methods for Stateless Logic

`FleetSpeedCalculator` is entirely static -- no instance state needed. `ShipStatsCalculator.get_component_effectiveness` and `has_warp_capability` are also static.

---

## Layer Separation

```
+---------------------------------------------------------+
|                      UI Layer                           |
|  (builder_screen.py, battle_scene.py, strategy_screen)  |
+----------------------------+----------------------------+
                             | Uses
                             v
+---------------------------------------------------------+
|                   Service Layer                         |
|  Simulation: BattleService, VehicleDesignService,       |
|              ModifierService                            |
|  Strategy:   FleetNavigationService,                    |
|              FleetSpeedCalculator, ShipStatsCalculator   |
+----------------------------+----------------------------+
                             | Uses
                             v
+---------------------------------------------------------+
|                   Domain Layer                          |
|  (Ship, Component, BattleEngine, Fleet, Galaxy)         |
+---------------------------------------------------------+
```

**Rules:**
- UI can import services
- Services can import domain objects
- Domain should NOT import services or UI
- UI should NOT directly manipulate domain objects for complex operations

---

## Testing Services

Services are tested in:
```
tests/unit/services/                    # Simulation services
tests/unit/strategy/services/           # Strategy services
```

**Example Test:**
```python
class TestVehicleDesignService:
    def test_create_ship_returns_valid_ship(self, registries):
        service = VehicleDesignService(registries=registries)
        result = service.create_ship(
            name="Test Ship",
            ship_class="Escort",
            theme_id="Federation"
        )
        assert result.success is True
        assert result.ship is not None
        assert result.ship.name == "Test Ship"

    def test_add_invalid_component_returns_error(self, registries):
        service = VehicleDesignService(registries=registries)
        result = service.create_ship("Test", "Escort")
        ship = result.ship

        result = service.add_component(ship, "nonexistent_component", LayerType.OUTER)
        assert not result.success
        assert len(result.errors) > 0
```

---

*Last Updated: February 2026*
