"""Right-click context menu for fleets in the strategy view (issue #20).

The menu is a thin ``pygame_gui.elements.UIPanel`` modelled on
``StrategyMenuPanel``: one row per ``FleetMenuItem`` returned by
``build_menu_items``, each row a ``UIButton`` with a label and an
optional shortcut suffix. Clicking a row dispatches the carried
``InputAction`` back through ``FleetCommandRouter`` so the menu reuses
the exact targeting flow the hotkey enters today.

The module also exposes two pure helpers used by the strategy_ui glue
and exercised in isolation by the unit tests:

  - ``clamp_menu_position(x, y, width, height, screen_width,
    screen_height)`` keeps the panel rect on-screen near edges.
  - ``dispatch_action(fleet_router, action)`` is the menu->router
    bridge: try the fleet handler first, fall back to the superweapon
    handler.
"""
from __future__ import annotations

from typing import Any, Callable, Sequence

import pygame
import pygame_gui
import pygame_gui.elements

from game.core.input_actions import InputAction
from game.ui.screens.fleet_menu_items import FleetMenuItem


# Layout constants — tuned for 2560x1600 and 3840x2160 displays.
ROW_HEIGHT = 32
ROW_GAP = 2
PANEL_PADDING = 8
PANEL_WIDTH = 260
SHORTCUT_COLUMN_WIDTH = 80


def clamp_menu_position(
    x: int,
    y: int,
    width: int,
    height: int,
    screen_width: int,
    screen_height: int,
) -> pygame.Rect:
    """Return a ``pygame.Rect`` clamped to fit inside the screen.

    Shifts left/up when the menu would overflow the right/bottom edge;
    clamps to ``(0, 0)`` if the caller passes negative coordinates.
    """
    if x + width > screen_width:
        x = screen_width - width
    if y + height > screen_height:
        y = screen_height - height
    x = max(0, x)
    y = max(0, y)
    return pygame.Rect(x, y, width, height)


def dispatch_action(fleet_router: Any, action: InputAction) -> None:
    """Route ``action`` through the existing fleet command router.

    Try ``handle_fleet_action`` first; if it didn't claim the action,
    fall through to ``handle_superweapon_action``. Mirrors the
    hotkey-dispatch chain in
    ``StrategyInputHandler._handle_keydown_mapped``.
    """
    if fleet_router.handle_fleet_action(action):
        return
    fleet_router.handle_superweapon_action(action)


class FleetContextMenu(pygame_gui.elements.UIPanel):
    """Floating panel of fleet orders for the right-clicked fleet.

    Spawned by ``StrategyUI.open_fleet_context_menu`` near the cursor.
    Each row is a ``UIButton`` whose ``InputAction`` is recorded in
    ``_action_buttons``. When a button is pressed the menu invokes
    ``on_action_selected(action)`` and the caller decides what to do
    (typically: close the menu and dispatch the action).
    """

    def __init__(
        self,
        relative_rect: pygame.Rect,
        manager: pygame_gui.UIManager,
        items: Sequence[FleetMenuItem],
        on_action_selected: Callable[[InputAction], None],
    ) -> None:
        super().__init__(
            relative_rect,
            starting_height=2,
            manager=manager,
        )
        self.on_action_selected = on_action_selected
        self._action_buttons: dict[pygame_gui.elements.UIButton, InputAction] = {}
        self._create_buttons(items)

    def _create_buttons(self, items: Sequence[FleetMenuItem]) -> None:
        for i, item in enumerate(items):
            y = PANEL_PADDING + i * (ROW_HEIGHT + ROW_GAP)
            text = self._format_row(item)
            button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(
                    PANEL_PADDING,
                    y,
                    PANEL_WIDTH - 2 * PANEL_PADDING,
                    ROW_HEIGHT,
                ),
                text=text,
                manager=self.ui_manager,
                container=self,
            )
            self._action_buttons[button] = item.action

    @staticmethod
    def _format_row(item: FleetMenuItem) -> str:
        """Return the row label text, with the shortcut right-aligned.

        If the action is unbound (``shortcut == ""``) only the label is
        rendered.
        """
        if not item.shortcut:
            return item.label
        # Right-justify the shortcut within a fixed character column.
        # This is a pragmatic alignment using monospace-friendly padding;
        # the UI builder is single-locale and the menu uses the default
        # font where this reads cleanly.
        pad = max(1, 26 - len(item.label))
        return f"{item.label}{' ' * pad}{item.shortcut}"

    def process_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            action = self._action_buttons.get(event.ui_element)
            if action is not None:
                self.on_action_selected(action)
                return True
        return super().process_event(event)

    @classmethod
    def required_height(cls, num_items: int) -> int:
        """Total panel height needed to hold ``num_items`` rows."""
        if num_items <= 0:
            return 2 * PANEL_PADDING
        return (
            2 * PANEL_PADDING
            + num_items * ROW_HEIGHT
            + (num_items - 1) * ROW_GAP
        )
