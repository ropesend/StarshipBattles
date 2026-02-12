"""
Unit tests for ValidationResult edge cases.

Tests initialization with None defaults, message property,
add_error with ErrorCode, merging behavior, and creation patterns.
"""
import pytest

from game.core.validation import ValidationResult
from game.core.error_codes import ErrorCode


class TestValidationResultInit:
    """Tests for ValidationResult initialization edge cases."""

    def test_init_with_none_errors_defaults_to_list(self):
        """Passing errors=None results in empty list."""
        result = ValidationResult(errors=None)
        assert result.errors == []

    def test_init_with_none_warnings_defaults_to_list(self):
        """Passing warnings=None results in empty list."""
        result = ValidationResult(warnings=None)
        assert result.warnings == []

    def test_init_default_is_valid(self):
        """Default initialization is valid with empty lists."""
        result = ValidationResult()
        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == []
        assert result.error_code is None


class TestValidationResultMessage:
    """Tests for the message property."""

    def test_message_property_empty_errors(self):
        """When no errors, message is empty string."""
        result = ValidationResult()
        assert result.message == ""

    def test_message_property_first_error(self):
        """Message returns the first error."""
        result = ValidationResult(is_valid=False, errors=["First error", "Second error"])
        assert result.message == "First error"

    def test_message_property_single_error(self):
        """Message returns single error correctly."""
        result = ValidationResult(is_valid=False, errors=["Only error"])
        assert result.message == "Only error"


class TestValidationResultAddError:
    """Tests for add_error method edge cases."""

    def test_add_error_with_error_code_enum(self):
        """ErrorCode enum is converted to its string value."""
        result = ValidationResult()
        result.add_error("Test error", code=ErrorCode.VALIDATION_FAILED)

        assert result.is_valid is False
        assert "Test error" in result.errors
        assert result.error_code == ErrorCode.VALIDATION_FAILED.value

    def test_add_error_with_string_code(self):
        """String error code is stored directly."""
        result = ValidationResult()
        result.add_error("Test error", code="CUSTOM_CODE")

        assert result.error_code == "CUSTOM_CODE"

    def test_add_error_second_code_ignored(self):
        """First error code wins, subsequent codes are ignored."""
        result = ValidationResult()
        result.add_error("First error", code="FIRST_CODE")
        result.add_error("Second error", code="SECOND_CODE")

        assert result.error_code == "FIRST_CODE"
        assert len(result.errors) == 2

    def test_add_error_no_code_leaves_none(self):
        """add_error without code leaves error_code as None."""
        result = ValidationResult()
        result.add_error("No code error")

        assert result.error_code is None
        assert result.is_valid is False


class TestValidationResultMerge:
    """Tests for merge method behavior."""

    def test_merge_valid_into_invalid(self):
        """Merging valid into invalid stays invalid."""
        invalid_result = ValidationResult(is_valid=False, errors=["Original error"])
        valid_result = ValidationResult(is_valid=True, warnings=["A warning"])

        invalid_result.merge(valid_result)

        assert invalid_result.is_valid is False
        assert "Original error" in invalid_result.errors
        assert "A warning" in invalid_result.warnings

    def test_merge_invalid_into_valid(self):
        """Merging invalid into valid becomes invalid."""
        valid_result = ValidationResult(is_valid=True)
        invalid_result = ValidationResult(is_valid=False, errors=["New error"])

        valid_result.merge(invalid_result)

        assert valid_result.is_valid is False
        assert "New error" in valid_result.errors

    def test_merge_combines_all_errors_and_warnings(self):
        """Merge combines all errors and warnings from both results."""
        result1 = ValidationResult(
            is_valid=False,
            errors=["Error 1"],
            warnings=["Warning 1"]
        )
        result2 = ValidationResult(
            is_valid=False,
            errors=["Error 2"],
            warnings=["Warning 2"]
        )

        result1.merge(result2)

        assert len(result1.errors) == 2
        assert "Error 1" in result1.errors
        assert "Error 2" in result1.errors
        assert len(result1.warnings) == 2
        assert "Warning 1" in result1.warnings
        assert "Warning 2" in result1.warnings

    def test_merge_two_valid_results(self):
        """Merging two valid results stays valid."""
        result1 = ValidationResult(is_valid=True)
        result2 = ValidationResult(is_valid=True, warnings=["Note"])

        result1.merge(result2)

        assert result1.is_valid is True
        assert "Note" in result1.warnings


class TestValidationResultCreation:
    """Tests for ValidationResult creation patterns."""

    def test_create_with_errors_list(self):
        """Creating with errors list directly."""
        result = ValidationResult(is_valid=False, errors=["Error A", "Error B"])

        assert result.is_valid is False
        assert len(result.errors) == 2

    def test_create_empty_message_in_errors(self):
        """Creating with empty string in errors list."""
        result = ValidationResult(is_valid=False, errors=[""])

        assert result.is_valid is False
        assert result.message == ""  # First error is empty string
        assert len(result.errors) == 1
