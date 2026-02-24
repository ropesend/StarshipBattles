"""
Cargo storage ability for transporting passengers and goods.

PROJ-68: Added generic cargo system - passengers first, extensible to other types.
"""

from typing import Any, Dict, List

from .base import Ability, AbilityLayer
from .stat_keys import AbilityStatBinding, StatKey
from .ui_colors import HINT_CARGO_PASSENGER, HINT_CARGO_GENERIC


class CargoStorage(Ability):
    """
    Ability to store cargo (passengers, goods, resources).

    Data formats:
        Dict: {"cargo_type": "passengers", "capacity": 5000}
        Scalar: 5000 (defaults to cargo_type="generic")

    The cargo_type parameter determines what can be loaded:
        - "passengers": Population units for colonization/transport
        - "generic": Any cargo type (future)
        - Other types as needed

    PROJ-68: Initial implementation for passenger transport.
    """

    layer = AbilityLayer.STRATEGIC  # Cargo only relevant in strategy layer

    STAT_BINDINGS: List[AbilityStatBinding] = [
        AbilityStatBinding(StatKey.CAPACITY_MULT, 'capacity', 'multiply', '_base_capacity'),
    ]

    def __init__(self, component, data: Any):
        super().__init__(component, data)
        if isinstance(data, dict):
            self.cargo_type = data.get('cargo_type', 'generic')
            self.capacity = float(data.get('capacity', 0))
        elif isinstance(data, (int, float)):
            self.cargo_type = 'generic'
            self.capacity = float(data)
        else:
            self.cargo_type = 'generic'
            self.capacity = 0.0
        self._base_capacity = self.capacity

    def sync_data(self, data: Any):
        """Update ability from new data."""
        super().sync_data(data)
        if isinstance(data, dict):
            self.cargo_type = data.get('cargo_type', self.cargo_type)
            self.capacity = float(data.get('capacity', 0))
            self._base_capacity = self.capacity
        elif isinstance(data, (int, float)):
            self.capacity = float(data)
            self._base_capacity = self.capacity

    def recalculate(self):
        """Recalculate capacity with modifiers."""
        self.capacity = self._base_capacity * self.get_effective_stat('capacity_mult', 1.0)

    def get_ui_rows(self) -> List[Dict[str, Any]]:
        """Return UI display data for this ability."""
        # Color by cargo type
        if self.cargo_type == 'passengers':
            color = HINT_CARGO_PASSENGER
            label = 'Passenger Cap'
        else:
            color = HINT_CARGO_GENERIC
            label = f'{self.cargo_type.title()} Cap'

        return [{'label': label, 'value': f"{self.capacity:.0f}", 'color_hint': color}]

    def get_primary_value(self) -> float:
        """Return the primary value (capacity) for this ability."""
        return self.capacity
