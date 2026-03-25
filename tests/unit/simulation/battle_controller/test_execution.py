"""Tests for BattleController execution methods (start, update, run_headless, run_ticks)."""
import pytest
from unittest.mock import Mock, patch

from game.simulation.battle_controller import BattleController
from game.simulation.battle_config import BattleConfig, BattleMode
from game.simulation.services.battle_service import BattleServiceResult


class TestBattleControllerStart:
    """Tests for BattleController.start()."""

    def test_start_fails_when_not_configured(self, controller):
        """start fails when not configured."""
        result = controller.start()
        assert result.success is False
        assert "not configured" in result.errors[0].lower()

    def test_start_fails_when_already_started(self, controller, basic_config, mock_service):
        """start fails when battle already started."""
        controller.configure(basic_config)
        controller._is_started = True

        result = controller.start()

        assert result.success is False
        assert "already started" in result.errors[0].lower()

    def test_start_calls_service_start_battle(self, controller, basic_config, mock_service):
        """start calls service.start_battle with correct args."""
        controller.configure(basic_config)

        controller.start()

        mock_service.start_battle.assert_called_once_with(
            end_mode=basic_config.end_mode,
            max_ticks=basic_config.max_ticks
        )

    def test_start_sets_is_started_on_success(self, controller, basic_config, mock_service):
        """start sets _is_started when service succeeds."""
        controller.configure(basic_config)

        controller.start()

        assert controller._is_started is True

    def test_start_does_not_set_is_started_on_failure(self, controller, basic_config, mock_service):
        """start does not set _is_started when service fails."""
        mock_service.start_battle.return_value = BattleServiceResult(success=False, errors=["Error"])
        controller.configure(basic_config)

        controller.start()

        assert controller._is_started is False

    def test_start_assigns_ids_to_ships(self, controller, basic_config, mock_service):
        """start assigns UUIDs to ships without IDs."""
        mock_ship = Mock()
        mock_service.get_all_ships.return_value = [mock_ship]
        controller.configure(basic_config)

        controller.start()

        assert id(mock_ship) in controller._ship_id_map

    def test_start_captures_initial_state(self, controller, basic_config, mock_service):
        """start captures the initial battle state via BattleStateManager."""
        mock_engine = Mock()
        mock_engine.ships = []
        mock_engine.projectiles = []
        mock_engine.tick_counter = 0
        mock_service.get_engine.return_value = mock_engine

        controller.configure(basic_config)

        with patch.object(controller._state_manager, 'capture_state', return_value=Mock()) as mock_capture:
            controller.start()
            mock_capture.assert_called_once_with(mock_engine, basic_config)

    def test_start_returns_service_result(self, controller, basic_config, mock_service):
        """start returns the result from service."""
        controller.configure(basic_config)
        expected_result = BattleServiceResult(success=True)
        mock_service.start_battle.return_value = expected_result

        result = controller.start()

        assert result is expected_result


class TestBattleControllerUpdate:
    """Tests for BattleController.update()."""

    def test_update_fails_when_not_started(self, controller, basic_config, mock_service):
        """update fails when battle not started."""
        controller.configure(basic_config)

        result = controller.update()

        assert result.success is False
        assert "not started" in result.errors[0].lower()

    def test_update_calls_service_update(self, controller, basic_config, mock_service):
        """update calls service.update."""
        controller.configure(basic_config)
        controller.start()

        controller.update()

        mock_service.update.assert_called()

    def test_update_processes_retreats_when_enabled(self, controller, mock_service):
        """update processes retreats when allow_retreat is True."""
        config = BattleConfig(mode=BattleMode.MANUAL, allow_retreat=True)
        controller.configure(config)
        controller.start()

        with patch.object(controller, '_update_retreats') as mock_update_retreats:
            controller.update()
            mock_update_retreats.assert_called_once()

    def test_update_skips_retreats_when_disabled(self, controller, basic_config, mock_service):
        """update skips retreat processing when allow_retreat is False."""
        controller.configure(basic_config)  # allow_retreat defaults to False
        controller.start()

        with patch.object(controller, '_update_retreats') as mock_update_retreats:
            controller.update()
            mock_update_retreats.assert_not_called()

    def test_update_calls_completion_callback_when_over(self, controller, basic_config, mock_service):
        """update calls completion callback when battle ends."""
        controller.configure(basic_config)
        controller.start()

        callback = Mock()
        controller.set_on_battle_complete(callback)

        mock_service.is_battle_over.return_value = True
        controller.update()

        callback.assert_called_once()

    def test_update_returns_service_result(self, controller, basic_config, mock_service):
        """update returns the result from service."""
        controller.configure(basic_config)
        controller.start()

        expected_result = BattleServiceResult(success=True)
        mock_service.update.return_value = expected_result

        result = controller.update()

        assert result is expected_result


class TestBattleControllerRunHeadless:
    """Tests for BattleController.run_headless()."""

    def test_run_headless_raises_when_not_started(self, controller, basic_config, mock_service):
        """run_headless raises StateException when not started."""
        from game.core.exceptions import StateException
        controller.configure(basic_config)

        with pytest.raises(StateException, match="not started"):
            controller.run_headless()

    def test_run_headless_runs_until_battle_over(self, controller, basic_config, mock_service):
        """run_headless runs until is_battle_over returns True."""
        controller.configure(basic_config)
        controller.start()

        # Battle ends after 5 updates
        call_count = [0]
        def side_effect():
            call_count[0] += 1
            return call_count[0] >= 5
        mock_service.is_battle_over.side_effect = side_effect

        controller.run_headless()

        # Should have called update 4 times (stopped when is_battle_over became True)
        assert mock_service.update.call_count == 4

    def test_run_headless_respects_max_ticks(self, controller, mock_service):
        """run_headless stops at max_ticks limit."""
        config = BattleConfig(mode=BattleMode.MANUAL, max_ticks=10)
        controller.configure(config)
        controller.start()

        # Battle never ends naturally
        mock_service.is_battle_over.return_value = False

        controller.run_headless()

        assert mock_service.update.call_count == 10

    def test_run_headless_calls_progress_callback(self, controller, mock_service):
        """run_headless calls progress callback every 100 ticks."""
        config = BattleConfig(mode=BattleMode.MANUAL, max_ticks=250)
        controller.configure(config)
        controller.start()

        mock_service.is_battle_over.return_value = False

        progress_calls = []
        def track_progress(tick, max_ticks):
            progress_calls.append((tick, max_ticks))

        controller.run_headless(progress_callback=track_progress)

        # Should be called at ticks 100, 200
        assert (100, 250) in progress_calls
        assert (200, 250) in progress_calls

    def test_run_headless_processes_retreats_when_enabled(self, controller, mock_service):
        """run_headless processes retreats each tick when enabled."""
        config = BattleConfig(mode=BattleMode.MANUAL, max_ticks=5, allow_retreat=True)
        controller.configure(config)
        controller.start()

        mock_service.is_battle_over.return_value = False

        with patch.object(controller, '_update_retreats') as mock_retreats:
            controller.run_headless()
            assert mock_retreats.call_count == 5

    def test_run_headless_returns_results(self, controller, basic_config, mock_service):
        """run_headless returns BattleServiceResults."""
        controller.configure(basic_config)
        controller.start()
        mock_service.is_battle_over.return_value = True

        results = controller.run_headless()

        # BattleServiceResults should be returned
        assert hasattr(results, 'winner')
        assert hasattr(results, 'tick_count')


class TestBattleControllerRunTicks:
    """Tests for BattleController.run_ticks()."""

    def test_run_ticks_fails_when_not_started(self, controller, basic_config, mock_service):
        """run_ticks fails when battle not started."""
        controller.configure(basic_config)

        result = controller.run_ticks(10)

        assert result.success is False
        assert "not started" in result.errors[0].lower()

    def test_run_ticks_runs_specified_count(self, controller, basic_config, mock_service):
        """run_ticks runs the specified number of ticks."""
        controller.configure(basic_config)
        controller.start()
        mock_service.is_battle_over.return_value = False

        controller.run_ticks(15)

        assert mock_service.update.call_count == 15

    def test_run_ticks_stops_when_battle_over(self, controller, basic_config, mock_service):
        """run_ticks stops early when battle ends."""
        controller.configure(basic_config)
        controller.start()

        # Battle ends after 5 ticks
        call_count = [0]
        def side_effect():
            call_count[0] += 1
            return call_count[0] >= 5
        mock_service.is_battle_over.side_effect = side_effect

        controller.run_ticks(100)

        # Should have run fewer ticks than requested
        assert mock_service.update.call_count < 100

    def test_run_ticks_processes_retreats_when_enabled(self, controller, mock_service):
        """run_ticks processes retreats each tick when enabled."""
        config = BattleConfig(mode=BattleMode.MANUAL, allow_retreat=True)
        controller.configure(config)
        controller.start()
        mock_service.is_battle_over.return_value = False

        with patch.object(controller, '_update_retreats') as mock_retreats:
            controller.run_ticks(10)
            assert mock_retreats.call_count == 10

    def test_run_ticks_returns_success(self, controller, basic_config, mock_service):
        """run_ticks returns success result."""
        controller.configure(basic_config)
        controller.start()
        mock_service.is_battle_over.return_value = False

        result = controller.run_ticks(5)

        assert result.success is True
