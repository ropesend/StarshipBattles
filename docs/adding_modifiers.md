# Adding New Modifiers

> Step-by-step guide for adding new modifiers to the game.

## Quick Start

1. Add modifier definition to `data/modifiers_v2.json`
2. Write regression tests
3. Done!

## Step 1: Define the Modifier

Add to `data/modifiers_v2.json`:

```json
{
  "id": "your_modifier_id",
  "name": "Display Name",
  "description": "What this modifier does",
  "param": {
    "name": "Slider Label",
    "min": 1.0,
    "max": 10.0,
    "default": 1.0
  },
  "effects": [
    {"stat": "mass_mult", "formula": "param"},
    {"stat": "damage_mult", "formula": "param ^ 0.5"}
  ],
  "restrictions": {
    "allow_types": ["Weapon"],
    "deny_abilities": ["Armor"]
  }
}
```

## Step 2: Choose the Right Stats

### Available Stat Keys

From `game/simulation/components/modifier_schema.py`:

| Stat Key | Operation | Affects |
|----------|-----------|---------|
| `mass_mult` | multiply | Component mass |
| `hp_mult` | multiply | Component HP |
| `cost_mult` | multiply | Resource costs |
| `damage_mult` | multiply | Weapon damage |
| `range_mult` | multiply | Weapon range |
| `reload_mult` | multiply | Reload time |
| `arc_add` | add | Firing arc degrees |
| `arc_set` | set | Override firing arc |
| `crew_req_mult` | multiply | Crew requirements |
| `endurance_mult` | multiply | Seeker endurance |
| `projectile_damage_mult` | multiply | Seeker missile damage |
| `projectile_hp_mult` | multiply | Seeker missile HP |
| `projectile_stealth_mult` | multiply | Seeker stealth |
| `capacity_mult` | multiply | Shield/storage capacity |

### Operations

- `multiply`: Final = Base × Value
- `add`: Final = Base + Value
- `set`: Final = Value (overrides)

## Step 3: Write Formulas

Formulas use `param` as the slider value. Available functions:

```
param           Direct value
param ^ 2       Power (quadratic)
2 ^ param       Exponential
1.0 / param     Inverse
sqrt(param)     Square root
ln(param)       Natural log
log10(param)    Log base 10
abs(param)      Absolute value
min(a, b)       Minimum
max(a, b)       Maximum
```

### Example Formulas

| Effect | Formula | Explanation |
|--------|---------|-------------|
| Linear scaling | `param` | 1:1 with slider |
| Quadratic HP | `param ^ 2` | HP = mass² |
| Double range per level | `2 ^ param` | 1→2, 2→4, 3→8 |
| Halve reload time | `1.0 / param` | 2→0.5, 3→0.33 |
| Logarithmic mass | `1.0 + 0.514 * ln(1.0 + param / 30.0)` | Diminishing returns |

## Step 4: Add Restrictions

### Restrict by Component Type

```json
"restrictions": {
  "allow_types": ["Weapon", "ProjectileWeapon"],
  "deny_types": ["Hull", "Bridge"]
}
```

### Restrict by Ability

```json
"restrictions": {
  "allow_abilities": ["WeaponAbility"],
  "deny_abilities": ["Armor", "LifeSupport"]
}
```

### Make Mandatory (Auto-Applied)

Set in the modifier definition or via component data:

```json
"restrictions": {
  "mandatory_for_abilities": ["TurretMount"]
}
```

## Step 5: Targeted Effects (Advanced)

Apply different effects to different abilities:

```json
{
  "effects": [
    {
      "stat": "damage_mult",
      "formula": "1.5",
      "target_ability": "ProjectileWeaponAbility"
    },
    {
      "stat": "damage_mult",
      "formula": "1.2",
      "target_ability": "BeamWeaponAbility"
    }
  ]
}
```

## Step 6: Write Tests

Add regression test in `tests/regression/test_modifier_ability_snapshots.py`:

```python
def test_your_modifier_effects():
    """your_modifier: mass scales with param, damage with sqrt."""
    from game.simulation.components.component_constants import Modifier

    mod_def = Modifier({
        'id': 'your_modifier',
        'name': 'Your Modifier',
        'effects': [
            {'stat': 'mass_mult', 'formula': 'param'},
            {'stat': 'damage_mult', 'formula': 'sqrt(param)'}
        ]
    })

    effects = mod_def.evaluate_effects(4.0)

    mass_effect = next(e for e in effects if e.stat_key == 'mass_mult')
    damage_effect = next(e for e in effects if e.stat_key == 'damage_mult')

    assert mass_effect.value == pytest.approx(4.0)
    assert damage_effect.value == pytest.approx(2.0)  # sqrt(4)
```

## Step 7: Configure UI (Optional)

Add UI config in `ui/builder/modifier_config.py`:

```python
MODIFIER_UI_CONFIG = {
    'your_modifier': {
        'control_type': 'linear',
        'slider_step': 0.1,
        'step_buttons': [
            {'label': '-1', 'mode': 'delta_sub', 'value': 1.0},
            {'label': '+1', 'mode': 'delta_add', 'value': 1.0}
        ]
    }
}
```

## Validation

Run validation on load:

```python
errors = ModifierEffectEvaluator.validate_modifier_definition(mod_def)
if errors:
    print(f"Invalid modifier: {errors}")
```

## Checklist

- [ ] Added to `data/modifiers_v2.json`
- [ ] Formula syntax is valid
- [ ] Restrictions are appropriate
- [ ] Regression test written
- [ ] UI config added (if needed)
- [ ] All tests pass
