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
from ._shared import _STORM_SCOPES
from ..ui_colors import (
    HINT_ACCURACY, HINT_DEFAULT, HINT_WARP_ENERGY, HINT_COLONIZE,
    HINT_SHIELD_CAP, HINT_DAMAGE,
)


class EnvironmentalDamageAbility(Ability):
    """Applies per-turn hull damage to fleets within scope (PROJ-300, rate-style).

    Consumed by `environmental_hazard_engine`. Carries a `damage_type` parameter
    for grouping (plasma, radiation, thermal, default 'environmental'). Two
    radiation belts at the same hex aggregate via intra-MAX (worst); plasma +
    radiation aggregate via inter-SUM.

    Data fields:
        rate: Hull HP damage per turn (>= 0)
        damage_type: Type label for grouping in `aggregate_rates` (default 'environmental')
    """

    layer = AbilityLayer.STRATEGIC
    allowed_scopes = _STORM_SCOPES
    default_scope = AbilityScope.SECTOR

    STAT_BINDINGS: List[AbilityStatBinding] = []

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        if isinstance(data, dict):
            self.rate = data.get("rate", 0.0)
            self.damage_type = data.get("damage_type", "environmental")
        else:
            self.rate = 0.0
            self.damage_type = "environmental"

    def get_primary_value(self) -> float:
        return self.rate

    def get_ui_rows(self) -> List[Dict[str, str]]:
        return [
            {'label': f'Damage ({self.damage_type})',
             'value': f'-{self.rate:.2f} hull/turn', 'color_hint': HINT_DAMAGE},
            {'label': 'Scope', 'value': self.scope.value.replace('_', ' ').title(),
             'color_hint': HINT_DEFAULT},
        ]


class FuelDrainAbility(Ability):
    """Drains fleet fuel per turn when within scope (PROJ-300, rate-style).

    Consumed by `environmental_hazard_engine`. Storm `radiation_belt` drains
    0.1 fuel/turn; multiple sources sum per damage_type. (FuelDrain has no
    sub-type so all entries share the same group.)

    Data fields:
        rate: Fuel units drained per turn (>= 0)
    """

    layer = AbilityLayer.STRATEGIC
    allowed_scopes = _STORM_SCOPES
    default_scope = AbilityScope.SECTOR

    STAT_BINDINGS: List[AbilityStatBinding] = []

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        self.rate = data.get("rate", 0.0) if isinstance(data, dict) else 0.0

    def get_primary_value(self) -> float:
        return self.rate

    def get_ui_rows(self) -> List[Dict[str, str]]:
        return [
            {'label': 'Fuel Drain', 'value': f'-{self.rate:.2f}/turn',
             'color_hint': HINT_WARP_ENERGY},
            {'label': 'Scope', 'value': self.scope.value.replace('_', ' ').title(),
             'color_hint': HINT_DEFAULT},
        ]
