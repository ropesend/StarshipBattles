"""
Unit tests for fleet navigation service pure unit tests.

Tests NavigationState and NavigationStep data structures.
"""
import pytest
from unittest.mock import MagicMock

from game.core.hex_math import HexCoord


class TestNavigationState:
    """Tests for NavigationState data structure."""

    def test_navigation_service_exists(self):
        """Fleet navigation service module can be imported."""
        from game.strategy.services import fleet_navigation_service
        assert fleet_navigation_service is not None

    def test_navigation_state_creation(self):
        """NavigationState can be created."""
        from game.strategy.services.fleet_navigation_service import NavigationState
        # Create with actual required params
        state = NavigationState(
            location=HexCoord(0, 0),
            path=(),
            orders=(),
            speed=10.0,
            can_warp=False
        )
        assert state.location == HexCoord(0, 0)
        assert state.speed == 10.0


class TestNavigationStep:
    """Tests for NavigationStep data structure."""

    def test_navigation_step_exists(self):
        """NavigationStep class exists."""
        from game.strategy.services.fleet_navigation_service import NavigationStep
        assert NavigationStep is not None
