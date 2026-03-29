"""
Planetary abilities for energy generation, storage, and shields.

PROJ-237: Strategic-layer abilities for planetary complexes.
These are marker abilities (no combat stat bindings) used by the
PlanetEnergyEngine and PlanetActionEngine in the strategy layer.
"""

from typing import Dict, Any, List
from .base import Ability
from .stat_keys import AbilityStatBinding
from .ui_colors import HINT_SHIELD_CAP, HINT_ACCURACY, HINT_DEFAULT, HINT_WARP_ENERGY


class PlanetaryShieldAbility(Ability):
    """Enables planetary shield protection.

    When active, consumes energy per turn and blocks planet destroyer
    superweapons. Activation and deactivation take time (in ticks).

    Data fields:
        energy_drain_rate: Energy consumed per turn while active
        activation_time: Ticks required to activate the shield
        deactivation_time: Ticks required to deactivate the shield
        shield_hp: Combat shield hit points (placeholder for future combat integration)
        shield_regen: Combat shield regeneration rate (placeholder for future combat integration)
    """

    STAT_BINDINGS: List[AbilityStatBinding] = []  # Strategic marker ability

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

        if isinstance(data, dict):
            self.energy_drain_rate = data.get("energy_drain_rate", 0.0)
            self.activation_time = data.get("activation_time", 1)
            self.deactivation_time = data.get("deactivation_time", 1)
            # Combat placeholders (future integration)
            self.shield_hp = data.get("shield_hp", 0.0)
            self.shield_regen = data.get("shield_regen", 0.0)
        else:
            self.energy_drain_rate = 0.0
            self.activation_time = 1
            self.deactivation_time = 1
            self.shield_hp = 0.0
            self.shield_regen = 0.0

    def get_primary_value(self) -> float:
        """Return the energy drain rate as primary value."""
        return self.energy_drain_rate

    def get_ui_rows(self) -> List[Dict[str, str]]:
        """Return UI rows showing shield stats."""
        return [
            {
                'label': 'Energy Drain',
                'value': f'{self.energy_drain_rate:.1f}/turn',
                'color_hint': HINT_WARP_ENERGY
            },
            {
                'label': 'Activation Time',
                'value': f'{self.activation_time} ticks',
                'color_hint': HINT_DEFAULT
            },
            {
                'label': 'Deactivation Time',
                'value': f'{self.deactivation_time} ticks',
                'color_hint': HINT_DEFAULT
            },
        ]


class PlanetaryEnergyGeneratorAbility(Ability):
    """Generates energy for planetary systems.

    Energy is stored in a per-planet pool and consumed by active
    planetary shields and other energy-dependent facilities.

    Data fields:
        generation_rate: Energy produced per turn
    """

    STAT_BINDINGS: List[AbilityStatBinding] = []  # Strategic marker ability

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

        if isinstance(data, dict):
            self.generation_rate = data.get("generation_rate", 0.0)
        else:
            self.generation_rate = float(data) if isinstance(data, (int, float)) else 0.0

    def get_primary_value(self) -> float:
        """Return the generation rate as primary value."""
        return self.generation_rate

    def get_ui_rows(self) -> List[Dict[str, str]]:
        """Return UI rows showing generator stats."""
        return [
            {
                'label': 'Generation Rate',
                'value': f'{self.generation_rate:.1f}/turn',
                'color_hint': HINT_ACCURACY
            },
        ]


class PlanetaryEnergyStorageAbility(Ability):
    """Provides energy storage capacity for a planet.

    Multiple storage facilities stack additively to increase
    the planet's total energy capacity.

    Data fields:
        capacity: Maximum energy units this component can store
    """

    STAT_BINDINGS: List[AbilityStatBinding] = []  # Strategic marker ability

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

        if isinstance(data, dict):
            self.capacity = data.get("capacity", 0.0)
        else:
            self.capacity = float(data) if isinstance(data, (int, float)) else 0.0

    def get_primary_value(self) -> float:
        """Return the storage capacity as primary value."""
        return self.capacity

    def get_ui_rows(self) -> List[Dict[str, str]]:
        """Return UI rows showing storage stats."""
        return [
            {
                'label': 'Energy Capacity',
                'value': f'{self.capacity:,.0f}',
                'color_hint': HINT_SHIELD_CAP
            },
        ]
