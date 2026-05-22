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
    """Method must short-circuit to None when context_data lacks an empire.

    PROJ-475 Phase 2 Task 2.4: the gate is now empire-only; the live
    ``game_session`` was replaced by a scalar ``save_path`` so the session is
    no longer threaded through (or required) here.
    """
    game = _make_bypass_init_game()

    result = game._create_workshop_context({"save_path": "saves/test_save"})

    assert result is None


def test_create_workshop_context_builds_workshop_context_when_inputs_present() -> None:
    """With a valid empire + scalar save_path, method must return a WorkshopContext.

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

    result = game._create_workshop_context({
        "empire": empire,
        "save_path": "saves/test_save",
    })

    assert isinstance(result, WorkshopContext)
    assert result.empire_id == 1


def test_create_workshop_context_handles_missing_save_path() -> None:
    """``save_path`` may be absent for new games — must not raise (PROJ-475)."""
    from game.ui.screens.workshop_context import WorkshopContext

    game = _make_bypass_init_game()

    empire = SimpleNamespace(id=2, empire_theme_id=None, built_ship_designs=set())

    # No save_path key at all (new game, never saved).
    result = game._create_workshop_context({"empire": empire})

    assert isinstance(result, WorkshopContext)
