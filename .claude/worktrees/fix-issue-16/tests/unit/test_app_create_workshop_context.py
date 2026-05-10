"""Regression test for `Game._create_workshop_context` (sub-phase 3.9 fix).

The original 850-LOC `app.py` had a self-contained `_create_workshop_context`
method that built a `WorkshopContext` from strategy-scene `context_data`
plus `self.registries`. During the PROJ-309 sub-phase 3.9 decomposition,
the method was accidentally replaced by a forwarder

    return self._router._create_workshop_context(context_data)

but `ScreenRouter` does NOT define `_create_workshop_context` — it was
only mentioned in the router's module docstring. Result: clicking
"Design" on the strategy screen crashed with `AttributeError`. This test
exercises the method directly so the regression cannot recur.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from game.app import Game


def _make_bypass_init_game() -> Game:
    """Construct a `Game` instance bypassing `__init__` (the bootstrap is
    pygame-dependent). Wires only what `_create_workshop_context` reads."""
    game = Game.__new__(Game)
    game.registries = MagicMock(name="GameRegistries")
    return game


def test_create_workshop_context_returns_none_when_empire_missing() -> None:
    """Method must short-circuit to None when context_data lacks an empire."""
    game = _make_bypass_init_game()

    result = game._create_workshop_context({"game_session": MagicMock()})

    assert result is None


def test_create_workshop_context_returns_none_when_session_missing() -> None:
    """Method must short-circuit to None when context_data lacks a game_session."""
    game = _make_bypass_init_game()

    result = game._create_workshop_context({"empire": MagicMock()})

    assert result is None


def test_create_workshop_context_builds_workshop_context_when_inputs_present() -> None:
    """With a valid empire + game_session, method must return a WorkshopContext.

    This is the regression — pre-fix this raised
    `AttributeError: 'ScreenRouter' object has no attribute '_create_workshop_context'`.
    """
    from game.ui.screens.workshop_context import WorkshopContext

    game = _make_bypass_init_game()

    empire = SimpleNamespace(
        id=1,
        empire_theme_id="default",
        built_ship_designs={"design_a", "design_b"},
    )
    game_session = SimpleNamespace(save_path="saves/test_save")

    result = game._create_workshop_context({
        "empire": empire,
        "game_session": game_session,
    })

    assert isinstance(result, WorkshopContext)
    assert result.empire_id == 1


def test_create_workshop_context_handles_session_without_save_path() -> None:
    """`game_session.save_path` may be missing for new games — must not raise."""
    from game.ui.screens.workshop_context import WorkshopContext

    game = _make_bypass_init_game()

    empire = SimpleNamespace(id=2, empire_theme_id=None, built_ship_designs=set())
    game_session = SimpleNamespace()  # no save_path attribute

    result = game._create_workshop_context({
        "empire": empire,
        "game_session": game_session,
    })

    assert isinstance(result, WorkshopContext)
