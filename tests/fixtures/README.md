# Test Fixtures Documentation

## Overview

This directory contains reusable test fixtures organized by domain. Fixtures eliminate boilerplate code and ensure consistent test setups across the test suite.

## Directory Structure

```
tests/fixtures/
    __init__.py           # Package initialization
    README.md             # This file
    ai.py                 # AI behavior fixtures
    battle.py             # Battle engine fixtures
    common.py             # Common utilities
    components.py         # Component fixtures
    paths.py              # Path constants
    ships.py              # Ship fixtures
    test_scenarios.py     # Pre-built test scenarios
```

## Fixture Modules

### ships.py

**Purpose:** Ship creation for tests.

**Fixtures:**
- `empty_ship` - Ship with only auto-equipped hull
- `basic_ship` - Ship with bridge and engine
- `armed_ship` - Ship with weapons
- `shielded_ship` - Ship with shields
- `fully_equipped_ship` - Ship with all common component types
- `two_opposing_ships` - Tuple of two ships on different teams

**Factory Function:**
```python
from tests.fixtures.ships import create_test_ship

ship = create_test_ship(
    name="Custom Ship",
    x=100, y=200,
    ship_class="Escort",
    add_bridge=True,
    add_engine=True,
    add_weapons=2
)
```

---

### components.py

**Purpose:** Component creation for tests.

**Fixtures:**
- `weapon_component` - Laser cannon
- `engine_component` - Standard engine
- `shield_component` - Shield generator
- `armor_component` - Armor plate
- `bridge_component` - Bridge
- `crew_quarters_component` - Crew quarters
- `life_support_component` - Life support

**Factory Functions:**
```python
from tests.fixtures.components import create_weapon, create_engine

weapon = create_weapon()  # Default laser cannon
engine = create_engine("advanced_engine")  # Specific ID
```

---

### battle.py

**Purpose:** Battle engine setup for tests.

**Fixtures:**
- `battle_engine` - Clean BattleEngine with no ships
- `battle_engine_with_ships` - BattleEngine with two opposing ships
- `mock_battle_engine` - Mock for unit tests
- `mock_battle_scene` - Mock scene with engine

**Factory Functions:**
```python
from tests.fixtures.battle import create_battle_engine, create_battle_engine_with_ships

engine = create_battle_engine(enable_logging=True)
engine = create_battle_engine_with_ships(team1_count=3, team2_count=2)
```

---

### paths.py

**Purpose:** Path constants for tests.

**Fixtures:**
- `project_root` - Path to project root
- `data_dir` - Path to data directory
- `assets_dir` - Path to assets directory
- `test_data_dir` - Path to test data directory

---

### ai.py

**Purpose:** AI behavior fixtures.

Provides pre-configured AI behaviors and mock targets for AI testing.

---

### common.py

**Purpose:** Common test utilities.

Shared helper functions used across multiple fixture modules.

---

## Usage Patterns

### Using Fixtures in Tests

Fixtures are automatically injected by pytest:

```python
def test_ship_has_hull(basic_ship):
    """basic_ship fixture is auto-injected."""
    assert basic_ship.hull is not None

def test_weapon_deals_damage(weapon_component):
    """weapon_component fixture is auto-injected."""
    assert weapon_component.has_ability('WeaponAbility')
```

### Using Factory Functions

For custom configurations, use factory functions directly:

```python
from tests.fixtures.ships import create_test_ship
from tests.fixtures.components import create_weapon

def test_custom_ship():
    ship = create_test_ship(
        name="Heavy Cruiser",
        add_weapons=4,
        add_shields=2
    )
    assert len(ship.get_components_by_ability('WeaponAbility')) == 4
```

### Combining Fixtures

Fixtures can depend on other fixtures:

```python
@pytest.fixture
def armed_escort(basic_ship):
    """Add weapons to a basic ship."""
    weapon = create_weapon()
    basic_ship.add_component(weapon, LayerType.OUTER)
    return basic_ship
```

### Test-Specific Conftest

Each test subdirectory can have a `conftest.py` that imports needed fixtures:

```python
# tests/unit/combat/conftest.py
from tests.fixtures.ships import basic_ship, armed_ship
from tests.fixtures.battle import battle_engine, battle_engine_with_ships
```

---

## Fixture vs Factory: When to Use Which

### Use Fixtures When:
- You need a standard, unchanged object
- The object doesn't need customization
- You want pytest's automatic injection
- You need fixture-level setup/teardown

```python
def test_basic_functionality(basic_ship):
    # basic_ship is clean and consistent every time
    assert basic_ship.name == "TestShip"
```

### Use Factories When:
- You need custom configuration
- You need multiple instances with variations
- You're building complex test scenarios
- You need control over object creation timing

```python
def test_fleet_battle():
    # Create multiple customized ships
    ships = [
        create_test_ship(f"Ship_{i}", add_weapons=i+1)
        for i in range(5)
    ]
    assert all(s.has_components() for s in ships)
```

---

## Adding New Fixtures

1. **Identify the domain** - Which module should contain the fixture?
2. **Write a factory function** - Flexible, parameterized creation
3. **Write a pytest fixture** - Uses factory with sensible defaults
4. **Document in module docstring** - Add to "Available fixtures" list
5. **Update this README** - Add to appropriate section

**Template:**
```python
# In appropriate module (e.g., ships.py)

def create_custom_thing(param1: str = "default") -> Thing:
    """Factory function with customization options."""
    return Thing(param1)

@pytest.fixture
def custom_thing():
    """Fixture using factory with defaults."""
    return create_custom_thing()
```

---

## Fixture Dependencies

Some fixtures depend on game data being loaded. The `reset_game_state` autouse fixture in `tests/unit/conftest.py` ensures registries are populated before tests run.

**Marker for custom data tests:**
```python
@pytest.mark.use_custom_data
def test_with_custom_registry():
    # This test uses custom component definitions
    pass
```

---

*Last Updated: January 2026*
