"""
Component Constants - Enums and basic data classes for the component system.
"""

from enum import Enum, auto


class ComponentStatus(Enum):
    ACTIVE = auto()
    DAMAGED = auto()  # >50% damage
    NO_CREW = auto()
    NO_POWER = auto()
    NO_FUEL = auto()
    NO_AMMO = auto()


class LayerType(Enum):
    HULL = 0    # [NEW] Innermost Chassis Layer
    CORE = 1
    INNER = 2
    OUTER = 3
    ARMOR = 4

    @staticmethod
    def from_string(s):
        return getattr(LayerType, s.upper())


class Modifier:
    """
    Definition of a modifier that can be applied to components.

    Supports two formats:
    - V1: effects is a dict with 'special' key referencing a handler function
    - V2: effects is a list of effect objects with 'stat' and 'formula' fields
    """
    def __init__(self, data):
        self.id = data['id']
        self.name = data.get('name', data['id'])
        self.description = data.get('description', '')
        self.restrictions = data.get('restrictions', {})
        self.readonly = data.get('readonly', False)

        # Detect format and load accordingly
        effects = data.get('effects', {})
        self.is_v2_format = isinstance(effects, list)

        if self.is_v2_format:
            # V2 format: effects is a list, param is a nested object
            self.effects = effects
            param = data.get('param', {})
            self.type_str = param.get('type', 'linear')
            self.param_name = param.get('name', 'value')
            self.min_val = param.get('min', 0)
            self.max_val = param.get('max', 100)
            self.default_val = param.get('default', self.min_val)
        else:
            # V1 format: effects is a dict, param fields at top level
            self.effects = effects
            self.type_str = data.get('type', 'linear')
            self.param_name = data.get('param_name', 'value')
            self.min_val = data.get('min_val', 0)
            self.max_val = data.get('max_val', 100)
            self.default_val = data.get('default_val', self.min_val)

    def create_modifier(self, value=None):
        return ApplicationModifier(self, value)

    def evaluate_effects(self, param_value):
        """
        Evaluate all effects with the given parameter value.

        Only works for V2 format modifiers. V1 modifiers use the old
        apply_modifier_effects() path.

        Args:
            param_value: The parameter value to evaluate with

        Returns:
            List[ModifierEffect] for V2 format, None for V1 format
        """
        if not self.is_v2_format:
            return None

        from .modifier_effects import ModifierEffectEvaluator
        return ModifierEffectEvaluator.evaluate_modifier(
            {'id': self.id, 'name': self.name, 'effects': self.effects},
            param_value
        )


class ApplicationModifier:
    """Instance of a modifier applied to a component."""
    def __init__(self, mod_def, value=None):
        self.definition = mod_def
        self.value = value if value is not None else mod_def.default_val
