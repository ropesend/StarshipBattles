"""
Simulation layer interfaces and protocols.

This package defines interfaces (protocols) that the simulation layer uses
for dependency injection, loose coupling with other layers, and type-safe
duck typing replacement.

PROJ-190: Added ability, component, and entity protocols to eliminate
duck typing (hasattr/getattr) patterns across the simulation layer.

Usage:
    from game.simulation.interfaces import (
        # AI Controller interfaces
        IAIController, IAIControllerFactory,

        # Ability protocols
        IAbility, IWeaponAbility, IBeamWeaponAbility, ISeekerWeaponAbility,
        IProjectileWeaponAbility, IResourceConsumptionAbility,
        IResourceStorageAbility, IResourceGenerationAbility, IWarpJumpAbility,

        # Component protocols
        IComponent,

        # Entity protocols
        ICombatShip, IProjectile, IPhysicsShip, ISerializableShip,

        # TypeGuard functions
        is_ability, is_weapon, is_beam_weapon, is_seeker_weapon,
        is_projectile_weapon, is_resource_consumption, is_resource_storage,
        is_resource_generation, is_warp_jump,
        is_component,
        is_combat_ship, is_projectile, is_physics_ship,
        is_serializable_ship,
    )

    # Example: Type-safe ability checking
    if is_weapon(ability):
        print(ability.damage)  # IDE knows ability has .damage

C#/Rust Portability:
    Python protocols map directly to interfaces/traits:
    - IAbility -> interface IAbility / trait Ability
    - isinstance(x, IAbility) -> x is IAbility / x.downcast_ref::<dyn Ability>()
"""

# AI Controller interfaces (existing)
from game.simulation.interfaces.ai_controller import IAIController, IAIControllerFactory

# Ability protocols (PROJ-190)
from game.simulation.interfaces.ability_protocols import (
    IAbility,
    IResourceConsumptionAbility,
    IResourceStorageAbility,
    IResourceGenerationAbility,
    IWeaponAbility,
    IBeamWeaponAbility,
    ISeekerWeaponAbility,
    IProjectileWeaponAbility,
    IWarpJumpAbility,
    # TypeGuard functions
    is_ability,
    is_resource_consumption,
    is_resource_storage,
    is_resource_generation,
    is_weapon,
    is_beam_weapon,
    is_seeker_weapon,
    is_projectile_weapon,
    is_warp_jump,
)

# Component protocols (PROJ-190)
from game.simulation.interfaces.component_protocols import (
    IComponent,
    is_component,
)

# Entity protocols (PROJ-190)
from game.simulation.interfaces.entity_protocols import (
    ICombatShip,
    IProjectile,
    IPhysicsShip,
    ISerializableShip,
    # TypeGuard functions
    is_combat_ship,
    is_projectile,
    is_physics_ship,
    is_serializable_ship,
)

__all__ = [
    # AI Controller interfaces
    'IAIController',
    'IAIControllerFactory',
    # Ability protocols
    'IAbility',
    'IResourceConsumptionAbility',
    'IResourceStorageAbility',
    'IResourceGenerationAbility',
    'IWeaponAbility',
    'IBeamWeaponAbility',
    'ISeekerWeaponAbility',
    'IProjectileWeaponAbility',
    'IWarpJumpAbility',
    # Ability TypeGuards
    'is_ability',
    'is_resource_consumption',
    'is_resource_storage',
    'is_resource_generation',
    'is_weapon',
    'is_beam_weapon',
    'is_seeker_weapon',
    'is_projectile_weapon',
    'is_warp_jump',
    # Component protocols
    'IComponent',
    'is_component',
    # Entity protocols
    'ICombatShip',
    'IProjectile',
    'IPhysicsShip',
    'ISerializableShip',
    # Entity TypeGuards
    'is_combat_ship',
    'is_projectile',
    'is_physics_ship',
    'is_serializable_ship',
]
