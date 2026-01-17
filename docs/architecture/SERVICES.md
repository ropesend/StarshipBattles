# Service Layer Architecture

## Overview

The Starship Battles codebase uses a service layer pattern to provide clean abstractions between UI components and domain logic. Services act as facades that encapsulate complex operations and provide stable APIs for UI consumption.

## Service Directory

Services are located in `game/simulation/services/`:

```
game/simulation/services/
    __init__.py
    battle_service.py      # Battle creation and simulation control
    data_service.py        # Data loading and registry management
    modifier_service.py    # Component modifier handling
    ship_builder_service.py    # Ship creation and modification
```

## Core Services

### BattleService

**Location:** `game/simulation/services/battle_service.py`

**Purpose:** Provides an abstraction between UI and BattleEngine, handling battle creation, ship management, and simulation control.

**Key Methods:**
- `create_battle(seed, enable_logging)` - Create a new battle instance
- `add_ship(ship, team_id)` - Add a ship to a team (before start)
- `remove_ship(ship)` - Remove a ship (before start)
- `start_battle(end_mode, max_ticks)` - Start the simulation
- `update()` - Run one simulation tick
- `run_ticks(count)` - Run multiple ticks
- `is_battle_over()` - Check if battle has ended
- `get_winner()` - Get winning team ID
- `get_battle_state()` - Get current battle state dict
- `get_all_ships()` - Get all ships in battle
- `get_alive_ships()` - Get all living ships
- `reset()` - Clear battle state

**Result Object:**
```python
@dataclass
class BattleResult:
    success: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    engine: Optional[BattleEngine] = None
```

**Usage:**
```python
from game.simulation.services.battle_service import BattleService
from game.simulation.systems.battle_end_conditions import BattleEndMode

# Create and configure battle
service = BattleService()
result = service.create_battle(seed=42, enable_logging=True)

# Add ships to teams
service.add_ship(ship1, team_id=0)
service.add_ship(ship2, team_id=1)

# Start and run battle
service.start_battle(end_mode=BattleEndMode.HP_BASED)

while not service.is_battle_over():
    service.update()
    state = service.get_battle_state()
    print(f"Tick {state['tick_count']}: {len(state['team_0_ships'])} vs {len(state['team_1_ships'])}")

# Get result
winner = service.get_winner()
print(f"Winner: Team {winner}")
```

---

### DataService

**Location:** `game/simulation/services/data_service.py`

**Purpose:** Centralizes all data access operations, providing a facade over the Registry system for querying components, modifiers, and vehicle classes.

**Key Methods:**
- `is_loaded()` - Check if data is loaded
- `get_components()` - Get all component definitions
- `get_modifiers()` - Get all modifier definitions
- `get_vehicle_classes()` - Get all vehicle class definitions
- `get_component(id)` - Get specific component
- `get_modifier(id)` - Get specific modifier
- `get_vehicle_class(name)` - Get specific vehicle class
- `get_components_by_classification(classification)` - Filter by classification
- `get_components_by_ability(ability_name)` - Filter by ability
- `get_classes_by_type(vehicle_type)` - Filter classes by type
- `get_data_summary()` - Get summary of loaded data

**Usage:**
```python
from game.simulation.services.data_service import DataService

service = DataService()

# Check if data is loaded
if service.is_loaded():
    # Get specific items
    laser = service.get_component("laser_cannon")
    escort_class = service.get_vehicle_class("Escort")

    # Filter components
    weapons = service.get_components_by_classification("Weapons")
    engines = service.get_components_by_ability("CombatPropulsion")

    # Get summary
    summary = service.get_data_summary()
    print(f"Loaded {summary['component_count']} components")
```

---

### ModifierService

**Location:** `game/simulation/services/modifier_service.py`

**Purpose:** Handles modifier-related logic including mandatory modifier management, allowance checking, and value constraints. This service was extracted from the UI layer to fix improper layer coupling.

**Key Methods:**
- `is_modifier_allowed(mod_id, component)` - Check if modifier is valid for component
- `get_mandatory_modifiers(component)` - Get list of required modifier IDs
- `is_modifier_mandatory(mod_id, component)` - Check if specific modifier is mandatory
- `get_initial_value(mod_id, component)` - Get default value for a modifier
- `ensure_mandatory_modifiers(component)` - Add all required modifiers to component
- `get_local_min_max(mod_id, component)` - Get (min, max) range for modifier

**Mandatory Modifiers:**
The following modifiers cannot be removed by users: `simple_size_mount`, `range_mount`, `facing`, `turret_mount`

**Usage:**
```python
from game.simulation.services.modifier_service import ModifierService

# Check what modifiers are allowed
if ModifierService.is_modifier_allowed('turret_mount', weapon):
    print("Turret mount available for this weapon")

# Get mandatory modifiers for a component
mandatory = ModifierService.get_mandatory_modifiers(weapon)
# Returns: ['simple_size_mount', 'range_mount', 'facing', 'turret_mount', ...]

# Ensure all mandatory modifiers are present
ModifierService.ensure_mandatory_modifiers(weapon)

# Get valid range for a modifier
min_val, max_val = ModifierService.get_local_min_max('turret_mount', weapon)
print(f"Turret arc range: {min_val} to {max_val} degrees")
```

---

### ShipBuilderService

**Location:** `game/simulation/services/ship_builder_service.py`

**Purpose:** Provides high-level operations for ship creation and modification, abstracting away the complexities of layer management, validation, and stat recalculation.

**Key Methods:**
- `create_ship(name, ship_class, theme_id)` - Create a new ship
- `add_component(ship, component_id, layer)` - Add component with validation
- `remove_component(ship, layer, index)` - Remove component at index
- `validate_design(ship)` - Full design validation
- `get_available_components(ship, layer)` - Get valid components for layer

**Result Object:**
```python
@dataclass
class ShipBuilderResult:
    success: bool
    ship: Optional[Ship] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
```

**Usage:**
```python
from game.simulation.services.ship_builder_service import ShipBuilderService
from game.simulation.components.component import LayerType

builder = ShipBuilderService()

# Create a new ship
result = builder.create_ship(
    name="USS Enterprise",
    ship_class="Cruiser",
    theme_id="Federation"
)

if result.success:
    ship = result.ship

    # Add components
    result = builder.add_component(ship, "laser_cannon", LayerType.OUTER)
    if not result.success:
        print(f"Failed: {result.errors}")

    # Validate complete design
    validation = builder.validate_design(ship)
    if validation.warnings:
        print(f"Warnings: {validation.warnings}")
```

---

## Design Principles

### 1. Single Responsibility

Each service has a focused purpose:
- **BattleService**: Battle lifecycle management
- **DataService**: Data access and queries
- **ModifierService**: Modifier logic
- **ShipBuilderService**: Ship construction

### 2. Facade Pattern

Services hide complex internal operations behind simple APIs. UI code doesn't need to know about registries, validators, or layer iteration.

### 3. Result Objects

Services return result objects for operations that can fail, rather than raising exceptions:

```python
@dataclass
class ServiceResult:
    success: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
```

**Handling Results:**
```python
result = service.some_operation()

if result.success:
    # Operation succeeded
    process(result.data)
else:
    # Operation failed
    for error in result.errors:
        log_error(error)
    show_user_error(result.errors[0])

# Always check warnings
for warning in result.warnings:
    log_warning(warning)
```

### 4. Static vs Instance Methods

- **ModifierService**: Uses static methods (no state needed)
- **DataService**: Instance methods (queries registry)
- **BattleService**: Instance methods (manages battle state)
- **ShipBuilderService**: Instance methods (may cache validators)

---

## Layer Separation

The service layer enforces proper separation between layers:

```
┌─────────────────────────────────────────────────────────────┐
│                        UI Layer                              │
│   (builder_screen.py, battle_scene.py, setup_screen.py)     │
└─────────────────────────┬───────────────────────────────────┘
                          │ Uses
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer                             │
│   (BattleService, DataService, ModifierService,             │
│    ShipBuilderService)                                       │
└─────────────────────────┬───────────────────────────────────┘
                          │ Uses
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Domain Layer                              │
│   (Ship, Component, BattleEngine, Validators)               │
└─────────────────────────────────────────────────────────────┘
```

**Rules:**
- UI can import Services
- Services can import Domain
- Domain should NOT import UI or Services
- UI should NOT directly manipulate Domain objects for complex operations

---

## Testing Services

Services are tested in `tests/unit/services/`:

```
tests/unit/services/
    test_battle_service.py
    test_data_service.py
    test_modifier_service.py
    test_ship_builder_service.py
```

**Example Test:**
```python
class TestShipBuilderService:
    def test_create_ship_returns_valid_ship(self, service):
        result = service.create_ship(
            name="Test Ship",
            ship_class="Escort",
            theme_id="Federation"
        )

        assert result.success is True
        assert result.ship is not None
        assert result.ship.name == "Test Ship"

    def test_add_component_validates(self, service):
        result = service.create_ship("Test", "Escort")
        ship = result.ship

        result = service.add_component(
            ship=ship,
            component_id="invalid_component",
            layer=LayerType.OUTER
        )

        assert not result.success
        assert len(result.errors) > 0
```

---

## Migration Guide

When adding new functionality:

1. **Identify the domain logic** - What operations need to happen?
2. **Check existing services** - Can an existing service be extended?
3. **Create new service if needed** - Following the patterns above
4. **Write tests first** - Test the service in isolation
5. **Update UI to use service** - Replace direct domain manipulation
6. **Document the service** - Update this file with API documentation

---

*Last Updated: January 2026*
