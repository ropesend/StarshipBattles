from typing import Dict, Any, List

from .base import Ability, AbilityLayer, AbilityScope, SimpleMultiplierAbility
from .stat_keys import StatKey, AbilityStatBinding
from .ui_colors import HINT_THRUST, HINT_TURN_SPEED, HINT_STRATEGIC_MOBILITY, HINT_SHIELD_CAP, HINT_DEFAULT, HINT_WARP_ENERGY


class CombatPropulsion(SimpleMultiplierAbility):
    """Provides Thrust."""

    stat_key = 'thrust_mult'
    value_attr = 'thrust_force'
    base_attr = 'base_thrust'
    ui_label = 'Thrust'
    ui_format = '{:.0f} N'
    ui_color = HINT_THRUST

    STAT_BINDINGS: List[AbilityStatBinding] = [
        AbilityStatBinding(StatKey.THRUST_MULT, 'thrust_force', 'multiply', 'base_thrust'),
    ]


class ManeuveringThruster(SimpleMultiplierAbility):
    """Provides Rotation."""

    stat_key = 'turn_mult'
    value_attr = 'turn_rate'
    base_attr = 'base_turn_rate'
    ui_label = 'Turn Speed'
    ui_format = '{:.1f} deg/s'
    ui_color = HINT_TURN_SPEED

    STAT_BINDINGS: List[AbilityStatBinding] = [
        AbilityStatBinding(StatKey.TURN_MULT, 'turn_rate', 'multiply', 'base_turn_rate'),
    ]


class StrategicMovement(SimpleMultiplierAbility):
    """
    Provides strategic map movement points.

    Movement points represent the engine's capacity for sustained interstellar travel,
    as opposed to CombatPropulsion's burst thrust for tactical maneuvering.

    An engine can have:
    - High combat thrust + low strategic movement (short-range interceptors)
    - Low combat thrust + high strategic movement (cargo haulers)
    - Balanced values (general purpose)

    Scope options:
    - SELF (default): Engine on ship provides movement to that ship
    - ALLIED_SECTOR: Tug providing boost to ships in same hex
    - ALLIED_SYSTEM: Orbital tractor array boosting all allied ships in system
    """
    layer = AbilityLayer.STRATEGIC
    allowed_scopes = [AbilityScope.SELF, AbilityScope.ALLIED_SECTOR, AbilityScope.ALLIED_SYSTEM]
    default_scope = AbilityScope.SELF

    stat_key = 'strategic_mult'
    value_attr = 'movement_points'
    base_attr = 'base_movement_points'
    ui_label = 'Strategic Mobility'
    ui_format = '{:.0f} MP'
    ui_color = HINT_STRATEGIC_MOBILITY

    STAT_BINDINGS: List[AbilityStatBinding] = [
        AbilityStatBinding(StatKey.STRATEGIC_MULT, 'movement_points', 'multiply', 'base_movement_points'),
    ]


class WarpJump(Ability):
    """
    Binary capability for warp transit between star systems.

    A ship must have a WarpJump ability to transit through warp points.
    The warp drive has a maximum tonnage limit - the ship's total mass
    must be <= max_tonnage to use the warp drive.

    Warp transit consumes 1 movement point.

    Note: WarpJump only affects SELF scope - a warp drive cannot enable
    other ships to jump.
    """
    layer = AbilityLayer.STRATEGIC
    allowed_scopes = [AbilityScope.SELF]
    default_scope = AbilityScope.SELF

    # WarpJump does not consume any modifier stats
    STAT_BINDINGS: List[AbilityStatBinding] = []

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        # Handle primitive shortcut: "WarpJump": 5000 means max_tonnage=5000
        if isinstance(data, (int, float)):
            self.max_tonnage = float(data)
            self.energy_cost = 0.0
        else:
            self.max_tonnage = float(data.get('max_tonnage', 0))
            self.energy_cost = float(data.get('energy_cost', 0))

    def can_jump(self, ship_mass: float) -> bool:
        """
        Check if a ship is light enough to use this warp drive.

        Args:
            ship_mass: Total mass of the ship attempting to jump

        Returns:
            True if ship can use this warp drive (mass <= max_tonnage)
        """
        return ship_mass <= self.max_tonnage

    def get_ui_rows(self) -> List[Dict[str, str]]:
        rows = [
            {'label': 'Warp Capable', 'value': 'Yes', 'color_hint': HINT_SHIELD_CAP},
            {'label': 'Max Tonnage', 'value': f'{self.max_tonnage:,.0f} kg', 'color_hint': HINT_DEFAULT},
        ]
        if self.energy_cost > 0:
            rows.append({'label': 'Warp Energy', 'value': f'{self.energy_cost:,.0f}', 'color_hint': HINT_WARP_ENERGY})
        return rows

    def get_primary_value(self) -> float:
        return self.max_tonnage
