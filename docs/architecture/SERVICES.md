# Service Layer Architecture

## Overview

The Starship Battles codebase uses a service layer pattern to provide clean abstractions between UI components and domain logic. Services act as facades that encapsulate complex operations and provide stable APIs for UI consumption.

## Service Directory

Services are located in `game/simulation/services/`:

```
game/simulation/services/
    __init__.py
    data_service.py        # Data loading and registry management
    modifier_service.py    # Component modifier handling
    ship_builder_service.py    # Ship creation and modification
```

## Core Services

### DataService

**Location:** `game/simulation/services/data_service.py`

**Purpose:** Centralizes all data loading operations and ensures the Registry is properly populated before use.

**Key Methods:**
- `ensure_loaded()` - Lazy-load all game data
- `get_component(id)` - Retrieve component definition
- `get_modifier(id)` - Retrieve modifier definition
- `get_vehicle_class(id)` - Retrieve ship class definition

**Usage:**
```python
from game.simulation.services.data_service import DataService

service = DataService.instance()
service.ensure_loaded()

component = service.get_component("laser_cannon")
```

### ModifierService

**Location:** `game/simulation/services/modifier_service.py`

**Purpose:** Handles mandatory modifier application and modifier-related logic. This service was extracted from the UI layer to fix improper layer coupling.

**Key Methods:**
- `ensure_mandatory_modifiers(component, layer_type)` - Add required modifiers based on component/layer rules

**Background:**
Previously, `Ship.add_component()` imported from `ui.builder.modifier_logic`, creating an improper dependency from domain to UI. This service moves that logic to the simulation layer where it belongs.

**Usage:**
```python
from game.simulation.services.modifier_service import ModifierService

service = ModifierService()
service.ensure_mandatory_modifiers(component, LayerType.OUTER)
```

### ShipBuilderService

**Location:** `game/simulation/services/ship_builder_service.py`

**Purpose:** Provides high-level operations for ship creation and modification, abstracting away the complexities of layer management, validation, and stat recalculation.

**Key Methods:**
- `create_ship(name, ship_class, theme_id)` - Create a new ship
- `add_component(ship, component_id, layer)` - Add component with validation
- `remove_component(ship, layer, index)` - Remove component at index
- `validate_design(ship)` - Full design validation

**Usage:**
```python
from game.simulation.services.ship_builder_service import ShipBuilderService

builder = ShipBuilderService()
ship = builder.create_ship("USS Enterprise", "Cruiser", "Federation")

result = builder.add_component(ship, "laser_cannon", LayerType.OUTER)
if not result.success:
    print(f"Failed: {result.error}")
```

## Design Principles

### 1. Single Responsibility

Each service has a focused purpose. DataService handles data loading, ModifierService handles modifiers, etc.

### 2. Facade Pattern

Services hide complex internal operations behind simple APIs. UI code doesn't need to know about registries, validators, or layer iteration.

### 3. Instance Pattern

Services that need global state (like DataService) use the singleton pattern with `instance()` classmethod for consistent access.

### 4. Lazy Loading

Services use lazy loading to defer expensive operations until actually needed:

```python
def ensure_loaded(self):
    if not self._loaded:
        self._load_data()
        self._loaded = True
```

### 5. Result Objects

Services return result objects for operations that can fail, rather than raising exceptions:

```python
@dataclass
class ValidationResult:
    success: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
```

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
│   (ShipBuilderService, DataService, ModifierService)        │
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

## Testing Services

Services are tested in `tests/unit/simulation/services/`:

```python
class TestShipBuilderService:
    def test_create_ship_returns_valid_ship(self):
        builder = ShipBuilderService()
        ship = builder.create_ship("Test", "Frigate", "Federation")

        assert ship.name == "Test"
        assert ship.ship_class == "Frigate"
        assert ship.hull is not None

    def test_add_component_validates(self):
        builder = ShipBuilderService()
        ship = builder.create_ship("Test", "Frigate", "Federation")

        result = builder.add_component(ship, "invalid_component", LayerType.OUTER)

        assert not result.success
        assert "not found" in result.errors[0]
```

## Migration Guide

When adding new functionality:

1. **Identify the domain logic** - What operations need to happen?
2. **Check existing services** - Can an existing service be extended?
3. **Create new service if needed** - Following the patterns above
4. **Write tests first** - Test the service in isolation
5. **Update UI to use service** - Replace direct domain manipulation
