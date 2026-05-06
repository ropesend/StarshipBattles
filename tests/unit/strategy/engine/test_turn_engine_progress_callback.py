"""Issue #7: TurnEngine.process_turn invokes progress_callback every tick.

Verifies the per-tick progress callback contract used by the strategy UI to
update the "PROCESSING TURN..." overlay with the current tick number while the
otherwise-synchronous 100-tick loop runs.
"""
from unittest.mock import MagicMock

import pytest

from game.strategy.data.empire import Empire
from game.strategy.engine.turn_engine import TICKS_PER_TURN, TurnEngine
from tests.fixtures.turn_engine import build_test_turn_engine


@pytest.fixture
def engine_inputs(fresh_registries):
    """Build a TurnEngine plus an empty empire/galaxy pair for a no-op turn."""
    engine = build_test_turn_engine(fresh_registries, ai_factory=MagicMock())

    empire = MagicMock(spec=Empire)
    empire.id = 0
    empire.name = "Test Empire"
    empire.fleets = []
    empire.colonies = []

    galaxy = MagicMock()
    galaxy.systems = {}
    galaxy.get_planets_at_global_hex = MagicMock(return_value=[])
    galaxy.get_system_of_planet = MagicMock(return_value=None)

    return engine, [empire], galaxy


def test_progress_callback_invoked_for_every_tick(engine_inputs):
    engine, empires, galaxy = engine_inputs
    cb = MagicMock()

    engine.process_turn(empires, galaxy, save_path=None, progress_callback=cb)

    assert cb.call_count == TICKS_PER_TURN
    expected = [((tick, TICKS_PER_TURN), {}) for tick in range(1, TICKS_PER_TURN + 1)]
    assert cb.call_args_list == expected


def test_progress_callback_exception_does_not_break_turn(engine_inputs, caplog):
    engine, empires, galaxy = engine_inputs

    def boom(tick, total):
        raise RuntimeError("ui callback bug")

    with caplog.at_level("WARNING", logger="game.strategy.engine.turn_engine"):
        engine.process_turn(empires, galaxy, save_path=None, progress_callback=boom)

    assert any(
        "progress_callback raised" in record.getMessage()
        for record in caplog.records
        if record.levelname == "WARNING"
    )


def test_progress_callback_default_none_is_backwards_compatible(engine_inputs):
    engine, empires, galaxy = engine_inputs
    engine.process_turn(empires, galaxy, save_path=None)


def test_progress_callback_cleared_between_calls(engine_inputs):
    """Engine must not leak a callback set on call N into call N+1."""
    engine, empires, galaxy = engine_inputs
    cb1 = MagicMock()

    engine.process_turn(empires, galaxy, save_path=None, progress_callback=cb1)
    assert cb1.call_count == TICKS_PER_TURN

    cb1.reset_mock()
    engine.process_turn(empires, galaxy, save_path=None)
    assert cb1.call_count == 0
