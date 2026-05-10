"""Tests for shared production math utilities.

PROJ-233 Phase 2: Tests for find_limiting_resource_ticks extracted from
ProductionEngine._calculate_tick_expenditure and construction_forecast.
"""
import pytest

from game.strategy.engine.production_math import find_limiting_resource_ticks


class TestFindLimitingResourceTicks:
    """Tests for the limiting-resource formula."""

    def test_empty_remaining_cost_returns_zero(self):
        """No remaining cost means zero ticks needed."""
        result = find_limiting_resource_ticks({}, {"metals": 100})
        assert result == 0.0

    def test_single_resource(self):
        """Single resource: 50 remaining at 100/turn with 100 ticks/turn = 50 ticks."""
        result = find_limiting_resource_ticks(
            {"metals": 50},
            {"metals": 100},
            ticks_per_turn=100
        )
        assert result == pytest.approx(50.0)

    def test_limiting_resource_wins(self):
        """With two resources, the one needing more ticks determines the result."""
        result = find_limiting_resource_ticks(
            {"metals": 50, "organics": 200},
            {"metals": 100, "organics": 100},
            ticks_per_turn=100
        )
        # Metals: 50 / (100/100) = 50 ticks
        # Organics: 200 / (100/100) = 200 ticks (limiting)
        assert result == pytest.approx(200.0)

    def test_zero_rate_returns_none(self):
        """Zero rate for a needed resource means cannot build."""
        result = find_limiting_resource_ticks(
            {"metals": 50},
            {"metals": 0},
            ticks_per_turn=100
        )
        assert result is None

    def test_missing_rate_returns_none(self):
        """Resource not in rate dict means zero rate, cannot build."""
        result = find_limiting_resource_ticks(
            {"metals": 50},
            {},
            ticks_per_turn=100
        )
        assert result is None

    def test_custom_ticks_per_turn(self):
        """With ticks_per_turn=1, result is in turns instead of ticks."""
        # 50 remaining at rate 100/turn, ticks_per_turn=1
        # rate_per_tick = 100/1 = 100
        # ticks = 50 / 100 = 0.5
        result = find_limiting_resource_ticks(
            {"metals": 50},
            {"metals": 100},
            ticks_per_turn=1
        )
        assert result == pytest.approx(0.5)

    def test_negative_rate_returns_none(self):
        """Negative rate should be treated as zero (cannot build)."""
        result = find_limiting_resource_ticks(
            {"metals": 50},
            {"metals": -10},
            ticks_per_turn=100
        )
        assert result is None

    def test_multiple_resources_all_with_rates(self):
        """Multiple resources each with rates, verifies correct limiting."""
        result = find_limiting_resource_ticks(
            {"metals": 100, "organics": 50, "vapors": 300},
            {"metals": 200, "organics": 200, "vapors": 200},
            ticks_per_turn=100
        )
        # Metals: 100 / (200/100) = 50 ticks
        # Organics: 50 / (200/100) = 25 ticks
        # Vapors: 300 / (200/100) = 150 ticks (limiting)
        assert result == pytest.approx(150.0)
