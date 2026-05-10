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


class StrategicResourceGenerationAbility(Ability):
    """Generates resources per turn on the strategy layer.

    Each instance generates a specific resource type at a given rate per turn
    (spread across 100 ticks). Works on any entity with facilities (planets,
    space stations, ships).

    Separate from combat ResourceGeneration which operates per second.

    Data fields:
        resource: Resource type identifier (e.g. from resources.json). Required.
        generation_rate: Amount produced per turn.
    """

    STAT_BINDINGS: List[AbilityStatBinding] = []  # Strategic marker ability

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

        if isinstance(data, dict):
            self.resource = data.get("resource", "")
            self.generation_rate = data.get("generation_rate", 0.0)
        else:
            self.resource = ""
            self.generation_rate = 0.0

    def get_primary_value(self) -> float:
        """Return the generation rate as primary value."""
        return self.generation_rate

    def get_ui_rows(self) -> List[Dict[str, str]]:
        """Return UI rows showing strategic generation stats."""
        return [
            {
                'label': 'Resource',
                'value': self.resource,
                'color_hint': HINT_COLONIZE
            },
            {
                'label': 'Strategic Rate',
                'value': f'{self.generation_rate:,.0f}/turn',
                'color_hint': HINT_ACCURACY
            },
        ]


class ResourceHarvestBoosterAbility(Ability):
    """Increases resource harvesting rate for a specific resource within scope.

    Multiplies the base_harvest_rate of matching ResourceHarvester abilities
    on colonies within the configured scope.

    Data fields:
        resource_type: Which resource to boost (e.g., "metals")
        multiplier: Harvest rate multiplier (e.g., 1.5 for 50% increase)
    """

    layer = AbilityLayer.STRATEGIC
    allowed_scopes = [
        AbilityScope.SELF, AbilityScope.PLANET, AbilityScope.SECTOR,
        AbilityScope.SYSTEM, AbilityScope.EMPIRE, AbilityScope.ALLIED_EMPIRE,
    ]
    default_scope = AbilityScope.PLANET

    STAT_BINDINGS: List[AbilityStatBinding] = []

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

        if isinstance(data, dict):
            self.resource_type = data.get("resource_type", "")
            self.multiplier = data.get("multiplier", 1.0)
        else:
            self.resource_type = ""
            self.multiplier = 1.0

    def get_primary_value(self) -> float:
        return self.multiplier

    def get_ui_rows(self) -> List[Dict[str, str]]:
        return [
            {
                'label': 'Resource',
                'value': self.resource_type.title(),
                'color_hint': HINT_COLONIZE
            },
            {
                'label': 'Boost',
                'value': f'{self.multiplier:.2f}x',
                'color_hint': HINT_ACCURACY
            },
            {
                'label': 'Scope',
                'value': self.scope.value.replace('_', ' ').title(),
                'color_hint': HINT_SHIELD_CAP
            },
        ]


class BuildRateBoosterAbility(Ability):
    """Increases construction/production rate within scope.

    Multiplies the production rate of all build queues on colonies
    within the configured scope.

    Data fields:
        multiplier: Build rate multiplier (e.g., 1.25 for 25% faster)
    """

    layer = AbilityLayer.STRATEGIC
    allowed_scopes = [
        AbilityScope.SELF, AbilityScope.PLANET, AbilityScope.SECTOR,
        AbilityScope.SYSTEM, AbilityScope.EMPIRE, AbilityScope.ALLIED_EMPIRE,
    ]
    default_scope = AbilityScope.SECTOR

    STAT_BINDINGS: List[AbilityStatBinding] = []

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

        if isinstance(data, dict):
            self.multiplier = data.get("multiplier", 1.0)
        else:
            self.multiplier = 1.0

    def get_primary_value(self) -> float:
        return self.multiplier

    def get_ui_rows(self) -> List[Dict[str, str]]:
        return [
            {
                'label': 'Build Rate',
                'value': f'{self.multiplier:.2f}x',
                'color_hint': HINT_ACCURACY
            },
            {
                'label': 'Scope',
                'value': self.scope.value.replace('_', ' ').title(),
                'color_hint': HINT_SHIELD_CAP
            },
        ]
