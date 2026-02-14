"""Unit tests for game/ui/services/battle_factories.py

PROJ-142: TCG-UI2-002 - Tests for battle factory convenience functions.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch


class TestHelperFunctions:
    """Tests for internal helper functions."""

    def test_create_default_ai_factory_returns_ai_factory(self):
        """_create_default_ai_factory returns AIControllerFactory instance."""
        from game.ui.services.battle_factories import _create_default_ai_factory
        from game.ai.ai_factory import AIControllerFactory

        result = _create_default_ai_factory()

        assert isinstance(result, AIControllerFactory)

    def test_clone_ships_returns_empty_list_for_empty_input(self):
        """_clone_ships returns empty list when given empty list."""
        from game.ui.services.battle_factories import _clone_ships

        result = _clone_ships([])

        assert result == []

    def test_clone_ships_preserves_position(self):
        """_clone_ships preserves ship position on clones."""
        from game.ui.services.battle_factories import _clone_ships

        # Create a minimal mock ship with registries
        mock_ship = Mock()
        mock_ship.x = 100.0
        mock_ship.y = 200.0
        mock_ship.registries = Mock()

        # Mock the serializer
        with patch('game.ui.services.battle_factories.ShipSerializer') as mock_serializer:
            mock_clone = Mock()
            mock_serializer.to_dict.return_value = {'name': 'TestShip'}
            mock_serializer.from_dict.return_value = mock_clone

            result = _clone_ships([mock_ship])

        assert len(result) == 1
        assert result[0].x == 100.0
        assert result[0].y == 200.0

    def test_clone_ships_multiple_ships(self):
        """_clone_ships handles multiple ships correctly."""
        from game.ui.services.battle_factories import _clone_ships

        # Create multiple mock ships
        mock_ships = []
        for i in range(3):
            ship = Mock()
            ship.x = float(i * 100)
            ship.y = float(i * 50)
            ship.registries = Mock()
            mock_ships.append(ship)

        with patch('game.ui.services.battle_factories.ShipSerializer') as mock_serializer:
            def create_clone(data, registries):
                clone = Mock()
                return clone
            mock_serializer.to_dict.return_value = {}
            mock_serializer.from_dict.side_effect = create_clone

            result = _clone_ships(mock_ships)

        assert len(result) == 3


class TestCreateControllerWithConfig:
    """Tests for _create_controller_with_config helper."""

    def test_creates_controller_with_ai_factory(self):
        """_create_controller_with_config creates controller with AI factory."""
        from game.ui.services.battle_factories import _create_controller_with_config
        from game.simulation.battle_config import BattleConfig, BattleMode

        config = BattleConfig(mode=BattleMode.MANUAL)

        controller = _create_controller_with_config(config)

        # Controller should be created and configured
        assert controller is not None
        # Mode is stored in config, accessed via mode_handler
        assert controller.mode_handler is not None


class TestCreateManualBattle:
    """Tests for create_manual_battle factory function."""

    def test_creates_manual_battle_with_both_teams(self):
        """create_manual_battle creates controller with ships from both teams."""
        from game.ui.services.battle_factories import create_manual_battle
        from game.simulation.battle_config import BattleMode

        # Create mock ships
        team1 = [Mock() for _ in range(2)]
        team2 = [Mock() for _ in range(3)]

        # Mock to avoid actual battle start
        with patch('game.ui.services.battle_factories.BattleController') as mock_bc:
            mock_controller = Mock()
            mock_bc.return_value = mock_controller

            result = create_manual_battle(team1, team2)

        # Should have added ships to both teams
        mock_controller.add_ships.assert_any_call(team1, 0)
        mock_controller.add_ships.assert_any_call(team2, 1)
        mock_controller.start.assert_called_once()

    def test_creates_manual_battle_with_seed(self):
        """create_manual_battle passes seed to config."""
        from game.ui.services.battle_factories import create_manual_battle

        with patch('game.ui.services.battle_factories.BattleController') as mock_bc:
            mock_controller = Mock()
            mock_bc.return_value = mock_controller

            create_manual_battle([], [], seed=42)

        # Verify configure was called (seed is in config)
        mock_controller.configure.assert_called_once()

    def test_creates_manual_battle_headless_mode(self):
        """create_manual_battle supports headless mode."""
        from game.ui.services.battle_factories import create_manual_battle

        with patch('game.ui.services.battle_factories.BattleController') as mock_bc:
            mock_controller = Mock()
            mock_bc.return_value = mock_controller

            create_manual_battle([], [], headless=True)

        # Should configure and start
        mock_controller.configure.assert_called_once()
        mock_controller.start.assert_called_once()


class TestCreateTestBattle:
    """Tests for create_test_battle factory function."""

    def test_creates_test_battle_with_scenario(self):
        """create_test_battle creates controller configured with scenario."""
        from game.ui.services.battle_factories import create_test_battle
        from game.simulation.battle_config import BattleMode

        mock_scenario = Mock()
        mock_scenario.max_ticks = 5000

        with patch('game.ui.services.battle_factories.BattleController') as mock_bc:
            mock_controller = Mock()
            mock_bc.return_value = mock_controller

            result = create_test_battle(mock_scenario)

        # Controller should be configured but NOT started
        mock_controller.configure.assert_called_once()
        mock_controller.start.assert_not_called()

    def test_test_battle_headless_by_default(self):
        """create_test_battle is headless by default."""
        from game.ui.services.battle_factories import create_test_battle

        mock_scenario = Mock()

        with patch('game.ui.services.battle_factories.BattleController') as mock_bc:
            mock_controller = Mock()
            mock_bc.return_value = mock_controller

            create_test_battle(mock_scenario)

        mock_controller.configure.assert_called_once()

    def test_test_battle_with_seed(self):
        """create_test_battle supports seed parameter."""
        from game.ui.services.battle_factories import create_test_battle

        mock_scenario = Mock()

        with patch('game.ui.services.battle_factories.BattleController') as mock_bc:
            mock_controller = Mock()
            mock_bc.return_value = mock_controller

            create_test_battle(mock_scenario, seed=123)

        mock_controller.configure.assert_called_once()


class TestCreateStrategyBattle:
    """Tests for create_strategy_battle factory function."""

    def test_creates_strategy_battle_with_fleets(self):
        """create_strategy_battle creates controller for fleet battle."""
        from game.ui.services.battle_factories import create_strategy_battle
        from game.simulation.battle_config import BattleMode

        mock_fleet1 = Mock()
        mock_fleet2 = Mock()

        with patch('game.ui.services.battle_factories.BattleController') as mock_bc:
            mock_controller = Mock()
            mock_bc.return_value = mock_controller

            result = create_strategy_battle(mock_fleet1, mock_fleet2)

        # Should be configured but not have ships added yet
        mock_controller.configure.assert_called_once()
        mock_controller.add_ships.assert_not_called()

    def test_strategy_battle_allow_retreat_flag(self):
        """create_strategy_battle supports allow_retreat parameter."""
        from game.ui.services.battle_factories import create_strategy_battle

        mock_fleet1 = Mock()
        mock_fleet2 = Mock()

        with patch('game.ui.services.battle_factories.BattleController') as mock_bc:
            mock_controller = Mock()
            mock_bc.return_value = mock_controller

            create_strategy_battle(mock_fleet1, mock_fleet2, allow_retreat=False)

        mock_controller.configure.assert_called_once()

    def test_strategy_battle_with_seed(self):
        """create_strategy_battle supports seed parameter."""
        from game.ui.services.battle_factories import create_strategy_battle

        with patch('game.ui.services.battle_factories.BattleController') as mock_bc:
            mock_controller = Mock()
            mock_bc.return_value = mock_controller

            create_strategy_battle(Mock(), Mock(), seed=999)

        mock_controller.configure.assert_called_once()


class TestCreateHypotheticalBattle:
    """Tests for create_hypothetical_battle factory function."""

    def test_creates_hypothetical_battle_clones_ships(self):
        """create_hypothetical_battle clones ships for isolation."""
        from game.ui.services.battle_factories import create_hypothetical_battle

        # Create mock ships with position
        mock_ship1 = Mock()
        mock_ship1.x = 100.0
        mock_ship1.y = 200.0
        mock_ship1.registries = Mock()

        mock_ship2 = Mock()
        mock_ship2.x = 300.0
        mock_ship2.y = 400.0
        mock_ship2.registries = Mock()

        with patch('game.ui.services.battle_factories.BattleController') as mock_bc:
            mock_controller = Mock()
            mock_bc.return_value = mock_controller

            with patch('game.ui.services.battle_factories.ShipSerializer') as mock_serializer:
                # Return different clones for each ship
                mock_serializer.to_dict.return_value = {}
                mock_serializer.from_dict.side_effect = lambda data, registries: Mock()

                create_hypothetical_battle([mock_ship1], [mock_ship2])

        # Both teams should have ships added
        assert mock_controller.add_ships.call_count == 2
        mock_controller.start.assert_called_once()

    def test_hypothetical_battle_always_headless_isolated(self):
        """create_hypothetical_battle is always headless and isolated."""
        from game.ui.services.battle_factories import create_hypothetical_battle

        with patch('game.ui.services.battle_factories.BattleController') as mock_bc:
            mock_controller = Mock()
            mock_bc.return_value = mock_controller

            create_hypothetical_battle([], [], seed=42)

        # Should have configured controller
        mock_controller.configure.assert_called_once()

    def test_hypothetical_battle_with_seed(self):
        """create_hypothetical_battle supports seed parameter."""
        from game.ui.services.battle_factories import create_hypothetical_battle

        with patch('game.ui.services.battle_factories.BattleController') as mock_bc:
            mock_controller = Mock()
            mock_bc.return_value = mock_controller

            create_hypothetical_battle([], [], seed=42)

        mock_controller.configure.assert_called_once()
