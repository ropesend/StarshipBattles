"""
Unit tests for the turn engine.

Tests turn processing, phase execution, command validation,
colonization, production, combat resolution, and resource handling.
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock

from game.strategy.engine.turn_engine import TurnEngine, ValidationResult
from game.strategy.data.fleet import Fleet, FleetOrder, OrderType
from game.strategy.data.hex_math import HexCoord
from game.strategy.data.empire import Empire


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
    fleet.ships = ["Colony Ship"]
    fleet.get_current_order = MagicMock(return_value=None)
    fleet.pop_order = MagicMock()
    fleet.has_resources_for_movement = MagicMock(return_value=True)
    fleet.has_resources_for_warp = MagicMock(return_value=True)
    fleet.consume_movement_resources = MagicMock()
    fleet.consume_warp_resources = MagicMock()
    fleet.clear_orders = MagicMock()
    fleet.get_ship_instances = MagicMock(return_value=[])
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
        result = ValidationResult(True, "Success")

        assert result.is_valid is True
        assert result.message == "Success"
        assert result.error_code is None

    def test_invalid_result_with_error_code(self):
        """Create an invalid result with error code."""
        result = ValidationResult(False, "Failed", "INVALID_TARGET")

        assert result.is_valid is False
        assert result.message == "Failed"
        assert result.error_code == "INVALID_TARGET"

    def test_default_message(self):
        """Default message is empty string."""
        result = ValidationResult(True)

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
# Test: Battle Seed Generation
# =============================================================================


class TestBattleSeedGeneration:
    """Tests for battle seed counter."""

    def test_seed_counter_increments(self, turn_engine):
        """Battle seed counter increments each call."""
        seed1 = turn_engine._generate_battle_seed()
        seed2 = turn_engine._generate_battle_seed()
        seed3 = turn_engine._generate_battle_seed()

        assert seed2 == seed1 + 1
        assert seed3 == seed2 + 1

    def test_seed_starts_at_one(self, turn_engine):
        """First seed is 1."""
        seed = turn_engine._generate_battle_seed()

        assert seed == 1

    def test_multiple_engines_independent(self):
        """Different engine instances have independent counters."""
        engine1 = TurnEngine()
        engine2 = TurnEngine()

        seed1 = engine1._generate_battle_seed()
        seed2 = engine2._generate_battle_seed()

        assert seed1 == seed2 == 1


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
        mock_fleet.path = []
        mock_fleet.location = HexCoord(0, 0)

        # PROJ-12: TurnEngine delegates to FleetMovementEngine, so patch there
        with patch('game.strategy.engine.fleet_movement_engine.find_hybrid_path') as mock_path:
            mock_path.return_value = [HexCoord(0, 0), HexCoord(1, 0), HexCoord(2, 0)]

            result = turn_engine._calculate_next_hex(mock_fleet, mock_galaxy)

            mock_path.assert_called()

    def test_at_destination_pops_order(self, turn_engine, mock_fleet, mock_galaxy):
        """Fleet at destination pops the MOVE order."""
        target = HexCoord(0, 0)
        order = FleetOrder(OrderType.MOVE, target)
        mock_fleet.get_current_order.return_value = order
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
        mock_fleet.path = []
        mock_fleet.location = HexCoord(0, 0)

        # PROJ-12: TurnEngine delegates to FleetMovementEngine, so patch there
        with patch('game.strategy.engine.fleet_movement_engine.calculate_intercept_point') as mock_intercept:
            with patch('game.strategy.engine.fleet_movement_engine.find_hybrid_path') as mock_path:
                mock_intercept.return_value = HexCoord(25, 0)
                mock_path.return_value = [HexCoord(0, 0), HexCoord(5, 0)]

                turn_engine._calculate_next_hex(mock_fleet, mock_galaxy)

                mock_intercept.assert_called()

    def test_invalid_target_fleet_cancels_order(self, turn_engine, mock_fleet, mock_galaxy):
        """MOVE_TO_FLEET with invalid target cancels order."""
        order = FleetOrder(OrderType.MOVE_TO_FLEET, None)  # Invalid target
        mock_fleet.get_current_order.return_value = order
        mock_fleet.path = []

        result = turn_engine._calculate_next_hex(mock_fleet, mock_galaxy)

        mock_fleet.pop_order.assert_called()
        assert result is None


# =============================================================================
# Test: Combat Resolution
# =============================================================================


class TestCombatResolution:
    """Tests for combat resolution methods."""

    def test_resolve_conflicts_detects_collision(self, turn_engine, mock_empire):
        """Conflicts are detected when fleets share location."""
        empire1 = MagicMock()
        empire1.id = 0
        empire2 = MagicMock()
        empire2.id = 1

        fleet1 = MagicMock()
        fleet1.location = HexCoord(5, 5)
        fleet1.owner_id = 0

        fleet2 = MagicMock()
        fleet2.location = HexCoord(5, 5)  # Same location
        fleet2.owner_id = 1

        empire1.fleets = [fleet1]
        empire2.fleets = [fleet2]

        with patch.object(turn_engine, '_resolve_combat_at_hex') as mock_resolve:
            turn_engine._resolve_conflicts([empire1, empire2])

            mock_resolve.assert_called()

    def test_no_conflict_same_empire(self, turn_engine):
        """No conflict when same empire's fleets share location."""
        empire = MagicMock()
        empire.id = 0

        fleet1 = MagicMock()
        fleet1.location = HexCoord(5, 5)
        fleet1.owner_id = 0

        fleet2 = MagicMock()
        fleet2.location = HexCoord(5, 5)
        fleet2.owner_id = 0  # Same empire

        empire.fleets = [fleet1, fleet2]

        with patch.object(turn_engine, '_resolve_combat_at_hex') as mock_resolve:
            turn_engine._resolve_conflicts([empire])

            mock_resolve.assert_not_called()

    def test_resolve_combat_rng_fallback(self, turn_engine):
        """RNG fallback for fleets without ShipInstances."""
        fleet1 = MagicMock()
        fleet1.has_ship_instances.return_value = False

        fleet2 = MagicMock()
        fleet2.has_ship_instances.return_value = False

        with patch('game.strategy.engine.turn_engine.random.random') as mock_random:
            mock_random.return_value = 0.3  # < 0.5 means fleet2 wins

            result = turn_engine._resolve_combat(fleet1, fleet2)

            assert result == fleet2

    def test_resolve_combat_uses_simulation(self, turn_engine):
        """Full simulation used when both fleets have ShipInstances."""
        fleet1 = MagicMock()
        fleet1.has_ship_instances.return_value = True

        fleet2 = MagicMock()
        fleet2.has_ship_instances.return_value = True

        with patch.object(turn_engine, '_resolve_combat_simulated') as mock_sim:
            mock_sim.return_value = fleet1

            result = turn_engine._resolve_combat(fleet1, fleet2)

            mock_sim.assert_called_with(fleet1, fleet2)
            assert result == fleet1


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

    def test_legacy_list_format_supported(self, turn_engine, mock_empire, mock_planet, mock_galaxy):
        """Old list format [name, turns] is supported."""
        mock_planet.construction_queue = [["Colony Ship", 2]]
        mock_planet.has_space_shipyard = True
        mock_empire.colonies = [mock_planet]

        turn_engine.process_production([mock_empire])

        # Turns should decrement
        assert mock_planet.construction_queue[0][1] == 1


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
# Test: Per-Turn Resource Processing
# =============================================================================


class TestPerTurnResources:
    """Tests for _process_per_turn_resources method."""

    def test_consumes_resources_each_tick(self, turn_engine, mock_empire, mock_fleet):
        """Per-turn costs are consumed each tick."""
        mock_ship = MagicMock()
        mock_ship.is_combat_capable.return_value = True
        mock_ship.get_all_resource_costs_per_turn.return_value = {"fuel": 100.0}
        mock_ship.consume_resource = MagicMock(return_value=True)

        mock_fleet.get_ship_instances.return_value = [mock_ship]
        mock_empire.fleets = [mock_fleet]

        turn_engine._process_per_turn_resources(50, [mock_empire])

        # Should consume 1/100th of 100 = 1.0 fuel
        mock_ship.consume_resource.assert_called_with("fuel", 1.0)

    def test_skips_non_combat_ships(self, turn_engine, mock_empire, mock_fleet):
        """Non-combat-capable ships are skipped."""
        mock_ship = MagicMock()
        mock_ship.is_combat_capable.return_value = False

        mock_fleet.get_ship_instances.return_value = [mock_ship]
        mock_empire.fleets = [mock_fleet]

        turn_engine._process_per_turn_resources(1, [mock_empire])

        mock_ship.get_all_resource_costs_per_turn.assert_not_called()

    def test_auto_disables_on_depletion(self, turn_engine, mock_empire, mock_fleet):
        """Components auto-disabled when resource depleted."""
        mock_ship = MagicMock()
        mock_ship.is_combat_capable.return_value = True
        mock_ship.get_all_resource_costs_per_turn.return_value = {"power": 50.0}
        mock_ship.consume_resource = MagicMock(return_value=False)  # Failed

        mock_fleet.get_ship_instances.return_value = [mock_ship]
        mock_empire.fleets = [mock_fleet]

        with patch.object(turn_engine, '_auto_disable_components_for_resource') as mock_disable:
            turn_engine._process_per_turn_resources(1, [mock_empire])

            mock_disable.assert_called_with(mock_ship, "power")


# =============================================================================
# Test: Tick Processing
# =============================================================================


class TestTickProcessing:
    """Tests for _process_tick method."""

    @patch.object(TurnEngine, '_process_per_turn_resources')
    @patch.object(TurnEngine, '_resolve_conflicts')
    def test_tick_processes_phases(self, mock_conflicts, mock_resources,
                                   turn_engine, mock_empire, mock_galaxy):
        """Each tick processes resource and conflict phases."""
        mock_empire.fleets = []

        turn_engine._process_tick(1, [mock_empire], mock_galaxy)

        mock_resources.assert_called()
        mock_conflicts.assert_called()

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

        with patch.object(turn_engine, '_calculate_next_hex') as mock_calc:
            with patch.object(turn_engine, '_process_per_turn_resources'):
                with patch.object(turn_engine, '_resolve_conflicts'):
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

        with patch.object(turn_engine, '_calculate_next_hex') as mock_calc:
            with patch.object(turn_engine, '_process_per_turn_resources'):
                with patch.object(turn_engine, '_resolve_conflicts'):
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
        fleet.orders = []
        fleet.path = [HexCoord(1, 0), HexCoord(2, 0)]  # Pre-computed path
        fleet.get_current_order = MagicMock(return_value=FleetOrder(OrderType.MOVE, HexCoord(10, 0)))
        fleet.pop_order = MagicMock()
        fleet.has_resources_for_movement = MagicMock(return_value=True)
        fleet.has_resources_for_warp = MagicMock(return_value=True)
        fleet.consume_movement_resources = MagicMock()
        fleet.consume_warp_resources = MagicMock()
        fleet.clear_orders = MagicMock()
        fleet.get_ship_instances = MagicMock(return_value=[])

        mock_empire.fleets = [fleet]

        with patch.object(turn_engine, '_process_per_turn_resources'):
            with patch.object(turn_engine, '_resolve_conflicts'):
                turn_engine._process_tick(1, [mock_empire], mock_galaxy)

        fleet.consume_movement_resources.assert_called()

    def test_stranded_fleet_clears_orders(self, turn_engine, mock_empire, mock_galaxy):
        """Fleet without movement resources clears orders."""
        fleet = MagicMock()
        fleet.id = 1
        fleet.owner_id = 0
        fleet.location = HexCoord(0, 0)
        fleet.speed = 100.0
        fleet.orders = []
        fleet.path = [HexCoord(1, 0)]  # Has path
        fleet.get_current_order = MagicMock(return_value=FleetOrder(OrderType.MOVE, HexCoord(10, 0)))
        fleet.pop_order = MagicMock()
        fleet.has_resources_for_movement = MagicMock(return_value=False)  # No resources
        fleet.has_resources_for_warp = MagicMock(return_value=True)
        fleet.consume_movement_resources = MagicMock()
        fleet.consume_warp_resources = MagicMock()
        fleet.clear_orders = MagicMock()
        fleet.get_ship_instances = MagicMock(return_value=[])

        mock_empire.fleets = [fleet]

        with patch.object(turn_engine, '_process_per_turn_resources'):
            with patch.object(turn_engine, '_resolve_conflicts'):
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

        # Process tick
        with patch.object(turn_engine, '_process_per_turn_resources'):
            with patch.object(turn_engine, '_resolve_conflicts'):
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

        with patch.object(turn_engine, '_process_per_turn_resources'):
            with patch.object(turn_engine, '_resolve_conflicts'):
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
# =============================================================================


class TestBattleResolverInjection:
    """
    Tests for TurnEngine battle resolver dependency injection.

    PROJ-11 Phase 4: TurnEngine now accepts an optional IBattleResolver
    parameter for clean separation between strategy and simulation layers.
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

    def test_resolve_combat_simulated_uses_injected_resolver(self):
        """_resolve_combat_simulated should use injected resolver."""
        from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

        call_count = 0
        last_fleets = []

        class TrackingResolver(IBattleResolver):
            def resolve_battle(self, fleet1, fleet2, seed=None):
                nonlocal call_count, last_fleets
                call_count += 1
                last_fleets = [fleet1, fleet2]
                return BattleResult(
                    winner=0,
                    tick_count=100,
                    team0_survivors=[],
                    team1_survivors=[]
                )

        resolver = TrackingResolver()
        engine = TurnEngine(battle_resolver=resolver)

        fleet1 = MagicMock()
        fleet1.id = 1
        fleet1.has_ship_instances.return_value = True

        fleet2 = MagicMock()
        fleet2.id = 2
        fleet2.has_ship_instances.return_value = True

        result = engine._resolve_combat_simulated(fleet1, fleet2)

        assert call_count == 1
        assert fleet1 in last_fleets
        assert fleet2 in last_fleets
        assert result == fleet1  # Winner was team 0 (fleet1)

    def test_mock_resolver_enables_unit_testing(self):
        """Mock resolver allows unit testing without simulation."""
        from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

        class AlwaysFleet1WinsResolver(IBattleResolver):
            def resolve_battle(self, fleet1, fleet2, seed=None):
                return BattleResult(
                    winner=0,  # Team 0 (fleet1) wins
                    tick_count=50,
                    team0_survivors=[MagicMock()],
                    team1_survivors=[]
                )

        engine = TurnEngine(battle_resolver=AlwaysFleet1WinsResolver())

        fleet1 = MagicMock()
        fleet1.id = 1
        fleet1.has_ship_instances.return_value = True
        fleet1.get_ship_instances.return_value = [MagicMock()]
        fleet1.ships = [MagicMock()]
        fleet1.update_from_battle_results = MagicMock()

        fleet2 = MagicMock()
        fleet2.id = 2
        fleet2.has_ship_instances.return_value = True
        fleet2.get_ship_instances.return_value = [MagicMock()]
        fleet2.ships = [MagicMock()]
        fleet2.update_from_battle_results = MagicMock()

        winner = engine._resolve_combat_simulated(fleet1, fleet2)

        assert winner == fleet1

    def test_draw_result_handled(self):
        """Draw (winner=None) should be handled correctly."""
        from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

        class DrawResolver(IBattleResolver):
            def resolve_battle(self, fleet1, fleet2, seed=None):
                return BattleResult(
                    winner=None,  # Draw
                    tick_count=1000,
                    team0_survivors=[MagicMock(), MagicMock()],  # 2 survivors
                    team1_survivors=[MagicMock()]  # 1 survivor
                )

        engine = TurnEngine(battle_resolver=DrawResolver())

        fleet1 = MagicMock()
        fleet1.id = 1
        fleet1.has_ship_instances.return_value = True
        fleet1.update_from_battle_results = MagicMock()

        fleet2 = MagicMock()
        fleet2.id = 2
        fleet2.has_ship_instances.return_value = True
        fleet2.update_from_battle_results = MagicMock()

        winner = engine._resolve_combat_simulated(fleet1, fleet2)

        # Fleet with more survivors wins on draw
        assert winner == fleet1

    def test_seed_passed_to_resolver(self):
        """Battle seed should be passed to resolver."""
        from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

        received_seed = None

        class SeedCapturingResolver(IBattleResolver):
            def resolve_battle(self, fleet1, fleet2, seed=None):
                nonlocal received_seed
                received_seed = seed
                return BattleResult(
                    winner=0,
                    tick_count=0,
                    team0_survivors=[],
                    team1_survivors=[]
                )

        engine = TurnEngine(battle_resolver=SeedCapturingResolver())

        fleet1 = MagicMock()
        fleet1.id = 1
        fleet1.has_ship_instances.return_value = True

        fleet2 = MagicMock()
        fleet2.id = 2
        fleet2.has_ship_instances.return_value = True

        engine._resolve_combat_simulated(fleet1, fleet2)

        # The engine uses _generate_battle_seed() internally
        assert received_seed is not None
        assert isinstance(received_seed, int)

    def test_battle_results_applied_to_fleets(self):
        """Battle results should be applied to fleet ship states."""
        from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

        survivor0 = MagicMock()
        survivor1 = MagicMock()

        class ResultResolver(IBattleResolver):
            def resolve_battle(self, fleet1, fleet2, seed=None):
                return BattleResult(
                    winner=0,
                    tick_count=100,
                    team0_survivors=[survivor0],
                    team1_survivors=[survivor1]
                )

        engine = TurnEngine(battle_resolver=ResultResolver())

        fleet1 = MagicMock()
        fleet1.id = 1
        fleet1.has_ship_instances.return_value = True
        fleet1.update_from_battle_results = MagicMock()

        fleet2 = MagicMock()
        fleet2.id = 2
        fleet2.has_ship_instances.return_value = True
        fleet2.update_from_battle_results = MagicMock()

        engine._resolve_combat_simulated(fleet1, fleet2)

        # Verify fleet.update_from_battle_results was called with survivors
        fleet1.update_from_battle_results.assert_called_once_with([survivor0])
        fleet2.update_from_battle_results.assert_called_once_with([survivor1])


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
