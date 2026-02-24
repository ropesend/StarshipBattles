"""
Superweapon abilities for strategic galaxy-altering powers.

PROJ-102: Strategic Superweapons and Special Orders

These abilities mark components as capable of performing one-shot strategic
superweapon actions: destroying planets/stars, opening/closing warp points,
creating Dyson Spheres, and self-destructing ships.

All superweapons:
- Are marker abilities (no stat bindings, no combat effects)
- Operate at STRATEGIC layer only
- Have SELF scope only (affect only the ship carrying them)
- Return 0.0 for get_primary_value() (no aggregation)
- Are consumed when used (entire ship carrying component is removed)
"""

from typing import Dict, Any, List

from .base import Ability, AbilityLayer, AbilityScope
from .ui_colors import HINT_SUPERWEAPON


class DestroyPlanet(Ability):
    """
    Marks a component as a Planet Imploder.

    Enables the ship to destroy a planet, removing it from the galaxy.
    The ship carrying this component is consumed when used.
    """

    layer = AbilityLayer.STRATEGIC
    allowed_scopes = [AbilityScope.SELF]
    default_scope = AbilityScope.SELF
    STAT_BINDINGS = []

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

    def get_ui_rows(self) -> List[Dict[str, str]]:
        """Return UI row showing superweapon capability."""
        return [{
            'label': 'Superweapon',
            'value': 'Planet Imploder',
            'color_hint': HINT_SUPERWEAPON,
        }]

    def get_primary_value(self) -> float:
        """Marker ability - returns 0.0."""
        return 0.0


class DestroyStar(Ability):
    """
    Marks a component as a Stellerator.

    Enables the ship to destroy a star, killing all ships in the system
    (including the firing ship) and removing all planets.
    """

    layer = AbilityLayer.STRATEGIC
    allowed_scopes = [AbilityScope.SELF]
    default_scope = AbilityScope.SELF
    STAT_BINDINGS = []

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

    def get_ui_rows(self) -> List[Dict[str, str]]:
        """Return UI row showing superweapon capability."""
        return [{
            'label': 'Superweapon',
            'value': 'Stellerator',
            'color_hint': HINT_SUPERWEAPON,
        }]

    def get_primary_value(self) -> float:
        """Marker ability - returns 0.0."""
        return 0.0


class OpenWarpPoint(Ability):
    """
    Marks a component as a Quantum Tunneling Inverter (Warp Point Creator).

    Enables the ship to create a new warp point connection between
    two star systems. The ship is consumed when used.
    """

    layer = AbilityLayer.STRATEGIC
    allowed_scopes = [AbilityScope.SELF]
    default_scope = AbilityScope.SELF
    STAT_BINDINGS = []

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

    def get_ui_rows(self) -> List[Dict[str, str]]:
        """Return UI row showing superweapon capability."""
        return [{
            'label': 'Superweapon',
            'value': 'Warp Point Creator',
            'color_hint': HINT_SUPERWEAPON,
        }]

    def get_primary_value(self) -> float:
        """Marker ability - returns 0.0."""
        return 0.0


class CloseWarpPoint(Ability):
    """
    Marks a component as a Quantum Tunneling Diverter (Warp Point Closer).

    Enables the ship to permanently close a warp point, removing the
    connection between two star systems. The ship is consumed when used.
    """

    layer = AbilityLayer.STRATEGIC
    allowed_scopes = [AbilityScope.SELF]
    default_scope = AbilityScope.SELF
    STAT_BINDINGS = []

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

    def get_ui_rows(self) -> List[Dict[str, str]]:
        """Return UI row showing superweapon capability."""
        return [{
            'label': 'Superweapon',
            'value': 'Warp Point Closer',
            'color_hint': HINT_SUPERWEAPON,
        }]

    def get_primary_value(self) -> float:
        """Marker ability - returns 0.0."""
        return 0.0


class CreateDysonSphere(Ability):
    """
    Marks a component as a Dyson Sphere Constructor.

    Enables the ship to construct a Dyson Sphere around a star,
    converting it into a massive energy-producing megastructure.
    The ship is consumed when used.
    """

    layer = AbilityLayer.STRATEGIC
    allowed_scopes = [AbilityScope.SELF]
    default_scope = AbilityScope.SELF
    STAT_BINDINGS = []

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

    def get_ui_rows(self) -> List[Dict[str, str]]:
        """Return UI row showing superweapon capability."""
        return [{
            'label': 'Superweapon',
            'value': 'Dyson Sphere Constructor',
            'color_hint': HINT_SUPERWEAPON,
        }]

    def get_primary_value(self) -> float:
        """Marker ability - returns 0.0."""
        return 0.0


class SelfDestruct(Ability):
    """
    Marks a component as a Self-Destruct Device.

    Enables the ship to be scheduled for self-destruction. Unlike other
    superweapons, this can be applied to multiple ships in a fleet.
    """

    layer = AbilityLayer.STRATEGIC
    allowed_scopes = [AbilityScope.SELF]
    default_scope = AbilityScope.SELF
    STAT_BINDINGS = []

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

    def get_ui_rows(self) -> List[Dict[str, str]]:
        """Return UI row showing superweapon capability."""
        return [{
            'label': 'Superweapon',
            'value': 'Self-Destruct Device',
            'color_hint': HINT_SUPERWEAPON,
        }]

    def get_primary_value(self) -> float:
        """Marker ability - returns 0.0."""
        return 0.0
