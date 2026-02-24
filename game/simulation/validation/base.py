"""Base validation rule classes using template method pattern.

This module provides the base infrastructure for validation rules,
using the template method pattern to reduce duplicate guard clauses
across rule implementations.

PROJ-21: ValidationResult is now imported from game.core.validation
for cross-layer consistency.
"""
from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

from game.core.validation import ValidationResult

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship
    from game.simulation.components.component import Component
    from game.core.constants import LayerType


class ValidationRule(ABC):
    """Abstract base class for validation rules using template method pattern.

    Subclasses implement _do_validate() with their specific validation logic.
    The base class handles common guard clause logic via _should_validate().

    Example usage:
        class MyRule(ValidationRule):
            def _do_validate(self, ship, component, layer_type):
                result = ValidationResult(True)
                if some_condition_fails:
                    result.add_error("Validation failed")
                return result

    Override _should_validate() to customize when the rule applies:
        def _should_validate(self, component, layer_type) -> bool:
            # Only validate for specific component types
            return component is not None and component.has_ability('SomeAbility')
    """

    def validate(
        self,
        ship: 'Ship',
        component: Optional['Component'] = None,
        layer_type: Optional['LayerType'] = None
    ) -> ValidationResult:
        """Execute validation using template method pattern.

        Args:
            ship: The ship being validated
            component: Optional component being added (for addition validation)
            layer_type: Optional target layer (for addition validation)

        Returns:
            ValidationResult with errors/warnings from validation
        """
        if not self._should_validate(component, layer_type):
            return ValidationResult.success()
        return self._do_validate(ship, component, layer_type)

    def _should_validate(
        self,
        component: Optional['Component'],
        layer_type: Optional['LayerType']
    ) -> bool:
        """Determine if validation should proceed.

        Default implementation requires both component and layer_type for
        addition validation. Override this in subclasses for different
        validation modes (e.g., design-only validation).

        Args:
            component: Component being validated (may be None for design validation)
            layer_type: Target layer (may be None for design validation)

        Returns:
            True if validation should proceed, False to skip
        """
        return component is not None and layer_type is not None

    @abstractmethod
    def _do_validate(
        self,
        ship: 'Ship',
        component: Optional['Component'],
        layer_type: Optional['LayerType']
    ) -> ValidationResult:
        """Perform the actual validation logic.

        Subclasses implement this method with their specific validation rules.
        This is only called if _should_validate() returns True.

        Args:
            ship: The ship being validated
            component: Component being added (may be None for design-only rules)
            layer_type: Target layer (may be None for design-only rules)

        Returns:
            ValidationResult with any errors or warnings
        """
        pass


class DesignValidationRule(ValidationRule):
    """Base class for rules that validate the overall ship design.

    These rules don't require a component/layer - they validate the ship
    as a whole. Override _should_validate to always return True.
    """

    def _should_validate(
        self,
        component: Optional['Component'],
        layer_type: Optional['LayerType']
    ) -> bool:
        """Design rules always run, regardless of component/layer."""
        return True


class AdditionValidationRule(ValidationRule):
    """Base class for rules that validate component additions.

    These rules require both component and layer_type to be present.
    Uses the default _should_validate() behavior.
    """
    pass
