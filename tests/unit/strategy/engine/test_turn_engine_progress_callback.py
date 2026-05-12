"""Issue #7 + PROJ-412 Phase 4: TurnEngine.process_turn invokes progress_callback
at a fixed cadence (tick 1, every Nth tick, tick 100).

The strategy UI uses the callback to repaint the "PROCESSING TURN..." overlay
between ticks. Probe B (Phase 1.4) showed the per-tick callback redraw cost
was the dominant contributor to the 2.5–3.7 s unaccounted-overhead gap; the
cadence change in Phase 4 cuts callback invocations from 100/turn to 21/turn
(default ``PROGRESS_CALLBACK_INTERVAL = 5``).
"""
from unittest.mock import MagicMock

import pytest

from game.strategy.data.empire import Empire
from game.strategy.engine.turn_engine import (
    PROGRESS_CALLBACK_INTERVAL,
    TICKS_PER_TURN,
    TurnEngine,
)
from tests.fixtures.turn_engine import build_test_turn_engine


_EXPECTED_CALLBACK_TICKS = (
    [1]
    + [t for t in range(PROGRESS_CALLBACK_INTERVAL, TICKS_PER_TURN + 1, PROGRESS_CALLBACK_INTERVAL)]
)
# For PROGRESS_CALLBACK_INTERVAL=5 this yields [1, 5, 10, 15, ..., 95, 100] = 21 ticks.


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


def test_progress_callback_fires_on_cadence(engine_inputs):
    """PROJ-412 Phase 4: callback fires at tick 1, every Nth tick, and tick 100.

    Replaces the pre-Phase-4 contract that invoked the callback on every
    tick (100/turn). The new cadence (default N=5) cuts callbacks to
    21/turn while keeping both endpoints visible to the UI.
    """
    engine, empires, galaxy = engine_inputs
    cb = MagicMock()

    engine.process_turn(empires, galaxy, save_path=None, progress_callback=cb)

    assert cb.call_count == len(_EXPECTED_CALLBACK_TICKS)
    expected = [((tick, TICKS_PER_TURN), {}) for tick in _EXPECTED_CALLBACK_TICKS]
    assert cb.call_args_list == expected


def test_progress_callback_always_fires_at_tick_1_and_last(engine_inputs):
    """UI must always see the first and last tick so the overlay shows 1/100 and 100/100."""
    engine, empires, galaxy = engine_inputs
    cb = MagicMock()

    engine.process_turn(empires, galaxy, save_path=None, progress_callback=cb)

    tick_args = [call.args[0] for call in cb.call_args_list]
    assert tick_args[0] == 1, "first callback invocation must be at tick 1"
    assert tick_args[-1] == TICKS_PER_TURN, (
        f"last callback invocation must be at tick {TICKS_PER_TURN}"
    )


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
    assert cb1.call_count == len(_EXPECTED_CALLBACK_TICKS)

    cb1.reset_mock()
    engine.process_turn(empires, galaxy, save_path=None)
    assert cb1.call_count == 0
