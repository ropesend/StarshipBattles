"""
Tests for FleetNavigationService data structures.

Tests for NavigationState, PathSegment, NavigationStep dataclasses
and path recalculation logic.

PROJ-35: Unified fleet navigation logic for UI projection and turn execution.
"""
import pytest
from unittest.mock import MagicMock

from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import FleetOrder, OrderType


class TestNavigationState:
    """Tests for NavigationState dataclass and factory method."""

    def test_navigation_state_from_fleet_creates_correct_snapshot(self):
        """NavigationState.from_fleet() should capture all required fleet data."""
        from game.strategy.services.fleet_navigation_service import NavigationState

        # Create a fleet with known state
        fleet = Fleet(
            fleet_id='test-fleet',
            owner_id=0,
            location=HexCoord(5, 3),
            speed=7.0
        )
        fleet.path = [HexCoord(6, 3), HexCoord(7, 3)]
        fleet.orders = [FleetOrder(OrderType.MOVE, HexCoord(7, 3))]

        # PROJ-210: Mock can_use_warp via capabilities property
        fleet._capabilities = MagicMock()
        fleet._capabilities.can_use_warp = MagicMock(return_value=True)

        state = NavigationState.from_fleet(fleet)

        assert state.location == HexCoord(5, 3)
        assert state.path == (HexCoord(6, 3), HexCoord(7, 3))  # Tuple, immutable
        assert len(state.orders) == 1
        assert state.orders[0].type == OrderType.MOVE
        assert state.speed == 7.0
        assert state.can_warp is True

    def test_navigation_state_is_immutable(self):
        """NavigationState should be frozen (immutable)."""
        from game.strategy.services.fleet_navigation_service import NavigationState

        state = NavigationState(
            location=HexCoord(0, 0),
            path=(),
            orders=(),
            speed=5.0,
            can_warp=False
        )

        with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
            state.location = HexCoord(1, 1)

    def test_navigation_state_path_is_tuple(self):
        """Path should be stored as tuple for immutability."""
        from game.strategy.services.fleet_navigation_service import NavigationState

        fleet = Fleet(
            fleet_id='test',
            owner_id=0,
            location=HexCoord(0, 0),
            speed=5.0
        )
        fleet.path = [HexCoord(1, 0), HexCoord(2, 0)]  # List in fleet
        fleet.can_use_warp = MagicMock(return_value=False)

        state = NavigationState.from_fleet(fleet)

        assert isinstance(state.path, tuple)

    def test_navigation_state_from_fleet_handles_empty_path(self):
        """from_fleet() should handle fleet with empty path."""
        from game.strategy.services.fleet_navigation_service import NavigationState

        fleet = Fleet(
            fleet_id='test',
            owner_id=0,
            location=HexCoord(0, 0),
            speed=5.0
        )
        fleet.path = []
        fleet.orders = []
        fleet.can_use_warp = MagicMock(return_value=True)

        state = NavigationState.from_fleet(fleet)

        assert state.path == ()
        assert state.orders == ()

    def test_navigation_state_can_warp_false(self):
        """from_fleet() should correctly capture can_warp=False."""
        from game.strategy.services.fleet_navigation_service import NavigationState

        fleet = Fleet(
            fleet_id='test',
            owner_id=0,
            location=HexCoord(0, 0),
            speed=5.0
        )
        fleet.can_use_warp = MagicMock(return_value=False)

        state = NavigationState.from_fleet(fleet)

        assert state.can_warp is False


class TestPathSegment:
    """Tests for PathSegment dataclass."""

    def test_path_segment_to_dict(self):
        """PathSegment.to_dict() should return correct dictionary."""
        from game.strategy.services.fleet_navigation_service import PathSegment

        segment = PathSegment(
            start=HexCoord(0, 0),
            end=HexCoord(1, 0),
            turn=2,
            is_warp=False
        )

        result = segment.to_dict()

        assert result['start'] == HexCoord(0, 0)
        assert result['end'] == HexCoord(1, 0)
        assert result['turn'] == 2
        assert result['is_warp'] is False
        assert result['hex'] == HexCoord(1, 0)  # Legacy field

    def test_path_segment_warp_flag(self):
        """PathSegment should correctly store is_warp flag."""
        from game.strategy.services.fleet_navigation_service import PathSegment

        segment = PathSegment(
            start=HexCoord(0, 0),
            end=HexCoord(5, 0),  # Distance > 1, warp jump
            turn=0,
            is_warp=True
        )

        assert segment.is_warp is True


class TestNavigationStep:
    """Tests for NavigationStep dataclass."""

    def test_navigation_step_defaults(self):
        """NavigationStep should have order_complete=False by default."""
        from game.strategy.services.fleet_navigation_service import (
            NavigationStep, NavigationState
        )

        state = NavigationState(
            location=HexCoord(1, 0),
            path=(),
            orders=(),
            speed=5.0,
            can_warp=False
        )

        step = NavigationStep(
            next_hex=HexCoord(1, 0),
            new_state=state
        )

        assert step.order_complete is False

    def test_navigation_step_with_order_complete(self):
        """NavigationStep can mark order as complete."""
        from game.strategy.services.fleet_navigation_service import (
            NavigationStep, NavigationState
        )

        state = NavigationState(
            location=HexCoord(2, 0),
            path=(),
            orders=(),
            speed=5.0,
            can_warp=False
        )

        step = NavigationStep(
            next_hex=HexCoord(2, 0),
            new_state=state,
            order_complete=True
        )

        assert step.order_complete is True


class TestNeedsPathRecalculation:
    """Tests for FleetNavigationService._needs_path_recalculation()."""

    def test_needs_recalc_true_when_destination_different(self):
        """Should return True when path endpoint differs from destination."""
        from game.strategy.services.fleet_navigation_service import (
            FleetNavigationService, NavigationState
        )

        service = FleetNavigationService()
        state = NavigationState(
            location=HexCoord(0, 0),
            path=(HexCoord(1, 0), HexCoord(2, 0)),  # Ends at (2, 0)
            orders=(),
            speed=5.0,
            can_warp=True
        )
        destination = HexCoord(5, 0)  # Different from path end

        result = service._needs_path_recalculation(state, destination)

        assert result is True

    def test_needs_recalc_false_when_destination_matches(self):
        """Should return False when path endpoint matches destination."""
        from game.strategy.services.fleet_navigation_service import (
            FleetNavigationService, NavigationState
        )

        service = FleetNavigationService()
        state = NavigationState(
            location=HexCoord(0, 0),
            path=(HexCoord(1, 0), HexCoord(2, 0)),  # Ends at (2, 0)
            orders=(),
            speed=5.0,
            can_warp=True
        )
        destination = HexCoord(2, 0)  # Same as path end

        result = service._needs_path_recalculation(state, destination)

        assert result is False

    def test_needs_recalc_true_when_path_empty(self):
        """Should return True when path is empty (need to calculate)."""
        from game.strategy.services.fleet_navigation_service import (
            FleetNavigationService, NavigationState
        )

        service = FleetNavigationService()
        state = NavigationState(
            location=HexCoord(0, 0),
            path=(),  # Empty path
            orders=(),
            speed=5.0,
            can_warp=True
        )
        destination = HexCoord(2, 0)

        result = service._needs_path_recalculation(state, destination)

        assert result is True
