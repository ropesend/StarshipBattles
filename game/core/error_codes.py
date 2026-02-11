"""Error code enumeration for Starship Battles.

PROJ-45: Error Handling and Exception Management Refactor

This module provides standardized error codes for programmatic error handling.
Error codes follow the format X### where X is a category letter and ### is
a three-digit number.

Categories
==========

- V: Validation (V001-V099)
- S: State (S001-S099)
- R: Resource (R001-R099)
- P: Persistence (P001-P099)
- F: Formula (F001-F099)
- C: Component (C001-C099)

Usage
=====

With exceptions::

    from game.core.exceptions import ValidationException
    from game.core.error_codes import ErrorCode

    raise ValidationException(
        "Invalid damage value",
        code=ErrorCode.VALIDATION_FAILED.value,
        context={"field": "damage", "value": -5}
    )

Programmatic handling::

    try:
        load_component(data)
    except ComponentException as e:
        if e.code == ErrorCode.COMPONENT_INVALID.value:
            # Handle specific error type
            pass

Design Notes
============
- NO imports from game.* to avoid circular dependencies
- All codes are unique within the enum
- Codes follow X### naming convention (letter + 3 digits)
- Categories are organized by functional area
"""
from enum import Enum


class ErrorCode(Enum):
    """Standardized error codes for programmatic error handling."""

    # =========================================================================
    # Validation Codes (V001-V099)
    # =========================================================================

    VALIDATION_FAILED = "V001"
    """General validation failure."""

    MISSING_REQUIRED = "V003"
    """Required field or value is missing."""

    OUT_OF_RANGE = "V004"
    """Value is outside allowed range."""

    # =========================================================================
    # State Codes (S001-S099)
    # =========================================================================

    STATE_FROZEN = "S001"
    """Object is frozen and cannot be modified."""

    NOT_INITIALIZED = "S002"
    """Object has not been properly initialized."""

    INVALID_STATE = "S003"
    """Object is in an invalid or unexpected state."""

    STATE_TRANSITION_DENIED = "S004"
    """Requested state transition is not allowed."""

    # =========================================================================
    # Resource Codes (R001-R099)
    # =========================================================================

    RESOURCE_NOT_FOUND = "R001"
    """Requested resource does not exist."""

    INVALID_FORMAT = "R002"
    """Resource has invalid or unsupported format."""

    RESOURCE_LOAD_FAILED = "R003"
    """Failed to load resource."""

    # =========================================================================
    # Persistence Codes (P001-P099)
    # =========================================================================

    SAVE_FAILED = "P001"
    """Failed to save game data."""

    LOAD_FAILED = "P002"
    """Failed to load game data."""

    CORRUPT_DATA = "P003"
    """Data is corrupted or malformed."""

    VERSION_MISMATCH = "P004"
    """Save file version is incompatible."""

    IO_ERROR = "P005"
    """File system I/O error occurred."""

    # =========================================================================
    # Formula Codes (F001-F099)
    # =========================================================================

    EVAL_ERROR = "F003"
    """Formula evaluation error."""

    # =========================================================================
    # Component Codes (C001-C099)
    # =========================================================================

    COMPONENT_NOT_FOUND = "C001"
    """Component does not exist."""

    COMPONENT_INVALID = "C002"
    """Component configuration is invalid."""

    SLOT_OCCUPIED = "C004"
    """Component slot is already occupied."""

    INCOMPATIBLE_COMPONENT = "C005"
    """Component is not compatible with target."""


# =============================================================================
# Exports
# =============================================================================

__all__ = ['ErrorCode']
