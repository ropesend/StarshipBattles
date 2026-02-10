"""Tests for ColonizationSystem using StrategySessionFacade.

These tests verify that ColonizationSystem correctly delegates to the facade
instead of directly accessing session internals.
"""
import pytest
from unittest.mock import Mock, MagicMock
from game.core.hex_math import HexCoord
from game.core.validation import validation_result


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
        mock_facade.can_colonize.return_value = validation_result(True, "OK")
        mock_facade.handle_command.return_value = validation_result(True, "OK")
        # PROJ-55: Mock pod filtering - must provide pod for planet type
        mock_facade.get_fleet_remaining_pods.return_value = {'CONTINENTAL': 1}

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
        mock_facade.handle_command.return_value = validation_result(True, "OK")

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
        mock_facade.handle_command.return_value = validation_result(True, "OK")

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
        mock_facade.handle_command.return_value = validation_result(False, "Already owned")

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
        mock_facade.handle_command.return_value = validation_result(True, "OK")

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
        mock_facade.handle_command.return_value = validation_result(True, "OK")

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
        mock_facade.handle_command.return_value = validation_result(False, "No path found")

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
        mock_facade.handle_command.return_value = validation_result(True, "OK")

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
        mock_facade.handle_command.return_value = validation_result(True, "OK")

        system = ColonizationSystem(mock_scene, mock_facade)

        mock_fleet = Mock()
        mock_fleet.id = 10

        result = system.queue_colonize_mission(HexCoord(5, 5), None, mock_fleet)

        assert result is not None
        assert result['type'] == 'success'


# =============================================================================
# PROJ-55: Phase 4 - Pod Filtering Tests
# =============================================================================

class TestFacadeColonyPodMethods:
    """Tests for facade methods that expose colony pod information."""

    def test_get_fleet_remaining_pods_returns_dict(self):
        """Facade.get_fleet_remaining_pods returns dict of remaining pods."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        mock_session = Mock()
        mock_fleet = Mock()
        mock_fleet.id = 10
        mock_fleet.ships = []
        mock_fleet.orders = []

        # Setup session internals
        mock_empire = Mock()
        mock_empire.fleets = [mock_fleet]
        mock_session.empires = [mock_empire]

        facade = StrategySessionFacade(mock_session)

        # Should return empty dict for fleet with no ships
        result = facade.get_fleet_remaining_pods(10)
        assert isinstance(result, dict)

    def test_get_fleet_remaining_pods_accounts_for_committed(self):
        """Remaining pods = available - committed."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade
        from game.strategy.data.fleet import FleetOrder, OrderType
        from enum import Enum

        class MockPlanetType(Enum):
            ICE_DWARF = "ICE_DWARF"

        mock_session = Mock()

        # Create mock ship with ice dwarf pod
        mock_ship = Mock()
        mock_ship.design_data = {
            'layers': {'HULL': [{'id': 'ice_dwarf_colony_pod'}]}
        }

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
        mock_session.empires = [mock_empire]

        # Need to provide component registry
        mock_registries = Mock()
        mock_registries.components = {
            'ice_dwarf_colony_pod': {
                'id': 'ice_dwarf_colony_pod',
                'abilities': {'ColonizePlanet': 'ICE_DWARF'}
            }
        }
        mock_session.registries = mock_registries

        facade = StrategySessionFacade(mock_session)
        result = facade.get_fleet_remaining_pods(10)

        # 1 available - 1 committed = 0 remaining
        assert result.get('ICE_DWARF', 0) == 0

    def test_get_fleet_remaining_pods_fleet_not_found_returns_empty(self):
        """get_fleet_remaining_pods returns empty dict if fleet not found."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        mock_session = Mock()
        mock_session.empires = []

        facade = StrategySessionFacade(mock_session)
        result = facade.get_fleet_remaining_pods(999)

        assert result == {}


class TestOnColonizeClickPodFiltering:
    """Tests for PROJ-55: Filtering planets by available pods."""

    def test_on_colonize_filters_by_available_pods(self):
        """on_colonize_click only returns planets with matching pods."""
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

        # Fleet only has Continental pod
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
        # Facade says both are valid (base validation passes)
        mock_facade.can_colonize.return_value = validation_result(True, "OK")
        mock_facade.handle_command.return_value = validation_result(True, "OK")
        # But remaining pods only has Continental
        mock_facade.get_fleet_remaining_pods.return_value = {'CONTINENTAL': 1}

        system = ColonizationSystem(mock_scene, mock_facade)
        system._get_system_at_hex = Mock(return_value=mock_star_system)

        result = system.on_colonize_click(mock_fleet)

        # Should return prompt with only Continental planet (Ice Dwarf filtered out)
        if result['type'] == 'prompt':
            assert len(result['planets']) == 1
            assert result['planets'][0].planet_type == MockPlanetType.CONTINENTAL
        elif result['type'] == 'success':
            # If only one valid, it auto-colonizes
            pass

    def test_on_colonize_accounts_for_committed_orders(self):
        """Committed orders reduce available pods for filtering."""
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
        mock_facade.can_colonize.return_value = validation_result(True, "OK")
        # No remaining pods (1 pod, 1 already committed)
        mock_facade.get_fleet_remaining_pods.return_value = {}

        system = ColonizationSystem(mock_scene, mock_facade)
        system._get_system_at_hex = Mock(return_value=mock_star_system)

        result = system.on_colonize_click(mock_fleet)

        # No valid targets because pod is committed
        assert result is None or result.get('type') == 'no_targets'

    def test_on_colonize_no_pods_returns_informative_message(self):
        """When fleet has no pods, return informative message."""
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
        mock_facade.can_colonize.return_value = validation_result(True, "OK")
        # No pods at all
        mock_facade.get_fleet_remaining_pods.return_value = {}

        system = ColonizationSystem(mock_scene, mock_facade)
        system._get_system_at_hex = Mock(return_value=mock_star_system)

        result = system.on_colonize_click(mock_fleet)

        # Should indicate no valid targets
        assert result is None or result.get('type') == 'no_targets'


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
        mock_facade.can_colonize.return_value = validation_result(True, "OK")
        # Both pod types available
        mock_facade.get_fleet_remaining_pods.return_value = {
            'ICE_DWARF': 1, 'CONTINENTAL': 1
        }

        system = ColonizationSystem(mock_scene, mock_facade)
        system._get_system_at_hex = Mock(return_value=mock_star_system)

        result = system.on_colonize_click(mock_fleet)

        # If prompt, verify planets have planet_type attribute accessible
        if result and result.get('type') == 'prompt':
            for planet in result['planets']:
                # Verify planet_type is accessible for display
                assert hasattr(planet, 'planet_type')
                assert planet.planet_type.name in ['ICE_DWARF', 'CONTINENTAL']
