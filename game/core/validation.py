"""Validation utilities shared across all layers.

This module provides the canonical ValidationResult class that can be safely
imported by all layers (simulation, strategy, UI). It serves as the single
source of truth for validation results across the codebase.

PROJ-21 Phase 1: Consolidated from 5 duplicate implementations:
- game/simulation/validation/base.py
- game/simulation/systems/validator.py
- game/strategy/engine/turn_engine.py
- game/ui/screens/race_validator.py

PROJ-43 Phase 11: Added IValidationRule protocol for cross-layer contracts.
PROJ-45 Phase 2: Added ErrorCode enum support.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Union, Any, Protocol, runtime_checkable

from game.core.error_codes import ErrorCode


@runtime_checkable
class IValidationRule(Protocol):
    """Protocol for validation rules across all layers.

    This protocol defines the contract for validators that can be used
    consistently across simulation, strategy, and UI layers. Using Protocol
    enables structural typing (duck typing) - any class with a matching
    validate() method satisfies this protocol without explicit inheritance.

    The context parameter is intentionally typed as Any to allow different
    layers to pass their domain-specific objects (ships, fleets, race configs).

    Usage:
        class MyValidator:
            def validate(self, context: Any) -> ValidationResult:
                result = ValidationResult()
                if not context:
                    result.add_error("Context required")
                return result

        # MyValidator automatically satisfies IValidationRule
        validator: IValidationRule = MyValidator()
        result = validator.validate(some_object)
    """

    def validate(self, context: Any) -> 'ValidationResult':
        """Validate the given context.

        Args:
            context: The object to validate. Type varies by domain:
                - Simulation: Ship, Component, etc.
                - Strategy: Fleet, Galaxy, etc.
                - UI: RaceConfig, etc.

        Returns:
            ValidationResult with is_valid, errors, and warnings.
        """
        ...


@dataclass
class ValidationResult:
    """Result of a validation operation.

    This is a Data Transfer Object (DTO) that can be safely imported
    by all layers (simulation, strategy, UI). It provides a unified
    interface for validation results across the codebase.

    Factory Methods:
        result = ValidationResult.with_errors(["Error 1", "Error 2"])

    Attributes:
        is_valid: True if validation passed, False otherwise.
        errors: List of error messages (validation failures).
        warnings: List of warning messages (non-fatal issues).
        error_code: Optional error code for programmatic handling.

    Example:
        result = ValidationResult.success()
        if some_condition_fails:
            result.add_error("Validation failed", code=ErrorCode.VALIDATION_FAILED.value)
        return result
    """
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    error_code: Optional[str] = None

    def __post_init__(self):
        """Ensure mutable defaults are properly initialized."""
        # Dataclass field(default_factory=list) handles this, but be explicit
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []

    @property
    def message(self) -> str:
        """First error message for display purposes.

        Returns the first error message if any errors exist, otherwise
        returns an empty string. Use this for simple single-message display
        scenarios (dialogs, logs). For multiple errors, iterate `.errors`.
        """
        return self.errors[0] if self.errors else ""

    def add_error(self, error: str, code: Optional[Union[str, ErrorCode]] = None) -> None:
        """Add an error and mark result as invalid.

        Args:
            error: Error message describing the validation failure.
            code: Optional error code for programmatic handling. Can be a string
                  or an ErrorCode enum value. Only sets error_code if not already
                  set (first code wins).
        """
        self.errors.append(error)
        self.is_valid = False
        if code and not self.error_code:
            # Convert ErrorCode enum to string value if needed
            self.error_code = code.value if isinstance(code, ErrorCode) else code

    def add_warning(self, warning: str) -> None:
        """Add a warning (does not affect validity).

        Args:
            warning: Warning message describing a non-fatal issue.
        """
        self.warnings.append(warning)

    def merge(self, other: 'ValidationResult') -> None:
        """Merge another result into this one.

        Combines errors and warnings from both results. If the other
        result is invalid, this result becomes invalid too.

        Args:
            other: Another ValidationResult to merge into this one.
        """
        if not other.is_valid:
            self.is_valid = False
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)

    @staticmethod
    def success() -> 'ValidationResult':
        """Create a successful validation result.

        Factory method for the common pattern of returning a valid result.

        Returns:
            A valid ValidationResult with no errors.

        Example:
            return ValidationResult.success()
        """
        return ValidationResult(is_valid=True)

    @staticmethod
    def error(message: str, code: Optional[Union[str, 'ErrorCode']] = None) -> 'ValidationResult':
        """Create a failed validation result with a single error.

        Factory method for the common pattern of returning a single error.

        Args:
            message: Error message describing the validation failure.
            code: Optional error code for programmatic handling.

        Returns:
            An invalid ValidationResult with the specified error.

        Example:
            return ValidationResult.error("Fleet not found")
        """
        error_code_value = None
        if code is not None:
            error_code_value = code.value if isinstance(code, ErrorCode) else code
        return ValidationResult(is_valid=False, errors=[message], error_code=error_code_value)

    @staticmethod
    def with_errors(messages: List[str]) -> 'ValidationResult':
        """Create a failed validation result with multiple errors.

        Factory method for the common pattern of returning multiple errors.

        Args:
            messages: List of error messages.

        Returns:
            An invalid ValidationResult with all specified errors.

        Example:
            return ValidationResult.with_errors(["Error 1", "Error 2"])
        """
        return ValidationResult(is_valid=False, errors=list(messages))


