import math
from typing import Any, List

from .base import Ability, SimpleMultiplierAbility
from .stat_keys import StatKey, AbilityStatBinding
from .ui_colors import HINT_CREW_CAP, HINT_LIFE_SUPPORT, HINT_CREW_REQ


class CrewCapacity(SimpleMultiplierAbility):
    """Provides crew capacity."""

    stat_key = 'crew_capacity_mult'
    value_attr = 'amount'
    base_attr = '_base_amount'
    ui_label = 'Crew Cap'
    ui_format = '{}'
    ui_color = HINT_CREW_CAP
    int_result = True

    STAT_BINDINGS: List[AbilityStatBinding] = [
        AbilityStatBinding(StatKey.CREW_CAPACITY_MULT, 'amount', 'multiply', '_base_amount'),
    ]


class LifeSupportCapacity(SimpleMultiplierAbility):
    """Provides life support capacity."""

    stat_key = 'life_support_capacity_mult'
    value_attr = 'amount'
    base_attr = '_base_amount'
    ui_label = 'Life Support'
    ui_format = '{}'
    ui_color = HINT_LIFE_SUPPORT
    int_result = True

    STAT_BINDINGS: List[AbilityStatBinding] = [
        AbilityStatBinding(StatKey.LIFE_SUPPORT_CAPACITY_MULT, 'amount', 'multiply', '_base_amount'),
    ]


class CrewRequired(Ability):
    """
    Ability that specifies how much crew a component requires to operate.

    Note on stat bindings:
        This ability uses mass_mult with non-standard handling (sqrt scaling)
        in addition to the standard crew_req_mult binding. The mass_mult dependency
        is intentionally NOT declared in STAT_BINDINGS because:
        1. It uses sqrt(mass_mult) rather than direct multiplication
        2. The STAT_BINDINGS framework doesn't support custom operation functions
        3. The crew scales with the square root of mass to reflect that
           larger components need more crew but not linearly proportional

        This is documented behavior, not a bug. See recalculate() for implementation.
    """

    STAT_BINDINGS: List[AbilityStatBinding] = [
        AbilityStatBinding(StatKey.CREW_REQ_MULT, 'amount', 'multiply', '_base_amount'),
    ]

    def _parse_attrs(self, data: Any) -> None:
        """Parse crew amount from data. Called from __init__ and sync_data, so
        formula-driven values (e.g. =ceil(sqrt(ship_class_mass / 1000))) refresh
        whenever the abilities dict is re-evaluated — including when the
        component is attached to a ship and ship_class_mass becomes resolvable.
        """
        self.amount = int(self._parse_primary_value(data, fallback_keys=('amount',)))
        self._base_amount = self.amount

    def recalculate(self):
        # Crew requirements scale with mass (sqrt) AND specific multiplier
        mass_mult = self.get_effective_stat('mass_mult', 1.0)
        if mass_mult < 0:
            mass_mult = 0
        crew_mult = math.sqrt(mass_mult)

        self.amount = int(math.ceil(self._base_amount * crew_mult * self.get_effective_stat('crew_req_mult', 1.0)))

    def get_ui_rows(self):
        return [{'label': 'Crew Req', 'value': f"{self.amount}", 'color_hint': HINT_CREW_REQ}]

    def get_primary_value(self) -> float:
        return float(self.amount)
