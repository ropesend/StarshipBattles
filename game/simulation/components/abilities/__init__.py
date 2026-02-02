"""
Abilities package - Component ability classes and registry.

This package contains all ability classes that can be attached to components.
"""

from typing import Any, Optional
from game.core.logger import log_warning

# Base class
from .base import Ability

# Colonization abilities
from .colonize import ColonizePlanet

# Resource abilities
from .resources import ResourceConsumption, ResourceStorage, ResourceGeneration

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

# Harvester abilities
from .harvester import ResourceHarvesterAbility, SpaceShipyardAbility

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
}

# Map registry shortcut names to their actual class names for instance matching
# (Legacy shortcuts removed - use ResourceStorage/ResourceConsumption/ResourceGeneration directly)
ABILITY_CLASS_MAP = {}


def create_ability(name: str, component, data: Any) -> Optional[Ability]:
    if name in ABILITY_REGISTRY:
        try:
            # Handle primitive shortcut inputs (e.g. "CombatPropulsion": 100)
            # passed as 'data'. Constructor must handle it, or we normalize here.
            # Our constructors above handle `isinstance(data, (int, float))` checks.
            return ABILITY_REGISTRY[name](component, data)
        except Exception as e:
            log_warning(f"Failed to create ability '{name}': {e}")
            return None
    return None


# Export all public names
__all__ = [
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
    # Harvester
    'ResourceHarvesterAbility',
    'SpaceShipyardAbility',
    # Registry
    'ABILITY_REGISTRY',
    'ABILITY_CLASS_MAP',
    'create_ability',
]
