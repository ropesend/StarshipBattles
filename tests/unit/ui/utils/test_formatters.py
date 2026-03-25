"""Tests for game.ui.utils.formatters module."""
import pytest


class TestFormatCompactNumber:
    """Tests for format_compact_number utility."""

    def test_zero(self):
        from game.ui.utils.formatters import format_compact_number
        assert format_compact_number(0) == "0"

    def test_small_number(self):
        from game.ui.utils.formatters import format_compact_number
        assert format_compact_number(500) == "500"

    def test_one(self):
        from game.ui.utils.formatters import format_compact_number
        assert format_compact_number(1) == "1"

    def test_exactly_1000(self):
        from game.ui.utils.formatters import format_compact_number
        assert format_compact_number(1000) == "1k"

    def test_1500(self):
        from game.ui.utils.formatters import format_compact_number
        assert format_compact_number(1500) == "2k"

    def test_15000(self):
        from game.ui.utils.formatters import format_compact_number
        assert format_compact_number(15000) == "15k"

    def test_999999(self):
        from game.ui.utils.formatters import format_compact_number
        assert format_compact_number(999999) == "1000k"

    def test_exactly_1_million(self):
        from game.ui.utils.formatters import format_compact_number
        assert format_compact_number(1_000_000) == "1.0M"

    def test_2_5_million(self):
        from game.ui.utils.formatters import format_compact_number
        assert format_compact_number(2_500_000) == "2.5M"

    def test_float_small(self):
        from game.ui.utils.formatters import format_compact_number
        assert format_compact_number(42.7) == "42"

    def test_negative_small(self):
        from game.ui.utils.formatters import format_compact_number
        result = format_compact_number(-500)
        assert result == "-500"

    def test_negative_thousands(self):
        from game.ui.utils.formatters import format_compact_number
        # Negative numbers below threshold are formatted as int
        result = format_compact_number(-1500)
        assert result == "-1500"


class TestGetDamageColor:
    """Tests for get_damage_color utility."""

    def test_full_health(self):
        from game.ui.utils.formatters import get_damage_color
        from game.ui.colors import HP_HEALTHY
        assert get_damage_color(1.0) == HP_HEALTHY

    def test_75_percent(self):
        from game.ui.utils.formatters import get_damage_color
        from game.ui.colors import HP_HEALTHY
        assert get_damage_color(0.75) == HP_HEALTHY

    def test_50_percent(self):
        from game.ui.utils.formatters import get_damage_color
        from game.ui.colors import HP_HEALTHY
        assert get_damage_color(0.50) == HP_HEALTHY

    def test_49_percent(self):
        from game.ui.utils.formatters import get_damage_color
        from game.ui.colors import HP_DAMAGED
        assert get_damage_color(0.49) == HP_DAMAGED

    def test_25_percent(self):
        from game.ui.utils.formatters import get_damage_color
        from game.ui.colors import HP_DAMAGED
        assert get_damage_color(0.25) == HP_DAMAGED

    def test_24_percent(self):
        from game.ui.utils.formatters import get_damage_color
        from game.ui.colors import HP_CRITICAL
        assert get_damage_color(0.24) == HP_CRITICAL

    def test_10_percent(self):
        from game.ui.utils.formatters import get_damage_color
        from game.ui.colors import HP_CRITICAL
        assert get_damage_color(0.10) == HP_CRITICAL

    def test_zero_health(self):
        from game.ui.utils.formatters import get_damage_color
        from game.ui.colors import HP_DESTROYED
        assert get_damage_color(0.0) == HP_DESTROYED

    def test_negative_health(self):
        from game.ui.utils.formatters import get_damage_color
        from game.ui.colors import HP_DESTROYED
        assert get_damage_color(-0.1) == HP_DESTROYED

    def test_inactive(self):
        from game.ui.utils.formatters import get_damage_color
        from game.ui.colors import HP_DESTROYED
        assert get_damage_color(1.0, is_active=False) == HP_DESTROYED

    def test_inactive_with_low_health(self):
        from game.ui.utils.formatters import get_damage_color
        from game.ui.colors import HP_DESTROYED
        assert get_damage_color(0.1, is_active=False) == HP_DESTROYED
