"""Header panel: title + global seed-mode controls.

Extracted from `renderer.py` by PROJ-309 sub-phase 3.3.

Viewmodel writes:
- ``viewmodel.seed_mode_rects`` — dict[str, pygame.Rect]
- ``viewmodel.seed_input_rect`` — pygame.Rect | None
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from game.ui.screens.test_lab import theme
from game.core.config import DisplayConfig

if TYPE_CHECKING:
    pass

WIDTH, HEIGHT = DisplayConfig.DEFAULT_WIDTH, DisplayConfig.DEFAULT_HEIGHT


class HeaderPanel:
    """Renders the Combat Lab header (title + seed controls)."""

    def __init__(
        self,
        title_font: pygame.font.Font,
        body_font: pygame.font.Font,
        small_font: pygame.font.Font,
        header_color: tuple,
        text_color: tuple,
        category_bg: tuple,
        border_color: tuple,
    ) -> None:
        self.title_font = title_font
        self.body_font = body_font
        self.small_font = small_font
        self.HEADER_COLOR = header_color
        self.TEXT_COLOR = text_color
        self.CATEGORY_BG = category_bg
        self.BORDER_COLOR = border_color

    def draw(self, screen: pygame.Surface, controller, registry, viewmodel) -> None:
        """Draw the header with title and global seed controls."""
        title = self.title_font.render("COMBAT LAB - TEST VIEWER", True, self.HEADER_COLOR)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))

        # Draw seed controls on the right side of header
        self._draw_seed_controls(screen, controller, registry, viewmodel)

    def _draw_seed_controls(self, screen: pygame.Surface, controller, registry, viewmodel) -> None:
        """Draw global seed controls in the header area (upper right)."""
        mx, my = pygame.mouse.get_pos()

        # Position in upper right
        x = WIDTH - 450
        y = 15

        # Seed label
        seed_label = self.body_font.render("Seed Mode:", True, theme.TEXT_MUTED)
        screen.blit(seed_label, (x, y))

        # Seed mode buttons
        mode_x = x + 100
        btn_height = 24
        btn_spacing = 8

        current_mode = controller.ui_state.get_seed_mode()
        seed_mode_rects = {}

        modes = [
            ("random", "Random", 65),
            ("metadata", "Fixed", 55),
            ("custom", "Custom", 60)
        ]

        for mode_id, mode_label, btn_width in modes:
            rect = pygame.Rect(mode_x, y - 2, btn_width, btn_height)
            seed_mode_rects[mode_id] = rect

            is_active = current_mode == mode_id
            is_hovered = rect.collidepoint(mx, my)

            if is_active:
                bg_color = theme.SEED_BUTTON_ACTIVE
                border_color = theme.SEED_BUTTON_ACTIVE_BORDER
                text_color = theme.SEED_BUTTON_ACTIVE_TEXT
            elif is_hovered:
                bg_color = theme.TAB_HOVER
                border_color = theme.TAG_NORMAL_BORDER
                text_color = self.TEXT_COLOR
            else:
                bg_color = self.CATEGORY_BG
                border_color = self.BORDER_COLOR
                text_color = theme.TEXT_DIM

            pygame.draw.rect(screen, bg_color, rect, border_radius=3)
            pygame.draw.rect(screen, border_color, rect, 1, border_radius=3)

            mode_text = self.small_font.render(mode_label, True, text_color)
            text_x = rect.x + (btn_width - mode_text.get_width()) // 2
            screen.blit(mode_text, (text_x, rect.y + 4))

            mode_x += btn_width + btn_spacing

        # Store rects in viewmodel for input handler
        viewmodel.seed_mode_rects = seed_mode_rects

        # Show current seed value / input area
        seed_x = mode_x + 10
        custom_seed = controller.ui_state.get_custom_seed()
        selected_test_id = controller.ui_state.get_selected_test_id()

        if current_mode == "random":
            seed_text = "(new each run)"
            seed_color = theme.SEED_RANDOM
        elif current_mode == "metadata":
            # Show the metadata seed if we have a selected test
            if selected_test_id:
                scenario_info = registry.get_by_id(selected_test_id)
                if scenario_info:
                    seed_text = f"= {scenario_info['metadata'].seed}"
                else:
                    seed_text = "(select test)"
            else:
                seed_text = "(select test)"
            seed_color = theme.SEED_FIXED
        else:  # custom
            if custom_seed is not None:
                seed_text = f"= {custom_seed}"
                seed_color = theme.SEED_CUSTOM
            else:
                seed_text = "[click to enter]"
                seed_color = theme.SEED_CUSTOM_PENDING

        # Draw seed value/input area as clickable region for custom mode
        seed_surf = self.small_font.render(seed_text, True, seed_color)
        seed_rect = pygame.Rect(seed_x, y, max(seed_surf.get_width() + 10, 120), btn_height)

        if current_mode == "custom":
            # Make it look clickable
            is_hovered = seed_rect.collidepoint(mx, my)
            if is_hovered:
                pygame.draw.rect(screen, theme.SEED_INPUT_HOVER_BG, seed_rect, border_radius=3)
            pygame.draw.rect(screen, theme.SEED_INPUT_HOVER_BORDER, seed_rect, 1, border_radius=3)
            viewmodel.seed_input_rect = seed_rect
        else:
            viewmodel.seed_input_rect = None

        screen.blit(seed_surf, (seed_x + 5, y + 4))
