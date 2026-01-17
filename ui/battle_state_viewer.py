"""
Battle State Viewer - Side-by-side JSON viewer with diff highlighting.

Displays initial and final battle states in two independently scrollable columns
with visual highlighting of changed, added, and removed values.
"""
import pygame
import json
from typing import Optional, Tuple, Dict, Any


# Font constants
FONT_MAIN = 'Consolas'
FONT_MONO = 'Consolas'


class DiffResult:
    """Represents the diff status of a JSON path."""
    UNCHANGED = 'unchanged'
    CHANGED = 'changed'
    ADDED = 'added'
    REMOVED = 'removed'


# Keys to ignore in diff (always different between captures)
DIFF_IGNORE_KEYS = {'created_at'}


def compute_json_diff(initial: Any, final: Any, path: str = "") -> Dict[str, str]:
    """
    Compute differences between two JSON structures.

    Returns a dict mapping JSON paths to their diff status.
    Paths are like "ships.0.current_hp" or "tick_count".
    """
    diffs = {}

    if type(initial) != type(final):
        # Type changed - mark as changed
        diffs[path] = DiffResult.CHANGED
        return diffs

    if isinstance(initial, dict):
        all_keys = set(initial.keys()) | set(final.keys())
        for key in all_keys:
            # Skip keys that are always different (like timestamps)
            if key in DIFF_IGNORE_KEYS:
                continue
            child_path = f"{path}.{key}" if path else key
            if key not in initial:
                # Key added in final
                _mark_all_paths(final[key], child_path, DiffResult.ADDED, diffs)
            elif key not in final:
                # Key removed in final
                _mark_all_paths(initial[key], child_path, DiffResult.REMOVED, diffs)
            else:
                # Key exists in both - recurse
                child_diffs = compute_json_diff(initial[key], final[key], child_path)
                diffs.update(child_diffs)

    elif isinstance(initial, list):
        # For lists, compare by index
        max_len = max(len(initial), len(final))
        for i in range(max_len):
            child_path = f"{path}.{i}" if path else str(i)
            if i >= len(initial):
                _mark_all_paths(final[i], child_path, DiffResult.ADDED, diffs)
            elif i >= len(final):
                _mark_all_paths(initial[i], child_path, DiffResult.REMOVED, diffs)
            else:
                child_diffs = compute_json_diff(initial[i], final[i], child_path)
                diffs.update(child_diffs)

    else:
        # Primitive value
        if initial != final:
            diffs[path] = DiffResult.CHANGED

    return diffs


def _mark_all_paths(data: Any, path: str, status: str, diffs: Dict[str, str]):
    """Mark all paths in a data structure with the given status."""
    diffs[path] = status

    if isinstance(data, dict):
        for key, value in data.items():
            child_path = f"{path}.{key}"
            _mark_all_paths(value, child_path, status, diffs)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            child_path = f"{path}.{i}"
            _mark_all_paths(item, child_path, status, diffs)


class ScrollableJsonPanel:
    """Single scrollable panel displaying JSON content with diff highlighting."""

    def __init__(self, x: int, y: int, width: int, height: int, title: str, is_final: bool = False):
        """Initialize scrollable JSON panel."""
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.title = title
        self.is_final = is_final  # True for final state panel

        # Content
        self.json_lines = []  # List of (indent_level, text, color, bg_color) tuples
        self.scroll_offset = 0
        self.max_scroll = 0
        self.line_height = 18

        # Diff data
        self.diff_paths: Dict[str, str] = {}

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

        # Diff highlight colors (background)
        self.changed_bg = (60, 50, 20)        # Yellow-ish for changed
        self.added_bg = (20, 50, 30)          # Green-ish for added
        self.removed_bg = (50, 20, 20)        # Red-ish for removed

        # Diff highlight colors (text) - brighter versions
        self.changed_text = (255, 220, 100)   # Bright yellow for changed values
        self.added_text = (100, 255, 150)     # Bright green for added
        self.removed_text = (255, 120, 120)   # Bright red for removed

        # Scrollbar
        self.scrollbar_width = 12
        self.scrollbar_dragging = False
        self.drag_start_offset = 0

    def set_json_with_diff(self, json_str: Optional[str], diff_paths: Dict[str, str]):
        """
        Set JSON content with diff information.

        Args:
            json_str: JSON string to parse and display
            diff_paths: Dict mapping paths to diff status
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
        """
        Recursively format JSON data with diff highlighting.
        """
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
        """Handle mouse events. Returns True if event was handled."""
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
        """Draw the scrollable JSON panel with diff highlighting."""
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
        pygame.draw.rect(surface, (50, 50, 60),
                        (scrollbar_x, scrollbar_y, self.scrollbar_width, scrollbar_height),
                        border_radius=3)

        # Thumb
        thumb_rect = self._get_scrollbar_thumb_rect()
        thumb_color = (100, 100, 120) if not self.scrollbar_dragging else (120, 120, 140)
        pygame.draw.rect(surface, thumb_color, thumb_rect, border_radius=3)


class BattleStateViewer:
    """
    Full-screen overlay for viewing initial and final battle states with diff highlighting.

    Displays two independently scrollable JSON panels with visual diff markers:
    - Yellow highlight: Value changed
    - Green highlight: Value added (only in final)
    - Red highlight: Value removed (only in initial)
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
        self.footer_height = 80  # More space for legend

        # Calculate panel dimensions
        available_width = screen_width - 2 * self.margin - self.panel_gap
        panel_width = available_width // 2
        panel_height = screen_height - 2 * self.margin - self.header_height - self.footer_height

        # Create panels (with is_final flag for diff display)
        self.initial_panel = ScrollableJsonPanel(
            x=self.margin,
            y=self.margin + self.header_height,
            width=panel_width,
            height=panel_height,
            title="Initial State",
            is_final=False
        )

        self.final_panel = ScrollableJsonPanel(
            x=self.margin + panel_width + self.panel_gap,
            y=self.margin + self.header_height,
            width=panel_width,
            height=panel_height,
            title="Final State",
            is_final=True
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
        self.legend_font = pygame.font.SysFont(FONT_MAIN, 14)

        # Colors
        self.overlay_color = (0, 0, 0, 200)
        self.header_color = (255, 255, 255)
        self.button_color = (80, 80, 100)
        self.button_hover_color = (100, 100, 130)

        # State info
        self.test_id = None
        self.run_number = None

        # Stats
        self.diff_stats = {'changed': 0, 'added': 0, 'removed': 0}

    def show(self, initial_json: Optional[str], final_json: Optional[str],
             test_id: str = None, run_number: int = None):
        """
        Show the viewer with diff highlighting.

        Args:
            initial_json: JSON string for initial state
            final_json: JSON string for final state
            test_id: Test identifier for display
            run_number: Run number for display
        """
        self.visible = True
        self.test_id = test_id
        self.run_number = run_number

        # Compute diff between states
        diff_paths = {}
        self.diff_stats = {'changed': 0, 'added': 0, 'removed': 0}

        if initial_json and final_json:
            try:
                initial_data = json.loads(initial_json)
                final_data = json.loads(final_json)
                diff_paths = compute_json_diff(initial_data, final_data)

                # Count diff stats
                for status in diff_paths.values():
                    if status == DiffResult.CHANGED:
                        self.diff_stats['changed'] += 1
                    elif status == DiffResult.ADDED:
                        self.diff_stats['added'] += 1
                    elif status == DiffResult.REMOVED:
                        self.diff_stats['removed'] += 1

            except json.JSONDecodeError:
                pass

        # Set JSON with diff info
        self.initial_panel.set_json_with_diff(initial_json, diff_paths)
        self.final_panel.set_json_with_diff(final_json, diff_paths)

    def hide(self):
        """Hide the viewer."""
        self.visible = False

    def handle_resize(self, width: int, height: int):
        """Handle window resize."""
        self.screen_width = width
        self.screen_height = height

        available_width = width - 2 * self.margin - self.panel_gap
        panel_width = available_width // 2
        panel_height = height - 2 * self.margin - self.header_height - self.footer_height

        self.initial_panel.x = self.margin
        self.initial_panel.y = self.margin + self.header_height
        self.initial_panel.width = panel_width
        self.initial_panel.height = panel_height

        self.final_panel.x = self.margin + panel_width + self.panel_gap
        self.final_panel.y = self.margin + self.header_height
        self.final_panel.width = panel_width
        self.final_panel.height = panel_height

        self.close_button_rect = pygame.Rect(
            width - self.margin - 100,
            height - self.margin - 40,
            100,
            35
        )

        self.initial_panel.scroll_offset = 0
        self.final_panel.scroll_offset = 0

    def handle_event(self, event) -> bool:
        """Handle mouse and keyboard events."""
        if not self.visible:
            return False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.hide()
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.close_button_rect.collidepoint(event.pos):
                self.hide()
                return False

        if self.initial_panel.handle_event(event):
            return True
        if self.final_panel.handle_event(event):
            return True

        return True

    def draw(self, surface):
        """Draw the battle state viewer with legend."""
        if not self.visible:
            return

        # Semi-transparent overlay
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

        # Draw legend
        self._draw_legend(surface)

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

    def _draw_legend(self, surface):
        """Draw the diff legend at the bottom."""
        legend_y = self.screen_height - self.margin - 70

        # Legend items
        items = [
            ((60, 50, 20), (255, 220, 100), f"Changed ({self.diff_stats['changed']})"),
            ((20, 50, 30), (100, 255, 150), f"Added ({self.diff_stats['added']})"),
            ((50, 20, 20), (255, 120, 120), f"Removed ({self.diff_stats['removed']})"),
        ]

        total_width = sum(100 + self.legend_font.size(text)[0] for _, _, text in items) + 40
        start_x = (self.screen_width - total_width) // 2

        x = start_x
        for bg_color, text_color, label in items:
            # Color swatch
            swatch_rect = pygame.Rect(x, legend_y + 2, 20, 16)
            pygame.draw.rect(surface, bg_color, swatch_rect)
            pygame.draw.rect(surface, (100, 100, 100), swatch_rect, 1)

            # Label
            label_surf = self.legend_font.render(label, True, text_color)
            surface.blit(label_surf, (x + 28, legend_y))

            x += 28 + label_surf.get_width() + 30
