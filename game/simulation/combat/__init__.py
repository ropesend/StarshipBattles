"""
Combat subsystem - extracted from ShipCombatEngine.

This package contains focused classes for combat operations:
- TargetingSystem: Target selection and firing solutions
- DamageCalculator: Damage application and absorption
- WeaponFiringSystem: Weapon firing and projectile creation
"""
from game.simulation.combat.targeting_system import TargetingSystem
from game.simulation.combat.damage_calculator import DamageCalculator
from game.simulation.combat.weapon_firing_system import WeaponFiringSystem

__all__ = [
    'TargetingSystem',
    'DamageCalculator',
    'WeaponFiringSystem',
]
