"""
Validation Service for UI layer.

PROJ-43: This service provides a facade for ship design validation,
allowing UI code to validate components without directly importing from
game.simulation.entities.ship.

The service encapsulates:
- Component addition validation
- Complete design validation
"""
from typing import Any, Optional, TYPE_CHECKING

from game.simulation.entities.ship_loader import get_or_create_validator
from game.core.validation import ValidationResult
from game.core.registry import get_default_registry_provider

if TYPE_CHECKING:
    from game.core.constants import LayerType
    from game.simulation.entities.ship import Ship
    from game.simulation.components.component import Component


class ValidationService:
    """Service for validating ship designs and component additions.

    This class provides a clean interface for UI code to perform validation
    without directly importing the VALIDATOR from the simulation layer.

    Usage:
        service = ValidationService()
        result = service.validate_addition(ship, component, LayerType.OUTER)
        if not result.is_valid:
            show_errors(result.errors)
    """

    def __init__(self, validator: Optional[Any] = None):
        """Initialize the ValidationService.

        Args:
            validator: Optional validator instance for dependency injection.
                If None, uses get_or_create_validator() to get the default.
        """
        self._validator = validator

    def _get_validator(self) -> Any:
        """Get the validator, using default if not injected."""
        if self._validator is None:
            # PROJ-211: Pass registry_provider explicitly
            self._validator = get_or_create_validator(registry_provider=get_default_registry_provider())
        return self._validator

    def validate_addition(
        self, ship: 'Ship', component: 'Component', layer_type: 'LayerType'
    ) -> ValidationResult:
        """Validate adding a component to a ship at a specified layer.

        Args:
            ship: The Ship instance to validate against.
            component: The Component to be added.
            layer_type: The layer where the component would be placed.

        Returns:
            ValidationResult with is_valid, errors, and warnings attributes.
        """
        validator = self._get_validator()
        return validator.validate_addition(ship, component, layer_type)

    def validate_design(self, ship: 'Ship') -> ValidationResult:
        """Validate the complete ship design.

        Args:
            ship: The Ship instance to validate.

        Returns:
            ValidationResult with is_valid, errors, and warnings attributes.
        """
        validator = self._get_validator()
        return validator.validate_design(ship)
