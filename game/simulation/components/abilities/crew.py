import math
from typing import Dict, Any, List

from .base import Ability
from .stat_keys import StatKey, AbilityStatBinding
from .ui_colors import HINT_CREW_CAP, HINT_LIFE_SUPPORT, HINT_CREW_REQ


class CrewCapacity(Ability):

    STAT_BINDINGS: List[AbilityStatBinding] = [
        AbilityStatBinding(StatKey.CREW_CAPACITY_MULT, 'amount', 'multiply', '_base_amount'),
    ]

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        self.amount = int(self._parse_primary_value(data))
        self._base_amount = self.amount

    def recalculate(self):
        self.amount = int(self._base_amount * self.get_effective_stat('crew_capacity_mult', 1.0))

    def get_ui_rows(self):
        return [{'label': 'Crew Cap', 'value': f"{self.amount}", 'color_hint': HINT_CREW_CAP}]

    def get_primary_value(self) -> float:
        return float(self.amount)


class LifeSupportCapacity(Ability):

    STAT_BINDINGS: List[AbilityStatBinding] = [
        AbilityStatBinding(StatKey.LIFE_SUPPORT_CAPACITY_MULT, 'amount', 'multiply', '_base_amount'),
    ]

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        self.amount = int(self._parse_primary_value(data))
        self._base_amount = self.amount

    def recalculate(self):
        self.amount = int(self._base_amount * self.get_effective_stat('life_support_capacity_mult', 1.0))

    def get_ui_rows(self):
        return [{'label': 'Life Support', 'value': f"{self.amount}", 'color_hint': HINT_LIFE_SUPPORT}]

    def get_primary_value(self) -> float:
        return float(self.amount)


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

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        val = data if isinstance(data, (int, float)) else data.get('value', data.get('amount', 0))
        self.amount = int(val)
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
