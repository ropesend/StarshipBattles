"""
Design roles — classification labels for vehicle designs.

Roles are assigned at design time in the workshop. They drive
auto-suggestion for fleet organization and UI grouping but have no direct
combat behavior effect.

Role definitions are loaded from data/design_roles.json. Each role
specifies which vehicle types it can be applied to.

Individual ShipInstances can override their design role via role_override.
"""

import logging
from enum import Enum
from typing import Dict, Any, List, Optional

from game.core.json_utils import load_json
from game.core.paths import Paths

logger = logging.getLogger(__name__)


class DesignRole(Enum):
    """Classification label for a ship design.

    Roles indicate what a ship is designed to do. They are used for:
    - Auto-suggesting fleet task group assignments
    - UI grouping and display
    - Fleet organization suggestions

    They do NOT directly affect combat behavior (that's the policy system).
    """

    # Combat roles
    LINE_COMBATANT = "line_combatant"
    FLEET_ESCORT = "fleet_escort"
    INTERCEPTOR = "interceptor"
    ASSAULT_SHIP = "assault_ship"
    MISSILE_PLATFORM = "missile_platform"
    RAIDER = "raider"

    # Support roles
    CARRIER = "carrier"
    SUPPORT_SHIP = "support_ship"
    SCOUT = "scout"
    COMMAND_SHIP = "command_ship"


# Ability names used for classification
_WEAPON_ABILITIES = {"BeamWeaponAbility", "ProjectileWeaponAbility", "SeekerWeaponAbility"}
_SEEKER_ABILITIES = {"SeekerWeaponAbility"}
_BEAM_PROJECTILE_ABILITIES = {"BeamWeaponAbility", "ProjectileWeaponAbility"}
_SENSOR_ABILITIES = {"SensorAbility", "ECMAbility"}
_SUPPORT_ABILITIES = {"ShipRepair", "SpaceShipyard", "ResourceGeneration"}
_CARRIER_ABILITIES = {"VehicleLaunch"}
_COMMAND_ABILITIES = {"TacticalDataLinkAbility"}

# Mass thresholds for light/heavy classification
_LIGHT_SHIP_MASS = 4000   # Escort, Frigate, Destroyer
_HEAVY_SHIP_MASS = 16000  # Battle Cruiser and above


def classify_design_role(
    abilities: Dict[str, Any],
    mass: float = 0,
) -> DesignRole:
    """Classify a ship design into a role based on its abilities and mass.

    Examines the set of ability names present on the design and applies
    priority-ordered rules to determine the best-fit role.

    Args:
        abilities: Dict mapping ability name -> value (from all components).
            Only the keys matter for classification.
        mass: Ship mass for light/heavy distinction.

    Returns:
        The classified DesignRole.
    """
    ability_names = set(abilities.keys())

    # Priority 1: Carrier (has fighter launch capability)
    if ability_names & _CARRIER_ABILITIES:
        return DesignRole.CARRIER

    # Priority 2: Support Ship (repair, shipyard, or resource generation)
    if ability_names & _SUPPORT_ABILITIES:
        return DesignRole.SUPPORT_SHIP

    # Priority 3: Command Ship (has tactical data link + C&C on a heavy hull)
    if ability_names & _COMMAND_ABILITIES and "CommandAndControl" in ability_names:
        if mass >= _HEAVY_SHIP_MASS:
            return DesignRole.COMMAND_SHIP

    # Priority 4: Missile Platform (seeker weapons, no beam/projectile)
    has_seekers = bool(ability_names & _SEEKER_ABILITIES)
    has_direct_weapons = bool(ability_names & _BEAM_PROJECTILE_ABILITIES)
    if has_seekers and not has_direct_weapons:
        return DesignRole.MISSILE_PLATFORM

    # Priority 5: Scout (sensors/ECM emphasis, no weapons, light hull)
    has_weapons = bool(ability_names & _WEAPON_ABILITIES)
    has_sensors = bool(ability_names & _SENSOR_ABILITIES)
    if has_sensors and not has_weapons and mass <= _LIGHT_SHIP_MASS:
        return DesignRole.SCOUT

    # Priority 6: Armed ships — classify by mass
    if has_weapons:
        if mass <= _LIGHT_SHIP_MASS:
            return DesignRole.FLEET_ESCORT
        else:
            return DesignRole.LINE_COMBATANT

    # Default: Line Combatant
    return DesignRole.LINE_COMBATANT


def classify_from_design_data(
    design_data: Dict[str, Any],
    component_registry: Dict[str, Any],
) -> DesignRole:
    """Classify a role from full design data using the component registry.

    Iterates all components in the design, collects their abilities,
    then delegates to classify_design_role().

    Args:
        design_data: Full ship design dict (with 'layers' containing components).
        component_registry: Dict mapping component_id -> component definition
            (with 'abilities' sub-dict).

    Returns:
        The classified DesignRole.
    """
    all_abilities: Dict[str, Any] = {}
    total_mass = 0

    layers = design_data.get("layers", {})
    for layer_name, components in layers.items():
        for comp_entry in components:
            comp_id = comp_entry.get("id") if isinstance(comp_entry, dict) else comp_entry
            comp_def = component_registry.get(comp_id, {})
            abilities = comp_def.get("abilities", {})
            for ab_name, ab_value in abilities.items():
                if not ab_name.startswith("_"):
                    all_abilities[ab_name] = ab_value

            comp_mass = comp_def.get("mass", 0)
            if isinstance(comp_mass, (int, float)):
                total_mass += comp_mass

    return classify_design_role(abilities=all_abilities, mass=total_mass)


# =============================================================================
# Data-Driven Role Registry (loaded from JSON)
# =============================================================================

class DesignRoleRegistry:
    """Registry of design roles loaded from data/design_roles.json.

    Provides role definitions with vehicle type filtering for the UI.
    """

    def __init__(self):
        self._roles: Dict[str, Dict[str, Any]] = {}
        self._loaded = False

    def load(self, file_path: Optional[str] = None) -> None:
        """Load role definitions from JSON.

        Args:
            file_path: Path to design_roles.json. Defaults to Paths constant.
        """
        if file_path is None:
            file_path = Paths.DESIGN_ROLES_FILE

        data = load_json(file_path, default={})
        self._roles = data.get("roles", {})
        self._loaded = True

        logger.info(f"DesignRoleRegistry loaded: {len(self._roles)} roles")

    def ensure_loaded(self) -> None:
        """Load if not already loaded."""
        if not self._loaded:
            self.load()

    def get_roles_for_vehicle_type(self, vehicle_type: str) -> List[Dict[str, Any]]:
        """Get roles allowed for a given vehicle type.

        Args:
            vehicle_type: e.g. "Ship", "Planetary Complex", "Satellite"

        Returns:
            List of role dicts with 'id', 'name', 'description' keys,
            sorted by name. Only includes roles that allow this vehicle type.
        """
        self.ensure_loaded()
        result = []
        for role_id, role_def in self._roles.items():
            allowed = role_def.get("allowed_vehicle_types", [])
            if vehicle_type in allowed:
                result.append({
                    "id": role_id,
                    "name": role_def.get("name", role_id),
                    "description": role_def.get("description", ""),
                })
        result.sort(key=lambda r: r["name"])
        return result

    def get_role_name(self, role_id: str) -> str:
        """Get the display name for a role ID.

        Returns the role_id itself if not found.
        """
        self.ensure_loaded()
        role_def = self._roles.get(role_id)
        if role_def:
            return role_def.get("name", role_id)
        return role_id

    def get_role_id_by_name(self, display_name: str) -> Optional[str]:
        """Find a role ID from its display name.

        Returns None if no match found.
        """
        self.ensure_loaded()
        for role_id, role_def in self._roles.items():
            if role_def.get("name") == display_name:
                return role_id
        return None

    def get_all_role_ids(self) -> List[str]:
        """Get all role IDs."""
        self.ensure_loaded()
        return list(self._roles.keys())


# Module-level singleton
_default_registry: Optional[DesignRoleRegistry] = None


def get_default_design_role_registry() -> DesignRoleRegistry:
    """Get the module-level DesignRoleRegistry, auto-creating on first access."""
    global _default_registry
    if _default_registry is None:
        _default_registry = DesignRoleRegistry()
    return _default_registry
