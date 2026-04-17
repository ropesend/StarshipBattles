"""
Superweapon abilities for strategic galaxy-altering powers.

PROJ-102: Strategic Superweapons and Special Orders
PROJ-176: Extracted SuperweaponMarker base class to eliminate duplication

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


class SuperweaponMarker(Ability):
    """Base class for all superweapon marker abilities.

    Superweapon markers share identical structure:
    - STRATEGIC layer only
    - SELF scope only
    - No stat bindings
    - Returns 0.0 for aggregation
    - UI shows 'Superweapon' label with weapon_name value

    Subclasses only need to set the weapon_name class attribute.
    """
    layer = AbilityLayer.STRATEGIC
    allowed_scopes = [AbilityScope.SELF]
    default_scope = AbilityScope.SELF
    STAT_BINDINGS: List = []

    weapon_name: str = ''

    def _parse_attrs(self, data: Any) -> None:
        """Parse action_time from data. Called from __init__ and sync_data
        so formula-driven values refresh correctly."""
        # PROJ-187: Parse action_time for tick-based execution
        # Boolean marker (True) defaults to 1, dict format supports action_time
        self.action_time = data.get('action_time', 1) if isinstance(data, dict) else 1

    def get_ui_rows(self) -> List[Dict[str, str]]:
        """Return UI row showing superweapon capability."""
        return [{
            'label': 'Superweapon',
            'value': self.weapon_name,
            'color_hint': HINT_SUPERWEAPON,
        }]

    def get_primary_value(self) -> float:
        """Marker ability - returns 0.0."""
        return 0.0


class DestroyPlanet(SuperweaponMarker):
    """Marks a component as a Planet Imploder.

    Enables the ship to destroy a planet, removing it from the galaxy.
    The ship carrying this component is consumed when used.
    """
    weapon_name = 'Planet Imploder'


class DestroyStar(SuperweaponMarker):
    """Marks a component as a Stellerator.

    Enables the ship to destroy a star, killing all ships in the system
    (including the firing ship) and removing all planets.
    """
    weapon_name = 'Stellerator'


class OpenWarpPoint(SuperweaponMarker):
    """Marks a component as a Quantum Tunneling Inverter (Warp Point Creator).

    Enables the ship to create a new warp point connection between
    two star systems. The ship is consumed when used.
    """
    weapon_name = 'Warp Point Creator'


class CloseWarpPoint(SuperweaponMarker):
    """Marks a component as a Quantum Tunneling Diverter (Warp Point Closer).

    Enables the ship to permanently close a warp point, removing the
    connection between two star systems. The ship is consumed when used.
    """
    weapon_name = 'Warp Point Closer'


class CreateDysonSphere(SuperweaponMarker):
    """Marks a component as a Dyson Sphere Constructor.

    Enables the ship to construct a Dyson Sphere around a star,
    converting it into a massive energy-producing megastructure.
    The ship is consumed when used.
    """
    weapon_name = 'Dyson Sphere Constructor'


class SelfDestruct(SuperweaponMarker):
    """Marks a component as a Self-Destruct Device.

    Enables the ship to be scheduled for self-destruction. Unlike other
    superweapons, this can be applied to multiple ships in a fleet.
    """
    weapon_name = 'Self-Destruct Device'
