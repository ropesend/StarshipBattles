# Combat Lab Data Files

## Overview

This directory contains all data files used by Combat Lab tests:

- `components.json` - Component definitions (weapons, armor, engines, etc.)
- `modifiers.json` - Stat modifiers
- `vehicleclasses.json` - Ship hull types
- `ships/` - Ship configurations for test scenarios

## components.json

Defines all components that can be installed on ships.

### Structure

```json
{
    "components": [
        {
            "id": "component_id",
            "name": "Display Name",
            "type": "ComponentType",
            "mass": 10,
            "hp": 50,
            "sprite_index": 0,
            "abilities": {
                "AbilityName": {
                    "ability_param": value
                }
            }
        }
    ]
}
```

### Test Components

#### Beam Weapons

| Component ID | Base Accuracy | Falloff | Range | Damage | Purpose |
|--------------|---------------|---------|-------|--------|---------|
| `test_beam_low_acc_1dmg` | 0.5 (~53% at point blank) | 0.002/px | 800 | 1 | Low accuracy tests |
| `test_beam_med_acc_1dmg` | 2.0 (~88% at point blank) | 0.001/px | 800 | 1 | Medium accuracy tests |
| `test_beam_high_acc_1dmg` | 5.0 (~99% at point blank) | 0.0005/px | 800 | 1 | High accuracy tests |

**Beam Weapon Abilities**:
```json
"abilities": {
    "BeamWeaponAbility": {
        "damage": 1,
        "range": 800,
        "reload": 0.0,
        "base_accuracy": 0.5,
        "accuracy_falloff": 0.002
    }
}
```

**Parameters**:
- `damage` - Damage per hit (integer)
- `range` - Maximum range in pixels
- `reload` - Time between shots in seconds (0.0 = every tick)
- `base_accuracy` - Sigmoid input score (not a probability; fed through `1/(1+e^-x)` to get hit chance)
- `accuracy_falloff` - Score reduction per pixel of surface distance

#### Armor Components

| Component ID | HP | Mass | Purpose |
|--------------|-----|------|---------|
| `test_armor_std` | 200 | 0 | Standard armor |
| `test_armor_extreme_hp` | 1,000,000,000 | 0 | Indestructible for long tests |
| `test_armor_small_extreme_hp` | 1,000,000,000 | 0 | Indestructible (same as extreme_hp) |

**Why 1 Billion HP?**
- Prevents target death during tests
- Even high-accuracy beams at 100k ticks: 99% × 100k = 99k damage (0.01% of 1B)
- Ensures tests run to completion

**Zero-Mass Architecture**:
- All non-hull components have mass = 0
- Ship mass comes ONLY from hull components
- This ensures regular and high-tick tests have identical expected hit rates

#### Engines & Thrusters

| Component ID | Value | Mass | Purpose |
|--------------|-------|------|---------|
| `test_engine_no_fuel` | 500 thrust | 0 | Basic engine (no fuel consumption) |
| `test_engine_slow` | 50 thrust | 0 | Slow engine for linear slow target |
| `test_thruster_std` | 5.0 raw turn | 0 | Standard maneuvering thruster (propulsion tests) |
| `test_thruster_high` | 500.0 raw turn | 0 | High agility thruster (erratic targets, 100x std) |

All propulsion components have mass = 0. Ship mass comes from hull only.

**Turn Speed Units**: `turn_speed` in expected_stats is in degrees per 100 ticks.
`rotate()` divides by 100, so effective rotation = `turn_speed / 100` deg/tick.
A ship with `turn_speed=1562.5` rotates at 15.6 deg/tick.

**Erratic Target Thruster Sizing**: The thruster must be powerful enough that
the leash overshoot (max_speed * ticks_for_180_turn) is well under the leash
radius. For the small ship (400kg, 31.25 px/tick), `test_thruster_high` gives
overshoot ~360px. For the large ship (4000kg, 3.125 px/tick), 4x thrusters are
needed for overshoot ~285px. Both fit within the 1000px leash.

#### Projectile Weapons

| Component ID | Damage | Speed | Range | Reload | Purpose |
|--------------|--------|-------|-------|--------|---------|
| `test_weapon_proj_omni` | 1 | 20000 (200 px/tick) | 1000 | 0.0 | Accuracy & damage tests |
| `test_proj_rapid` | 1 | 5000 (50 px/tick) | 1000 | 0.0 | Resource consumption tests |

**Projectile Weapon Design**:
- **Damage = 1**: `damage_dealt == number_of_hits` for simple counting
- **Reload = 0.0**: Fires every tick for high sample counts
- **Speed = 20000**: 200 px/tick after PROJECTILE_SPEED_SCALE(100), ~5x faster than the fastest test target

**Speed Units**: `projectile_speed` is divided by `PROJECTILE_SPEED_SCALE` (100) to
convert to px/tick. Ship speed uses `(thrust * K_SPEED) / mass` directly in px/tick.
A projectile at 20000 = 200 px/tick, a fast ship at max_speed 37.5 = 37.5 px/tick.

### Adding New Test Components

1. **Identify Required Stats** (use game data as reference for realistic values):
   ```
   Need: Projectile weapon, 1 damage, 20000 speed, 0.0 reload
   ```

2. **Create Component Entry** (mass=0 for test components):
   ```json
   {
       "id": "test_projectile_std",
       "name": "Test Projectile (Standard)",
       "type": "ProjectileWeaponAbility",
       "mass": 0,
       "hp": 50,
       "sprite_index": 85,
       "abilities": {
           "ProjectileWeaponAbility": {
               "damage": 1,
               "projectile_speed": 20000,
               "range": 1000,
               "reload": 0.0,
               "firing_arc": 360
           }
       }
   }
   ```

3. **Validate in test** using `check_exact`:
   ```python
   weapon = self.get_ability(self.attacker, 'ProjectileWeaponAbility')
   checks.append(check_exact("Weapon Damage", 1, weapon.damage))
   checks.append(check_exact("Weapon Range", 1000, weapon.range))
   ```

## Ship Files (ships/ directory)

Define complete ship configurations for test scenarios.

### File Naming Convention

```
Test_[Role]_[Variant].json

Examples:
Test_Attacker_Beam360_Low.json     # Attacker with low accuracy beam
Test_Target_Stationary.json        # Stationary target
Test_Target_Stationary_HighTick.json  # High-tick variant
Test_Target_Erratic_Small.json     # Small maneuverable target
```

### Ship Structure

```json
{
    "name": "Test Target Stationary",
    "color": [0, 0, 255],
    "team_id": 2,
    "ship_class": "TestM_2L",
    "theme_id": "Federation",
    "ai_strategy": "test_do_nothing",
    "layers": {
        "CORE": [
            {"id": "test_armor_extreme_hp"}
        ],
        "ARMOR": [],
        "HULL": []
    },
    "_test_notes": "Comments explaining purpose",
    "expected_stats": {
        "max_hp": 1000000500,
        "mass": 400.0,
        "armor_hp_pool": 1000000000
    },
    "resources": {
        "fuel": 0.0,
        "energy": 0.0,
        "ammo": 0.0
    }
}
```

### Ship Fields

#### Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `name` | string | Ship display name | `"Test Target Stationary"` |
| `color` | [r,g,b] | Ship color (0-255) | `[0, 0, 255]` |
| `team_id` | int | Team number (1 or 2) | `2` |
| `ship_class` | string | Hull type ID | `"TestM_2L"` |
| `theme_id` | string | Visual theme | `"Federation"` |
| `ai_strategy` | string | AI behavior | `"test_do_nothing"` |
| `layers` | object | Component layers | See below |

#### layers Object

```json
"layers": {
    "CORE": [
        {"id": "component_id_1"},
        {"id": "component_id_2"}
    ],
    "ARMOR": [
        {"id": "armor_component_id"}
    ],
    "HULL": [
        {"id": "hull_component_id"}
    ]
}
```

Components are installed in layers:
- **CORE**: Essential components (weapons, armor, engines)
- **ARMOR**: Additional armor plating
- **HULL**: Hull reinforcements

#### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `_test_notes` | string | Internal comments (not used by game) |
| `expected_stats` | object | Expected ship stats for validation |
| `resources` | object | Starting fuel/energy/ammo |

#### expected_stats

Used to validate ship loaded correctly:

```json
"expected_stats": {
    "max_hp": 1000000500,
    "mass": 400.0,
    "armor_hp_pool": 1000000000,
    "max_speed": 192.30769230769232,
    "total_thrust": 500.0
}
```

If actual stats don't match after loading, warning is printed.

### Test Ship Configurations

#### Attackers (Team 1)

| Ship File | Mass | Weapon | Purpose |
|-----------|------|--------|---------|
| `Test_Attacker_Beam360_Low.json` | 400 | Low accuracy beam | Low accuracy tests |
| `Test_Attacker_Beam360_Med.json` | 400 | Medium accuracy beam | Medium accuracy tests |
| `Test_Attacker_Beam360_High.json` | 400 | High accuracy beam | High accuracy tests |

**Example**:
```json
{
    "name": "Test Attacker Beam360 Low",
    "color": [255, 0, 0],
    "team_id": 1,
    "ship_class": "TestS_2L",
    "ai_strategy": "test_do_nothing",
    "layers": {
        "CORE": [
            {"id": "test_beam_low_acc_1dmg"}
        ]
    },
    "expected_stats": {
        "mass": 400.0
    }
}
```

#### Targets (Team 2)

| Ship File | Mass | HP | Behavior | Purpose |
|-----------|------|-----|----------|---------|
| `Test_Target_Stationary.json` | 400 | 1B | Stationary | Standard tests |
| `Test_Target_Stationary_HighTick.json` | 400 | 1B | Stationary | High-tick tests (same mass as standard) |
| `Test_Target_Erratic_Small.json` | 400 | 1B | Erratic maneuvers | Moving target tests |

**Standard Target** (mass 400):
```json
{
    "name": "Test Target Stationary",
    "team_id": 2,
    "ship_class": "TestS_2L",  // hull_test_s = mass 400
    "ai_strategy": "test_do_nothing",
    "layers": {
        "CORE": [
            {"id": "test_armor_extreme_hp"}  // 1B HP, mass 0
        ]
    },
    "expected_stats": {
        "max_hp": 1000000100,
        "mass": 400.0  // hull_test_s only (armor has 0 mass)
    }
}
```

**High-Tick Target** (mass 400 - now identical to standard):
```json
{
    "name": "Test Target Stationary (High-Tick)",
    "ship_class": "TestS_2L",  // hull_test_s = mass 400
    "layers": {
        "CORE": [
            {"id": "test_armor_extreme_hp"}  // 1B HP, mass 0
        ]
    },
    "expected_stats": {
        "mass": 400.0  // hull_test_s only (identical to standard)
    }
}
```

**Erratic Small Target** (mass 400):
```json
{
    "name": "Test Target Erratic Small",
    "ship_class": "TestS_2L",  // hull_test_s = mass 400
    "ai_strategy": "test_erratic_maneuver",
    "layers": {
        "CORE": [
            {"id": "test_armor_small_extreme_hp"},  // 1B HP, mass 0
            {"id": "test_engine_no_fuel"},          // mass 0
            {"id": "test_thruster_std"}             // mass 0
        ]
    },
    "expected_stats": {
        "mass": 400.0,  // hull_test_s only
        "total_thrust": 500.0
    }
}
```

### AI Strategies

| Strategy | Behavior | Used For |
|----------|----------|----------|
| `test_do_nothing` | No movement, no actions | Stationary targets, attackers |
| `test_erratic_maneuver` | Random acceleration/turning | Moving target tests |

### Ship Classes (Hull Types)

From `vehicleclasses.json`:

| Class ID | Size | Base Mass | Layers | Purpose |
|----------|------|-----------|--------|---------|
| `TestS_2L` | Small | 400 (hull_test_s) | 2 (CORE, ARMOR) | Small ships |
| `TestM_2L` | Medium | 1000 (hull_test_m) | 2 (CORE, ARMOR) | Medium ships |

Hull mass comes from the default hull component, not a base_mass field. All non-hull test components have mass 0.

### Creating New Test Ships

**Example: Create attacker with projectile weapon**

1. **Identify Requirements**:
   ```
   Need: Attacker with projectile weapon
   Team: 1 (attackers)
   Behavior: Stationary
   ```

2. **Choose Components**:
   ```
   Weapon: test_projectile_std (mass 0, zero-mass architecture)
   Hull class: TestS_2L (hull_test_s = 400 tons)
   Total: 0 + 400 = 400 mass
   ```

3. **Create JSON File** (`Test_Attacker_Projectile.json`):
   ```json
   {
       "name": "Test Attacker Projectile",
       "color": [255, 0, 0],
       "team_id": 1,
       "ship_class": "TestS_2L",
       "theme_id": "Federation",
       "ai_strategy": "test_do_nothing",
       "layers": {
           "CORE": [
               {"id": "test_projectile_std"}
           ],
           "ARMOR": [],
           "HULL": []
       },
       "_test_notes": "Attacker with standard projectile weapon for PROJ tests",
       "expected_stats": {
           "max_hp": 120,
           "mass": 400.0
       },
       "resources": {
           "fuel": 0.0,
           "energy": 0.0,
           "ammo": 0.0
       }
   }
   ```

4. **Calculate Expected Stats**:
   ```python
   # Hull: hull_test_s (default for TestS_2L)
   hull_mass = 400
   hull_hp = 100

   # Component: test_projectile_std (zero-mass architecture)
   component_hp = 20
   component_mass = 0

   # Total
   max_hp = hull_hp + component_hp = 120
   mass = hull_mass + component_mass = 400.0
   ```

5. **Use in Test**:
   ```python
   def setup(self, engine):
       attacker_data = load_ship_json('Test_Attacker_Projectile.json')
       self.attacker = Ship.from_dict(attacker_data, team_id=1)
   ```

## Target Mass and Radius

### Radius Formula

```python
radius = 40 × (mass / 1000) ^ (1/3)
```

### Standard Hull Masses

| Hull ID | Mass | Radius | Use Case |
|---------|------|--------|----------|
| `hull_test_xs` | 100 | 18.57px | Minimum mass (matches physics safeguard) |
| `hull_test_s` | 400 | 29.47px | Standard small target |
| `hull_test_m` | 1000 | 40.00px | Reference mass target |
| `hull_test_l` | 4000 | 63.50px | Large target |

**Note**: All non-hull components have mass = 0, so ship mass equals hull mass.

### Surface Distance Calculation

For tests, ALWAYS use surface distance:

```python
# Ships positioned at:
attacker.position = (100, 100)
target.position = (150, 100)

# Center-to-center distance
center_distance = 50px

# Target radius (mass 400)
target_radius = 40 × (400/1000)^(1/3) = 29.47px

# Surface distance (ACTUAL firing distance)
surface_distance = 50 - 29.47 = 20.53px  # USE THIS FOR CALCULATIONS!
```

**Critical**: Beam weapon accuracy calculations use surface distance, not center distance.

## modifiers.json

Defines stat modifiers applied by abilities or effects.

**Structure**:
```json
{
    "modifiers": [
        {
            "id": "modifier_id",
            "stat": "stat_name",
            "value": 10,
            "type": "add"
        }
    ]
}
```

**Types**:
- `add` - Add to base value
- `multiply` - Multiply base value

**Not heavily used in current tests**, but loaded for completeness.

## vehicleclasses.json

Defines ship hull types.

**Structure**:
```json
{
    "classes": [
        {
            "id": "TestS_2L",
            "name": "Test Small (2 Layers)",
            "base_mass": 10,
            "base_hp": 0,
            "sprite_sheet": "test_ships",
            "layers": ["CORE", "ARMOR"]
        }
    ]
}
```

**Test Hull Classes**:

| ID | Name | Base Mass | Layers | Purpose |
|----|------|-----------|--------|---------|
| `TestS_2L` | Test Small | 10 | CORE, ARMOR | Small ships (attackers, small targets) |
| `TestM_2L` | Test Medium | 200 | CORE, ARMOR | Medium ships (standard targets) |

**Base Mass**: Added to component masses to get total ship mass.

## Data Loading Sequence

When a test runs:

1. **TestRunner.load_data_for_scenario()**:
   ```python
   registry.clear()                           # Clear old data
   registry.load_modifiers('modifiers.json')
   registry.load_components('components.json')
   registry.load_vehicle_classes('vehicleclasses.json')
   ```

2. **scenario.setup()**:
   ```python
   # Ships reference components from registry
   attacker = Ship.from_dict(attacker_json, team_id=1)
   # Internally: registry.get_component('test_beam_low_acc_1dmg')
   ```

3. **Ship Construction**:
   ```python
   # For each component ID in ship layers:
   component = registry.get_component(component_id)
   ship.add_component(component)

   # Calculate ship stats
   ship.mass = hull_base_mass + sum(component.mass for component in ship.components)
   ship.hp = sum(component.hp for component in ship.components)
   ```

## Best Practices

### 1. Always Use Extreme HP Armor

```json
// GOOD - Target survives 100k ticks
"layers": {
    "CORE": [
        {"id": "test_armor_extreme_hp"}  // 1 billion HP
    ]
}

// BAD - Target may die during test
"layers": {
    "CORE": [
        {"id": "test_armor_std"}  // 200 HP - dies quickly
    ]
}
```

### 2. Ship Mass = Hull Mass Only

```json
// Target should be mass 400
// Use hull_test_s (mass 400) via ship class TestS_2L
"ship_class": "TestS_2L",  // hull_test_s = mass 400
"layers": {
    "CORE": [
        {"id": "test_armor_extreme_hp"}  // mass 0 (all components are 0 mass)
    ]
}
// Total: 400 (hull only) ✓
```

**Zero-Mass Architecture**: All non-hull components have mass = 0. Choose the hull that gives you the desired ship mass.

### 3. Document Expected Stats

```json
"expected_stats": {
    "max_hp": 1000000500,    // For validation
    "mass": 400.0,           // Critical for radius calculation
    "armor_hp_pool": 1000000000
}
```

### 4. Use Descriptive Names

```json
"name": "Test Target Stationary",  // GOOD - Clear purpose
"name": "Target 1",                // BAD - Unclear
```

### 5. Add Test Notes

```json
"_test_notes": "Stationary target with extreme HP (1B) for beam weapon testing. Mass 400 for standard tests."
```

## See Also

- `../COMBAT_LAB_DOCUMENTATION.md` - Complete system documentation
- `../scenarios/beam_scenarios.py` - Example ship usage
- `ships/` - Actual ship JSON files
