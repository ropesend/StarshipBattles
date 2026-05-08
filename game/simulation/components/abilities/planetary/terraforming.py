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


class AtmosphereModifierAbility(Ability):
    """Modifies a planet's atmosphere toward target gas compositions.

    Slowly adds or removes atmospheric gases each turn. The rate is in kg of
    gas that can be processed per turn. Conversion to pressure change depends
    on the planet's surface area and gravity.

    Data fields:
        modification_rate: kg of atmosphere that can be added/removed per turn
    """

    layer = AbilityLayer.STRATEGIC
    allowed_scopes = [AbilityScope.SELF]
    default_scope = AbilityScope.SELF

    STAT_BINDINGS: List[AbilityStatBinding] = []

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

        if isinstance(data, dict):
            self.modification_rate = data.get("modification_rate", 0.0)
        else:
            self.modification_rate = 0.0

    def get_primary_value(self) -> float:
        return self.modification_rate

    def get_ui_rows(self) -> List[Dict[str, str]]:
        return [
            {
                'label': 'Modification Rate',
                'value': f'{self.modification_rate:.2e} kg/turn',
                'color_hint': HINT_COLONIZE
            },
        ]


class QualityImprovementAbility(Ability):
    """Permanently improves resource deposit quality on a planet.

    Each turn, adds improvement_rate to the quality value of the specified
    resource on the planet. The change is permanent — it persists even if
    the facility is later removed. Quality caps at 100.

    Data fields:
        resource_type: Which resource to improve (e.g., "metals")
        improvement_rate: Quality increase per turn (e.g., 0.1)
    """

    layer = AbilityLayer.STRATEGIC
    allowed_scopes = [AbilityScope.SELF]
    default_scope = AbilityScope.SELF

    STAT_BINDINGS: List[AbilityStatBinding] = []

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

        if isinstance(data, dict):
            self.resource_type = data.get("resource_type", "")
            self.improvement_rate = data.get("improvement_rate", 0.0)
        else:
            self.resource_type = ""
            self.improvement_rate = 0.0

    def get_primary_value(self) -> float:
        return self.improvement_rate

    def get_ui_rows(self) -> List[Dict[str, str]]:
        return [
            {
                'label': 'Resource',
                'value': self.resource_type.title(),
                'color_hint': HINT_COLONIZE
            },
            {
                'label': 'Improvement',
                'value': f'+{self.improvement_rate:.1f}/turn',
                'color_hint': HINT_ACCURACY
            },
        ]


class GravityModifierAbility(Ability):
    """Modifies planet gravity when active. Reverts on deactivation.

    Activatable ability that changes the planet's effective gravity to a
    player-set target. Requires energy and uses the ComponentActivationEngine
    timer system. When the facility is deactivated or destroyed, gravity
    reverts to the original value.

    Data fields:
        energy_drain_rate: Energy consumed per turn while active
        activation_time: Ticks required to activate
        deactivation_time: Ticks required to deactivate
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
                'label': 'Activation',
                'value': f'{self.activation_time} ticks',
                'color_hint': HINT_DEFAULT
            },
        ]


class WaterModifierAbility(Ability):
    """Gradually changes planet water level toward target. Permanent.

    Passive ability that modifies surface_water each turn. The rate is the
    fraction of water coverage that can be changed per turn. Processed by
    WaterEngine once per turn, similar to AtmosphereEngine.

    Data fields:
        modification_rate: Fraction of water coverage change per turn (e.g., 0.005)
    """

    layer = AbilityLayer.STRATEGIC
    allowed_scopes = [AbilityScope.SELF]
    default_scope = AbilityScope.SELF

    STAT_BINDINGS: List[AbilityStatBinding] = []

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

        if isinstance(data, dict):
            self.modification_rate = data.get("modification_rate", 0.0)
        else:
            self.modification_rate = 0.0

    def get_primary_value(self) -> float:
        return self.modification_rate

    def get_ui_rows(self) -> List[Dict[str, str]]:
        return [
            {
                'label': 'Modification Rate',
                'value': f'{self.modification_rate:.4f}/turn',
                'color_hint': HINT_COLONIZE
            },
        ]
