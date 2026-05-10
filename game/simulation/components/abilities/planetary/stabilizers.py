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


class GeologicStabilizerAbility(Ability):
    """Prevents planet-destroying superweapons within scope.

    When active, protects planets from IMPLODE_PLANET superweapon.
    Scope determines range of protection:
    - PLANET: protects only the planet this facility is on
    - SECTOR: protects all planets in the same hex
    - SYSTEM: protects all planets in the star system

    Requires energy and manual activation (same mechanism as PlanetaryShield).

    Data fields:
        energy_drain_rate: Energy consumed per turn while active
        activation_time: Ticks required to activate
        deactivation_time: Ticks required to deactivate
    """

    layer = AbilityLayer.STRATEGIC
    allowed_scopes = [AbilityScope.PLANET, AbilityScope.SECTOR, AbilityScope.SYSTEM]
    default_scope = AbilityScope.SECTOR

    STAT_BINDINGS: List[AbilityStatBinding] = []

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

        if isinstance(data, dict):
            self.energy_drain_rate = data.get("energy_drain_rate", 0.0)
            self.activation_time = data.get("activation_time", 1)
            self.deactivation_time = data.get("deactivation_time", 1)
        else:
            self.energy_drain_rate = 0.0
            self.activation_time = 1
            self.deactivation_time = 1

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
                'label': 'Scope',
                'value': self.scope.value.replace('_', ' ').title(),
                'color_hint': HINT_SHIELD_CAP
            },
            {
                'label': 'Activation',
                'value': f'{self.activation_time} ticks',
                'color_hint': HINT_DEFAULT
            },
        ]


class StellarStabilizerAbility(Ability):
    """Prevents star-destroying superweapons (DestroyStar, CreateDysonSphere) within scope.

    When active, blocks STELLERATE_STAR and CREATE_DYSON_SPHERE superweapon orders
    from affecting any star in the system. Requires energy and manual activation.

    Data fields:
        energy_drain_rate: Energy consumed per turn while active
        activation_time: Ticks required to activate
        deactivation_time: Ticks required to deactivate
    """

    layer = AbilityLayer.STRATEGIC
    allowed_scopes = [AbilityScope.SECTOR, AbilityScope.SYSTEM]
    default_scope = AbilityScope.SYSTEM

    STAT_BINDINGS: List[AbilityStatBinding] = []

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

        if isinstance(data, dict):
            self.energy_drain_rate = data.get("energy_drain_rate", 0.0)
            self.activation_time = data.get("activation_time", 1)
            self.deactivation_time = data.get("deactivation_time", 1)
        else:
            self.energy_drain_rate = 0.0
            self.activation_time = 1
            self.deactivation_time = 1

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
                'label': 'Scope',
                'value': self.scope.value.replace('_', ' ').title(),
                'color_hint': HINT_SHIELD_CAP
            },
            {
                'label': 'Activation',
                'value': f'{self.activation_time} ticks',
                'color_hint': HINT_DEFAULT
            },
        ]


class WarpFieldStabilizerAbility(Ability):
    """Prevents warp point creation and destruction within scope.

    When active, blocks OPEN_WARP_POINT and CLOSE_WARP_POINT superweapon orders
    from affecting the system. Requires energy and manual activation.

    Data fields:
        energy_drain_rate: Energy consumed per turn while active
        activation_time: Ticks required to activate
        deactivation_time: Ticks required to deactivate
    """

    layer = AbilityLayer.STRATEGIC
    allowed_scopes = [AbilityScope.SECTOR, AbilityScope.SYSTEM]
    default_scope = AbilityScope.SYSTEM

    STAT_BINDINGS: List[AbilityStatBinding] = []

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

        if isinstance(data, dict):
            self.energy_drain_rate = data.get("energy_drain_rate", 0.0)
            self.activation_time = data.get("activation_time", 1)
            self.deactivation_time = data.get("deactivation_time", 1)
        else:
            self.energy_drain_rate = 0.0
            self.activation_time = 1
            self.deactivation_time = 1

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
                'label': 'Scope',
                'value': self.scope.value.replace('_', ' ').title(),
                'color_hint': HINT_SHIELD_CAP
            },
            {
                'label': 'Activation',
                'value': f'{self.activation_time} ticks',
                'color_hint': HINT_DEFAULT
            },
        ]
