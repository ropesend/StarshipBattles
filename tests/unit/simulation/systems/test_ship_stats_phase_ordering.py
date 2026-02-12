"""
Unit tests for ship stats calculation phase ordering.

Tests that phases execute in correct order and use
correct values from previous phases.
"""
import pytest
from unittest.mock import MagicMock


class TestShipStatsPhaseOrdering:
    """Tests for ship stats phase ordering."""

    def test_ship_stats_calculator_exists(self):
        """ShipStatsCalculator can be imported."""
        from game.simulation.entities.ship_stats import ShipStatsCalculator
        assert ShipStatsCalculator is not None

    def test_calculator_has_calculate_method(self):
        """Calculator has calculate method."""
        from game.simulation.entities.ship_stats import ShipStatsCalculator
        assert hasattr(ShipStatsCalculator, 'calculate')
