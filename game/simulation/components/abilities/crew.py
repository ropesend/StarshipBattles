import math
from typing import Dict, Any

from .base import Ability


class CrewCapacity(Ability):
    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        val = data if isinstance(data, (int, float)) else data.get('value', 0)
        self.amount = int(val)
        self._base_amount = self.amount

    def recalculate(self):
        self.amount = int(self._base_amount * self.component.stats.get('crew_capacity_mult', 1.0))

    def get_ui_rows(self):
        return [{'label': 'Crew Cap', 'value': f"{self.amount}", 'color_hint': '#96FF96'}]

    def get_primary_value(self) -> float:
        return float(self.amount)


class LifeSupportCapacity(Ability):
    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        val = data if isinstance(data, (int, float)) else data.get('value', 0)
        self.amount = int(val)
        self._base_amount = self.amount

    def recalculate(self):
        self.amount = int(self._base_amount * self.component.stats.get('life_support_capacity_mult', 1.0))

    def get_ui_rows(self):
        return [{'label': 'Life Support', 'value': f"{self.amount}", 'color_hint': '#96FFFF'}]

    def get_primary_value(self) -> float:
        return float(self.amount)


class CrewRequired(Ability):
    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        val = data if isinstance(data, (int, float)) else data.get('value', data.get('amount', 0))
        self.amount = int(val)
        self._base_amount = self.amount

    def recalculate(self):
        # Crew requirements scale with mass (sqrt) AND specific multiplier
        mass_mult = self.component.stats.get('mass_mult', 1.0)
        if mass_mult < 0:
            mass_mult = 0
        crew_mult = math.sqrt(mass_mult)

        self.amount = int(math.ceil(self._base_amount * crew_mult * self.component.stats.get('crew_req_mult', 1.0)))

    def get_ui_rows(self):
        return [{'label': 'Crew Req', 'value': f"{self.amount}", 'color_hint': '#FF9696'}]

    def get_primary_value(self) -> float:
        return float(self.amount)
