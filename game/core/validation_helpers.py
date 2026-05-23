"""Validation helpers for deserialization (from_dict methods).

PROJ-171: Deserialization Input Validation

This module provides reusable validation helpers to reduce boilerplate in
from_dict methods across the codebase. All helpers raise PersistenceException
with CORRUPT_DATA error code and detailed context dicts.

Usage
=====

Basic field validation::

    from game.core.validation_helpers import require_keys, validate_enum, validate_positive

    @classmethod
    def from_dict(cls, data: dict) -> "MyClass":
        require_keys(data, ['name', 'id', 'type'], 'MyClass')
        obj_type = validate_enum(data['type'], MyEnum, 'type', 'MyClass')
        validate_positive(data['count'], 'count', 'MyClass')
        return cls(name=data['name'], id=data['id'], obj_type=obj_type)

Wrapping nested from_dict calls::

    from game.core.validation_helpers import safe_from_dict

    child = safe_from_dict(ChildClass.from_dict, data['child'], 'ParentClass.child')

Design Notes
============
- All helpers use PersistenceException (not ValidationException) because
  from_dict receives external/saved data - this is a persistence boundary
- All helpers include context dicts for detailed error information
- Exception chaining preserves original cause with `raise from`
"""
from enum import Enum
from typing import Any, Callable, TypeVar

from game.core.exceptions import PersistenceException
from game.core.error_codes import ErrorCode


T = TypeVar('T')
EnumT = TypeVar('EnumT', bound=Enum)


def require_keys(data: dict[str, Any], keys: list[str], context: str) -> None:
    """Verify all required keys are present in data dict.

    Args:
        data: Dictionary to check
        keys: List of required key names
        context: Description of source object (e.g., 'StarSystem', 'Fleet')

    Raises:
        PersistenceException: If any required keys are missing, with CORRUPT_DATA code
            and missing_keys list in context
    """
    missing = [key for key in keys if key not in data]
    if missing:
        raise PersistenceException(
            f"{context}: missing required keys: {missing}",
            code=ErrorCode.CORRUPT_DATA.value,
            context={
                "source": context,
                "missing_keys": missing,
            }
        )


def validate_enum(value: str, enum_class: type[EnumT], field_name: str, context: str) -> EnumT:
    """Validate and return an enum member by name.

    Args:
        value: String name of the enum member
        enum_class: The enum class to look up in
        field_name: Name of the field being validated
        context: Description of source object

    Returns:
        The enum member if valid

    Raises:
        PersistenceException: If value is not a valid enum member name, with
            CORRUPT_DATA code and valid_values list in context
    """
    try:
        return enum_class[value]
    except (KeyError, ValueError):
        valid_names = [e.name for e in enum_class]
        raise PersistenceException(
            f"{context}: invalid {field_name} '{value}', expected one of {valid_names}",
            code=ErrorCode.CORRUPT_DATA.value,
            context={
                "source": context,
                "field": field_name,
                "value": value,
                "valid_values": valid_names,
            }
        )


def validate_positive(value: Any, field_name: str, context: str) -> None:
    """Validate that a numeric value is positive (> 0).

    Args:
        value: Numeric value to check
        field_name: Name of the field being validated
        context: Description of source object

    Raises:
        PersistenceException: If value <= 0, with CORRUPT_DATA code
    """
    if value <= 0:
        raise PersistenceException(
            f"{context}: {field_name} must be positive, got {value}",
            code=ErrorCode.CORRUPT_DATA.value,
            context={
                "source": context,
                "field": field_name,
                "value": value,
                "expected": "positive",
            }
        )


def validate_non_negative(value: Any, field_name: str, context: str) -> None:
    """Validate that a numeric value is non-negative (>= 0).

    Args:
        value: Numeric value to check
        field_name: Name of the field being validated
        context: Description of source object

    Raises:
        PersistenceException: If value < 0, with CORRUPT_DATA code
    """
    if value < 0:
        raise PersistenceException(
            f"{context}: {field_name} must be non-negative, got {value}",
            code=ErrorCode.CORRUPT_DATA.value,
            context={
                "source": context,
                "field": field_name,
                "value": value,
                "expected": "non-negative",
            }
        )


def validate_range(
    value: Any,
    min_val: Any,
    max_val: Any,
    field_name: str,
    context: str
) -> None:
    """Validate that a numeric value is within a range [min_val, max_val].

    Args:
        value: Numeric value to check
        min_val: Minimum allowed value (inclusive)
        max_val: Maximum allowed value (inclusive)
        field_name: Name of the field being validated
        context: Description of source object

    Raises:
        PersistenceException: If value outside range, with min/max in context
    """
    if value < min_val or value > max_val:
        raise PersistenceException(
            f"{context}: {field_name} must be in range [{min_val}, {max_val}], got {value}",
            code=ErrorCode.CORRUPT_DATA.value,
            context={
                "source": context,
                "field": field_name,
                "value": value,
                "min": min_val,
                "max": max_val,
            }
        )


def safe_from_dict(
    from_dict_fn: Callable[[dict[str, Any]], T],
    data: dict[str, Any],
    context: str
) -> T:
    """Wrap a from_dict call to convert common exceptions to PersistenceException.

    Args:
        from_dict_fn: The from_dict method to call
        data: Dictionary data to pass to from_dict
        context: Description of what is being loaded (e.g., 'Fleet.ships[0]')

    Returns:
        Result of from_dict_fn(data)

    Raises:
        PersistenceException: If from_dict raises KeyError, TypeError, or ValueError,
            with original exception chained via `from e`
    """
    try:
        return from_dict_fn(data)
    except (KeyError, TypeError, ValueError) as e:
        raise PersistenceException(
            f"{context}: failed to deserialize - {type(e).__name__}: {e}",
            code=ErrorCode.CORRUPT_DATA.value,
            context={
                "source": context,
                "error_type": type(e).__name__,
                "error": str(e),
            }
        ) from e


__all__ = [
    'require_keys',
    'validate_enum',
    'validate_positive',
    'validate_non_negative',
    'validate_range',
    'safe_from_dict',
]
