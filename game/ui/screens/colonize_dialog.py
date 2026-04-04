"""Colonization Dialog - Select population and cargo amounts to drop with colony.

Shows the fleet's capacity for each resource/population type with arrow buttons
to adjust how much to transfer to the new colony. Amounts are stored on the
COLONIZE order and applied at execution time (clamped to what's available).
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Dict, Callable, Tuple

import logging

import pygame
import pygame_gui
from pygame_gui.elements import UIWindow, UIButton, UILabel

logger = logging.getLogger(__name__)

# Resources in display order
RESOURCE_TYPES = [
    "metals", "organics", "vapors", "radioactives", "exotics",
    "fuel", "energy", "ammo",
]

RESOURCE_DISPLAY_NAMES = {
    "metals": "Metals", "organics": "Organics", "vapors": "Vapors",
    "radioactives": "Radioactives", "exotics": "Exotics",
    "fuel": "Fuel", "energy": "Energy", "ammo": "Ammo",
}

# Arrow increments: 4 per direction, each 10x the previous
ARROW_INCREMENTS = [1, 10, 100, 1000]
ARROW_LABELS_DEC = ["<", "<<", "<<<", "<<<<"]
ARROW_LABELS_INC = [">", ">>", ">>>", ">>>>"]


class ColonizeDialog(UIWindow):
    """Dialog for choosing population and cargo amounts to drop when colonizing.

    Callback-based: on confirm, calls on_confirm(population_amount, cargo_amounts)
    where population_amount is int and cargo_amounts is Dict[str, int].
    """

    ROW_HEIGHT = 32

    # Layout X positions
    NAME_X = 5
    NAME_W = 100
    AMOUNT_X = 110
    AMOUNT_W = 70
    CAPACITY_X = 185
    CAPACITY_W = 70
    ALL_BTN_X = 260
    ALL_BTN_W = 36
    DEC_ARROWS_X = 300
    INC_ARROWS_X = 440

    def __init__(
        self,
        relative_rect: pygame.Rect,
        manager: pygame_gui.UIManager,
        planet_name: str,
        passenger_capacity: int,
        cargo_capacities: Dict[str, int],
        on_confirm: Callable[[int, Dict[str, int]], None],
    ):
        """Initialize the colonize dialog.

        Args:
            relative_rect: Window position and size.
            manager: pygame_gui UIManager.
            planet_name: Name of planet being colonized (for title).
            passenger_capacity: Fleet's max passenger capacity.
            cargo_capacities: Dict of resource_type -> fleet capacity.
            on_confirm: Callback(population_amount, cargo_amounts).
        """
        super().__init__(
            relative_rect,
            manager,
            window_display_title=f"Colonize: {planet_name}",
            resizable=False,
        )

        self.on_confirm_callback = on_confirm
        self._amounts: Dict[str, int] = {}
        self._capacities: Dict[str, int] = {}
        self._amount_labels: Dict[str, UILabel] = {}
        self._widgets = []

        # Population row
        self._capacities['passengers'] = passenger_capacity
        self._amounts['passengers'] = passenger_capacity  # Default: drop all

        # Cargo rows
        for res in RESOURCE_TYPES:
            cap = cargo_capacities.get(res, 0)
            self._capacities[res] = cap
            self._amounts[res] = cap  # Default: drop all

        self._build_ui()

    def _build_ui(self):
        """Build all UI elements."""
        container = self.get_container()
        y = 10

        # Header row
        hdr = UILabel(
            relative_rect=pygame.Rect(self.NAME_X, y, self.NAME_W, self.ROW_HEIGHT),
            text="Resource",
            manager=self.ui_manager,
            container=container,
        )
        self._widgets.append(hdr)
        hdr2 = UILabel(
            relative_rect=pygame.Rect(self.AMOUNT_X, y, self.AMOUNT_W, self.ROW_HEIGHT),
            text="Drop",
            manager=self.ui_manager,
            container=container,
        )
        self._widgets.append(hdr2)
        hdr3 = UILabel(
            relative_rect=pygame.Rect(self.CAPACITY_X, y, self.CAPACITY_W, self.ROW_HEIGHT),
            text="Capacity",
            manager=self.ui_manager,
            container=container,
        )
        self._widgets.append(hdr3)
        y += self.ROW_HEIGHT + 5

        # Population row
        self._add_row(container, y, "passengers", "Population")
        y += self.ROW_HEIGHT

        # Separator
        y += 5

        # Cargo rows
        for res in RESOURCE_TYPES:
            if self._capacities.get(res, 0) > 0:
                display = RESOURCE_DISPLAY_NAMES.get(res, res.capitalize())
                self._add_row(container, y, res, display)
                y += self.ROW_HEIGHT

        y += 10

        # Confirm / Cancel buttons
        btn_w = 100
        btn_h = 32
        center_x = self.relative_rect.width // 2
        self.btn_confirm = UIButton(
            relative_rect=pygame.Rect(center_x - btn_w - 10, y, btn_w, btn_h),
            text="Confirm",
            manager=self.ui_manager,
            container=container,
        )
        self.btn_cancel = UIButton(
            relative_rect=pygame.Rect(center_x + 10, y, btn_w, btn_h),
            text="Cancel",
            manager=self.ui_manager,
            container=container,
        )

    def _add_row(self, container, y: int, key: str, display_name: str):
        """Add a row with name, amount, capacity, All button, and arrow buttons."""
        capacity = self._capacities.get(key, 0)

        # Name label
        name_lbl = UILabel(
            relative_rect=pygame.Rect(self.NAME_X, y, self.NAME_W, self.ROW_HEIGHT),
            text=display_name,
            manager=self.ui_manager,
            container=container,
        )
        self._widgets.append(name_lbl)

        # Amount label (editable via arrows)
        amount_lbl = UILabel(
            relative_rect=pygame.Rect(self.AMOUNT_X, y, self.AMOUNT_W, self.ROW_HEIGHT),
            text=str(self._amounts.get(key, 0)),
            manager=self.ui_manager,
            container=container,
        )
        self._widgets.append(amount_lbl)
        self._amount_labels[key] = amount_lbl

        # Capacity label
        cap_lbl = UILabel(
            relative_rect=pygame.Rect(self.CAPACITY_X, y, self.CAPACITY_W, self.ROW_HEIGHT),
            text=f"/ {capacity}",
            manager=self.ui_manager,
            container=container,
        )
        self._widgets.append(cap_lbl)

        # "All" button
        all_btn = UIButton(
            relative_rect=pygame.Rect(self.ALL_BTN_X, y, self.ALL_BTN_W, self.ROW_HEIGHT),
            text="All",
            manager=self.ui_manager,
            container=container,
        )
        all_btn._colonize_key = key
        all_btn._colonize_action = 'all'
        self._widgets.append(all_btn)

        # Decrease arrows (<<<< <<< << <)
        arrow_w = 32
        x = self.DEC_ARROWS_X
        for i, (label, inc) in enumerate(zip(reversed(ARROW_LABELS_DEC), reversed(ARROW_INCREMENTS))):
            btn = UIButton(
                relative_rect=pygame.Rect(x, y, arrow_w, self.ROW_HEIGHT),
                text=label,
                manager=self.ui_manager,
                container=container,
            )
            btn._colonize_key = key
            btn._colonize_action = 'dec'
            btn._colonize_delta = inc
            self._widgets.append(btn)
            x += arrow_w + 2

        # Increase arrows (> >> >>> >>>>)
        x = self.INC_ARROWS_X
        for i, (label, inc) in enumerate(zip(ARROW_LABELS_INC, ARROW_INCREMENTS)):
            btn = UIButton(
                relative_rect=pygame.Rect(x, y, arrow_w, self.ROW_HEIGHT),
                text=label,
                manager=self.ui_manager,
                container=container,
            )
            btn._colonize_key = key
            btn._colonize_action = 'inc'
            btn._colonize_delta = inc
            self._widgets.append(btn)
            x += arrow_w + 2

    def process_event(self, event: pygame.event.Event) -> bool:
        """Handle button clicks."""
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_confirm:
                self._on_confirm()
                return True
            elif event.ui_element == self.btn_cancel:
                self.kill()
                return True

            # Arrow / All buttons
            key = getattr(event.ui_element, '_colonize_key', None)
            action = getattr(event.ui_element, '_colonize_action', None)
            if key and action:
                capacity = self._capacities.get(key, 0)
                current = self._amounts.get(key, 0)

                if action == 'all':
                    self._amounts[key] = capacity
                elif action == 'inc':
                    delta = getattr(event.ui_element, '_colonize_delta', 1)
                    self._amounts[key] = min(current + delta, capacity)
                elif action == 'dec':
                    delta = getattr(event.ui_element, '_colonize_delta', 1)
                    self._amounts[key] = max(current - delta, 0)

                # Update label
                if key in self._amount_labels:
                    self._amount_labels[key].set_text(str(self._amounts[key]))
                return True

        return super().process_event(event)

    def _on_confirm(self):
        """Issue the colonize command with selected amounts."""
        population = self._amounts.get('passengers', 0)
        cargo = {res: self._amounts.get(res, 0) for res in RESOURCE_TYPES
                 if self._amounts.get(res, 0) > 0}

        self.on_confirm_callback(population, cargo)
        self.kill()
