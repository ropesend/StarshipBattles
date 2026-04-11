# Adding New Abilities

> Step-by-step guide for adding new abilities to the game.
> For a complete catalog of all existing abilities, see [ability_reference.md](../systems/ability_reference.md).

## Overview

Abilities are behavior classes that:
1. Parse component data into typed attributes
2. Declare which stats they consume via STAT_BINDINGS
3. Implement game logic (firing, shields, movement, etc.)

## Quick Start

1. Create ability class in `game/simulation/components/abilities/`
2. Register in ABILITY_REGISTRY
3. Define STAT_BINDINGS for modifier integration
4. Implement `recalculate()` for stat application
5. Write tests

## Choosing a Base Class

Most new abilities should extend `SimpleMultiplierAbility` (defined in `abilities/base.py`). Use the raw `Ability` base class only when you need custom multi-stat logic.

| Base Class | When to Use |
|------------|-------------|
| `SimpleMultiplierAbility` | Single numeric value with one multiplier stat |
| `Ability` | Multiple stats, custom recalculate logic, marker abilities |

## Step 1: Create the Ability Class (SimpleMultiplierAbility)

This is the standard pattern. Create in the appropriate module (e.g., `abilities/propulsion.py`):

```python
from typing import List
from .base import SimpleMultiplierAbility
from .stat_keys import StatKey, AbilityStatBinding
from .ui_colors import HINT_THRUST

class ThrusterAbility(SimpleMultiplierAbility):
    """Provides thrust force for combat movement."""

    # Required class attributes (validated at class creation time)
    stat_key = 'thrust_mult'           # Modifier stat key string
    value_attr = 'thrust_force'        # Name of current-value attribute
    base_attr = 'base_thrust'          # Name of base-value attribute
    ui_label = 'Thrust'                # Display label for UI
    ui_format = '{:.0f} N'             # Format string for value display
    ui_color = HINT_THRUST             # Color hint from ui_colors.py
    int_result = False                 # Set True to cast result to int

    # Declare stat bindings for modifier introspection
    STAT_BINDINGS: List[AbilityStatBinding] = [
        AbilityStatBinding(StatKey.THRUST_MULT, 'thrust_force', 'multiply', 'base_thrust'),
    ]
```

That is the complete implementation. `SimpleMultiplierAbility` provides:
- `__init__()` - parses value from data using `_parse_primary_value()`
- `sync_data()` - updates base value when component data changes
- `recalculate()` - applies `get_effective_stat(stat_key) * base` to value
- `get_ui_rows()` - returns formatted UI row
- `get_primary_value()` - returns current value as float

Real examples using this pattern: `CombatPropulsion`, `ManeuveringThruster`, `StrategicMovement`, `ShieldProjection`, `ShieldRegeneration`, `CrewCapacity`, `LifeSupportCapacity`.

## Step 1 (Alternative): Create from Raw Ability Base Class

For abilities that need custom logic (multiple stats, non-standard operations, etc.):

```python
from typing import Dict, Any, List
from .base import Ability
from .stat_keys import StatKey, AbilityStatBinding
from .ui_colors import HINT_DAMAGE

class CustomAbility(Ability):
    """Example ability with multiple stats."""

    STAT_BINDINGS: List[AbilityStatBinding] = [
        AbilityStatBinding(StatKey.DAMAGE_MULT, 'damage', 'multiply', '_base_damage'),
        AbilityStatBinding(StatKey.RANGE_MULT, 'range', 'multiply', '_base_range'),
    ]

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

        # Parse data (handle dict or direct value)
        if isinstance(data, dict):
            self.damage = float(data.get('damage', 0))
            self.range = float(data.get('range', 0))
        else:
            self.damage = self._parse_primary_value(data)
            self.range = 0.0

        # Store base values for modifier calculations
        self._base_damage = self.damage
        self._base_range = self.range

    def recalculate(self):
        """Apply modifiers using get_effective_stat()."""
        self.damage = self._base_damage * self.get_effective_stat('damage_mult', 1.0)
        self.range = self._base_range * self.get_effective_stat('range_mult', 1.0)

    def get_ui_rows(self):
        return [
            {'label': 'Damage', 'value': f"{self.damage:.0f}", 'color_hint': HINT_DAMAGE},
        ]

    def get_primary_value(self) -> float:
        return self.damage
```

Real examples using this pattern: `WeaponAbility`, `ResourceConsumption`, `CrewRequired`, `EmissiveArmor`.

## Step 2: Register the Ability

Add to `game/simulation/components/abilities/__init__.py`:

```python
# Import at the top with the other imports
from .movement import ThrusterAbility

# Add to ABILITY_REGISTRY dict
ABILITY_REGISTRY = {
    # ... existing entries ...
    'ThrusterAbility': ThrusterAbility,
}

# Add to __all__ list
__all__ = [
    # ... existing entries ...
    'ThrusterAbility',
]
```

The registry key is what you use in `components.json` ability data:
```json
"abilities": {
    "ThrusterAbility": 1500
}
```

## Step 3: Define STAT_BINDINGS

STAT_BINDINGS connect modifier stats to ability attributes:

```python
AbilityStatBinding(
    stat_key=StatKey.DAMAGE_MULT,    # StatKey enum from stat_keys.py
    attribute_name='damage',          # Ability attribute to modify
    operation='multiply',             # How to apply: 'multiply', 'add', 'set'
    base_attribute='_base_damage'     # Base value attribute (defaults to '_base_{attribute_name}')
)
```

### Available StatKeys

From `game/simulation/components/abilities/stat_keys.py`:

**Multiplicative (default 1.0):**

| StatKey | Typical Use |
|---------|-------------|
| `MASS_MULT` | Component mass |
| `HP_MULT` | Component HP |
| `DAMAGE_MULT` | Weapon damage |
| `RANGE_MULT` | Weapon range |
| `RELOAD_MULT` | Reload time |
| `COST_MULT` | Resource costs |
| `THRUST_MULT` | Engine thrust |
| `TURN_MULT` | Maneuver turn rate |
| `STRATEGIC_MULT` | Strategic movement points |
| `ENERGY_GEN_MULT` | Energy generation / shield regen |
| `CAPACITY_MULT` | Shield / storage capacity |
| `SHIELD_CAPACITY_MULT` | Shield-specific capacity |
| `CREW_CAPACITY_MULT` | Crew capacity |
| `LIFE_SUPPORT_CAPACITY_MULT` | Life support capacity |
| `CONSUMPTION_MULT` | Resource consumption |
| `ENDURANCE_MULT` | Seeker endurance |
| `PROJECTILE_HP_MULT` | Seeker projectile HP |
| `PROJECTILE_DAMAGE_MULT` | Seeker projectile damage |
| `CREW_REQ_MULT` | Crew requirements |

**Additive (default 0.0):**

| StatKey | Typical Use |
|---------|-------------|
| `MASS_ADD` | Flat mass addition |
| `ARC_ADD` | Add to firing arc |
| `ACCURACY_ADD` | Beam accuracy bonus |
| `PROJECTILE_STEALTH_LEVEL` | Seeker stealth level |

**Set/Override (default None):**

| StatKey | Typical Use |
|---------|-------------|
| `ARC_SET` | Override firing arc to fixed value |

### Operations

- `multiply`: `attribute = base_attr * stat_value`
- `add`: `attribute = base_attr + stat_value`
- `set`: `attribute = stat_value` (ignores base)

## Step 4: Implement recalculate()

For `SimpleMultiplierAbility` subclasses, `recalculate()` is inherited and works automatically. Override only if you need custom logic (like `ShieldProjection` which stacks two multipliers):

```python
def recalculate(self):
    """Apply both capacity_mult and shield_capacity_mult multiplicatively."""
    capacity_mult = self.get_effective_stat('capacity_mult', 1.0)
    shield_capacity_mult = self.get_effective_stat('shield_capacity_mult', 1.0)
    self.capacity = self.base_capacity * capacity_mult * shield_capacity_mult
```

For raw `Ability` subclasses, call `get_effective_stat()` directly:

```python
def recalculate(self):
    self.damage = self._base_damage * self.get_effective_stat('damage_mult', 1.0)
    self.range = self._base_range * self.get_effective_stat('range_mult', 1.0)
```

### Custom Stat Handling

For non-standard calculations (like sqrt scaling in `CrewRequired`):

```python
def recalculate(self):
    import math
    mass_mult = self.get_effective_stat('mass_mult', 1.0)
    if mass_mult < 0:
        mass_mult = 0
    crew_mult = math.sqrt(mass_mult)
    self.amount = int(math.ceil(self._base_amount * crew_mult * self.get_effective_stat('crew_req_mult', 1.0)))
```

## Step 5: Understand get_effective_stat()

`get_effective_stat()` is inherited from `Ability`. It resolves stats with this priority:

1. **Targeted ability stats:** `component.ability_stats[ClassName][stat_key]`
2. **Global component stats:** `component.stats[stat_key]`
3. **Default value:** Based on key naming convention:
   - `*_mult` stats -> `1.0`
   - `*_add` stats -> `0.0`
   - Other stats -> `None` (or explicit default)

```python
# Multiplicative stats default to 1.0 (no change)
damage_mult = self.get_effective_stat('damage_mult', 1.0)

# Additive stats default to 0.0 (no change)
arc_add = self.get_effective_stat('arc_add', 0.0)

# Override stats default to None (not applied)
arc_set = self.get_effective_stat('arc_set', None)
```

**Targeted vs Global Effects:**
- **Targeted:** `target_ability: "WeaponAbility"` only affects that ability class
- **Global:** No `target_ability` affects all abilities on the component

## Step 6: Implement UI Methods

### get_ui_rows()

Returns display data for component detail panel. `SimpleMultiplierAbility` provides this automatically. For raw `Ability` subclasses:

```python
def get_ui_rows(self):
    return [
        {'label': 'Damage', 'value': f"{self.damage:.0f}", 'color_hint': HINT_DAMAGE},
        {'label': 'Range', 'value': f"{self.range:.0f}", 'color_hint': HINT_RANGE},
    ]
```

Use color constants from `game/simulation/components/abilities/ui_colors.py`.

### get_primary_value()

Returns the main numeric value for aggregation. `SimpleMultiplierAbility` provides this automatically. For raw `Ability` subclasses:

```python
def get_primary_value(self) -> float:
    return self.damage
```

Marker abilities return `0.0` (the default).

## Step 7: Configure Layer and Scope (Optional)

Abilities can specify which game layer they apply to and what scope they affect:

```python
from .base import Ability, AbilityLayer, AbilityScope

class MyStrategicAbility(Ability):
    layer = AbilityLayer.STRATEGIC              # Only active on strategy map
    allowed_scopes = [AbilityScope.SELF, AbilityScope.ALLIED_SECTOR]
    default_scope = AbilityScope.SELF
```

**AbilityLayer values:** `COMBAT`, `STRATEGIC`, `BOTH`

**AbilityScope values:** `SELF`, `FLEET`, `SECTOR`, `ALLIED_SECTOR`, `PLAYER_SECTOR`, `ENEMY_SECTOR`, `SYSTEM`, `ALLIED_SYSTEM`, `PLAYER_SYSTEM`, `ENEMY_SYSTEM`, `PLANET`, `EMPIRE`, `ALLIED_EMPIRE`

Scope can also be set per-instance in component JSON:
```json
"abilities": {
    "StrategicMovement": {"value": 100, "scope": "allied_sector"}
}
```

## Step 8: Strategic Ability Registration (if applicable)

Strategic-layer abilities that appear in the game UI require additional registration beyond the ABILITY_REGISTRY. See [strategy_layer.md](../systems/strategy_layer.md) for the full checklist.

**If the ability is activatable** (has `energy_drain_rate`/`activation_time`):
1. Add to `TOGGLEABLE_ABILITIES` in `game/ui/screens/planet_abilities_window.py`
2. Add to `_ACTIVATABLE_ABILITIES` in `game/strategy/engine/planet_energy_engine.py`
3. Add to `_ACTIVATABLE_DISPLAY_NAMES` in `game/ui/screens/strategy_detail_fmt.py`

**If the ability affects system/sector scope:**
4. Add to `SYSTEM_EFFECT_ABILITIES` in `game/strategy/services/system_effects_collector.py`

**If the ability modifies combat stats:**
5. Add collection logic to `game/strategy/services/combat_modifier_collector.py` with `require_active=True`

**If the ability modifies planet properties** (like gravity, water, radiation):
6. Add an editor window (follow `gravity_target_editor.py` pattern with `species_selector_mixin`)
7. Add the editor's ability key to `_ENVIRONMENT_EDITORS` in `planet_abilities_window.py`
8. Add an `_open_*_editor()` method to `strategy_event_router.py`
9. Wire the editor in `strategy_window_manager.py:_open_planet_editor()`

## Working with Ship Layers

Ships organize components into layers.

### LayerType Reference

Defined in `game/core/constants.py`:

| LayerType | Value | Contents |
|-----------|-------|----------|
| `HULL` | 0 | Ship hull (innermost chassis layer) |
| `CORE` | 1 | Core systems (bridge, reactors, crew quarters) |
| `INNER` | 2 | Inner systems (engines, storage) |
| `OUTER` | 3 | Outer systems (shields, sensors, weapons) |
| `ARMOR` | 4 | Armor layer (outermost) |

```python
from game.core.constants import LayerType
```

### Ability Access Methods

| Method | Returns | Notes |
|--------|---------|-------|
| `comp.has_ability('Name')` | `bool` | Check if ability exists |
| `comp.get_ability('Name')` | `Ability` or `None` | Get first ability instance |
| `comp.get_abilities('Name')` | `List[Ability]` | Get all abilities of type |

Access supports polymorphism: `get_ability('WeaponAbility')` returns `ProjectileWeaponAbility`, `BeamWeaponAbility`, etc.

## Step 8: Write Tests

### Unit Test

```python
def test_thruster_ability_stat_bindings():
    """ThrusterAbility should have correct STAT_BINDINGS."""
    from game.simulation.components.abilities.movement import ThrusterAbility
    from game.simulation.components.abilities.stat_keys import StatKey

    assert ThrusterAbility.STAT_BINDINGS is not None

    thrust_binding = next(
        (b for b in ThrusterAbility.STAT_BINDINGS if b.stat_key == StatKey.THRUST_MULT),
        None
    )
    assert thrust_binding is not None
    assert thrust_binding.attribute_name == 'thrust_force'
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
            'ThrusterAbility': {'value': 1000}
        }
    }

    comp = Component(comp_data, registries=provider)
    thruster = comp.get_ability('ThrusterAbility')

    assert thruster.thrust_force == 1000

    # Apply modifier and recalculate
    comp.recalculate_stats()
    # Verify stats updated correctly
```

## Marker Abilities

For abilities that mark a component but have no numeric value, extend `Ability` directly with empty STAT_BINDINGS:

```python
class CommandAndControl(Ability):
    """Marks component as providing ship command capability."""

    STAT_BINDINGS: List[AbilityStatBinding] = []  # Marker ability

    def get_ui_rows(self):
        return [{'label': 'Command', 'value': 'Active', 'color_hint': HINT_CREW_CAP}]

    def get_primary_value(self) -> float:
        return 1.0
```

No `__init__` override needed -- the base `Ability.__init__` handles `component`, `data`, tags, and scope parsing.

## File Locations

| File | Purpose |
|------|---------|
| `game/simulation/components/abilities/base.py` | `Ability` and `SimpleMultiplierAbility` base classes |
| `game/simulation/components/abilities/__init__.py` | `ABILITY_REGISTRY` and `create_ability()` |
| `game/simulation/components/abilities/stat_keys.py` | `StatKey` enum, `AbilityStatBinding` dataclass |
| `game/simulation/components/abilities/ui_colors.py` | Color hint constants for UI |
| `game/simulation/components/abilities/weapons.py` | Weapon abilities |
| `game/simulation/components/abilities/defense.py` | Shield, armor, evasion abilities |
| `game/simulation/components/abilities/propulsion.py` | Propulsion abilities |
| `game/simulation/components/abilities/crew.py` | Crew and life support |
| `game/simulation/components/abilities/resources.py` | Resource consumption, storage, generation |
| `game/simulation/components/abilities/markers.py` | Marker abilities (CommandAndControl, etc.) |
| `game/simulation/components/abilities/superweapons.py` | Superweapon abilities |
| `game/simulation/components/abilities/colonize.py` | Colonization ability |
| `game/simulation/components/abilities/harvester.py` | Resource harvester, shipyard, empire storage |
| `game/simulation/components/abilities/cargo.py` | Cargo storage |
| `game/core/constants.py` | `LayerType` enum |
| `game/core/registry.py` | `RegistryManager`, `DefaultRegistryProvider`, `TestRegistryProvider` |

## Checklist

- [ ] Class created extending `SimpleMultiplierAbility` or `Ability`
- [ ] STAT_BINDINGS declared with correct StatKey values
- [ ] Registered in ABILITY_REGISTRY in `__init__.py`
- [ ] Added to `__all__` in `__init__.py`
- [ ] `recalculate()` uses `get_effective_stat()` (not needed for SimpleMultiplierAbility)
- [ ] `get_ui_rows()` returns display data with color hints
- [ ] `get_primary_value()` returns aggregation value
- [ ] Unit tests for STAT_BINDINGS
- [ ] Integration tests for modifier interaction
- [ ] All tests pass
- [ ] (If activatable) Added to `TOGGLEABLE_ABILITIES`, `_ACTIVATABLE_ABILITIES`, `_ACTIVATABLE_DISPLAY_NAMES`
- [ ] (If system/sector scope) Added to `SYSTEM_EFFECT_ABILITIES` in system_effects_collector
- [ ] (If combat-affecting) Added to combat_modifier_collector with `require_active=True`
- [ ] (If planet modifier) Editor window, `_ENVIRONMENT_EDITORS`, event router method

## Common Errors and Solutions

### Ability Not Found

**Symptom:** `None` returned when loading component from JSON.

**Cause:** Ability class not registered in ABILITY_REGISTRY.

**Solution:** Add to `game/simulation/components/abilities/__init__.py`:
```python
ABILITY_REGISTRY = {
    'MyAbility': MyAbility,
}
```

### Missing Base Attribute

**Symptom:** `AttributeError` for base attribute in `recalculate()`.

**Cause:** STAT_BINDINGS references a base attribute that was not set in `__init__()`.

**Solution:** Store base values when parsing component data:
```python
def __init__(self, component, data):
    super().__init__(component, data)
    self.damage = float(data.get('damage', 10))
    self._base_damage = self.damage  # Must match STAT_BINDINGS base_attribute
```

### SimpleMultiplierAbility Missing Class Attributes

**Symptom:** `TypeError` at class definition time: "MyAbility must set class attribute 'stat_key'"

**Cause:** `SimpleMultiplierAbility.__init_subclass__()` validates that required attributes are set.

**Solution:** Set all four required class attributes:
```python
class MyAbility(SimpleMultiplierAbility):
    stat_key = 'my_mult'       # Required
    value_attr = 'my_value'    # Required
    base_attr = 'base_my'      # Required
    ui_label = 'My Label'      # Required
```

### Invalid StatKey

**Symptom:** `KeyError` or `AttributeError` when applying modifiers.

**Cause:** Using string instead of StatKey enum, or using an undefined stat key.

**Solution:** Always use `StatKey` enum values:
```python
# Wrong
AbilityStatBinding('damage_mult', 'damage', ...)

# Correct
AbilityStatBinding(StatKey.DAMAGE_MULT, 'damage', ...)
```

### Stats Not Updating

**Symptom:** Modifier changes have no effect on ability values.

**Cause:** `recalculate()` is not calling `get_effective_stat()` for the correct stat key.

**Solution:** Verify that `recalculate()` reads from the same stat key declared in STAT_BINDINGS, and that the stat key string matches between the modifier definition and the StatKey enum value.
