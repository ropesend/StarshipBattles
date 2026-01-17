"""
Battle State Viewer - Side-by-side JSON viewer for battle states.

Displays initial and final battle states in two independently scrollable columns
for analyzing test results in Combat Lab.
"""
import pygame
import json
from typing import Optional, Tuple


# Font constants
FONT_MAIN = 'Consolas'
FONT_MONO = 'Consolas'


class ScrollableJsonPanel:
    """Single scrollable panel displaying JSON content."""

    def __init__(self, x: int, y: int, width: int, height: int, title: str):
        """Initialize scrollable JSON panel."""
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.title = title

        # Content
        self.json_lines = []  # List of (indent_level, text, color) tuples
        self.scroll_offset = 0
        self.max_scroll = 0
        self.line_height = 18

        # Fonts
        self.title_font = pygame.font.SysFont(FONT_MAIN, 18)
        self.content_font = pygame.font.SysFont(FONT_MONO, 13)

        # Colors
        self.bg_color = (25, 25, 30)
        self.border_color = (80, 80, 100)
        self.title_bg_color = (40, 40, 50)
        self.title_color = (220, 220, 255)
        self.text_color = (200, 200, 200)

        # JSON syntax colors
        self.key_color = (156, 220, 254)      # Light blue for keys
        self.string_color = (206, 145, 120)   # Orange-brown for strings
        self.number_color = (181, 206, 168)   # Green for numbers
        self.bool_color = (86, 156, 214)      # Blue for booleans
        self.null_color = (86, 156, 214)      # Blue for null
        self.bracket_color = (180, 180, 180)  # Gray for brackets

        # Scrollbar
        self.scrollbar_width = 12
        self.scrollbar_dragging = False
        self.drag_start_offset = 0

    def set_json(self, json_str: Optional[str]):
        """
        Set JSON content to display.

        Args:
            json_str: JSON string to parse and display, or None to clear
        """
        self.scroll_offset = 0
        self.json_lines = []

        if not json_str:
            self.max_scroll = 0
            return

        try:
            # Parse and re-format for pretty display
            data = json.loads(json_str)
            self._format_json(data, indent=0)
        except json.JSONDecodeError as e:
            # Show raw content if parsing fails
            self.json_lines.append((0, f"Error parsing JSON: {e}", (255, 100, 100)))
            for line in json_str.split('\n'):
                self.json_lines.append((0, line, self.text_color))

        # Calculate max scroll
        content_height = len(self.json_lines) * self.line_height
        visible_height = self.height - 40  # Minus title bar
        self.max_scroll = max(0, content_height - visible_height)

    def _format_json(self, data, indent: int, key_prefix: str = ""):
        """
        Recursively format JSON data into colored lines.

        Args:
            data: Parsed JSON data
            indent: Current indentation level
            key_prefix: Key name if this is a dict value
        """
        if isinstance(data, dict):
            if key_prefix:
                self.json_lines.append((indent, f'{key_prefix}: {{', self.key_color))
            else:
                self.json_lines.append((indent, '{', self.bracket_color))

            items = list(data.items())
            for i, (k, v) in enumerate(items):
                if isinstance(v, (dict, list)):
                    self._format_json(v, indent + 1, f'"{k}"')
                else:
                    comma = ',' if i < len(items) - 1 else ''
                    self._add_key_value_line(indent + 1, k, v, comma)

            self.json_lines.append((indent, '}', self.bracket_color))

        elif isinstance(data, list):
            if key_prefix:
                self.json_lines.append((indent, f'{key_prefix}: [', self.key_color))
            else:
                self.json_lines.append((indent, '[', self.bracket_color))

            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    self._format_json(item, indent + 1)
                    # Add comma if not last
                    if i < len(data) - 1:
                        # Modify last line to add comma
                        if self.json_lines:
                            last = self.json_lines[-1]
                            self.json_lines[-1] = (last[0], last[1] + ',', last[2])
                else:
                    comma = ',' if i < len(data) - 1 else ''
                    self._add_value_line(indent + 1, item, comma)

            self.json_lines.append((indent, ']', self.bracket_color))

        else:
            # Primitive at root level (unusual but handle it)
            self._add_value_line(indent, data, '')

    def _add_key_value_line(self, indent: int, key: str, value, comma: str):
        """Add a line with key: value format."""
        key_str = f'"{key}": '
        value_str, value_color = self._format_value(value)
        # Create line with mixed colors (we'll render key and value separately)
        self.json_lines.append((indent, (key_str, value_str + comma, self.key_color, value_color), None))

    def _add_value_line(self, indent: int, value, comma: str):
        """Add a line with just a value (for arrays)."""
        value_str, value_color = self._format_value(value)
        self.json_lines.append((indent, value_str + comma, value_color))

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
        """Handle mouse events. Returns True if event was handled."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            # Check if click is in our area
            if not (self.x <= mx <= self.x + self.width and
                    self.y <= my <= self.y + self.height):
                return False

            # Check scrollbar click
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

        # Thumb size proportional to visible content
        content_height = len(self.json_lines) * self.line_height
        visible_ratio = min(1.0, (self.height - 40) / content_height) if content_height > 0 else 1.0
        thumb_height = max(30, int(scrollbar_height * visible_ratio))

        # Thumb position
        scroll_ratio = self.scroll_offset / self.max_scroll if self.max_scroll > 0 else 0
        thumb_y = scrollbar_y + int((scrollbar_height - thumb_height) * scroll_ratio)

        return pygame.Rect(scrollbar_x, thumb_y, self.scrollbar_width, thumb_height)

    def _handle_scrollbar_drag(self, my: int):
        """Handle scrollbar drag motion."""
        scrollbar_y = self.y + 35
        scrollbar_height = self.height - 40
        thumb_rect = self._get_scrollbar_thumb_rect()

        # Calculate new scroll position
        drag_y = my - self.drag_start_offset
        available_range = scrollbar_height - thumb_rect.height

        if available_range > 0:
            scroll_ratio = (drag_y - scrollbar_y) / available_range
            scroll_ratio = max(0, min(1, scroll_ratio))
            self.scroll_offset = int(scroll_ratio * self.max_scroll)

    def draw(self, surface):
        """Draw the scrollable JSON panel."""
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

            indent, text, color = line_data
            x = self.x + 10 + indent * 20

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
        pygame.draw.rect(surface, (50, 50, 60),
                        (scrollbar_x, scrollbar_y, self.scrollbar_width, scrollbar_height),
                        border_radius=3)

        # Thumb
        thumb_rect = self._get_scrollbar_thumb_rect()
        thumb_color = (100, 100, 120) if not self.scrollbar_dragging else (120, 120, 140)
        pygame.draw.rect(surface, thumb_color, thumb_rect, border_radius=3)


class BattleStateViewer:
    """
    Full-screen overlay for viewing initial and final battle states side-by-side.

    Displays two independently scrollable JSON panels with a close button.
    """

    def __init__(self, screen_width: int, screen_height: int):
        """Initialize battle state viewer."""
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.visible = False

        # Layout
        self.margin = 40
        self.panel_gap = 20
        self.header_height = 60
        self.footer_height = 50

        # Calculate panel dimensions
        available_width = screen_width - 2 * self.margin - self.panel_gap
        panel_width = available_width // 2
        panel_height = screen_height - 2 * self.margin - self.header_height - self.footer_height

        # Create panels
        self.initial_panel = ScrollableJsonPanel(
            x=self.margin,
            y=self.margin + self.header_height,
            width=panel_width,
            height=panel_height,
            title="Initial State"
        )

        self.final_panel = ScrollableJsonPanel(
            x=self.margin + panel_width + self.panel_gap,
            y=self.margin + self.header_height,
            width=panel_width,
            height=panel_height,
            title="Final State"
        )

        # Close button
        self.close_button_rect = pygame.Rect(
            screen_width - self.margin - 100,
            screen_height - self.margin - 40,
            100,
            35
        )

        # Fonts
        self.header_font = pygame.font.SysFont(FONT_MAIN, 24)
        self.button_font = pygame.font.SysFont(FONT_MAIN, 16)

        # Colors
        self.overlay_color = (0, 0, 0, 200)  # Semi-transparent black
        self.header_color = (255, 255, 255)
        self.button_color = (80, 80, 100)
        self.button_hover_color = (100, 100, 130)

        # State info
        self.test_id = None
        self.run_number = None

    def show(self, initial_json: Optional[str], final_json: Optional[str],
             test_id: str = None, run_number: int = None):
        """
        Show the viewer with the given battle states.

        Args:
            initial_json: JSON string for initial state (or None)
            final_json: JSON string for final state (or None)
            test_id: Test identifier for display
            run_number: Run number for display
        """
        self.visible = True
        self.test_id = test_id
        self.run_number = run_number
        self.initial_panel.set_json(initial_json)
        self.final_panel.set_json(final_json)

    def hide(self):
        """Hide the viewer."""
        self.visible = False

    def handle_resize(self, width: int, height: int):
        """Handle window resize."""
        self.screen_width = width
        self.screen_height = height

        # Recalculate layout
        available_width = width - 2 * self.margin - self.panel_gap
        panel_width = available_width // 2
        panel_height = height - 2 * self.margin - self.header_height - self.footer_height

        # Update panels
        self.initial_panel.x = self.margin
        self.initial_panel.y = self.margin + self.header_height
        self.initial_panel.width = panel_width
        self.initial_panel.height = panel_height

        self.final_panel.x = self.margin + panel_width + self.panel_gap
        self.final_panel.y = self.margin + self.header_height
        self.final_panel.width = panel_width
        self.final_panel.height = panel_height

        # Update close button
        self.close_button_rect = pygame.Rect(
            width - self.margin - 100,
            height - self.margin - 40,
            100,
            35
        )

        # Re-render JSON with new dimensions
        # (Need to re-set to recalculate scroll)
        # This would require storing the raw JSON - for now just reset scroll
        self.initial_panel.scroll_offset = 0
        self.final_panel.scroll_offset = 0

    def handle_event(self, event) -> bool:
        """
        Handle mouse and keyboard events.

        Returns:
            True if event was handled (viewer should stay open),
            False if viewer should be closed
        """
        if not self.visible:
            return False

        # ESC to close
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.hide()
            return False

        # Close button click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.close_button_rect.collidepoint(event.pos):
                self.hide()
                return False

        # Forward to panels
        if self.initial_panel.handle_event(event):
            return True
        if self.final_panel.handle_event(event):
            return True

        # Consume all other events while visible (modal behavior)
        return True

    def draw(self, surface):
        """Draw the battle state viewer overlay."""
        if not self.visible:
            return

        # Semi-transparent overlay background
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill(self.overlay_color)
        surface.blit(overlay, (0, 0))

        # Header
        header_text = "Battle State Comparison"
        if self.test_id:
            header_text = f"Battle States - {self.test_id}"
            if self.run_number:
                header_text += f" (Run #{self.run_number})"

        header_surf = self.header_font.render(header_text, True, self.header_color)
        header_x = (self.screen_width - header_surf.get_width()) // 2
        surface.blit(header_surf, (header_x, self.margin + 15))

        # Draw panels
        self.initial_panel.draw(surface)
        self.final_panel.draw(surface)

        # Close button
        mouse_pos = pygame.mouse.get_pos()
        button_hover = self.close_button_rect.collidepoint(mouse_pos)
        button_color = self.button_hover_color if button_hover else self.button_color

        pygame.draw.rect(surface, button_color, self.close_button_rect, border_radius=5)
        pygame.draw.rect(surface, (120, 120, 140), self.close_button_rect, 2, border_radius=5)

        button_text = self.button_font.render("Close (ESC)", True, (255, 255, 255))
        text_x = self.close_button_rect.x + (self.close_button_rect.width - button_text.get_width()) // 2
        text_y = self.close_button_rect.y + (self.close_button_rect.height - button_text.get_height()) // 2
        surface.blit(button_text, (text_x, text_y))
