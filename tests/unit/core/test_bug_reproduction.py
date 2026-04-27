import pytest
from game.core.validation import ValidationResult

def test_validation_result_has_first_error():
    """Reproduce AttributeError: 'ValidationResult' object has no attribute 'first_error'"""
    result = ValidationResult(is_valid=False, errors=["Test error"])
    # This should fail if the bug is present
    assert result.first_error == "Test error"
