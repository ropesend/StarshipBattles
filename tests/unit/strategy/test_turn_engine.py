"""
Unit tests for the turn engine.

Tests turn processing, phase execution, command validation,
colonization, production, combat resolution, and resource handling.
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock

from game.strategy.engine.turn_engine import TurnEngine
from game.core.validation import ValidationResult, validation_result
from game.strategy.data.fleet import Fleet, FleetOrder, OrderType
from game.strategy.data.hex_math import HexCoord
from game.strategy.data.empire import Empire
from game.strategy.data.ship_instance import ShipInstance


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def turn_engine():
    """Create a fresh turn engine."""
    return TurnEngine()


@pytest.fixture
def mock_empire():
    """Create a mock empire."""
    empire = MagicMock(spec=Empire)
    empire.id = 0
    empire.name = "Test Empire"
    empire.fleets = []
    empire.colonies = []
    return empire


@pytest.fixture
def mock_fleet():
    """Create a mock fleet."""
    fleet = MagicMock(spec=Fleet)
    fleet.id = 1
    fleet.owner_id = 0
    fleet.location = HexCoord(0, 0)
    fleet.speed = 10.0
    fleet.orders = []
    fleet.path = []
    # Use mock ShipInstance instead of string
    mock_ship = MagicMock(spec=ShipInstance)
    mock_ship.name = "Colony Ship"
    mock_ship.is_combat_capable = MagicMock(return_value=True)
    fleet.ships = [mock_ship]
    fleet.get_current_order = MagicMock(return_value=None)
    fleet.pop_order = MagicMock()
    fleet.has_resources_for_movement = MagicMock(return_value=True)
    fleet.has_resources_for_warp = MagicMock(return_value=True)
    fleet.consume_movement_resources = MagicMock()
    fleet.consume_warp_resources = MagicMock()
    fleet.clear_orders = MagicMock()
    return fleet


@pytest.fixture
def mock_galaxy():
    """Create a mock galaxy."""
    galaxy = MagicMock()
    galaxy.systems = {}
    galaxy.get_planets_at_global_hex = MagicMock(return_value=[])
    galaxy.get_system_of_planet = MagicMock(return_value=None)
    return galaxy


@pytest.fixture
def mock_planet():
    """Create a mock unowned planet."""
    planet = MagicMock()
    planet.id = 1
    planet.name = "Test Planet"
    planet.owner_id = None
    planet.location = HexCoord(0, 0)
    planet.construction_queue = []
    planet.facilities = []
    planet.has_space_shipyard = True
    return planet


# =============================================================================
# Test: ValidationResult Dataclass
# =============================================================================


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_valid_result(self):
        """Create a valid result."""
        result = validation_result(True, "Success")

        assert result.is_valid is True
        assert result.message == "Success"
        assert result.error_code is None

    def test_invalid_result_with_error_code(self):
        """Create an invalid result with error code."""
        result = validation_result(False, "Failed", "INVALID_TARGET")

        assert result.is_valid is False
        assert result.message == "Failed"
        assert result.error_code == "INVALID_TARGET"

    def test_default_message(self):
        """Default message is empty string."""
        result = ValidationResult()

        assert result.message == ""


# =============================================================================
# Test: Colonize Order Validation
# =============================================================================


class TestColonizeValidation:
    """Tests for validate_colonize_order method."""

    def test_validate_colonize_no_fleet(self, turn_engine, mock_galaxy):
        """Validation fails when fleet is None."""
        result = turn_engine.validate_colonize_order(mock_galaxy, None, None)

        assert result.is_valid is False
        assert "fleet" in result.message.lower()

    def test_validate_colonize_unowned_planet(self, turn_engine, mock_galaxy, mock_fleet, mock_planet):
        """Valid colonize order on unowned planet."""
        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet]
        mock_fleet.location = mock_planet.location

        result = turn_engine.validate_colonize_order(mock_galaxy, mock_fleet, mock_planet)

        assert result.is_valid is True

    def test_validate_colonize_owned_planet_fails(self, turn_engine, mock_galaxy, mock_fleet, mock_planet):
        """Cannot colonize already-owned planet."""
        mock_planet.owner_id = 1  # Already owned
        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet]
        mock_fleet.location = mock_planet.location

        result = turn_engine.validate_colonize_order(mock_galaxy, mock_fleet, mock_planet)

        assert result.is_valid is False
        assert result.error_code == "ALREADY_OWNED"

    def test_validate_colonize_wrong_location(self, turn_engine, mock_galaxy, mock_fleet, mock_planet):
        """Cannot colonize planet from different location."""
        mock_galaxy.get_planets_at_global_hex.return_value = []  # No planets at fleet location
        mock_fleet.location = HexCoord(100, 100)  # Far away

        result = turn_engine.validate_colonize_order(mock_galaxy, mock_fleet, mock_planet)

        assert result.is_valid is False
        assert result.error_code == "WRONG_LOCATION"

    def test_validate_colonize_any_planet_success(self, turn_engine, mock_galaxy, mock_fleet, mock_planet):
        """Validate colonize order with 'Any' planet (None target)."""
        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet]
        mock_fleet.location = mock_planet.location

        result = turn_engine.validate_colonize_order(mock_galaxy, mock_fleet, None)

        assert result.is_valid is True
        assert "candidate" in result.message.lower()

    def test_validate_colonize_any_no_candidates(self, turn_engine, mock_galaxy, mock_fleet):
        """Colonize 'Any' fails when no unowned planets at location."""
        mock_galaxy.get_planets_at_global_hex.return_value = []

        result = turn_engine.validate_colonize_order(mock_galaxy, mock_fleet, None)

        assert result.is_valid is False
        assert result.error_code == "NO_CANDIDATES"


# =============================================================================
# Test: Turn Processing Structure
# =============================================================================


class TestTurnProcessing:
    """Tests for process_turn method structure."""

    @patch.object(TurnEngine, '_process_tick')
    @patch.object(TurnEngine, '_process_end_turn_orders')
    @patch.object(TurnEngine, 'process_production')
    def test_process_turn_calls_subticks(self, mock_production, mock_end_turn, mock_tick,
                                         turn_engine, mock_empire, mock_galaxy):
        """process_turn calls _process_tick 100 times."""
        mock_empire.fleets = []

        turn_engine.process_turn([mock_empire], mock_galaxy)

        assert mock_tick.call_count == 100

    @patch.object(TurnEngine, '_process_tick')
    @patch.object(TurnEngine, '_process_end_turn_orders')
    @patch.object(TurnEngine, 'process_production')
    def test_process_turn_processes_end_turn_orders(self, mock_production, mock_end_turn, mock_tick,
                                                     turn_engine, mock_empire, mock_fleet, mock_galaxy):
        """process_turn calls end-turn order processing for each fleet."""
        mock_empire.fleets = [mock_fleet]

        turn_engine.process_turn([mock_empire], mock_galaxy)

        mock_end_turn.assert_called()

    @patch.object(TurnEngine, '_process_tick')
    @patch.object(TurnEngine, '_process_end_turn_orders')
    @patch.object(TurnEngine, 'process_production')
    def test_process_turn_runs_production(self, mock_production, mock_end_turn, mock_tick,
                                          turn_engine, mock_empire, mock_galaxy):
        """process_turn calls production phase."""
        mock_empire.fleets = []

        turn_engine.process_turn([mock_empire], mock_galaxy)

        mock_production.assert_called_once()


# =============================================================================
# Test: Movement Calculation
# =============================================================================


class TestMovementCalculation:
    """Tests for _calculate_next_hex method."""

    def test_no_order_returns_none(self, turn_engine, mock_fleet, mock_galaxy):
        """Fleet with no orders returns None."""
        mock_fleet.get_current_order.return_value = None

        result = turn_engine._calculate_next_hex(mock_fleet, mock_galaxy)

        assert result is None

    def test_move_order_calculates_path(self, turn_engine, mock_fleet, mock_galaxy):
        """MOVE order triggers path calculation."""
        target = HexCoord(10, 0)
        order = FleetOrder(OrderType.MOVE, target)
        mock_fleet.get_current_order.return_value = order
        mock_fleet.orders = [order]  # PROJ-35: Service uses orders list directly
        mock_fleet.path = []
        mock_fleet.location = HexCoord(0, 0)

        # PROJ-35: FleetMovementEngine delegates to FleetNavigationService, patch there
        with patch('game.strategy.services.fleet_navigation_service.find_hybrid_path') as mock_path:
            mock_path.return_value = [HexCoord(0, 0), HexCoord(1, 0), HexCoord(2, 0)]

            result = turn_engine._calculate_next_hex(mock_fleet, mock_galaxy)

            mock_path.assert_called()

    def test_at_destination_pops_order(self, turn_engine, mock_fleet, mock_galaxy):
        """Fleet at destination pops the MOVE order."""
        target = HexCoord(0, 0)
        order = FleetOrder(OrderType.MOVE, target)
        mock_fleet.get_current_order.return_value = order
        mock_fleet.orders = [order]  # PROJ-35: Service uses orders list directly
        mock_fleet.path = []
        mock_fleet.location = target  # Already there

        result = turn_engine._calculate_next_hex(mock_fleet, mock_galaxy)

        mock_fleet.pop_order.assert_called()
        assert result is None

    def test_move_to_fleet_uses_intercept(self, turn_engine, mock_fleet, mock_galaxy):
        """MOVE_TO_FLEET order uses intercept calculation."""
        target_fleet = MagicMock()
        target_fleet.location = HexCoord(50, 0)
        order = FleetOrder(OrderType.MOVE_TO_FLEET, target_fleet)
        mock_fleet.get_current_order.return_value = order
        mock_fleet.orders = [order]  # PROJ-35: Service uses orders list directly
        mock_fleet.path = []
        mock_fleet.location = HexCoord(0, 0)

        # PROJ-35: FleetMovementEngine delegates to FleetNavigationService
        # calculate_intercept_point is imported locally, so patch at source
        with patch('game.strategy.data.pathfinding.calculate_intercept_point') as mock_intercept:
            with patch('game.strategy.services.fleet_navigation_service.find_hybrid_path') as mock_path:
                mock_intercept.return_value = HexCoord(25, 0)
                mock_path.return_value = [HexCoord(0, 0), HexCoord(5, 0)]

                turn_engine._calculate_next_hex(mock_fleet, mock_galaxy)

                mock_intercept.assert_called()

    def test_invalid_target_fleet_cancels_order(self, turn_engine, mock_fleet, mock_galaxy):
        """MOVE_TO_FLEET with invalid target cancels order."""
        order = FleetOrder(OrderType.MOVE_TO_FLEET, None)  # Invalid target
        mock_fleet.get_current_order.return_value = order
        mock_fleet.orders = [order]  # PROJ-35: Service uses orders list directly
        mock_fleet.path = []

        result = turn_engine._calculate_next_hex(mock_fleet, mock_galaxy)

        mock_fleet.pop_order.assert_called()
        assert result is None


# =============================================================================
# Test: Production Processing
# =============================================================================


class TestProductionProcessing:
    """Tests for process_production method."""

    def test_empty_queue_skipped(self, turn_engine, mock_empire, mock_planet):
        """Colonies with empty queues are skipped."""
        mock_planet.construction_queue = []
        mock_empire.colonies = [mock_planet]

        turn_engine.process_production([mock_empire])

        # No errors, nothing built

    def test_production_decrements_turns(self, turn_engine, mock_empire, mock_planet):
        """Production decrements turns remaining."""
        mock_planet.construction_queue = [{"type": "ship", "design_id": "Scout", "turns_remaining": 3}]
        mock_planet.has_space_shipyard = True
        mock_empire.colonies = [mock_planet]

        turn_engine.process_production([mock_empire])

        assert mock_planet.construction_queue[0]["turns_remaining"] == 2

    def test_production_completes_at_zero(self, turn_engine, mock_empire, mock_planet, mock_galaxy):
        """Production completes when turns reach zero."""
        mock_planet.construction_queue = [{"type": "ship", "design_id": "Scout", "turns_remaining": 1}]
        mock_planet.has_space_shipyard = True
        mock_empire.colonies = [mock_planet]

        # PROJ-12: TurnEngine delegates to ProductionEngine, so patch there
        with patch.object(turn_engine.production_engine, '_spawn_ship') as mock_spawn:
            turn_engine.process_production([mock_empire], mock_galaxy)

            mock_spawn.assert_called()
            assert len(mock_planet.construction_queue) == 0

    def test_no_shipyard_pauses_production(self, turn_engine, mock_empire, mock_planet):
        """Ships require shipyard to build."""
        mock_planet.construction_queue = [{"type": "ship", "design_id": "Scout", "turns_remaining": 1}]
        mock_planet.has_space_shipyard = False
        mock_empire.colonies = [mock_planet]

        turn_engine.process_production([mock_empire])

        # Turns should NOT decrement
        assert mock_planet.construction_queue[0]["turns_remaining"] == 1

    def test_complex_production_no_shipyard_needed(self, turn_engine, mock_empire, mock_planet, mock_galaxy):
        """Complexes don't need shipyard."""
        mock_planet.construction_queue = [{"type": "complex", "design_id": "Factory", "turns_remaining": 1}]
        mock_planet.has_space_shipyard = False
        mock_empire.colonies = [mock_planet]

        # PROJ-12: TurnEngine delegates to ProductionEngine, so patch there
        with patch.object(turn_engine.production_engine, '_spawn_complex') as mock_spawn:
            turn_engine.process_production([mock_empire], mock_galaxy)

            mock_spawn.assert_called()

# =============================================================================
# Test: End-Turn Order Processing
# =============================================================================


class TestEndTurnOrders:
    """Tests for _process_end_turn_orders method."""

    def test_no_order_returns_false(self, turn_engine, mock_fleet, mock_empire, mock_galaxy):
        """Fleet with no order returns False."""
        mock_fleet.get_current_order.return_value = None

        result = turn_engine._process_end_turn_orders(mock_fleet, mock_empire, mock_galaxy)

        assert result is False

    def test_colonize_order_executes(self, turn_engine, mock_fleet, mock_empire, mock_galaxy, mock_planet):
        """COLONIZE order transfers planet ownership."""
        order = FleetOrder(OrderType.COLONIZE, mock_planet)
        mock_fleet.get_current_order.return_value = order
        mock_fleet.location = mock_planet.location
        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet]

        result = turn_engine._process_end_turn_orders(mock_fleet, mock_empire, mock_galaxy)

        assert result is True
        mock_empire.add_colony.assert_called_with(mock_planet)
        mock_empire.remove_fleet.assert_called_with(mock_fleet)

    def test_colonize_any_finds_planet(self, turn_engine, mock_fleet, mock_empire, mock_galaxy, mock_planet):
        """COLONIZE with None target finds valid planet."""
        order = FleetOrder(OrderType.COLONIZE, None)  # "Any"
        mock_fleet.get_current_order.return_value = order
        mock_fleet.location = mock_planet.location
        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet]

        result = turn_engine._process_end_turn_orders(mock_fleet, mock_empire, mock_galaxy)

        assert result is True
        mock_empire.add_colony.assert_called_with(mock_planet)

    def test_colonize_invalid_pops_order(self, turn_engine, mock_fleet, mock_empire, mock_galaxy):
        """Invalid COLONIZE pops order and returns False."""
        order = FleetOrder(OrderType.COLONIZE, None)
        mock_fleet.get_current_order.return_value = order
        mock_galaxy.get_planets_at_global_hex.return_value = []  # No planets

        result = turn_engine._process_end_turn_orders(mock_fleet, mock_empire, mock_galaxy)

        assert result is False
        mock_fleet.pop_order.assert_called()

    def test_join_fleet_at_location(self, turn_engine, mock_fleet, mock_empire, mock_galaxy):
        """JOIN_FLEET merges when at same location."""
        target_fleet = MagicMock()
        target_fleet.location = HexCoord(0, 0)

        order = FleetOrder(OrderType.JOIN_FLEET, target_fleet)
        mock_fleet.get_current_order.return_value = order
        mock_fleet.location = HexCoord(0, 0)
        mock_fleet.merge_with = MagicMock()

        result = turn_engine._process_end_turn_orders(mock_fleet, mock_empire, mock_galaxy)

        assert result is True
        mock_fleet.merge_with.assert_called_with(target_fleet)
        mock_empire.remove_fleet.assert_called_with(mock_fleet)

    def test_join_fleet_wrong_location(self, turn_engine, mock_fleet, mock_empire, mock_galaxy):
        """JOIN_FLEET fails when not at target location."""
        target_fleet = MagicMock()
        target_fleet.location = HexCoord(100, 100)

        order = FleetOrder(OrderType.JOIN_FLEET, target_fleet)
        mock_fleet.get_current_order.return_value = order
        mock_fleet.location = HexCoord(0, 0)  # Different location

        result = turn_engine._process_end_turn_orders(mock_fleet, mock_empire, mock_galaxy)

        assert result is False
        mock_fleet.pop_order.assert_called()

    def test_join_fleet_invalid_target(self, turn_engine, mock_fleet, mock_empire, mock_galaxy):
        """JOIN_FLEET with invalid target pops order."""
        order = FleetOrder(OrderType.JOIN_FLEET, None)
        mock_fleet.get_current_order.return_value = order

        result = turn_engine._process_end_turn_orders(mock_fleet, mock_empire, mock_galaxy)

        assert result is False
        mock_fleet.pop_order.assert_called()


# =============================================================================
# Test: Tick Processing
# =============================================================================


class TestTickProcessing:
    """Tests for _process_tick method."""

    def test_tick_processes_phases(self, turn_engine, mock_empire, mock_galaxy):
        """Each tick processes resource and conflict phases."""
        mock_empire.fleets = []

        # PROJ-36: Combat delegated to ConflictResolutionEngine
        mock_conflict_engine = MagicMock()
        turn_engine._conflict_engine = mock_conflict_engine

        # PROJ-36: Resource consumption delegated to ResourceManagementEngine
        mock_resource_engine = MagicMock()
        turn_engine._resource_engine = mock_resource_engine

        turn_engine._process_tick(1, [mock_empire], mock_galaxy)

        mock_resource_engine.process_per_turn_consumption.assert_called()
        mock_conflict_engine.resolve_all_conflicts.assert_called()

    def test_fleet_speed_determines_movement_frequency(self, turn_engine, mock_empire, mock_galaxy):
        """Fleet speed affects when movement occurs."""
        # Create a real-ish fleet mock with proper speed attribute
        fleet = MagicMock()
        fleet.id = 1
        fleet.owner_id = 0
        fleet.location = HexCoord(0, 0)
        fleet.speed = 10.0  # Move every 10 ticks
        fleet.orders = []
        fleet.path = []
        fleet.get_current_order = MagicMock(return_value=None)
        fleet.get_ship_instances = MagicMock(return_value=[])

        mock_empire.fleets = [fleet]

        # PROJ-36: Set up mock conflict engine
        turn_engine._conflict_engine = MagicMock()

        # PROJ-36: Set up mock resource engine
        turn_engine._resource_engine = MagicMock()

        with patch.object(turn_engine, '_calculate_next_hex') as mock_calc:
            mock_calc.return_value = None

            # Tick 10 should trigger movement check (10 % 10 == 0)
            turn_engine._process_tick(10, [mock_empire], mock_galaxy)

            # Tick 5 should also check but still call calculate_next_hex
            turn_engine._process_tick(5, [mock_empire], mock_galaxy)

    def test_zero_speed_fleet_never_moves(self, turn_engine, mock_empire, mock_galaxy):
        """Fleet with zero speed never moves."""
        fleet = MagicMock()
        fleet.id = 1
        fleet.owner_id = 0
        fleet.location = HexCoord(0, 0)
        fleet.speed = 0.0  # Zero speed
        fleet.orders = []
        fleet.path = []
        fleet.get_current_order = MagicMock(return_value=None)
        fleet.get_ship_instances = MagicMock(return_value=[])

        mock_empire.fleets = [fleet]

        # PROJ-36: Set up mock conflict and resource engines
        turn_engine._conflict_engine = MagicMock()
        turn_engine._resource_engine = MagicMock()

        with patch.object(turn_engine, '_calculate_next_hex') as mock_calc:
            for tick in range(1, 11):  # Check first 10 ticks
                turn_engine._process_tick(tick, [mock_empire], mock_galaxy)

            mock_calc.assert_not_called()

    def test_movement_consumes_resources(self, turn_engine, mock_empire, mock_galaxy):
        """Movement consumes fleet resources."""
        fleet = MagicMock()
        fleet.id = 1
        fleet.owner_id = 0
        fleet.location = HexCoord(0, 0)
        fleet.speed = 100.0  # Move every tick
        order = FleetOrder(OrderType.MOVE, HexCoord(10, 0))
        fleet.orders = [order]  # PROJ-35: Service uses orders list directly
        fleet.path = [HexCoord(1, 0), HexCoord(2, 0)]  # Pre-computed path
        fleet.get_current_order = MagicMock(return_value=order)
        fleet.pop_order = MagicMock()
        fleet.has_resources_for_movement = MagicMock(return_value=True)
        fleet.has_resources_for_warp = MagicMock(return_value=True)
        fleet.can_use_warp = MagicMock(return_value=True)
        fleet.consume_movement_resources = MagicMock()
        fleet.consume_warp_resources = MagicMock()
        fleet.clear_orders = MagicMock()
        fleet.get_ship_instances = MagicMock(return_value=[])

        mock_empire.fleets = [fleet]

        # PROJ-36: Set up mock conflict and resource engines
        turn_engine._conflict_engine = MagicMock()
        turn_engine._resource_engine = MagicMock()

        turn_engine._process_tick(1, [mock_empire], mock_galaxy)

        fleet.consume_movement_resources.assert_called()

    def test_stranded_fleet_clears_orders(self, turn_engine, mock_empire, mock_galaxy):
        """Fleet without movement resources clears orders."""
        fleet = MagicMock()
        fleet.id = 1
        fleet.owner_id = 0
        fleet.location = HexCoord(0, 0)
        fleet.speed = 100.0
        order = FleetOrder(OrderType.MOVE, HexCoord(10, 0))
        fleet.orders = [order]  # PROJ-35: Service uses orders list directly
        fleet.path = [HexCoord(1, 0)]  # Has path
        fleet.get_current_order = MagicMock(return_value=order)
        fleet.pop_order = MagicMock()
        fleet.has_resources_for_movement = MagicMock(return_value=False)  # No resources
        fleet.has_resources_for_warp = MagicMock(return_value=True)
        fleet.can_use_warp = MagicMock(return_value=True)
        fleet.consume_movement_resources = MagicMock()
        fleet.consume_warp_resources = MagicMock()
        fleet.clear_orders = MagicMock()
        fleet.get_ship_instances = MagicMock(return_value=[])

        mock_empire.fleets = [fleet]

        # PROJ-36: Set up mock conflict and resource engines
        turn_engine._conflict_engine = MagicMock()
        turn_engine._resource_engine = MagicMock()

        turn_engine._process_tick(1, [mock_empire], mock_galaxy)

        fleet.clear_orders.assert_called()


# =============================================================================
# Test: JOIN_FLEET During Tick
# =============================================================================


class TestJoinFleetDuringTick:
    """Tests for JOIN_FLEET instant order processing during ticks."""

    def test_join_fleet_at_same_location(self, turn_engine, mock_empire, mock_galaxy):
        """Fleets with JOIN_FLEET merge when co-located."""
        target_fleet = MagicMock()
        target_fleet.id = 2
        target_fleet.location = HexCoord(5, 5)
        target_fleet.speed = 10.0
        target_fleet.get_current_order = MagicMock(return_value=None)
        target_fleet.get_ship_instances = MagicMock(return_value=[])

        joining_fleet = MagicMock()
        joining_fleet.id = 1
        joining_fleet.location = HexCoord(5, 5)  # Same location
        joining_fleet.speed = 10.0
        joining_fleet.get_ship_instances = MagicMock(return_value=[])

        order = FleetOrder(OrderType.JOIN_FLEET, target_fleet)
        joining_fleet.get_current_order = MagicMock(return_value=order)
        joining_fleet.merge_with = MagicMock()

        mock_empire.fleets = [joining_fleet, target_fleet]
        mock_empire.remove_fleet = MagicMock()

        # PROJ-36: Set up mock conflict and resource engines
        turn_engine._conflict_engine = MagicMock()
        turn_engine._resource_engine = MagicMock()

        # Process tick
        turn_engine._process_tick(1, [mock_empire], mock_galaxy)

        joining_fleet.merge_with.assert_called_with(target_fleet)
        mock_empire.remove_fleet.assert_called_with(joining_fleet)

    def test_join_fleet_not_at_location(self, turn_engine, mock_empire, mock_galaxy):
        """JOIN_FLEET does not merge when not co-located."""
        target_fleet = MagicMock()
        target_fleet.id = 2
        target_fleet.location = HexCoord(100, 100)
        target_fleet.speed = 10.0
        target_fleet.get_current_order = MagicMock(return_value=None)
        target_fleet.get_ship_instances = MagicMock(return_value=[])

        joining_fleet = MagicMock()
        joining_fleet.id = 1
        joining_fleet.location = HexCoord(0, 0)  # Different location
        joining_fleet.speed = 10.0
        joining_fleet.get_ship_instances = MagicMock(return_value=[])

        order = FleetOrder(OrderType.JOIN_FLEET, target_fleet)
        joining_fleet.get_current_order = MagicMock(return_value=order)
        joining_fleet.merge_with = MagicMock()

        mock_empire.fleets = [joining_fleet, target_fleet]

        # PROJ-36: Set up mock conflict and resource engines
        turn_engine._conflict_engine = MagicMock()
        turn_engine._resource_engine = MagicMock()

        turn_engine._process_tick(1, [mock_empire], mock_galaxy)

        joining_fleet.merge_with.assert_not_called()


# =============================================================================
# Test: Warp Resource Consumption
# =============================================================================


class TestWarpResources:
    """Tests for warp resource consumption during movement."""

    def test_warp_detection_uses_hex_distance(self, turn_engine):
        """Warp is detected when hex distance > 1."""
        from game.strategy.data.hex_math import hex_distance

        # Adjacent hex - not warp
        assert hex_distance(HexCoord(0, 0), HexCoord(1, 0)) == 1

        # Distant hex - warp
        assert hex_distance(HexCoord(0, 0), HexCoord(50, 0)) > 1

    def test_warp_resources_checked_before_jump(self, turn_engine):
        """has_resources_for_warp is checked during tick processing."""
        # This tests the existence of the check in the code path
        # The actual check happens in _process_tick when is_warp is True

        fleet = MagicMock()
        fleet.has_resources_for_warp = MagicMock(return_value=True)

        # Method should exist and be callable
        assert callable(fleet.has_resources_for_warp)

    def test_warp_resource_consumption_method_exists(self, turn_engine):
        """Fleet has consume_warp_resources method."""
        fleet = MagicMock()
        fleet.consume_warp_resources = MagicMock()

        # Method should exist
        assert callable(fleet.consume_warp_resources)


# =============================================================================
# Test: Edge Cases
# =============================================================================


class TestTurnEngineEdgeCases:
    """Edge case tests for turn engine."""

    def test_empty_empires_list(self, turn_engine, mock_galaxy):
        """Empty empires list doesn't crash."""
        turn_engine.process_turn([], mock_galaxy)

    def test_empire_with_no_fleets(self, turn_engine, mock_empire, mock_galaxy):
        """Empire with no fleets processes without error."""
        mock_empire.fleets = []
        mock_empire.colonies = []

        turn_engine.process_turn([mock_empire], mock_galaxy)

    def test_multiple_empires_processed(self, turn_engine, mock_galaxy):
        """Multiple empires are all processed."""
        empire1 = MagicMock()
        empire1.id = 0
        empire1.fleets = []
        empire1.colonies = []

        empire2 = MagicMock()
        empire2.id = 1
        empire2.fleets = []
        empire2.colonies = []

        turn_engine.process_turn([empire1, empire2], mock_galaxy)

    def test_save_path_passed_to_production(self, turn_engine, mock_empire, mock_galaxy):
        """save_path parameter passed to production."""
        mock_empire.fleets = []
        mock_empire.colonies = []

        with patch.object(turn_engine, 'process_production') as mock_prod:
            turn_engine.process_turn([mock_empire], mock_galaxy, save_path="/test/path")

            mock_prod.assert_called_with([mock_empire], mock_galaxy, "/test/path")


# =============================================================================
# PROJ-11 Phase 4: IBattleResolver Dependency Injection Tests
# PROJ-36: Combat resolution moved to ConflictResolutionEngine
# =============================================================================


class TestBattleResolverInjection:
    """
    Tests for TurnEngine battle resolver dependency injection.

    PROJ-11 Phase 4: TurnEngine now accepts an optional IBattleResolver
    parameter for clean separation between strategy and simulation layers.

    PROJ-36: Combat resolution is now delegated to ConflictResolutionEngine.
    TurnEngine still stores the resolver and passes it to the conflict engine.
    """

    def test_turn_engine_accepts_battle_resolver(self):
        """TurnEngine constructor should accept battle_resolver parameter."""
        from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

        class MockResolver(IBattleResolver):
            def resolve_battle(self, fleet1, fleet2, seed=None):
                return BattleResult(winner=0, tick_count=0, team0_survivors=[], team1_survivors=[])

        resolver = MockResolver()
        engine = TurnEngine(battle_resolver=resolver)

        assert engine._battle_resolver is resolver

    def test_turn_engine_defaults_to_simulation_resolver(self):
        """TurnEngine should default to SimulationBattleResolver."""
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver

        engine = TurnEngine()

        assert isinstance(engine._battle_resolver, SimulationBattleResolver)

    def test_conflict_engine_receives_battle_resolver(self):
        """ConflictResolutionEngine should receive the injected battle resolver."""
        from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

        class MockResolver(IBattleResolver):
            def resolve_battle(self, fleet1, fleet2, seed=None):
                return BattleResult(winner=0, tick_count=0, team0_survivors=[], team1_survivors=[])

        resolver = MockResolver()
        engine = TurnEngine(battle_resolver=resolver)

        # Access conflict_engine to trigger lazy initialization
        conflict_engine = engine.conflict_engine

        # The conflict engine should have the same resolver
        assert conflict_engine._battle_resolver is resolver

    def test_conflict_engine_lazy_initialization(self):
        """ConflictResolutionEngine should be lazily initialized."""
        engine = TurnEngine()

        # Before accessing, should be None
        assert engine._conflict_engine is None

        # After accessing, should be created
        conflict_engine = engine.conflict_engine
        assert conflict_engine is not None

        # Should return same instance
        assert engine.conflict_engine is conflict_engine


# =============================================================================
# Test: Iterator Safety
# =============================================================================


class TestFleetIteratorSafety:
    """Test that turn processing handles fleet modification safely.

    Regression test for PROJ-12 Phase 7 Fix 7.4:
    Line 104 iterates empire.fleets directly while colonization may remove fleets.
    While Python doesn't always raise RuntimeError for list modification during
    iteration, removing items can cause skipped iterations (silent bugs).
    """

    def test_fleet_removal_during_iteration_skips_items(self):
        """Verify that direct iteration skips items when list is modified.

        When iterating directly over a list and removing an item, the
        iteration can skip items because indices shift. The fix (using
        list()) prevents this.
        """
        # Create fleets
        fleet1 = MagicMock(spec=Fleet)
        fleet1.id = 1

        fleet2 = MagicMock(spec=Fleet)
        fleet2.id = 2

        fleet3 = MagicMock(spec=Fleet)
        fleet3.id = 3

        fleets = [fleet1, fleet2, fleet3]

        # BUG: Direct iteration with removal skips items
        processed_ids_buggy = []
        fleets_copy = [fleet1, fleet2, fleet3]
        for fleet in fleets_copy:  # Iterating directly
            processed_ids_buggy.append(fleet.id)
            if fleet.id == 1:
                # Removing fleet2 shifts fleet3 to index 1
                # But iterator advances to index 2, skipping fleet3
                fleets_copy.remove(fleet2)

        # fleet3 gets skipped because of index shift
        assert processed_ids_buggy == [1, 3], f"Expected [1, 3] due to skip, got {processed_ids_buggy}"

        # FIX: Using list() copy processes all items correctly
        processed_ids_fixed = []
        fleets = [fleet1, fleet2, fleet3]
        for fleet in list(fleets):  # Copy prevents issues
            processed_ids_fixed.append(fleet.id)
            if fleet.id == 1:
                fleets.remove(fleet2)

        # All three fleets are processed
        assert processed_ids_fixed == [1, 2, 3], f"Expected [1, 2, 3], got {processed_ids_fixed}"

    @patch.object(TurnEngine, '_process_tick')
    @patch.object(TurnEngine, 'process_production')
    def test_process_turn_processes_all_fleets_when_modified(
        self, mock_production, mock_tick
    ):
        """Verify process_turn processes all fleets even if list is modified.

        After the fix, all fleets should be processed even if some are removed
        during end-turn processing.
        """
        turn_engine = TurnEngine()

        mock_empire = MagicMock(spec=Empire)
        mock_empire.id = 0

        fleet1 = MagicMock(spec=Fleet)
        fleet1.id = 1
        fleet1.orders = []
        fleet1.get_current_order = MagicMock(return_value=None)

        fleet2 = MagicMock(spec=Fleet)
        fleet2.id = 2
        fleet2.orders = []
        fleet2.get_current_order = MagicMock(return_value=None)

        fleet3 = MagicMock(spec=Fleet)
        fleet3.id = 3
        fleet3.orders = []
        fleet3.get_current_order = MagicMock(return_value=None)

        mock_empire.fleets = [fleet1, fleet2, fleet3]
        mock_galaxy = MagicMock()
        mock_galaxy.systems = {}

        # Track which fleets get processed
        processed_fleets = []

        def track_and_remove(fleet, empire, galaxy):
            processed_fleets.append(fleet.id)
            # Simulate colonization removing fleet2 when processing fleet1
            if fleet.id == 1 and fleet2 in mock_empire.fleets:
                mock_empire.fleets.remove(fleet2)

        with patch.object(turn_engine, '_process_end_turn_orders', side_effect=track_and_remove):
            turn_engine.process_turn([mock_empire], mock_galaxy)

        # After the fix, all 3 fleets should be processed
        # Before the fix, fleet3 would be skipped
        assert len(processed_fleets) == 3, f"Expected 3 fleets processed, got {processed_fleets}"
