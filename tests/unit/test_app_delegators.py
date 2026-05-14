"""Unit coverage for thin Game delegators that do not require bootstrap."""
from types import SimpleNamespace
from unittest.mock import MagicMock

from game.app import Game
from game.core.constants import GameState


def test_request_shutdown_is_safe_without_loop():
    """`_request_shutdown` must tolerate a missing `_loop` attribute
    (Game.__new__-bypass tests, partial construction)."""
    game = Game.__new__(Game)

    # Should not raise even though `_loop` was never set.
    game._request_shutdown()


def test_request_shutdown_delegates_to_loop_when_present():
    """`_request_shutdown` is the canonical shutdown entry point; it
    must forward to `RunLoop.request_shutdown()`."""
    game = Game.__new__(Game)
    game._loop = MagicMock()

    game._request_shutdown()

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
    import game.app as app_mod

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
    monkeypatch.setattr(
        app_mod, "build_replay_ship_builder",
        lambda r, *, registry_provider: object(),
    )

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
    # PROJ-368 (post-r001): replays launched from the strategy Event Log
    # must return to the Strategy scene on exit, not to Battle Setup.
    from game.core.return_destination import ReturnDestination
    assert config.return_destination == ReturnDestination.STRATEGY


def test_start_replay_threads_replay_ship_builder_into_start_battle(monkeypatch):
    """PROJ-368: replay playback must use the snapshot-backed ship_builder
    (not the default InstanceBackedMaterializer, which fails because
    replays' ShipSpecs have instance_ref=None).
    """
    import game.simulation.replay.replay_player as replay_player
    import game.app as app_mod

    game = Game.__new__(Game)
    game.start_battle = MagicMock()
    spec = SimpleNamespace(
        seed=1, end_condition=object(), absolute_max_ticks=10,
        telemetry_level="full",
    )
    record = SimpleNamespace(replay_id="replay-1")
    monkeypatch.setattr(replay_player, "replay_record_to_spec", lambda r: spec)

    sentinel_builder = object()
    captured: dict = {}

    def fake_build_replay_ship_builder(passed_record, *, registry_provider):
        captured["record"] = passed_record
        captured["registry_provider"] = registry_provider
        return sentinel_builder

    monkeypatch.setattr(
        app_mod, "build_replay_ship_builder", fake_build_replay_ship_builder
    )

    game.start_replay(record)

    assert captured["record"] is record
    assert captured["registry_provider"] is not None
    assert game.start_battle.call_args.kwargs.get("ship_builder") is sentinel_builder
