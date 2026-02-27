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
1. Definition    → Component defined in components.json
2. Registration  → Loaded into ComponentRegistry at startup
3. Instantiation → Component() created from definition data
4. Attachment    → Added to Ship via ship.add_component()
5. Initialization→ Abilities created, modifiers applied
6. Simulation    → update() called each tick, abilities fire
7. Damage        → take_damage() reduces HP, may disable
8. Destruction   → HP reaches 0, component destroyed
```

### Key Lifecycle Methods

| Method | When Called | Purpose |
|--------|-------------|---------|
| `__init__()` | Instantiation | Parse data, create abilities |
| `recalculate()` | After modifier change | Apply stat modifiers |
| `update()` | Each tick | Run ability updates, cooldowns |
| `take_damage()` | On hit | Apply damage, check disable threshold |
| `activate()` | Ability trigger | Execute special ability |

## Ability System

Abilities are the functional capabilities of components. A weapon component has WeaponAbility, an engine has CombatPropulsion, etc.

### Ability Hierarchy

```
Ability (base)
├── WeaponAbility
│   ├── ProjectileWeaponAbility
│   ├── BeamWeaponAbility
│   └── SeekerWeaponAbility
├── DefenseAbility
│   ├── ShieldAbility
│   └── ArmorAbility
├── PropulsionAbility
│   └── CombatPropulsion
├── SensorAbility
└── SpecialAbility
    ├── RepairAbility
    └── StealthAbility
```

### Key Ability Classes

| Class | Location | Purpose |
|-------|----------|---------|
| `Ability` | `game/simulation/components/abilities/base.py` | Base class with stat binding |
| `WeaponAbility` | `game/simulation/components/abilities/weapons.py` | Damage, range, reload, firing arc |
| `ShieldAbility` | `game/simulation/components/abilities/defense.py` | Shield HP, regen rate |
| `CombatPropulsion` | `game/simulation/components/abilities/propulsion.py` | Thrust, turn rate |

### Ability Stat Bindings

Abilities declare which stats they expose via `STAT_BINDINGS`:

```python
STAT_BINDINGS = [
    AbilityStatBinding(StatKey.DAMAGE_MULT, 'damage', 'multiply', '_base_damage'),
    AbilityStatBinding(StatKey.RANGE_MULT, 'range', 'multiply', '_base_range'),
]
```

This allows modifiers to affect ability stats using operations like `multiply`, `add`, or `set`.

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
4. Component.recalculate() triggered
5. Ability.recalculate() applies stat bindings
6. Final stat values updated
```

For detailed modifier documentation, see [modifier_system.md](modifier_system.md).

## Key Classes Reference

| Class | File | Responsibility |
|-------|------|----------------|
| `Component` | `game/simulation/components/component.py` | Component instance, ability host |
| `ComponentRegistry` | `game/core/registries.py` | Stores component definitions |
| `Ability` | `game/simulation/components/abilities/base.py` | Base ability class |
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
component = Component(comp_data)
```

### Adding to Ship

```python
ship.add_component(component, layer_name='weapons')
component.recalculate()  # Apply modifiers
```

### Querying Abilities

```python
# Check if component has weapon ability
if component.has_ability('WeaponAbility'):
    weapon = component.get_ability('WeaponAbility')
    damage = weapon.get_damage(range_to_target=1000)

# Get total thrust from all engines
total_thrust = ship.get_total_ability_value('CombatPropulsion')
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

## Related Documentation

- [adding_abilities.md](adding_abilities.md) - How to create new abilities
- [adding_modifiers.md](adding_modifiers.md) - How to create new modifiers
- [modifier_system.md](modifier_system.md) - Detailed modifier documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) - Overall system architecture
