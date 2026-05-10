"""Tests for game.ui.utils.formatters module."""
import pytest

from game.ui.utils.formatters import (
    format_compact_number,
    format_signed_float,
    get_damage_color,
)
from game.ui.colors import HP_CRITICAL, HP_DAMAGED, HP_DESTROYED, HP_HEALTHY


class TestFormatCompactNumber:
    """Tests for format_compact_number utility."""

    def test_zero(self):
        assert format_compact_number(0) == "0"

    def test_small_number(self):
        assert format_compact_number(500) == "500"

    def test_one(self):
        assert format_compact_number(1) == "1"

    def test_exactly_1000(self):
        assert format_compact_number(1000) == "1k"

    def test_1500(self):
        assert format_compact_number(1500) == "2k"

    def test_15000(self):
        assert format_compact_number(15000) == "15k"

    def test_999999(self):
        assert format_compact_number(999999) == "1000k"

    def test_exactly_1_million(self):
        assert format_compact_number(1_000_000) == "1.0M"

    def test_2_5_million(self):
        assert format_compact_number(2_500_000) == "2.5M"

    def test_float_small(self):
        assert format_compact_number(42.7) == "42"

    def test_negative_small(self):
        result = format_compact_number(-500)
        assert result == "-500"

    def test_negative_thousands(self):
        # Negative numbers below threshold are formatted as int
        result = format_compact_number(-1500)
        assert result == "-1500"


class TestGetDamageColor:
    """Tests for get_damage_color utility."""

    def test_full_health(self):
        assert get_damage_color(1.0) == HP_HEALTHY

    def test_75_percent(self):
        assert get_damage_color(0.75) == HP_HEALTHY

    def test_50_percent(self):
        assert get_damage_color(0.50) == HP_HEALTHY

    def test_49_percent(self):
        assert get_damage_color(0.49) == HP_DAMAGED

    def test_25_percent(self):
        assert get_damage_color(0.25) == HP_DAMAGED

    def test_24_percent(self):
        assert get_damage_color(0.24) == HP_CRITICAL

    def test_10_percent(self):
        assert get_damage_color(0.10) == HP_CRITICAL

    def test_zero_health(self):
        assert get_damage_color(0.0) == HP_DESTROYED

    def test_negative_health(self):
        assert get_damage_color(-0.1) == HP_DESTROYED

    def test_inactive(self):
        assert get_damage_color(1.0, is_active=False) == HP_DESTROYED

    def test_inactive_with_low_health(self):
        assert get_damage_color(0.1, is_active=False) == HP_DESTROYED


class TestFormatSignedFloat:
    """PROJ-289 Phase 1 Task 1.1: signed-prefix float formatting for the
    planet report panel's per-species sub-block + per-resource grid."""

    def test_positive_gets_plus_prefix(self):
        assert format_signed_float(1.2) == "+1.2"

    def test_negative_keeps_native_minus(self):
        assert format_signed_float(-0.8) == "-0.8"

    def test_zero_renders_as_signed_zero(self):
        """Zero gets the `+` prefix (no native sign on 0). Keeps grid
        alignment consistent across positive / zero / negative cells."""
        assert format_signed_float(0.0) == "+0.0"

    def test_decimals_kwarg_controls_precision(self):
        assert format_signed_float(1.234, decimals=2) == "+1.23"
        assert format_signed_float(-1.234, decimals=2) == "-1.23"
        assert format_signed_float(1.0, decimals=0) == "+1"

    def test_default_decimals_is_one(self):
        assert format_signed_float(1.0) == "+1.0"

    def test_large_positive(self):
        assert format_signed_float(1234.5) == "+1234.5"

    def test_very_small_positive(self):
        assert format_signed_float(0.001, decimals=3) == "+0.001"

    def test_negative_zero_input_renders_as_signed_zero(self):
        """`-0.0` is mathematically zero — the helper must NOT emit `-0.0`
        because that would break the "negative = red" rule downstream."""
        assert format_signed_float(-0.0) == "+0.0"
