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
- T: Turn Processing (T001-T099)
- L: LLM Service (L001-L099)
- I: Image Service (I001-I099)

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

    SCHEMA_VALIDATION_ERROR = "V002"
    """Schema or structural validation error (missing fields, invalid data structure)."""

    MISSING_ENTITY = "V003"
    """Referenced entity does not exist."""

    OUT_OF_RANGE = "V004"
    """Value is outside allowed range."""

    OWNERSHIP_MISMATCH = "V005"
    """Entity exists but does not belong to the requesting empire (PROJ-381)."""

    # =========================================================================
    # State Codes (S001-S099)
    # =========================================================================

    STATE_FROZEN = "S001"
    """Object is frozen and cannot be modified."""

    NOT_INITIALIZED = "S002"
    """Object has not been properly initialized."""

    INVALID_STATE = "S003"
    """Object is in an invalid or unexpected state."""

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

    FORMULA_SYNTAX_ERROR = "F001"
    """Formula syntax error."""

    FORMULA_UNDEFINED_VAR = "F002"
    """Undefined variable in formula."""

    EVAL_ERROR = "F003"
    """Formula runtime evaluation error (division by zero, arithmetic errors)."""

    FORMULA_GENERAL_ERROR = "F004"
    """General formula evaluation failure."""

    # =========================================================================
    # Component Codes (C001-C099)
    # =========================================================================

    COMPONENT_NOT_FOUND = "C001"
    """Component does not exist."""

    COMPONENT_INVALID = "C002"
    """Component configuration is invalid."""

    MISSING_DEPENDENCY = "C003"
    """Required dependency injection parameter not provided."""

    SLOT_OCCUPIED = "C004"
    """Component slot is already occupied."""

    INCOMPATIBLE_COMPONENT = "C005"
    """Component is not compatible with target."""

    # =========================================================================
    # Turn Processing Codes (T001-T099)
    # =========================================================================

    PHASE_FAILED = "T001"
    """Sub-engine phase failed during turn processing."""

    TURN_ROLLBACK = "T002"
    """Turn was rolled back due to phase failure."""

    SNAPSHOT_FAILED = "T003"
    """Failed to create pre-turn state snapshot."""

    # =========================================================================
    # LLM Service Codes (L001-L099) - PROJ-296
    # =========================================================================

    LLM_CONFIG_MISSING = "L001"
    """LLM provider not configured (no API key, unknown provider)."""

    LLM_NETWORK_ERROR = "L002"
    """LLM network failure (connection, DNS, SSL, exhausted retries)."""

    LLM_BAD_RESPONSE = "L003"
    """LLM response was malformed or non-2xx (other than rate-limit)."""

    LLM_RATE_LIMITED = "L004"
    """LLM provider returned 429 - rate limit exceeded."""

    LLM_TIMEOUT = "L005"
    """LLM request exceeded its timeout."""

    LLM_CANCELLED = "L006"
    """LLM call was cancelled via cancel_token."""

    # =========================================================================
    # Image Service Codes (I001-I099) - PROJ-314
    # =========================================================================

    IMAGE_CONFIG_MISSING = "I001"
    """Image provider not configured (no API key, unknown provider)."""

    IMAGE_NETWORK_ERROR = "I002"
    """Image network failure (connection, DNS, SSL, exhausted retries)."""

    IMAGE_BAD_RESPONSE = "I003"
    """Image response was malformed or non-2xx (other than rate-limit)."""

    IMAGE_RATE_LIMITED = "I004"
    """Image provider returned 429 - rate limit exceeded."""

    IMAGE_TIMEOUT = "I005"
    """Image request exceeded its timeout."""

    IMAGE_CANCELLED = "I006"
    """Image call was cancelled via cancel_token."""


# =============================================================================
# Exports
# =============================================================================

__all__ = ['ErrorCode']
