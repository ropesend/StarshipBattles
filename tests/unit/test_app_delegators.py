"""Unit coverage for thin Game delegators that do not require bootstrap."""
from types import SimpleNamespace
from unittest.mock import MagicMock

from game.app import Game
from game.core.constants import GameState


def test_request_shutdown_clears_running_without_loop():
    game = Game.__new__(Game)
    game.running = True

    game._request_shutdown()

    assert game.running is False


def test_request_shutdown_notifies_loop_when_present():
    game = Game.__new__(Game)
    game.running = True
    game._loop = MagicMock()

    game._request_shutdown()

    assert game.running is False
    game._loop.request_shutdown.assert_called_once_with()


def test_return_to_test_lab_resets_selection_and_starts_screen():
    game = Game.__new__(Game)
    game.test_lab_scene = MagicMock()
    game.start_test_lab = MagicMock()

    game._return_to("test_lab")

    game.test_lab_scene.reset_selection.assert_called_once_with()
    game.start_test_lab.assert_called_once_with()


def test_return_to_battle_setup_preserves_teams():
    game = Game.__new__(Game)
    game.start_battle_setup = MagicMock()

    game._return_to("battle_setup")

    game.start_battle_setup.assert_called_once_with(preserve_teams=True)


def test_return_to_strategy_switches_to_strategy_scene():
    game = Game.__new__(Game)
    game.strategy_scene = object()
    game._switch_scene = MagicMock()

    game._return_to("strategy")

    game._switch_scene.assert_called_once_with(GameState.STRATEGY, game.strategy_scene)


def test_start_replay_builds_replay_config_and_starts_battle(monkeypatch):
    import game.simulation.replay.replay_player as replay_player

    game = Game.__new__(Game)
    game.start_battle = MagicMock()
    end_condition = object()
    spec = SimpleNamespace(
        seed=123,
        end_condition=end_condition,
        absolute_max_ticks=456,
        telemetry_level="full",
    )
    record = SimpleNamespace(replay_id="replay-1")
    monkeypatch.setattr(replay_player, "replay_record_to_spec", lambda actual: spec)

    game.start_replay(record)

    game.start_battle.assert_called_once()
    actual_spec = game.start_battle.call_args.args[0]
    config = game.start_battle.call_args.kwargs["config"]
    assert actual_spec is spec
    assert config.seed == 123
    assert config.end_condition is end_condition
    assert config.absolute_max_ticks == 456
    assert config.replay_mode is True
    assert config.replay_id == "replay-1"
    assert config.captured_telemetry_level == "full"
