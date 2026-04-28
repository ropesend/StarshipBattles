"""FEAT-20: Tests for the dev-mode `Run 10 Turns` button in the strategy top bar.

The button is conditionally instantiated by `create_strategy_panels` only when
`dev_mode=True`. When dev_mode is False (production builds), the button is left
as None on the StrategyWidgets dataclass so click-handler comparisons safely
skip routing to it.
"""
from __future__ import annotations

import os
from dataclasses import fields
from unittest.mock import MagicMock

import pytest


# Force headless before pygame import.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


class TestRun10TurnsButtonField:
    """`btn_run_10_turns` must exist as a declared field on StrategyWidgets."""

    def test_btn_run_10_turns_field_declared(self):
        """The widgets dataclass must declare `btn_run_10_turns: Any = None`."""
        from game.ui.screens.strategy_panel_manager import StrategyWidgets
        field_names = {f.name for f in fields(StrategyWidgets)}
        assert "btn_run_10_turns" in field_names

    def test_btn_run_10_turns_default_is_none(self):
        """Default value is None so production (no dev_mode) leaves it unset."""
        from game.ui.screens.strategy_panel_manager import StrategyWidgets
        widgets = StrategyWidgets()
        assert widgets.btn_run_10_turns is None


def _create_panels(dev_mode: bool):
    """Create panels via `create_strategy_panels` with a real UIManager."""
    import pygame
    import pygame_gui
    from game.ui.screens.strategy_panel_manager import create_strategy_panels

    pygame.init()
    pygame.font.init()
    if not pygame.display.get_surface():
        pygame.display.set_mode((1440, 900), pygame.NOFRAME)

    manager = pygame_gui.UIManager((1440, 900))
    selection_cb = MagicMock()
    widgets = create_strategy_panels(
        manager, 1440, 900, sidebar_width=400,
        on_ui_selection_callback=selection_cb,
        dev_mode=dev_mode,
    )
    return widgets


class TestRun10TurnsButtonVisibility:
    """The button is created only when dev_mode=True."""

    def test_present_when_dev_mode_true(self):
        widgets = _create_panels(dev_mode=True)
        assert widgets.btn_run_10_turns is not None

    def test_absent_when_dev_mode_false(self):
        widgets = _create_panels(dev_mode=False)
        assert widgets.btn_run_10_turns is None
