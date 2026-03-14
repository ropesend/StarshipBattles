# Component System

This document provides an overview of the ship component system in Starship Battles.

## Overview

Ships are built from components - modular parts that provide capabilities like weapons, engines, shields, and special systems. The component system handles:

- Component definition (JSON data files)
- Runtime instantiation and attachment to ships
- Ability activation and stat calculation
- Damage tracking and status management
- Modifier application for customization

## Component Lifecycle

```
1. Definition    -> Component defined in data/components.json
2. Registration  -> Loaded into RegistryManager at startup
3. Instantiation -> Component() created from definition data
4. Attachment    -> Added to Ship via ship.add_component()
5. Initialization-> Abilities created, modifiers applied
6. Simulation    -> update() called each tick, abilities fire
7. Damage        -> take_damage() reduces HP, may disable
8. Destruction   -> HP reaches 0, component destroyed
```

### Key Lifecycle Methods

| Method | When Called | Purpose |
|--------|-------------|---------|
| `__init__()` | Instantiation | Parse data, create abilities |
| `recalculate_stats()` | After modifier change | Apply stat modifiers |
| `update()` | Each tick | Run ability updates, cooldowns |
| `take_damage()` | On hit | Apply damage, check disable threshold |
| `on_activation()` | Ability trigger | Execute special ability (e.g. fire weapon) |

## Ability System

Abilities are the functional capabilities of components. A weapon component has WeaponAbility, an engine has CombatPropulsion, etc.

### Ability Hierarchy

```
Ability (base)
+-- SimpleMultiplierAbility (standard pattern for single-value abilities)
|   +-- CombatPropulsion
|   +-- ManeuveringThruster
|   +-- StrategicMovement
|   +-- ShieldProjection
|   +-- ShieldRegeneration
|   +-- CrewCapacity
|   +-- LifeSupportCapacity
+-- WeaponAbility
|   +-- ProjectileWeaponAbility
|   +-- BeamWeaponAbility
|   +-- SeekerWeaponAbility
+-- ResourceConsumption
+-- ResourceStorage
+-- ResourceGeneration
+-- ToHitAttackModifier
+-- ToHitDefenseModifier
+-- EmissiveArmor
+-- CrewRequired
+-- WarpJump
+-- VehicleLaunchAbility
+-- CommandAndControl (marker)
+-- RequiresCommandAndControl (marker)
+-- RequiresCombatMovement (marker)
+-- StructuralIntegrity (marker)
+-- ColonizePlanet
+-- Superweapons (DestroyPlanet, DestroyStar, OpenWarpPoint, etc.)
```

### Key Ability Classes

| Class | Location | Purpose |
|-------|----------|---------|
| `Ability` | `abilities/base.py` | Base class with scope, layer, stat bindings |
| `SimpleMultiplierAbility` | `abilities/base.py` | Standard pattern for single-value abilities |
| `WeaponAbility` | `abilities/weapons.py` | Damage, range, reload, firing arc |
| `ShieldProjection` | `abilities/defense.py` | Shield capacity |
| `ShieldRegeneration` | `abilities/defense.py` | Shield regen rate |
| `CombatPropulsion` | `abilities/propulsion.py` | Thrust force |
| `ResourceConsumption` | `abilities/resources.py` | Fuel, ammo, energy consumption |

### Ability Stat Bindings

Abilities declare which stats they consume via `STAT_BINDINGS`:

```python
STAT_BINDINGS: List[AbilityStatBinding] = [
    AbilityStatBinding(StatKey.DAMAGE_MULT, 'damage', 'multiply', '_base_damage'),
    AbilityStatBinding(StatKey.RANGE_MULT, 'range', 'multiply', '_base_range'),
]
```

This allows modifiers to affect ability stats using operations like `multiply`, `add`, or `set`.

### SimpleMultiplierAbility Pattern

Most abilities that track a single numeric value should extend `SimpleMultiplierAbility`. It eliminates boilerplate by configuring behavior via class attributes:

```python
class CombatPropulsion(SimpleMultiplierAbility):
    stat_key = 'thrust_mult'       # Modifier stat key
    value_attr = 'thrust_force'    # Current-value attribute name
    base_attr = 'base_thrust'      # Base-value attribute name
    ui_label = 'Thrust'            # Display label
    ui_format = '{:.0f} N'         # Value format string
    ui_color = HINT_THRUST          # Color hint constant

    STAT_BINDINGS: List[AbilityStatBinding] = [
        AbilityStatBinding(StatKey.THRUST_MULT, 'thrust_force', 'multiply', 'base_thrust'),
    ]
```

`SimpleMultiplierAbility` automatically handles `__init__`, `recalculate`, `get_ui_rows`, and `get_primary_value`.

## Modifier System

Modifiers customize component stats. They are applied in the Workshop during ship design.

### Modifier Operations

| Operation | Effect | Example |
|-----------|--------|---------|
| `add` | Adds value to base | Range +500 |
| `multiply` | Multiplies base | Damage x1.5 |
| `set` | Overrides value | Firing Arc = 360 |

### Common Modifiers

| Modifier | Target | Effect |
|----------|--------|--------|
| `simple_size_mount` | All | Scales mass and stats |
| `range_mount` | Weapons | Adjusts weapon range |
| `turret_mount` | Weapons | Expands firing arc |
| `hardened_mount` | Most | Trades mass for HP |
| `efficiency_mount` | Resource users | Trades efficiency for mass |

### Modifier Flow

```
1. User adjusts slider in Workshop UI
2. Component.set_modifier_value() called
3. Modifier value stored in component.modifiers dict
4. Component.recalculate_stats() triggered
5. Ability.recalculate() applies stat bindings
6. Final stat values updated
```

For detailed modifier documentation, see [modifier_system.md](modifier_system.md).

## Key Classes Reference

| Class | File | Responsibility |
|-------|------|----------------|
| `Component` | `game/simulation/components/component.py` | Component instance, ability host |
| `RegistryManager` | `game/core/registry.py` | Singleton managing all game data registries |
| `DefaultRegistryProvider` | `game/core/registry.py` | DI provider backed by RegistryManager |
| `TestRegistryProvider` | `game/core/registry.py` | Isolated registry for tests |
| `Ability` | `game/simulation/components/abilities/base.py` | Base ability class |
| `SimpleMultiplierAbility` | `game/simulation/components/abilities/base.py` | Standard single-value ability base |
| `AbilityManager` | `game/simulation/components/ability_manager.py` | Creates abilities from data |
| `ModifierManager` | `game/simulation/components/modifier_manager.py` | Applies modifier effects |
| `ModifierService` | `game/simulation/services/modifier_service.py` | Modifier validation logic |
| `ComponentStatsCalculator` | `game/simulation/components/component_stats_calculator.py` | Stat aggregation |

## Usage Examples

### Creating a Component

```python
from game.core.registry import get_default_registry_provider

provider = get_default_registry_provider()
comp_data = provider.get_components().get('laser_mk1')
component = Component(comp_data, registries=provider)
```

### Querying Abilities

```python
# Check if component has weapon ability
if component.has_ability('WeaponAbility'):
    weapon = component.get_ability('WeaponAbility')
    damage = weapon.get_damage(range_to_target=1000)

# Get all abilities of a type
weapons = component.get_abilities('WeaponAbility')
```

### Applying Damage

```python
# Component takes damage
component.take_damage(50)

if not component.is_active:
    print("Component disabled!")

if component.current_hp <= 0:
    print("Component destroyed!")
```

## Ship Layers

Ships organize components into layers. The `LayerType` enum is defined in `game/core/constants.py`.

### LayerType Reference

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

## Component Data Format (components.json)

Components are defined in `data/components.json`. Each entry has:

```json
{
    "id": "railgun",
    "name": "Railgun",
    "type": "ProjectileWeaponAbility",
    "mass": 100,
    "hp": 150,
    "allowed_vehicle_types": ["Ship", "Satellite", "Planetary Complex"],
    "abilities": {
        "CrewRequired": 5,
        "ResourceConsumption": [
            {"resource": "ammo", "amount": 1, "trigger": "activation"}
        ],
        "ProjectileWeaponAbility": {
            "damage": "=40 - (0.01 * range_to_target)",
            "range": 2400,
            "reload": 2.0,
            "projectile_speed": 20000,
            "firing_arc": 1
        }
    }
}
```

Ability data supports three formats:
- **Dict:** `{"damage": 100, "range": 5000}` - full parameter specification
- **Primitive:** `5` or `true` - shorthand for single-value abilities
- **Formula:** `"=50 * sqrt(ship_class_mass / 1000)"` - runtime evaluated expression

## Related Documentation

- [adding_abilities.md](adding_abilities.md) - How to create new abilities
- [adding_modifiers.md](adding_modifiers.md) - How to create new modifiers
- [modifier_system.md](modifier_system.md) - Detailed modifier documentation
- [01_ARCHITECTURE.md](../01_ARCHITECTURE.md) - Overall system architecture
