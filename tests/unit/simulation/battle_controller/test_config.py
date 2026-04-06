"""Tests for BattleController config classes and mode handlers."""
import pytest
from unittest.mock import Mock, patch

from game.simulation.battle_controller import (
    BattleController,
    BattleConfig,
    BattleMode,
)
from game.simulation.managers.retreat_manager import RetreatState
from game.simulation.systems.battle_end_conditions import TeamEliminatedCondition


class TestBattleMode:
    """Tests for BattleMode enum."""

    def test_battle_modes_exist(self):
        """All expected battle modes exist."""
        assert BattleMode.MANUAL.value == "manual"
        assert BattleMode.TEST.value == "test"
        assert BattleMode.STRATEGY.value == "strategy"
        assert BattleMode.HYPOTHETICAL.value == "hypothetical"


class TestBattleConfig:
    """Tests for BattleConfig dataclass."""

    def test_config_defaults(self):
        """BattleConfig has expected defaults."""
        config = BattleConfig()

        assert config.mode == BattleMode.MANUAL
        assert config.seed is None
        assert config.absolute_max_ticks == 1000000
        assert isinstance(config.end_condition, TeamEliminatedCondition)
        assert config.headless is False
        assert config.start_paused is False
        assert config.enable_logging is True
        assert config.allow_retreat is False
        assert config.allow_reinforcements is False

    def test_config_custom_values(self):
        """BattleConfig accepts custom values."""
        config = BattleConfig(
            mode=BattleMode.STRATEGY,
            seed=42,
            absolute_max_ticks=5000,
            headless=True,
            allow_retreat=True,
        )

        assert config.mode == BattleMode.STRATEGY
        assert config.seed == 42
        assert config.absolute_max_ticks == 5000
        assert config.headless is True
        assert config.allow_retreat is True


class TestRetreatState:
    """Tests for RetreatState dataclass."""

    def test_retreat_state_edge(self):
        """RetreatState for edge method."""
        state = RetreatState(method="edge", target=(0, 5000))

        assert state.method == "edge"
        assert state.target == (0, 5000)

    def test_retreat_state_warp(self):
        """RetreatState for warp method."""
        state = RetreatState(method="warp")

        assert state.method == "warp"
        assert state.charge_ticks == 0
        assert state.required_ticks == 500
        assert state.interruptible is True


class TestBattleControllerModeHandlers:
    """Tests for BattleController mode handler integration."""

    def test_configure_creates_mode_handler(self, controller, basic_config, mock_service):
        """configure() creates appropriate mode handler."""
        controller.configure(basic_config)

        assert controller.mode_handler is not None

    def test_manual_mode_creates_manual_handler(self, controller, mock_service):
        """MANUAL mode creates ManualBattleModeHandler."""
        from game.simulation.combat.battle_mode_handler import ManualBattleModeHandler

        config = BattleConfig(mode=BattleMode.MANUAL)
        controller.configure(config)

        assert isinstance(controller.mode_handler, ManualBattleModeHandler)

    def test_test_mode_creates_test_handler(self, controller, mock_service):
        """TEST mode creates TestBattleModeHandler."""
        from game.simulation.combat.battle_mode_handler import TestBattleModeHandler

        config = BattleConfig(mode=BattleMode.TEST)
        controller.configure(config)

        assert isinstance(controller.mode_handler, TestBattleModeHandler)

    def test_strategy_mode_creates_strategy_handler(self, controller, mock_service):
        """STRATEGY mode creates StrategyBattleModeHandler."""
        from game.simulation.combat.battle_mode_handler import StrategyBattleModeHandler

        config = BattleConfig(mode=BattleMode.STRATEGY)
        controller.configure(config)

        assert isinstance(controller.mode_handler, StrategyBattleModeHandler)

    def test_hypothetical_mode_creates_hypothetical_handler(self, controller, mock_service):
        """HYPOTHETICAL mode creates HypotheticalBattleModeHandler."""
        from game.simulation.combat.battle_mode_handler import HypotheticalBattleModeHandler

        config = BattleConfig(mode=BattleMode.HYPOTHETICAL)
        controller.configure(config)

        assert isinstance(controller.mode_handler, HypotheticalBattleModeHandler)

    def test_reset_clears_mode_handler(self, controller, basic_config, mock_service):
        """reset() clears the mode handler."""
        controller.configure(basic_config)
        assert controller.mode_handler is not None

        controller.reset()

        assert controller.mode_handler is None

    def test_strategy_mode_allows_retreat(self, controller, mock_service, mock_ship):
        """Strategy mode with handler allows retreat."""
        config = BattleConfig(mode=BattleMode.STRATEGY)
        controller.configure(config)
        controller.start()

        # Add ship to tracking
        controller._ship_id_map[mock_ship.id] = "ship-id"

        result = controller.request_retreat(mock_ship, method="edge")

        assert result.success is True

    def test_manual_mode_blocks_retreat(self, controller, mock_service, mock_ship):
        """Manual mode blocks retreat even without config flag."""
        config = BattleConfig(mode=BattleMode.MANUAL)
        controller.configure(config)
        controller.start()

        result = controller.request_retreat(mock_ship)

        assert result.success is False
        assert "not allowed" in result.errors[0].lower()

    def test_strategy_mode_allows_reinforcements(self, controller, mock_service, mock_ship):
        """Strategy mode allows reinforcements."""
        config = BattleConfig(mode=BattleMode.STRATEGY)
        controller.configure(config)
        controller.start()

        mock_engine = Mock()
        mock_service.get_engine.return_value = mock_engine

        result = controller.add_reinforcements([mock_ship], team_id=0, entry_point=(0, 0))

        assert result.success is True

    def test_manual_mode_blocks_reinforcements(self, controller, mock_service, mock_ship):
        """Manual mode blocks reinforcements."""
        config = BattleConfig(mode=BattleMode.MANUAL)
        controller.configure(config)
        controller.start()

        result = controller.add_reinforcements([mock_ship], team_id=0, entry_point=(0, 0))

        assert result.success is False
        assert "not allowed" in result.errors[0].lower()
