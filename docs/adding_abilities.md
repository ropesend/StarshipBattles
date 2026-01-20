# Adding New Abilities

> Step-by-step guide for adding new abilities to the game.

## Overview

Abilities are behavior classes that:
1. Parse component data into typed attributes
2. Declare which stats they consume via STAT_BINDINGS
3. Implement game logic (firing, shields, movement, etc.)

## Quick Start

1. Create ability class in `game/simulation/components/abilities/`
2. Register in ABILITY_REGISTRY
3. Define STAT_BINDINGS for modifier integration
4. Implement recalculate() for stat application
5. Write tests

## Step 1: Create the Ability Class

Create in appropriate module (e.g., `abilities/movement.py`):

```python
from typing import Dict, Any, List
from .base import Ability, AbilityStatBinding, StatKey

class ThrusterAbility(Ability):
    """
    Example ability for thruster components.
    """

    # Declare which stats this ability consumes
    STAT_BINDINGS: List[AbilityStatBinding] = [
        AbilityStatBinding(StatKey.THRUST_MULT, 'thrust_force', 'multiply', '_base_thrust'),
        AbilityStatBinding(StatKey.FUEL_MULT, 'fuel_consumption', 'multiply', '_base_fuel'),
    ]

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

        # Parse data (handle dict or direct value)
        if isinstance(data, dict):
            self.thrust_force = data.get('thrust', 100)
            self.fuel_consumption = data.get('fuel', 1.0)
        else:
            self.thrust_force = data
            self.fuel_consumption = 1.0

        # Store base values for modifier calculations
        self._base_thrust = self.thrust_force
        self._base_fuel = self.fuel_consumption

    def recalculate(self):
        """Called when component stats change. Apply STAT_BINDINGS."""
        self.apply_stat_bindings()  # Base class method handles the work

    def get_ui_rows(self):
        """Return data for detail panel display."""
        return [
            {'label': 'Thrust', 'value': f"{self.thrust_force:.0f}", 'color_hint': '#96FF96'},
            {'label': 'Fuel/s', 'value': f"{self.fuel_consumption:.1f}", 'color_hint': '#FFFF96'},
        ]

    def get_primary_value(self) -> float:
        """Return the primary numeric value for aggregation."""
        return self.thrust_force
```

## Step 2: Register the Ability

Add to `game/simulation/components/abilities/__init__.py`:

```python
from .movement import ThrusterAbility

ABILITY_REGISTRY = {
    # ... existing entries ...
    'ThrusterAbility': ThrusterAbility,
    'Thruster': ThrusterAbility,  # Alias for JSON data
}
```

## Step 3: Define STAT_BINDINGS

STAT_BINDINGS connect modifier stats to ability attributes:

```python
STAT_BINDINGS: List[AbilityStatBinding] = [
    AbilityStatBinding(
        stat_key=StatKey.DAMAGE_MULT,    # From modifier
        attribute='damage',               # Ability attribute to modify
        operation='multiply',             # How to apply (multiply, add, set)
        base_attr='_base_damage'          # Where to store original value
    ),
]
```

### Available StatKeys

From `modifier_schema.py`:

| StatKey | Typical Use |
|---------|-------------|
| MASS_MULT | Component mass |
| HP_MULT | Component HP |
| COST_MULT | Resource costs |
| DAMAGE_MULT | Weapon damage |
| RANGE_MULT | Weapon range |
| RELOAD_MULT | Reload time |
| ARC_ADD | Add to firing arc |
| ARC_SET | Override firing arc |
| CREW_REQ_MULT | Crew requirements |
| CAPACITY_MULT | Storage/shield capacity |

### Operations

- `multiply`: `attribute = base_attr * stat_value`
- `add`: `attribute = base_attr + stat_value`
- `set`: `attribute = stat_value` (ignores base)

## Step 4: Implement recalculate()

Call `apply_stat_bindings()` to apply all STAT_BINDINGS:

```python
def recalculate(self):
    """Called when modifiers change."""
    self.apply_stat_bindings()

    # Optional: Additional calculations after stats applied
    self.effective_dps = self.damage / self.reload_time
```

### Custom Stat Handling

For non-standard calculations (like sqrt scaling):

```python
def recalculate(self):
    import math

    # Apply standard bindings first
    self.apply_stat_bindings()

    # Custom: Scale crew with sqrt of mass
    mass_mult = self.get_effective_stat('mass_mult', 1.0)
    crew_mult = math.sqrt(mass_mult)
    self.crew_required = int(math.ceil(self._base_crew * crew_mult))
```

## Step 5: Implement get_effective_stat()

Use inherited method for stat lookups:

```python
# In recalculate() or other methods:
damage_mult = self.get_effective_stat('damage_mult', default=1.0)

# For targeted effects, ability-specific stats are checked first
# Then global component.stats
```

## Step 6: Implement UI Methods

### get_ui_rows()

Returns display data for component detail panel:

```python
def get_ui_rows(self):
    return [
        {'label': 'Damage', 'value': f"{self.damage:.0f}", 'color_hint': '#FF9696'},
        {'label': 'Range', 'value': f"{self.range:.0f}m", 'color_hint': '#96FF96'},
        {'label': 'Reload', 'value': f"{self.reload_time:.1f}s", 'color_hint': '#C8C8C8'},
    ]
```

### get_primary_value()

Returns the main numeric value for aggregation:

```python
def get_primary_value(self) -> float:
    return self.thrust_force  # For totaling ship thrust
```

### get_effect_summary()

Returns introspection data for modifier display:

```python
def get_effect_summary(self):
    return [
        {
            'attribute': 'damage',
            'base': self._base_damage,
            'current': self.damage,
            'stat_key': 'damage_mult',
            'operation': 'multiply'
        },
        # ... more stats ...
    ]
```

## Step 7: Write Tests

### Unit Test

```python
def test_thruster_ability_stat_bindings():
    """ThrusterAbility should have correct STAT_BINDINGS."""
    from game.simulation.components.abilities.movement import ThrusterAbility
    from game.simulation.components.modifier_schema import StatKey

    assert ThrusterAbility.STAT_BINDINGS is not None

    # Find thrust binding
    thrust_binding = next(
        (b for b in ThrusterAbility.STAT_BINDINGS if b.stat_key == StatKey.THRUST_MULT),
        None
    )
    assert thrust_binding is not None
    assert thrust_binding.attribute == 'thrust_force'
```

### Integration Test

```python
def test_thruster_modifier_integration():
    """Modifiers should affect ThrusterAbility stats."""
    from game.simulation.components.component import Component

    comp_data = {
        'id': 'test_thruster',
        'name': 'Test Thruster',
        'type': 'Engine',
        'abilities': {
            'ThrusterAbility': {'thrust': 1000, 'fuel': 2.0}
        }
    }

    comp = Component(comp_data)
    thruster = comp.get_ability('ThrusterAbility')

    assert thruster.thrust_force == 1000

    # Apply modifier
    comp.add_modifier('engine_boost')  # 1.5x thrust
    comp.recalculate_stats()

    assert thruster.thrust_force == pytest.approx(1500)
```

## File Locations

| File | Purpose |
|------|---------|
| `game/simulation/components/abilities/base.py` | Ability base class |
| `game/simulation/components/abilities/__init__.py` | ABILITY_REGISTRY |
| `game/simulation/components/abilities/weapons.py` | Weapon abilities |
| `game/simulation/components/abilities/defense.py` | Shield, armor abilities |
| `game/simulation/components/abilities/movement.py` | Propulsion abilities |
| `game/simulation/components/abilities/crew.py` | Crew/life support |
| `game/simulation/components/abilities/resources.py` | Storage/generation |
| `game/simulation/components/modifier_schema.py` | StatKey enum |

## Marker Abilities

For abilities that mark a component but don't have numeric values:

```python
class CommandControlAbility(Ability):
    """Marker ability for command components."""

    STAT_BINDINGS = []  # No stats to consume

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

    def recalculate(self):
        pass  # No stats to recalculate

    def get_primary_value(self) -> float:
        return 0.0  # Marker abilities return 0
```

## Checklist

- [ ] Class created with STAT_BINDINGS
- [ ] Registered in ABILITY_REGISTRY
- [ ] `__init__()` parses data and stores `_base_*` values
- [ ] `recalculate()` calls `apply_stat_bindings()`
- [ ] `get_ui_rows()` returns display data
- [ ] `get_primary_value()` returns aggregation value
- [ ] Unit tests for STAT_BINDINGS
- [ ] Integration tests for modifier interaction
- [ ] All tests pass
