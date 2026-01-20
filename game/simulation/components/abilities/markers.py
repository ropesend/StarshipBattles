from typing import Dict, Any, List

from game.core.config import PhysicsConfig
from .base import Ability
from .stat_keys import StatKey, AbilityStatBinding


class VehicleLaunchAbility(Ability):
    """Allows storing and launching fighters."""

    STAT_BINDINGS: List[AbilityStatBinding] = [
        AbilityStatBinding(StatKey.CAPACITY_MULT, 'capacity', 'multiply', '_base_capacity'),
    ]

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        self.fighter_class = data.get('fighter_class', 'Fighter (Small)')
        self.capacity = data.get('capacity', 0)
        self._base_capacity = self.capacity
        self.cycle_time = data.get('cycle_time', 5.0)
        self.cooldown = 0.0

    def recalculate(self):
        # Apply capacity mult
        self.capacity = int(self._base_capacity * self.get_effective_stat('capacity_mult', 1.0))

    def update(self) -> bool:
        if self.cooldown > 0:
            self.cooldown -= PhysicsConfig.TICK_RATE
        return True

    def try_launch(self):
        if self.cooldown <= 0:
            self.cooldown = self.cycle_time
            return True
        return False

    def get_ui_rows(self):
        return [
            {'label': 'Hangar', 'value': f"{self.fighter_class}", 'color_hint': '#C8C8C8'},
            {'label': 'Cycle', 'value': f"{self.cycle_time}s", 'color_hint': '#C8C8C8'}
        ]

    def get_primary_value(self) -> float:
        return float(self.capacity)


class CommandAndControl(Ability):
    """Marks component as providing ship command capability."""

    STAT_BINDINGS: List[AbilityStatBinding] = []  # Marker ability

    def get_ui_rows(self):
        return [{'label': 'Command', 'value': 'Active', 'color_hint': '#96FF96'}]

    def get_primary_value(self) -> float:
        return 1.0


class RequiresCommandAndControl(Ability):
    """Marker ability: Component (e.g. Hull) requires Command and Control to be operational."""

    STAT_BINDINGS: List[AbilityStatBinding] = []  # Marker ability

    def get_ui_rows(self):
        return [{'label': 'Requires C&C', 'value': 'Yes', 'color_hint': '#FFCC66'}]

    def get_primary_value(self) -> float:
        return 1.0


class RequiresCombatMovement(Ability):
    """Marker ability: Component (e.g. Hull) requires Combat Propulsion to be operational."""

    STAT_BINDINGS: List[AbilityStatBinding] = []  # Marker ability

    def get_ui_rows(self):
        return [{'label': 'Requires Propulsion', 'value': 'Yes', 'color_hint': '#FFCC66'}]

    def get_primary_value(self) -> float:
        return 1.0


class StructuralIntegrity(Ability):
    """Marker ability: Hull provides structural integrity for the ship."""

    STAT_BINDINGS: List[AbilityStatBinding] = []  # Marker ability

    def get_ui_rows(self):
        return [{'label': 'Structural Integrity', 'value': 'Yes', 'color_hint': '#96FF96'}]
