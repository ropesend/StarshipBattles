"""Tests for _retreat_allowed() and _reinforcements_allowed() priority logic.

The OR-based priority rule:
  Mode handler provides the default per battle mode.
  BattleConfig.allow_retreat=True can OVERRIDE to enable retreat in modes
  that normally deny it. Config cannot DISABLE retreat when mode handler
  allows it.

Same logic applies to _reinforcements_allowed().
"""
import pytest
from unittest.mock import Mock

from game.simulation.battle_controller import BattleController
from game.simulation.battle_config import BattleConfig, BattleMode
from game.simulation.services.battle_service import BattleServiceResult


class TestRetreatAllowedPriority:
    """Tests for _retreat_allowed() OR-based priority logic."""

    def _make_controller_with_mode_and_config(
        self, handler_can_retreat: bool, config_allow_retreat: bool,
        mode: BattleMode = BattleMode.MANUAL,
    ) -> BattleController:
        """Create a configured controller with specific retreat settings."""
        service = Mock()
        service.create_battle.return_value = BattleServiceResult(success=True)
        service.get_engine.return_value = Mock(tick_counter=0, ships=[], projectiles=[])

        controller = BattleController(service=service)
        config = BattleConfig(mode=mode, allow_retreat=config_allow_retreat)
        controller.configure(config)

        # Override mode handler's can_retreat to control test precisely
        controller._mode_handler.can_retreat = Mock(return_value=handler_can_retreat)
        return controller

    def test_handler_false_config_true_allows_retreat(self):
        """Config override: retreat allowed even when mode handler denies it."""
        ctrl = self._make_controller_with_mode_and_config(
            handler_can_retreat=False, config_allow_retreat=True,
        )
        assert ctrl._retreat_allowed() is True

    def test_handler_true_config_false_allows_retreat(self):
        """Mode handler wins: retreat allowed even when config is False."""
        ctrl = self._make_controller_with_mode_and_config(
            handler_can_retreat=True, config_allow_retreat=False,
        )
        assert ctrl._retreat_allowed() is True

    def test_handler_false_config_false_denies_retreat(self):
        """Both deny: retreat is not allowed."""
        ctrl = self._make_controller_with_mode_and_config(
            handler_can_retreat=False, config_allow_retreat=False,
        )
        assert ctrl._retreat_allowed() is False

    def test_handler_true_config_true_allows_retreat(self):
        """Both allow: retreat is allowed."""
        ctrl = self._make_controller_with_mode_and_config(
            handler_can_retreat=True, config_allow_retreat=True,
        )
        assert ctrl._retreat_allowed() is True

    def test_no_mode_handler_uses_config_only(self):
        """Without mode handler, config alone determines retreat."""
        service = Mock()
        service.create_battle.return_value = BattleServiceResult(success=True)

        controller = BattleController(service=service)
        controller._config = BattleConfig(allow_retreat=True)
        controller._mode_handler = None

        assert controller._retreat_allowed() is True

    def test_no_mode_handler_no_config_denies_retreat(self):
        """Without mode handler or config, retreat is denied."""
        service = Mock()
        controller = BattleController(service=service)
        controller._mode_handler = None
        controller._config = None

        assert controller._retreat_allowed() is False


class TestReinforcementsAllowedPriority:
    """Tests for _reinforcements_allowed() OR-based priority logic.

    Same OR-based pattern as _retreat_allowed().
    """

    def _make_controller_with_mode_and_config(
        self, handler_can_reinforce: bool, config_allow_reinforcements: bool,
        mode: BattleMode = BattleMode.MANUAL,
    ) -> BattleController:
        """Create a configured controller with specific reinforcement settings."""
        service = Mock()
        service.create_battle.return_value = BattleServiceResult(success=True)
        service.get_engine.return_value = Mock(tick_counter=0, ships=[], projectiles=[])

        controller = BattleController(service=service)
        config = BattleConfig(mode=mode, allow_reinforcements=config_allow_reinforcements)
        controller.configure(config)

        # Override mode handler's can_reinforce to control test precisely
        controller._mode_handler.can_reinforce = Mock(return_value=handler_can_reinforce)
        return controller

    def test_handler_false_config_true_allows_reinforcements(self):
        """Config override: reinforcements allowed even when mode handler denies it."""
        ctrl = self._make_controller_with_mode_and_config(
            handler_can_reinforce=False, config_allow_reinforcements=True,
        )
        assert ctrl._reinforcements_allowed() is True

    def test_handler_true_config_false_allows_reinforcements(self):
        """Mode handler wins: reinforcements allowed even when config is False."""
        ctrl = self._make_controller_with_mode_and_config(
            handler_can_reinforce=True, config_allow_reinforcements=False,
        )
        assert ctrl._reinforcements_allowed() is True

    def test_handler_false_config_false_denies_reinforcements(self):
        """Both deny: reinforcements are not allowed."""
        ctrl = self._make_controller_with_mode_and_config(
            handler_can_reinforce=False, config_allow_reinforcements=False,
        )
        assert ctrl._reinforcements_allowed() is False

    def test_handler_true_config_true_allows_reinforcements(self):
        """Both allow: reinforcements are allowed."""
        ctrl = self._make_controller_with_mode_and_config(
            handler_can_reinforce=True, config_allow_reinforcements=True,
        )
        assert ctrl._reinforcements_allowed() is True
