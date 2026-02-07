"""
Strategy Layer Validation Module

PROJ-36: Centralized validation for fleet orders.
PROJ-68: Added TransferValidator for cargo operations.

Usage:
    from game.strategy.validation import ColonizeValidator, TransferValidator
    result = ColonizeValidator.validate(galaxy, fleet, target_planet)
    result = TransferValidator.validate(galaxy, fleet, planet, cargo_type, direction, amount)
"""
from .colonize_validator import ColonizeValidator
from .transfer_validator import TransferValidator

__all__ = ['ColonizeValidator', 'TransferValidator']
