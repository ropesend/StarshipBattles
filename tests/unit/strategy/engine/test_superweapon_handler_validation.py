"""
Unit tests for superweapon command handler validation - PROJ-207 Phase 2.

Tests for Task 2.1 (VC-001) and Task 2.2 (VC-002/CP-005):
- Direct handlers pass component_registry to validators
- Mission handlers call validators before queuing orders
"""
import pytest
from unittest.mock import Mock, MagicMock, patch, PropertyMock
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
    fleet.ships = [Mock(id=1)]  # At least one ship
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
    galaxy.get_system_at_location = Mock(return_value=system)
    return galaxy


@pytest.fixture
def mock_component_registry():
    """Create a mock component registry."""
    return {"PlanetImploder": {"abilities": ["DestroyPlanet"]}}


@pytest.fixture
def mock_session(mock_fleet, mock_galaxy, mock_planet, mock_component_registry):
    """Create a mock game session with component registry."""
    session = Mock()
    session._get_fleet_by_id = Mock(return_value=mock_fleet)
    session._get_planet_by_id = Mock(return_value=mock_planet)
    session.galaxy = mock_galaxy
    session.empires = []

    # Use public registries API
    registries = Mock()
    registries.components = mock_component_registry
    session.registries = registries

    return session


# =============================================================================
# Task 2.1: Direct Handlers Pass component_registry (VC-001)
# =============================================================================

class TestImplodePlanetCommandHandlerPassesRegistry:
    """Tests that ImplodePlanetCommandHandler passes component_registry to validator."""

    def test_passes_component_registry_to_validator(self, mock_session, mock_component_registry):
        """Validator is called with component_registry parameter."""
        from game.strategy.engine.superweapon_command_handlers import ImplodePlanetCommandHandler
        from game.strategy.engine.commands import IssueImplodePlanetCommand

        cmd = IssueImplodePlanetCommand(fleet_id=1, planet_id=100)
        handler = ImplodePlanetCommandHandler()

        with patch('game.strategy.engine.superweapon_command_handlers.SuperweaponValidator') as mock_validator:
            mock_validator.validate_implode_planet.return_value = ValidationResult()
            handler.execute(mock_session, cmd)

            # Verify component_registry was passed
            call_kwargs = mock_validator.validate_implode_planet.call_args.kwargs
            assert 'component_registry' in call_kwargs
            assert call_kwargs['component_registry'] == mock_component_registry



class TestStellerateStarCommandHandlerPassesRegistry:
    """Tests that StellerateStarCommandHandler passes component_registry to validator."""

    def test_passes_component_registry_to_validator(self, mock_session, mock_component_registry):
        """Validator is called with component_registry parameter."""
        from game.strategy.engine.superweapon_command_handlers import StellerateStarCommandHandler
        from game.strategy.engine.commands import IssueStellerateStarCommand

        cmd = IssueStellerateStarCommand(fleet_id=1)
        handler = StellerateStarCommandHandler()

        with patch('game.strategy.engine.superweapon_command_handlers.SuperweaponValidator') as mock_validator:
            mock_validator.validate_stellerate_star.return_value = ValidationResult()
            handler.execute(mock_session, cmd)

            call_kwargs = mock_validator.validate_stellerate_star.call_args.kwargs
            assert 'component_registry' in call_kwargs
            assert call_kwargs['component_registry'] == mock_component_registry



class TestOpenWarpPointCommandHandlerPassesRegistry:
    """Tests that OpenWarpPointCommandHandler passes component_registry to validator."""

    def test_passes_component_registry_to_validator(self, mock_session, mock_component_registry):
        """Validator is called with component_registry parameter."""
        from game.strategy.engine.superweapon_command_handlers import OpenWarpPointCommandHandler
        from game.strategy.engine.commands import IssueOpenWarpPointCommand

        cmd = IssueOpenWarpPointCommand(
            fleet_id=1, target_hex=HexCoord(10, 10), target_system_name="Target System"
        )
        handler = OpenWarpPointCommandHandler()

        with patch('game.strategy.engine.superweapon_command_handlers.SuperweaponValidator') as mock_validator:
            mock_validator.validate_open_warp_point.return_value = ValidationResult()
            handler.execute(mock_session, cmd)

            call_kwargs = mock_validator.validate_open_warp_point.call_args.kwargs
            assert 'component_registry' in call_kwargs
            assert call_kwargs['component_registry'] == mock_component_registry



class TestCloseWarpPointCommandHandlerPassesRegistry:
    """Tests that CloseWarpPointCommandHandler passes component_registry to validator."""

    def test_passes_component_registry_to_validator(self, mock_session, mock_component_registry):
        """Validator is called with component_registry parameter."""
        from game.strategy.engine.superweapon_command_handlers import CloseWarpPointCommandHandler
        from game.strategy.engine.commands import IssueCloseWarpPointCommand

        cmd = IssueCloseWarpPointCommand(fleet_id=1, warp_point_destination_id="Alpha Centauri")
        handler = CloseWarpPointCommandHandler()

        with patch('game.strategy.engine.superweapon_command_handlers.SuperweaponValidator') as mock_validator:
            mock_validator.validate_close_warp_point.return_value = ValidationResult()
            handler.execute(mock_session, cmd)

            call_kwargs = mock_validator.validate_close_warp_point.call_args.kwargs
            assert 'component_registry' in call_kwargs
            assert call_kwargs['component_registry'] == mock_component_registry



class TestCreateDysonSphereCommandHandlerPassesRegistry:
    """Tests that CreateDysonSphereCommandHandler passes component_registry to validator."""

    def test_passes_component_registry_to_validator(self, mock_session, mock_component_registry):
        """Validator is called with component_registry parameter."""
        from game.strategy.engine.superweapon_command_handlers import CreateDysonSphereCommandHandler
        from game.strategy.engine.commands import IssueCreateDysonSphereCommand

        cmd = IssueCreateDysonSphereCommand(fleet_id=1)
        handler = CreateDysonSphereCommandHandler()

        with patch('game.strategy.engine.superweapon_command_handlers.SuperweaponValidator') as mock_validator:
            mock_validator.validate_create_dyson_sphere.return_value = ValidationResult()
            handler.execute(mock_session, cmd)

            call_kwargs = mock_validator.validate_create_dyson_sphere.call_args.kwargs
            assert 'component_registry' in call_kwargs
            assert call_kwargs['component_registry'] == mock_component_registry



# =============================================================================
# Task 2.2: Mission Handlers Call Validators (VC-002/CP-005)
# =============================================================================

class TestImplodePlanetMissionCommandHandlerValidates:
    """Tests that ImplodePlanetMissionCommandHandler calls validator."""

    def test_calls_validator_with_component_registry(self, mock_session, mock_component_registry):
        """Mission handler calls validator with component_registry."""
        from game.strategy.engine.superweapon_command_handlers import ImplodePlanetMissionCommandHandler
        from game.strategy.engine.commands import QueueImplodePlanetMissionCommand

        cmd = QueueImplodePlanetMissionCommand(
            fleet_id=1, target_hex=HexCoord(10, 10), planet_id=100
        )
        handler = ImplodePlanetMissionCommandHandler()

        with patch('game.strategy.engine.superweapon_command_handlers.SuperweaponValidator') as mock_validator, \
             patch('game.strategy.engine.command_handlers.find_hybrid_path') as mock_path:
            mock_validator.validate_implode_planet.return_value = ValidationResult()
            mock_path.return_value = [HexCoord(5, 5), HexCoord(10, 10)]
            handler.execute(mock_session, cmd)

            # Verify validator was called with component_registry
            mock_validator.validate_implode_planet.assert_called_once()
            call_kwargs = mock_validator.validate_implode_planet.call_args.kwargs
            assert 'component_registry' in call_kwargs
            assert call_kwargs['component_registry'] == mock_component_registry

    def test_rejects_fleet_without_ability(self, mock_session):
        """Mission handler rejects fleet without DestroyPlanet ability."""
        from game.strategy.engine.superweapon_command_handlers import ImplodePlanetMissionCommandHandler
        from game.strategy.engine.commands import QueueImplodePlanetMissionCommand

        cmd = QueueImplodePlanetMissionCommand(
            fleet_id=1, target_hex=HexCoord(10, 10), planet_id=100
        )
        handler = ImplodePlanetMissionCommandHandler()

        with patch('game.strategy.validation.superweapon_validator.SuperweaponValidator.find_ship_with_ability', return_value=None):
            result = handler.execute(mock_session, cmd)

        assert not result.is_valid
        assert "DestroyPlanet" in result.message


class TestStellerateStarMissionCommandHandlerValidates:
    """Tests that StellerateStarMissionCommandHandler calls validator."""

    def test_calls_validator_with_component_registry(self, mock_session, mock_component_registry):
        """Mission handler calls validator with component_registry."""
        from game.strategy.engine.superweapon_command_handlers import StellerateStarMissionCommandHandler
        from game.strategy.engine.commands import QueueStellerateStarMissionCommand

        cmd = QueueStellerateStarMissionCommand(fleet_id=1, target_hex=HexCoord(10, 10))
        handler = StellerateStarMissionCommandHandler()

        with patch('game.strategy.engine.superweapon_command_handlers.SuperweaponValidator') as mock_validator, \
             patch('game.strategy.engine.command_handlers.find_hybrid_path') as mock_path:
            mock_validator.validate_stellerate_star.return_value = ValidationResult()
            mock_path.return_value = [HexCoord(5, 5), HexCoord(10, 10)]
            handler.execute(mock_session, cmd)

            mock_validator.validate_stellerate_star.assert_called_once()
            call_kwargs = mock_validator.validate_stellerate_star.call_args.kwargs
            assert 'component_registry' in call_kwargs
            assert call_kwargs['component_registry'] == mock_component_registry

    def test_rejects_fleet_without_ability(self, mock_session):
        """Mission handler rejects fleet without DestroyStar ability."""
        from game.strategy.engine.superweapon_command_handlers import StellerateStarMissionCommandHandler
        from game.strategy.engine.commands import QueueStellerateStarMissionCommand

        cmd = QueueStellerateStarMissionCommand(fleet_id=1, target_hex=HexCoord(10, 10))
        handler = StellerateStarMissionCommandHandler()

        with patch('game.strategy.validation.superweapon_validator.SuperweaponValidator.find_ship_with_ability', return_value=None):
            result = handler.execute(mock_session, cmd)

        assert not result.is_valid
        assert "DestroyStar" in result.message


class TestOpenWarpPointMissionCommandHandlerValidates:
    """Tests that OpenWarpPointMissionCommandHandler calls validator."""

    def test_calls_validator_with_component_registry(self, mock_session, mock_component_registry):
        """Mission handler calls validator with component_registry."""
        from game.strategy.engine.superweapon_command_handlers import OpenWarpPointMissionCommandHandler
        from game.strategy.engine.commands import QueueOpenWarpPointMissionCommand

        cmd = QueueOpenWarpPointMissionCommand(
            fleet_id=1, target_hex=HexCoord(10, 10), target_system_name="Target System"
        )
        handler = OpenWarpPointMissionCommandHandler()

        with patch('game.strategy.engine.superweapon_command_handlers.SuperweaponValidator') as mock_validator, \
             patch('game.strategy.engine.command_handlers.find_hybrid_path') as mock_path:
            mock_validator.validate_open_warp_point.return_value = ValidationResult()
            mock_path.return_value = [HexCoord(5, 5), HexCoord(10, 10)]
            handler.execute(mock_session, cmd)

            mock_validator.validate_open_warp_point.assert_called_once()
            call_kwargs = mock_validator.validate_open_warp_point.call_args.kwargs
            assert 'component_registry' in call_kwargs
            assert call_kwargs['component_registry'] == mock_component_registry

    def test_rejects_fleet_without_ability(self, mock_session):
        """Mission handler rejects fleet without OpenWarpPoint ability."""
        from game.strategy.engine.superweapon_command_handlers import OpenWarpPointMissionCommandHandler
        from game.strategy.engine.commands import QueueOpenWarpPointMissionCommand

        cmd = QueueOpenWarpPointMissionCommand(
            fleet_id=1, target_hex=HexCoord(10, 10), target_system_name="Target System"
        )
        handler = OpenWarpPointMissionCommandHandler()

        with patch('game.strategy.validation.superweapon_validator.SuperweaponValidator.find_ship_with_ability', return_value=None):
            result = handler.execute(mock_session, cmd)

        assert not result.is_valid
        assert "OpenWarpPoint" in result.message


class TestCloseWarpPointMissionCommandHandlerValidates:
    """Tests that CloseWarpPointMissionCommandHandler calls validator."""

    def test_calls_validator_with_component_registry(self, mock_session, mock_component_registry):
        """Mission handler calls validator with component_registry."""
        from game.strategy.engine.superweapon_command_handlers import CloseWarpPointMissionCommandHandler
        from game.strategy.engine.commands import QueueCloseWarpPointMissionCommand

        cmd = QueueCloseWarpPointMissionCommand(
            fleet_id=1, target_hex=HexCoord(10, 10), warp_point_destination_id="Alpha Centauri"
        )
        handler = CloseWarpPointMissionCommandHandler()

        with patch('game.strategy.engine.superweapon_command_handlers.SuperweaponValidator') as mock_validator, \
             patch('game.strategy.engine.command_handlers.find_hybrid_path') as mock_path:
            mock_validator.validate_close_warp_point.return_value = ValidationResult()
            mock_path.return_value = [HexCoord(5, 5), HexCoord(10, 10)]
            handler.execute(mock_session, cmd)

            mock_validator.validate_close_warp_point.assert_called_once()
            call_kwargs = mock_validator.validate_close_warp_point.call_args.kwargs
            assert 'component_registry' in call_kwargs
            assert call_kwargs['component_registry'] == mock_component_registry

    def test_rejects_fleet_without_ability(self, mock_session):
        """Mission handler rejects fleet without CloseWarpPoint ability."""
        from game.strategy.engine.superweapon_command_handlers import CloseWarpPointMissionCommandHandler
        from game.strategy.engine.commands import QueueCloseWarpPointMissionCommand

        cmd = QueueCloseWarpPointMissionCommand(
            fleet_id=1, target_hex=HexCoord(10, 10), warp_point_destination_id="Alpha Centauri"
        )
        handler = CloseWarpPointMissionCommandHandler()

        with patch('game.strategy.validation.superweapon_validator.SuperweaponValidator.find_ship_with_ability', return_value=None):
            result = handler.execute(mock_session, cmd)

        assert not result.is_valid
        assert "CloseWarpPoint" in result.message


class TestCreateDysonSphereMissionCommandHandlerValidates:
    """Tests that CreateDysonSphereMissionCommandHandler calls validator."""

    def test_calls_validator_with_component_registry(self, mock_session, mock_component_registry):
        """Mission handler calls validator with component_registry."""
        from game.strategy.engine.superweapon_command_handlers import CreateDysonSphereMissionCommandHandler
        from game.strategy.engine.commands import QueueCreateDysonSphereMissionCommand

        cmd = QueueCreateDysonSphereMissionCommand(fleet_id=1, target_hex=HexCoord(10, 10))
        handler = CreateDysonSphereMissionCommandHandler()

        with patch('game.strategy.engine.superweapon_command_handlers.SuperweaponValidator') as mock_validator, \
             patch('game.strategy.engine.command_handlers.find_hybrid_path') as mock_path:
            mock_validator.validate_create_dyson_sphere.return_value = ValidationResult()
            mock_path.return_value = [HexCoord(5, 5), HexCoord(10, 10)]
            handler.execute(mock_session, cmd)

            mock_validator.validate_create_dyson_sphere.assert_called_once()
            call_kwargs = mock_validator.validate_create_dyson_sphere.call_args.kwargs
            assert 'component_registry' in call_kwargs
            assert call_kwargs['component_registry'] == mock_component_registry

    def test_rejects_fleet_without_ability(self, mock_session):
        """Mission handler rejects fleet without CreateDysonSphere ability."""
        from game.strategy.engine.superweapon_command_handlers import CreateDysonSphereMissionCommandHandler
        from game.strategy.engine.commands import QueueCreateDysonSphereMissionCommand

        cmd = QueueCreateDysonSphereMissionCommand(fleet_id=1, target_hex=HexCoord(10, 10))
        handler = CreateDysonSphereMissionCommandHandler()

        with patch('game.strategy.validation.superweapon_validator.SuperweaponValidator.find_ship_with_ability', return_value=None):
            result = handler.execute(mock_session, cmd)

        assert not result.is_valid
        assert "CreateDysonSphere" in result.message
