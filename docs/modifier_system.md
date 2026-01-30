# Modifier System Architecture

> Overview of the V2 modifier system with formula-based effects.

## Core Concepts

### Modifiers vs Abilities

- **Modifiers**: Data-driven multipliers/adjustments that affect component stats (mass, HP, damage, etc.)
- **Abilities**: Behavior classes (WeaponAbility, ShieldProjection, etc.) that consume stats and implement game logic

### Data Flow

```
JSON Modifier Definition
         ↓
ModifierEffectEvaluator.evaluate_modifier()
         ↓
List[ModifierEffect] (evaluated concrete values)
         ↓
Component.stats / Component.ability_stats
         ↓
Ability.recalculate() applies via STAT_BINDINGS
```

## Architecture Components

### 1. Modifier Definition (JSON)

V2 format stored in `data/modifiers.json`:

```json
{
  "id": "hardened_mount",
  "name": "Hardened",
  "description": "HP scales quadratically with mass",
  "param": {
    "name": "Mass Mult",
    "type": "linear",
    "min": 1.0,
    "max": 10.0,
    "default": 1.0
  },
  "effects": [
    {"stat": "mass_mult", "formula": "param"},
    {"stat": "hp_mult", "formula": "param ^ 2"},
    {"stat": "cost_mult", "formula": "param"}
  ],
  "restrictions": {
    "deny_abilities": ["Armor"]
  }
}
```

### 2. ModifierEffect (dataclass)

A single evaluated effect ready to apply:

```python
@dataclass
class ModifierEffect:
    stat_key: str           # "damage_mult", "hp_mult", etc.
    value: float            # Evaluated value (e.g., 1.5)
    operation: str          # "multiply", "add", "set"
    target_ability: str     # Optional: "WeaponAbility" for targeted effects
    source_modifier_id: str
    formula_str: str        # Original formula for UI display
    param_value: float      # Param value used for evaluation
```

### 3. ModifierEffectEvaluator

Evaluates formulas and produces ModifierEffect instances:

```python
effects = ModifierEffectEvaluator.evaluate_modifier(mod_def, param_value=2.0)
# Returns list of ModifierEffect with evaluated values
```

Supported formula syntax:
- `param` - Direct value
- `param ^ 2` - Power
- `2 ^ param` - Exponential
- `1.0 + param * 0.5` - Linear
- `1.0 + 0.514 * ln(1.0 + param / 30.0)` - Logarithmic
- `1.0 / param` - Inverse

### 4. STAT_BINDINGS (Ability System)

Abilities declare which stats they consume via STAT_BINDINGS:

```python
class WeaponAbility(Ability):
    STAT_BINDINGS = [
        AbilityStatBinding(StatKey.DAMAGE_MULT, 'damage', 'multiply', '_base_damage'),
        AbilityStatBinding(StatKey.RANGE_MULT, 'range', 'multiply', '_base_range'),
        AbilityStatBinding(StatKey.RELOAD_MULT, 'reload_time', 'multiply', '_base_reload'),
    ]
```

When `ability.recalculate()` is called, bindings automatically apply stats.

### 5. Component.stats / Component.ability_stats

- `component.stats`: Global stats affecting all abilities
- `component.ability_stats`: Dict keyed by ability class name for targeted effects

```python
# ability.get_effective_stat() checks ability_stats first, then falls back to stats
```

## File Locations

| File | Purpose |
|------|---------|
| `game/simulation/components/modifier_effects.py` | ModifierEffect, ModifierEffectEvaluator |
| `game/simulation/components/modifiers.py` | apply_modifier_effects(), aggregation |
| `game/simulation/components/abilities/stat_keys.py` | StatKey enum, AbilityStatBinding |
| `game/simulation/components/modifier_schema.py` | V2 format validation |
| `game/simulation/components/modifier_introspection.py` | UI introspection utilities |
| `game/simulation/components/component_constants.py` | Modifier, ApplicationModifier classes |
| `game/simulation/components/abilities/base.py` | Ability base class, STAT_BINDINGS |
| `data/modifiers.json` | Modifier definitions |

## Targeted Effects

Modifiers can target specific abilities:

```json
{
  "effects": [
    {"stat": "damage_mult", "formula": "1.5", "target_ability": "ProjectileWeaponAbility"},
    {"stat": "damage_mult", "formula": "1.2", "target_ability": "BeamWeaponAbility"}
  ]
}
```

This allows one modifier to affect different abilities differently.

## UI Integration

### ModifierIntrospection

Provides UI-friendly data:

```python
# Get modifier effects preview
affects = ModifierIntrospection.get_modifier_affects(mod_def, component, param_value)

# Get component modifier summary
summary = ModifierIntrospection.get_component_modifier_summary(component)

# Generate ability stats display (base vs current)
stats = ModifierIntrospection.generate_ability_stats_display(ability)
```

### Tooltip Generation

```python
tooltip = ModifierIntrospection.generate_modifier_tooltip(mod_def, param_value, component)
```

## Formula Validation

Formulas are validated on load:

```python
errors = ModifierEffectEvaluator.validate_formula("param ^ 2")  # Returns []
errors = ModifierEffectEvaluator.validate_formula("invalid_var")  # Returns error list
```

## Save/Load Compatibility

Applied modifiers are saved as:
```json
{
  "modifiers": [
    {"id": "hardened_mount", "value": 2.0}
  ]
}
```

On load, effects are re-evaluated from the current modifier definitions.

## API Reference

### ModifierEffectEvaluator

```python
class ModifierEffectEvaluator:
    @staticmethod
    def evaluate_modifier(mod_def: dict, param_value: float) -> List[ModifierEffect]:
        """Evaluate all effects in a modifier definition at a given parameter value.

        Args:
            mod_def: Modifier definition dict with 'effects' key
            param_value: The parameter value to evaluate formulas with

        Returns:
            List of ModifierEffect instances with evaluated values
        """

    @staticmethod
    def validate_formula(formula: str) -> List[str]:
        """Validate a formula string for syntax and allowed variables.

        Args:
            formula: Formula string (e.g., "param ^ 2", "1.0 + param * 0.5")

        Returns:
            Empty list if valid, list of error messages if invalid
        """
```

### ModifierEffect

```python
@dataclass
class ModifierEffect:
    stat_key: str           # Target stat (e.g., "damage_mult", "hp_mult")
    value: float            # Evaluated numeric value
    operation: str          # "multiply", "add", or "set"
    target_ability: str     # Optional: ability class name for targeted effects
    source_modifier_id: str # ID of the source modifier definition
    formula_str: str        # Original formula string for UI display
    param_value: float      # Parameter value used in evaluation
```

### ModifierIntrospection

```python
class ModifierIntrospection:
    @staticmethod
    def get_modifier_affects(mod_def: dict, component: Component, param_value: float) -> dict:
        """Get a preview of how a modifier would affect a component.

        Returns:
            Dict with 'global_effects' and 'ability_effects' keys
        """

    @staticmethod
    def get_component_modifier_summary(component: Component) -> dict:
        """Get summary of all modifiers applied to a component.

        Returns:
            Dict with 'modifiers' list and 'total_effects' aggregation
        """

    @staticmethod
    def generate_ability_stats_display(ability: Ability) -> List[dict]:
        """Generate stat display data showing base vs current values.

        Returns:
            List of dicts with 'name', 'base', 'current', 'formatted' keys
        """

    @staticmethod
    def generate_modifier_tooltip(mod_def: dict, param_value: float, component: Component) -> str:
        """Generate a human-readable tooltip for a modifier.

        Returns:
            Formatted string describing modifier effects at given param value
        """
```

### apply_modifier_effects

```python
def apply_modifier_effects(
    component: Component,
    effects: List[ModifierEffect],
    reset_first: bool = True
) -> None:
    """Apply a list of modifier effects to a component's stats.

    Args:
        component: Target component to modify
        effects: List of ModifierEffect instances to apply
        reset_first: If True, reset stats to defaults before applying
    """
```
