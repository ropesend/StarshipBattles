"""PROJ-282 Phase 4: right-panel renderer for `FleetBattleSetupScreen`.

Builds the right-side "Available Designs" library panel. Mutates the
screen's `_design_buttons` handle list in-place.
"""
from __future__ import annotations

import pygame
from pygame_gui.elements import UIPanel, UIButton, UILabel


def build(screen, x: int, width: int, height: int) -> None:
    """Build the right panel. Mutates `screen` with pygame_gui handles."""
    panel = UIPanel(
        relative_rect=pygame.Rect(x, 0, width, height),
        manager=screen._ui_manager, object_id='#right_panel'
    )
    y = 10

    UILabel(pygame.Rect(10, y, width - 20, 28), "Available Designs",
            manager=screen._ui_manager, container=panel)
    y += 35

    screen._design_buttons = []
    for i, design in enumerate(screen.view_model.available_designs):
        name = design.get('name', '?')
        ship_class = design.get('ship_class', '')
        btn = UIButton(
            pygame.Rect(10, y, width - 20, 28),
            f"{name} ({ship_class})",
            manager=screen._ui_manager, container=panel
        )
        btn._design_index = i
        screen._design_buttons.append(btn)
        y += 30
