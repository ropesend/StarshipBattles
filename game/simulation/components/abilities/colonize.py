"""
ColonizePlanet ability for planet-type-specific colonization.

PROJ-55: Data-Driven Planet-Specific Colonization System

This ability marks a component (colony pod) as capable of colonizing
a specific planet type. Ships with a colony pod can colonize planets
matching the pod's planet_type.
"""

from typing import Dict, Any, List

from game.core.string_utils import display_name

from .base import Ability, AbilityLayer, AbilityScope
from .ui_colors import HINT_COLONIZE


class ColonizePlanet(Ability):
    """
    Marks a component as a colony pod for a specific planet type.

    This is a strategic-layer ability that enables a ship to colonize
    planets of the specified type. When colonization occurs, the ship
    carrying the pod is consumed.

    Data formats:
    - String shorthand: "ColonizePlanet": "ICE_DWARF"
    - Dict format: "ColonizePlanet": {"planet_type": "ICE_DWARF"}

    Supported planet types (11 total):
    - CONTINENTAL, ARID, PELAGIC, MAGMA, CRYOPLANET, BARREN
    - JOVIAN, ICE_GIANT, CHTHONIAN, ICE_DWARF, PLANETOID
    """

    # Strategic layer only - colonization happens on strategy map
    layer = AbilityLayer.STRATEGIC

    # Colony pods only affect the ship carrying them
    allowed_scopes = [AbilityScope.SELF]
    default_scope = AbilityScope.SELF

    # No stat bindings - this is a marker ability
    STAT_BINDINGS = []

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

        # Handle both string shorthand and dict format
        if isinstance(data, str):
            self.planet_type = data
            self.action_time = 1  # Default for string shorthand
        elif isinstance(data, dict):
            self.planet_type = data.get('planet_type', '')
            self.action_time = data.get('action_time', 1)  # PROJ-187: Tick-based actions
        else:
            self.planet_type = str(data)
            self.action_time = 1  # Default for non-dict data

    def get_ui_rows(self) -> List[Dict[str, str]]:
        """
        Return UI display row showing what planet type this pod colonizes.

        Returns:
            List with single row showing 'Colonizes: <Planet Type>'
        """
        # Format planet type: "ICE_DWARF" -> "Ice Dwarf"
        formatted_type = display_name(self.planet_type)

        return [{
            'label': 'Colonizes',
            'value': formatted_type,
            'color_hint': HINT_COLONIZE,
        }]

    def get_primary_value(self) -> float:
        """
        Return primary value for aggregation.

        ColonizePlanet is a marker ability - returns 0.0.
        """
        return 0.0
