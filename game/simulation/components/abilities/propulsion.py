from typing import Dict, Any, List

from .base import Ability, AbilityLayer, AbilityScope
from .stat_keys import StatKey, AbilityStatBinding


class CombatPropulsion(Ability):
    """Provides Thrust."""

    STAT_BINDINGS: List[AbilityStatBinding] = [
        AbilityStatBinding(StatKey.THRUST_MULT, 'thrust_force', 'multiply', 'base_thrust'),
    ]

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        self.base_thrust = self._parse_primary_value(data)
        self.thrust_force = self.base_thrust

    def sync_data(self, data: Any):
        super().sync_data(data)
        self.base_thrust = self._parse_primary_value(data)
        self.thrust_force = self.base_thrust

    def recalculate(self):
        self.thrust_force = self.base_thrust * self.get_effective_stat('thrust_mult', 1.0)

    def get_ui_rows(self):
        return [{'label': 'Thrust', 'value': f"{self.thrust_force:.0f} N", 'color_hint': '#64FF64'}]  # Light Green

    def get_primary_value(self) -> float:
        return self.thrust_force


class ManeuveringThruster(Ability):
    """Provides Rotation."""

    STAT_BINDINGS: List[AbilityStatBinding] = [
        AbilityStatBinding(StatKey.TURN_MULT, 'turn_rate', 'multiply', 'base_turn_rate'),
    ]

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        self.base_turn_rate = self._parse_primary_value(data)
        self.turn_rate = self.base_turn_rate

    def sync_data(self, data: Any):
        super().sync_data(data)
        self.base_turn_rate = self._parse_primary_value(data)
        self.turn_rate = self.base_turn_rate

    def recalculate(self):
        self.turn_rate = self.base_turn_rate * self.get_effective_stat('turn_mult', 1.0)

    def get_ui_rows(self):
        return [{'label': 'Turn Speed', 'value': f"{self.turn_rate:.1f} deg/s", 'color_hint': '#64FF96'}]  # Slightly different green

    def get_primary_value(self) -> float:
        return self.turn_rate


class StrategicMovement(Ability):
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

    STAT_BINDINGS: List[AbilityStatBinding] = [
        AbilityStatBinding(StatKey.STRATEGIC_MULT, 'movement_points', 'multiply', 'base_movement_points'),
    ]

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        self.base_movement_points = self._parse_primary_value(data)
        self.movement_points = self.base_movement_points

    def sync_data(self, data: Any):
        super().sync_data(data)
        self.base_movement_points = self._parse_primary_value(data)
        self.movement_points = self.base_movement_points

    def recalculate(self):
        self.movement_points = self.base_movement_points * self.get_effective_stat('strategic_mult', 1.0)

    def get_ui_rows(self) -> List[Dict[str, str]]:
        return [{'label': 'Strategic Mobility', 'value': f"{self.movement_points:.0f} MP", 'color_hint': '#6496FF'}]

    def get_primary_value(self) -> float:
        return self.movement_points


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
            {'label': 'Warp Capable', 'value': 'Yes', 'color_hint': '#00FFFF'},
            {'label': 'Max Tonnage', 'value': f'{self.max_tonnage:,.0f} kg', 'color_hint': '#FFFFFF'},
        ]
        if self.energy_cost > 0:
            rows.append({'label': 'Warp Energy', 'value': f'{self.energy_cost:,.0f}', 'color_hint': '#64C8FF'})
        return rows

    def get_primary_value(self) -> float:
        return self.max_tonnage
