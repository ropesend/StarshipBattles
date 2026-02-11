"""
Strategy Layer Validation Module

PROJ-36: Centralized validation for fleet orders.
PROJ-68: Added TransferValidator for cargo operations.
PROJ-102: Added SuperweaponValidator for superweapon orders.

Usage:
    from game.strategy.validation import ColonizeValidator, TransferValidator, SuperweaponValidator
    result = ColonizeValidator.validate(galaxy, fleet, target_planet)
    result = TransferValidator.validate(galaxy, fleet, planet, cargo_type, direction, amount)
    result = SuperweaponValidator.validate_implode_planet(galaxy, fleet, planet, registry)
"""
from .colonize_validator import ColonizeValidator
from .transfer_validator import TransferValidator
from .superweapon_validator import SuperweaponValidator

__all__ = ['ColonizeValidator', 'TransferValidator', 'SuperweaponValidator']
