"""
Harvester and Production abilities for planetary complexes.
"""

from typing import Dict, Any, List
from .base import Ability


class ResourceHarvesterAbility(Ability):
    """Enables resource harvesting on planets."""

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

        if isinstance(data, dict):
            self.resource_type = data.get("resource_type", "Unknown")
            self.base_harvest_rate = data.get("base_harvest_rate", 0.0)
        else:
            self.resource_type = "Unknown"
            self.base_harvest_rate = 0.0

    def get_primary_value(self) -> float:
        """Return the harvest rate as primary value."""
        return self.base_harvest_rate

    def get_ui_rows(self) -> List[Dict[str, str]]:
        """Return UI rows showing harvester stats."""
        return [
            {
                'label': 'Resource Type',
                'value': self.resource_type,
                'color_hint': '#00FF00'
            },
            {
                'label': 'Harvest Rate',
                'value': f'{self.base_harvest_rate:.1f}/turn',
                'color_hint': '#FFFF00'
            }
        ]


class SpaceShipyardAbility(Ability):
    """Enables ship construction at colonies."""

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

        if isinstance(data, dict):
            self.construction_speed_bonus = data.get("construction_speed_bonus", 1.0)
            self.max_ship_mass = data.get("max_ship_mass", 100000)
        else:
            self.construction_speed_bonus = 1.0
            self.max_ship_mass = 100000

    def get_primary_value(self) -> float:
        """Return the construction speed bonus as primary value."""
        return self.construction_speed_bonus

    def get_ui_rows(self) -> List[Dict[str, str]]:
        """Return UI rows showing shipyard stats."""
        return [
            {
                'label': 'Construction Bonus',
                'value': f'{self.construction_speed_bonus:.1f}x',
                'color_hint': '#00FFFF'
            },
            {
                'label': 'Max Ship Mass',
                'value': f'{self.max_ship_mass:,} kg',
                'color_hint': '#FFFFFF'
            }
        ]
