"""Tri-state radio button filter widget for sidebar filter panels."""
from typing import Optional

import pygame
from pygame_gui.elements import UIButton, UILabel

from game.ui.filters.filter_state import FilterState


# Button widths for the three radio buttons
_BTN_WIDTH = 40
_BTN_GAP = 2
_BUTTONS_TOTAL_WIDTH = 3 * _BTN_WIDTH + 2 * _BTN_GAP


class TriStateFilterWidget:
    """A single filter row with a label and three radio buttons (Yes / No / Ign).

    Layout: [Label (flexible)] [Yes (40px)] [No (40px)] [Ign (40px)]
    """

    def __init__(
        self,
        attribute_name: str,
        label: str,
        rect: pygame.Rect,
        manager,
        container,
    ) -> None:
        self._attribute_name = attribute_name
        self._current_state = FilterState.IGNORE

        # Label takes remaining space on the left
        label_width = rect.width - _BUTTONS_TOTAL_WIDTH - 4
        self._label = UILabel(
            relative_rect=pygame.Rect(rect.x, rect.y, label_width, rect.height),
            text=label,
            manager=manager,
            container=container,
        )

        # Three radio buttons on the right
        btn_x = rect.x + label_width + 4
        self._btn_yes = UIButton(
            relative_rect=pygame.Rect(btn_x, rect.y, _BTN_WIDTH, rect.height),
            text="Yes",
            manager=manager,
            container=container,
            object_id="@tri_state_radio",
        )
        btn_x += _BTN_WIDTH + _BTN_GAP
        self._btn_no = UIButton(
            relative_rect=pygame.Rect(btn_x, rect.y, _BTN_WIDTH, rect.height),
            text="No",
            manager=manager,
            container=container,
            object_id="@tri_state_radio",
        )
        btn_x += _BTN_WIDTH + _BTN_GAP
        self._btn_ignore = UIButton(
            relative_rect=pygame.Rect(btn_x, rect.y, _BTN_WIDTH, rect.height),
            text="Ign",
            manager=manager,
            container=container,
            object_id="@tri_state_radio",
        )

        self._update_visuals()

    @property
    def attribute_name(self) -> str:
        """The filter attribute this widget controls."""
        return self._attribute_name

    @property
    def current_state(self) -> FilterState:
        """Current tri-state value."""
        return self._current_state

    def set_state(self, state: FilterState) -> None:
        """Set the filter state and update button visuals."""
        self._current_state = state
        self._update_visuals()

    def check_pressed(self, element=None) -> Optional[FilterState]:
        """Check if a button was pressed. Return the new FilterState or None.

        Can be used two ways:
        - Polling (no args): checks each button's check_pressed() method
        - Event-based (element): checks if element matches one of our buttons
        """
        if element is not None:
            if element is self._btn_yes:
                return FilterState.YES
            if element is self._btn_no:
                return FilterState.NO
            if element is self._btn_ignore:
                return FilterState.IGNORE
            return None

        # Polling mode: check each button
        if self._btn_yes.check_pressed():
            return FilterState.YES
        if self._btn_no.check_pressed():
            return FilterState.NO
        if self._btn_ignore.check_pressed():
            return FilterState.IGNORE
        return None

    def kill(self) -> None:
        """Destroy all child widgets."""
        self._label.kill()
        self._btn_yes.kill()
        self._btn_no.kill()
        self._btn_ignore.kill()

    def _update_visuals(self) -> None:
        """Select the active button, unselect others."""
        buttons = {
            FilterState.YES: self._btn_yes,
            FilterState.NO: self._btn_no,
            FilterState.IGNORE: self._btn_ignore,
        }
        for state, btn in buttons.items():
            if state is self._current_state:
                btn.select()
            else:
                btn.unselect()
