"""
Tests for SimulationConstants.

PROJ-44 Task 1.5: Create SimulationConstants Class
"""
import pytest


class TestSimulationConstants:
    """Tests for SimulationConstants class."""

    def test_constants_exist(self):
        """SimulationConstants should be importable with expected attributes."""
        from game.core.constants import SimulationConstants

        assert hasattr(SimulationConstants, 'TICKS_PER_SECOND')
        assert hasattr(SimulationConstants, 'WARP_CHARGE_TICKS')
        assert hasattr(SimulationConstants, 'DEFAULT_MAP_EDGE_THRESHOLD')
        assert hasattr(SimulationConstants, 'DEFAULT_MAP_SIZE')
        assert hasattr(SimulationConstants, 'DEFAULT_MAX_TICKS')

    def test_warp_charge_timing(self):
        """Warp charge should be 5 seconds at standard tick rate."""
        from game.core.constants import SimulationConstants

        ticks = SimulationConstants.WARP_CHARGE_TICKS
        tps = SimulationConstants.TICKS_PER_SECOND

        # 500 ticks / 100 tps = 5 seconds
        assert ticks / tps == 5.0

    def test_map_defaults_reasonable(self):
        """Map defaults should be reasonable values."""
        from game.core.constants import SimulationConstants

        # Edge threshold should be much smaller than map size
        assert SimulationConstants.DEFAULT_MAP_EDGE_THRESHOLD < SimulationConstants.DEFAULT_MAP_SIZE / 10

    def test_exported_from_module(self):
        """SimulationConstants should be in __all__."""
        from game.core import constants

        assert 'SimulationConstants' in constants.__all__

    def test_absolute_max_ticks_exists(self):
        """ABSOLUTE_MAX_TICKS should exist as safety ceiling."""
        from game.core.constants import SimulationConstants

        assert hasattr(SimulationConstants, 'ABSOLUTE_MAX_TICKS')
        assert SimulationConstants.ABSOLUTE_MAX_TICKS == 1_000_000

    def test_absolute_max_ticks_greater_than_default(self):
        """ABSOLUTE_MAX_TICKS should be greater than DEFAULT_MAX_TICKS."""
        from game.core.constants import SimulationConstants

        assert SimulationConstants.ABSOLUTE_MAX_TICKS >= SimulationConstants.DEFAULT_MAX_TICKS
