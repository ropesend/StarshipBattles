"""Test list panel: scrollable list of test cards + scrollbar + Run-Tests button.

Extracted from `renderer.py` by PROJ-309 sub-phase 3.3.

Viewmodel writes:
- ``viewmodel.test_list_panel_rect`` — pygame.Rect (for scroll event handling)
- ``viewmodel.run_all_tests_btn_rect`` — pygame.Rect
- ``viewmodel.scroll_offset`` (via ``set_max_scroll``)
"""
from __future__ import annotations

from typing import Any, Dict

import pygame

from game.ui.screens.test_lab import theme
from game.core.config import DisplayConfig

from ._draw_helpers import draw_validation_flag

WIDTH, HEIGHT = DisplayConfig.DEFAULT_WIDTH, DisplayConfig.DEFAULT_HEIGHT


class TestListPanel:
    """Renders the scrollable test list."""

    def __init__(
        self,
        header_font: pygame.font.Font,
        body_font: pygame.font.Font,
        small_font: pygame.font.Font,
        header_color: tuple,
        text_color: tuple,
        selected_color: tuple,
        panel_bg: tuple,
        border_color: tuple,
        category_width: int,
        test_list_width: int,
        header_height: int,
    ) -> None:
        self.header_font = header_font
        self.body_font = body_font
        self.small_font = small_font
        self.HEADER_COLOR = header_color
        self.TEXT_COLOR = text_color
        self.SELECTED_COLOR = selected_color
        self.PANEL_BG = panel_bg
        self.BORDER_COLOR = border_color
        self.category_width = category_width
        self.test_list_width = test_list_width
        self.header_height = header_height

    def draw(
        self,
        screen: pygame.Surface,
        controller,
        filtered_scenarios: Dict[str, Any],
        viewmodel,
        executor,
    ) -> None:
        """Draw the test list panel with scrolling support."""
        x = 20 + self.category_width + 20
        y = self.header_height + 20

        # Draw panel background
        panel_rect = pygame.Rect(x - 10, y - 10, self.test_list_width, HEIGHT - y - 100)
        viewmodel.test_list_panel_rect = panel_rect  # Store for scroll event handling
        pygame.draw.rect(screen, self.PANEL_BG, panel_rect, border_radius=5)
        pygame.draw.rect(screen, self.BORDER_COLOR, panel_rect, 2, border_radius=5)

        # Header - always say "TESTS" for consistency
        header_text = self.header_font.render("TESTS", True, self.HEADER_COLOR)
        screen.blit(header_text, (x, y - 5))
        y += 40

        # Get filtered scenarios
        sorted_test_ids = sorted(filtered_scenarios.keys())

        # Draw "Run Tests" button
        mouse_pos = pygame.mouse.get_pos()
        btn_width = 120
        btn_height = 32
        run_all_btn_rect = pygame.Rect(
            x + self.test_list_width - btn_width - 30, y - 35, btn_width, btn_height
        )
        viewmodel.run_all_tests_btn_rect = run_all_btn_rect

        if executor.batch_running:
            # Show progress during batch execution
            progress_text = f"{executor.batch_current_index + 1}/{executor.batch_total}"
            btn_color = theme.BUTTON_PROGRESS_BG
            btn_border = theme.BUTTON_PROGRESS_BORDER
            text_color = theme.BUTTON_PROGRESS_TEXT
        else:
            btn_hover = run_all_btn_rect.collidepoint(mouse_pos)
            btn_color = theme.BUTTON_GREEN_HOVER if btn_hover else theme.BUTTON_GREEN
            btn_border = theme.BUTTON_GREEN_BORDER
            progress_text = "Run Tests"
            text_color = theme.BUTTON_GREEN_TEXT

        pygame.draw.rect(screen, btn_color, run_all_btn_rect, border_radius=4)
        pygame.draw.rect(screen, btn_border, run_all_btn_rect, 1, border_radius=4)
        btn_text = self.small_font.render(progress_text, True, text_color)
        text_rect = btn_text.get_rect(center=run_all_btn_rect.center)
        screen.blit(btn_text, text_rect)

        if not sorted_test_ids:
            no_tests_text = self.body_font.render("No tests available", True, theme.TEXT_DIM)
            screen.blit(no_tests_text, (x + 20, y + 20))
            return

        # Calculate scrolling dimensions
        item_height = 55
        content_height = len(sorted_test_ids) * item_height
        visible_height = panel_rect.height - 50  # Space for header
        max_scroll = max(0, content_height - visible_height)

        # Update viewmodel max_scroll (for clamping)
        viewmodel.set_max_scroll(max_scroll)
        scroll_offset = viewmodel.scroll_offset

        # Set clipping region for test items
        clip_rect = pygame.Rect(panel_rect.x, y, panel_rect.width, visible_height)
        screen.set_clip(clip_rect)

        selected_test_id = controller.ui_state.get_selected_test_id()
        test_hover = controller.ui_state.get_test_hover()

        # Draw test items with scroll offset
        for i, test_id in enumerate(sorted_test_ids):
            item_y = y + i * item_height - scroll_offset

            # Skip items outside visible area for performance
            if item_y + 50 < y or item_y > y + visible_height:
                continue

            scenario_info = filtered_scenarios[test_id]
            metadata = scenario_info['metadata']

            rect = pygame.Rect(x, item_y, 400, 50)

            # Determine color
            if selected_test_id == test_id:
                color = self.SELECTED_COLOR
            elif test_hover == test_id:
                color = theme.BG_ITEM_HOVER
            else:
                color = theme.BG_CONTENT

            pygame.draw.rect(screen, color, rect, border_radius=3)
            pygame.draw.rect(screen, self.BORDER_COLOR, rect, 1, border_radius=3)

            # Validation status flag (if available)
            flag_x = rect.x + rect.width - 30
            flag_y = rect.y + rect.height // 2  # Vertically centered
            draw_validation_flag(screen, self.small_font, flag_x, flag_y, scenario_info)

            # Test ID
            id_text = self.body_font.render(test_id, True, self.HEADER_COLOR)
            screen.blit(id_text, (rect.x + 10, rect.y + 5))

            # Test name
            name_text = self.small_font.render(metadata.name, True, self.TEXT_COLOR)
            screen.blit(name_text, (rect.x + 10, rect.y + 28))

        # Reset clipping
        screen.set_clip(None)

        # Draw scrollbar if needed
        if max_scroll > 0:
            self._draw_scrollbar(
                screen, panel_rect, y, visible_height, scroll_offset, max_scroll
            )

    def _draw_scrollbar(
        self,
        screen: pygame.Surface,
        panel_rect: pygame.Rect,
        content_y: int,
        visible_height: int,
        scroll_offset: int,
        max_scroll: int,
    ) -> None:
        """Draw scrollbar for the test list panel."""
        scrollbar_width = 8
        scrollbar_x = panel_rect.x + panel_rect.width - scrollbar_width - 5
        scrollbar_y = content_y
        scrollbar_height = visible_height

        # Draw track
        track_rect = pygame.Rect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height)
        pygame.draw.rect(screen, theme.SCROLLBAR_TRACK, track_rect, border_radius=4)

        # Calculate thumb size and position
        content_height = max_scroll + visible_height
        thumb_height = max(30, int(visible_height * visible_height / content_height))
        scroll_ratio = scroll_offset / max_scroll if max_scroll > 0 else 0
        thumb_y = scrollbar_y + int(scroll_ratio * (scrollbar_height - thumb_height))

        # Draw thumb
        thumb_rect = pygame.Rect(scrollbar_x, thumb_y, scrollbar_width, thumb_height)
        pygame.draw.rect(screen, theme.SCROLLBAR_THUMB, thumb_rect, border_radius=4)
