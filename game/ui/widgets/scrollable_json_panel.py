"""
Scrollable JSON Panel Widget - Displays JSON content with syntax highlighting and diff markers.

A standalone, reusable panel component that renders JSON data with:
- Syntax highlighting (keys, strings, numbers, booleans, null)
- Diff highlighting (changed, added, removed paths)
- Mouse wheel scrolling with visual scrollbar
- Scrollbar thumb dragging support

This widget is designed to be composed into larger screens like BattleStateViewer.
"""
import pygame
import json
from typing import Optional, Tuple, Dict

from game.ui.utils.json_diff import DiffResult
from game.ui.fonts import get_font, FONT_MONO
from game.ui.colors import (
    BORDER_LIGHT, TEXT_ITEM,
    JSON_BG, JSON_BORDER, JSON_TITLE_BG, JSON_TITLE_TEXT,
    JSON_KEY, JSON_STRING, JSON_NUMBER, JSON_BOOL, JSON_NULL, JSON_BRACKET,
    DIFF_CHANGED_BG, DIFF_CHANGED_TEXT, DIFF_ADDED_BG, DIFF_ADDED_TEXT,
    DIFF_REMOVED_BG, DIFF_REMOVED_TEXT, SCROLLBAR_TRACK, SCROLLBAR_THUMB_ACTIVE
)


class ScrollableJsonPanel:
    """
    Single scrollable panel displaying JSON content with diff highlighting.

    Renders JSON data with syntax highlighting and optional diff markers.
    Supports mouse wheel scrolling and scrollbar drag interaction.

    Attributes:
        x, y: Panel position
        width, height: Panel dimensions
        title: Header text displayed at top
        is_final: If True, shows ADDED items. If False, shows REMOVED items.
    """

    def __init__(self, x: int, y: int, width: int, height: int, title: str, is_final: bool = False):
        """
        Initialize scrollable JSON panel.

        Args:
            x: X position of panel
            y: Y position of panel
            width: Panel width
            height: Panel height
            title: Title text to display in header
            is_final: True for "final state" panel (shows added), False for "initial" (shows removed)
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.title = title
        self.is_final = is_final

        # Content
        self.json_lines = []  # List of (indent_level, text, color, bg_color) tuples
        self.scroll_offset = 0
        self.max_scroll = 0
        self.line_height = 18

        # Diff data
        self.diff_paths: Dict[str, str] = {}

        # Fonts
        self.title_font = get_font(18, FONT_MONO)
        self.content_font = get_font(13, FONT_MONO)

        # Colors
        self.bg_color = JSON_BG
        self.border_color = JSON_BORDER
        self.title_bg_color = JSON_TITLE_BG
        self.title_color = JSON_TITLE_TEXT
        self.text_color = TEXT_ITEM

        # JSON syntax colors
        self.key_color = JSON_KEY
        self.string_color = JSON_STRING
        self.number_color = JSON_NUMBER
        self.bool_color = JSON_BOOL
        self.null_color = JSON_NULL
        self.bracket_color = JSON_BRACKET

        # Diff highlight colors (background)
        self.changed_bg = DIFF_CHANGED_BG
        self.added_bg = DIFF_ADDED_BG
        self.removed_bg = DIFF_REMOVED_BG

        # Diff highlight colors (text) - brighter versions
        self.changed_text = DIFF_CHANGED_TEXT
        self.added_text = DIFF_ADDED_TEXT
        self.removed_text = DIFF_REMOVED_TEXT

        # Scrollbar
        self.scrollbar_width = 12
        self.scrollbar_dragging = False
        self.drag_start_offset = 0

    def set_json_with_diff(self, json_str: Optional[str], diff_paths: Dict[str, str]):
        """
        Set JSON content with diff information.

        Args:
            json_str: JSON string to parse and display
            diff_paths: Dict mapping paths to diff status (DiffResult constants)
        """
        self.scroll_offset = 0
        self.json_lines = []
        self.diff_paths = diff_paths

        if not json_str:
            self.max_scroll = 0
            return

        try:
            data = json.loads(json_str)
            self._format_json_with_diff(data, indent=0, path="")
        except json.JSONDecodeError as e:
            self.json_lines.append((0, f"Error parsing JSON: {e}", (255, 100, 100), None))
            for line in json_str.split('\n'):
                self.json_lines.append((0, line, self.text_color, None))

        # Calculate max scroll
        content_height = len(self.json_lines) * self.line_height
        visible_height = self.height - 40
        self.max_scroll = max(0, content_height - visible_height)

    def _get_diff_colors(self, path: str) -> Tuple[Optional[Tuple], Optional[Tuple]]:
        """
        Get text and background colors based on diff status.

        Returns (text_color_override, bg_color) or (None, None) if unchanged.
        """
        status = self.diff_paths.get(path)

        if status == DiffResult.CHANGED:
            return self.changed_text, self.changed_bg
        elif status == DiffResult.ADDED:
            if self.is_final:
                return self.added_text, self.added_bg
            else:
                return None, None  # Don't show added items in initial
        elif status == DiffResult.REMOVED:
            if not self.is_final:
                return self.removed_text, self.removed_bg
            else:
                return None, None  # Don't show removed items in final

        return None, None

    def _path_has_changes(self, path: str) -> bool:
        """Check if a path or any of its children have changes."""
        if path in self.diff_paths:
            return True
        # Check if any child path has changes
        path_prefix = path + "." if path else ""
        for diff_path in self.diff_paths:
            if diff_path.startswith(path_prefix):
                return True
        return False

    def _format_json_with_diff(self, data, indent: int, path: str, key_prefix: str = ""):
        """Recursively format JSON data with diff highlighting."""
        text_override, bg_color = self._get_diff_colors(path)

        if isinstance(data, dict):
            # Opening brace
            if key_prefix:
                line_text = f'{key_prefix}: {{'
                self.json_lines.append((indent, line_text, text_override or self.key_color, bg_color))
            else:
                self.json_lines.append((indent, '{', text_override or self.bracket_color, bg_color))

            items = list(data.items())
            for i, (k, v) in enumerate(items):
                child_path = f"{path}.{k}" if path else k

                if isinstance(v, (dict, list)):
                    self._format_json_with_diff(v, indent + 1, child_path, f'"{k}"')
                else:
                    comma = ',' if i < len(items) - 1 else ''
                    self._add_key_value_line_with_diff(indent + 1, k, v, comma, child_path)

            self.json_lines.append((indent, '}', text_override or self.bracket_color, bg_color))

        elif isinstance(data, list):
            # Opening bracket
            if key_prefix:
                line_text = f'{key_prefix}: ['
                self.json_lines.append((indent, line_text, text_override or self.key_color, bg_color))
            else:
                self.json_lines.append((indent, '[', text_override or self.bracket_color, bg_color))

            for i, item in enumerate(data):
                child_path = f"{path}.{i}" if path else str(i)

                if isinstance(item, (dict, list)):
                    self._format_json_with_diff(item, indent + 1, child_path)
                    # Add comma if not last
                    if i < len(data) - 1 and self.json_lines:
                        last = self.json_lines[-1]
                        self.json_lines[-1] = (last[0], last[1] + ',', last[2], last[3])
                else:
                    comma = ',' if i < len(data) - 1 else ''
                    self._add_value_line_with_diff(indent + 1, item, comma, child_path)

            self.json_lines.append((indent, ']', text_override or self.bracket_color, bg_color))

        else:
            # Primitive at root level
            self._add_value_line_with_diff(indent, data, '', path)

    def _add_key_value_line_with_diff(self, indent: int, key: str, value, comma: str, path: str):
        """Add a line with key: value format, with diff highlighting."""
        text_override, bg_color = self._get_diff_colors(path)

        key_str = f'"{key}": '
        value_str, value_color = self._format_value(value)

        # Override colors if this path has changes
        if text_override:
            value_color = text_override

        # Create line with mixed colors (color is None since colors are in the text tuple)
        self.json_lines.append((indent, (key_str, value_str + comma, self.key_color, value_color), None, bg_color))

    def _add_value_line_with_diff(self, indent: int, value, comma: str, path: str):
        """Add a line with just a value, with diff highlighting."""
        text_override, bg_color = self._get_diff_colors(path)

        value_str, value_color = self._format_value(value)

        if text_override:
            value_color = text_override

        self.json_lines.append((indent, value_str + comma, value_color, bg_color))

    def _format_value(self, value) -> Tuple[str, Tuple[int, int, int]]:
        """Format a primitive value and return (string, color)."""
        if value is None:
            return 'null', self.null_color
        elif isinstance(value, bool):
            return str(value).lower(), self.bool_color
        elif isinstance(value, (int, float)):
            return str(value), self.number_color
        elif isinstance(value, str):
            # Truncate very long strings
            if len(value) > 50:
                value = value[:47] + '...'
            return f'"{value}"', self.string_color
        else:
            return str(value), self.text_color

    def handle_event(self, event) -> bool:
        """
        Handle mouse events.

        Args:
            event: Pygame event to handle

        Returns:
            True if event was consumed, False otherwise
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            if not (self.x <= mx <= self.x + self.width and
                    self.y <= my <= self.y + self.height):
                return False

            if event.button == 1 and self._is_in_scrollbar(mx, my):
                self.scrollbar_dragging = True
                thumb_rect = self._get_scrollbar_thumb_rect()
                self.drag_start_offset = my - thumb_rect.y
                return True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.scrollbar_dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.scrollbar_dragging:
                mx, my = event.pos
                self._handle_scrollbar_drag(my)
                return True

        elif event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            if self.x <= mx <= self.x + self.width and self.y <= my <= self.y + self.height:
                self.scroll_offset -= event.y * 40
                self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))
                return True

        return False

    def _is_in_scrollbar(self, mx: int, my: int) -> bool:
        """Check if position is in scrollbar area."""
        scrollbar_x = self.x + self.width - self.scrollbar_width - 5
        return (scrollbar_x <= mx <= scrollbar_x + self.scrollbar_width and
                self.y + 35 <= my <= self.y + self.height - 5)

    def _get_scrollbar_thumb_rect(self) -> pygame.Rect:
        """Get the scrollbar thumb rectangle."""
        if self.max_scroll <= 0:
            return pygame.Rect(0, 0, 0, 0)

        scrollbar_x = self.x + self.width - self.scrollbar_width - 5
        scrollbar_y = self.y + 35
        scrollbar_height = self.height - 40

        content_height = len(self.json_lines) * self.line_height
        visible_ratio = min(1.0, (self.height - 40) / content_height) if content_height > 0 else 1.0
        thumb_height = max(30, int(scrollbar_height * visible_ratio))

        scroll_ratio = self.scroll_offset / self.max_scroll if self.max_scroll > 0 else 0
        thumb_y = scrollbar_y + int((scrollbar_height - thumb_height) * scroll_ratio)

        return pygame.Rect(scrollbar_x, thumb_y, self.scrollbar_width, thumb_height)

    def _handle_scrollbar_drag(self, my: int):
        """Handle scrollbar drag motion."""
        scrollbar_y = self.y + 35
        scrollbar_height = self.height - 40
        thumb_rect = self._get_scrollbar_thumb_rect()

        drag_y = my - self.drag_start_offset
        available_range = scrollbar_height - thumb_rect.height

        if available_range > 0:
            scroll_ratio = (drag_y - scrollbar_y) / available_range
            scroll_ratio = max(0, min(1, scroll_ratio))
            self.scroll_offset = int(scroll_ratio * self.max_scroll)

    def draw(self, surface):
        """
        Draw the scrollable JSON panel with diff highlighting.

        Args:
            surface: Pygame surface to draw on
        """
        # Background
        pygame.draw.rect(surface, self.bg_color,
                        (self.x, self.y, self.width, self.height), border_radius=5)
        pygame.draw.rect(surface, self.border_color,
                        (self.x, self.y, self.width, self.height), 2, border_radius=5)

        # Title bar
        pygame.draw.rect(surface, self.title_bg_color,
                        (self.x + 2, self.y + 2, self.width - 4, 30), border_radius=3)
        title_surf = self.title_font.render(self.title, True, self.title_color)
        surface.blit(title_surf, (self.x + 10, self.y + 6))

        # Content area with clipping
        content_y = self.y + 35
        content_height = self.height - 40
        clip_rect = pygame.Rect(self.x + 5, content_y, self.width - self.scrollbar_width - 15, content_height)
        surface.set_clip(clip_rect)

        # Draw JSON lines
        y = content_y - self.scroll_offset
        for line_data in self.json_lines:
            if y + self.line_height < content_y:
                y += self.line_height
                continue
            if y > self.y + self.height:
                break

            indent, text, color, bg_color = line_data
            x = self.x + 10 + indent * 20

            # Draw background highlight if present
            if bg_color:
                bg_rect = pygame.Rect(self.x + 5, y, self.width - self.scrollbar_width - 15, self.line_height)
                pygame.draw.rect(surface, bg_color, bg_rect)

            if isinstance(text, tuple):
                # Mixed color line (key: value)
                key_str, value_str, key_color, value_color = text
                key_surf = self.content_font.render(key_str, True, key_color)
                surface.blit(key_surf, (x, y))
                value_surf = self.content_font.render(value_str, True, value_color)
                surface.blit(value_surf, (x + key_surf.get_width(), y))
            else:
                # Single color line
                text_surf = self.content_font.render(text, True, color)
                surface.blit(text_surf, (x, y))

            y += self.line_height

        surface.set_clip(None)

        # Scrollbar
        if self.max_scroll > 0:
            self._draw_scrollbar(surface)

    def _draw_scrollbar(self, surface):
        """Draw the scrollbar."""
        scrollbar_x = self.x + self.width - self.scrollbar_width - 5
        scrollbar_y = self.y + 35
        scrollbar_height = self.height - 40

        # Track
        pygame.draw.rect(surface, SCROLLBAR_TRACK,
                        (scrollbar_x, scrollbar_y, self.scrollbar_width, scrollbar_height),
                        border_radius=3)

        # Thumb
        thumb_rect = self._get_scrollbar_thumb_rect()
        thumb_color = BORDER_LIGHT if not self.scrollbar_dragging else SCROLLBAR_THUMB_ACTIVE
        pygame.draw.rect(surface, thumb_color, thumb_rect, border_radius=3)
