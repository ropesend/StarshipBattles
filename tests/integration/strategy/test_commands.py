"""
Integration tests for commands.

PROJ-55: Updated to include colony pod data in mock fleets for colonization tests.
"""
from enum import Enum
from unittest.mock import MagicMock
from game.strategy.engine.commands import IssueColonizeCommand, CommandType
from game.strategy.engine.turn_engine import TurnEngine
from game.core.validation import ValidationResult
from game.strategy.data.fleet import Fleet, FleetOrder, OrderType
from game.core.hex_math import HexCoord
from game.strategy.data.galaxy import Galaxy, StarSystem, Planet


# PROJ-55: Mock planet type enum for tests
class MockPlanetType(Enum):
    CONTINENTAL = "CONTINENTAL"


def create_mock_fleet_with_colony_pod(fleet_id, location, planet_type_str="CONTINENTAL"):
    """Create a mock fleet with a ship that has a colony pod.

    PROJ-55: Ships now need colony pods to colonize specific planet types.
    """
    # Create mock ship with design_data containing colony pod
    mock_ship = MagicMock()
    mock_ship.name = "Colony Ship"
    mock_ship.design_data = {
        'layers': {
            'HULL': [{'id': f'{planet_type_str.lower()}_colony_pod'}]
        }
    }

    fleet = MagicMock(spec=Fleet)
    fleet.id = fleet_id
    fleet.location = location
    fleet.ships = [mock_ship]
    fleet.orders = []
    return fleet


class TestCommands:
    def test_issue_colonize_command_validation_success(self):
        turn_engine = TurnEngine()
        galaxy = MagicMock(spec=Galaxy)

        # PROJ-55: Use fleet with colony pod matching planet type
        fleet = create_mock_fleet_with_colony_pod(101, HexCoord(10, 10), "CONTINENTAL")

        planet = MagicMock(spec=Planet)
        planet.name = "TestPlanet"
        planet.location = HexCoord(0, 0)
        planet.owner_id = None
        planet.planet_type = MockPlanetType.CONTINENTAL  # PROJ-55: Add planet type

        # Mock System
        system = MagicMock(spec=StarSystem)
        system.global_location = HexCoord(10, 10)
        system.planets = [planet]

        galaxy.systems = {HexCoord(10, 10): system}

        # Mock the new spatial index method
        def get_planets_at_global_hex(global_hex):
            result = []
            for sys in galaxy.systems.values():
                for p in sys.planets:
                    if (sys.global_location + p.location) == global_hex:
                        result.append(p)
            return result
        galaxy.get_planets_at_global_hex = get_planets_at_global_hex

        # Setup: Fleet at planet location (Global System 10,10 + Planet Local 0,0 = 10,10)
        # Fleet is there with colony pod.
        # Planet is unowned.

        res = turn_engine.validate_colonize_order(galaxy, fleet, planet)
        assert res.is_valid
        assert res.errors == []

    def test_issue_colonize_command_validation_fail_owned(self):
        turn_engine = TurnEngine()
        galaxy = MagicMock(spec=Galaxy)
        fleet = MagicMock(spec=Fleet)
        fleet.id = 101
        fleet.location = HexCoord(10, 10)

        planet = MagicMock(spec=Planet)
        planet.name = "TestPlanet"
        planet.location = HexCoord(0, 0)
        planet.owner_id = 99  # Already owned

        # Mock System
        system = MagicMock(spec=StarSystem)
        system.global_location = HexCoord(10, 10)
        system.planets = [planet]

        galaxy.systems = {HexCoord(10, 10): system}

        def get_planets_at_global_hex(global_hex):
            result = []
            for sys in galaxy.systems.values():
                for p in sys.planets:
                    if (sys.global_location + p.location) == global_hex:
                        result.append(p)
            return result
        galaxy.get_planets_at_global_hex = get_planets_at_global_hex

        res = turn_engine.validate_colonize_order(galaxy, fleet, planet)
        assert not res.is_valid
        assert res.error_code == "ALREADY_OWNED"

    def test_issue_colonize_command_validation_fail_location(self):
        turn_engine = TurnEngine()
        galaxy = MagicMock(spec=Galaxy)
        fleet = MagicMock(spec=Fleet)
        fleet.id = 101
        fleet.location = HexCoord(20, 20)  # Fleet away from planet

        planet = MagicMock(spec=Planet)
        planet.name = "TestPlanet"
        planet.location = HexCoord(0, 0)
        planet.owner_id = None

        # Mock System
        system = MagicMock(spec=StarSystem)
        system.global_location = HexCoord(10, 10)
        system.planets = [planet]

        galaxy.systems = {HexCoord(10, 10): system}

        def get_planets_at_global_hex(global_hex):
            result = []
            for sys in galaxy.systems.values():
                for p in sys.planets:
                    if (sys.global_location + p.location) == global_hex:
                        result.append(p)
            return result
        galaxy.get_planets_at_global_hex = get_planets_at_global_hex

        res = turn_engine.validate_colonize_order(galaxy, fleet, planet)
        assert not res.is_valid
        assert res.error_code == "WRONG_LOCATION"

    def test_issue_colonize_command_any_planet(self):
        turn_engine = TurnEngine()
        galaxy = MagicMock(spec=Galaxy)
        fleet = MagicMock(spec=Fleet)
        fleet.id = 101
        fleet.location = HexCoord(10, 10)

        planet = MagicMock(spec=Planet)
        planet.name = "TestPlanet"
        planet.location = HexCoord(0, 0)
        planet.owner_id = None

        # Mock System
        system = MagicMock(spec=StarSystem)
        system.global_location = HexCoord(10, 10)
        system.planets = [planet]

        galaxy.systems = {HexCoord(10, 10): system}

        def get_planets_at_global_hex(global_hex):
            result = []
            for sys in galaxy.systems.values():
                for p in sys.planets:
                    if (sys.global_location + p.location) == global_hex:
                        result.append(p)
            return result
        galaxy.get_planets_at_global_hex = get_planets_at_global_hex

        # Valid candidate exists
        res = turn_engine.validate_colonize_order(galaxy, fleet, None)
        assert res.is_valid

        # No candidate
        planet.owner_id = 99
        res = turn_engine.validate_colonize_order(galaxy, fleet, None)
        assert not res.is_valid
        assert res.error_code == "NO_CANDIDATES"


class TestGameSessionCommands:
    def test_handle_command(self):
        # Mock Session logic
        # Ideally we test GameSession class but it has complex init.
        # We can implement a partial mock or just test the dispatch logic if we extracted it.
        # Given we modified GameSession, let's try to mock it properly if possible or just rely on TurnEngine tests
        # since GameSession just delegates.
        # But we added `handle_command` in GameSession.
        pass


class TestIssueInterceptCommand:
    """Tests for IssueInterceptCommand class."""

    def test_create_intercept_command(self):
        """IssueInterceptCommand can be created with fleet and target IDs."""
        from game.strategy.engine.commands import IssueInterceptCommand, CommandType

        cmd = IssueInterceptCommand(fleet_id=1, target_fleet_id=2)

        assert cmd.fleet_id == 1
        assert cmd.target_fleet_id == 2
        assert cmd.type == CommandType.ISSUE_ORDER

    def test_intercept_command_has_name(self):
        """IssueInterceptCommand has correct name property."""
        from game.strategy.engine.commands import IssueInterceptCommand

        cmd = IssueInterceptCommand(fleet_id=1, target_fleet_id=2)

        assert cmd.name == "IssueInterceptCommand"


class TestIssueJoinFleetCommand:
    """Tests for IssueJoinFleetCommand class."""

    def test_create_join_fleet_command(self):
        """IssueJoinFleetCommand can be created with fleet and target IDs."""
        from game.strategy.engine.commands import IssueJoinFleetCommand, CommandType

        cmd = IssueJoinFleetCommand(fleet_id=1, target_fleet_id=2)

        assert cmd.fleet_id == 1
        assert cmd.target_fleet_id == 2
        assert cmd.type == CommandType.ISSUE_ORDER

    def test_join_fleet_command_has_name(self):
        """IssueJoinFleetCommand has correct name property."""
        from game.strategy.engine.commands import IssueJoinFleetCommand

        cmd = IssueJoinFleetCommand(fleet_id=1, target_fleet_id=2)

        assert cmd.name == "IssueJoinFleetCommand"


class TestQueueColonizeMissionCommand:
    """Tests for QueueColonizeMissionCommand class."""

    def test_create_colonize_mission_command(self):
        """QueueColonizeMissionCommand can be created with all required fields."""
        from game.strategy.engine.commands import QueueColonizeMissionCommand, CommandType

        target = HexCoord(10, 20)
        cmd = QueueColonizeMissionCommand(fleet_id=1, target_hex=target, planet_id=42)

        assert cmd.fleet_id == 1
        assert cmd.target_hex == target
        assert cmd.planet_id == 42
        assert cmd.type == CommandType.ISSUE_ORDER

    def test_colonize_mission_command_has_name(self):
        """QueueColonizeMissionCommand has correct name property."""
        from game.strategy.engine.commands import QueueColonizeMissionCommand

        cmd = QueueColonizeMissionCommand(fleet_id=1, target_hex=HexCoord(0, 0), planet_id=1)

        assert cmd.name == "QueueColonizeMissionCommand"


class TestClearFleetOrdersCommand:
    """Tests for ClearFleetOrdersCommand class."""

    def test_create_clear_orders_command(self):
        """ClearFleetOrdersCommand can be created with fleet ID."""
        from game.strategy.engine.commands import ClearFleetOrdersCommand, CommandType

        cmd = ClearFleetOrdersCommand(fleet_id=5)

        assert cmd.fleet_id == 5
        assert cmd.type == CommandType.ISSUE_ORDER

    def test_clear_orders_command_has_name(self):
        """ClearFleetOrdersCommand has correct name property."""
        from game.strategy.engine.commands import ClearFleetOrdersCommand

        cmd = ClearFleetOrdersCommand(fleet_id=5)

        assert cmd.name == "ClearFleetOrdersCommand"
