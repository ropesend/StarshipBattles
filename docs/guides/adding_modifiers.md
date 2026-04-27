# Adding New Modifiers

> **Last verified:** 2026-03-14

> Step-by-step guide for adding new modifiers to the game.

## Quick Start

1. Add modifier definition to `data/modifiers.json`
2. Write regression tests
3. Done!

## Step 1: Define the Modifier

Add to `data/modifiers.json`:

```json
{
  "id": "your_modifier_id",
  "name": "Display Name",
  "description": "What this modifier does",
  "param": {
    "name": "Slider Label",
    "type": "linear",
    "min": 1.0,
    "max": 10.0,
    "default": 1.0
  },
  "effects": [
    {"stat": "mass_mult", "formula": "param"},
    {"stat": "damage_mult", "formula": "param ^ 0.5"}
  ],
  "restrictions": {
    "allow_abilities": ["WeaponAbility"],
    "deny_abilities": ["Armor"]
  }
}
```

## Step 2: Choose the Right Stats

### Available Stat Keys

From `game/simulation/components/abilities/stat_keys.py`:

| Stat Key | Default | Operation | Affects |
|----------|---------|-----------|---------|
| `mass_mult` | 1.0 | multiply | Component mass |
| `hp_mult` | 1.0 | multiply | Component HP |
| `cost_mult` | 1.0 | multiply | Resource costs |
| `damage_mult` | 1.0 | multiply | Weapon damage |
| `range_mult` | 1.0 | multiply | Weapon range |
| `reload_mult` | 1.0 | multiply | Reload time |
| `thrust_mult` | 1.0 | multiply | Engine thrust |
| `turn_mult` | 1.0 | multiply | Turn rate |
| `strategic_mult` | 1.0 | multiply | Strategic speed |
| `energy_gen_mult` | 1.0 | multiply | Energy generation |
| `capacity_mult` | 1.0 | multiply | General capacity |
| `shield_capacity_mult` | 1.0 | multiply | Shield capacity |
| `crew_capacity_mult` | 1.0 | multiply | Crew capacity |
| `life_support_capacity_mult` | 1.0 | multiply | Life support capacity |
| `consumption_mult` | 1.0 | multiply | Resource consumption |
| `endurance_mult` | 1.0 | multiply | Seeker endurance |
| `projectile_damage_mult` | 1.0 | multiply | Seeker missile damage |
| `projectile_hp_mult` | 1.0 | multiply | Seeker missile HP |
| `crew_req_mult` | 1.0 | multiply | Crew requirements |
| `mass_add` | 0.0 | add | Additional mass |
| `arc_add` | 0.0 | add | Firing arc degrees |
| `accuracy_add` | 0.0 | add | Accuracy bonus |
| `projectile_stealth_level` | 0.0 | add | Seeker stealth level |
| `arc_set` | None | set | Override firing arc |

**Note:** The stat key for seeker stealth in effect definitions is `projectile_stealth_add` (operation: add), which maps to the internal stat `projectile_stealth_level`. See the `seeker_stealth` modifier in `data/modifiers.json` for an example.

### Operations

- `multiply`: Final = Base x Value (default if not specified)
- `add`: Final = Base + Value
- `add_to_mult`: Final = Base + Value (used for additive contributions to multiplier stats, e.g., rapid_fire mass scaling)
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
| Quadratic HP | `param ^ 2` | HP = mass squared |
| Double range per level | `2 ^ param` | 1->2, 2->4, 3->8 |
| Halve reload time | `1.0 / param` | 2->0.5, 3->0.33 |
| Logarithmic mass | `1.0 + 0.514 * ln(1.0 + param / 30.0)` | Diminishing returns |
| Additive mass scaling | `(param - 1.0) * 2.0` | With `add_to_mult` operation |

## Step 4: Add Restrictions

Restrictions use ability class names to control which components can use a modifier.

### Allow Specific Abilities

```json
"restrictions": {
  "allow_abilities": ["WeaponAbility", "ProjectileWeaponAbility", "BeamWeaponAbility"]
}
```

### Deny Specific Abilities

```json
"restrictions": {
  "deny_abilities": ["Armor", "LifeSupport"]
}
```

### Combined Restrictions

You can combine allow and deny:

```json
"restrictions": {
  "allow_abilities": ["WeaponAbility"],
  "deny_abilities": ["SeekerWeaponAbility"]
}
```

This allows projectile and beam weapons but not seeker/missile weapons.

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

Add UI config in `game/ui/screens/builder/modifier_config.py`:

```python
MODIFIER_UI_CONFIG = {
    'your_modifier': {
        'control_type': 'linear_stepped',
        'slider_step': 0.1,
        'step_buttons': [
            {'label': '<<', 'value': 1.0, 'mode': 'delta_sub'},
            {'label': '<', 'value': 0.1, 'mode': 'delta_sub'},
            {'label': '>', 'value': 0.1, 'mode': 'delta_add'},
            {'label': '>>', 'value': 1.0, 'mode': 'delta_add'}
        ]
    }
}
```

Modifiers not listed in `MODIFIER_UI_CONFIG` use the `DEFAULT_CONFIG` (linear slider with 0.01 step).

## Validation

Run validation on load:

```python
errors = ModifierEffectEvaluator.validate_modifier_definition(mod_def)
if errors:
    print(f"Invalid modifier: {errors}")
```

## Checklist

- [ ] Added to `data/modifiers.json`
- [ ] Formula syntax is valid
- [ ] Restrictions are appropriate
- [ ] Regression test written
- [ ] UI config added in `game/ui/screens/builder/modifier_config.py` (if custom controls needed)
- [ ] All tests pass
