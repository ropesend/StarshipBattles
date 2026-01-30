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
    common.py             # Data initialization fixtures
    components.py         # Component fixtures
    paths.py              # Path utilities
    ships.py              # Ship fixtures
    test_scenarios.py     # Combat Lab scenario mocks
```

---

## Module Documentation

### paths.py

**Purpose:** Path utilities and fixtures for consistent path resolution.

**Utility Functions:**
```python
from tests.fixtures.paths import (
    get_project_root,       # Returns Path to project root
    get_data_dir,           # Returns Path to data/ directory
    get_assets_dir,         # Returns Path to assets/ directory
    get_test_data_dir,      # Returns Path to tests/data/
    get_unit_test_data_dir, # Returns Path to tests/unit/data/
    get_simulation_test_data_dir,  # Returns Path to simulation_tests/data/
)
```

**Fixtures:**
| Fixture | Scope | Description |
|---------|-------|-------------|
| `project_root` | function | Path to project root |
| `data_dir` | function | Path to data/ directory |
| `assets_dir` | function | Path to assets/ directory |
| `test_data_dir` | function | Path to tests/data/ |
| `unit_test_data_dir` | function | Path to tests/unit/data/ |
| `simulation_test_data_dir` | function | Path to simulation_tests/data/ |

---

### common.py

**Purpose:** Data initialization fixtures for loading game data.

**Fixtures:**
| Fixture | Scope | Description |
|---------|-------|-------------|
| `initialized_ship_data` | function | Loads vehicle classes + components |
| `initialized_ship_data_with_modifiers` | function | Loads vehicle classes + components + modifiers |

**Note:** For read-only tests that don't modify registry state, prefer the session-scoped
`global_ship_data` and `global_ship_data_with_modifiers` fixtures in `tests/conftest.py`.

---

### ships.py

**Purpose:** Ship creation for tests.

**Factory Function:**
```python
from tests.fixtures.ships import create_test_ship

ship = create_test_ship(
    name="Custom Ship",      # Ship name
    x=100, y=200,            # Position
    color=(255, 255, 255),   # RGB color
    ship_class="Escort",     # Vehicle class name
    team_id=0,               # Team ID
    add_bridge=True,         # Add bridge component
    add_engine=True,         # Add engine component
    add_weapons=2,           # Number of weapons to add
    add_shields=1,           # Number of shields to add
    add_crew=True,           # Add crew quarters + life support (default)
)
```

**Fixtures:**
| Fixture | Scope | Description |
|---------|-------|-------------|
| `empty_ship` | function | Ship with only auto-equipped hull |
| `basic_ship` | function | Ship with bridge and engine |
| `armed_ship` | function | Ship with weapons and shields |
| `shielded_ship` | function | Ship with shields, no weapons |
| `fully_equipped_ship` | function | Ship with all common component types |
| `two_opposing_ships` | function | Tuple of (ship1, ship2) on different teams |
| `basic_cruiser_ship` | function | Cruiser class ship (requires initialized_ship_data) |
| `basic_escort_ship` | function | Escort class ship (requires initialized_ship_data) |

---

### components.py

**Purpose:** Component creation for tests.

**Factory Functions:**
```python
from tests.fixtures.components import (
    create_weapon,          # Creates laser_cannon
    create_engine,          # Creates standard_engine
    create_shield,          # Creates shield_generator
    create_armor,           # Creates armor_plate
    create_bridge,          # Creates bridge
    create_crew_quarters,   # Creates crew_quarters
    create_life_support,    # Creates life_support
)

# Custom component ID
weapon = create_weapon("advanced_laser")
```

**Fixtures:**
| Fixture | Scope | Description |
|---------|-------|-------------|
| `weapon_component` | function | Laser cannon component |
| `engine_component` | function | Standard engine component |
| `shield_component` | function | Shield generator component |
| `armor_component` | function | Armor plate component |
| `bridge_component` | function | Bridge component |
| `crew_quarters_component` | function | Crew quarters component |
| `life_support_component` | function | Life support component |

---

### battle.py

**Purpose:** Battle engine setup for combat tests.

**Factory Functions:**
```python
from tests.fixtures.battle import (
    create_battle_engine,           # Clean engine, no ships
    create_battle_engine_with_ships, # Engine with ships added
    create_mock_battle_engine,      # Mock for unit tests
    create_mock_battle_screen,      # Mock battle screen
)

engine = create_battle_engine(enable_logging=True)
engine = create_battle_engine_with_ships(team1_count=3, team2_count=2)
```

**Fixtures:**
| Fixture | Scope | Description |
|---------|-------|-------------|
| `battle_engine` | function | Clean BattleEngine with no ships |
| `battle_engine_with_ships` | function | BattleEngine with two opposing ships |
| `mock_battle_engine` | function | Mock for unit tests |
| `mock_battle_screen` | function | Mock battle screen with engine |

---

### ai.py

**Purpose:** AI-related fixtures and setup.

**Fixtures:**
| Fixture | Scope | Description |
|---------|-------|-------------|
| `strategy_manager_with_test_data` | function | StrategyManager loaded with test AI policies |

**Usage:**
```python
def test_ai_targeting(strategy_manager_with_test_data):
    manager = strategy_manager_with_test_data
    # Manager has test targeting, movement, and strategy policies loaded
```

---

### test_scenarios.py

**Purpose:** Mock fixtures for Combat Lab service tests.

**Factory Functions:**
```python
from tests.fixtures.test_scenarios import (
    create_test_metadata,       # Create TestMetadata with defaults
    create_mock_test_scenario,  # Create mock TestScenario
    create_mock_test_registry,  # Create mock TestRegistry
    create_mock_test_runner,    # Create mock TestRunner
    create_mock_test_history,   # Create mock TestHistory
    create_scenario_info,       # Create scenario info dict
    create_sample_ship_data,    # Create sample ship JSON
    create_sample_component_data, # Create sample component JSON
)
```

**Fixtures:**
| Fixture | Scope | Description |
|---------|-------|-------------|
| `sample_test_metadata` | function | Sample TestMetadata object |
| `mock_test_scenario` | function | Mock TestScenario instance |
| `mock_test_registry` | function | Mock TestRegistry instance |
| `mock_test_runner` | function | Mock TestRunner instance |
| `mock_test_history` | function | Mock TestHistory instance |
| `sample_scenario_info` | function | Sample scenario info dict |
| `sample_ship_data` | function | Sample ship JSON data |
| `sample_component_data` | function | Sample component JSON data |

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
    """
    Factory function with customization options.

    Args:
        param1: Description of parameter

    Returns:
        Thing instance
    """
    return Thing(param1)


@pytest.fixture
def custom_thing():
    """
    Fixture using factory with defaults.

    Returns a Thing instance for testing basic functionality.
    """
    return create_custom_thing()
```

---

## Fixture Dependencies

Some fixtures depend on game data being loaded. The `reset_game_state` autouse fixture in the root `conftest.py` ensures registries are populated before tests run.

**Marker for custom data tests:**
```python
@pytest.mark.use_custom_data
def test_with_custom_registry():
    # This test uses custom component definitions
    # Production data will NOT be hydrated
    pass
```

---

## See Also

- [tests/README.md](../README.md) - Test suite overview and fixture hierarchy
- [CLAUDE.md](../../CLAUDE.md) - Development guidelines

---

*Last Updated: January 2026 (PROJ-48 Phase 2)*
