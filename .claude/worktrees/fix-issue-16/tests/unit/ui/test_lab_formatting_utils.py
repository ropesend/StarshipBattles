"""Tests for test lab formatting utilities.

Tests the consolidated format_value function from DUP-UI1-002.
"""

import pytest
from game.ui.screens.test_lab.formatting_utils import format_value


class TestFormatValueNoneAndBasicTypes:
    """Tests for None, bool, and int handling."""

    def test_format_none_full(self):
        """None returns 'None' string."""
        assert format_value(None) == "None"
        assert format_value(None, precision="full") == "None"

    def test_format_none_compact(self):
        """None returns 'None' in compact mode too."""
        assert format_value(None, precision="compact") == "None"

    def test_format_bool_true(self):
        """Bool True formats as 'True'."""
        assert format_value(True) == "True"
        assert format_value(True, precision="compact") == "True"

    def test_format_bool_false(self):
        """Bool False formats as 'False'."""
        assert format_value(False) == "False"
        assert format_value(False, precision="compact") == "False"

    def test_format_int(self):
        """Integers format as plain strings."""
        assert format_value(42) == "42"
        assert format_value(0) == "0"
        assert format_value(-100) == "-100"

    def test_format_int_compact(self):
        """Integers format as plain strings in compact mode."""
        assert format_value(42, precision="compact") == "42"
        assert format_value(0, precision="compact") == "0"

    def test_format_string(self):
        """Strings pass through as-is."""
        assert format_value("hello") == "hello"
        assert format_value("test", precision="compact") == "test"


class TestFormatValueFloatFull:
    """Tests for float formatting in 'full' precision mode."""

    def test_format_integer_like_float(self):
        """Floats that are essentially integers format without decimals."""
        assert format_value(42.0) == "42"
        assert format_value(100.0) == "100"
        assert format_value(-5.0) == "-5"
        assert format_value(0.0) == "0"

    def test_format_probability(self):
        """Values between 0 and 1 (exclusive) format as percentages."""
        assert format_value(0.5) == "50.00%"
        assert format_value(0.123) == "12.30%"
        assert format_value(0.999) == "99.90%"
        assert format_value(0.001) == "0.10%"

    def test_format_very_small_numbers(self):
        """Very small negative numbers use scientific notation."""
        # Note: Small positive values in 0-1 range are treated as probabilities
        assert format_value(-0.00001) == "-1.000000e-05"
        assert format_value(-0.00005) == "-5.000000e-05"

    def test_format_regular_float(self):
        """Regular floats format with 4 decimal places."""
        assert format_value(3.14159) == "3.1416"
        assert format_value(1.5) == "1.5000"
        assert format_value(-2.718) == "-2.7180"

    def test_format_large_float(self):
        """Large floats in full mode still use 4 decimals."""
        assert format_value(150.5) == "150.5000"
        assert format_value(1000.123) == "1000.1230"

    def test_zero_not_scientific(self):
        """Zero should not use scientific notation."""
        # 0.0 is integer-like, should be "0"
        assert format_value(0.0) == "0"


class TestFormatValueFloatCompact:
    """Tests for float formatting in 'compact' precision mode."""

    def test_format_integer_like_float(self):
        """Floats that are essentially integers format without decimals."""
        assert format_value(42.0, precision="compact") == "42"
        assert format_value(-5.0, precision="compact") == "-5"

    def test_format_probability(self):
        """Values between 0 and 1 (exclusive) format as single-decimal percentages."""
        assert format_value(0.5, precision="compact") == "50.0%"
        assert format_value(0.123, precision="compact") == "12.3%"
        assert format_value(0.999, precision="compact") == "99.9%"

    def test_format_very_small_numbers(self):
        """Very small negative numbers use shorter scientific notation."""
        # Note: Small positive values in 0-1 range are treated as probabilities
        assert format_value(-0.0001, precision="compact") == "-1.00e-04"
        assert format_value(-0.00005, precision="compact") == "-5.00e-05"

    def test_format_large_float(self):
        """Large floats (>=100) use single decimal in compact mode."""
        assert format_value(150.5, precision="compact") == "150.5"
        assert format_value(1000.123, precision="compact") == "1000.1"
        assert format_value(100.0, precision="compact") == "100"  # Integer-like

    def test_format_regular_float(self):
        """Regular floats format with 3 decimal places."""
        assert format_value(3.14159, precision="compact") == "3.142"
        assert format_value(1.5, precision="compact") == "1.500"


class TestFormatValueEdgeCases:
    """Edge case tests."""

    def test_boundary_value_one(self):
        """Value of exactly 1.0 is not a probability (integer-like)."""
        assert format_value(1.0) == "1"
        assert format_value(1.0, precision="compact") == "1"

    def test_boundary_value_zero(self):
        """Value of exactly 0.0 is not a probability (integer-like)."""
        assert format_value(0.0) == "0"
        assert format_value(0.0, precision="compact") == "0"

    def test_negative_probability_range(self):
        """Negative values in 0-1 range are NOT probabilities."""
        # -0.5 is not between 0 and 1, so not treated as probability
        assert format_value(-0.5) == "-0.5000"
        assert format_value(-0.5, precision="compact") == "-0.500"

    def test_small_threshold_difference(self):
        """Test the different small-number thresholds between modes."""
        # Negative small values test the threshold difference
        # -0.0005 > -0.0001 in absolute terms, so not scientific in full mode
        assert format_value(-0.0005) == "-0.0005"
        # -0.0005 has |value| < 0.001, so IS scientific in compact mode
        assert format_value(-0.0005, precision="compact") == "-5.00e-04"

    def test_default_precision_is_full(self):
        """Default precision should be 'full'."""
        # Compare same value with explicit and implicit precision
        assert format_value(0.5) == format_value(0.5, precision="full")
        assert format_value(3.14159) == format_value(3.14159, precision="full")
