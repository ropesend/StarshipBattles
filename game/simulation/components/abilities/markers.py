from typing import Dict, Any, List

from .base import Ability
from .stat_keys import AbilityStatBinding
from .ui_colors import HINT_NEUTRAL, HINT_CREW_CAP, HINT_REQUIREMENT


# PROJ-FMS-C audit Fix 1: ``VehicleLaunchAbility`` removed.
# The legacy class-string fighter launch path was replaced by
# :class:`game.simulation.components.abilities.launch.TacticalFighterLaunchAbility`
# (PROJ-FMS-A Phase 5) plus :class:`game.simulation.components.abilities.launch.StrategicFighterLaunchAbility`
# for strategic-layer launches. The production caller is
# :class:`game.ai.carrier_controller.CarrierAIController` (auto-launch) and
# the strategic-layer :class:`LaunchFightersCommandHandler`.


class CommandAndControl(Ability):
    """Marks component as providing ship command capability."""

    STAT_BINDINGS: List[AbilityStatBinding] = []  # Marker ability

    def get_ui_rows(self) -> List[Dict[str, Any]]:
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

    def get_ui_rows(self) -> List[Dict[str, Any]]:
        return [{'label': 'Requires C&C', 'value': 'Yes', 'color_hint': HINT_REQUIREMENT}]

    def get_primary_value(self) -> float:
        return 1.0


class RequiresCombatMovement(Ability):
    """Marker ability: Component (e.g. Hull) requires Combat Propulsion to be operational."""

    STAT_BINDINGS: List[AbilityStatBinding] = []  # Marker ability

    def get_ui_rows(self) -> List[Dict[str, Any]]:
        return [{'label': 'Requires Propulsion', 'value': 'Yes', 'color_hint': HINT_REQUIREMENT}]

    def get_primary_value(self) -> float:
        return 1.0


class StructuralIntegrity(Ability):
    """Marker ability: Hull provides structural integrity for the ship."""

    STAT_BINDINGS: List[AbilityStatBinding] = []  # Marker ability

    def get_ui_rows(self) -> List[Dict[str, Any]]:
        return [{'label': 'Structural Integrity', 'value': 'Yes', 'color_hint': HINT_CREW_CAP}]


# ---------------------------------------------------------------------------
# PROJ-367 Phase 1: typed ability classes for previously-untyped abilities.
#
# These three classes replace `comp.abilities.get("MultiplexTracking"/"VehicleStorage"/"PodStorage", ...)`
# raw-dict reads in the Phase-3 stat-aggregation path. The `Armor` ability
# stays exclusively `has_ability`-based (marker idiom).
# ---------------------------------------------------------------------------


class MultiplexTrackingAbility(Ability):
    """Tracking-multiplex ability — increases ``ship.max_targets``.

    Production data shape is a scalar (e.g. ``"MultiplexTracking": 10``);
    a dict shape (``{"slots": 10}``) is also accepted as a forward-compat
    hedge. PROJ-367 Phase 1 (closes EXT-07).
    """

    STAT_BINDINGS: List[AbilityStatBinding] = []  # No multiplier — direct read.

    def _parse_attrs(self, data: Any) -> None:
        """Parse `slots` from scalar or dict data."""
        if isinstance(data, dict):
            self.slots = int(data.get('slots', 0))
        elif isinstance(data, (int, float)):
            self.slots = int(data)
        else:
            self.slots = 0

    def get_primary_value(self) -> float:
        return float(self.slots)

    def get_ui_rows(self) -> List[Dict[str, Any]]:
        return [{'label': 'Targets', 'value': str(self.slots), 'color_hint': HINT_NEUTRAL}]


class VehicleStorageAbility(Ability):
    """Vehicle (fighter) storage capacity — additive into ``ship.fighter_capacity``.

    Production data shape is a scalar (e.g. ``"VehicleStorage": 50``); dict
    shape (``{"capacity": 50}``) is accepted as a forward-compat hedge.
    PROJ-367 Phase 1 (closes EXT-07).

    No STAT_BINDINGS — storage is additive, not modifier-scaled.
    """

    STAT_BINDINGS: List[AbilityStatBinding] = []

    def _parse_attrs(self, data: Any) -> None:
        if isinstance(data, dict):
            self.capacity = int(data.get('capacity', 0))
        elif isinstance(data, (int, float)):
            self.capacity = int(data)
        else:
            self.capacity = 0

    def get_primary_value(self) -> float:
        return float(self.capacity)

    def get_ui_rows(self) -> List[Dict[str, Any]]:
        return [{'label': 'Vehicle Storage', 'value': str(self.capacity), 'color_hint': HINT_NEUTRAL}]


class PodStorageAbility(Ability):
    """Pod (colony / drop pod) mass-capacity — additive into ``ship.pod_storage_mass``.

    Production data shape is a dict (``{"capacity_mass": 5000}``, see
    ``data/components.json:2396-2397``); a scalar shape is also accepted.
    Single attribute only — no ``pod_class``. PROJ-367 Phase 1 (closes
    EXT-07; verified at ``docs/systems/ability_reference.md:768-786``).
    """

    STAT_BINDINGS: List[AbilityStatBinding] = []

    def _parse_attrs(self, data: Any) -> None:
        if isinstance(data, dict):
            self.capacity_mass = float(data.get('capacity_mass', 0.0))
        elif isinstance(data, (int, float)):
            self.capacity_mass = float(data)
        else:
            self.capacity_mass = 0.0

    def get_primary_value(self) -> float:
        return float(self.capacity_mass)

    def get_ui_rows(self) -> List[Dict[str, Any]]:
        return [{'label': 'Pod Capacity', 'value': f"{self.capacity_mass:g} mass", 'color_hint': HINT_NEUTRAL}]
