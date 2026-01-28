"""Tests for ColonizationSystem using StrategySessionFacade.

These tests verify that ColonizationSystem correctly delegates to the facade
instead of directly accessing session internals.
"""
import pytest
from unittest.mock import Mock, MagicMock
from game.strategy.data.hex_math import HexCoord
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

        mock_scene = Mock()
        mock_scene.systems = []

        mock_facade = Mock()
        mock_facade.can_colonize.return_value = validation_result(True, "OK")
        mock_facade.handle_command.return_value = validation_result(True, "OK")

        system = ColonizationSystem(mock_scene, mock_facade)

        # Mock internal method to return a planet
        mock_planet = Mock()
        mock_planet.id = 42
        mock_planet.location = HexCoord(0, 0)

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
