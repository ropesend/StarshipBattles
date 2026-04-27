"""
Edge case tests for superweapon command handlers and order processors.

PROJ-143 Phase 2, Task 2.4: Tests for edge cases not covered by existing test files.
Focuses on:
- Error paths in command handlers
- Error paths in order processors
- add_move_order_if_needed helper function behavior (via mission handlers)
- Missing target validation
- Invalid state handling
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from game.core.hex_math import HexCoord
from game.core.validation import ValidationResult
from game.strategy.data.order_types import Order, OrderType


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_fleet():
    """Create a mock fleet with basic attributes."""
    fleet = Mock()
    fleet.id = 1
    fleet.location = HexCoord(5, 5)
    fleet.orders = []
    fleet.path = []
    fleet.ships = []
    fleet.add_order = Mock(side_effect=lambda o: fleet.orders.append(o))
    return fleet


@pytest.fixture
def mock_planet():
    """Create a mock planet."""
    planet = Mock()
    planet.id = 100
    planet.name = "Test Planet"
    planet.location = HexCoord(2, 0)
    planet.owner_id = None
    return planet


@pytest.fixture
def mock_galaxy():
    """Create a mock galaxy with a star system."""
    galaxy = Mock()
    system = Mock()
    system.stars = [Mock(location=HexCoord(0, 0))]
    system.planets = []
    system.warp_points = []
    system.name = "Alpha"
    system.global_location = HexCoord(5, 5)
    galaxy.systems = {HexCoord(5, 5): system}
    galaxy.name_map = {"Alpha": system, "Target System": Mock(name="Target System", global_location=HexCoord(20, 20), warp_points=[])}
    galaxy.get_planet_by_id = Mock(return_value=None)
    galaxy.get_system_at_location = Mock(return_value=system)
    return galaxy


@pytest.fixture
def mock_session(mock_fleet, mock_galaxy, mock_planet):
    """Create a mock game session."""
    session = Mock()
    session._get_fleet_by_id = Mock(return_value=mock_fleet)
    session._get_planet_by_id = Mock(return_value=mock_planet)
    session.galaxy = mock_galaxy
    session.empires = []
    # Use public registries API
    registries = Mock()
    registries.components = {}
    session.registries = registries
    return session


# =============================================================================
# Mission Move Helper Tests (add_move_order_if_needed via mission handlers)
# =============================================================================

class TestSetupMissionMove:
    """Tests for the add_move_order_if_needed helper used by mission handlers."""

    def test_uses_last_move_order_target_as_start_hex(self, mock_session, mock_fleet, mock_planet):
        """Start hex is determined from last MOVE order's target if orders exist."""
        from game.strategy.engine.superweapon_command_handlers import ImplodePlanetMissionCommandHandler
        from game.strategy.engine.commands import QueueImplodePlanetMissionCommand

        # Fleet has existing MOVE order to (8, 8)
        existing_move = Order(OrderType.MOVE, target=HexCoord(8, 8))
        mock_fleet.orders = [existing_move]

        target_hex = HexCoord(12, 12)
        cmd = QueueImplodePlanetMissionCommand(fleet_id=1, target_hex=target_hex, planet_id=100)
        handler = ImplodePlanetMissionCommandHandler()

        with patch('game.strategy.engine.superweapon_command_handlers.SuperweaponValidator') as mock_validator, \
             patch('game.strategy.engine.command_handlers.find_hybrid_path') as mock_path:
            mock_validator.validate_implode_planet.return_value = ValidationResult()
            # Path should be calculated from (8,8) not (5,5)
            mock_path.return_value = [HexCoord(8, 8), HexCoord(10, 10), HexCoord(12, 12)]
            handler.execute(mock_session, cmd)

            # find_hybrid_path called with start=(8,8)
            mock_path.assert_called_once()
            call_args = mock_path.call_args[0]
            assert call_args[1] == HexCoord(8, 8)  # start hex
            assert call_args[2] == HexCoord(12, 12)  # target hex

    def test_uses_fleet_location_when_no_orders(self, mock_session, mock_fleet, mock_planet):
        """Start hex is fleet.location when no orders exist."""
        from game.strategy.engine.superweapon_command_handlers import ImplodePlanetMissionCommandHandler
        from game.strategy.engine.commands import QueueImplodePlanetMissionCommand

        mock_fleet.orders = []  # No existing orders
        target_hex = HexCoord(10, 10)
        cmd = QueueImplodePlanetMissionCommand(fleet_id=1, target_hex=target_hex, planet_id=100)
        handler = ImplodePlanetMissionCommandHandler()

        with patch('game.strategy.engine.superweapon_command_handlers.SuperweaponValidator') as mock_validator, \
             patch('game.strategy.engine.command_handlers.find_hybrid_path') as mock_path:
            mock_validator.validate_implode_planet.return_value = ValidationResult()
            mock_path.return_value = [HexCoord(5, 5), HexCoord(10, 10)]
            handler.execute(mock_session, cmd)

            call_args = mock_path.call_args[0]
            assert call_args[1] == HexCoord(5, 5)  # Uses fleet location

    def test_ignores_non_move_orders_for_start_hex(self, mock_session, mock_fleet, mock_planet):
        """Non-MOVE orders are ignored when determining start hex."""
        from game.strategy.engine.superweapon_command_handlers import ImplodePlanetMissionCommandHandler
        from game.strategy.engine.commands import QueueImplodePlanetMissionCommand

        # Last order is not a MOVE order
        existing_order = Order(OrderType.IMPLODE_PLANET, target=mock_planet)
        mock_fleet.orders = [existing_order]

        target_hex = HexCoord(10, 10)
        cmd = QueueImplodePlanetMissionCommand(fleet_id=1, target_hex=target_hex, planet_id=100)
        handler = ImplodePlanetMissionCommandHandler()

        with patch('game.strategy.engine.superweapon_command_handlers.SuperweaponValidator') as mock_validator, \
             patch('game.strategy.engine.command_handlers.find_hybrid_path') as mock_path:
            mock_validator.validate_implode_planet.return_value = ValidationResult()
            mock_path.return_value = [HexCoord(5, 5), HexCoord(10, 10)]
            handler.execute(mock_session, cmd)

            call_args = mock_path.call_args[0]
            # Should use fleet location, not the IMPLODE_PLANET order's target
            assert call_args[1] == HexCoord(5, 5)

    def test_does_not_set_path_when_not_first_order(self, mock_session, mock_fleet, mock_planet):
        """fleet.path is not set when move order is not the first order."""
        from game.strategy.engine.superweapon_command_handlers import ImplodePlanetMissionCommandHandler
        from game.strategy.engine.commands import QueueImplodePlanetMissionCommand

        # Fleet already has an order
        existing_order = Order(OrderType.MOVE, target=HexCoord(8, 8))
        mock_fleet.orders = [existing_order]

        target_hex = HexCoord(12, 12)
        cmd = QueueImplodePlanetMissionCommand(fleet_id=1, target_hex=target_hex, planet_id=100)
        handler = ImplodePlanetMissionCommandHandler()

        with patch('game.strategy.engine.superweapon_command_handlers.SuperweaponValidator') as mock_validator, \
             patch('game.strategy.engine.command_handlers.find_hybrid_path') as mock_path:
            mock_validator.validate_implode_planet.return_value = ValidationResult()
            mock_path.return_value = [HexCoord(8, 8), HexCoord(10, 10), HexCoord(12, 12)]
            handler.execute(mock_session, cmd)

            # Path should NOT be set (orders existed before this call)
            # Note: mock_fleet.path is [] initially and should remain unchanged
            assert mock_fleet.path == []


# =============================================================================
# Mission Handler Fleet/Planet Not Found Tests
# =============================================================================

class TestMissionHandlerNotFound:
    """Tests for mission handlers when fleet or planet not found."""

    def test_implode_planet_mission_fleet_not_found(self, mock_session):
        """ImplodePlanetMissionCommandHandler returns invalid when fleet not found."""
        from game.strategy.engine.superweapon_command_handlers import ImplodePlanetMissionCommandHandler
        from game.strategy.engine.commands import QueueImplodePlanetMissionCommand

        mock_session._get_fleet_by_id.return_value = None
        cmd = QueueImplodePlanetMissionCommand(fleet_id=999, target_hex=HexCoord(10, 10), planet_id=100)
        handler = ImplodePlanetMissionCommandHandler()

        result = handler.execute(mock_session, cmd)

        assert not result.is_valid
        assert "Fleet not found" in result.message

    def test_implode_planet_mission_planet_not_found(self, mock_session, mock_fleet):
        """ImplodePlanetMissionCommandHandler returns invalid when planet not found."""
        from game.strategy.engine.superweapon_command_handlers import ImplodePlanetMissionCommandHandler
        from game.strategy.engine.commands import QueueImplodePlanetMissionCommand

        mock_session._get_planet_by_id.return_value = None
        cmd = QueueImplodePlanetMissionCommand(fleet_id=1, target_hex=HexCoord(10, 10), planet_id=999)
        handler = ImplodePlanetMissionCommandHandler()

        result = handler.execute(mock_session, cmd)

        assert not result.is_valid
        assert "Planet not found" in result.message

    def test_stellerate_mission_fleet_not_found(self, mock_session):
        """StellerateStarMissionCommandHandler returns invalid when fleet not found."""
        from game.strategy.engine.superweapon_command_handlers import StellerateStarMissionCommandHandler
        from game.strategy.engine.commands import QueueStellerateStarMissionCommand

        mock_session._get_fleet_by_id.return_value = None
        cmd = QueueStellerateStarMissionCommand(fleet_id=999, target_hex=HexCoord(10, 10))
        handler = StellerateStarMissionCommandHandler()

        result = handler.execute(mock_session, cmd)

        assert not result.is_valid
        assert "Fleet not found" in result.message

    def test_open_warp_point_mission_fleet_not_found(self, mock_session):
        """OpenWarpPointMissionCommandHandler returns invalid when fleet not found."""
        from game.strategy.engine.superweapon_command_handlers import OpenWarpPointMissionCommandHandler
        from game.strategy.engine.commands import QueueOpenWarpPointMissionCommand

        mock_session._get_fleet_by_id.return_value = None
        cmd = QueueOpenWarpPointMissionCommand(
            fleet_id=999, target_hex=HexCoord(10, 10), target_system_name="Beta"
        )
        handler = OpenWarpPointMissionCommandHandler()

        result = handler.execute(mock_session, cmd)

        assert not result.is_valid
        assert "Fleet not found" in result.message

    def test_close_warp_point_mission_fleet_not_found(self, mock_session):
        """CloseWarpPointMissionCommandHandler returns invalid when fleet not found."""
        from game.strategy.engine.superweapon_command_handlers import CloseWarpPointMissionCommandHandler
        from game.strategy.engine.commands import QueueCloseWarpPointMissionCommand

        mock_session._get_fleet_by_id.return_value = None
        cmd = QueueCloseWarpPointMissionCommand(
            fleet_id=999, target_hex=HexCoord(10, 10), warp_point_destination_id="Beta"
        )
        handler = CloseWarpPointMissionCommandHandler()

        result = handler.execute(mock_session, cmd)

        assert not result.is_valid
        assert "Fleet not found" in result.message

    def test_create_dyson_sphere_mission_fleet_not_found(self, mock_session):
        """CreateDysonSphereMissionCommandHandler returns invalid when fleet not found."""
        from game.strategy.engine.superweapon_command_handlers import CreateDysonSphereMissionCommandHandler
        from game.strategy.engine.commands import QueueCreateDysonSphereMissionCommand

        mock_session._get_fleet_by_id.return_value = None
        cmd = QueueCreateDysonSphereMissionCommand(fleet_id=999, target_hex=HexCoord(10, 10))
        handler = CreateDysonSphereMissionCommandHandler()

        result = handler.execute(mock_session, cmd)

        assert not result.is_valid
        assert "Fleet not found" in result.message


# =============================================================================
# Order Processor Error Cases
# =============================================================================

class TestOrderProcessorErrorCases:
    """Tests for error cases in SuperweaponOrderProcessor."""

    def test_implode_planet_no_order(self):
        """process_implode_planet fails when fleet has no order."""
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor

        fleet = Mock()
        fleet.get_current_order.return_value = None

        empire = Mock()
        processor = SuperweaponOrderProcessor()
        result = processor.process_implode_planet(fleet, empire, Mock(), [empire])

        assert not result.success
        assert "No IMPLODE_PLANET order" in result.message

    def test_implode_planet_wrong_order_type(self):
        """process_implode_planet fails when order is wrong type."""
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor

        fleet = Mock()
        fleet.get_current_order.return_value = Order(OrderType.MOVE, target=HexCoord(10, 10))

        empire = Mock()
        processor = SuperweaponOrderProcessor()
        result = processor.process_implode_planet(fleet, empire, Mock(), [empire])

        assert not result.success
        assert "No IMPLODE_PLANET order" in result.message

    def test_implode_planet_no_target_planet(self):
        """process_implode_planet fails when order has no target planet."""
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor

        fleet = Mock()
        fleet.get_current_order.return_value = Order(OrderType.IMPLODE_PLANET, target=None)
        fleet.pop_order = Mock()

        empire = Mock()
        processor = SuperweaponOrderProcessor()
        result = processor.process_implode_planet(fleet, empire, Mock(), [empire])

        assert not result.success
        assert "No target planet" in result.message
        fleet.pop_order.assert_called_once()

    def test_stellerate_star_no_order(self):
        """process_stellerate_star fails when fleet has no order."""
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor

        fleet = Mock()
        fleet.get_current_order.return_value = None

        processor = SuperweaponOrderProcessor()
        result = processor.process_stellerate_star(fleet, Mock(), Mock(), [])

        assert not result.success
        assert "No STELLERATE_STAR order" in result.message

    def test_stellerate_star_not_at_system(self):
        """process_stellerate_star fails when fleet not at a star system."""
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor

        fleet = Mock()
        fleet.location = HexCoord(100, 100)
        fleet.get_current_order.return_value = Order(OrderType.STELLERATE_STAR)
        fleet.pop_order = Mock()

        galaxy = Mock()
        galaxy.systems = {}  # Empty dict for get_system_at_hex lookup

        processor = SuperweaponOrderProcessor()
        result = processor.process_stellerate_star(fleet, Mock(), galaxy, [])

        assert not result.success
        assert "not at a star system" in result.message
        fleet.pop_order.assert_called_once()

    def test_open_warp_point_invalid_params(self):
        """process_open_warp_point fails when target is not a dict."""
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor

        fleet = Mock()
        fleet.get_current_order.return_value = Order(OrderType.OPEN_WARP_POINT, target="invalid")
        fleet.pop_order = Mock()

        processor = SuperweaponOrderProcessor()
        result = processor.process_open_warp_point(fleet, Mock(), Mock())

        assert not result.success
        assert "Invalid warp point params" in result.message
        fleet.pop_order.assert_called_once()

    def test_open_warp_point_not_at_system(self):
        """process_open_warp_point fails when fleet not at star system."""
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor

        fleet = Mock()
        fleet.location = HexCoord(100, 100)
        fleet.get_current_order.return_value = Order(
            OrderType.OPEN_WARP_POINT, target={'target_system_name': 'Beta'}
        )
        fleet.pop_order = Mock()

        galaxy = Mock()
        galaxy.systems = {}  # Empty dict for get_system_at_hex lookup

        processor = SuperweaponOrderProcessor()
        result = processor.process_open_warp_point(fleet, Mock(), galaxy)

        assert not result.success
        assert "not at a star system" in result.message
        fleet.pop_order.assert_called_once()

    def test_open_warp_point_target_system_not_found(self):
        """process_open_warp_point fails when target system not found."""
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor

        fleet = Mock()
        fleet.location = HexCoord(10, 10)
        fleet.get_current_order.return_value = Order(
            OrderType.OPEN_WARP_POINT, target={'target_system_name': 'Nonexistent'}
        )
        fleet.pop_order = Mock()

        current_system = Mock()
        current_system.name = "Alpha"
        current_system.global_location = HexCoord(10, 10)

        galaxy = Mock()
        galaxy.systems = {HexCoord(10, 10): current_system}  # For get_system_at_hex lookup
        galaxy.name_map = {'Alpha': current_system}  # No 'Nonexistent'

        processor = SuperweaponOrderProcessor()
        result = processor.process_open_warp_point(fleet, Mock(), galaxy)

        assert not result.success
        assert "not found" in result.message
        fleet.pop_order.assert_called_once()

    def test_close_warp_point_no_destination(self):
        """process_close_warp_point fails when no destination specified."""
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor

        fleet = Mock()
        fleet.get_current_order.return_value = Order(OrderType.CLOSE_WARP_POINT, target=None)
        fleet.pop_order = Mock()

        processor = SuperweaponOrderProcessor()
        result = processor.process_close_warp_point(fleet, Mock(), Mock())

        assert not result.success
        assert "No destination" in result.message
        fleet.pop_order.assert_called_once()

    def test_close_warp_point_not_at_system(self):
        """process_close_warp_point fails when fleet not at star system."""
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor

        fleet = Mock()
        fleet.location = HexCoord(100, 100)
        fleet.get_current_order.return_value = Order(OrderType.CLOSE_WARP_POINT, target={'destination_id': 'Beta', 'target_hex': {'q': 100, 'r': 100}})
        fleet.pop_order = Mock()

        galaxy = Mock()
        galaxy.systems = {}  # Empty dict for get_system_at_hex lookup

        processor = SuperweaponOrderProcessor()
        result = processor.process_close_warp_point(fleet, Mock(), galaxy)

        assert not result.success
        assert "not at a star system" in result.message
        fleet.pop_order.assert_called_once()

    def test_create_dyson_sphere_no_stars(self):
        """process_create_dyson_sphere fails when system has no stars."""
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor

        fleet = Mock()
        fleet.location = HexCoord(10, 10)
        fleet.get_current_order.return_value = Order(OrderType.CREATE_DYSON_SPHERE)
        fleet.pop_order = Mock()

        system = Mock()
        system.stars = []  # No stars
        system.planets = []

        galaxy = Mock()
        galaxy.systems = {HexCoord(10, 10): system}  # For get_system_at_hex lookup

        empire = Mock()
        processor = SuperweaponOrderProcessor()
        result = processor.process_create_dyson_sphere(fleet, empire, galaxy, [empire])

        assert not result.success
        assert "no stars" in result.message
        fleet.pop_order.assert_called_once()

    def test_self_destruct_empty_ship_ids(self):
        """process_self_destruct fails when ship_ids is empty list."""
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor

        fleet = Mock()
        fleet.get_current_order.return_value = Order(OrderType.SELF_DESTRUCT, target=[])
        fleet.pop_order = Mock()

        processor = SuperweaponOrderProcessor()
        result = processor.process_self_destruct(fleet, Mock(), Mock())

        assert not result.success
        assert "No ships specified" in result.message
        fleet.pop_order.assert_called_once()

    def test_self_destruct_invalid_target_type(self):
        """process_self_destruct fails when target is not a list."""
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor

        fleet = Mock()
        fleet.get_current_order.return_value = Order(OrderType.SELF_DESTRUCT, target="invalid")
        fleet.pop_order = Mock()

        processor = SuperweaponOrderProcessor()
        result = processor.process_self_destruct(fleet, Mock(), Mock())

        assert not result.success
        assert "No ships specified" in result.message
        fleet.pop_order.assert_called_once()


# =============================================================================
# Order Processor - No Ship With Ability
# =============================================================================

class TestOrderProcessorNoAbility:
    """Tests for order processors when no ship has required ability."""

    def test_implode_planet_no_ability_with_registry(self):
        """process_implode_planet fails when no ship has DestroyPlanet ability."""
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor

        # Ship without DestroyPlanet
        ship = Mock()
        ship.id = "ship-1"
        ship.design_data = {'layers': {'core': [{'id': 'laser'}]}}

        fleet = Mock()
        fleet.ships = [ship]
        fleet.get_current_order.return_value = Order(OrderType.IMPLODE_PLANET, target=Mock(name="Planet"))
        fleet.pop_order = Mock()

        galaxy = Mock()
        galaxy.unregister_planet = Mock()

        # Registry without DestroyPlanet ability for 'laser'
        component_registry = {'laser': {'abilities': {}}}

        empire = Mock(colonies=[])
        processor = SuperweaponOrderProcessor()
        with patch('game.strategy.engine.superweapon_order_processor.SuperweaponValidator.find_ship_with_ability', return_value=None):
            result = processor.process_implode_planet(fleet, empire, galaxy, [empire], component_registry)

        assert not result.success
        assert "DestroyPlanet ability" in result.message
        fleet.pop_order.assert_called_once()


# =============================================================================
# Order Processor - Colony Removal
# =============================================================================

class TestOrderProcessorColonyRemoval:
    """Tests for colony removal in order processors."""

    def test_implode_planet_removes_from_empire_colonies(self):
        """Owned planet should be removed from empire's colonies list."""
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor

        planet = Mock()
        planet.name = "Owned Planet"
        planet.owner_id = 1

        ship = Mock()
        ship.id = "ship-1"
        ship.design_data = {'layers': {'core': [{'id': 'planet_imploder'}]}}

        fleet = Mock()
        fleet.id = 1
        fleet.ships = [ship]
        fleet.get_current_order.return_value = Order(OrderType.IMPLODE_PLANET, target=planet)
        fleet.pop_order = Mock()
        fleet.remove_ship = Mock()

        empire = Mock()
        empire.id = 1
        empire.colonies = [planet]

        galaxy = Mock()
        galaxy.unregister_planet = Mock()

        component_registry = {'planet_imploder': {'abilities': {'DestroyPlanet': {}}}}

        processor = SuperweaponOrderProcessor()
        with patch('game.strategy.engine.superweapon_order_processor.SuperweaponValidator.find_ship_with_ability', return_value=ship):
            processor.process_implode_planet(fleet, empire, galaxy, [empire], component_registry)

        # Planet should be removed from colonies
        assert planet not in empire.colonies

    def test_stellerate_star_removes_all_colonies_from_all_empires(self):
        """All planets in system should be removed from all empire colonies."""
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor

        planet1 = Mock()
        planet1.name = "Empire1 Planet"
        planet1.owner_id = 1

        planet2 = Mock()
        planet2.name = "Empire2 Planet"
        planet2.owner_id = 2

        ship = Mock()
        ship.id = "ship-1"
        ship.design_data = {'layers': {'core': [{'id': 'stellerator'}]}}

        fleet = Mock()
        fleet.id = 1
        fleet.location = HexCoord(10, 10)
        fleet.ships = [ship]
        fleet.get_current_order.return_value = Order(OrderType.STELLERATE_STAR)
        fleet.pop_order = Mock()

        empire1 = Mock()
        empire1.id = 1
        empire1.colonies = [planet1]
        empire1.fleets = [fleet]  # Post-PROJ-277 SystemDestroyer iterates empire.fleets
        empire1.remove_fleet = Mock()

        empire2 = Mock()
        empire2.id = 2
        empire2.colonies = [planet2]
        empire2.fleets = []
        empire2.remove_fleet = Mock()

        system = Mock()
        system.name = "Alpha"
        system.global_location = HexCoord(10, 10)
        system.stars = [Mock()]
        system.planets = [planet1, planet2]
        system.warp_points = []

        galaxy = Mock()
        galaxy.systems = {HexCoord(10, 10): system}  # For get_system_at_hex lookup
        galaxy.get_all_fleets_in_system.return_value = [(empire1, fleet)]
        galaxy.unregister_planet = Mock()

        component_registry = {'stellerator': {'abilities': {'DestroyStar': {}}}}
        empires = [empire1, empire2]

        processor = SuperweaponOrderProcessor()
        processor.process_stellerate_star(fleet, empire1, galaxy, empires, component_registry)

        # Both planets should be removed from respective empire colonies
        assert planet1 not in empire1.colonies
        assert planet2 not in empire2.colonies


# =============================================================================
# Self-Destruct Ship Name Handling
# =============================================================================

class TestSelfDestructShipNames:
    """Tests for ship name handling in self-destruct."""

    def test_handles_mock_ship_without_name(self):
        """Self-destruct handles ships without proper name attribute."""
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor

        # Ship with non-string name (mock's default)
        ship = Mock()
        ship.id = "ship-1"
        ship.name = Mock()  # Not a string

        fleet = Mock()
        fleet.id = 1
        fleet.ships = [ship]
        fleet.get_current_order.return_value = Order(OrderType.SELF_DESTRUCT, target=["ship-1"])
        fleet.pop_order = Mock()
        fleet.remove_ship = Mock()

        processor = SuperweaponOrderProcessor()
        empire = Mock()
        empire.id = 0

        # Should not raise, should use ship_id as name fallback
        with patch('game.strategy.engine.superweapon_order_processor.logger'):
            result = processor.process_self_destruct(fleet, empire, Mock())

        assert result.success
        fleet.remove_ship.assert_called_once_with(ship)

    def test_handles_ship_with_none_name(self):
        """Self-destruct handles ships with None name."""
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor

        ship = Mock()
        ship.id = "ship-1"
        ship.name = None

        fleet = Mock()
        fleet.id = 1
        fleet.ships = [ship]
        fleet.get_current_order.return_value = Order(OrderType.SELF_DESTRUCT, target=["ship-1"])
        fleet.pop_order = Mock()
        fleet.remove_ship = Mock()

        processor = SuperweaponOrderProcessor()
        empire = Mock()
        empire.id = 0

        with patch('game.strategy.engine.superweapon_order_processor.logger'):
            result = processor.process_self_destruct(fleet, empire, Mock())

        assert result.success

    def test_skips_nonexistent_ship_ids(self):
        """Self-destruct skips ship IDs that don't exist in fleet."""
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor

        ship = Mock()
        ship.id = "ship-1"
        ship.name = "Existing Ship"

        fleet = Mock()
        fleet.id = 1
        fleet.ships = [ship]
        # Request to destroy both existing and nonexistent ship
        fleet.get_current_order.return_value = Order(
            OrderType.SELF_DESTRUCT, target=["ship-1", "nonexistent"]
        )
        fleet.pop_order = Mock()
        fleet.remove_ship = Mock()

        processor = SuperweaponOrderProcessor()
        empire = Mock()

        with patch('game.strategy.engine.superweapon_order_processor.logger'):
            result = processor.process_self_destruct(fleet, empire, Mock())

        assert result.success
        # Only existing ship should be removed
        fleet.remove_ship.assert_called_once_with(ship)
