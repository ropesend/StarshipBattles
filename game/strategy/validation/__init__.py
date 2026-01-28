"""
Strategy Layer Validation Module

PROJ-36: Centralized validation for fleet orders.

Usage:
    from game.strategy.validation import ColonizeValidator
    result = ColonizeValidator.validate(galaxy, fleet, target_planet)
"""
from .colonize_validator import ColonizeValidator

__all__ = ['ColonizeValidator']
