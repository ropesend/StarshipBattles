"""Tests for base validation rule classes.

Tests the template method pattern implementation in ValidationRule
and its subclasses (DesignValidationRule, AdditionValidationRule).
"""
import pytest
from unittest.mock import MagicMock, Mock

from game.simulation.validation.base import (
    ValidationResult,
    ValidationRule,
    DesignValidationRule,
    AdditionValidationRule
)


class TestValidationResult:
    """Tests for ValidationResult class."""

    def test_init_valid(self):
        """ValidationResult can be created as valid."""
        result = ValidationResult(True)
        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == []

    def test_init_invalid_with_errors(self):
        """ValidationResult can be created as invalid with errors."""
        result = ValidationResult(False, errors=["Error 1", "Error 2"])
        assert result.is_valid is False
        assert len(result.errors) == 2
        assert "Error 1" in result.errors

    def test_init_with_warnings(self):
        """ValidationResult can have warnings without being invalid."""
        result = ValidationResult(True, warnings=["Warning 1"])
        assert result.is_valid is True
        assert len(result.warnings) == 1
        assert "Warning 1" in result.warnings

    def test_add_error_marks_invalid(self):
        """add_error() sets is_valid to False."""
        result = ValidationResult(True)
        assert result.is_valid is True

        result.add_error("Something went wrong")
        assert result.is_valid is False
        assert "Something went wrong" in result.errors

    def test_add_warning_preserves_validity(self):
        """add_warning() does not affect is_valid."""
        result = ValidationResult(True)
        result.add_warning("Consider this")
        assert result.is_valid is True
        assert "Consider this" in result.warnings

    def test_merge_combines_errors(self):
        """merge() combines errors from both results."""
        result1 = ValidationResult(True)
        result1.add_error("Error A")

        result2 = ValidationResult(True)
        result2.add_error("Error B")

        result1.merge(result2)
        assert result1.is_valid is False
        assert "Error A" in result1.errors
        assert "Error B" in result1.errors

    def test_merge_combines_warnings(self):
        """merge() combines warnings from both results."""
        result1 = ValidationResult(True, warnings=["Warn A"])
        result2 = ValidationResult(True, warnings=["Warn B"])

        result1.merge(result2)
        assert "Warn A" in result1.warnings
        assert "Warn B" in result1.warnings

    def test_merge_propagates_invalid(self):
        """merge() sets is_valid to False if other is invalid."""
        result1 = ValidationResult(True)
        result2 = ValidationResult(False)

        result1.merge(result2)
        assert result1.is_valid is False


class ConcreteValidationRule(ValidationRule):
    """Concrete implementation for testing ValidationRule."""

    def __init__(self, validation_result=None):
        self._test_result = validation_result or ValidationResult(True)
        self.do_validate_called = False
        self.do_validate_args = None

    def _do_validate(self, ship, component, layer_type):
        self.do_validate_called = True
        self.do_validate_args = (ship, component, layer_type)
        return self._test_result


class CustomShouldValidateRule(ValidationRule):
    """Rule with custom _should_validate() for testing."""

    def __init__(self, should_validate_return=True):
        self._should_validate_return = should_validate_return
        self.should_validate_called = False

    def _should_validate(self, component, layer_type):
        self.should_validate_called = True
        return self._should_validate_return

    def _do_validate(self, ship, component, layer_type):
        return ValidationResult(True)


class TestValidationRule:
    """Tests for ValidationRule base class."""

    def test_validate_calls_do_validate_when_should_validate_true(self):
        """validate() calls _do_validate() when _should_validate() returns True."""
        rule = ConcreteValidationRule()
        mock_ship = MagicMock()
        mock_component = MagicMock()
        mock_layer = MagicMock()

        rule.validate(mock_ship, mock_component, mock_layer)

        assert rule.do_validate_called is True
        assert rule.do_validate_args == (mock_ship, mock_component, mock_layer)

    def test_validate_skips_do_validate_when_should_validate_false(self):
        """validate() skips _do_validate() when _should_validate() returns False."""
        rule = CustomShouldValidateRule(should_validate_return=False)
        mock_ship = MagicMock()

        result = rule.validate(mock_ship, None, None)

        assert rule.should_validate_called is True
        assert result.is_valid is True

    def test_default_should_validate_requires_component_and_layer(self):
        """Default _should_validate() returns False without component/layer."""
        rule = ConcreteValidationRule()
        mock_ship = MagicMock()

        # No component, no layer
        result = rule.validate(mock_ship, None, None)
        assert rule.do_validate_called is False
        assert result.is_valid is True

    def test_default_should_validate_requires_both(self):
        """Default _should_validate() requires both component AND layer."""
        rule = ConcreteValidationRule()
        mock_ship = MagicMock()
        mock_component = MagicMock()
        mock_layer = MagicMock()

        # Only component
        rule.do_validate_called = False
        rule.validate(mock_ship, mock_component, None)
        assert rule.do_validate_called is False

        # Only layer
        rule.do_validate_called = False
        rule.validate(mock_ship, None, mock_layer)
        assert rule.do_validate_called is False

        # Both present
        rule.do_validate_called = False
        rule.validate(mock_ship, mock_component, mock_layer)
        assert rule.do_validate_called is True

    def test_validate_returns_do_validate_result(self):
        """validate() returns the result from _do_validate()."""
        expected_result = ValidationResult(False, errors=["Test error"])
        rule = ConcreteValidationRule(validation_result=expected_result)
        mock_ship = MagicMock()
        mock_component = MagicMock()
        mock_layer = MagicMock()

        result = rule.validate(mock_ship, mock_component, mock_layer)

        assert result is expected_result
        assert result.is_valid is False
        assert "Test error" in result.errors

    def test_subclass_can_override_should_validate(self):
        """Subclass can override _should_validate() behavior."""
        rule = CustomShouldValidateRule(should_validate_return=True)
        mock_ship = MagicMock()

        # Even without component/layer, custom _should_validate returns True
        rule.validate(mock_ship, None, None)

        assert rule.should_validate_called is True


class ConcreteDesignRule(DesignValidationRule):
    """Concrete implementation for testing DesignValidationRule."""

    def __init__(self):
        self.do_validate_called = False

    def _do_validate(self, ship, component, layer_type):
        self.do_validate_called = True
        return ValidationResult(True)


class TestDesignValidationRule:
    """Tests for DesignValidationRule class."""

    def test_always_validates_without_component(self):
        """DesignValidationRule validates even without component/layer."""
        rule = ConcreteDesignRule()
        mock_ship = MagicMock()

        rule.validate(mock_ship, None, None)

        assert rule.do_validate_called is True

    def test_always_validates_with_component(self):
        """DesignValidationRule validates with component/layer too."""
        rule = ConcreteDesignRule()
        mock_ship = MagicMock()
        mock_component = MagicMock()
        mock_layer = MagicMock()

        rule.validate(mock_ship, mock_component, mock_layer)

        assert rule.do_validate_called is True


class ConcreteAdditionRule(AdditionValidationRule):
    """Concrete implementation for testing AdditionValidationRule."""

    def __init__(self):
        self.do_validate_called = False

    def _do_validate(self, ship, component, layer_type):
        self.do_validate_called = True
        return ValidationResult(True)


class TestAdditionValidationRule:
    """Tests for AdditionValidationRule class."""

    def test_requires_component_and_layer(self):
        """AdditionValidationRule requires component and layer."""
        rule = ConcreteAdditionRule()
        mock_ship = MagicMock()

        # Without component/layer, should not validate
        rule.validate(mock_ship, None, None)
        assert rule.do_validate_called is False

    def test_validates_with_component_and_layer(self):
        """AdditionValidationRule validates when component and layer present."""
        rule = ConcreteAdditionRule()
        mock_ship = MagicMock()
        mock_component = MagicMock()
        mock_layer = MagicMock()

        rule.validate(mock_ship, mock_component, mock_layer)

        assert rule.do_validate_called is True
