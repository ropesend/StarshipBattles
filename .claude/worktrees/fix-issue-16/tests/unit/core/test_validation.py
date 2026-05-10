"""Tests for canonical ValidationResult in game.core.validation.

This tests the unified ValidationResult class that serves all layers
(simulation, strategy, UI) from game/core/validation.py.

PROJ-43 Phase 11: Added tests for IValidationRule protocol.
"""
import pytest
from typing import Any

from game.core.validation import ValidationResult, IValidationRule


class TestValidationResultInit:
    """Tests for ValidationResult initialization."""

    def test_default_initialization(self):
        """ValidationResult defaults to valid with empty lists."""
        result = ValidationResult()
        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == []
        assert result.error_code is None

    def test_init_with_none_errors_defaults_to_list(self):
        """Passing errors=None results in empty list."""
        result = ValidationResult(errors=None)
        assert result.errors == []

    def test_init_with_none_warnings_defaults_to_list(self):
        """Passing warnings=None results in empty list."""
        result = ValidationResult(warnings=None)
        assert result.warnings == []

    def test_init_valid(self):
        """ValidationResult can be created as valid."""
        result = ValidationResult(is_valid=True)
        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == []

    def test_init_invalid(self):
        """ValidationResult can be created as invalid."""
        result = ValidationResult(is_valid=False)
        assert result.is_valid is False

    def test_init_with_errors(self):
        """ValidationResult can be initialized with error list."""
        result = ValidationResult(is_valid=False, errors=["Error 1", "Error 2"])
        assert result.is_valid is False
        assert len(result.errors) == 2
        assert "Error 1" in result.errors
        assert "Error 2" in result.errors

    def test_init_with_warnings(self):
        """ValidationResult can have warnings without being invalid."""
        result = ValidationResult(is_valid=True, warnings=["Warning 1"])
        assert result.is_valid is True
        assert len(result.warnings) == 1
        assert "Warning 1" in result.warnings

    def test_init_with_error_code(self):
        """ValidationResult can store an error code."""
        result = ValidationResult(is_valid=False, error_code="E001")
        assert result.error_code == "E001"


class TestValidationResultMessage:
    """Tests for the message property (UI/strategy compatibility)."""

    def test_message_returns_first_error(self):
        """message property returns first error when errors exist."""
        result = ValidationResult(is_valid=False, errors=["First error", "Second error"])
        assert result.message == "First error"

    def test_message_empty_when_no_errors(self):
        """message property returns empty string when no errors."""
        result = ValidationResult(is_valid=True)
        assert result.message == ""

    def test_message_empty_when_only_warnings(self):
        """message property returns empty string when only warnings exist."""
        result = ValidationResult(is_valid=True, warnings=["A warning"])
        assert result.message == ""


class TestValidationResultFirstError:
    """Tests for the first_error semantic alias of message."""

    def test_first_error_returns_first_error(self):
        result = ValidationResult(is_valid=False, errors=["First", "Second"])
        assert result.first_error == "First"

    def test_first_error_empty_when_no_errors(self):
        result = ValidationResult(is_valid=True)
        assert result.first_error == ""

    def test_first_error_matches_message(self):
        """first_error and message must always return the same value.

        Regression: an earlier half-merged rename left `.first_error`
        used by call sites (race_setup_screen save handler,
        test_quickstart_races) without the property actually existing
        on the class. Adding the property as an alias prevented those
        call sites from crashing. The alias contract is: both names
        return identical values for any state.
        """
        # Empty
        r = ValidationResult()
        assert r.first_error == r.message

        # Single error
        r = ValidationResult(is_valid=False, errors=["Only error"])
        assert r.first_error == r.message

        # Multiple errors
        r = ValidationResult(is_valid=False, errors=["A", "B", "C"])
        assert r.first_error == r.message

        # Warnings only
        r = ValidationResult(warnings=["A warning"])
        assert r.first_error == r.message


class TestValidationResultAddError:
    """Tests for add_error method."""

    def test_add_error_marks_invalid(self):
        """add_error() sets is_valid to False."""
        result = ValidationResult()
        assert result.is_valid is True

        result.add_error("Something went wrong")
        assert result.is_valid is False
        assert "Something went wrong" in result.errors

    def test_add_error_appends_to_list(self):
        """add_error() appends error to existing list."""
        result = ValidationResult(is_valid=False, errors=["Error 1"])
        result.add_error("Error 2")
        assert len(result.errors) == 2
        assert "Error 1" in result.errors
        assert "Error 2" in result.errors

    def test_add_error_with_code(self):
        """add_error() can set error_code."""
        result = ValidationResult()
        result.add_error("Error message", code="E001")
        assert result.error_code == "E001"
        assert "Error message" in result.errors

    def test_add_error_first_code_wins(self):
        """add_error() only sets error_code if not already set."""
        result = ValidationResult()
        result.add_error("First error", code="E001")
        result.add_error("Second error", code="E002")
        assert result.error_code == "E001"

    def test_add_error_with_error_code_enum(self):
        """ErrorCode enum is converted to its string value."""
        from game.core.error_codes import ErrorCode

        result = ValidationResult()
        result.add_error("Test error", code=ErrorCode.VALIDATION_FAILED)

        assert result.is_valid is False
        assert "Test error" in result.errors
        assert result.error_code == ErrorCode.VALIDATION_FAILED.value

    def test_add_error_no_code_leaves_none(self):
        """add_error without code leaves error_code as None."""
        result = ValidationResult()
        result.add_error("No code error")

        assert result.error_code is None
        assert result.is_valid is False


class TestValidationResultAddWarning:
    """Tests for add_warning method."""

    def test_add_warning_preserves_validity(self):
        """add_warning() does not affect is_valid."""
        result = ValidationResult()
        result.add_warning("Consider this")
        assert result.is_valid is True
        assert "Consider this" in result.warnings

    def test_add_warning_appends_to_list(self):
        """add_warning() appends warning to existing list."""
        result = ValidationResult(warnings=["Warning 1"])
        result.add_warning("Warning 2")
        assert len(result.warnings) == 2
        assert "Warning 1" in result.warnings
        assert "Warning 2" in result.warnings


class TestValidationResultMerge:
    """Tests for merge method."""

    def test_merge_combines_errors(self):
        """merge() combines errors from both results."""
        result1 = ValidationResult()
        result1.add_error("Error A")

        result2 = ValidationResult()
        result2.add_error("Error B")

        result1.merge(result2)
        assert result1.is_valid is False
        assert "Error A" in result1.errors
        assert "Error B" in result1.errors

    def test_merge_combines_warnings(self):
        """merge() combines warnings from both results."""
        result1 = ValidationResult(warnings=["Warn A"])
        result2 = ValidationResult(warnings=["Warn B"])

        result1.merge(result2)
        assert "Warn A" in result1.warnings
        assert "Warn B" in result1.warnings

    def test_merge_propagates_invalid(self):
        """merge() sets is_valid to False if other is invalid."""
        result1 = ValidationResult(is_valid=True)
        result2 = ValidationResult(is_valid=False)

        result1.merge(result2)
        assert result1.is_valid is False

    def test_merge_valid_into_valid(self):
        """merge() keeps valid if both are valid."""
        result1 = ValidationResult(is_valid=True)
        result2 = ValidationResult(is_valid=True)

        result1.merge(result2)
        assert result1.is_valid is True

    def test_merge_does_not_restore_validity(self):
        """merge() does not restore validity from invalid."""
        result1 = ValidationResult(is_valid=False)
        result2 = ValidationResult(is_valid=True)

        result1.merge(result2)
        assert result1.is_valid is False


class TestValidationResultCreation:
    """Tests for ValidationResult creation patterns."""

    def test_create_empty_message_in_errors(self):
        """Creating with empty string in errors list."""
        result = ValidationResult(is_valid=False, errors=[""])

        assert result.is_valid is False
        assert result.message == ""  # First error is empty string
        assert len(result.errors) == 1


class TestValidationResultDataclass:
    """Tests for dataclass behavior."""

    def test_is_dataclass(self):
        """ValidationResult should be a dataclass."""
        from dataclasses import is_dataclass
        assert is_dataclass(ValidationResult)

    def test_mutable_default_lists(self):
        """Each instance gets its own list instances."""
        result1 = ValidationResult()
        result2 = ValidationResult()

        result1.errors.append("Error in result1")

        assert "Error in result1" in result1.errors
        assert "Error in result1" not in result2.errors


class TestIValidationRuleProtocol:
    """Tests for IValidationRule protocol.

    PROJ-43 Phase 11: Verifies the protocol can be used for structural typing.
    """

    def test_protocol_is_importable(self):
        """IValidationRule can be imported from game.core.validation."""
        from game.core.validation import IValidationRule
        assert IValidationRule is not None

    def test_class_implementing_protocol_is_recognized(self):
        """A class with validate() method satisfies the protocol."""
        from typing import runtime_checkable, Protocol

        class MyValidator:
            """A validator that implements the protocol."""
            def validate(self, context: Any) -> ValidationResult:
                return ValidationResult(is_valid=True)

        # Create instance and verify it has the expected method
        validator = MyValidator()
        result = validator.validate({"test": "data"})
        assert result.is_valid is True
        assert isinstance(result, ValidationResult)

    def test_protocol_works_with_different_context_types(self):
        """Protocol validate() accepts any context type."""
        class StringValidator:
            def validate(self, context: str) -> ValidationResult:
                if not context:
                    result = ValidationResult()
                    result.add_error("Empty string not allowed")
                    return result
                return ValidationResult(is_valid=True)

        validator = StringValidator()

        # Valid case
        result = validator.validate("hello")
        assert result.is_valid is True

        # Invalid case
        result = validator.validate("")
        assert result.is_valid is False
        assert "Empty string not allowed" in result.errors

    def test_protocol_structural_typing(self):
        """Verify protocol uses structural typing (duck typing)."""
        from typing import runtime_checkable

        # IValidationRule should be runtime_checkable for isinstance checks
        class ConformingValidator:
            def validate(self, context: Any) -> ValidationResult:
                return ValidationResult()

        # The class should work as a validator even without explicit inheritance
        validator = ConformingValidator()
        result = validator.validate(None)
        assert isinstance(result, ValidationResult)


class TestValidationResultFactoryMethods:
    """Tests for ValidationResult factory methods.

    PROJ-176 Phase 1: Factory methods for cleaner construction patterns.
    """

    def test_success_returns_valid_result(self):
        """success() returns a valid result with no errors."""
        result = ValidationResult.success()
        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == []
        assert result.error_code is None

    def test_error_returns_invalid_result_with_message(self):
        """error() returns an invalid result with single error message."""
        result = ValidationResult.error("Something went wrong")
        assert result.is_valid is False
        assert result.errors == ["Something went wrong"]
        assert result.warnings == []

    def test_error_with_code(self):
        """error() can include an error code."""
        result = ValidationResult.error("Invalid input", code="V001")
        assert result.is_valid is False
        assert result.errors == ["Invalid input"]
        assert result.error_code == "V001"

    def test_error_with_error_code_enum(self):
        """error() converts ErrorCode enum to string value."""
        from game.core.error_codes import ErrorCode
        result = ValidationResult.error("Test error", code=ErrorCode.VALIDATION_FAILED)
        assert result.is_valid is False
        assert result.error_code == ErrorCode.VALIDATION_FAILED.value

    def test_with_errors_returns_invalid_result_with_multiple_messages(self):
        """with_errors() returns an invalid result with multiple error messages."""
        result = ValidationResult.with_errors(["Error 1", "Error 2", "Error 3"])
        assert result.is_valid is False
        assert result.errors == ["Error 1", "Error 2", "Error 3"]
        assert result.warnings == []

    def test_with_errors_with_empty_list_is_still_invalid(self):
        """with_errors() with empty list returns invalid result."""
        result = ValidationResult.with_errors([])
        assert result.is_valid is False
        assert result.errors == []

    def test_with_errors_copies_input_list(self):
        """with_errors() makes a copy of the input list to avoid mutation."""
        original = ["Error A", "Error B"]
        result = ValidationResult.with_errors(original)
        original.append("Error C")
        assert "Error C" not in result.errors
        assert len(result.errors) == 2
