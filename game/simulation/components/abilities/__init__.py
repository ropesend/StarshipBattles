"""
Abilities package - Component ability classes and registry.

This package contains all ability classes that can be attached to components.
"""
import logging
from typing import Any, Optional

from game.core.exceptions import ValidationException, ComponentException

logger = logging.getLogger(__name__)

# Base class
from .base import Ability

# Colonization abilities
from .colonize import ColonizePlanet

# Resource abilities
from .resources import ResourceConsumption, ResourceStorage, ResourceGeneration

# Cargo abilities
from .cargo import CargoStorage

# Superweapon abilities
from .superweapons import (
    DestroyPlanet,
    DestroyStar,
    OpenWarpPoint,
    CloseWarpPoint,
    CreateDysonSphere,
    SelfDestruct,
)

# Propulsion abilities
from .propulsion import CombatPropulsion, ManeuveringThruster, StrategicMovement, WarpJump

# Defense abilities
from .defense import (
    ShieldProjection,
    ShieldRegeneration,
    ToHitAttackModifier,
    ToHitDefenseModifier,
    EmissiveArmor,
)

# Crew abilities
from .crew import CrewCapacity, LifeSupportCapacity, CrewRequired

# Marker abilities
from .markers import (
    VehicleLaunchAbility,
    CommandAndControl,
    RequiresCommandAndControl,
    RequiresCombatMovement,
    StructuralIntegrity,
)

# Weapon abilities
from .weapons import (
    WeaponAbility,
    ProjectileWeaponAbility,
    BeamWeaponAbility,
    SeekerWeaponAbility,
)

# Harvester and storage abilities
from .harvester import ResourceHarvesterAbility, SpaceShipyardAbility, LocalStorageAbility

# Planetary abilities (PROJ-237)
from .planetary import PlanetaryShieldAbility, StrategicResourceGenerationAbility

# --- Registry ---

ABILITY_REGISTRY = {
    "ColonizePlanet": ColonizePlanet,
    "ResourceConsumption": ResourceConsumption,
    "ResourceStorage": ResourceStorage,
    "ResourceGeneration": ResourceGeneration,
    "CombatPropulsion": CombatPropulsion,
    "ManeuveringThruster": ManeuveringThruster,
    "StrategicMovement": StrategicMovement,
    "WarpJump": WarpJump,
    "ShieldProjection": ShieldProjection,
    "ShieldRegeneration": ShieldRegeneration,
    "VehicleLaunch": VehicleLaunchAbility,
    "WeaponAbility": WeaponAbility,
    "ProjectileWeaponAbility": ProjectileWeaponAbility,
    "BeamWeaponAbility": BeamWeaponAbility,
    "SeekerWeaponAbility": SeekerWeaponAbility,
    "CommandAndControl": CommandAndControl,
    "CrewCapacity": CrewCapacity,
    "LifeSupportCapacity": LifeSupportCapacity,
    "CrewRequired": CrewRequired,
    "ToHitAttackModifier": ToHitAttackModifier,
    "ToHitDefenseModifier": ToHitDefenseModifier,
    "EmissiveArmor": EmissiveArmor,
    "Armor": lambda c, d: Ability(c, d),  # Dummy ability for tag/existence checks
    "RequiresCommandAndControl": RequiresCommandAndControl,
    "RequiresCombatMovement": RequiresCombatMovement,
    "StructuralIntegrity": StructuralIntegrity,
    "ResourceHarvester": ResourceHarvesterAbility,
    "SpaceShipyard": SpaceShipyardAbility,
    "LocalStorage": LocalStorageAbility,
    "CargoStorage": CargoStorage,
    # Planetary & strategic abilities (PROJ-237/238)
    "PlanetaryShield": PlanetaryShieldAbility,
    "StrategicResourceGeneration": StrategicResourceGenerationAbility,
    # Superweapon abilities
    "DestroyPlanet": DestroyPlanet,
    "DestroyStar": DestroyStar,
    "OpenWarpPoint": OpenWarpPoint,
    "CloseWarpPoint": CloseWarpPoint,
    "CreateDysonSphere": CreateDysonSphere,
    "SelfDestruct": SelfDestruct,
}



def create_ability(name: str, component, data: Any) -> Optional[Ability]:
    if name in ABILITY_REGISTRY:
        try:
            # Handle primitive shortcut inputs (e.g. "CombatPropulsion": 100)
            # passed as 'data'. Constructor must handle it, or we normalize here.
            # Our constructors above handle `isinstance(data, (int, float))` checks.
            return ABILITY_REGISTRY[name](component, data)
        except (TypeError, ValueError, KeyError, AttributeError, ValidationException, ComponentException) as e:
            logger.warning(f"Failed to create ability '{name}': {e}")
            return None
    return None


# Color constants for UI hints
from . import ui_colors

# Export all public names
__all__ = [
    # Color constants module
    'ui_colors',
    # Base
    'Ability',
    # Colonization
    'ColonizePlanet',
    # Resources
    'ResourceConsumption',
    'ResourceStorage',
    'ResourceGeneration',
    # Propulsion
    'CombatPropulsion',
    'ManeuveringThruster',
    'StrategicMovement',
    'WarpJump',
    # Defense
    'ShieldProjection',
    'ShieldRegeneration',
    'ToHitAttackModifier',
    'ToHitDefenseModifier',
    'EmissiveArmor',
    # Crew
    'CrewCapacity',
    'LifeSupportCapacity',
    'CrewRequired',
    # Markers
    'VehicleLaunchAbility',
    'CommandAndControl',
    'RequiresCommandAndControl',
    'RequiresCombatMovement',
    'StructuralIntegrity',
    # Weapons
    'WeaponAbility',
    'ProjectileWeaponAbility',
    'BeamWeaponAbility',
    'SeekerWeaponAbility',
    # Harvester and storage
    'ResourceHarvesterAbility',
    'SpaceShipyardAbility',
    'LocalStorageAbility',
    # Cargo
    'CargoStorage',
    # Planetary & strategic (PROJ-237/238)
    'PlanetaryShieldAbility',
    'StrategicResourceGenerationAbility',
    # Superweapons
    'DestroyPlanet',
    'DestroyStar',
    'OpenWarpPoint',
    'CloseWarpPoint',
    'CreateDysonSphere',
    'SelfDestruct',
    # Registry
    'ABILITY_REGISTRY',
    'create_ability',
]
