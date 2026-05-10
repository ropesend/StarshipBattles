"""
Unit tests for OrderProcessor.

PROJ-12 Phase 3: TDD tests written before implementation.
Tests order lifecycle management - advance, complete, cancel operations.
"""

import pytest
from unittest.mock import MagicMock, patch

from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.core.hex_math import HexCoord


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_fleet():
    """Create a mock fleet with standard order attributes."""
    fleet = MagicMock(spec=Fleet)
    fleet.id = 1
    fleet.owner_id = 0
    fleet.location = HexCoord(0, 0)
    fleet.orders = []
    fleet.path = []
    fleet.get_current_order = MagicMock(return_value=None)
    fleet.pop_order = MagicMock()
    fleet.clear_orders = MagicMock()
    fleet.merge_with = MagicMock()
    return fleet


@pytest.fixture
def mock_empire():
    """Create a mock empire."""
    empire = MagicMock()
    empire.id = 0
    empire.name = "Test Empire"
    empire.fleets = []
    empire.remove_fleet = MagicMock()
    empire.add_colony = MagicMock()
    return empire


@pytest.fixture
def mock_galaxy():
    """Create a mock galaxy."""
    galaxy = MagicMock()
    galaxy.get_planets_at_global_hex = MagicMock(return_value=[])
    return galaxy


# =============================================================================
# Test: OrderProcessor Creation
# =============================================================================

# =============================================================================
# Test: JOIN_FLEET Processing
# =============================================================================

class TestJoinFleetProcessing:
    """Tests for JOIN_FLEET order processing."""

    def test_process_join_fleet_merges_at_same_location(self, mock_fleet, mock_empire, mock_galaxy):
        """JOIN_FLEET merges fleets when at same location."""
        from game.strategy.engine.order_processor import OrderProcessor

        processor = OrderProcessor()

        target_fleet = MagicMock()
        target_fleet.id = 2
        target_fleet.location = HexCoord(5, 5)

        mock_fleet.location = HexCoord(5, 5)  # Same location
        order = Order(OrderType.JOIN_FLEET, target_fleet)
        mock_fleet.get_current_order.return_value = order

        result = processor.process_join_fleet(mock_fleet, mock_empire, mock_galaxy)

        assert result.merged is True
        mock_fleet.merge_with.assert_called_with(target_fleet, event_bus=None)
        mock_empire.remove_fleet.assert_called_with(mock_fleet, event_bus=None)

    def test_process_join_fleet_fails_at_different_location(self, mock_fleet, mock_empire, mock_galaxy):
        """JOIN_FLEET fails when not at same location."""
        from game.strategy.engine.order_processor import OrderProcessor

        processor = OrderProcessor()

        target_fleet = MagicMock()
        target_fleet.id = 2
        target_fleet.location = HexCoord(100, 100)  # Different

        mock_fleet.location = HexCoord(0, 0)
        order = Order(OrderType.JOIN_FLEET, target_fleet)
        mock_fleet.get_current_order.return_value = order

        result = processor.process_join_fleet(mock_fleet, mock_empire, mock_galaxy)

        assert result.merged is False
        mock_fleet.merge_with.assert_not_called()

    def test_process_join_fleet_cancels_with_invalid_target(self, mock_fleet, mock_empire, mock_galaxy):
        """JOIN_FLEET is cancelled when target is invalid."""
        from game.strategy.engine.order_processor import OrderProcessor

        processor = OrderProcessor()

        order = Order(OrderType.JOIN_FLEET, None)  # Invalid target
        mock_fleet.get_current_order.return_value = order

        result = processor.process_join_fleet(mock_fleet, mock_empire, mock_galaxy)

        assert result.merged is False
        assert result.cancelled is True
        mock_fleet.pop_order.assert_called()

    def test_process_join_fleet_no_order(self, mock_fleet, mock_empire, mock_galaxy):
        """process_join_fleet returns empty result when no order."""
        from game.strategy.engine.order_processor import OrderProcessor

        processor = OrderProcessor()
        mock_fleet.get_current_order.return_value = None

        result = processor.process_join_fleet(mock_fleet, mock_empire, mock_galaxy)

        assert result.merged is False


# =============================================================================
# Test: COLONIZE Processing
# =============================================================================

class TestColonizeProcessing:
    """Tests for COLONIZE order processing."""

    @pytest.fixture
    def component_registry(self):
        """Component registry with colony pod definitions."""
        return {
            'colony_pod': {
                'id': 'colony_pod',
                'abilities': {'ColonizePlanet': True}
            },
        }

    @pytest.fixture
    def mock_planet_continental(self):
        """Create a mock CONTINENTAL planet."""
        from enum import Enum
        from game.strategy.data.planet import Planet

        class MockPlanetType(Enum):
            CONTINENTAL = "CONTINENTAL"

        planet = MagicMock(spec=Planet)
        planet.name = "Target Planet"
        planet.owner_id = None
        planet.planet_type = MockPlanetType.CONTINENTAL
        return planet

    @pytest.fixture
    def mock_ship_with_continental_pod(self):
        """Create a mock ship with a drop pod in carried_items."""
        ship = MagicMock()
        ship.name = "Colony Ship"
        ship.carried_items = [{"vehicle_type": "drop_pod", "design_id": "test_pod", "name": "Test Pod", "design_data": {"layers": {"CORE": []}}, "mass": 500}]
        return ship

    def test_process_colonize_success(
        self, mock_fleet, mock_empire, mock_galaxy,
        mock_planet_continental, mock_ship_with_continental_pod, component_registry
    ):
        """COLONIZE succeeds when valid planet at location."""
        from game.strategy.engine.order_processor import OrderProcessor

        processor = OrderProcessor()

        # Setup fleet with colony ship carrying drop pod
        mock_fleet.ships = [mock_ship_with_continental_pod]

        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet_continental]

        order = Order(OrderType.COLONIZE, mock_planet_continental)
        mock_fleet.get_current_order.return_value = order
        mock_fleet.location = HexCoord(5, 5)

        with patch.object(processor, '_deploy_drop_pod'):
            result = processor.process_colonize(
                mock_fleet, mock_empire, mock_galaxy,
                component_registry=component_registry
            )

        assert result.colonized is True
        mock_empire.add_colony.assert_called_with(mock_planet_continental)
        mock_empire.remove_fleet.assert_not_called()

    def test_process_colonize_any_planet(
        self, mock_fleet, mock_empire, mock_galaxy,
        mock_planet_continental, mock_ship_with_continental_pod, component_registry
    ):
        """COLONIZE with None target picks matching planet."""
        from game.strategy.engine.order_processor import OrderProcessor

        processor = OrderProcessor()

        # Setup fleet with colony ship carrying drop pod
        mock_fleet.ships = [mock_ship_with_continental_pod]

        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet_continental]

        order = Order(OrderType.COLONIZE, None)  # Any planet
        mock_fleet.get_current_order.return_value = order
        mock_fleet.location = HexCoord(5, 5)

        with patch.object(processor, '_deploy_drop_pod'):
            result = processor.process_colonize(
                mock_fleet, mock_empire, mock_galaxy,
                component_registry=component_registry
            )

        assert result.colonized is True
        mock_empire.add_colony.assert_called_with(mock_planet_continental)

    def test_process_colonize_fails_no_planet(
        self, mock_fleet, mock_empire, mock_galaxy, component_registry
    ):
        """COLONIZE fails when no valid planet at location."""
        from game.strategy.engine.order_processor import OrderProcessor

        processor = OrderProcessor()

        mock_galaxy.get_planets_at_global_hex.return_value = []  # No planets

        order = Order(OrderType.COLONIZE, None)
        mock_fleet.get_current_order.return_value = order

        result = processor.process_colonize(
            mock_fleet, mock_empire, mock_galaxy,
            component_registry=component_registry
        )

        assert result.colonized is False
        mock_fleet.pop_order.assert_called()

    def test_process_colonize_fails_owned_planet(
        self, mock_fleet, mock_empire, mock_galaxy,
        mock_planet_continental, component_registry
    ):
        """COLONIZE fails when planet is already owned."""
        from game.strategy.engine.order_processor import OrderProcessor

        processor = OrderProcessor()

        mock_planet_continental.owner_id = 1  # Already owned

        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet_continental]

        order = Order(OrderType.COLONIZE, mock_planet_continental)
        mock_fleet.get_current_order.return_value = order

        result = processor.process_colonize(
            mock_fleet, mock_empire, mock_galaxy,
            component_registry=component_registry
        )

        assert result.colonized is False


# =============================================================================
# Test: End-Turn Order Processing
# =============================================================================

class TestEndTurnOrderProcessing:
    """Tests for execute_action_order method."""

    def test_execute_action_order_colonize(self, mock_fleet, mock_empire, mock_galaxy):
        """Action order processing handles COLONIZE orders."""
        from game.strategy.engine.order_processor import OrderProcessor
        from game.strategy.data.planet import Planet
        from enum import Enum

        class MockPlanetType(Enum):
            CONTINENTAL = "CONTINENTAL"

        processor = OrderProcessor()

        mock_planet = MagicMock(spec=Planet)
        mock_planet.owner_id = None
        mock_planet.name = "Test Planet"
        mock_planet.planet_type = MockPlanetType.CONTINENTAL

        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet]

        # Setup fleet with colony ship carrying drop pod
        mock_ship = MagicMock()
        mock_ship.name = "Colony Ship"
        mock_ship.carried_items = [{"vehicle_type": "drop_pod", "design_id": "test_pod", "name": "Test Pod", "design_data": {"layers": {"CORE": []}}, "mass": 500}]
        mock_fleet.ships = [mock_ship]

        component_registry = {}

        order = Order(OrderType.COLONIZE, mock_planet)
        mock_fleet.get_current_order.return_value = order
        mock_fleet.location = HexCoord(5, 5)

        with patch.object(processor, '_deploy_drop_pod'):
            result = processor.execute_action_order(
                mock_fleet, mock_empire, mock_galaxy,
                component_registry=component_registry
            )

        # Phase 2: colonized=True but fleet NOT consumed (ship stays)
        assert result is True
        mock_empire.add_colony.assert_called()

    # PROJ-207 EP-001: Removed test_process_end_turn_orders_join_fleet
    # JOIN_FLEET is now handled ONLY by process_instant_orders(), not by
    # process_end_turn_orders(). See TestInstantOrderProcessing tests instead.

    def test_process_end_turn_orders_no_order(self, mock_fleet, mock_empire, mock_galaxy):
        """End-turn processing with no order returns False."""
        from game.strategy.engine.order_processor import OrderProcessor

        processor = OrderProcessor()
        mock_fleet.get_current_order.return_value = None

        result = processor.execute_action_order(mock_fleet, mock_empire, mock_galaxy)

        assert result is False


# =============================================================================
# Test: Instant Order Processing (During Tick)
# =============================================================================

class TestInstantOrderProcessing:
    """Tests for process_instant_orders during ticks."""

    def test_process_instant_join_fleet_at_location(self, mock_empire, mock_galaxy):
        """Instant JOIN_FLEET processing merges co-located fleets."""
        from game.strategy.engine.order_processor import OrderProcessor

        processor = OrderProcessor()

        target_fleet = MagicMock()
        target_fleet.id = 2
        target_fleet.location = HexCoord(5, 5)
        target_fleet.get_current_order = MagicMock(return_value=None)

        joining_fleet = MagicMock()
        joining_fleet.id = 1
        joining_fleet.location = HexCoord(5, 5)  # Same location
        joining_fleet.merge_with = MagicMock()

        order = Order(OrderType.JOIN_FLEET, target_fleet)
        joining_fleet.get_current_order = MagicMock(return_value=order)

        mock_empire.fleets = [joining_fleet, target_fleet]
        mock_empire.remove_fleet = MagicMock()

        removed = processor.process_instant_orders([mock_empire])

        assert len(removed) > 0
        joining_fleet.merge_with.assert_called_with(target_fleet, event_bus=None)

    def test_process_instant_join_fleet_not_at_location(self, mock_empire, mock_galaxy):
        """Instant JOIN_FLEET doesn't merge when not co-located."""
        from game.strategy.engine.order_processor import OrderProcessor

        processor = OrderProcessor()

        target_fleet = MagicMock()
        target_fleet.id = 2
        target_fleet.location = HexCoord(100, 100)  # Different location
        target_fleet.get_current_order = MagicMock(return_value=None)

        joining_fleet = MagicMock()
        joining_fleet.id = 1
        joining_fleet.location = HexCoord(0, 0)
        joining_fleet.merge_with = MagicMock()

        order = Order(OrderType.JOIN_FLEET, target_fleet)
        joining_fleet.get_current_order = MagicMock(return_value=order)

        mock_empire.fleets = [joining_fleet, target_fleet]

        removed = processor.process_instant_orders([mock_empire])

        assert len(removed) == 0
        joining_fleet.merge_with.assert_not_called()

    def test_process_instant_join_fleet_preserves_order_when_not_colocated(self, mock_empire, mock_galaxy):
        """PROJ-207 EP-001: JOIN_FLEET order stays queued when fleets not co-located.

        When a fleet has a JOIN_FLEET order but isn't at the target's location yet,
        the order should remain in the queue (not be popped or cleared).
        The preceding MOVE_TO_FLEET will bring the fleet to the target.
        """
        from game.strategy.engine.order_processor import OrderProcessor

        processor = OrderProcessor()

        target_fleet = MagicMock()
        target_fleet.id = 2
        target_fleet.location = HexCoord(100, 100)  # Target is far away
        target_fleet.get_current_order = MagicMock(return_value=None)

        joining_fleet = MagicMock()
        joining_fleet.id = 1
        joining_fleet.location = HexCoord(0, 0)  # Fleet hasn't arrived yet
        joining_fleet.merge_with = MagicMock()
        joining_fleet.pop_order = MagicMock()
        joining_fleet.clear_orders = MagicMock()

        order = Order(OrderType.JOIN_FLEET, target_fleet)
        joining_fleet.get_current_order = MagicMock(return_value=order)

        mock_empire.fleets = [joining_fleet, target_fleet]

        processor.process_instant_orders([mock_empire])

        # Order should NOT be popped or cleared - it waits for arrival
        joining_fleet.pop_order.assert_not_called()
        joining_fleet.clear_orders.assert_not_called()

    def test_join_fleet_not_in_action_order_types(self):
        """PROJ-207 EP-001: JOIN_FLEET is NOT in ACTION_ORDER_TYPES.

        JOIN_FLEET should only be processed by the instant path, not by
        tick-based action processing via ActionExecutionEngine.
        """
        from game.strategy.data.order_types import ACTION_ORDER_TYPES, OrderType

        # JOIN_FLEET should NOT be in ACTION_ORDER_TYPES
        assert OrderType.JOIN_FLEET not in ACTION_ORDER_TYPES


# =============================================================================
# Test: Order Result Dataclass
# =============================================================================

# =============================================================================
# Test: PROJ-55 Colony Ship Removal
# =============================================================================

class TestColonizeDropPodDeployment:
    """Tests for Phase 3: Drop pod deployed from carried_items, ship stays."""

    @pytest.fixture
    def mock_ship_with_pod(self):
        """Create a mock ship with drop pod in carried_items."""
        ship = MagicMock()
        ship.name = "Colony Ship"
        ship.carried_items = [{"vehicle_type": "drop_pod", "design_id": "test_pod", "name": "Test Pod", "design_data": {"layers": {"CORE": []}}, "mass": 500}]
        return ship

    @pytest.fixture
    def mock_ship_combat(self):
        """Create a mock combat ship without drop pod."""
        ship = MagicMock()
        ship.name = "Combat Ship"
        ship.carried_items = []
        return ship

    @pytest.fixture
    def mock_component_registry(self):
        """Component registry (kept for API compatibility)."""
        return {}

    @pytest.fixture
    def mock_planet_ice_dwarf(self):
        """Create a mock ICE_DWARF planet."""
        from enum import Enum

        class MockPlanetType(Enum):
            ICE_DWARF = "ICE_DWARF"

        planet = MagicMock()
        planet.name = "Frostworld"
        planet.owner_id = None
        planet.planet_type = MockPlanetType.ICE_DWARF
        return planet

    def test_process_colonize_deploys_drop_pod(
        self, mock_fleet, mock_empire, mock_galaxy,
        mock_ship_with_pod, mock_ship_combat,
        mock_planet_ice_dwarf, mock_component_registry
    ):
        """Colonize deploys drop pod, ship stays in fleet."""
        from game.strategy.engine.order_processor import OrderProcessor

        processor = OrderProcessor()

        mock_fleet.ships = [mock_ship_with_pod, mock_ship_combat]

        order = Order(OrderType.COLONIZE, mock_planet_ice_dwarf)
        mock_fleet.get_current_order.return_value = order
        mock_fleet.location = HexCoord(5, 5)

        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet_ice_dwarf]

        with patch.object(processor, '_deploy_drop_pod') as mock_deploy:
            result = processor.process_colonize(
                mock_fleet, mock_empire, mock_galaxy,
                component_registry=mock_component_registry
            )

        assert result.colonized is True
        # Drop pod deployed
        mock_deploy.assert_called_once()
        # Ship NOT removed
        mock_empire.remove_fleet.assert_not_called()

    def test_process_colonize_single_ship_fleet_stays(
        self, mock_fleet, mock_empire, mock_galaxy,
        mock_ship_with_pod, mock_planet_ice_dwarf, mock_component_registry
    ):
        """Single-ship fleet stays after colonization (ship is reusable)."""
        from game.strategy.engine.order_processor import OrderProcessor

        processor = OrderProcessor()

        mock_fleet.ships = [mock_ship_with_pod]

        order = Order(OrderType.COLONIZE, mock_planet_ice_dwarf)
        mock_fleet.get_current_order.return_value = order
        mock_fleet.location = HexCoord(5, 5)

        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet_ice_dwarf]

        with patch.object(processor, '_deploy_drop_pod'):
            result = processor.process_colonize(
                mock_fleet, mock_empire, mock_galaxy,
                component_registry=mock_component_registry
            )

        assert result.colonized is True
        # Fleet NOT removed - ship is reusable
        mock_empire.remove_fleet.assert_not_called()

    def test_process_colonize_multi_ship_fleet_all_stay(
        self, mock_fleet, mock_empire, mock_galaxy,
        mock_ship_with_pod, mock_ship_combat,
        mock_planet_ice_dwarf, mock_component_registry
    ):
        """Multi-ship fleet: all ships stay after colonization."""
        from game.strategy.engine.order_processor import OrderProcessor

        processor = OrderProcessor()

        mock_fleet.ships = [mock_ship_with_pod, mock_ship_combat]

        order = Order(OrderType.COLONIZE, mock_planet_ice_dwarf)
        mock_fleet.get_current_order.return_value = order
        mock_fleet.location = HexCoord(5, 5)

        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet_ice_dwarf]

        with patch.object(processor, '_deploy_drop_pod'):
            result = processor.process_colonize(
                mock_fleet, mock_empire, mock_galaxy,
                component_registry=mock_component_registry
            )

        assert result.colonized is True
        # No ships removed, fleet stays
        mock_empire.remove_fleet.assert_not_called()
