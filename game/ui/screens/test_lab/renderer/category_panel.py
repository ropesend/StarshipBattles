"""Category sidebar panel: collapsible group/category tree.

Extracted from `renderer.py` by PROJ-309 sub-phase 3.3. The original
`_draw_category_sidebar` called `_draw_tag_filters` directly so the tag
filter section knew where to start (vertical-layout coupling). The split
breaks this coupling: this panel's `draw(...)` returns its terminal-y so
the orchestrator can pass it to `TagFilterPanel.draw(...)`.

Viewmodel writes:
- ``viewmodel.group_header_rects`` — dict[str, pygame.Rect]
- ``viewmodel.category_rects`` — dict[str, pygame.Rect]
"""
from __future__ import annotations

from typing import List

import pygame

from game.ui.screens.test_lab import theme
from game.core.config import DisplayConfig

WIDTH, HEIGHT = DisplayConfig.DEFAULT_WIDTH, DisplayConfig.DEFAULT_HEIGHT


class CategoryPanel:
    """Renders the collapsible category tree sidebar."""

    def __init__(
        self,
        header_font: pygame.font.Font,
        body_font: pygame.font.Font,
        small_font: pygame.font.Font,
        header_color: tuple,
        text_color: tuple,
        selected_color: tuple,
        category_bg: tuple,
        panel_bg: tuple,
        border_color: tuple,
        category_width: int,
        header_height: int,
    ) -> None:
        self.header_font = header_font
        self.body_font = body_font
        self.small_font = small_font
        self.HEADER_COLOR = header_color
        self.TEXT_COLOR = text_color
        self.SELECTED_COLOR = selected_color
        self.CATEGORY_BG = category_bg
        self.PANEL_BG = panel_bg
        self.BORDER_COLOR = border_color
        self.category_width = category_width
        self.header_height = header_height

    def draw(
        self,
        screen: pygame.Surface,
        controller,
        registry,
        categories: List[str],
        viewmodel,
    ) -> int:
        """Draw the category selection sidebar as a collapsible tree.

        Returns the y-coordinate just below the rendered tree, so the caller
        can position the tag-filter section beneath it.
        """
        x = 20
        y = self.header_height + 20

        # Draw panel background
        panel_rect = pygame.Rect(x - 10, y - 10, self.category_width, HEIGHT - y - 100)
        pygame.draw.rect(screen, self.PANEL_BG, panel_rect, border_radius=5)
        pygame.draw.rect(screen, self.BORDER_COLOR, panel_rect, 2, border_radius=5)

        # Header
        header_text = self.header_font.render("CATEGORIES", True, self.HEADER_COLOR)
        screen.blit(header_text, (x, y - 5))
        y += 40

        selected_category = controller.ui_state.get_selected_category()
        selected_group = controller.ui_state.get_selected_group()
        category_hover = controller.ui_state.get_category_hover()
        all_scenarios = controller.all_scenarios

        # Store rects for input handler
        viewmodel.group_header_rects = {}
        viewmodel.category_rects = {}

        # "All Tests" option
        all_rect = pygame.Rect(x, y, 200, 36)
        if selected_category is None and selected_group is None:
            color = self.SELECTED_COLOR
        elif category_hover == "ALL":
            color = theme.TAB_HOVER
        else:
            color = self.CATEGORY_BG

        pygame.draw.rect(screen, color, all_rect, border_radius=3)
        pygame.draw.rect(screen, self.BORDER_COLOR, all_rect, 1, border_radius=3)
        all_text = self.body_font.render(f"All Tests ({len(all_scenarios)})", True, self.TEXT_COLOR)
        screen.blit(all_text, (all_rect.x + 10, all_rect.y + 8))
        y += 42

        # Group tree
        groups = registry.get_groups()
        group_header_color = (30, 30, 38)
        group_text_color = (170, 200, 240)
        expand_color = (120, 140, 170)

        for group in groups:
            group_count = registry.get_group_count(group)
            is_expanded = controller.ui_state.is_group_expanded(group)

            # Group header
            group_rect = pygame.Rect(x, y, 200, 32)
            viewmodel.group_header_rects[group] = group_rect

            if selected_group == group:
                bg = self.SELECTED_COLOR
            elif category_hover == f"GROUP:{group}":
                bg = theme.TAB_HOVER
            else:
                bg = group_header_color

            pygame.draw.rect(screen, bg, group_rect, border_radius=3)

            # Expand/collapse triangle
            arrow = "\u25BC" if is_expanded else "\u25B6"
            arrow_surf = self.small_font.render(arrow, True, expand_color)
            screen.blit(arrow_surf, (x + 6, y + 8))

            # Group name + count
            group_label = self.body_font.render(f"{group} ({group_count})", True, group_text_color)
            screen.blit(group_label, (x + 22, y + 7))
            y += 36

            # Child categories (if expanded)
            if is_expanded:
                child_categories = registry.get_categories_in_group(group)
                for cat in child_categories:
                    cat_count = len(registry.get_by_category(cat))
                    cat_rect = pygame.Rect(x + 18, y, 182, 30)
                    viewmodel.category_rects[cat] = cat_rect

                    if selected_category == cat:
                        cat_bg = self.SELECTED_COLOR
                    elif category_hover == cat:
                        cat_bg = theme.TAB_HOVER
                    else:
                        cat_bg = self.CATEGORY_BG

                    pygame.draw.rect(screen, cat_bg, cat_rect, border_radius=3)
                    cat_text = self.small_font.render(f"{cat} ({cat_count})", True, self.TEXT_COLOR)
                    screen.blit(cat_text, (cat_rect.x + 8, cat_rect.y + 7))
                    y += 33

        return y
