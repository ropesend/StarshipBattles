"""Regression tests for PROJ-342: drop self.game handle from TestLab UI.

These tests pin the bug surface that triggered the project (the "Run All"
crash) and the new constructor contract that replaces it.

Both tests must FAIL on pre-PROJ-342 code and PASS after the refactor.
"""
from __future__ import annotations

import inspect
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pygame
import pytest

from game.ui.screens.test_lab.screen import TestLabScreen


@pytest.fixture
def mock_display_surface():
    """Mock pygame display surface that supports the operations
    `_render_progress` and `_draw_and_flip` perform on it."""
    surface = Mock(spec=pygame.Surface)
    surface.get_width.return_value = 3840
    surface.get_height.return_value = 2160
    return surface


def test_render_progress_does_not_require_game_screen_attribute(
    mock_display_surface,
) -> None:
    """The original crash: `self.game.screen.get_width()` at screen.py:382.

    `ScreenRouter` (the production `self.game`) has no `.screen` attribute,
    so the call raises `AttributeError`. After PROJ-342 the helper uses
    `pygame.display.get_surface()` and cached dimensions instead.

    This test bypasses `__init__` to set up the minimal post-refactor state
    on either old or new code, so it pins the access pattern rather than
    the constructor signature.
    """
    screen = TestLabScreen.__new__(TestLabScreen)
    # Stub `self.game` to a ScreenRouter-shaped object: has battle_scene,
    # has NO `screen` attribute. This is the exact production shape that
    # crashed at the user's "Run All" click.
    screen.game = SimpleNamespace(battle_scene=Mock())
    # Provide cached dimensions (post-refactor stores these at init).
    screen.screen_width = 3840
    screen.screen_height = 2160
    # Pre-refactor stores `battle_scene` only via `self.game`; post-refactor
    # adds `self.battle_scene`. Set both so the test runs on either side.
    screen.battle_scene = screen.game.battle_scene

    with patch("pygame.display.get_surface", return_value=mock_display_surface):
        # Must not raise AttributeError on `self.game.screen` lookup.
        screen._render_progress("title", "subtitle", "detail")


def test_constructor_signature_drops_game_handle() -> None:
    """The new constructor signature: `(screen_width, screen_height, battle_scene, scene_callback)`.

    Pre-PROJ-342 signature is `(self, game, scene_callback=None)`. After the
    refactor the constructor takes explicit dimensions and a `battle_scene`
    reference instead.

    Inspect-only check; no collaborator wiring is exercised here so the
    test stays fast and isolated.
    """
    sig = inspect.signature(TestLabScreen.__init__)
    params = list(sig.parameters.keys())

    assert "game" not in params, (
        f"TestLabScreen.__init__ must not take a `game` parameter after PROJ-342, "
        f"got: {params}"
    )
    assert "screen_width" in params, (
        f"TestLabScreen.__init__ must accept `screen_width`, got: {params}"
    )
    assert "screen_height" in params, (
        f"TestLabScreen.__init__ must accept `screen_height`, got: {params}"
    )
    assert "battle_scene" in params, (
        f"TestLabScreen.__init__ must accept `battle_scene`, got: {params}"
    )
    assert "scene_callback" in params, (
        f"TestLabScreen.__init__ must accept `scene_callback`, got: {params}"
    )
