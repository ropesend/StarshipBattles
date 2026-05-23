"""Contract test for the public API of `game.app`.

Locks the public symbol surface of `game.app` ahead of the PROJ-309 sub-phase
3.9 decomposition. This test MUST pass both before and after the split.

Public symbols required by external callers (launcher.py + 4 test files):
- `Game` class
- `main` callable
- `Game.__init__` signature must be `(self, args=None)` (positional/optional)
- Methods asserted by `tests/unit/ui/screens/test_strategy_menu_actions.py`:
    `_handle_strategy_action`, `_create_workshop_context`, `_switch_scene`,
    `start_builder`, `_on_load_game`
- Methods asserted by `tests/integration/test_app_integration.py`:
    `_start_quickstart`, `start_quickstart_1p`, `start_quickstart_2p`
- Attributes asserted by `tests/unit/systems/test_main_integration.py`:
    `battle_scene`, `battle_scene.engine`
- The aliases REMOVED test (regression): `MENU`, `BUILDER`, `BATTLE`,
    `SETTINGS` must NOT exist on the module.
"""
from __future__ import annotations

import inspect
import os

import pytest


# Ensure headless-safe display driver before importing pygame in tests below.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


def test_main_is_callable() -> None:
    """`main` must be importable as a top-level callable from `game.app`."""
    from game.app import main
    assert callable(main)


def test_game_class_importable() -> None:
    """`Game` class must be importable as a top-level symbol from `game.app`."""
    from game.app import Game
    assert inspect.isclass(Game)


def test_game_constructs_with_no_args() -> None:
    """`Game()` must be constructable with no positional/keyword args.

    PROJ-491 Task 1.4: replace the brittle ``inspect.signature`` parameter
    introspection on ``Game.__init__`` with a behavioral assertion — the
    public contract callers (launcher.py + several tests) depend on is that
    ``Game()`` can be called with no arguments. We verify by attempting the
    real construction and asserting no exception. Headless-safe pygame setup
    mirrors ``tests/unit/systems/test_main_integration.py``.

    PROJ-491 Phase 5 Task 5.1: the sibling test
    ``test_game_constructs_with_args_positional`` exercises the
    ``Game(args)`` positional path used by ``main()`` at
    ``game/app.py:510-513``. BOTH calling conventions documented in the
    module header are now exercised behaviorally.
    """
    import pygame
    from unittest.mock import MagicMock, patch

    from game.app import Game
    from game.simulation.replay.replay_capture import reset_default_capture_sink
    from game.strategy.services.replay_verification_coordinator import (
        shutdown_all_coordinators,
    )
    from game.strategy.systems.save_game_service import SaveGameService

    try:
        if not pygame.display.get_surface():
            pygame.display.set_mode((1440, 900), pygame.NOFRAME)
        with patch(
            "pygame.display.Info",
            return_value=MagicMock(current_w=1920, current_h=1080),
        ):
            game = Game()
            assert game is not None
    finally:
        # Drain coordinator threads / reset replay globals to mirror the
        # cleanup fixture used elsewhere for Game-instantiation tests.
        shutdown_all_coordinators(timeout=5.0)
        reset_default_capture_sink()
        SaveGameService.default().set_replay_store(None)


def test_game_constructs_with_args_positional() -> None:
    """`Game(args)` must be constructable with a positional args object.

    PROJ-491 Phase 5 Task 5.1: production ``main()`` calls
    ``Game(args)`` positionally with a parsed ``argparse.Namespace`` at
    ``game/app.py:510-513``. The module header documents the
    ``__init__(self, args=None)`` contract, so the positional-call path
    must also be exercised behaviorally — not just ``Game()`` with no
    args. We construct the args via the production ``parse_args()``
    helper (the same object ``main()`` passes through), then call
    ``Game(args)`` positionally — exactly matching the production
    call site.

    Headless-safe pygame setup + cleanup mirrors
    ``test_game_constructs_with_no_args``.
    """
    import pygame
    from unittest.mock import MagicMock, patch

    from game.app import Game
    from game.app_bootstrap import parse_args
    from game.simulation.replay.replay_capture import reset_default_capture_sink
    from game.strategy.services.replay_verification_coordinator import (
        shutdown_all_coordinators,
    )
    from game.strategy.systems.save_game_service import SaveGameService

    try:
        if not pygame.display.get_surface():
            pygame.display.set_mode((1440, 900), pygame.NOFRAME)
        with patch(
            "pygame.display.Info",
            return_value=MagicMock(current_w=1920, current_h=1080),
        ):
            args = parse_args()
            game = Game(args)
            assert game is not None
    finally:
        shutdown_all_coordinators(timeout=5.0)
        reset_default_capture_sink()
        SaveGameService.default().set_replay_store(None)


@pytest.mark.parametrize("method_name", [
    # Quickstart helpers (tests/integration/test_app_integration.py)
    "_start_quickstart",
    "start_quickstart_1p",
    "start_quickstart_2p",
    # Strategy action handler (tests/unit/ui/screens/test_strategy_menu_actions.py)
    "_handle_strategy_action",
    "_create_workshop_context",
    "_switch_scene",
    # Builder
    "start_builder",
    "on_builder_return",
    # Strategy lifecycle
    "start_strategy_layer",
    # Battle setup / battle
    "start_battle_setup",
    "start_battle",
    "_handle_battle_action",
    "_handle_battle_setup_action",
    # Test lab
    "start_test_lab",
    "_handle_test_lab_action",
    # Other entry points
    "show_load_menu",
    "_on_load_game",
    "start_keybindings",
    "on_keybindings_return",
    "start_research_tree",
    "on_research_tree_return",
    "start_galaxy_test",
    "on_galaxy_test_return",
    "start_race_setup",
    # Run loop
    "run",
])
def test_game_has_required_method(method_name: str) -> None:
    """Each method asserted by a caller must exist on the `Game` class."""
    from game.app import Game
    assert hasattr(Game, method_name), (
        f"Game.{method_name} missing — required by callers/tests"
    )
    assert callable(getattr(Game, method_name))


def test_game_state_property_is_property() -> None:
    """`Game.state` must be a property (with setter)."""
    from game.app import Game
    assert isinstance(Game.state, property)
    assert Game.state.fget is not None
    assert Game.state.fset is not None


def test_screen_transitions_constant_present() -> None:
    """`_SCREEN_TRANSITIONS` constant should remain importable from the module."""
    from game import app as app_mod
    assert hasattr(app_mod, "_SCREEN_TRANSITIONS")
    transitions = app_mod._SCREEN_TRANSITIONS
    assert isinstance(transitions, frozenset)
    # Spot-check a few transitions from the original
    from game.core.constants import GameState
    assert (GameState.MENU, GameState.BUILDER) in transitions
    assert (GameState.STRATEGY, GameState.BATTLE) in transitions


def test_game_state_aliases_remain_removed() -> None:
    """Regression: GameState aliases stay removed (per existing regression suite)."""
    from game import app as app_mod
    assert not hasattr(app_mod, "MENU")
    assert not hasattr(app_mod, "BUILDER")
    assert not hasattr(app_mod, "BATTLE")
    assert not hasattr(app_mod, "SETTINGS")


