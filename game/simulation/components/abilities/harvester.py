"""
Harvester, Storage, and Production abilities for planetary complexes.
"""

from typing import Dict, Any, List
from .base import Ability
from .stat_keys import AbilityStatBinding
from .ui_colors import HINT_COLONIZE, HINT_ACCURACY, HINT_SHIELD_CAP, HINT_DEFAULT


class ResourceHarvesterAbility(Ability):
    """Enables resource harvesting on planets."""

    STAT_BINDINGS: List[AbilityStatBinding] = []  # Marker ability

    def _parse_attrs(self, data: Any) -> None:
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
                'color_hint': HINT_COLONIZE
            },
            {
                'label': 'Harvest Rate',
                'value': f'{self.base_harvest_rate:.1f}/turn',
                'color_hint': HINT_ACCURACY
            }
        ]


class LocalStorageAbility(Ability):
    """Provides storage capacity for local colony storage.

    Each instance adds capacity for a specific resource type.
    Multiple storage facilities stack additively.

    Data fields:
        resource_type: Resource identifier (e.g. "metals", "organics")
        capacity: Base storage capacity units
    """

    STAT_BINDINGS: List[AbilityStatBinding] = []  # Marker ability

    def _parse_attrs(self, data: Any) -> None:
        if isinstance(data, dict):
            self.resource_type = data.get("resource_type", "")
            self.capacity = data.get("capacity", 0.0)
        else:
            self.resource_type = ""
            self.capacity = 0.0
        self._base_capacity = self.capacity

    def recalculate(self) -> None:
        """Recalculate capacity with any storage modifiers."""
        modifier = self.get_effective_stat('storage_mult', 1.0)
        self.capacity = self._base_capacity * modifier

    def get_primary_value(self) -> float:
        """Return the storage capacity as primary value."""
        return self.capacity

    def get_ui_rows(self) -> List[Dict[str, str]]:
        """Return UI rows showing storage stats."""
        return [
            {
                'label': 'Resource Type',
                'value': self.resource_type,
                'color_hint': HINT_COLONIZE
            },
            {
                'label': 'Storage Capacity',
                'value': f'{self.capacity:,.0f}',
                'color_hint': HINT_ACCURACY
            }
        ]


class StagingYardAbility(Ability):
    """Provides planet-side storage for constructed items (fighters, drop pods).

    Each instance adds mass capacity for storing assembled vehicles on the planet.
    Multiple staging yard facilities stack additively.
    """

    STAT_BINDINGS: List[AbilityStatBinding] = []

    def _parse_attrs(self, data: Any) -> None:
        if isinstance(data, dict):
            self.capacity_mass = data.get('capacity_mass', 0.0)
        else:
            self.capacity_mass = float(data) if data else 0.0

    def get_primary_value(self) -> float:
        return self.capacity_mass

    def get_ui_rows(self) -> List[Dict[str, str]]:
        return [{'label': 'Staging Capacity', 'value': f'{self.capacity_mass:.0f} mass', 'hint_color': None}]


class PlanetaryYardAbility(Ability):
    """Enables base planetary construction queue on a colony.

    A colony must have at least one operational facility with this ability
    to use its base construction queue (for building complexes).
    The starter complex placed during colonization provides this ability.
    """

    STAT_BINDINGS: List[AbilityStatBinding] = []  # Marker ability

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

    def get_primary_value(self) -> float:
        return 1.0

    def get_ui_rows(self) -> List[Dict[str, str]]:
        return [{'label': 'Planetary Yard', 'value': 'Yes', 'hint_color': None}]


class SpaceShipyardAbility(Ability):
    """Enables ship construction at colonies."""

    STAT_BINDINGS: List[AbilityStatBinding] = []  # Marker ability

    def _parse_attrs(self, data: Any) -> None:
        if isinstance(data, dict):
            self.construction_speed_bonus = data.get("construction_speed_bonus", 1.0)
            self.max_ship_mass = data.get("max_ship_mass", 100000)
            self.production_rates: Dict[str, float] = data.get("production_rates", {})
        else:
            self.construction_speed_bonus = 1.0
            self.max_ship_mass = 100000
            self.production_rates: Dict[str, float] = {}

    def get_primary_value(self) -> float:
        """Return the construction speed bonus as primary value."""
        return self.construction_speed_bonus

    def get_ui_rows(self) -> List[Dict[str, str]]:
        """Return UI rows showing shipyard stats."""
        rows = [
            {
                'label': 'Construction Bonus',
                'value': f'{self.construction_speed_bonus:.1f}x',
                'color_hint': HINT_SHIELD_CAP
            },
            {
                'label': 'Max Ship Mass',
                'value': f'{self.max_ship_mass:,} kg',
                'color_hint': HINT_DEFAULT
            }
        ]
        if self.production_rates:
            # Show max rate if all rates are equal, otherwise show range
            rates = list(self.production_rates.values())
            if len(set(rates)) == 1:
                rows.append({
                    'label': 'Production Rate',
                    'value': f'{int(rates[0]):,}/turn',
                    'color_hint': HINT_COLONIZE
                })
            else:
                rows.append({
                    'label': 'Production Rate',
                    'value': f'{int(min(rates)):,}-{int(max(rates)):,}/turn',
                    'color_hint': HINT_COLONIZE
                })
        return rows
