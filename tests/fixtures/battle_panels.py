"""Shared mock-pygame fixture for battle_panels tests.

PROJ-479 Task 5.2 (DUP-002): consolidates the `_draw_setup` / `_stub_fonts`
/ `_install_battle_panels_pygame_mock` helpers that were duplicated between
`tests/unit/ui/test_battle_panels_characterization.py` and
`tests/unit/ui/test_battle_panels_extended.py`.

Tests should consume the `battle_panels_module` pytest fixture exported here.
"""
from __future__ import annotations

import importlib
import sys
from unittest.mock import MagicMock, patch

import pytest


class MockRect:
    """Reused MockRect used by battle_panels tests."""

    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.topleft = (x, y)
        self.bottomleft = (x, y + h)
        self.center = (x + w // 2, y + h // 2)
        self.centerx = x + w // 2
        self.bottom = y + h
        self.size = (w, h)

    def collidepoint(self, *args):
        if len(args) == 1:
            px, py = args[0]
        else:
            px, py = args
        return (
            self.x <= px < self.x + self.width
            and self.y <= py < self.y + self.height
        )

    def inflate(self, *_args):
        return self


@pytest.fixture
def battle_panels_module():
    """Yield (battle_panels module, mock_pygame) with pygame substituted.

    Sets up MockRect, K_LSHIFT/RSHIFT, SRCALPHA, and a shift-not-held
    key.get_pressed() default. Reloads battle_panels under the patched
    sys.modules so module-level pygame references bind to the mock.
    """
    mock_pygame = MagicMock()
    mock_pygame.K_LSHIFT = 1
    mock_pygame.K_RSHIFT = 2
    mock_pygame.SRCALPHA = 0
    mock_pygame.Rect = MockRect

    modules_patcher = patch.dict(sys.modules, {"pygame": mock_pygame})
    modules_patcher.start()
    try:
        from game.ui.panels import battle_panels
        importlib.reload(battle_panels)
        mock_pygame.key.get_pressed.return_value = {
            mock_pygame.K_LSHIFT: False,
            mock_pygame.K_RSHIFT: False,
        }
        yield battle_panels, mock_pygame
    finally:
        modules_patcher.stop()
