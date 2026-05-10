"""
Tests for calculate_design_stats error handling (PROJ-254 Phase 3).

Verifies that invalid designs raise exceptions instead of silently
returning stale expected_stats data.
"""
import pytest

from game.simulation.entities.ship_design_stats import calculate_design_stats
from game.core.registry import GameRegistries


class TestDesignStatsNoFallback:
    """calculate_design_stats should raise on invalid design, not return stale data."""

    def test_invalid_design_raises_not_returns_stale(self, fresh_registries):
        """Completely invalid design data should raise, not return expected_stats."""
        bad_design = {
            'expected_stats': {'max_hp': 999},  # Stale data that should NOT be used
            'layers': 'not_a_dict',  # Invalid
        }
        with pytest.raises(Exception):
            calculate_design_stats(bad_design, fresh_registries)

    def test_valid_design_works(self, fresh_registries):
        """Valid design should return computed stats normally."""
        from tests.fixtures.ships import create_test_ship
        ship = create_test_ship(
            name="Test", x=0, y=0,
            add_bridge=True,
            registries=fresh_registries,
        )
        design = ship.to_dict()
        result = calculate_design_stats(design, fresh_registries)
        assert result['max_hp'] > 0
        assert result['mass'] > 0
