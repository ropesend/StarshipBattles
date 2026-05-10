"""PROJ-382 Phase 5: split sub-module of ``planetary.py``.

The original 913-LOC ``planetary.py`` was decomposed into a package
(``planetary/``) with one sub-module per responsibility. The package
``__init__`` re-exports every Ability so legacy imports
``from game.simulation.components.abilities.planetary import X``
continue to resolve.
"""

from typing import Dict, Any, List
from ..base import Ability, AbilityLayer, AbilityScope
from ..stat_keys import AbilityStatBinding
from ..ui_colors import (
    HINT_ACCURACY, HINT_DEFAULT, HINT_WARP_ENERGY, HINT_COLONIZE,
    HINT_SHIELD_CAP, HINT_DAMAGE,
)


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


class RadiationShieldAbility(Ability):
    """Provides radiation shielding when active. Reverts on deactivation.

    Activatable ability that adds artificial radiation protection to a planet.
    The shielding value is additive with the planet's natural magnetic_field
    in habitability calculations. When deactivated or destroyed, the shielding
    reverts to zero.

    Data fields:
        energy_drain_rate: Energy consumed per turn while active
        activation_time: Ticks required to activate
        deactivation_time: Ticks required to deactivate
        max_shielding: Maximum radiation shielding strength (additive with magnetic_field)
    """

    layer = AbilityLayer.STRATEGIC
    allowed_scopes = [AbilityScope.SELF]
    default_scope = AbilityScope.SELF

    STAT_BINDINGS: List[AbilityStatBinding] = []

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

        if isinstance(data, dict):
            self.energy_drain_rate = data.get("energy_drain_rate", 0.0)
            self.activation_time = data.get("activation_time", 1)
            self.deactivation_time = data.get("deactivation_time", 1)
            self.max_shielding = data.get("max_shielding", 1.0)
        else:
            self.energy_drain_rate = 0.0
            self.activation_time = 1
            self.deactivation_time = 1
            self.max_shielding = 1.0

    def get_primary_value(self) -> float:
        return self.energy_drain_rate

    def get_ui_rows(self) -> List[Dict[str, str]]:
        return [
            {
                'label': 'Energy Drain',
                'value': f'{self.energy_drain_rate:.1f}/turn',
                'color_hint': HINT_WARP_ENERGY
            },
            {
                'label': 'Max Shielding',
                'value': f'{self.max_shielding:.1f}',
                'color_hint': HINT_SHIELD_CAP
            },
            {
                'label': 'Activation',
                'value': f'{self.activation_time} ticks',
                'color_hint': HINT_DEFAULT
            },
        ]


