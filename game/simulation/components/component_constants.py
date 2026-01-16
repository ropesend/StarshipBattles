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
    """Definition of a modifier that can be applied to components."""
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.type_str = data['type']  # 'boolean' or 'linear'
        self.description = data.get('description', '')
        self.effects = data.get('effects', {})
        self.restrictions = data.get('restrictions', {})
        self.param_name = data.get('param_name', 'value')
        self.min_val = data.get('min_val', 0)
        self.max_val = data.get('max_val', 100)
        self.default_val = data.get('default_val', self.min_val)
        self.readonly = data.get('readonly', False)

    def create_modifier(self, value=None):
        return ApplicationModifier(self, value)


class ApplicationModifier:
    """Instance of a modifier applied to a component."""
    def __init__(self, mod_def, value=None):
        self.definition = mod_def
        self.value = value if value is not None else mod_def.default_val
