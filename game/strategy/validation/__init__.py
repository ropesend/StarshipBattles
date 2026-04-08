"""
Strategy Layer Validation Module

PROJ-36: Centralized validation for fleet orders.
PROJ-68: Added TransferValidator for cargo operations.
PROJ-102: Added SuperweaponValidator for superweapon orders.
PROJ-238: Added PlanetOrderValidator for planet action orders.

Usage:
    from game.strategy.validation import ColonizeValidator, TransferValidator, SuperweaponValidator
    from game.strategy.validation import PlanetOrderValidator
    result = ColonizeValidator.validate(galaxy, fleet, target_planet)
    result = TransferValidator.validate(galaxy, fleet, planet, cargo_type, direction, amount)
    result = SuperweaponValidator.validate_implode_planet(galaxy, fleet, planet, registry)
    result = PlanetOrderValidator.validate_activate_ability(planet, facility_id, ability, registry)
"""
from .colonize_validator import ColonizeValidator
from .planet_order_validator import PlanetOrderValidator
from .transfer_validator import TransferValidator
from .superweapon_validator import SuperweaponValidator

__all__ = ['ColonizeValidator', 'PlanetOrderValidator', 'TransferValidator', 'SuperweaponValidator']
