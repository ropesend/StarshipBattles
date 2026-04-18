"""PROJ-282 Phase 4: `BattleSetupRenderer`.

Orchestrates the three per-panel builders (left/center/right) + bottom
bar for `FleetBattleSetupScreen`. Owns panel-width layout math for the
2560×1600+ display targets.

The renderer doesn't own pygame_gui handles or the `UIManager` — those
stay on the screen until Phase 8 slims the screen to a thin shell. This
keeps Phase 4 a pure structural extraction with no behavior change.
"""
from __future__ import annotations

import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UIButton

from game.ui.screens.battle_setup.panels import (
    center_panel,
    left_panel,
    right_panel,
)


class BattleSetupRenderer:
    """Orchestrates panel construction for the battle setup screen.

    Methods:
      - `rebuild(screen)` — reset the `UIManager` and rebuild all panels +
        bottom bar. Called by `screen._rebuild_ui` on every state change.

    Design note (Phase 4): this renderer is stateless between calls. All
    pygame_gui element handles live on `screen` (transitional); Phase 8
    moves them onto a dedicated `RendererHandles` dataclass when the
    screen becomes a thin shell.
    """

    def rebuild(self, screen) -> None:
        """Rebuild all UI elements. Mutates `screen` in-place with handles."""
        if screen._ui_manager:
            screen._ui_manager.clear_and_reset()

        screen._ui_manager = pygame_gui.UIManager(
            (screen.screen_width, screen.screen_height)
        )

        # Layout math — panel widths.
        w = screen.screen_width
        h = screen.screen_height
        left_w = 250
        right_w = 280
        center_w = w - left_w - right_w
        bottom_h = 60

        left_panel.build(screen, left_w, h - bottom_h)
        center_panel.build(screen, left_w, center_w, h - bottom_h)
        right_panel.build(screen, left_w + center_w, right_w, h - bottom_h)
        self._build_bottom_bar(screen, w, h, bottom_h)
        screen._panels_built = True

    def _build_bottom_bar(self, screen, width: int, height: int, bar_height: int) -> None:
        """Build the bottom action-button bar (Start / Headless / Save / Load / Return)."""
        panel = UIPanel(
            relative_rect=pygame.Rect(0, height - bar_height, width, bar_height),
            manager=screen._ui_manager, object_id='#bottom_bar'
        )

        btn_w = 140
        spacing = 15
        buttons = [
            ("Start Battle", "_start_btn"),
            ("Start Headless", "_headless_btn"),
            ("Save Setup", "_save_btn"),
            ("Load Setup", "_load_btn"),
            ("Return", "_return_btn"),
        ]
        total = len(buttons) * btn_w + (len(buttons) - 1) * spacing
        x = (width - total) // 2

        for text, attr in buttons:
            btn = UIButton(
                pygame.Rect(x, 10, btn_w, 40), text,
                manager=screen._ui_manager, container=panel
            )
            setattr(screen, attr, btn)
            x += btn_w + spacing
