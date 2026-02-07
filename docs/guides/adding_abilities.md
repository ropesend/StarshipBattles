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
from .base import Ability
from .stat_keys import AbilityStatBinding, StatKey

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

From `game/simulation/components/abilities/stat_keys.py`:

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

### Stat Resolution Order

When `get_effective_stat()` is called, values are resolved in this priority:

1. **Targeted ability stats:** `component.ability_stats[ClassName][stat_key]`
2. **Global component stats:** `component.stats[stat_key]`
3. **Default value:** Based on stat type:
   - `*_mult` stats → `1.0`
   - `*_add` stats → `0.0`
   - Other stats → `None` (or explicit default)

**Example with defaults:**
```python
def recalculate(self):
    # Multiplicative stats default to 1.0 (no change)
    damage_mult = self.get_effective_stat('damage_mult', 1.0)

    # Additive stats default to 0.0 (no change)
    arc_add = self.get_effective_stat('arc_add', 0.0)

    # Apply modifications
    self.damage = self._base_damage * damage_mult
    self.firing_arc = self._base_arc + arc_add
```

**Targeted vs Global Effects:**
- **Targeted:** `target_ability: "WeaponAbility"` only affects that ability class
- **Global:** No `target_ability` affects all abilities on the component

```python
# Modifier targets only ProjectileWeaponAbility
{"stat": "damage_mult", "formula": "1.5", "target_ability": "ProjectileWeaponAbility"}

# Modifier affects ALL abilities on the component
{"stat": "damage_mult", "formula": "1.2"}
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

## Working with Ship Layers

Ships organize components into layers. Understanding this structure helps when abilities need to query other components.

### Layer Structure

```python
ship.layers = {
    LayerType.HULL: {'components': [hull_component]},
    LayerType.INTERNAL: {'components': [engine, reactor, ...]},
    LayerType.EXTERNAL: {'components': [armor, sensor, ...]},
    LayerType.WEAPONS: {'components': [turret1, turret2, ...]}
}
```

### LayerType Reference

| LayerType | Contents |
|-----------|----------|
| `HULL` | Ship hull (exactly one) |
| `INTERNAL` | Engines, reactors, crew quarters, storage |
| `EXTERNAL` | Armor, shields, sensors |
| `WEAPONS` | Turrets, missile launchers, point defense |

### Common Iteration Patterns

**Get all components with a specific ability:**
```python
# Get all operational weapons
weapons = ship.get_components_by_ability('WeaponAbility', operational_only=True)

# Get all thrusters (including damaged)
thrusters = ship.get_components_by_ability('CombatPropulsion', operational_only=False)
```

**Iterate over a specific layer:**
```python
from game.simulation.entities.layer_type import LayerType

for comp in ship.layers[LayerType.WEAPONS]['components']:
    if comp.is_operational():
        weapon = comp.get_ability('WeaponAbility')
        # Process weapon...
```

**Sum values across all components with an ability:**
```python
total_thrust = sum(
    comp.get_ability('CombatPropulsion').get_primary_value()
    for comp in ship.get_components_by_ability('CombatPropulsion', operational_only=True)
)
```

### Ability Access Methods

| Method | Returns | Notes |
|--------|---------|-------|
| `comp.has_ability('Name')` | `bool` | Check if ability exists |
| `comp.get_ability('Name')` | `Ability` or `None` | Get ability instance |
| `comp.get_abilities()` | `List[Ability]` | All abilities on component |

```python
# Safe ability access
if comp.has_ability('ShieldProjection'):
    shield = comp.get_ability('ShieldProjection')
    shield_strength = shield.get_primary_value()
```

## Step 7: Write Tests

### Unit Test

```python
def test_thruster_ability_stat_bindings():
    """ThrusterAbility should have correct STAT_BINDINGS."""
    from game.simulation.components.abilities.movement import ThrusterAbility
    from game.simulation.components.abilities.stat_keys import StatKey

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
| `game/simulation/components/abilities/stat_keys.py` | StatKey enum, AbilityStatBinding |

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

## Common Errors and Solutions

### Missing STAT_BINDINGS

**Symptom:** Modifiers have no effect on ability stats.

**Cause:** Ability class has no STAT_BINDINGS defined or is empty.

**Solution:**
```python
class MyAbility(Ability):
    STAT_BINDINGS = [
        AbilityStatBinding(StatKey.DAMAGE_MULT, 'damage', 'multiply', '_base_damage'),
    ]
```

### Invalid StatKey

**Symptom:** `KeyError` when applying modifiers.

**Cause:** Using string instead of StatKey enum, or using an undefined stat key.

**Solution:** Always use `StatKey` enum values:
```python
# Wrong
AbilityStatBinding('damage_mult', 'damage', ...)

# Correct
AbilityStatBinding(StatKey.DAMAGE_MULT, 'damage', ...)
```

### Missing Base Attribute

**Symptom:** `AttributeError: '_base_damage'` in recalculate().

**Cause:** STAT_BINDINGS references a `_base_*` attribute that wasn't set in `__init__()`.

**Solution:** Store base values when parsing component data:
```python
def __init__(self, component, data):
    super().__init__(component, data)
    self.damage = data.get('damage', 10)
    self._base_damage = self.damage  # Store base value
```

### Ability Not Found

**Symptom:** `KeyError` when loading component from JSON.

**Cause:** Ability class not registered in ABILITY_REGISTRY.

**Solution:** Add to `game/simulation/components/abilities/__init__.py`:
```python
ABILITY_REGISTRY = {
    'MyAbility': MyAbility,
    'My': MyAbility,  # Optional short alias
}
```

### recalculate() Not Called

**Symptom:** Stats don't update when modifiers change.

**Cause:** `recalculate()` method doesn't call `apply_stat_bindings()`.

**Solution:** Always call the base class method:
```python
def recalculate(self):
    self.apply_stat_bindings()  # This applies all STAT_BINDINGS
    # Additional custom calculations here
