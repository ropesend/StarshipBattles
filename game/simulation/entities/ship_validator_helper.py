"""Ship validation helper - extracted from Ship class (PROJ-88 Phase 3).

This module provides the ShipValidatorHelper class which handles all ship design
validation logic, including checking validity, getting warnings, and listing
missing requirements.
"""
from typing import List, TYPE_CHECKING

from .ship_loader import get_or_create_validator
from game.core.registry import get_default_registry_provider

if TYPE_CHECKING:
    from .ship import Ship


class ShipValidatorHelper:
    """Handles ship design validation by delegating to the centralized ShipValidator.

    This helper is created lazily by Ship and encapsulates all validation-related
    methods. It writes back to the ship reference for the mass_limits_ok flag.

    Attributes:
        _ship: Reference to the Ship instance being validated.
    """

    def __init__(self, ship: 'Ship') -> None:
        """Initialize the validator helper with a ship reference.

        Args:
            ship: The Ship instance to validate.
        """
        self._ship = ship

    def check_validity(self) -> bool:
        """Check if the current ship design is valid.

        Recalculates ship stats before validation to ensure accuracy.
        Updates the ship's mass_limits_ok flag for UI feedback.

        Returns:
            True if the ship design passes all validation checks, False otherwise.
        """
        self._ship.recalculate_stats()
        result = get_or_create_validator(registry_provider=get_default_registry_provider()).validate_design(self._ship)
        # Check for mass errors specifically for UI feedback flag
        self._ship.mass_limits_ok = not any("Mass budget exceeded" in e for e in result.errors)
        return result.is_valid

    def get_validation_warnings(self) -> List[str]:
        """Get list of validation warnings (soft requirements).

        Returns:
            List of warning strings from the validation result.
        """
        result = get_or_create_validator(registry_provider=get_default_registry_provider()).validate_design(self._ship)
        return result.warnings

    def get_missing_requirements(self) -> List[str]:
        """Check class requirements and return list of missing items.

        Returns:
            List of error strings prefixed with warning emoji, or empty list if valid.
        """
        result = get_or_create_validator(registry_provider=get_default_registry_provider()).validate_design(self._ship)
        if result.is_valid:
            return []
        # Return all errors as list of strings
        return [f"\u26a0 {err}" for err in result.errors]
