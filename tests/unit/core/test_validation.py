"""Tests for canonical ValidationResult in game.core.validation.

This tests the unified ValidationResult class that serves all layers
(simulation, strategy, UI) from game/core/validation.py.
"""
import pytest

from game.core.validation import ValidationResult


class TestValidationResultInit:
    """Tests for ValidationResult initialization."""

    def test_default_initialization(self):
        """ValidationResult defaults to valid with empty lists."""
        result = ValidationResult()
        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == []
        assert result.error_code is None

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
