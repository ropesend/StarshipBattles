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
from game.strategy.data.order_types import Order, OrderType


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_fleet():
    """Create a mock fleet with basic attributes."""
    fleet = Mock()
    fleet.id = 1
    fleet.owner_id = 0
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
    # BUG-125: align active_empire with mock_fleet owner so authorization passes.
    session.active_empire = Mock(id=mock_fleet.owner_id)

    # Use public registries API
    registries = Mock()
    registries.components = mock_component_registry
    session.registries = registries

    return session


# =============================================================================
# Task 2.1: Direct Handlers Pass component_registry (VC-001)
# =============================================================================
# PROJ-323 Task 3.2: 5 near-identical direct-handler tests parametrized.


def _direct_handler_cases():
    from game.strategy.engine.superweapon_command_handlers import (
        ImplodePlanetCommandHandler,
        StellerateStarCommandHandler,
        OpenWarpPointCommandHandler,
        CloseWarpPointCommandHandler,
        CreateDysonSphereCommandHandler,
    )
    from game.strategy.engine.commands import (
        IssueImplodePlanetCommand,
        IssueStellerateStarCommand,
        IssueOpenWarpPointCommand,
        IssueCloseWarpPointCommand,
        IssueCreateDysonSphereCommand,
    )
    return [
        (
            ImplodePlanetCommandHandler,
            IssueImplodePlanetCommand(fleet_id=1, planet_id=100),
            'validate_implode_planet',
        ),
        (
            StellerateStarCommandHandler,
            IssueStellerateStarCommand(fleet_id=1),
            'validate_stellerate_star',
        ),
        (
            OpenWarpPointCommandHandler,
            IssueOpenWarpPointCommand(
                fleet_id=1, target_hex=HexCoord(10, 10), target_system_name="Target System",
            ),
            'validate_open_warp_point',
        ),
        (
            CloseWarpPointCommandHandler,
            IssueCloseWarpPointCommand(fleet_id=1, warp_point_destination_id="Alpha Centauri"),
            'validate_close_warp_point',
        ),
        (
            CreateDysonSphereCommandHandler,
            IssueCreateDysonSphereCommand(fleet_id=1),
            'validate_create_dyson_sphere',
        ),
    ]


@pytest.mark.parametrize(
    "handler_cls,cmd,validator_attr",
    [pytest.param(*case, id=case[0].__name__) for case in _direct_handler_cases()],
)
def test_direct_handler_passes_component_registry(
    mock_session, mock_component_registry, handler_cls, cmd, validator_attr,
):
    """All direct superweapon handlers pass component_registry to their validator."""
    handler = handler_cls()
    with patch('game.strategy.engine.superweapon_command_handlers.SuperweaponValidator') as mock_validator:
        getattr(mock_validator, validator_attr).return_value = ValidationResult()
        handler.execute(mock_session, cmd)

        call_kwargs = getattr(mock_validator, validator_attr).call_args.kwargs
        assert 'component_registry' in call_kwargs
        assert call_kwargs['component_registry'] == mock_component_registry



# =============================================================================
# Task 2.2: Mission Handlers Call Validators (VC-002/CP-005)
# =============================================================================
# PROJ-323 Task 3.2: 5 mission-handler tests collapsed into two parametrized
# tests (validates-with-registry and rejects-fleet-without-ability).


def _mission_handler_cases():
    from game.strategy.engine.superweapon_command_handlers import (
        ImplodePlanetMissionCommandHandler,
        StellerateStarMissionCommandHandler,
        OpenWarpPointMissionCommandHandler,
        CloseWarpPointMissionCommandHandler,
        CreateDysonSphereMissionCommandHandler,
    )
    from game.strategy.engine.commands import (
        QueueImplodePlanetMissionCommand,
        QueueStellerateStarMissionCommand,
        QueueOpenWarpPointMissionCommand,
        QueueCloseWarpPointMissionCommand,
        QueueCreateDysonSphereMissionCommand,
    )
    return [
        (
            ImplodePlanetMissionCommandHandler,
            QueueImplodePlanetMissionCommand(fleet_id=1, target_hex=HexCoord(10, 10), planet_id=100),
            'validate_implode_planet',
            'DestroyPlanet',
        ),
        (
            StellerateStarMissionCommandHandler,
            QueueStellerateStarMissionCommand(fleet_id=1, target_hex=HexCoord(10, 10)),
            'validate_stellerate_star',
            'DestroyStar',
        ),
        (
            OpenWarpPointMissionCommandHandler,
            QueueOpenWarpPointMissionCommand(
                fleet_id=1, target_hex=HexCoord(10, 10), target_system_name="Target System",
            ),
            'validate_open_warp_point',
            'OpenWarpPoint',
        ),
        (
            CloseWarpPointMissionCommandHandler,
            QueueCloseWarpPointMissionCommand(
                fleet_id=1, target_hex=HexCoord(10, 10), warp_point_destination_id="Alpha Centauri",
            ),
            'validate_close_warp_point',
            'CloseWarpPoint',
        ),
        (
            CreateDysonSphereMissionCommandHandler,
            QueueCreateDysonSphereMissionCommand(fleet_id=1, target_hex=HexCoord(10, 10)),
            'validate_create_dyson_sphere',
            'CreateDysonSphere',
        ),
    ]


@pytest.mark.parametrize(
    "handler_cls,cmd,validator_attr,ability_name",
    [pytest.param(*case, id=case[0].__name__) for case in _mission_handler_cases()],
)
def test_mission_handler_passes_component_registry(
    mock_session, mock_component_registry, handler_cls, cmd, validator_attr, ability_name,
):
    """All mission handlers call validator with component_registry."""
    handler = handler_cls()
    with patch('game.strategy.engine.superweapon_command_handlers.SuperweaponValidator') as mock_validator, \
         patch('game.strategy.services.galaxy_pathfinding_service.GalaxyPathfindingService.find_hybrid_path') as mock_path:
        getattr(mock_validator, validator_attr).return_value = ValidationResult()
        mock_path.return_value = [HexCoord(5, 5), HexCoord(10, 10)]
        handler.execute(mock_session, cmd)

        getattr(mock_validator, validator_attr).assert_called_once()
        call_kwargs = getattr(mock_validator, validator_attr).call_args.kwargs
        assert 'component_registry' in call_kwargs
        assert call_kwargs['component_registry'] == mock_component_registry


@pytest.mark.parametrize(
    "handler_cls,cmd,validator_attr,ability_name",
    [pytest.param(*case, id=case[0].__name__) for case in _mission_handler_cases()],
)
def test_mission_handler_rejects_fleet_without_ability(
    mock_session, handler_cls, cmd, validator_attr, ability_name,
):
    """All mission handlers reject when fleet lacks the relevant ability."""
    handler = handler_cls()
    with patch(
        'game.strategy.validation.superweapon_validator.SuperweaponValidator.find_ship_with_ability',
        return_value=None,
    ):
        result = handler.execute(mock_session, cmd)

    assert not result.is_valid
    assert ability_name in result.message
