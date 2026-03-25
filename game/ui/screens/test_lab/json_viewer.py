"""Scrollable JSON viewer component for Combat Lab UI.

Displays formatted JSON data with scrolling support.
"""

import json
import pygame

from game.ui.fonts import get_font
from game.ui.screens.test_lab import theme
from game.ui.widgets.scroll_state import ScrollState


class ScrollableJSONViewer:
    """Scrollable panel for displaying formatted JSON with syntax highlighting."""

    def __init__(self, x, y, width, height, title, json_data):
        """
        Initialize JSON viewer.

        Args:
            x, y: Top-left position
            width, height: Panel dimensions
            title: Panel title (e.g., "Ship: Attacker")
            json_data: Dictionary to display as JSON
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.title = title

        # Format JSON with 2-space indentation
        self.json_text = json.dumps(json_data, indent=2) if json_data else "{}"
        self.lines = self.json_text.split('\n')

        # Scrolling state (line-based: offset is line index)
        self.line_height = 18
        self.title_height = 30
        self.content_height = height - self.title_height
        self.visible_lines = max(1, self.content_height // self.line_height)
        self.scroll = ScrollState(
            content_height=len(self.lines),
            viewport_height=self.visible_lines,
            step=3,
        )

        # Fonts (match Test Details panel style)
        self.body_font = get_font(14)
        self.title_font = get_font(18)

        # Colors
        self.bg_color = theme.BG_CONTENT
        self.title_bg_color = theme.JSON_TITLE_BG
        self.text_color = theme.TEXT
        self.title_color = theme.TEXT_WHITE
        self.border_color = theme.BORDER_ACTIVE

    def update_json(self, json_data):
        """Update displayed JSON data."""
        self.json_text = json.dumps(json_data, indent=2) if json_data else "{}"
        self.lines = self.json_text.split('\n')
        self.scroll.content_height = len(self.lines)
        self.scroll.clamp()

    def handle_scroll(self, event):
        """Handle mouse wheel scrolling."""
        if event.type == pygame.MOUSEWHEEL:
            # Check if mouse is over this panel
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if (self.x <= mouse_x <= self.x + self.width and
                self.y <= mouse_y <= self.y + self.height):
                return self.scroll.handle_mousewheel(event)
        return False

    def draw(self, surface):
        """Draw the JSON viewer panel."""
        # Draw border
        pygame.draw.rect(surface, self.border_color,
                        (self.x, self.y, self.width, self.height), 2)

        # Draw title bar
        title_rect = (self.x + 2, self.y + 2, self.width - 4, self.title_height - 4)
        pygame.draw.rect(surface, self.title_bg_color, title_rect)

        title_surface = self.title_font.render(self.title, True, self.title_color)
        title_x = self.x + 10
        title_y = self.y + (self.title_height - title_surface.get_height()) // 2
        surface.blit(title_surface, (title_x, title_y))

        # Draw content background
        content_rect = (self.x + 2, self.y + self.title_height,
                       self.width - 4, self.content_height)
        pygame.draw.rect(surface, self.bg_color, content_rect)

        # Draw JSON lines (visible range only)
        start_line = self.scroll.offset
        end_line = min(start_line + self.visible_lines, len(self.lines))

        for i in range(start_line, end_line):
            line = self.lines[i]
            text_surface = self.body_font.render(line, True, self.text_color)

            text_x = self.x + 10
            text_y = self.y + self.title_height + ((i - start_line) * self.line_height) + 5

            surface.blit(text_surface, (text_x, text_y))

        # Draw scrollbar if needed
        if self.scroll.can_scroll:
            scrollbar_x = self.x + self.width - 15
            scrollbar_y = self.y + self.title_height + 5
            scrollbar_height = self.content_height - 10

            # Scrollbar track
            pygame.draw.rect(surface, theme.JSON_SCROLLBAR_TRACK,
                           (scrollbar_x, scrollbar_y, 10, scrollbar_height))

            # Scrollbar thumb
            thumb_height = max(20, int(scrollbar_height * self.visible_lines / len(self.lines)))
            thumb_y = scrollbar_y + int((scrollbar_height - thumb_height) * self.scroll.scroll_ratio)
            pygame.draw.rect(surface, theme.JSON_SCROLLBAR_THUMB,
                           (scrollbar_x, thumb_y, 10, thumb_height))
