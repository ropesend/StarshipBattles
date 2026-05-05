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
    ShieldRegeneratingArmor,
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
    # PROJ-367 Phase 1: typed classes for previously-untyped abilities.
    MultiplexTrackingAbility,
    VehicleStorageAbility,
    PodStorageAbility,
)

# Weapon abilities
from .weapons import (
    WeaponAbility,
    ProjectileWeaponAbility,
    BeamWeaponAbility,
    SeekerWeaponAbility,
)

# Harvester and storage abilities
from .harvester import ResourceHarvesterAbility, SpaceShipyardAbility, LocalStorageAbility, PlanetaryYardAbility, StagingYardAbility

# Planetary abilities (PROJ-237)
from .planetary import (
    PlanetaryShieldAbility, StrategicResourceGenerationAbility,
    GeologicStabilizerAbility, StellarStabilizerAbility, WarpFieldStabilizerAbility,
    ResourceHarvestBoosterAbility, BuildRateBoosterAbility,
    AtmosphereModifierAbility, QualityImprovementAbility,
    ShieldModifierAbility, DamageModifierAbility,
    GravityModifierAbility, WaterModifierAbility, RadiationShieldAbility,
    # PROJ-300 environmental abilities
    ThrustModifierAbility, StrategicSpeedModifierAbility,
    EnvironmentalDamageAbility, FuelDrainAbility,
)

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
    # PROJ-367 Phase 1: typed classes for previously-untyped abilities.
    "MultiplexTracking": MultiplexTrackingAbility,
    "VehicleStorage": VehicleStorageAbility,
    "PodStorage": PodStorageAbility,
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
    "ShieldRegeneratingArmor": ShieldRegeneratingArmor,
    "Armor": lambda c, d: Ability(c, d),  # Dummy ability for tag/existence checks
    "RequiresCommandAndControl": RequiresCommandAndControl,
    "RequiresCombatMovement": RequiresCombatMovement,
    "StructuralIntegrity": StructuralIntegrity,
    "ResourceHarvester": ResourceHarvesterAbility,
    "SpaceShipyard": SpaceShipyardAbility,
    "PlanetaryYard": PlanetaryYardAbility,
    "StagingYard": StagingYardAbility,
    "LocalStorage": LocalStorageAbility,
    "CargoStorage": CargoStorage,
    # Planetary & strategic abilities (PROJ-237/238)
    "PlanetaryShield": PlanetaryShieldAbility,
    "StrategicResourceGeneration": StrategicResourceGenerationAbility,
    "GeologicStabilizer": GeologicStabilizerAbility,
    "StellarStabilizer": StellarStabilizerAbility,
    "WarpFieldStabilizer": WarpFieldStabilizerAbility,
    "ResourceHarvestBooster": ResourceHarvestBoosterAbility,
    "BuildRateBooster": BuildRateBoosterAbility,
    "AtmosphereModifier": AtmosphereModifierAbility,
    "QualityImprovement": QualityImprovementAbility,
    "ShieldModifier": ShieldModifierAbility,
    "DamageModifier": DamageModifierAbility,
    "GravityModifier": GravityModifierAbility,
    "WaterModifier": WaterModifierAbility,
    "RadiationShield": RadiationShieldAbility,
    # PROJ-300 environmental / storm-style abilities
    "ThrustModifier": ThrustModifierAbility,
    "StrategicSpeedModifier": StrategicSpeedModifierAbility,
    "EnvironmentalDamage": EnvironmentalDamageAbility,
    "FuelDrain": FuelDrainAbility,
    # Superweapon abilities
    "DestroyPlanet": DestroyPlanet,
    "DestroyStar": DestroyStar,
    "OpenWarpPoint": OpenWarpPoint,
    "CloseWarpPoint": CloseWarpPoint,
    "CreateDysonSphere": CreateDysonSphere,
    "SelfDestruct": SelfDestruct,
}



def _contains_unevaluated_formula(data: Any) -> bool:
    """Detect whether `data` contains any unevaluated formula strings (starting with '=').

    Component definitions in the registry may have formula strings like
    '=ship_class_mass' that cannot be evaluated until a ship context exists.
    Attempting to construct an ability from such data will raise; we'd rather
    skip silently and let the ability be instantiated later when formulas
    resolve to numbers.
    """
    if isinstance(data, str):
        return data.startswith('=')
    if isinstance(data, dict):
        return any(_contains_unevaluated_formula(v) for v in data.values())
    if isinstance(data, list):
        return any(_contains_unevaluated_formula(v) for v in data)
    return False


def create_ability(name: str, component, data: Any) -> Optional[Ability]:
    if name not in ABILITY_REGISTRY:
        return None
    try:
        # Handle primitive shortcut inputs (e.g. "CombatPropulsion": 100)
        # passed as 'data'. Constructor must handle it, or we normalize here.
        # Our constructors above handle `isinstance(data, (int, float))` checks.
        return ABILITY_REGISTRY[name](component, data)
    except (TypeError, ValueError, KeyError, AttributeError, ValidationException, ComponentException) as e:
        # If the failure was due to unevaluated formula strings in the data
        # (typical at registry-load time for components with =ship_class_mass
        # formulas), skip silently. The ability will be instantiated later by
        # ComponentStatsCalculator.recalculate once the component is attached
        # to a ship and formulas resolve to numbers. Only genuine
        # misconfiguration (bad scope, malformed data without formulas) still
        # logs a warning so it's visible.
        if _contains_unevaluated_formula(data):
            return None
        logger.warning(f"Failed to create ability '{name}': {e}")
        return None


def get_ability_default_scope(ability_name: str) -> str:
    """Resolve the class-level `default_scope` for an ability by name.

    Mirrors the runtime behavior of `Ability._parse_scope`: when JSON data
    omits `scope`, the runtime falls back to the ability class's
    `default_scope`. Compilers and collectors that pre-compute scope for
    routing must use THIS helper (not a hardcoded "self" fallback) to
    agree with the runtime.

    PROJ-272 Phase 1: fixes compiler/runtime disagreement that silently
    dropped complexes whose author forgot to specify `scope` on
    ShieldModifier/DamageModifier abilities (class default ALLIED_SYSTEM).

    Args:
        ability_name: Registry key (e.g., "ShieldModifier", "DamageModifier").

    Returns:
        String scope value (e.g., "allied_system"). Falls back to "self"
        for unknown abilities, logging a warning once per name.
    """
    ability_cls = ABILITY_REGISTRY.get(ability_name)
    if ability_cls is None:
        logger.warning(
            "get_ability_default_scope: unknown ability %r in registry; "
            "falling back to 'self'.", ability_name,
        )
        return "self"
    default = getattr(ability_cls, 'default_scope', None)
    if default is None:
        return "self"
    return default.value if hasattr(default, 'value') else str(default)


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
    # PROJ-367 Phase 1
    'MultiplexTrackingAbility',
    'VehicleStorageAbility',
    'PodStorageAbility',
    # Weapons
    'WeaponAbility',
    'ProjectileWeaponAbility',
    'BeamWeaponAbility',
    'SeekerWeaponAbility',
    # Harvester and storage
    'ResourceHarvesterAbility',
    'SpaceShipyardAbility',
    'PlanetaryYardAbility',
    'StagingYardAbility',
    'LocalStorageAbility',
    # Cargo
    'CargoStorage',
    # Planetary & strategic (PROJ-237/238)
    'PlanetaryShieldAbility',
    'StrategicResourceGenerationAbility',
    'GeologicStabilizerAbility',
    'StellarStabilizerAbility',
    'WarpFieldStabilizerAbility',
    'ResourceHarvestBoosterAbility',
    'BuildRateBoosterAbility',
    'AtmosphereModifierAbility',
    'QualityImprovementAbility',
    'ShieldModifierAbility',
    'DamageModifierAbility',
    'GravityModifierAbility',
    'WaterModifierAbility',
    'RadiationShieldAbility',
    # PROJ-300 environmental abilities
    'ThrustModifierAbility',
    'StrategicSpeedModifierAbility',
    'EnvironmentalDamageAbility',
    'FuelDrainAbility',
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
