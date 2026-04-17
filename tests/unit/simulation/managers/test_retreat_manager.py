"""
Tests for RetreatManager (PROJ-29 SIM-03 Phase 2)

Tests the extracted RetreatManager class that handles:
- Retreat requests (edge and warp methods)
- Retreat state tracking and updates
- Ship escape detection
- Reinforcement handling

PROJ-270 Task 5.4: RetreatManager now consumes a `BoundaryRegion` via
`boundary=...`. The legacy `map_bounds=(min_x, min_y, max_x, max_y)`
tuple (corner-rooted, axis-aligned only) has been replaced with a
`BoundaryRegion` API. Fixtures use `RectBoundary(width=100000,
height=100000)` centered on origin — ship positions re-centered from
the old 0..100000 coordinate range to -50000..+50000.
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
from game.simulation.combat.boundary import (
    RectBoundary,
    UnboundedRegion,
    ExitPolicy,
)


# === Fixtures ===

@pytest.fixture
def mock_ship():
    """Create a mock Ship object (at origin — center of 100k x 100k rect)."""
    ship = Mock()
    ship.name = "Test Ship"
    ship.id = "mock-ship-uuid-001"
    ship.is_alive = True
    ship.x = 0
    ship.y = 0
    return ship


@pytest.fixture
def default_boundary():
    """Default `RectBoundary` for testing — 100k x 100k centered on origin."""
    return RectBoundary(
        width=100000.0,
        height=100000.0,
        exit_policy=ExitPolicy.RETREAT,
    )


@pytest.fixture
def retreat_manager(default_boundary):
    """Create a RetreatManager with the default rectangular boundary."""
    return RetreatManager(boundary=default_boundary)


@pytest.fixture
def ship_id_map(mock_ship):
    """Create a ship ID mapping."""
    return {mock_ship.id: "test-ship-id"}


# === Initialization Tests ===

class TestRetreatManagerInit:
    """Tests for RetreatManager initialization."""

    def test_init_with_boundary(self, default_boundary):
        """RetreatManager initializes with a BoundaryRegion."""
        manager = RetreatManager(boundary=default_boundary)
        assert manager.boundary is default_boundary

    def test_init_empty_state(self, retreat_manager):
        """RetreatManager starts with empty state."""
        assert retreat_manager.retreating_ships == {}
        assert retreat_manager.escaped_ships == []

    def test_init_no_escape_callback(self, retreat_manager):
        """RetreatManager starts with no escape callback."""
        assert retreat_manager._on_ship_escaped is None

    def test_init_accepts_unbounded_region(self):
        """`UnboundedRegion` is a valid boundary (edge-retreat disabled)."""
        manager = RetreatManager(boundary=UnboundedRegion())
        assert isinstance(manager.boundary, UnboundedRegion)


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
        ship_id = ship_id_map[mock_ship.id]
        retreat_manager.retreating_ships[ship_id] = RetreatState(
            method=RetreatMethod.EDGE, target=(-50000, 0)
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

        ship_id = ship_id_map[mock_ship.id]
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
        ship_id = ship_id_map[mock_ship.id]
        state = retreat_manager.retreating_ships[ship_id]
        assert state.method == RetreatMethod.WARP
        assert state.charge_ticks == 0
        assert state.required_ticks == 500

    def test_request_retreat_edge_calculates_nearest_edge(self, retreat_manager, ship_id_map):
        """request_retreat calculates target for nearest edge."""
        # Ship close to left edge (origin-centered 100k x 100k: half-extent
        # is 50000, so x=-49900 is 100 units from left edge).
        mock_ship = Mock()
        mock_ship.id = "left-ship-uuid"
        mock_ship.is_alive = True
        mock_ship.x = -49900
        mock_ship.y = 0
        ship_id_map[mock_ship.id] = "left-ship"

        retreat_manager.request_retreat(mock_ship, ship_id_map, method=RetreatMethod.EDGE)

        state = retreat_manager.retreating_ships["left-ship"]
        assert state.target == (-50000, 0)  # Should target left edge


# === Cancel Retreat Tests ===

class TestRetreatManagerCancelRetreat:
    """Tests for RetreatManager.cancel_retreat()."""

    def test_cancel_retreat_removes_state(self, retreat_manager, mock_ship, ship_id_map):
        """cancel_retreat removes retreat state."""
        ship_id = ship_id_map[mock_ship.id]
        retreat_manager.retreating_ships[ship_id] = RetreatState(
            method=RetreatMethod.EDGE, target=(-50000, 0)
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
        ship_id = ship_id_map[mock_ship.id]
        retreat_manager.retreating_ships[ship_id] = RetreatState(
            method=RetreatMethod.WARP, charge_ticks=0, required_ticks=500
        )

        def get_ship_by_id(sid):
            return mock_ship if sid == ship_id else None

        retreat_manager.update(get_ship_by_id)

        assert retreat_manager.retreating_ships[ship_id].charge_ticks == 1

    def test_update_warp_escape_when_charged(self, retreat_manager, mock_ship, ship_id_map):
        """update triggers escape when warp fully charged."""
        ship_id = ship_id_map[mock_ship.id]
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
        # Ship near left edge (x=-49900 → 100 units from -50000 edge,
        # within DEFAULT_MAP_EDGE_THRESHOLD).
        mock_ship = Mock()
        mock_ship.id = "edge-ship-uuid"
        mock_ship.is_alive = True
        mock_ship.x = -49900  # Within edge threshold
        mock_ship.y = 0
        ship_id = "edge-ship"
        ship_id_map[mock_ship.id] = ship_id

        retreat_manager.retreating_ships[ship_id] = RetreatState(
            method=RetreatMethod.EDGE, target=(-50000, 0)
        )

        def get_ship_by_id(sid):
            return mock_ship if sid == ship_id else None

        retreat_manager.update(get_ship_by_id)

        assert ship_id in retreat_manager.escaped_ships

    def test_update_removes_dead_ships_from_retreat(self, retreat_manager, mock_ship, ship_id_map):
        """update removes dead ships from retreat tracking."""
        ship_id = ship_id_map[mock_ship.id]
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
        ship_id = ship_id_map[mock_ship.id]
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
    """Tests for RetreatManager.find_nearest_edge().

    Fixtures use `RectBoundary(width=100000, height=100000)` centered on
    origin, so edges are at ±50000 in each axis.
    """

    def test_find_nearest_edge_left(self, retreat_manager):
        """find_nearest_edge finds left edge when closest."""
        mock_ship = Mock()
        mock_ship.x = -49900
        mock_ship.y = 0

        target = retreat_manager.find_nearest_edge(mock_ship)

        assert target == (-50000, 0)

    def test_find_nearest_edge_right(self, retreat_manager):
        """find_nearest_edge finds right edge when closest."""
        mock_ship = Mock()
        mock_ship.x = 49900
        mock_ship.y = 0

        target = retreat_manager.find_nearest_edge(mock_ship)

        assert target == (50000, 0)

    def test_find_nearest_edge_top(self, retreat_manager):
        """find_nearest_edge finds top edge when closest."""
        mock_ship = Mock()
        mock_ship.x = 0
        mock_ship.y = -49900

        target = retreat_manager.find_nearest_edge(mock_ship)

        assert target == (0, -50000)

    def test_find_nearest_edge_bottom(self, retreat_manager):
        """find_nearest_edge finds bottom edge when closest."""
        mock_ship = Mock()
        mock_ship.x = 0
        mock_ship.y = 49900

        target = retreat_manager.find_nearest_edge(mock_ship)

        assert target == (0, 50000)


# === At Map Edge Tests ===

class TestRetreatManagerAtMapEdge:
    """Tests for RetreatManager.at_map_edge().

    `RectBoundary` 100k x 100k origin-centered → edges at ±50000.
    DEFAULT_EDGE_THRESHOLD governs how close counts as "at edge".
    """

    def test_at_map_edge_left(self, retreat_manager):
        """at_map_edge detects left edge."""
        mock_ship = Mock()
        mock_ship.x = -49600  # 400 units from -50000 edge
        mock_ship.y = 0

        assert retreat_manager.at_map_edge(mock_ship) is True

    def test_at_map_edge_right(self, retreat_manager):
        """at_map_edge detects right edge."""
        mock_ship = Mock()
        mock_ship.x = 49600  # 400 units from 50000 edge
        mock_ship.y = 0

        assert retreat_manager.at_map_edge(mock_ship) is True

    def test_at_map_edge_center(self, retreat_manager):
        """at_map_edge returns False for center position."""
        mock_ship = Mock()
        mock_ship.x = 0
        mock_ship.y = 0

        assert retreat_manager.at_map_edge(mock_ship) is False

    def test_at_map_edge_custom_threshold(self, retreat_manager):
        """at_map_edge respects custom threshold."""
        mock_ship = Mock()
        mock_ship.x = -49200  # 800 units from -50000 edge
        mock_ship.y = 0

        assert retreat_manager.at_map_edge(mock_ship, threshold=500) is False
        assert retreat_manager.at_map_edge(mock_ship, threshold=1000) is True

    def test_at_map_edge_false_for_unbounded(self):
        """`UnboundedRegion` → at_map_edge always False (no edge)."""
        manager = RetreatManager(boundary=UnboundedRegion())
        mock_ship = Mock()
        mock_ship.x = 1e9
        mock_ship.y = 1e9
        assert manager.at_map_edge(mock_ship) is False


# === Is Retreating Tests ===

class TestRetreatManagerIsRetreating:
    """Tests for RetreatManager.is_retreating()."""

    def test_is_retreating_true(self, retreat_manager, mock_ship, ship_id_map):
        """is_retreating returns True for retreating ship."""
        ship_id = ship_id_map[mock_ship.id]
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
        ship_id = ship_id_map[mock_ship.id]
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
        ship_id = ship_id_map[mock_ship.id]
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


# === Unbounded-region behavior (PROJ-270 Task 5.4) ===

class TestRetreatManagerUnbounded:
    """Edge-retreat must gracefully refuse when the arena is unbounded."""

    def test_request_retreat_edge_rejected_for_unbounded(self):
        """EDGE retreat fails with a clear error when no edge exists."""
        manager = RetreatManager(boundary=UnboundedRegion())
        ship = Mock()
        ship.name = "Probe"
        ship.id = "probe-uuid"
        ship.is_alive = True
        ship.x = 0
        ship.y = 0
        ship_id_map = {ship.id: "probe"}

        success, error = manager.request_retreat(
            ship, ship_id_map, method=RetreatMethod.EDGE
        )

        assert success is False
        assert "unbounded" in error.lower() or "no edge" in error.lower(), (
            f"Expected mention of 'unbounded' or 'no edge', got: {error!r}"
        )

    def test_warp_retreat_still_works_in_unbounded(self):
        """WARP retreat is shape-independent and still functions."""
        manager = RetreatManager(boundary=UnboundedRegion())
        ship = Mock()
        ship.name = "Probe"
        ship.id = "probe-uuid"
        ship.is_alive = True
        ship_id_map = {ship.id: "probe"}

        success, error = manager.request_retreat(
            ship, ship_id_map, method=RetreatMethod.WARP
        )

        assert success is True
        assert error is None
