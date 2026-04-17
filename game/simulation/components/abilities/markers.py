from typing import Dict, Any, List

from game.core.config import PhysicsConfig
from .base import Ability
from .stat_keys import StatKey, AbilityStatBinding
from .ui_colors import HINT_NEUTRAL, HINT_CREW_CAP, HINT_REQUIREMENT


class VehicleLaunchAbility(Ability):
    """Allows storing and launching fighters."""

    STAT_BINDINGS: List[AbilityStatBinding] = [
        AbilityStatBinding(StatKey.CAPACITY_MULT, 'capacity', 'multiply', '_base_capacity'),
    ]

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        self.cooldown = 0.0  # runtime state, NOT data-derived

    def _parse_attrs(self, data: Any) -> None:
        """Parse data attributes; called from __init__ and sync_data so
        formula-driven attributes refresh on data updates."""
        if not isinstance(data, dict):
            data = {}
        self.fighter_class = data.get('fighter_class', 'Fighter (Small)')
        self.capacity = data.get('capacity', 0)
        self._base_capacity = self.capacity
        self.cycle_time = data.get('cycle_time', 5.0)

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
            {'label': 'Hangar', 'value': f"{self.fighter_class}", 'color_hint': HINT_NEUTRAL},
            {'label': 'Cycle', 'value': f"{self.cycle_time}s", 'color_hint': HINT_NEUTRAL}
        ]

    def get_primary_value(self) -> float:
        return float(self.capacity)


class CommandAndControl(Ability):
    """Marks component as providing ship command capability."""

    STAT_BINDINGS: List[AbilityStatBinding] = []  # Marker ability

    def get_ui_rows(self):
        return [{'label': 'Command', 'value': 'Active', 'color_hint': HINT_CREW_CAP}]

    def get_primary_value(self) -> float:
        return 1.0


class RequiresCommandAndControl(Ability):
    """Component requires an operational CommandAndControl provider on the ship.

    When update() is called each tick, checks if the ship has at least one
    active component with the CommandAndControl ability. Returns False if
    not found, which marks this component as non-operational (its stats
    won't contribute to the ship).
    """

    STAT_BINDINGS: List[AbilityStatBinding] = []

    def update(self, resources=None) -> bool:
        """Check if ship has an active C&C provider. Returns False if not."""
        comp = self.component
        if comp is None or comp.ship is None:
            return True  # No ship context yet, assume OK
        ship = comp.ship
        # Check for any active CommandAndControl provider on the ship.
        # Uses is_active (not is_operational) to avoid circular dependency:
        # checking operational status would trigger another C&C check.
        for layer_data in ship.layers.values():
            for c in layer_data.components:
                if c is comp:
                    continue
                if not c.is_active:
                    continue
                if c.has_ability('CommandAndControl'):
                    return True
        return False

    def get_ui_rows(self):
        return [{'label': 'Requires C&C', 'value': 'Yes', 'color_hint': HINT_REQUIREMENT}]

    def get_primary_value(self) -> float:
        return 1.0


class RequiresCombatMovement(Ability):
    """Marker ability: Component (e.g. Hull) requires Combat Propulsion to be operational."""

    STAT_BINDINGS: List[AbilityStatBinding] = []  # Marker ability

    def get_ui_rows(self):
        return [{'label': 'Requires Propulsion', 'value': 'Yes', 'color_hint': HINT_REQUIREMENT}]

    def get_primary_value(self) -> float:
        return 1.0


class StructuralIntegrity(Ability):
    """Marker ability: Hull provides structural integrity for the ship."""

    STAT_BINDINGS: List[AbilityStatBinding] = []  # Marker ability

    def get_ui_rows(self):
        return [{'label': 'Structural Integrity', 'value': 'Yes', 'color_hint': HINT_CREW_CAP}]
