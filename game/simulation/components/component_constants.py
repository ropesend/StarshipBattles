"""
Component Constants - Enums and basic data classes for the component system.
"""

from enum import Enum, auto

__all__ = [
    'ComponentStatus',
    'Modifier',
    'ApplicationModifier',
]


class ComponentStatus(Enum):
    ACTIVE = auto()
    DAMAGED = auto()  # >50% damage
    NO_CREW = auto()
    NO_POWER = auto()
    NO_FUEL = auto()
    NO_AMMO = auto()



class Modifier:
    """
    Definition of a modifier that can be applied to components.

    Uses V2 format: effects is a list of effect objects with 'stat' and 'formula' fields.
    """
    def __init__(self, data):
        self.id = data['id']
        self.name = data.get('name', data['id'])
        self.description = data.get('description', '')
        self.restrictions = data.get('restrictions', {})
        self.readonly = data.get('readonly', False)

        # V2 format: effects is a list, param is a nested object
        self.effects = data.get('effects', [])
        param = data.get('param', {})
        self.min_val = param.get('min', 0)
        self.max_val = param.get('max', 100)
        self.default_val = param.get('default', self.min_val)

    def create_modifier(self, value=None):
        return ApplicationModifier(self, value)

    def evaluate_effects(self, param_value):
        """
        Evaluate all effects with the given parameter value.

        Args:
            param_value: The parameter value to evaluate with

        Returns:
            List[ModifierEffect] from formula evaluation
        """
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
