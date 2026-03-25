from typing import List

from .base import SimpleMultiplierAbility, StaticValueAbility
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


class ToHitAttackModifier(StaticValueAbility):
    """Modifier for to-hit attack bonuses."""

    ui_label = 'Targeting'
    ui_color = HINT_DAMAGE
    ui_format = '{:+.1f}'


class ToHitDefenseModifier(StaticValueAbility):
    """Modifier for to-hit defense bonuses."""

    ui_label = 'Evasion'
    ui_color = HINT_EVASION
    ui_format = '{:+.1f}'


class EmissiveArmor(StaticValueAbility):
    """Provides damage ignore (ablative armor)."""

    ui_label = 'Dmg Ignore'
    ui_color = HINT_ACCURACY
    ui_format = '{}'
    int_result = True
