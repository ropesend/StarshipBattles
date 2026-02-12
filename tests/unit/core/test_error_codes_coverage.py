"""
Unit tests for ErrorCode enum coverage.

Tests that all error codes are unique, follow naming conventions,
and are properly categorized by their prefix letter.
"""
import re
import pytest

from game.core.error_codes import ErrorCode


class TestErrorCodeUniqueness:
    """Tests for error code uniqueness."""

    def test_all_error_codes_unique_values(self):
        """No duplicate .value among all members."""
        values = [code.value for code in ErrorCode]
        unique_values = set(values)
        assert len(values) == len(unique_values), (
            f"Duplicate error code values found: "
            f"{[v for v in values if values.count(v) > 1]}"
        )


class TestErrorCodeNamingConvention:
    """Tests for error code naming conventions."""

    def test_all_codes_follow_naming_convention(self):
        """Each value matches X### pattern (letter + 3 digits)."""
        pattern = re.compile(r"^[A-Z]\d{3}$")
        for code in ErrorCode:
            assert pattern.match(code.value), (
                f"Error code {code.name} has invalid format: '{code.value}' "
                f"(expected X###)"
            )


class TestValidationCodes:
    """Tests for validation code category."""

    def test_validation_codes_start_with_v(self):
        """V001-V099 pattern for validation codes."""
        validation_codes = [
            ErrorCode.VALIDATION_FAILED,
            ErrorCode.MISSING_REQUIRED,
            ErrorCode.OUT_OF_RANGE,
        ]
        for code in validation_codes:
            assert code.value.startswith("V"), (
                f"Validation code {code.name} should start with 'V'"
            )
            # Check number part is in range 001-099
            num = int(code.value[1:])
            assert 1 <= num <= 99, f"Validation code {code.name} out of range"


class TestStateCodes:
    """Tests for state code category."""

    def test_state_codes_start_with_s(self):
        """S001-S099 pattern for state codes."""
        state_codes = [
            ErrorCode.STATE_FROZEN,
            ErrorCode.NOT_INITIALIZED,
            ErrorCode.INVALID_STATE,
            ErrorCode.STATE_TRANSITION_DENIED,
        ]
        for code in state_codes:
            assert code.value.startswith("S"), (
                f"State code {code.name} should start with 'S'"
            )
            num = int(code.value[1:])
            assert 1 <= num <= 99, f"State code {code.name} out of range"


class TestResourceCodes:
    """Tests for resource code category."""

    def test_resource_codes_start_with_r(self):
        """R001-R099 pattern for resource codes."""
        resource_codes = [
            ErrorCode.RESOURCE_NOT_FOUND,
            ErrorCode.INVALID_FORMAT,
            ErrorCode.RESOURCE_LOAD_FAILED,
        ]
        for code in resource_codes:
            assert code.value.startswith("R"), (
                f"Resource code {code.name} should start with 'R'"
            )
            num = int(code.value[1:])
            assert 1 <= num <= 99, f"Resource code {code.name} out of range"


class TestPersistenceCodes:
    """Tests for persistence code category."""

    def test_persistence_codes_start_with_p(self):
        """P001-P099 pattern for persistence codes."""
        persistence_codes = [
            ErrorCode.SAVE_FAILED,
            ErrorCode.LOAD_FAILED,
            ErrorCode.CORRUPT_DATA,
            ErrorCode.VERSION_MISMATCH,
            ErrorCode.IO_ERROR,
        ]
        for code in persistence_codes:
            assert code.value.startswith("P"), (
                f"Persistence code {code.name} should start with 'P'"
            )
            num = int(code.value[1:])
            assert 1 <= num <= 99, f"Persistence code {code.name} out of range"


class TestFormulaCodes:
    """Tests for formula code category."""

    def test_formula_codes_start_with_f(self):
        """F001-F099 pattern for formula codes."""
        formula_codes = [
            ErrorCode.FORMULA_SYNTAX_ERROR,
            ErrorCode.FORMULA_UNDEFINED_VAR,
            ErrorCode.EVAL_ERROR,
            ErrorCode.FORMULA_GENERAL_ERROR,
        ]
        for code in formula_codes:
            assert code.value.startswith("F"), (
                f"Formula code {code.name} should start with 'F'"
            )
            num = int(code.value[1:])
            assert 1 <= num <= 99, f"Formula code {code.name} out of range"


class TestComponentCodes:
    """Tests for component code category."""

    def test_component_codes_start_with_c(self):
        """C001-C099 pattern for component codes."""
        component_codes = [
            ErrorCode.COMPONENT_NOT_FOUND,
            ErrorCode.COMPONENT_INVALID,
            ErrorCode.SLOT_OCCUPIED,
            ErrorCode.INCOMPATIBLE_COMPONENT,
        ]
        for code in component_codes:
            assert code.value.startswith("C"), (
                f"Component code {code.name} should start with 'C'"
            )
            num = int(code.value[1:])
            assert 1 <= num <= 99, f"Component code {code.name} out of range"


class TestAICodes:
    """Tests for AI code category."""

    def test_ai_codes_start_with_a(self):
        """A001-A099 pattern for AI codes."""
        ai_codes = [
            ErrorCode.AI_STATE_ERROR,
        ]
        for code in ai_codes:
            assert code.value.startswith("A"), (
                f"AI code {code.name} should start with 'A'"
            )
            num = int(code.value[1:])
            assert 1 <= num <= 99, f"AI code {code.name} out of range"
