"""Custom exception hierarchy for Starship Battles.

PROJ-45: Error Handling and Exception Management Refactor

This module provides a semantic exception hierarchy for better error handling
throughout the codebase. All exceptions inherit from GameException and support
error codes and context dictionaries for detailed error information.

Usage
=====

Basic usage::

    from game.core.exceptions import ValidationException
    from game.core.error_codes import ErrorCode

    raise ValidationException(
        "Invalid component configuration",
        code=ErrorCode.VALIDATION_FAILED.value,
        context={"component_id": "laser_1", "field": "damage"}
    )

Exception chaining (preserve original cause)::

    from game.core.error_codes import ErrorCode

    try:
        load_json(path)
    except json.JSONDecodeError as e:
        raise PersistenceException(
            f"Failed to parse save file: {path}",
            code=ErrorCode.CORRUPT_DATA.value,
            context={"path": path}
        ) from e

Catching and handling::

    from game.core.error_codes import ErrorCode

    try:
        component = load_component(data)
    except ComponentException as e:
        if e.code == ErrorCode.COMPONENT_INVALID.value:
            log_warning(f"Invalid component: {e.context}")
            component = default_component

Hierarchy
=========

GameException (base)
    StateException         - Object state errors
        FrozenStateException   - Modifying frozen objects
    ValidationException    - Input validation failures
    ResourceException      - Resource loading errors
        MissingResourceException - Resource not found
    PersistenceException   - Save/load failures
    SimulationException    - Combat engine errors
        ComponentException     - Component operation errors
        FormulaException       - Formula evaluation errors

Error Codes
===========
Use error codes from game.core.error_codes.ErrorCode for programmatic handling::

    from game.core.error_codes import ErrorCode

    raise ValidationException(
        "Value out of range",
        code=ErrorCode.OUT_OF_RANGE.value,  # "V004"
        context={"value": 150, "max": 100}
    )

Design Notes
============
- NO imports from game.* to avoid circular dependencies
- All exceptions support code and context attributes
- Context defaults to empty dict (never None)
- Exception chaining preserves original cause with `raise from`
- See docs/ERROR_HANDLING_GUIDELINES.md for complete usage guide
"""
from typing import Optional


class GameException(Exception):
    """Base class for all Starship Battles exceptions.

    Attributes:
        code: Optional error code for programmatic handling (e.g., "V001")
        context: Dictionary of contextual information about the error
    """

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        context: Optional[dict] = None
    ):
        """Initialize GameException.

        Args:
            message: Human-readable error message
            code: Optional error code (e.g., "V001", "S001")
            context: Optional dictionary with additional context
        """
        super().__init__(message)
        self.code = code
        self.context = context or {}


# =============================================================================
# State Management Exceptions
# =============================================================================

class StateException(GameException):
    """Exception for state-related errors.

    Raised when operations are attempted on objects in an invalid state,
    or when state transitions are not allowed.
    """
    pass


class FrozenStateException(StateException):
    """Exception for attempting to modify frozen/immutable state.

    Raised when code attempts to modify a ship, component, or other object
    that has been frozen (e.g., during combat resolution).
    """
    pass


# =============================================================================
# Validation Exceptions
# =============================================================================

class ValidationException(GameException):
    """Exception for validation failures.

    Raised when input validation fails, such as invalid component
    configurations, out-of-range values, or schema violations.
    """
    pass


# =============================================================================
# Resource Exceptions
# =============================================================================

class ResourceException(GameException):
    """Exception for resource-related errors.

    Base class for errors involving game resources such as images,
    sounds, data files, and other assets.
    """
    pass


class MissingResourceException(ResourceException):
    """Exception for missing resources.

    Raised when a required resource (image, sound, data file) cannot be found.
    """
    pass


# =============================================================================
# Persistence Exceptions
# =============================================================================

class PersistenceException(GameException):
    """Exception for save/load errors.

    Raised when saving or loading game data fails, including file I/O errors,
    serialization errors, and data corruption.
    """
    pass


# =============================================================================
# Simulation Exceptions
# =============================================================================

class SimulationException(GameException):
    """Exception for simulation engine errors.

    Base class for errors that occur during combat simulation,
    including component and formula evaluation errors.
    """
    pass


class ComponentException(SimulationException):
    """Exception for component-related errors.

    Raised when component operations fail, such as invalid component
    configurations, missing abilities, or component state errors.
    """
    pass


class FormulaException(SimulationException):
    """Exception for formula evaluation errors.

    Raised when formula parsing or evaluation fails, including
    syntax errors, undefined variables, and evaluation errors.
    """
    pass


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Base
    'GameException',
    # State
    'StateException',
    'FrozenStateException',
    # Validation
    'ValidationException',
    # Resources
    'ResourceException',
    'MissingResourceException',
    # Persistence
    'PersistenceException',
    # Simulation
    'SimulationException',
    'ComponentException',
    'FormulaException',
]
