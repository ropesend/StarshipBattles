"""Tests for error code enumeration in game.core.error_codes.

PROJ-45 Phase 1: Foundation - Error Code Tests

These tests verify:
- All error codes are unique
- Error code naming conventions (X###)
- Category organization
"""
import pytest
import re

from game.core.error_codes import ErrorCode


class TestErrorCodeUniqueness:
    """Tests to verify all error codes are unique."""

    def test_all_codes_are_unique(self):
        """Every error code value must be unique."""
        values = [code.value for code in ErrorCode]
        assert len(values) == len(set(values)), "Duplicate error code values found"

    def test_all_names_are_unique(self):
        """Every error code name must be unique."""
        names = [code.name for code in ErrorCode]
        assert len(names) == len(set(names)), "Duplicate error code names found"


class TestErrorCodeNamingConvention:
    """Tests for error code naming convention."""

    def test_code_format_pattern(self):
        """All codes follow X### format (letter + 3 digits)."""
        pattern = re.compile(r'^[A-Z]\d{3}$')
        for code in ErrorCode:
            assert pattern.match(code.value), f"{code.name} has invalid format: {code.value}"

    def test_validation_codes_start_with_v(self):
        """Validation category codes start with 'V'."""
        # Note: INVALID_STATE, INVALID_FORMAT are not validation codes
        validation_names = ('VALIDATION', 'INVALID_COMPONENT', 'INVALID_TYPE', 'OUT_OF_RANGE', 'SCHEMA')
        validation_codes = [c for c in ErrorCode if any(c.name.startswith(n) for n in validation_names)]
        for code in validation_codes:
            assert code.value.startswith('V'), f"{code.name} should start with V"

    def test_state_codes_start_with_s(self):
        """State category codes start with 'S'."""
        state_codes = [c for c in ErrorCode if c.name.startswith('STATE') or c.name.startswith('NOT_INITIALIZED')]
        for code in state_codes:
            assert code.value.startswith('S'), f"{code.name} should start with S"

    def test_resource_codes_start_with_r(self):
        """Resource category codes start with 'R'."""
        resource_codes = [c for c in ErrorCode if c.name.startswith('RESOURCE') or c.name == 'INVALID_FORMAT']
        for code in resource_codes:
            assert code.value.startswith('R'), f"{code.name} should start with R"

    def test_persistence_codes_start_with_p(self):
        """Persistence category codes start with 'P'."""
        persistence_codes = [c for c in ErrorCode if c.name.startswith('SAVE') or c.name.startswith('LOAD') or c.name.startswith('CORRUPT')]
        for code in persistence_codes:
            assert code.value.startswith('P'), f"{code.name} should start with P"

    def test_formula_codes_start_with_f(self):
        """Formula category codes start with 'F'."""
        formula_codes = [c for c in ErrorCode if c.name.startswith('SYNTAX') or c.name.startswith('UNDEFINED') or c.name.startswith('EVAL')]
        for code in formula_codes:
            assert code.value.startswith('F'), f"{code.name} should start with F"

    def test_component_codes_start_with_c(self):
        """Component category codes start with 'C'."""
        component_codes = [c for c in ErrorCode if c.name.startswith('COMPONENT')]
        for code in component_codes:
            assert code.value.startswith('C'), f"{code.name} should start with C"


class TestErrorCodeCategories:
    """Tests for error code category organization."""

    def test_has_validation_codes(self):
        """At least one validation code exists."""
        v_codes = [c for c in ErrorCode if c.value.startswith('V')]
        assert len(v_codes) > 0, "No validation codes found"

    def test_has_state_codes(self):
        """At least one state code exists."""
        s_codes = [c for c in ErrorCode if c.value.startswith('S')]
        assert len(s_codes) > 0, "No state codes found"

    def test_has_resource_codes(self):
        """At least one resource code exists."""
        r_codes = [c for c in ErrorCode if c.value.startswith('R')]
        assert len(r_codes) > 0, "No resource codes found"

    def test_has_persistence_codes(self):
        """At least one persistence code exists."""
        p_codes = [c for c in ErrorCode if c.value.startswith('P')]
        assert len(p_codes) > 0, "No persistence codes found"

    def test_has_formula_codes(self):
        """At least one formula code exists."""
        f_codes = [c for c in ErrorCode if c.value.startswith('F')]
        assert len(f_codes) > 0, "No formula codes found"

    def test_has_component_codes(self):
        """At least one component code exists."""
        c_codes = [c for c in ErrorCode if c.value.startswith('C')]
        assert len(c_codes) > 0, "No component codes found"


class TestErrorCodeAccess:
    """Tests for accessing error codes."""

    def test_access_by_name(self):
        """Error codes can be accessed by name."""
        assert ErrorCode.VALIDATION_FAILED.value == "V001"

    def test_access_by_value(self):
        """Error codes can be looked up by value."""
        code = ErrorCode("V001")
        assert code == ErrorCode.VALIDATION_FAILED

    def test_iteration(self):
        """Can iterate over all error codes."""
        codes = list(ErrorCode)
        assert len(codes) > 0
        for code in codes:
            assert isinstance(code, ErrorCode)

    def test_string_representation(self):
        """Error codes have useful string representation."""
        code = ErrorCode.VALIDATION_FAILED
        assert "VALIDATION_FAILED" in repr(code)


class TestErrorCodeMinimumSet:
    """Tests to verify minimum required error codes exist."""

    def test_validation_failed_exists(self):
        """VALIDATION_FAILED code exists."""
        assert ErrorCode.VALIDATION_FAILED.value == "V001"

    def test_state_frozen_exists(self):
        """STATE_FROZEN code exists."""
        assert ErrorCode.STATE_FROZEN.value == "S001"

    def test_resource_not_found_exists(self):
        """RESOURCE_NOT_FOUND code exists."""
        assert ErrorCode.RESOURCE_NOT_FOUND.value == "R001"

    def test_save_failed_exists(self):
        """SAVE_FAILED code exists."""
        assert ErrorCode.SAVE_FAILED.value == "P001"

