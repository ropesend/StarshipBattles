"""
Base validation classes for strategy layer.

PROJ-36: Provides base class for order validation rules.
"""
from abc import ABC, abstractmethod
from game.core.validation import ValidationResult


class OrderValidationRule(ABC):
    """Base class for order validation rules."""

    @abstractmethod
    def validate(self, fleet, galaxy, **kwargs) -> ValidationResult:
        """Validate an order for the given fleet."""
        pass
