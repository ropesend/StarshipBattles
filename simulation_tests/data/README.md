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
| `test_beam_low_acc_1dmg` | 50% | 0.2%/px | 800 | 1 | Low accuracy tests |
| `test_beam_med_acc_1dmg` | 80% | 0.1%/px | 800 | 1 | Medium accuracy tests |
| `test_beam_high_acc_1dmg` | 99% | 0.01%/px | 800 | 1 | High accuracy tests |

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
- `base_accuracy` - Base hit chance (0.0-1.0)
- `accuracy_falloff` - Accuracy reduction per pixel distance

#### Armor Components

| Component ID | HP | Mass | Purpose |
|--------------|-----|------|---------|
| `test_armor_std` | 200 | 20 | Standard armor |
| `test_armor_ultra_high_hp` | 10,000 | 200 | Old high-HP armor |
| `test_armor_extreme_hp` | 1,000,000,000 | 200 | Indestructible (mass 400 ships) |
| `test_armor_extreme_hp_heavy` | 1,000,000,000 | 400 | Indestructible (mass 600 ships) |
| `test_armor_small_extreme_hp` | 1,000,000,000 | 20 | Indestructible (mass 65 ships) |

**Why 1 Billion HP?**
- Prevents target death during tests
- Even high-accuracy beams at 100k ticks: 99% × 100k = 99k damage (0.01% of 1B)
- Ensures tests run to completion

**Mass Variants**:
- Different masses maintain target ship total mass
- Example: Target needs mass=400
  - Core: 200 mass (fixed)
  - Armor: 200 mass (test_armor_extreme_hp)
  - Total: 400 mass ✓

#### Engines & Thrusters

| Component ID | Thrust | Mass | Purpose |
|--------------|--------|------|---------|
| `test_engine_no_fuel` | 0 | 10 | Stationary ships |
| `test_thruster_std` | 500 | 25 | Moving targets |

Used for erratic target tests (mass 65 ships).

### Adding New Test Components

1. **Identify Required Stats**:
   ```
   Need: Projectile weapon, 10 damage, 300 speed, 1.0s reload
   ```

2. **Create Component Entry**:
   ```json
   {
       "id": "test_projectile_std",
       "name": "Test Projectile (Standard)",
       "type": "ProjectileWeaponAbility",
       "mass": 5,
       "hp": 20,
       "sprite_index": 87,
       "abilities": {
           "ProjectileWeaponAbility": {
               "damage": 10,
               "projectile_speed": 300,
               "range": 800,
               "reload": 1.0
           }
       }
   }
   ```

3. **Add ExactMatchRules** in test:
   ```python
   ExactMatchRule(name='Projectile Damage', path='attacker.weapon.damage', expected=10),
   ExactMatchRule(name='Projectile Speed', path='attacker.weapon.projectile_speed', expected=300),
   # etc.
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
| `Test_Attacker_Beam360_Low.json` | 25 | Low accuracy beam | Low accuracy tests |
| `Test_Attacker_Beam360_Med.json` | 25 | Medium accuracy beam | Medium accuracy tests |
| `Test_Attacker_Beam360_High.json` | 25 | High accuracy beam | High accuracy tests |

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
        "mass": 25.0
    }
}
```

#### Targets (Team 2)

| Ship File | Mass | HP | Behavior | Purpose |
|-----------|------|-----|----------|---------|
| `Test_Target_Stationary.json` | 400 | 1B | Stationary | Standard tests |
| `Test_Target_Stationary_HighTick.json` | 600 | 1B | Stationary | High-tick tests |
| `Test_Target_Erratic_Small.json` | 65 | 1B | Erratic maneuvers | Moving target tests |

**Standard Target** (mass 400):
```json
{
    "name": "Test Target Stationary",
    "team_id": 2,
    "ship_class": "TestM_2L",
    "ai_strategy": "test_do_nothing",
    "layers": {
        "CORE": [
            {"id": "test_armor_extreme_hp"}  # 1B HP, mass 200
        ]
    },
    "expected_stats": {
        "max_hp": 1000000500,
        "mass": 400.0  # 200 (armor) + 200 (core hull)
    }
}
```

**High-Tick Target** (mass 600):
```json
{
    "name": "Test Target Stationary (High-Tick)",
    "layers": {
        "CORE": [
            {"id": "test_armor_extreme_hp_heavy"}  # 1B HP, mass 400
        ]
    },
    "expected_stats": {
        "mass": 600.0  # 400 (armor) + 200 (core hull)
    }
}
```

**Erratic Small Target** (mass 65):
```json
{
    "name": "Test Target Erratic Small",
    "ship_class": "TestS_2L",
    "ai_strategy": "test_erratic_maneuver",
    "layers": {
        "CORE": [
            {"id": "test_armor_small_extreme_hp"},  # 1B HP, mass 20
            {"id": "test_engine_no_fuel"},
            {"id": "test_thruster_std"}
        ]
    },
    "expected_stats": {
        "mass": 65.0,  # 20 + 10 + 25 + 10 (hull)
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
| `TestS_2L` | Small | 10 | 2 (CORE only) | Small ships (mass <100) |
| `TestM_2L` | Medium | 200 | 2 (CORE only) | Medium ships (mass 200-600) |

Base mass is added to component masses to get total ship mass.

### Creating New Test Ships

**Example: Create attacker with projectile weapon**

1. **Identify Requirements**:
   ```
   Need: Attacker with projectile weapon, mass ~25
   Team: 1 (attackers)
   Behavior: Stationary
   ```

2. **Choose Components**:
   ```
   Weapon: test_projectile_std (mass 5)
   Hull class: TestS_2L (base mass 10)
   Total: 5 + 10 = 15 mass (close enough to 25)
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
           "max_hp": 20,
           "mass": 15.0
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
   # Component: test_projectile_std
   component_hp = 20
   component_mass = 5

   # Hull: TestS_2L
   hull_mass = 10
   hull_hp = 0  # Assume hull adds no HP (check vehicleclasses.json)

   # Total
   max_hp = component_hp + hull_hp = 20
   mass = component_mass + hull_mass = 15.0
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

### Common Target Radii

| Mass | Radius | Use Case |
|------|--------|----------|
| 65 | 16.08px | Small erratic target |
| 400 | 29.47px | Standard tests |
| 600 | 33.74px | High-tick tests |
| 1000 | 40.00px | Heavy targets |

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

### 2. Match Armor Mass to Target Mass

```json
// Target should be mass 400
// Use test_armor_extreme_hp (mass 200)
"ship_class": "TestM_2L",  // base mass 200
"layers": {
    "CORE": [
        {"id": "test_armor_extreme_hp"}  // mass 200
    ]
}
// Total: 200 + 200 = 400 ✓

// For mass 600, use test_armor_extreme_hp_heavy (mass 400)
// Total: 200 + 400 = 600 ✓
```

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
