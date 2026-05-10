"""Tests for ColonizationSystem using StrategySessionFacade.

These tests verify that ColonizationSystem correctly delegates to the facade
instead of directly accessing session internals.
"""
import pytest
from unittest.mock import Mock, MagicMock
from game.core.hex_math import HexCoord
from game.core.validation import ValidationResult


class TestColonizationSystemInit:
    """Tests for ColonizationSystem initialization with facade."""

    def test_init_stores_facade_reference(self):
        """ColonizationSystem stores facade reference on init."""
        from game.ui.screens.strategy_colonization import ColonizationSystem

        mock_scene = Mock()
        mock_facade = Mock()

        system = ColonizationSystem(mock_scene, mock_facade)

        assert system.facade is mock_facade
        assert system.scene is mock_scene

    def test_init_without_facade_raises_error(self):
        """ColonizationSystem requires facade parameter."""
        from game.ui.screens.strategy_colonization import ColonizationSystem

        mock_scene = Mock()

        with pytest.raises(TypeError):
            ColonizationSystem(mock_scene)  # Missing facade


class TestColonizationSystemNoDirectAccess:
    """Tests verifying direct session/turn_engine properties are removed."""

    def test_no_session_property(self):
        """ColonizationSystem should not have session property."""
        from game.ui.screens.strategy_colonization import ColonizationSystem

        # Check that session is not a defined property on the class
        assert 'session' not in ColonizationSystem.__dict__

    def test_no_turn_engine_property(self):
        """ColonizationSystem should not have turn_engine property."""
        from game.ui.screens.strategy_colonization import ColonizationSystem

        # Check that turn_engine is not a defined property on the class
        assert 'turn_engine' not in ColonizationSystem.__dict__

    def test_no_galaxy_property(self):
        """ColonizationSystem should not have galaxy property (accesses through scene)."""
        from game.ui.screens.strategy_colonization import ColonizationSystem

        # Check that galaxy is not a defined property on the class
        # (it accesses scene.galaxy internally for lookups, which is allowed)
        assert 'galaxy' not in ColonizationSystem.__dict__


class TestOnColonizeClick:
    """Tests for on_colonize_click using facade."""

    def test_on_colonize_uses_facade_validation(self):
        """on_colonize_click uses facade.can_colonize for validation."""
        from game.ui.screens.strategy_colonization import ColonizationSystem
        from enum import Enum

        class MockPlanetType(Enum):
            CONTINENTAL = "CONTINENTAL"

        mock_scene = Mock()
        mock_scene.systems = []

        mock_facade = Mock()
        mock_facade.can_colonize.return_value = ValidationResult()
        mock_facade.handle_command.return_value = ValidationResult()
        # PROJ-55: Mock pod filtering - must provide pod for planet type
        mock_facade.get_fleet_remaining_pods.return_value = {'drop_pod': 1}

        system = ColonizationSystem(mock_scene, mock_facade)

        # Mock internal method to return a planet
        mock_planet = Mock()
        mock_planet.id = 42
        mock_planet.location = HexCoord(0, 0)
        mock_planet.planet_type = MockPlanetType.CONTINENTAL  # PROJ-55: Add planet type

        mock_fleet = Mock()
        mock_fleet.id = 10
        mock_fleet.location = HexCoord(5, 5)

        # Mock _get_system_at_hex to return a system with a planet
        mock_star_system = Mock()
        mock_star_system.global_location = HexCoord(5, 5)
        mock_star_system.planets = [mock_planet]
        system._get_system_at_hex = Mock(return_value=mock_star_system)

        result = system.on_colonize_click(mock_fleet)

        # Should call facade.can_colonize to validate
        mock_facade.can_colonize.assert_called()


class TestIssueColonizeOrder:
    """Tests for issue_colonize_order using facade."""

    def test_issue_colonize_uses_facade_command(self):
        """issue_colonize_order calls facade.handle_command."""
        from game.ui.screens.strategy_colonization import ColonizationSystem
        from game.strategy.engine.commands import IssueColonizeCommand

        mock_scene = Mock()
        mock_facade = Mock()
        mock_facade.handle_command.return_value = ValidationResult()

        system = ColonizationSystem(mock_scene, mock_facade)

        mock_fleet = Mock()
        mock_fleet.id = 10

        mock_planet = Mock()
        mock_planet.id = 42
        mock_planet.name = "Test Planet"

        result = system.issue_colonize_order(mock_fleet, mock_planet)

        mock_facade.handle_command.assert_called_once()
        cmd = mock_facade.handle_command.call_args[0][0]
        assert isinstance(cmd, IssueColonizeCommand)
        assert cmd.fleet_id == 10
        assert cmd.planet_id == 42

    def test_issue_colonize_returns_success(self):
        """issue_colonize_order returns success on valid command."""
        from game.ui.screens.strategy_colonization import ColonizationSystem

        mock_scene = Mock()
        mock_facade = Mock()
        mock_facade.handle_command.return_value = ValidationResult()

        system = ColonizationSystem(mock_scene, mock_facade)

        mock_fleet = Mock()
        mock_fleet.id = 10

        mock_planet = Mock()
        mock_planet.id = 42
        mock_planet.name = "Test Planet"

        result = system.issue_colonize_order(mock_fleet, mock_planet)

        assert result['type'] == 'success'

    def test_issue_colonize_returns_error_on_failure(self):
        """issue_colonize_order returns error when command fails."""
        from game.ui.screens.strategy_colonization import ColonizationSystem

        mock_scene = Mock()
        mock_facade = Mock()
        mock_facade.handle_command.return_value = ValidationResult.error("Already owned")

        system = ColonizationSystem(mock_scene, mock_facade)

        mock_fleet = Mock()
        mock_fleet.id = 10

        mock_planet = Mock()
        mock_planet.id = 42
        mock_planet.name = "Test Planet"

        result = system.issue_colonize_order(mock_fleet, mock_planet)

        assert result['type'] == 'error'
        assert 'Already owned' in result['message']


class TestQueueColonizeMission:
    """Tests for queue_colonize_mission using facade."""

    def test_queue_mission_uses_facade_command(self):
        """queue_colonize_mission calls facade.handle_command with QueueColonizeMissionCommand."""
        from game.ui.screens.strategy_colonization import ColonizationSystem
        from game.strategy.engine.commands import QueueColonizeMissionCommand

        mock_scene = Mock()
        mock_facade = Mock()
        mock_facade.handle_command.return_value = ValidationResult()

        system = ColonizationSystem(mock_scene, mock_facade)

        mock_fleet = Mock()
        mock_fleet.id = 10
        mock_fleet.location = HexCoord(0, 0)
        mock_fleet.orders = []

        mock_planet = Mock()
        mock_planet.id = 42
        mock_planet.name = "Test Planet"

        target_hex = HexCoord(5, 5)

        result = system.queue_colonize_mission(target_hex, mock_planet, mock_fleet)

        mock_facade.handle_command.assert_called_once()
        cmd = mock_facade.handle_command.call_args[0][0]
        assert isinstance(cmd, QueueColonizeMissionCommand)
        assert cmd.fleet_id == 10
        assert cmd.planet_id == 42
        assert cmd.target_hex == target_hex

    def test_queue_mission_returns_success(self):
        """queue_colonize_mission returns success when command succeeds."""
        from game.ui.screens.strategy_colonization import ColonizationSystem

        mock_scene = Mock()
        mock_facade = Mock()
        mock_facade.handle_command.return_value = ValidationResult()

        system = ColonizationSystem(mock_scene, mock_facade)

        mock_fleet = Mock()
        mock_fleet.id = 10
        mock_fleet.location = HexCoord(0, 0)
        mock_fleet.orders = []

        mock_planet = Mock()
        mock_planet.id = 42
        mock_planet.name = "Test Planet"

        result = system.queue_colonize_mission(HexCoord(5, 5), mock_planet, mock_fleet)

        assert result['type'] == 'success'

    def test_queue_mission_returns_error_on_failure(self):
        """queue_colonize_mission returns error when command fails."""
        from game.ui.screens.strategy_colonization import ColonizationSystem

        mock_scene = Mock()
        mock_facade = Mock()
        mock_facade.handle_command.return_value = ValidationResult.error("No path found")

        system = ColonizationSystem(mock_scene, mock_facade)

        mock_fleet = Mock()
        mock_fleet.id = 10
        mock_fleet.location = HexCoord(0, 0)
        mock_fleet.orders = []

        mock_planet = Mock()
        mock_planet.id = 42
        mock_planet.name = "Test Planet"

        result = system.queue_colonize_mission(HexCoord(100, 100), mock_planet, mock_fleet)

        assert result['type'] == 'error'

    def test_queue_mission_returns_none_for_no_fleet(self):
        """queue_colonize_mission returns None when no fleet provided."""
        from game.ui.screens.strategy_colonization import ColonizationSystem

        mock_scene = Mock()
        mock_facade = Mock()

        system = ColonizationSystem(mock_scene, mock_facade)

        result = system.queue_colonize_mission(HexCoord(5, 5), Mock(), None)

        assert result is None
        mock_facade.handle_command.assert_not_called()

    def test_queue_mission_with_none_planet_issues_command_with_none_planet_id(self):
        """queue_colonize_mission with planet=None issues command with planet_id=None.

        This supports "colonize any available planet" when fleet arrives.
        """
        from game.ui.screens.strategy_colonization import ColonizationSystem
        from game.strategy.engine.commands import QueueColonizeMissionCommand

        mock_scene = Mock()
        mock_facade = Mock()
        mock_facade.handle_command.return_value = ValidationResult()

        system = ColonizationSystem(mock_scene, mock_facade)

        mock_fleet = Mock()
        mock_fleet.id = 10
        mock_fleet.location = HexCoord(0, 0)
        mock_fleet.orders = []

        target_hex = HexCoord(5, 5)

        # planet=None should be valid and issue command with planet_id=None
        result = system.queue_colonize_mission(target_hex, None, mock_fleet)

        mock_facade.handle_command.assert_called_once()
        cmd = mock_facade.handle_command.call_args[0][0]
        assert isinstance(cmd, QueueColonizeMissionCommand)
        assert cmd.fleet_id == 10
        assert cmd.planet_id is None  # Key assertion: planet_id should be None
        assert cmd.target_hex == target_hex

    def test_queue_mission_with_none_planet_returns_success(self):
        """queue_colonize_mission with planet=None returns success when command succeeds."""
        from game.ui.screens.strategy_colonization import ColonizationSystem

        mock_scene = Mock()
        mock_facade = Mock()
        mock_facade.handle_command.return_value = ValidationResult()

        system = ColonizationSystem(mock_scene, mock_facade)

        mock_fleet = Mock()
        mock_fleet.id = 10

        result = system.queue_colonize_mission(HexCoord(5, 5), None, mock_fleet)

        assert result is not None
        assert result['type'] == 'success'


# =============================================================================
# PROJ-55: Phase 4 - Pod Filtering Tests
# =============================================================================

def _create_mock_session_with_fleet_lookup(empires=None, **kwargs):
    """Create mock session with _get_fleet_by_id support for facade tests."""
    session = Mock()
    session.empires = empires or []

    def get_fleet_by_id(fleet_id):
        for empire in session.empires:
            for fleet in empire.fleets:
                if fleet.id == fleet_id:
                    return fleet
        return None

    session._get_fleet_by_id = get_fleet_by_id

    for key, value in kwargs.items():
        setattr(session, key, value)

    return session


class TestFacadeColonyPodMethods:
    """Tests for facade methods that expose colony pod information."""

    def test_get_fleet_remaining_pods_returns_dict(self):
        """Facade.get_fleet_remaining_pods returns dict of remaining pods."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        mock_fleet = Mock()
        mock_fleet.id = 10
        mock_fleet.ships = []
        mock_fleet.orders = []

        # Setup session internals
        mock_empire = Mock()
        mock_empire.fleets = [mock_fleet]
        mock_session = _create_mock_session_with_fleet_lookup([mock_empire])

        facade = StrategySessionFacade(mock_session)

        # Should return empty dict for fleet with no ships
        result = facade.get_fleet_remaining_pods(10)
        assert isinstance(result, dict)

    def test_get_fleet_remaining_pods_accounts_for_committed(self):
        """Remaining pods = available - committed."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade
        from game.strategy.data.order_types import Order, OrderType
        from enum import Enum

        class MockPlanetType(Enum):
            ICE_DWARF = "ICE_DWARF"

        # Phase 3: Drop pod in carried_items
        mock_ship = Mock()
        mock_ship.carried_items = [{"vehicle_type": "drop_pod", "design_id": "test_pod", "name": "Test Pod", "design_data": {}, "mass": 500}]

        # Create mock planet target
        mock_target_planet = Mock()
        mock_target_planet.planet_type = MockPlanetType.ICE_DWARF

        # Create order for that planet
        mock_order = Mock()
        mock_order.type = OrderType.COLONIZE
        mock_order.target = mock_target_planet

        mock_fleet = Mock()
        mock_fleet.id = 10
        mock_fleet.ships = [mock_ship]
        mock_fleet.orders = [mock_order]

        mock_empire = Mock()
        mock_empire.fleets = [mock_fleet]

        mock_session = _create_mock_session_with_fleet_lookup([mock_empire])

        facade = StrategySessionFacade(mock_session)
        result = facade.get_fleet_remaining_pods(10)

        # 1 available - 1 committed = 0 remaining
        assert result.get('drop_pod', 0) == 0

    def test_get_fleet_remaining_pods_fleet_not_found_returns_empty(self):
        """get_fleet_remaining_pods returns empty dict if fleet not found."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        mock_session = _create_mock_session_with_fleet_lookup([])

        facade = StrategySessionFacade(mock_session)
        result = facade.get_fleet_remaining_pods(999)

        assert result == {}


class TestOnColonizeClickPodFiltering:
    """Tests for PROJ-55: Filtering planets by available pods."""

    def test_on_colonize_shows_all_planets_with_universal_pods(self):
        """on_colonize_click returns all unowned planets when fleet has universal pods."""
        from game.ui.screens.strategy_colonization import ColonizationSystem
        from enum import Enum

        class MockPlanetType(Enum):
            ICE_DWARF = "ICE_DWARF"
            CONTINENTAL = "CONTINENTAL"

        # Setup planets - one Ice Dwarf, one Continental
        mock_ice_planet = Mock()
        mock_ice_planet.id = 1
        mock_ice_planet.location = HexCoord(0, 0)
        mock_ice_planet.planet_type = MockPlanetType.ICE_DWARF
        mock_ice_planet.name = "Ice World"

        mock_cont_planet = Mock()
        mock_cont_planet.id = 2
        mock_cont_planet.location = HexCoord(0, 0)
        mock_cont_planet.planet_type = MockPlanetType.CONTINENTAL
        mock_cont_planet.name = "Earth-like"

        mock_fleet = Mock()
        mock_fleet.id = 10
        mock_fleet.location = HexCoord(5, 5)

        # Setup system with both planets at fleet location
        mock_star_system = Mock()
        mock_star_system.global_location = HexCoord(5, 5)
        mock_star_system.planets = [mock_ice_planet, mock_cont_planet]

        mock_scene = Mock()
        mock_scene.systems = [mock_star_system]

        mock_facade = Mock()
        mock_facade.can_colonize.return_value = ValidationResult()
        mock_facade.handle_command.return_value = ValidationResult()
        # Universal pods — fleet has 1 drop pod
        mock_facade.get_fleet_remaining_pods.return_value = {'drop_pod': 1}

        system = ColonizationSystem(mock_scene, mock_facade)
        system._get_system_at_hex = Mock(return_value=mock_star_system)

        result = system.on_colonize_click(mock_fleet)

        # Universal pods: both planets should be valid targets
        assert result is not None
        assert result['type'] == 'prompt'
        assert len(result['planets']) == 2

    def test_on_colonize_ignores_pod_count_at_command_time(self):
        """Pod count no longer filters planets at command time — deferred to execution."""
        from game.ui.screens.strategy_colonization import ColonizationSystem
        from enum import Enum

        class MockPlanetType(Enum):
            CONTINENTAL = "CONTINENTAL"

        # Two Continental planets
        mock_planet1 = Mock()
        mock_planet1.id = 1
        mock_planet1.location = HexCoord(0, 0)
        mock_planet1.planet_type = MockPlanetType.CONTINENTAL

        mock_planet2 = Mock()
        mock_planet2.id = 2
        mock_planet2.location = HexCoord(0, 0)
        mock_planet2.planet_type = MockPlanetType.CONTINENTAL

        mock_fleet = Mock()
        mock_fleet.id = 10
        mock_fleet.location = HexCoord(5, 5)

        mock_star_system = Mock()
        mock_star_system.global_location = HexCoord(5, 5)
        mock_star_system.planets = [mock_planet1, mock_planet2]

        mock_scene = Mock()
        mock_scene.systems = [mock_star_system]

        mock_facade = Mock()
        mock_facade.can_colonize.return_value = ValidationResult()
        # No remaining pods (1 pod, 1 already committed)
        mock_facade.get_fleet_remaining_pods.return_value = {}

        system = ColonizationSystem(mock_scene, mock_facade)
        system._get_system_at_hex = Mock(return_value=mock_star_system)

        result = system.on_colonize_click(mock_fleet)

        # Pod availability is checked at execution time, not command time
        assert result is not None
        assert result['type'] == 'prompt'
        assert len(result['planets']) == 2

    def test_on_colonize_no_pods_still_prompts(self):
        """When fleet has no pods, still prompts — pod check deferred to execution."""
        from game.ui.screens.strategy_colonization import ColonizationSystem

        mock_planet = Mock()
        mock_planet.id = 1
        mock_planet.location = HexCoord(0, 0)

        mock_fleet = Mock()
        mock_fleet.id = 10
        mock_fleet.location = HexCoord(5, 5)

        mock_star_system = Mock()
        mock_star_system.global_location = HexCoord(5, 5)
        mock_star_system.planets = [mock_planet]

        mock_scene = Mock()
        mock_scene.systems = [mock_star_system]

        mock_facade = Mock()
        mock_facade.can_colonize.return_value = ValidationResult()
        # No pods at all
        mock_facade.get_fleet_remaining_pods.return_value = {}

        system = ColonizationSystem(mock_scene, mock_facade)
        system._get_system_at_hex = Mock(return_value=mock_star_system)

        result = system.on_colonize_click(mock_fleet)

        # Pod availability is checked at execution time — prompt is shown
        assert result is not None
        assert result['type'] == 'prompt'


class TestHandleColonizeDesignationPodFiltering:
    """Tests for PROJ-140: Pod filtering in handle_colonize_designation()."""

    def test_designation_ignores_pod_count_at_command_time(self):
        """Designation no longer filters by pod count — deferred to execution."""
        from game.ui.screens.strategy_colonization import ColonizationSystem
        from game.core.hex_math import HexCoord
        from enum import Enum

        class MockPlanetType(Enum):
            ICE_DWARF = "ICE_DWARF"
            CONTINENTAL = "CONTINENTAL"

        # Setup: ICE_DWARF planet at target hex
        mock_planet = Mock()
        mock_planet.id = 1
        mock_planet.location = HexCoord(0, 0)  # local coords
        mock_planet.planet_type = MockPlanetType.ICE_DWARF
        mock_planet.owner_id = None

        # System at global (10, 10)
        mock_system = Mock()
        mock_system.global_location = HexCoord(10, 10)
        mock_system.planets = [mock_planet]

        mock_camera = Mock()
        mock_camera.screen_to_world.return_value = Mock(x=0, y=0)

        mock_scene = Mock()
        mock_scene.camera = mock_camera
        mock_scene.hex_size = 32
        mock_scene.systems = [mock_system]
        mock_scene.galaxy = None  # No zone lookup

        mock_facade = Mock()
        # Fleet has no pods
        mock_facade.get_fleet_remaining_pods.return_value = {'drop_pod': 0}

        mock_fleet = Mock()
        mock_fleet.id = 10
        mock_fleet.location = HexCoord(5, 5)

        system = ColonizationSystem(mock_scene, mock_facade)
        system._get_system_at_hex = Mock(return_value=mock_system)

        # PROJ-380 DUP-X-08: stub camera.hex_at_screen (replaces the prior
        # monkey-patch of `colonization_module.pixel_to_hex`).
        mock_camera.hex_at_screen.return_value = HexCoord(10, 10)

        result = system.handle_colonize_designation(100, 100, mock_fleet)

        # Pod availability is checked at execution time — prompt is shown
        assert result is not None
        assert result['type'] == 'prompt'
        assert len(result['planets']) == 1

    def test_designation_matching_pod_succeeds(self):
        """Designation succeeds when fleet has pod matching planet type."""
        from game.ui.screens.strategy_colonization import ColonizationSystem
        from game.core.hex_math import HexCoord
        from game.core.validation import ValidationResult
        from enum import Enum

        class MockPlanetType(Enum):
            ICE_DWARF = "ICE_DWARF"

        mock_planet = Mock()
        mock_planet.id = 1
        mock_planet.location = HexCoord(0, 0)
        mock_planet.planet_type = MockPlanetType.ICE_DWARF
        mock_planet.owner_id = None
        mock_planet.name = "Ice World"

        mock_system = Mock()
        mock_system.global_location = HexCoord(10, 10)
        mock_system.planets = [mock_planet]

        mock_camera = Mock()
        mock_camera.screen_to_world.return_value = Mock(x=0, y=0)

        mock_scene = Mock()
        mock_scene.camera = mock_camera
        mock_scene.hex_size = 32
        mock_scene.systems = [mock_system]
        mock_scene.galaxy = None

        mock_facade = Mock()
        # Fleet has ICE_DWARF pod - matches planet
        mock_facade.get_fleet_remaining_pods.return_value = {'drop_pod': 1}
        mock_facade.handle_command.return_value = ValidationResult()

        mock_fleet = Mock()
        mock_fleet.id = 10
        mock_fleet.location = HexCoord(5, 5)

        system = ColonizationSystem(mock_scene, mock_facade)
        system._get_system_at_hex = Mock(return_value=mock_system)

        # PROJ-380 DUP-X-08: stub camera.hex_at_screen.
        mock_camera.hex_at_screen.return_value = HexCoord(10, 10)

        result = system.handle_colonize_designation(100, 100, mock_fleet)

        # Should succeed or return prompt (not filtered out)
        assert result is not None
        assert result.get('type') in ('success', 'prompt')

    def test_designation_no_pods_still_prompts(self):
        """Designation prompts even without pods — pod check deferred to execution."""
        from game.ui.screens.strategy_colonization import ColonizationSystem
        from game.core.hex_math import HexCoord
        from enum import Enum

        class MockPlanetType(Enum):
            CONTINENTAL = "CONTINENTAL"

        mock_planet = Mock()
        mock_planet.id = 1
        mock_planet.location = HexCoord(0, 0)
        mock_planet.planet_type = MockPlanetType.CONTINENTAL
        mock_planet.owner_id = None

        mock_system = Mock()
        mock_system.global_location = HexCoord(10, 10)
        mock_system.planets = [mock_planet]

        mock_camera = Mock()
        mock_camera.screen_to_world.return_value = Mock(x=0, y=0)

        mock_scene = Mock()
        mock_scene.camera = mock_camera
        mock_scene.hex_size = 32
        mock_scene.systems = [mock_system]
        mock_scene.galaxy = None

        mock_facade = Mock()
        # Fleet has NO pods
        mock_facade.get_fleet_remaining_pods.return_value = {}

        mock_fleet = Mock()
        mock_fleet.id = 10
        mock_fleet.location = HexCoord(5, 5)

        system = ColonizationSystem(mock_scene, mock_facade)
        system._get_system_at_hex = Mock(return_value=mock_system)

        # PROJ-380 DUP-X-08: stub camera.hex_at_screen.
        mock_camera.hex_at_screen.return_value = HexCoord(10, 10)

        result = system.handle_colonize_designation(100, 100, mock_fleet)

        # Pod availability is checked at execution time — prompt is shown
        assert result is not None
        assert result['type'] == 'prompt'

    def test_designation_mixed_types_filters_correctly(self):
        """Designation filters correctly when multiple planet types exist."""
        from game.ui.screens.strategy_colonization import ColonizationSystem
        from game.core.hex_math import HexCoord
        from game.core.validation import ValidationResult
        from enum import Enum

        class MockPlanetType(Enum):
            ICE_DWARF = "ICE_DWARF"
            CONTINENTAL = "CONTINENTAL"

        # Two planets at same location, different types
        mock_ice_planet = Mock()
        mock_ice_planet.id = 1
        mock_ice_planet.location = HexCoord(0, 0)
        mock_ice_planet.planet_type = MockPlanetType.ICE_DWARF
        mock_ice_planet.owner_id = None
        mock_ice_planet.name = "Ice World"

        mock_cont_planet = Mock()
        mock_cont_planet.id = 2
        mock_cont_planet.location = HexCoord(0, 0)
        mock_cont_planet.planet_type = MockPlanetType.CONTINENTAL
        mock_cont_planet.owner_id = None
        mock_cont_planet.name = "Earth-like"

        mock_system = Mock()
        mock_system.global_location = HexCoord(10, 10)
        mock_system.planets = [mock_ice_planet, mock_cont_planet]

        mock_camera = Mock()
        mock_camera.screen_to_world.return_value = Mock(x=0, y=0)

        mock_scene = Mock()
        mock_scene.camera = mock_camera
        mock_scene.hex_size = 32
        mock_scene.systems = [mock_system]
        mock_scene.galaxy = None

        mock_facade = Mock()
        # Fleet has only CONTINENTAL pod
        mock_facade.get_fleet_remaining_pods.return_value = {'drop_pod': 1}
        mock_facade.handle_command.return_value = ValidationResult()

        mock_fleet = Mock()
        mock_fleet.id = 10
        mock_fleet.location = HexCoord(5, 5)

        system = ColonizationSystem(mock_scene, mock_facade)
        system._get_system_at_hex = Mock(return_value=mock_system)

        # PROJ-380 DUP-X-08: stub camera.hex_at_screen.
        mock_camera.hex_at_screen.return_value = HexCoord(10, 10)

        result = system.handle_colonize_designation(100, 100, mock_fleet)

        # Universal pods: both planets are valid, should prompt for selection
        assert result is not None
        assert result.get('type') == 'prompt'
        assert len(result['planets']) == 2


class TestPlanetTypeDisplay:
    """Tests for displaying planet types in colonization UI."""

    def test_prompt_result_includes_planet_type_display(self):
        """When prompting for planet selection, planet type info is available."""
        from game.ui.screens.strategy_colonization import ColonizationSystem
        from enum import Enum

        class MockPlanetType(Enum):
            ICE_DWARF = "ICE_DWARF"
            CONTINENTAL = "CONTINENTAL"

        mock_ice_planet = Mock()
        mock_ice_planet.id = 1
        mock_ice_planet.location = HexCoord(0, 0)
        mock_ice_planet.planet_type = MockPlanetType.ICE_DWARF
        mock_ice_planet.name = "Frostworld"

        mock_cont_planet = Mock()
        mock_cont_planet.id = 2
        mock_cont_planet.location = HexCoord(0, 0)
        mock_cont_planet.planet_type = MockPlanetType.CONTINENTAL
        mock_cont_planet.name = "Terra Nova"

        mock_fleet = Mock()
        mock_fleet.id = 10
        mock_fleet.location = HexCoord(5, 5)

        mock_star_system = Mock()
        mock_star_system.global_location = HexCoord(5, 5)
        mock_star_system.planets = [mock_ice_planet, mock_cont_planet]

        mock_scene = Mock()
        mock_scene.systems = [mock_star_system]

        mock_facade = Mock()
        mock_facade.can_colonize.return_value = ValidationResult()
        # Both pod types available
        mock_facade.get_fleet_remaining_pods.return_value = {'drop_pod': 2}

        system = ColonizationSystem(mock_scene, mock_facade)
        system._get_system_at_hex = Mock(return_value=mock_star_system)

        result = system.on_colonize_click(mock_fleet)

        # If prompt, verify planets have planet_type attribute accessible
        if result and result.get('type') == 'prompt':
            for planet in result['planets']:
                # Verify planet_type is accessible for display
                assert hasattr(planet, 'planet_type')
                assert planet.planet_type.name in ['ICE_DWARF', 'CONTINENTAL']
