"""PROJ-411 Task 2.6: Hidden ``StrategyModalWindow`` subclasses must not
consume input.

After Task 2.5 (Esc → hide for reuse), the hidden windows stayed in the
pygame_gui sprite group. ``UIManager.process_events`` walks every
``is_window`` sprite and calls ``check_clicked_inside_or_blocking`` —
the default pygame_gui implementation collides on rect only (no
visibility check), so a 90%-screen hidden window consumed every left-
click in its rect, blocking End Turn, hex selection, zoom, etc.

This test pins the contract on ``StrategyModalWindow.check_clicked_inside_or_blocking``:

* When ``self.visible == False``: short-circuit to False (don't consume).
* When ``self.visible == True``: delegate to pygame_gui's default.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pygame

from game.ui.screens.strategy_modal_window import StrategyModalWindow


def _make_fake_modal(visible: bool):
    """Cheapest possible stand-in: a MagicMock with the override bound
    to it. Skips pygame_gui construction entirely.
    """
    fake = MagicMock(name="modal")
    fake.visible = visible
    # Bind the unbound override to the fake instance.
    fake.check_clicked_inside_or_blocking = (
        StrategyModalWindow.check_clicked_inside_or_blocking.__get__(fake)
    )
    return fake


def test_hidden_modal_short_circuits_false():
    """visible=False → returns False, never delegates to super()."""
    fake = _make_fake_modal(visible=False)
    event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (50, 50)}
    )
    # Patch the super() call so we can detect if it was reached.
    from unittest.mock import patch
    with patch(
        "pygame_gui.elements.ui_window.UIWindow.check_clicked_inside_or_blocking",
        return_value=True,  # would consume the event if reached
    ) as mock_super:
        result = fake.check_clicked_inside_or_blocking(event)
    assert result is False, (
        "Hidden modal must not consume clicks — blocks End Turn / hex / "
        "zoom otherwise."
    )
    mock_super.assert_not_called()


def test_hide_removes_window_from_pygame_gui_window_stack():
    """PROJ-411 Task 2.8: hide() must remove the window from
    ``pygame_gui.UIWindow.window_stack`` so the hidden window isn't
    z-top — otherwise hit-testing / focus state routes events to it
    and blocks End Turn / zoom on the strategy view behind."""
    from unittest.mock import patch
    from game.ui.screens.event_log_window import EventLogWindow
    from tests.fixtures.ui_widget_factory import bypass_init

    with bypass_init(EventLogWindow):
        rect = pygame.Rect(0, 0, 100, 100)
        manager = MagicMock()
        win = EventLogWindow(rect, manager, [], window_manager=MagicMock())
    win.window_stack = MagicMock(name="window_stack")
    win.is_blocking = True
    with patch("pygame_gui.elements.ui_window.UIWindow.hide"):
        win.hide()
    win.window_stack.remove_window.assert_called_once_with(win)
    win._window_manager.unregister_modal.assert_called_once_with(win)
    assert win.is_blocking is False


def test_show_re_adds_window_to_pygame_gui_window_stack():
    """show() puts the window back in the stack at z-top."""
    from unittest.mock import patch
    from game.ui.screens.event_log_window import EventLogWindow
    from tests.fixtures.ui_widget_factory import bypass_init

    with bypass_init(EventLogWindow):
        rect = pygame.Rect(0, 0, 100, 100)
        manager = MagicMock()
        win = EventLogWindow(rect, manager, [], window_manager=MagicMock())
    win.window_stack = MagicMock(name="window_stack")
    with patch("pygame_gui.elements.ui_window.UIWindow.show"):
        win.show()
    win.window_stack.add_new_window.assert_called_once_with(win)
    win._window_manager.register_modal.assert_called_once_with(win)
    assert win.is_blocking is True


def test_override_is_inherited_by_all_proj411_reusable_windows():
    """All four PROJ-411 reusable windows inherit the override.

    The override lives on ``StrategyModalWindow`` so every subclass
    benefits. We assert MRO inheritance rather than calling the method
    on bypassed instances (which lack pygame_gui sprite-group state
    needed by ``super()``).
    """
    from game.ui.screens.planet_list_window import PlanetListWindow
    from game.ui.screens.star_list_window import StarListWindow
    from game.ui.screens.empire_panel_window import EmpirePanelWindow
    from game.ui.screens.event_log_window import EventLogWindow

    base_method = StrategyModalWindow.check_clicked_inside_or_blocking
    for cls in (PlanetListWindow, StarListWindow, EmpirePanelWindow,
                EventLogWindow):
        # The class either inherits the base override directly or
        # overrides further itself. In either case, the resolved method
        # must come from StrategyModalWindow (or a subclass) — NOT from
        # pygame_gui.UIWindow.
        resolved = cls.check_clicked_inside_or_blocking
        assert resolved is base_method or "StrategyModalWindow" in str(resolved), (
            f"{cls.__name__} does not inherit the StrategyModalWindow "
            f"visibility override; got {resolved}"
        )
