"""
Unit tests for superweapon command handlers.

PROJ-102 Phase 5: Tests for command handlers that wire commands to validators
and create fleet orders.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from game.core.hex_math import HexCoord
from game.core.validation import ValidationResult
from game.strategy.data.order_types import FleetOrder, OrderType


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
    return planet


@pytest.fixture
def mock_galaxy():
    """Create a mock galaxy with a star system."""
    galaxy = Mock()
    system = Mock()
    system.stars = [Mock()]
    system.planets = []
    system.warp_points = []
    system.global_location = HexCoord(5, 5)
    galaxy.systems = {HexCoord(5, 5): system}
    galaxy.name_map = {"Target System": system}
    galaxy.get_planet_by_id = Mock(return_value=None)
    return galaxy


@pytest.fixture
def mock_session(mock_fleet, mock_galaxy, mock_planet):
    """Create a mock game session."""
    session = Mock()
    session._get_fleet_by_id = Mock(return_value=mock_fleet)
    session._get_planet_by_id = Mock(return_value=mock_planet)
    session.galaxy = mock_galaxy
    session.empires = []
    return session


# =============================================================================
# Direct Handler Tests - ImplodePlanetCommandHandler
# =============================================================================

class TestImplodePlanetCommandHandler:
    """Tests for ImplodePlanetCommandHandler."""

    def test_execute_returns_valid_when_validation_passes(self, mock_session, mock_fleet, mock_planet):
        """Handler returns valid result when validation passes."""
        from game.strategy.engine.superweapon_command_handlers import ImplodePlanetCommandHandler
        from game.strategy.engine.commands import IssueImplodePlanetCommand

        cmd = IssueImplodePlanetCommand(fleet_id=1, planet_id=100)
        handler = ImplodePlanetCommandHandler()

        with patch('game.strategy.engine.superweapon_command_handlers.SuperweaponValidator') as mock_validator:
            mock_validator.validate_implode_planet.return_value = ValidationResult()
            result = handler.execute(mock_session, cmd)

        assert result.is_valid

    def test_execute_adds_correct_order_type(self, mock_session, mock_fleet, mock_planet):
        """Handler adds IMPLODE_PLANET order to fleet."""
        from game.strategy.engine.superweapon_command_handlers import ImplodePlanetCommandHandler
        from game.strategy.engine.commands import IssueImplodePlanetCommand

        cmd = IssueImplodePlanetCommand(fleet_id=1, planet_id=100)
        handler = ImplodePlanetCommandHandler()

        with patch('game.strategy.engine.superweapon_command_handlers.SuperweaponValidator') as mock_validator:
            mock_validator.validate_implode_planet.return_value = ValidationResult()
            handler.execute(mock_session, cmd)

        assert len(mock_fleet.orders) == 1
        assert mock_fleet.orders[0].type == OrderType.IMPLODE_PLANET

    def test_execute_fails_when_fleet_not_found(self, mock_session):
        """Handler returns invalid when fleet not found."""
        from game.strategy.engine.superweapon_command_handlers import ImplodePlanetCommandHandler
        from game.strategy.engine.commands import IssueImplodePlanetCommand

        mock_session._get_fleet_by_id.return_value = None
        cmd = IssueImplodePlanetCommand(fleet_id=999, planet_id=100)
        handler = ImplodePlanetCommandHandler()

        result = handler.execute(mock_session, cmd)

        assert not result.is_valid
        assert "Fleet not found" in result.message

    def test_execute_fails_when_validation_fails(self, mock_session, mock_fleet):
        """Handler returns invalid when validation fails."""
        from game.strategy.engine.superweapon_command_handlers import ImplodePlanetCommandHandler
        from game.strategy.engine.commands import IssueImplodePlanetCommand

        cmd = IssueImplodePlanetCommand(fleet_id=1, planet_id=100)
        handler = ImplodePlanetCommandHandler()

        with patch('game.strategy.engine.superweapon_command_handlers.SuperweaponValidator') as mock_validator:
            mock_validator.validate_implode_planet.return_value = ValidationResult.error(
                "No ship in fleet has DestroyPlanet ability."
            )
            result = handler.execute(mock_session, cmd)

        assert not result.is_valid
        assert "DestroyPlanet" in result.message


# =============================================================================
# Direct Handler Tests - StellerateStarCommandHandler
# =============================================================================

class TestStellerateStarCommandHandler:
    """Tests for StellerateStarCommandHandler."""

    def test_execute_returns_valid_when_validation_passes(self, mock_session, mock_fleet):
        """Handler returns valid result when validation passes."""
        from game.strategy.engine.superweapon_command_handlers import StellerateStarCommandHandler
        from game.strategy.engine.commands import IssueStellerateStarCommand

        cmd = IssueStellerateStarCommand(fleet_id=1)
        handler = StellerateStarCommandHandler()

        with patch('game.strategy.engine.superweapon_command_handlers.SuperweaponValidator') as mock_validator:
            mock_validator.validate_stellerate_star.return_value = ValidationResult()
            result = handler.execute(mock_session, cmd)

        assert result.is_valid

    def test_execute_adds_correct_order_type(self, mock_session, mock_fleet):
        """Handler adds STELLERATE_STAR order to fleet."""
        from game.strategy.engine.superweapon_command_handlers import StellerateStarCommandHandler
        from game.strategy.engine.commands import IssueStellerateStarCommand

        cmd = IssueStellerateStarCommand(fleet_id=1)
        handler = StellerateStarCommandHandler()

        with patch('game.strategy.engine.superweapon_command_handlers.SuperweaponValidator') as mock_validator:
            mock_validator.validate_stellerate_star.return_value = ValidationResult()
            handler.execute(mock_session, cmd)

        assert len(mock_fleet.orders) == 1
        assert mock_fleet.orders[0].type == OrderType.STELLERATE_STAR
        assert mock_fleet.orders[0].target is None

    def test_execute_fails_when_fleet_not_found(self, mock_session):
        """Handler returns invalid when fleet not found."""
        from game.strategy.engine.superweapon_command_handlers import StellerateStarCommandHandler
        from game.strategy.engine.commands import IssueStellerateStarCommand

        mock_session._get_fleet_by_id.return_value = None
        cmd = IssueStellerateStarCommand(fleet_id=999)
        handler = StellerateStarCommandHandler()

        result = handler.execute(mock_session, cmd)

        assert not result.is_valid


# =============================================================================
# Direct Handler Tests - OpenWarpPointCommandHandler
# =============================================================================

class TestOpenWarpPointCommandHandler:
    """Tests for OpenWarpPointCommandHandler."""

    def test_execute_returns_valid_when_validation_passes(self, mock_session, mock_fleet):
        """Handler returns valid result when validation passes."""
        from game.strategy.engine.superweapon_command_handlers import OpenWarpPointCommandHandler
        from game.strategy.engine.commands import IssueOpenWarpPointCommand

        cmd = IssueOpenWarpPointCommand(
            fleet_id=1,
            target_hex=HexCoord(10, 10),
            target_system_name="Target System"
        )
        handler = OpenWarpPointCommandHandler()

        with patch('game.strategy.engine.superweapon_command_handlers.SuperweaponValidator') as mock_validator:
            mock_validator.validate_open_warp_point.return_value = ValidationResult()
            result = handler.execute(mock_session, cmd)

        assert result.is_valid

    def test_execute_adds_order_with_target_dict(self, mock_session, mock_fleet):
        """Handler adds OPEN_WARP_POINT order with target dict."""
        from game.strategy.engine.superweapon_command_handlers import OpenWarpPointCommandHandler
        from game.strategy.engine.commands import IssueOpenWarpPointCommand

        cmd = IssueOpenWarpPointCommand(
            fleet_id=1,
            target_hex=HexCoord(10, 10),
            target_system_name="Target System"
        )
        handler = OpenWarpPointCommandHandler()

        with patch('game.strategy.engine.superweapon_command_handlers.SuperweaponValidator') as mock_validator:
            mock_validator.validate_open_warp_point.return_value = ValidationResult()
            handler.execute(mock_session, cmd)

        assert len(mock_fleet.orders) == 1
        assert mock_fleet.orders[0].type == OrderType.OPEN_WARP_POINT
        assert mock_fleet.orders[0].target['target_hex'] == HexCoord(10, 10)
        assert mock_fleet.orders[0].target['target_system_name'] == "Target System"


# =============================================================================
# Direct Handler Tests - CloseWarpPointCommandHandler
# =============================================================================

class TestCloseWarpPointCommandHandler:
    """Tests for CloseWarpPointCommandHandler."""

    def test_execute_returns_valid_when_validation_passes(self, mock_session, mock_fleet):
        """Handler returns valid result when validation passes."""
        from game.strategy.engine.superweapon_command_handlers import CloseWarpPointCommandHandler
        from game.strategy.engine.commands import IssueCloseWarpPointCommand

        cmd = IssueCloseWarpPointCommand(fleet_id=1, warp_point_destination_id="Alpha Centauri")
        handler = CloseWarpPointCommandHandler()

        with patch('game.strategy.engine.superweapon_command_handlers.SuperweaponValidator') as mock_validator:
            mock_validator.validate_close_warp_point.return_value = ValidationResult()
            result = handler.execute(mock_session, cmd)

        assert result.is_valid

    def test_execute_adds_order_with_destination_id(self, mock_session, mock_fleet):
        """Handler adds CLOSE_WARP_POINT order with destination ID."""
        from game.strategy.engine.superweapon_command_handlers import CloseWarpPointCommandHandler
        from game.strategy.engine.commands import IssueCloseWarpPointCommand

        cmd = IssueCloseWarpPointCommand(fleet_id=1, warp_point_destination_id="Alpha Centauri")
        handler = CloseWarpPointCommandHandler()

        with patch('game.strategy.engine.superweapon_command_handlers.SuperweaponValidator') as mock_validator:
            mock_validator.validate_close_warp_point.return_value = ValidationResult()
            handler.execute(mock_session, cmd)

        assert len(mock_fleet.orders) == 1
        assert mock_fleet.orders[0].type == OrderType.CLOSE_WARP_POINT
        assert mock_fleet.orders[0].target == "Alpha Centauri"


# =============================================================================
# Direct Handler Tests - CreateDysonSphereCommandHandler
# =============================================================================

class TestCreateDysonSphereCommandHandler:
    """Tests for CreateDysonSphereCommandHandler."""

    def test_execute_returns_valid_when_validation_passes(self, mock_session, mock_fleet):
        """Handler returns valid result when validation passes."""
        from game.strategy.engine.superweapon_command_handlers import CreateDysonSphereCommandHandler
        from game.strategy.engine.commands import IssueCreateDysonSphereCommand

        cmd = IssueCreateDysonSphereCommand(fleet_id=1)
        handler = CreateDysonSphereCommandHandler()

        with patch('game.strategy.engine.superweapon_command_handlers.SuperweaponValidator') as mock_validator:
            mock_validator.validate_create_dyson_sphere.return_value = ValidationResult()
            result = handler.execute(mock_session, cmd)

        assert result.is_valid

    def test_execute_adds_order_with_no_target(self, mock_session, mock_fleet):
        """Handler adds CREATE_DYSON_SPHERE order with None target."""
        from game.strategy.engine.superweapon_command_handlers import CreateDysonSphereCommandHandler
        from game.strategy.engine.commands import IssueCreateDysonSphereCommand

        cmd = IssueCreateDysonSphereCommand(fleet_id=1)
        handler = CreateDysonSphereCommandHandler()

        with patch('game.strategy.engine.superweapon_command_handlers.SuperweaponValidator') as mock_validator:
            mock_validator.validate_create_dyson_sphere.return_value = ValidationResult()
            handler.execute(mock_session, cmd)

        assert len(mock_fleet.orders) == 1
        assert mock_fleet.orders[0].type == OrderType.CREATE_DYSON_SPHERE
        assert mock_fleet.orders[0].target is None


# =============================================================================
# Direct Handler Tests - SelfDestructCommandHandler
# =============================================================================

class TestSelfDestructCommandHandler:
    """Tests for SelfDestructCommandHandler."""

    def test_execute_returns_valid_when_validation_passes(self, mock_session, mock_fleet):
        """Handler returns valid result when validation passes."""
        from game.strategy.engine.superweapon_command_handlers import SelfDestructCommandHandler
        from game.strategy.engine.commands import IssueSelfDestructCommand

        mock_fleet.ships = [Mock(id=1), Mock(id=2)]
        cmd = IssueSelfDestructCommand(fleet_id=1, ship_ids=[1, 2])
        handler = SelfDestructCommandHandler()

        with patch('game.strategy.engine.superweapon_command_handlers.SuperweaponValidator') as mock_validator:
            mock_validator.validate_self_destruct.return_value = ValidationResult()
            result = handler.execute(mock_session, cmd)

        assert result.is_valid

    def test_execute_adds_order_with_ship_ids(self, mock_session, mock_fleet):
        """Handler adds SELF_DESTRUCT order with ship IDs list."""
        from game.strategy.engine.superweapon_command_handlers import SelfDestructCommandHandler
        from game.strategy.engine.commands import IssueSelfDestructCommand

        mock_fleet.ships = [Mock(id=1), Mock(id=2)]
        cmd = IssueSelfDestructCommand(fleet_id=1, ship_ids=[1, 2])
        handler = SelfDestructCommandHandler()

        with patch('game.strategy.engine.superweapon_command_handlers.SuperweaponValidator') as mock_validator:
            mock_validator.validate_self_destruct.return_value = ValidationResult()
            handler.execute(mock_session, cmd)

        assert len(mock_fleet.orders) == 1
        assert mock_fleet.orders[0].type == OrderType.SELF_DESTRUCT
        assert mock_fleet.orders[0].target == [1, 2]


# =============================================================================
# Mission Handler Tests - ImplodePlanetMissionCommandHandler
# =============================================================================

class TestImplodePlanetMissionCommandHandler:
    """Tests for ImplodePlanetMissionCommandHandler."""

    def test_execute_creates_move_and_action_orders(self, mock_session, mock_fleet, mock_planet):
        """Mission handler creates MOVE + IMPLODE_PLANET orders."""
        from game.strategy.engine.superweapon_command_handlers import ImplodePlanetMissionCommandHandler
        from game.strategy.engine.commands import QueueImplodePlanetMissionCommand

        target_hex = HexCoord(10, 10)
        cmd = QueueImplodePlanetMissionCommand(fleet_id=1, target_hex=target_hex, planet_id=100)
        handler = ImplodePlanetMissionCommandHandler()

        with patch('game.strategy.engine.superweapon_command_handlers.SuperweaponValidator') as mock_validator, \
             patch('game.strategy.engine.superweapon_command_handlers.find_hybrid_path') as mock_path:
            mock_validator.validate_implode_planet.return_value = ValidationResult()
            mock_path.return_value = [HexCoord(5, 5), HexCoord(7, 7), HexCoord(10, 10)]
            result = handler.execute(mock_session, cmd)

        assert result.is_valid
        assert len(mock_fleet.orders) == 2
        assert mock_fleet.orders[0].type == OrderType.MOVE
        assert mock_fleet.orders[1].type == OrderType.IMPLODE_PLANET

    def test_execute_sets_fleet_path_when_first_order(self, mock_session, mock_fleet, mock_planet):
        """Mission handler sets fleet.path when it's the first order."""
        from game.strategy.engine.superweapon_command_handlers import ImplodePlanetMissionCommandHandler
        from game.strategy.engine.commands import QueueImplodePlanetMissionCommand

        target_hex = HexCoord(10, 10)
        cmd = QueueImplodePlanetMissionCommand(fleet_id=1, target_hex=target_hex, planet_id=100)
        handler = ImplodePlanetMissionCommandHandler()

        path = [HexCoord(5, 5), HexCoord(7, 7), HexCoord(10, 10)]
        with patch('game.strategy.engine.superweapon_command_handlers.SuperweaponValidator') as mock_validator, \
             patch('game.strategy.engine.superweapon_command_handlers.find_hybrid_path') as mock_path:
            mock_validator.validate_implode_planet.return_value = ValidationResult()
            mock_path.return_value = path
            handler.execute(mock_session, cmd)

        # Path should be set (without the start hex)
        assert mock_fleet.path == [HexCoord(7, 7), HexCoord(10, 10)]


# =============================================================================
# Mission Handler Tests - StellerateStarMissionCommandHandler
# =============================================================================

class TestStellerateStarMissionCommandHandler:
    """Tests for StellerateStarMissionCommandHandler."""

    def test_execute_creates_move_and_action_orders(self, mock_session, mock_fleet):
        """Mission handler creates MOVE + STELLERATE_STAR orders."""
        from game.strategy.engine.superweapon_command_handlers import StellerateStarMissionCommandHandler
        from game.strategy.engine.commands import QueueStellerateStarMissionCommand

        target_hex = HexCoord(10, 10)
        cmd = QueueStellerateStarMissionCommand(fleet_id=1, target_hex=target_hex)
        handler = StellerateStarMissionCommandHandler()

        with patch('game.strategy.engine.superweapon_command_handlers.SuperweaponValidator') as mock_validator, \
             patch('game.strategy.engine.superweapon_command_handlers.find_hybrid_path') as mock_path:
            mock_validator.validate_stellerate_star.return_value = ValidationResult()
            mock_path.return_value = [HexCoord(5, 5), HexCoord(10, 10)]
            result = handler.execute(mock_session, cmd)

        assert result.is_valid
        assert len(mock_fleet.orders) == 2
        assert mock_fleet.orders[0].type == OrderType.MOVE
        assert mock_fleet.orders[1].type == OrderType.STELLERATE_STAR


# =============================================================================
# Mission Handler Tests - OpenWarpPointMissionCommandHandler
# =============================================================================

class TestOpenWarpPointMissionCommandHandler:
    """Tests for OpenWarpPointMissionCommandHandler."""

    def test_execute_creates_move_and_action_orders(self, mock_session, mock_fleet):
        """Mission handler creates MOVE + OPEN_WARP_POINT orders."""
        from game.strategy.engine.superweapon_command_handlers import OpenWarpPointMissionCommandHandler
        from game.strategy.engine.commands import QueueOpenWarpPointMissionCommand

        target_hex = HexCoord(10, 10)
        cmd = QueueOpenWarpPointMissionCommand(
            fleet_id=1,
            target_hex=target_hex,
            target_system_name="Target System"
        )
        handler = OpenWarpPointMissionCommandHandler()

        with patch('game.strategy.engine.superweapon_command_handlers.SuperweaponValidator') as mock_validator, \
             patch('game.strategy.engine.superweapon_command_handlers.find_hybrid_path') as mock_path:
            mock_validator.validate_open_warp_point.return_value = ValidationResult()
            mock_path.return_value = [HexCoord(5, 5), HexCoord(10, 10)]
            result = handler.execute(mock_session, cmd)

        assert result.is_valid
        assert len(mock_fleet.orders) == 2
        assert mock_fleet.orders[0].type == OrderType.MOVE
        assert mock_fleet.orders[1].type == OrderType.OPEN_WARP_POINT
        assert mock_fleet.orders[1].target['target_system_name'] == "Target System"


# =============================================================================
# Mission Handler Tests - CloseWarpPointMissionCommandHandler
# =============================================================================

class TestCloseWarpPointMissionCommandHandler:
    """Tests for CloseWarpPointMissionCommandHandler."""

    def test_execute_creates_move_and_action_orders(self, mock_session, mock_fleet):
        """Mission handler creates MOVE + CLOSE_WARP_POINT orders."""
        from game.strategy.engine.superweapon_command_handlers import CloseWarpPointMissionCommandHandler
        from game.strategy.engine.commands import QueueCloseWarpPointMissionCommand

        target_hex = HexCoord(10, 10)
        cmd = QueueCloseWarpPointMissionCommand(
            fleet_id=1,
            target_hex=target_hex,
            warp_point_destination_id="Alpha Centauri"
        )
        handler = CloseWarpPointMissionCommandHandler()

        with patch('game.strategy.engine.superweapon_command_handlers.SuperweaponValidator') as mock_validator, \
             patch('game.strategy.engine.superweapon_command_handlers.find_hybrid_path') as mock_path:
            mock_validator.validate_close_warp_point.return_value = ValidationResult()
            mock_path.return_value = [HexCoord(5, 5), HexCoord(10, 10)]
            result = handler.execute(mock_session, cmd)

        assert result.is_valid
        assert len(mock_fleet.orders) == 2
        assert mock_fleet.orders[0].type == OrderType.MOVE
        assert mock_fleet.orders[1].type == OrderType.CLOSE_WARP_POINT
        assert mock_fleet.orders[1].target == "Alpha Centauri"


# =============================================================================
# Mission Handler Tests - CreateDysonSphereMissionCommandHandler
# =============================================================================

class TestCreateDysonSphereMissionCommandHandler:
    """Tests for CreateDysonSphereMissionCommandHandler."""

    def test_execute_creates_move_and_action_orders(self, mock_session, mock_fleet):
        """Mission handler creates MOVE + CREATE_DYSON_SPHERE orders."""
        from game.strategy.engine.superweapon_command_handlers import CreateDysonSphereMissionCommandHandler
        from game.strategy.engine.commands import QueueCreateDysonSphereMissionCommand

        target_hex = HexCoord(10, 10)
        cmd = QueueCreateDysonSphereMissionCommand(fleet_id=1, target_hex=target_hex)
        handler = CreateDysonSphereMissionCommandHandler()

        with patch('game.strategy.engine.superweapon_command_handlers.SuperweaponValidator') as mock_validator, \
             patch('game.strategy.engine.superweapon_command_handlers.find_hybrid_path') as mock_path:
            mock_validator.validate_create_dyson_sphere.return_value = ValidationResult()
            mock_path.return_value = [HexCoord(5, 5), HexCoord(10, 10)]
            result = handler.execute(mock_session, cmd)

        assert result.is_valid
        assert len(mock_fleet.orders) == 2
        assert mock_fleet.orders[0].type == OrderType.MOVE
        assert mock_fleet.orders[1].type == OrderType.CREATE_DYSON_SPHERE


# =============================================================================
# Mission Handler - No Path Scenario
# =============================================================================

class TestMissionHandlerNoPath:
    """Tests for mission handlers when no path is found."""

    def test_returns_invalid_when_no_path_found(self, mock_session, mock_fleet):
        """Mission handler returns invalid when path is empty."""
        from game.strategy.engine.superweapon_command_handlers import StellerateStarMissionCommandHandler
        from game.strategy.engine.commands import QueueStellerateStarMissionCommand

        target_hex = HexCoord(100, 100)  # Unreachable
        cmd = QueueStellerateStarMissionCommand(fleet_id=1, target_hex=target_hex)
        handler = StellerateStarMissionCommandHandler()

        with patch('game.strategy.engine.superweapon_command_handlers.SuperweaponValidator') as mock_validator, \
             patch('game.strategy.engine.superweapon_command_handlers.find_hybrid_path') as mock_path:
            mock_validator.validate_stellerate_star.return_value = ValidationResult()
            mock_path.return_value = []  # No path found
            result = handler.execute(mock_session, cmd)

        assert not result.is_valid
        assert "No path" in result.message


# =============================================================================
# Registry Tests
# =============================================================================

class TestHandlerRegistration:
    """Tests for handler registration in the factory."""

    def test_all_handlers_registered(self):
        """All 11 superweapon handlers are registered in default registry."""
        from game.strategy.engine.command_handlers import create_default_registry

        registry = create_default_registry()

        # Direct handlers
        assert registry._handlers.get('IssueImplodePlanetCommand') is not None
        assert registry._handlers.get('IssueStellerateStarCommand') is not None
        assert registry._handlers.get('IssueOpenWarpPointCommand') is not None
        assert registry._handlers.get('IssueCloseWarpPointCommand') is not None
        assert registry._handlers.get('IssueCreateDysonSphereCommand') is not None
        assert registry._handlers.get('IssueSelfDestructCommand') is not None

        # Mission handlers
        assert registry._handlers.get('QueueImplodePlanetMissionCommand') is not None
        assert registry._handlers.get('QueueStellerateStarMissionCommand') is not None
        assert registry._handlers.get('QueueOpenWarpPointMissionCommand') is not None
        assert registry._handlers.get('QueueCloseWarpPointMissionCommand') is not None
        assert registry._handlers.get('QueueCreateDysonSphereMissionCommand') is not None


# =============================================================================
# Edge Cases
# =============================================================================

class TestHandlerEdgeCases:
    """Edge case tests for command handlers."""

    def test_mission_handler_skips_move_when_already_at_target(self, mock_session, mock_fleet):
        """Mission handler skips MOVE when fleet is already at target hex."""
        from game.strategy.engine.superweapon_command_handlers import StellerateStarMissionCommandHandler
        from game.strategy.engine.commands import QueueStellerateStarMissionCommand

        # Fleet is already at target
        target_hex = HexCoord(5, 5)  # Same as fleet location
        cmd = QueueStellerateStarMissionCommand(fleet_id=1, target_hex=target_hex)
        handler = StellerateStarMissionCommandHandler()

        with patch('game.strategy.engine.superweapon_command_handlers.SuperweaponValidator') as mock_validator, \
             patch('game.strategy.engine.superweapon_command_handlers.find_hybrid_path') as mock_path:
            mock_validator.validate_stellerate_star.return_value = ValidationResult()
            mock_path.return_value = [HexCoord(5, 5)]  # Already there
            result = handler.execute(mock_session, cmd)

        assert result.is_valid
        # Only action order, no MOVE
        assert len(mock_fleet.orders) == 1
        assert mock_fleet.orders[0].type == OrderType.STELLERATE_STAR

    def test_planet_not_found_returns_invalid(self, mock_session):
        """ImplodePlanetCommandHandler returns invalid when planet not found."""
        from game.strategy.engine.superweapon_command_handlers import ImplodePlanetCommandHandler
        from game.strategy.engine.commands import IssueImplodePlanetCommand

        mock_session._get_planet_by_id.return_value = None
        cmd = IssueImplodePlanetCommand(fleet_id=1, planet_id=999)
        handler = ImplodePlanetCommandHandler()

        result = handler.execute(mock_session, cmd)

        assert not result.is_valid
        assert "Planet not found" in result.message
