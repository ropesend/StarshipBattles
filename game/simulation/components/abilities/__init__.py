"""
Abilities package - Component ability classes and registry.

This package contains all ability classes that can be attached to components.
"""

from typing import Any, Optional

# Base class
from .base import Ability

# Resource abilities
from .resources import ResourceConsumption, ResourceStorage, ResourceGeneration

# Propulsion abilities
from .propulsion import CombatPropulsion, ManeuveringThruster

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

# --- Registry ---

ABILITY_REGISTRY = {
    "ResourceConsumption": ResourceConsumption,
    "ResourceStorage": ResourceStorage,
    "ResourceGeneration": ResourceGeneration,
    "CombatPropulsion": CombatPropulsion,
    "ManeuveringThruster": ManeuveringThruster,
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
    # Primitive/Shortcut Factories
    "FuelStorage": lambda c, d: ResourceStorage(c, {"resource": "fuel", "amount": d} if isinstance(d, (int, float)) else {**d, "resource": "fuel"}),
    "EnergyStorage": lambda c, d: ResourceStorage(c, {"resource": "energy", "amount": d} if isinstance(d, (int, float)) else {**d, "resource": "energy"}),
    "AmmoStorage": lambda c, d: ResourceStorage(c, {"resource": "ammo", "amount": d} if isinstance(d, (int, float)) else {**d, "resource": "ammo"}),
    "EnergyGeneration": lambda c, d: ResourceGeneration(c, {"resource": "energy", "amount": d} if isinstance(d, (int, float)) else {**d, "resource": "energy"}),
    "EnergyConsumption": lambda c, d: ResourceConsumption(c, {"resource": "energy", "amount": d, "trigger": "constant"} if isinstance(d, (int, float)) else {**d, "resource": "energy"}),
    "AmmoConsumption": lambda c, d: ResourceConsumption(c, {"resource": "ammo", "amount": d, "trigger": "activation"} if isinstance(d, (int, float)) else {**d, "resource": "ammo"})
}

# Map registry shortcut names to their actual class names for instance matching
ABILITY_CLASS_MAP = {
    "FuelStorage": "ResourceStorage",
    "EnergyStorage": "ResourceStorage",
    "AmmoStorage": "ResourceStorage",
    "EnergyGeneration": "ResourceGeneration",
    "EnergyConsumption": "ResourceConsumption",
    "AmmoConsumption": "ResourceConsumption",
}


def create_ability(name: str, component, data: Any) -> Optional[Ability]:
    if name in ABILITY_REGISTRY:
        try:
            # Handle primitive shortcut inputs (e.g. "CombatPropulsion": 100)
            # passed as 'data'. Constructor must handle it, or we normalize here.
            # Our constructors above handle `isinstance(data, (int, float))` checks.
            return ABILITY_REGISTRY[name](component, data)
        except Exception:
            return None
    return None


# Export all public names
__all__ = [
    # Base
    'Ability',
    # Resources
    'ResourceConsumption',
    'ResourceStorage',
    'ResourceGeneration',
    # Propulsion
    'CombatPropulsion',
    'ManeuveringThruster',
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
    # Registry
    'ABILITY_REGISTRY',
    'ABILITY_CLASS_MAP',
    'create_ability',
]
