"""Tag filter panel: tag buttons + active/excluded counter + Clear button.

Extracted from `renderer.py` by PROJ-309 sub-phase 3.3. Vertical positioning
depends on the category tree above it; orchestrator passes the post-tree y.

Viewmodel writes:
- ``viewmodel.tag_filter_rects`` — dict[str, pygame.Rect]
- ``viewmodel.tag_clear_rect`` — pygame.Rect | None
"""
from __future__ import annotations

import pygame

from game.ui.screens.test_lab import theme


class TagFilterPanel:
    """Renders the tag filter region below the category sidebar."""

    def __init__(
        self,
        small_font: pygame.font.Font,
        header_color: tuple,
        text_color: tuple,
        category_bg: tuple,
        border_color: tuple,
    ) -> None:
        self.small_font = small_font
        self.HEADER_COLOR = header_color
        self.TEXT_COLOR = text_color
        self.CATEGORY_BG = category_bg
        self.BORDER_COLOR = border_color

    def draw(
        self,
        screen: pygame.Surface,
        x: int,
        y: int,
        controller,
        registry,
        viewmodel,
    ) -> None:
        """Draw tag filter buttons for quick filtering.

        Caller passes ``y`` as the y-coordinate just below the category tree
        plus a 15px gap (matches the original ``tag_section_y = y + 15``).
        """
        # Header
        header_text = self.small_font.render("TAG FILTERS", True, self.HEADER_COLOR)
        screen.blit(header_text, (x, y))
        y += 25

        # Get all unique tags from registry
        all_tags = registry.get_all_tags()

        # Prioritize common filter tags at the top
        priority_tags = ['high-tick', 'precision', 'quick']
        sorted_tags = [t for t in priority_tags if t in all_tags]
        sorted_tags += [t for t in sorted(all_tags) if t not in priority_tags]

        # Limit display to avoid overcrowding
        display_tags = sorted_tags[:8]  # Show top 8 tags

        tag_filter_rects = {}
        mx, my = pygame.mouse.get_pos()

        for i, tag in enumerate(display_tags):
            # Create tag button
            btn_width = 95
            btn_height = 24
            col = i % 2
            row = i // 2
            btn_x = x + col * (btn_width + 5)
            btn_y = y + row * (btn_height + 4)

            rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)
            tag_filter_rects[tag] = rect

            # Determine state and color
            is_active = controller.ui_state.is_tag_active(tag)
            is_excluded = controller.ui_state.is_tag_excluded(tag)
            is_hovered = rect.collidepoint(mx, my)

            if is_excluded:
                bg_color = theme.TAG_EXCLUDED_BG
                border_color = theme.TAG_EXCLUDED_BORDER
                text_color = theme.TAG_EXCLUDED_TEXT
                prefix = "X "
            elif is_active:
                bg_color = theme.TAG_ACTIVE_BG
                border_color = theme.TAG_ACTIVE_BORDER
                text_color = theme.TAG_ACTIVE_TEXT
                prefix = "V "
            elif is_hovered:
                bg_color = theme.TAB_HOVER
                border_color = theme.TAG_NORMAL_BORDER
                text_color = self.TEXT_COLOR
                prefix = ""
            else:
                bg_color = self.CATEGORY_BG
                border_color = self.BORDER_COLOR
                text_color = theme.TAG_NORMAL_TEXT
                prefix = ""

            pygame.draw.rect(screen, bg_color, rect, border_radius=3)
            pygame.draw.rect(screen, border_color, rect, 1, border_radius=3)

            # Truncate tag text if needed
            display_tag = prefix + tag
            if len(display_tag) > 12:
                display_tag = display_tag[:11] + "..."
            tag_text = self.small_font.render(display_tag, True, text_color)
            screen.blit(tag_text, (rect.x + 4, rect.y + 4))

        # Store rects in viewmodel
        viewmodel.tag_filter_rects = tag_filter_rects

        # Show filter count if active
        active_count = len(controller.ui_state.get_active_tag_filters())
        excluded_count = len(controller.ui_state.get_excluded_tags())
        if active_count > 0 or excluded_count > 0:
            filter_y = y + ((len(display_tags) + 1) // 2) * 28 + 5
            if active_count > 0 and excluded_count > 0:
                filter_text = f"+{active_count} / -{excluded_count}"
            elif active_count > 0:
                filter_text = f"+{active_count} tags"
            else:
                filter_text = f"-{excluded_count} tags"

            # Clear filters button
            clear_rect = pygame.Rect(x, filter_y, 80, 20)
            is_clear_hovered = clear_rect.collidepoint(mx, my)
            clear_bg = theme.CLEAR_BUTTON_HOVER if is_clear_hovered else theme.CLEAR_BUTTON_BG
            pygame.draw.rect(screen, clear_bg, clear_rect, border_radius=3)
            pygame.draw.rect(screen, theme.CLEAR_BUTTON_BORDER, clear_rect, 1, border_radius=3)
            clear_text = self.small_font.render("Clear", True, theme.CLEAR_BUTTON_TEXT)
            screen.blit(clear_text, (clear_rect.x + 22, clear_rect.y + 3))

            # Store for click handling
            viewmodel.tag_clear_rect = clear_rect

            # Filter count display
            count_text = self.small_font.render(filter_text, True, theme.TEXT_DIM)
            screen.blit(count_text, (x + 90, filter_y + 3))
        else:
            viewmodel.tag_clear_rect = None
