"""
Tests for RetreatManager (PROJ-29 SIM-03 Phase 2)

Tests the extracted RetreatManager class that handles:
- Retreat requests (edge and warp methods)
- Retreat state tracking and updates
- Ship escape detection
- Reinforcement handling
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from dataclasses import dataclass
from typing import Dict, Optional, Tuple, List

# The class we're testing (will be created after tests)
from game.simulation.managers.retreat_manager import (
    RetreatManager,
    RetreatState,
    RetreatMethod,
)


# === Fixtures ===

@pytest.fixture
def mock_ship():
    """Create a mock Ship object."""
    ship = Mock()
    ship.name = "Test Ship"
    ship.is_alive = True
    ship.x = 50000
    ship.y = 50000
    return ship


@pytest.fixture
def default_map_bounds():
    """Default map bounds for testing."""
    return (0, 0, 100000, 100000)


@pytest.fixture
def retreat_manager(default_map_bounds):
    """Create a RetreatManager with default map bounds."""
    return RetreatManager(map_bounds=default_map_bounds)


@pytest.fixture
def ship_id_map(mock_ship):
    """Create a ship ID mapping."""
    return {id(mock_ship): "test-ship-id"}


# === Initialization Tests ===

class TestRetreatManagerInit:
    """Tests for RetreatManager initialization."""

    def test_init_with_map_bounds(self, default_map_bounds):
        """RetreatManager initializes with map bounds."""
        manager = RetreatManager(map_bounds=default_map_bounds)
        assert manager.map_bounds == default_map_bounds

    def test_init_empty_state(self, retreat_manager):
        """RetreatManager starts with empty state."""
        assert retreat_manager.retreating_ships == {}
        assert retreat_manager.escaped_ships == []

    def test_init_no_escape_callback(self, retreat_manager):
        """RetreatManager starts with no escape callback."""
        assert retreat_manager._on_ship_escaped is None


# === Request Retreat Tests ===

class TestRetreatManagerRequestRetreat:
    """Tests for RetreatManager.request_retreat()."""

    def test_request_retreat_fails_for_dead_ship(self, retreat_manager, mock_ship, ship_id_map):
        """request_retreat fails for dead ship."""
        mock_ship.is_alive = False

        success, error = retreat_manager.request_retreat(
            mock_ship, ship_id_map, method=RetreatMethod.EDGE
        )

        assert success is False
        assert "not alive" in error.lower()

    def test_request_retreat_fails_for_unknown_ship(self, retreat_manager, mock_ship):
        """request_retreat fails for ship not in ID map."""
        success, error = retreat_manager.request_retreat(
            mock_ship, {}, method=RetreatMethod.EDGE
        )

        assert success is False
        assert "not found" in error.lower()

    def test_request_retreat_fails_if_already_retreating(self, retreat_manager, mock_ship, ship_id_map):
        """request_retreat fails if ship already retreating."""
        ship_id = ship_id_map[id(mock_ship)]
        retreat_manager.retreating_ships[ship_id] = RetreatState(
            method=RetreatMethod.EDGE, target=(0, 50000)
        )

        success, error = retreat_manager.request_retreat(
            mock_ship, ship_id_map, method=RetreatMethod.EDGE
        )

        assert success is False
        assert "already retreating" in error.lower()

    def test_request_retreat_edge_creates_state(self, retreat_manager, mock_ship, ship_id_map):
        """request_retreat with EDGE method creates proper state."""
        success, error = retreat_manager.request_retreat(
            mock_ship, ship_id_map, method=RetreatMethod.EDGE
        )

        assert success is True
        assert error is None

        ship_id = ship_id_map[id(mock_ship)]
        assert ship_id in retreat_manager.retreating_ships
        state = retreat_manager.retreating_ships[ship_id]
        assert state.method == RetreatMethod.EDGE
        assert state.target is not None

    def test_request_retreat_warp_creates_state(self, retreat_manager, mock_ship, ship_id_map):
        """request_retreat with WARP method creates proper state."""
        success, error = retreat_manager.request_retreat(
            mock_ship, ship_id_map, method=RetreatMethod.WARP
        )

        assert success is True
        ship_id = ship_id_map[id(mock_ship)]
        state = retreat_manager.retreating_ships[ship_id]
        assert state.method == RetreatMethod.WARP
        assert state.charge_ticks == 0
        assert state.required_ticks == 500

    def test_request_retreat_edge_calculates_nearest_edge(self, retreat_manager, ship_id_map):
        """request_retreat calculates target for nearest edge."""
        # Ship close to left edge
        mock_ship = Mock()
        mock_ship.is_alive = True
        mock_ship.x = 100
        mock_ship.y = 50000
        ship_id_map[id(mock_ship)] = "left-ship"

        retreat_manager.request_retreat(mock_ship, ship_id_map, method=RetreatMethod.EDGE)

        state = retreat_manager.retreating_ships["left-ship"]
        assert state.target == (0, 50000)  # Should target left edge


# === Cancel Retreat Tests ===

class TestRetreatManagerCancelRetreat:
    """Tests for RetreatManager.cancel_retreat()."""

    def test_cancel_retreat_removes_state(self, retreat_manager, mock_ship, ship_id_map):
        """cancel_retreat removes retreat state."""
        ship_id = ship_id_map[id(mock_ship)]
        retreat_manager.retreating_ships[ship_id] = RetreatState(
            method=RetreatMethod.EDGE, target=(0, 50000)
        )

        success, error = retreat_manager.cancel_retreat(mock_ship, ship_id_map)

        assert success is True
        assert ship_id not in retreat_manager.retreating_ships

    def test_cancel_retreat_fails_when_not_retreating(self, retreat_manager, mock_ship, ship_id_map):
        """cancel_retreat fails when ship not retreating."""
        success, error = retreat_manager.cancel_retreat(mock_ship, ship_id_map)

        assert success is False
        assert "not retreating" in error.lower()


# === Update Retreats Tests ===

class TestRetreatManagerUpdateRetreats:
    """Tests for RetreatManager.update()."""

    def test_update_increments_warp_charge(self, retreat_manager, mock_ship, ship_id_map):
        """update increments warp charge ticks."""
        ship_id = ship_id_map[id(mock_ship)]
        retreat_manager.retreating_ships[ship_id] = RetreatState(
            method=RetreatMethod.WARP, charge_ticks=0, required_ticks=500
        )

        def get_ship_by_id(sid):
            return mock_ship if sid == ship_id else None

        retreat_manager.update(get_ship_by_id)

        assert retreat_manager.retreating_ships[ship_id].charge_ticks == 1

    def test_update_warp_escape_when_charged(self, retreat_manager, mock_ship, ship_id_map):
        """update triggers escape when warp fully charged."""
        ship_id = ship_id_map[id(mock_ship)]
        retreat_manager.retreating_ships[ship_id] = RetreatState(
            method=RetreatMethod.WARP, charge_ticks=499, required_ticks=500
        )

        def get_ship_by_id(sid):
            return mock_ship if sid == ship_id else None

        retreat_manager.update(get_ship_by_id)

        # Ship should have escaped
        assert ship_id in retreat_manager.escaped_ships
        assert ship_id not in retreat_manager.retreating_ships

    def test_update_edge_escape_at_map_edge(self, retreat_manager, ship_id_map):
        """update triggers escape when ship reaches map edge."""
        # Ship at left edge
        mock_ship = Mock()
        mock_ship.is_alive = True
        mock_ship.x = 100  # Within edge threshold
        mock_ship.y = 50000
        ship_id = "edge-ship"
        ship_id_map[id(mock_ship)] = ship_id

        retreat_manager.retreating_ships[ship_id] = RetreatState(
            method=RetreatMethod.EDGE, target=(0, 50000)
        )

        def get_ship_by_id(sid):
            return mock_ship if sid == ship_id else None

        retreat_manager.update(get_ship_by_id)

        assert ship_id in retreat_manager.escaped_ships

    def test_update_removes_dead_ships_from_retreat(self, retreat_manager, mock_ship, ship_id_map):
        """update removes dead ships from retreat tracking."""
        ship_id = ship_id_map[id(mock_ship)]
        retreat_manager.retreating_ships[ship_id] = RetreatState(
            method=RetreatMethod.WARP, charge_ticks=0
        )

        mock_ship.is_alive = False

        def get_ship_by_id(sid):
            return mock_ship if sid == ship_id else None

        retreat_manager.update(get_ship_by_id)

        # Dead ship should be removed from retreating but added to escaped
        assert ship_id not in retreat_manager.retreating_ships

    def test_update_calls_escape_callback(self, retreat_manager, mock_ship, ship_id_map):
        """update calls escape callback when ship escapes."""
        ship_id = ship_id_map[id(mock_ship)]
        retreat_manager.retreating_ships[ship_id] = RetreatState(
            method=RetreatMethod.WARP, charge_ticks=499, required_ticks=500
        )

        callback = Mock()
        retreat_manager.set_on_ship_escaped(callback)

        def get_ship_by_id(sid):
            return mock_ship if sid == ship_id else None

        retreat_manager.update(get_ship_by_id)

        callback.assert_called_once_with(mock_ship)


# === Find Nearest Edge Tests ===

class TestRetreatManagerFindNearestEdge:
    """Tests for RetreatManager.find_nearest_edge()."""

    def test_find_nearest_edge_left(self, retreat_manager):
        """find_nearest_edge finds left edge when closest."""
        mock_ship = Mock()
        mock_ship.x = 100
        mock_ship.y = 50000

        target = retreat_manager.find_nearest_edge(mock_ship)

        assert target == (0, 50000)

    def test_find_nearest_edge_right(self, retreat_manager):
        """find_nearest_edge finds right edge when closest."""
        mock_ship = Mock()
        mock_ship.x = 99900
        mock_ship.y = 50000

        target = retreat_manager.find_nearest_edge(mock_ship)

        assert target == (100000, 50000)

    def test_find_nearest_edge_top(self, retreat_manager):
        """find_nearest_edge finds top edge when closest."""
        mock_ship = Mock()
        mock_ship.x = 50000
        mock_ship.y = 100

        target = retreat_manager.find_nearest_edge(mock_ship)

        assert target == (50000, 0)

    def test_find_nearest_edge_bottom(self, retreat_manager):
        """find_nearest_edge finds bottom edge when closest."""
        mock_ship = Mock()
        mock_ship.x = 50000
        mock_ship.y = 99900

        target = retreat_manager.find_nearest_edge(mock_ship)

        assert target == (50000, 100000)


# === At Map Edge Tests ===

class TestRetreatManagerAtMapEdge:
    """Tests for RetreatManager.at_map_edge()."""

    def test_at_map_edge_left(self, retreat_manager):
        """at_map_edge detects left edge."""
        mock_ship = Mock()
        mock_ship.x = 400
        mock_ship.y = 50000

        assert retreat_manager.at_map_edge(mock_ship) is True

    def test_at_map_edge_right(self, retreat_manager):
        """at_map_edge detects right edge."""
        mock_ship = Mock()
        mock_ship.x = 99600
        mock_ship.y = 50000

        assert retreat_manager.at_map_edge(mock_ship) is True

    def test_at_map_edge_center(self, retreat_manager):
        """at_map_edge returns False for center position."""
        mock_ship = Mock()
        mock_ship.x = 50000
        mock_ship.y = 50000

        assert retreat_manager.at_map_edge(mock_ship) is False

    def test_at_map_edge_custom_threshold(self, retreat_manager):
        """at_map_edge respects custom threshold."""
        mock_ship = Mock()
        mock_ship.x = 800
        mock_ship.y = 50000

        assert retreat_manager.at_map_edge(mock_ship, threshold=500) is False
        assert retreat_manager.at_map_edge(mock_ship, threshold=1000) is True


# === Is Retreating Tests ===

class TestRetreatManagerIsRetreating:
    """Tests for RetreatManager.is_retreating()."""

    def test_is_retreating_true(self, retreat_manager, mock_ship, ship_id_map):
        """is_retreating returns True for retreating ship."""
        ship_id = ship_id_map[id(mock_ship)]
        retreat_manager.retreating_ships[ship_id] = RetreatState(method=RetreatMethod.EDGE)

        assert retreat_manager.is_retreating(mock_ship, ship_id_map) is True

    def test_is_retreating_false(self, retreat_manager, mock_ship, ship_id_map):
        """is_retreating returns False for non-retreating ship."""
        assert retreat_manager.is_retreating(mock_ship, ship_id_map) is False

    def test_is_retreating_unknown_ship(self, retreat_manager, mock_ship):
        """is_retreating returns False for unknown ship."""
        assert retreat_manager.is_retreating(mock_ship, {}) is False


# === Get Escape State Tests ===

class TestRetreatManagerGetRetreatState:
    """Tests for RetreatManager.get_retreat_state()."""

    def test_get_retreat_state_returns_state(self, retreat_manager, mock_ship, ship_id_map):
        """get_retreat_state returns the retreat state."""
        ship_id = ship_id_map[id(mock_ship)]
        expected_state = RetreatState(method=RetreatMethod.WARP, charge_ticks=100)
        retreat_manager.retreating_ships[ship_id] = expected_state

        result = retreat_manager.get_retreat_state(mock_ship, ship_id_map)

        assert result is expected_state

    def test_get_retreat_state_returns_none(self, retreat_manager, mock_ship, ship_id_map):
        """get_retreat_state returns None for non-retreating ship."""
        result = retreat_manager.get_retreat_state(mock_ship, ship_id_map)

        assert result is None


# === Reset Tests ===

class TestRetreatManagerReset:
    """Tests for RetreatManager.reset()."""

    def test_reset_clears_state(self, retreat_manager, mock_ship, ship_id_map):
        """reset clears all tracking state."""
        ship_id = ship_id_map[id(mock_ship)]
        retreat_manager.retreating_ships[ship_id] = RetreatState(method=RetreatMethod.EDGE)
        retreat_manager.escaped_ships.append(ship_id)

        retreat_manager.reset()

        assert retreat_manager.retreating_ships == {}
        assert retreat_manager.escaped_ships == []


# === Callback Tests ===

class TestRetreatManagerCallbacks:
    """Tests for callback management."""

    def test_set_on_ship_escaped(self, retreat_manager):
        """set_on_ship_escaped stores callback."""
        callback = Mock()
        retreat_manager.set_on_ship_escaped(callback)

        assert retreat_manager._on_ship_escaped is callback
