# Modifier System Architecture

> Overview of the V2 modifier system with formula-based effects.
> For a complete catalog of all abilities and their stat bindings, see [ability_reference.md](../systems/ability_reference.md).

## Core Concepts

### Modifiers vs Abilities

- **Modifiers**: Data-driven multipliers/adjustments that affect component stats (mass, HP, damage, etc.)
- **Abilities**: Behavior classes (WeaponAbility, ShieldProjection, etc.) that consume stats and implement game logic

### Data Flow

Modifiers reach ability/ship math via TWO parallel paths — component-born
modifiers (left) and battle-scoped team auras (right):

```
Component-born modifiers                   Battle-scoped team auras
(persistent ship state)                    (rebuilt each battle from ModifierStack)

JSON Modifier Definition                   spec compilers emit ModifierEntry
         |                                          |
ModifierEffectEvaluator.evaluate_modifier()         v
         |                                  FleetAuraManager._apply_bonuses
List[ModifierEffect]                                |
         |                                  ship.external_stats[stat_key]: float
apply_modifier_effects()                            |
         |                                          +--------------------------+
Component.stats / Component.ability_stats                                      |
         |                                                                     |
Ability.recalculate() via STAT_BINDINGS <----- composed in              read directly in
                                               Ability.get_effective_stat      ship_stats._apply_aggregated_stats
                                               (per-ability keys,              (ship-level keys,
                                                e.g. damage_mult)                e.g. shield_bonus_add)
```

Component-born modifiers live on `component.stats` and survive
serialization; battle-scoped team auras live on `ship.external_stats`
and are NEVER serialized (they are recomputed from
`ModifierStack` each battle). See patterns 24 (External-Stats Bridge)
and 25 (Scope-Driven Team Routing) in [02_PATTERNS.md](../02_PATTERNS.md).

## Architecture Components

### 1. Modifier Definition (JSON)

V2 format stored in `data/modifiers.json`:

```json
{
  "id": "hardened_mount",
  "name": "Hardened",
  "description": "HP increases as the square of mass multiplier. 2x mass = 4x HP.",
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
    stat_key: str               # "damage_mult", "hp_mult", etc.
    value: float                # Evaluated value (e.g., 1.5)
    operation: str              # "multiply", "add", "set"
    target_ability: Optional[str]  # None = all abilities; "WeaponAbility" for targeted
    source_modifier_id: str
    source_modifier_name: str
    formula_str: str            # Original formula for UI display
    param_value: float          # Param value used for evaluation
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
- `sqrt(param)` - Square root
- `min(a, b)` / `max(a, b)` - Min/max
- References to other stats via `stats_context` (e.g., `mass_mult - 1.0`)

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
| `game/simulation/components/modifiers.py` | apply_modifier_effects(), get_default_stat_multipliers(), calculate_stat_multipliers() |
| `game/simulation/components/abilities/stat_keys.py` | StatKey enum, AbilityStatBinding |
| `game/simulation/components/modifier_schema.py` | V2 format validation |
| `game/simulation/components/modifier_introspection.py` | UI introspection utilities |
| `game/simulation/components/component_constants.py` | Modifier, ApplicationModifier classes |
| `game/simulation/components/abilities/base.py` | Ability base class, STAT_BINDINGS |
| `game/simulation/services/modifier_service.py` | ModifierService (validation, mandatory modifiers, value constraints) |
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

This allows one modifier to affect different abilities differently. Targeted effects are stored in `component.ability_stats[target_ability]` rather than the global `component.stats` dict.

## UI Integration

### ModifierIntrospection

Provides UI-friendly data:

```python
# Get modifier effects preview (what abilities does this modifier affect?)
affects = ModifierIntrospection.get_modifier_affects(mod_def, component, param_value)

# Get component modifier summary (all applied modifiers and their effects)
summary = ModifierIntrospection.get_component_modifier_summary(component)

# Get ability-level summary (base vs current for each stat binding)
ability_summary = ModifierIntrospection.get_ability_modifier_summary(ability)

# Generate display-ready stat entries for UI rendering
stats = ModifierIntrospection.generate_ability_stats_display(ability)
```

### Tooltip Generation

```python
tooltip = ModifierIntrospection.generate_modifier_tooltip(mod_def, param_value, component)
```

### Modifier UI Config

`game/ui/screens/builder/modifier_config.py` defines per-modifier UI controls:

```python
MODIFIER_UI_CONFIG = {
    'simple_size_mount': {
        'control_type': 'linear_stepped',
        'step_buttons': [
            {'label': '<<<', 'value': 5.0, 'mode': 'delta_sub'},
            ...
        ],
        'slider_step': 0.1,
    },
    'turret_mount': { ... },
    'facing': { 'control_type': 'facing_selector', ... },
    ...
}
```

## Formula Validation

Formulas are validated on load:

```python
errors = ModifierEffectEvaluator.validate_formula("param ^ 2")  # Returns []
errors = ModifierEffectEvaluator.validate_formula("invalid_var")  # Returns error list
```

Full modifier definition validation:

```python
errors = ModifierEffectEvaluator.validate_modifier_definition(mod_def)
if errors:
    print(f"Invalid modifier: {errors}")
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

### apply_modifier_effects

```python
def apply_modifier_effects(
    modifier_def,
    value: float,
    stats: dict,
    component=None
) -> None:
    """Apply the effects of a single modifier to the stats dictionary.

    All modifiers use V2 format with formula-based effects.

    Args:
        modifier_def: The Modifier definition object (has evaluate_effects method).
        value: The current value of the modifier application (slider/param value).
        stats: Dictionary containing accumulated multipliers and properties
               (from get_default_stat_multipliers()).
        component: Optional reference to the component. Required for targeted
                   effects that write to component.ability_stats.
    """
```

### calculate_stat_multipliers

```python
def calculate_stat_multipliers(
    modifier_entries: list,
    modifier_registry: dict
) -> dict:
    """Calculate stat multipliers from a list of modifier entries.

    Pure function - no side effects, no object state needed.

    Args:
        modifier_entries: List of dicts with 'id' and 'value' keys
                         e.g., [{'id': 'simple_size_mount', 'value': 20.0}]
        modifier_registry: Dict mapping modifier IDs to Modifier definitions

    Returns:
        Dict of stat_key -> value (multipliers, additive values, etc.)
    """
```

### get_default_stat_multipliers

```python
def get_default_stat_multipliers() -> dict:
    """Return default stat multipliers dictionary.

    Canonical list of all supported modifier stats. Returns:
        {
            'mass_mult': 1.0,          # Multiplicative (default 1.0)
            'hp_mult': 1.0,
            'damage_mult': 1.0,
            'range_mult': 1.0,
            'cost_mult': 1.0,
            'thrust_mult': 1.0,
            'turn_mult': 1.0,
            'strategic_mult': 1.0,
            'energy_gen_mult': 1.0,
            'capacity_mult': 1.0,
            'shield_capacity_mult': 1.0,
            'crew_capacity_mult': 1.0,
            'life_support_capacity_mult': 1.0,
            'consumption_mult': 1.0,
            'reload_mult': 1.0,
            'endurance_mult': 1.0,
            'projectile_hp_mult': 1.0,
            'projectile_damage_mult': 1.0,
            'crew_req_mult': 1.0,
            'mass_add': 0.0,           # Additive (default 0.0)
            'arc_add': 0.0,
            'accuracy_add': 0.0,
            'projectile_stealth_level': 0.0,
            'arc_set': None,           # Set/override (default None)
            'properties': {},
        }
    """
```

### ModifierEffectEvaluator

```python
class ModifierEffectEvaluator:
    @staticmethod
    def evaluate_formula(formula: str, context: Dict[str, float]) -> float:
        """Evaluate a formula string with the given context.

        Args:
            formula: Formula string (e.g., "param ^ 2", "1.0 + param * 0.5")
            context: Dictionary of variable values (e.g., {'param': 2.0})

        Returns:
            Evaluated result as float

        Raises:
            FormulaException: If formula cannot be evaluated
        """

    @classmethod
    def evaluate_modifier(
        cls,
        mod_def: Dict[str, Any],
        param_value: float,
        stats_context: Optional[Dict[str, float]] = None
    ) -> List[ModifierEffect]:
        """Evaluate a modifier definition with a given parameter value.

        Args:
            mod_def: Modifier definition dict with 'effects' key
            param_value: The parameter value to evaluate formulas with
            stats_context: Optional dict of already-computed stats for
                           dependency resolution (e.g., referencing mass_mult
                           in another formula)

        Returns:
            List of ModifierEffect instances with evaluated values
        """

    @classmethod
    def validate_formula(cls, formula: str) -> List[str]:
        """Validate a formula string for syntax and allowed variables.

        Args:
            formula: Formula string (e.g., "param ^ 2", "1.0 + param * 0.5")

        Returns:
            Empty list if valid, list of error messages if invalid
        """

    @classmethod
    def validate_modifier_definition(cls, mod_def: Dict[str, Any]) -> List[str]:
        """Validate all formulas in a modifier definition.

        Args:
            mod_def: Modifier definition dict

        Returns:
            List of error messages (empty if valid)
        """
```

### ModifierEffect

```python
@dataclass
class ModifierEffect:
    stat_key: str               # Target stat (e.g., "damage_mult", "hp_mult")
    value: float                # Evaluated numeric value
    operation: str              # "multiply", "add", "add_to_mult", or "set"
    target_ability: Optional[str]  # Ability class name for targeted effects, or None
    source_modifier_id: str     # ID of the source modifier definition
    source_modifier_name: str   # Display name of the source modifier
    formula_str: str            # Original formula string for UI display
    param_value: float          # Parameter value used in evaluation

    def describe(self) -> str:
        """Human-readable description (e.g., 'damage_mult x1.50')."""

    def is_targeted(self) -> bool:
        """Returns True if this effect targets a specific ability."""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization/introspection."""
```

### ModifierIntrospection

```python
class ModifierIntrospection:
    @staticmethod
    def get_modifier_affects(
        mod_def: dict, component: Component, param_value: Optional[float] = None
    ) -> dict:
        """Determine what abilities a modifier affects on a given component.

        Returns:
            {
                'abilities': ['ProjectileWeaponAbility', ...],
                'effects_preview': ['damage_mult x1.50', ...],
                'affected_stats': ['damage_mult', ...],
                'targeted_abilities': ['ProjectileWeaponAbility', ...],
            }
        """

    @staticmethod
    def get_component_modifier_summary(component: Component) -> dict:
        """Get summary of all modifiers applied to a component.

        Returns:
            {
                'component_id': 'railgun',
                'component_name': 'Railgun',
                'applied_modifiers': [{'id': ..., 'name': ..., 'param_value': ..., 'effects': [...]}],
                'total_stats': {'mass_mult': 2.0, ...}
            }
        """

    @staticmethod
    def get_ability_modifier_summary(ability: Ability) -> dict:
        """Get summary of how modifiers affect a specific ability.

        Returns:
            {
                'ability_class': 'ProjectileWeaponAbility',
                'stats': [{'attribute': 'damage', 'base': 100.0, 'current': 150.0, ...}]
            }
        """

    @staticmethod
    def generate_ability_stats_display(ability: Ability) -> List[dict]:
        """Generate display-ready stat entries showing base vs current values.

        Returns:
            [{'label': 'Damage', 'attribute': 'damage', 'base': 100.0,
              'current': 150.0, 'modified': True, 'change_percent': 50.0,
              'display_text': '150.0 (base: 100.0, +50%)'}]
        """

    @staticmethod
    def generate_modifier_tooltip(
        mod_def: dict, param_value: float, component: Optional[Component] = None
    ) -> str:
        """Generate a human-readable tooltip for a modifier.

        Returns:
            Formatted multi-line string describing modifier effects
        """
```

### ModifierService

```python
class ModifierService:
    """Service for component modifier operations (validation, mandatory modifiers, value constraints).

    Usage:
        service = ModifierService(modifier_registry=registries.modifiers)
        if service.is_modifier_allowed('turret_mount', component):
            service.ensure_mandatory_modifiers(component)
    """

    MANDATORY_MODIFIERS = ['simple_size_mount', 'range_mount', 'facing', 'turret_mount']

    def __init__(self, modifier_registry: Dict[str, Any]):
        """Initialize with modifier registry (required, strict DI)."""

    def is_modifier_allowed(self, mod_id: str, component) -> bool:
        """Check if a modifier is allowed for the given component."""

    def get_mandatory_modifiers(self, component) -> list:
        """Returns list of modifier IDs that are mandatory for this component."""

    def is_modifier_mandatory(self, mod_id: str, component) -> bool:
        """Check if a specific modifier is mandatory for this component."""

    def get_initial_value(self, mod_id: str, component) -> float:
        """Get the initial/default value for a newly applied modifier."""

    def ensure_mandatory_modifiers(self, component) -> None:
        """Auto-apply all mandatory modifiers that are missing from the component."""

    def get_local_min_max(self, mod_id: str, component) -> tuple:
        """Returns (min, max) for a modifier, accounting for component-specific constraints."""
```

### Modifier (Definition Class)

```python
class Modifier:
    """Definition of a modifier loaded from JSON.

    Attributes:
        id: Unique modifier ID
        name: Display name
        description: Human-readable description
        restrictions: Dict of allow/deny rules
        readonly: Whether the modifier is read-only
        effects: List of effect dicts from JSON
        min_val: Minimum parameter value
        max_val: Maximum parameter value
        default_val: Default parameter value
    """

    def create_modifier(self, value=None) -> ApplicationModifier:
        """Create an ApplicationModifier instance from this definition."""

    def evaluate_effects(self, param_value: float) -> List[ModifierEffect]:
        """Evaluate all effects with the given parameter value."""
```
