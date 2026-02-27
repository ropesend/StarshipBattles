"""Tests for deserialization validation helpers.

PROJ-171: Deserialization Input Validation - Phase 1
"""
import pytest
from enum import Enum

from game.core.validation_helpers import (
    require_keys,
    validate_enum,
    validate_positive,
    validate_non_negative,
    validate_range,
    safe_from_dict,
)
from game.core.exceptions import PersistenceException
from game.core.error_codes import ErrorCode


class SampleEnum(Enum):
    """Test enum for validate_enum tests."""
    ALPHA = "a"
    BETA = "b"
    GAMMA = "c"


class TestRequireKeys:
    """Tests for require_keys helper."""

    def test_all_keys_present_no_exception(self):
        """When all required keys are present, no exception is raised."""
        data = {"name": "Test", "id": 123, "value": 5.0}
        # Should not raise
        require_keys(data, ["name", "id", "value"], "TestObject")

    def test_missing_one_key_raises_persistence_exception(self):
        """When one key is missing, raises PersistenceException with context."""
        data = {"name": "Test", "value": 5.0}

        with pytest.raises(PersistenceException) as exc_info:
            require_keys(data, ["name", "id", "value"], "TestObject")

        exc = exc_info.value
        assert exc.code == ErrorCode.CORRUPT_DATA.value
        assert "missing_keys" in exc.context
        assert "id" in exc.context["missing_keys"]
        assert "TestObject" in str(exc)

    def test_missing_multiple_keys_lists_all(self):
        """When multiple keys are missing, all are listed."""
        data = {"name": "Test"}

        with pytest.raises(PersistenceException) as exc_info:
            require_keys(data, ["name", "id", "value", "count"], "TestObject")

        exc = exc_info.value
        missing = exc.context["missing_keys"]
        assert "id" in missing
        assert "value" in missing
        assert "count" in missing

    def test_empty_dict_all_keys_missing(self):
        """When dict is empty, all keys are listed as missing."""
        data = {}

        with pytest.raises(PersistenceException) as exc_info:
            require_keys(data, ["name", "id"], "TestObject")

        exc = exc_info.value
        missing = exc.context["missing_keys"]
        assert "name" in missing
        assert "id" in missing


class TestValidateEnum:
    """Tests for validate_enum helper."""

    def test_valid_enum_name_returns_member(self):
        """Valid enum name returns the correct enum member."""
        result = validate_enum("ALPHA", SampleEnum, "field", "TestObject")
        assert result == SampleEnum.ALPHA

        result = validate_enum("BETA", SampleEnum, "field", "TestObject")
        assert result == SampleEnum.BETA

    def test_invalid_enum_name_raises_persistence_exception(self):
        """Invalid enum name raises PersistenceException with valid_values."""
        with pytest.raises(PersistenceException) as exc_info:
            validate_enum("INVALID", SampleEnum, "type_field", "TestObject")

        exc = exc_info.value
        assert exc.code == ErrorCode.CORRUPT_DATA.value
        assert "valid_values" in exc.context
        assert "ALPHA" in exc.context["valid_values"]
        assert "BETA" in exc.context["valid_values"]
        assert "GAMMA" in exc.context["valid_values"]
        assert "type_field" in str(exc)

    def test_case_sensitive_lookup(self):
        """Enum lookup is case-sensitive."""
        with pytest.raises(PersistenceException):
            validate_enum("alpha", SampleEnum, "field", "TestObject")


class TestValidatePositive:
    """Tests for validate_positive helper."""

    def test_positive_integer_passes(self):
        """Positive integer passes validation."""
        validate_positive(1, "count", "TestObject")
        validate_positive(100, "count", "TestObject")

    def test_positive_float_passes(self):
        """Positive float passes validation."""
        validate_positive(0.5, "value", "TestObject")
        validate_positive(0.001, "value", "TestObject")

    def test_zero_raises_persistence_exception(self):
        """Zero raises PersistenceException."""
        with pytest.raises(PersistenceException) as exc_info:
            validate_positive(0, "mass", "Ship")

        exc = exc_info.value
        assert exc.code == ErrorCode.CORRUPT_DATA.value
        assert "mass" in str(exc)
        assert exc.context.get("expected") == "positive"

    def test_negative_raises_persistence_exception(self):
        """Negative value raises PersistenceException."""
        with pytest.raises(PersistenceException) as exc_info:
            validate_positive(-5, "radius", "Planet")

        exc = exc_info.value
        assert exc.code == ErrorCode.CORRUPT_DATA.value
        assert "radius" in str(exc)


class TestValidateNonNegative:
    """Tests for validate_non_negative helper."""

    def test_zero_passes(self):
        """Zero passes non-negative validation."""
        validate_non_negative(0, "hp", "Component")

    def test_positive_passes(self):
        """Positive value passes non-negative validation."""
        validate_non_negative(1, "hp", "Component")
        validate_non_negative(100.5, "hp", "Component")

    def test_negative_raises_persistence_exception(self):
        """Negative value raises PersistenceException."""
        with pytest.raises(PersistenceException) as exc_info:
            validate_non_negative(-1, "current_hp", "ComponentState")

        exc = exc_info.value
        assert exc.code == ErrorCode.CORRUPT_DATA.value
        assert "current_hp" in str(exc)
        assert exc.context.get("expected") == "non-negative"


class TestValidateRange:
    """Tests for validate_range helper."""

    def test_value_in_range_passes(self):
        """Value within range passes validation."""
        validate_range(5, 0, 10, "level", "Character")
        validate_range(0, 0, 10, "level", "Character")
        validate_range(10, 0, 10, "level", "Character")

    def test_below_min_raises_persistence_exception(self):
        """Value below min raises PersistenceException with min/max in context."""
        with pytest.raises(PersistenceException) as exc_info:
            validate_range(-5, 0, 100, "health", "Unit")

        exc = exc_info.value
        assert exc.code == ErrorCode.CORRUPT_DATA.value
        assert exc.context.get("min") == 0
        assert exc.context.get("max") == 100
        assert "health" in str(exc)

    def test_above_max_raises_persistence_exception(self):
        """Value above max raises PersistenceException."""
        with pytest.raises(PersistenceException) as exc_info:
            validate_range(150, 0, 100, "health", "Unit")

        exc = exc_info.value
        assert exc.code == ErrorCode.CORRUPT_DATA.value
        assert exc.context.get("min") == 0
        assert exc.context.get("max") == 100


class TestSafeFromDict:
    """Tests for safe_from_dict helper."""

    def test_successful_call_returns_result(self):
        """Successful from_dict call returns the result."""
        def mock_from_dict(data):
            return {"loaded": data["name"]}

        result = safe_from_dict(mock_from_dict, {"name": "Test"}, "TestObject")
        assert result == {"loaded": "Test"}

    def test_key_error_converted_to_persistence_exception_with_chaining(self):
        """KeyError is converted to PersistenceException with __cause__ set."""
        def mock_from_dict(data):
            return data["missing_key"]

        with pytest.raises(PersistenceException) as exc_info:
            safe_from_dict(mock_from_dict, {}, "TestObject")

        exc = exc_info.value
        assert exc.code == ErrorCode.CORRUPT_DATA.value
        assert exc.__cause__ is not None
        assert isinstance(exc.__cause__, KeyError)
        assert "TestObject" in str(exc)

    def test_type_error_converted_to_persistence_exception_with_chaining(self):
        """TypeError is converted to PersistenceException with __cause__ set."""
        def mock_from_dict(data):
            return data["value"] + "string"  # TypeError if value is int

        with pytest.raises(PersistenceException) as exc_info:
            safe_from_dict(mock_from_dict, {"value": 123}, "TestObject")

        exc = exc_info.value
        assert exc.code == ErrorCode.CORRUPT_DATA.value
        assert exc.__cause__ is not None
        assert isinstance(exc.__cause__, TypeError)

    def test_value_error_converted_to_persistence_exception_with_chaining(self):
        """ValueError is converted to PersistenceException with __cause__ set."""
        def mock_from_dict(data):
            raise ValueError("Invalid value format")

        with pytest.raises(PersistenceException) as exc_info:
            safe_from_dict(mock_from_dict, {}, "TestObject")

        exc = exc_info.value
        assert exc.code == ErrorCode.CORRUPT_DATA.value
        assert exc.__cause__ is not None
        assert isinstance(exc.__cause__, ValueError)
