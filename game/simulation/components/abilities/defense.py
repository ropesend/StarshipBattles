from typing import Dict, Any, List

from game.core.config import PhysicsConfig
from .base import Ability, SimpleMultiplierAbility
from .stat_keys import StatKey, AbilityStatBinding
from .ui_colors import HINT_SHIELD_CAP, HINT_SHIELD_REGEN, HINT_DAMAGE, HINT_EVASION, HINT_ACCURACY


class ShieldProjection(SimpleMultiplierAbility):
    """Provides Shield Capacity.

    Shield capacity is affected by both:
    - CAPACITY_MULT: General capacity modifiers (from components/modifiers)
    - SHIELD_CAPACITY_MULT: Shield-specific modifiers (from environmental effects)

    Both multipliers stack multiplicatively.
    """

    stat_key = 'capacity_mult'
    value_attr = 'capacity'
    base_attr = 'base_capacity'
    ui_label = 'Shield Cap'
    ui_format = '{:.0f}'
    ui_color = HINT_SHIELD_CAP

    STAT_BINDINGS: List[AbilityStatBinding] = [
        AbilityStatBinding(StatKey.CAPACITY_MULT, 'capacity', 'multiply', 'base_capacity'),
        AbilityStatBinding(StatKey.SHIELD_CAPACITY_MULT, 'capacity', 'multiply', 'base_capacity'),
    ]

    def recalculate(self):
        """Apply both capacity_mult and shield_capacity_mult multiplicatively."""
        capacity_mult = self.get_effective_stat('capacity_mult', 1.0)
        shield_capacity_mult = self.get_effective_stat('shield_capacity_mult', 1.0)
        self.capacity = self.base_capacity * capacity_mult * shield_capacity_mult


class ShieldRegeneration(SimpleMultiplierAbility):
    """Regenerates Shields."""

    stat_key = 'energy_gen_mult'
    value_attr = 'rate'
    base_attr = 'base_rate'
    ui_label = 'Regen'
    ui_format = '{:.1f}/s'
    ui_color = HINT_SHIELD_REGEN

    STAT_BINDINGS: List[AbilityStatBinding] = [
        AbilityStatBinding(StatKey.ENERGY_GEN_MULT, 'rate', 'multiply', 'base_rate'),
    ]


class ToHitAttackModifier(Ability):
    """Modifier for to-hit attack bonuses."""

    STAT_BINDINGS: List[AbilityStatBinding] = []  # No modifier stats consumed

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        self.value = self._parse_primary_value(data)
        self._base_value = self.value

    def recalculate(self):
        # Apply generic properties or specific mult if needed.
        # Modifiers usually stack by addition in 'properties', but if we want mult:
        # For now, just re-setting base in case we add multipliers later.
        pass

    def get_ui_rows(self):
        val = self.value
        sign = "+" if val >= 0 else ""
        return [{'label': 'Targeting', 'value': f"{sign}{val:.1f}", 'color_hint': HINT_DAMAGE}]

    def get_primary_value(self) -> float:
        return self.value


class ToHitDefenseModifier(Ability):
    """Modifier for to-hit defense bonuses."""

    STAT_BINDINGS: List[AbilityStatBinding] = []  # No modifier stats consumed

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        self.value = self._parse_primary_value(data)
        self._base_value = self.value

    def recalculate(self):
        pass

    def get_ui_rows(self):
        val = self.value
        sign = "+" if val >= 0 else ""
        return [{'label': 'Evasion', 'value': f"{sign}{val:.1f}", 'color_hint': HINT_EVASION}]

    def get_primary_value(self) -> float:
        return self.value


class EmissiveArmor(Ability):
    """Provides damage ignore (ablative armor)."""

    STAT_BINDINGS: List[AbilityStatBinding] = []  # No modifier stats consumed

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        self.amount = int(self._parse_primary_value(data))
        self._base_amount = self.amount

    def recalculate(self):
        pass

    def get_ui_rows(self):
        return [{'label': 'Dmg Ignore', 'value': f"{self.amount}", 'color_hint': HINT_ACCURACY}]

    def get_primary_value(self) -> float:
        return float(self.amount)
