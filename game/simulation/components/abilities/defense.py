from typing import Dict, Any, List

from game.core.config import PhysicsConfig
from .base import Ability
from .stat_keys import StatKey, AbilityStatBinding


class ShieldProjection(Ability):
    """Provides Shield Capacity."""

    STAT_BINDINGS: List[AbilityStatBinding] = [
        AbilityStatBinding(StatKey.CAPACITY_MULT, 'capacity', 'multiply', 'base_capacity'),
    ]

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        val = data if isinstance(data, (int, float)) else data.get('value', 0)
        self.base_capacity = float(val)
        self.capacity = self.base_capacity

    def recalculate(self):
        # Apply capacity_mult from component stats (populated by modifiers)
        mult = self.get_effective_stat('capacity_mult', 1.0)
        self.capacity = self.base_capacity * mult

    def get_ui_rows(self):
        return [{'label': 'Shield Cap', 'value': f"{self.capacity:.0f}", 'color_hint': '#00FFFF'}]  # Cyan

    def get_primary_value(self) -> float:
        return self.capacity


class ShieldRegeneration(Ability):
    """Regenerates Shields."""

    STAT_BINDINGS: List[AbilityStatBinding] = [
        AbilityStatBinding(StatKey.ENERGY_GEN_MULT, 'rate', 'multiply', 'base_rate'),
    ]

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        val = data if isinstance(data, (int, float)) else data.get('value', 0)
        self.base_rate = float(val)
        self.rate = self.base_rate

    def recalculate(self):
        # Apply energy_gen_mult (modifier stat key)
        mult = self.get_effective_stat('energy_gen_mult', 1.0)
        self.rate = self.base_rate * mult

    def get_ui_rows(self):
        return [{'label': 'Regen', 'value': f"{self.rate:.1f}/s", 'color_hint': '#00C8FF'}]  # Deep Sky Blue

    def get_primary_value(self) -> float:
        return self.rate


class ToHitAttackModifier(Ability):
    """Modifier for to-hit attack bonuses."""

    STAT_BINDINGS: List[AbilityStatBinding] = []  # No modifier stats consumed

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        val = data if isinstance(data, (int, float)) else data.get('value', 0)
        self.value = float(val)
        self._base_value = self.value

    def recalculate(self):
        # Apply generic properties or specific mult if needed.
        # Modifiers usually stack by addition in 'properties', but if we want mult:
        # For now, just re-setting base in case we add multipliers later.
        pass

    def get_ui_rows(self):
        val = self.value
        sign = "+" if val >= 0 else ""
        return [{'label': 'Targeting', 'value': f"{sign}{val:.1f}", 'color_hint': '#FF6464'}]

    def get_primary_value(self) -> float:
        return self.value


class ToHitDefenseModifier(Ability):
    """Modifier for to-hit defense bonuses."""

    STAT_BINDINGS: List[AbilityStatBinding] = []  # No modifier stats consumed

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        val = data if isinstance(data, (int, float)) else data.get('value', 0)
        self.value = float(val)
        self._base_value = self.value

    def recalculate(self):
        pass

    def get_ui_rows(self):
        val = self.value
        sign = "+" if val >= 0 else ""
        return [{'label': 'Evasion', 'value': f"{sign}{val:.1f}", 'color_hint': '#64FFFF'}]

    def get_primary_value(self) -> float:
        return self.value


class EmissiveArmor(Ability):
    """Provides damage ignore (ablative armor)."""

    STAT_BINDINGS: List[AbilityStatBinding] = []  # No modifier stats consumed

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        val = data if isinstance(data, (int, float)) else data.get('value', 0)
        self.amount = int(val)
        self._base_amount = self.amount

    def recalculate(self):
        pass

    def get_ui_rows(self):
        return [{'label': 'Dmg Ignore', 'value': f"{self.amount}", 'color_hint': '#FFFF00'}]

    def get_primary_value(self) -> float:
        return float(self.amount)
