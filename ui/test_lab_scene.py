import pygame
import os
import sys
import json
import time

from game.core.constants import WHITE, BLACK, BLUE, WIDTH, HEIGHT, FONT_MAIN
from game.core.json_utils import load_json
from ui.components import Button
from test_framework.runner import TestRunner
from test_framework.registry import TestRegistry
from test_framework.test_history import TestHistory
from simulation_tests.logging_config import get_logger

logger = get_logger(__name__)


class JSONPopup:
    """Popup window for displaying JSON data."""

    def __init__(self, title, json_data, screen_width, screen_height):
        """
        Create JSON popup.

        Args:
            title: Title for the popup
            json_data: Dictionary or string to display as JSON
            screen_width: Screen width
            screen_height: Screen height
        """
        self.title = title
        self.json_text = json.dumps(json_data, indent=2) if isinstance(json_data, dict) else str(json_data)
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Popup dimensions (80% of screen)
        self.width = int(screen_width * 0.8)
        self.height = int(screen_height * 0.8)
        self.x = (screen_width - self.width) // 2
        self.y = (screen_height - self.height) // 2

        # Fonts
        self.title_font = pygame.font.SysFont(FONT_MAIN, 24)
        self.body_font = pygame.font.SysFont('Courier New', 14)  # Monospace for JSON

        # Scrolling
        self.scroll_offset = 0
        self.line_height = 18
        self.lines = self.json_text.split('\n')

        # Close button
        self.close_button = Button(self.x + self.width - 120, self.y + 10, 100, 40, "Close", self.close)
        self.is_open = True

    def close(self):
        """Close the popup."""
        self.is_open = False

    def handle_event(self, event):
        """Handle user input."""
        # Handle close button
        self.close_button.handle_event(event)

        # Handle scrolling
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset -= event.y * 3
            self.scroll_offset = max(0, min(self.scroll_offset, len(self.lines) - 20))

        # Close on Escape
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.close()

    def draw(self, screen):
        """Draw the popup."""
        if not self.is_open:
            return

        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # Popup background
        popup_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, (30, 30, 35), popup_rect, border_radius=10)
        pygame.draw.rect(screen, (100, 100, 120), popup_rect, 3, border_radius=10)

        # Title
        title_surf = self.title_font.render(self.title, True, (150, 200, 255))
        screen.blit(title_surf, (self.x + 20, self.y + 15))

        # Close button
        self.close_button.draw(screen)

        # Content area
        content_y = self.y + 70
        content_height = self.height - 90
        max_visible_lines = content_height // self.line_height

        # Draw JSON lines (with scrolling)
        for i, line in enumerate(self.lines[self.scroll_offset:self.scroll_offset + max_visible_lines]):
            line_surf = self.body_font.render(line, True, (220, 220, 220))
            screen.blit(line_surf, (self.x + 20, content_y + i * self.line_height))

        # Scrollbar indicator (if needed)
        if len(self.lines) > max_visible_lines:
            scrollbar_height = max(30, int(content_height * (max_visible_lines / len(self.lines))))
            scrollbar_y = content_y + int(content_height * (self.scroll_offset / len(self.lines)))
            scrollbar_rect = pygame.Rect(self.x + self.width - 20, scrollbar_y, 10, scrollbar_height)
            pygame.draw.rect(screen, (100, 100, 120), scrollbar_rect, border_radius=5)


class ConfirmationDialog:
    """Dialog for confirming changes to test metadata."""

    def __init__(self, title, changes, screen_width, screen_height, on_confirm, on_cancel):
        """
        Create confirmation dialog.

        Args:
            title: Dialog title
            changes: List of dicts with 'field', 'old_value', 'new_value'
            screen_width: Screen width
            screen_height: Screen height
            on_confirm: Callback function when confirmed
            on_cancel: Callback function when canceled
        """
        self.title = title
        self.changes = changes
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel

        # Dialog dimensions (60% of screen, but smaller than JSON popup)
        self.width = min(800, int(screen_width * 0.6))
        self.height = min(600, int(screen_height * 0.6))
        self.x = (screen_width - self.width) // 2
        self.y = (screen_height - self.height) // 2

        # Fonts
        self.title_font = pygame.font.SysFont(FONT_MAIN, 24)
        self.body_font = pygame.font.SysFont(FONT_MAIN, 16)
        self.small_font = pygame.font.SysFont(FONT_MAIN, 14)

        # Buttons
        button_y = self.y + self.height - 60
        button_width = 120
        button_spacing = 20
        total_button_width = button_width * 2 + button_spacing
        button_start_x = self.x + (self.width - total_button_width) // 2

        self.confirm_button = Button(
            button_start_x, button_y, button_width, 40,
            "Confirm", self._handle_confirm
        )
        self.cancel_button = Button(
            button_start_x + button_width + button_spacing, button_y, button_width, 40,
            "Cancel", self._handle_cancel
        )

        self.is_open = True
        self.result = None  # Will be 'confirm' or 'cancel'

    def _handle_confirm(self):
        """User confirmed changes."""
        self.result = 'confirm'
        self.is_open = False
        if self.on_confirm:
            self.on_confirm()

    def _handle_cancel(self):
        """User canceled changes."""
        self.result = 'cancel'
        self.is_open = False
        if self.on_cancel:
            self.on_cancel()

    def handle_event(self, event):
        """Handle user input."""
        # Handle button clicks
        self.confirm_button.handle_event(event)
        self.cancel_button.handle_event(event)

        # Close on Escape
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._handle_cancel()

    def draw(self, screen):
        """Draw the confirmation dialog."""
        if not self.is_open:
            return

        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # Dialog background
        dialog_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, (30, 30, 35), dialog_rect, border_radius=10)
        pygame.draw.rect(screen, (100, 100, 120), dialog_rect, 3, border_radius=10)

        # Title
        title_surf = self.title_font.render(self.title, True, (255, 200, 100))
        screen.blit(title_surf, (self.x + 20, self.y + 15))

        # Description
        desc_y = self.y + 60
        desc_text = "The following changes will be made to the test metadata:"
        desc_surf = self.body_font.render(desc_text, True, (220, 220, 220))
        screen.blit(desc_surf, (self.x + 20, desc_y))

        # Changes list
        changes_y = desc_y + 40
        line_height = 25

        for i, change in enumerate(self.changes):
            change_y = changes_y + i * (line_height * 3 + 10)

            # Field name
            field_text = f"• {change['field']}:"
            field_surf = self.body_font.render(field_text, True, (150, 200, 255))
            screen.blit(field_surf, (self.x + 30, change_y))

            # Old value (strikethrough)
            old_text = f"  Old: {change['old_value']}"
            old_surf = self.small_font.render(old_text, True, (255, 100, 100))
            screen.blit(old_surf, (self.x + 50, change_y + line_height))

            # Draw strikethrough line over old value
            text_width = old_surf.get_width()
            pygame.draw.line(screen, (255, 100, 100),
                           (self.x + 50, change_y + line_height + 8),
                           (self.x + 50 + text_width, change_y + line_height + 8), 2)

            # New value
            new_text = f"  New: {change['new_value']}"
            new_surf = self.small_font.render(new_text, True, (100, 255, 150))
            screen.blit(new_surf, (self.x + 50, change_y + line_height * 2))

        # Buttons
        self.confirm_button.draw(screen)
        self.cancel_button.draw(screen)


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

        # Scrolling state
        self.scroll_offset = 0
        self.line_height = 18
        self.title_height = 30
        self.content_height = height - self.title_height
        self.visible_lines = max(1, self.content_height // self.line_height)
        self.max_scroll = max(0, len(self.lines) - self.visible_lines)

        # Fonts (match Test Details panel style)
        self.body_font = pygame.font.SysFont(FONT_MAIN, 14)
        self.title_font = pygame.font.SysFont(FONT_MAIN, 18)

        # Colors
        self.bg_color = (30, 30, 35)
        self.title_bg_color = (45, 45, 50)
        self.text_color = (220, 220, 220)
        self.title_color = (255, 255, 255)
        self.border_color = (100, 100, 120)

    def update_json(self, json_data):
        """Update displayed JSON data."""
        self.json_text = json.dumps(json_data, indent=2) if json_data else "{}"
        self.lines = self.json_text.split('\n')
        self.max_scroll = max(0, len(self.lines) - self.visible_lines)
        self.scroll_offset = min(self.scroll_offset, self.max_scroll)

    def handle_scroll(self, event):
        """Handle mouse wheel scrolling."""
        if event.type == pygame.MOUSEWHEEL:
            # Check if mouse is over this panel
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if (self.x <= mouse_x <= self.x + self.width and
                self.y <= mouse_y <= self.y + self.height):

                # Scroll up/down
                self.scroll_offset -= event.y * 3  # 3 lines per wheel tick
                self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))
                return True
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
        start_line = self.scroll_offset
        end_line = min(start_line + self.visible_lines, len(self.lines))

        for i in range(start_line, end_line):
            line = self.lines[i]
            text_surface = self.body_font.render(line, True, self.text_color)

            text_x = self.x + 10
            text_y = self.y + self.title_height + ((i - start_line) * self.line_height) + 5

            surface.blit(text_surface, (text_x, text_y))

        # Draw scrollbar if needed
        if self.max_scroll > 0:
            scrollbar_x = self.x + self.width - 15
            scrollbar_y = self.y + self.title_height + 5
            scrollbar_height = self.content_height - 10

            # Scrollbar track
            pygame.draw.rect(surface, (60, 60, 70),
                           (scrollbar_x, scrollbar_y, 10, scrollbar_height))

            # Scrollbar thumb
            thumb_height = max(20, int(scrollbar_height * self.visible_lines / len(self.lines)))
            thumb_y = scrollbar_y + int((scrollbar_height - thumb_height) * (self.scroll_offset / self.max_scroll))
            pygame.draw.rect(surface, (120, 120, 140),
                           (scrollbar_x, thumb_y, 10, thumb_height))


class ComponentDropdown:
    """Dropdown menu for selecting components from a ship's component list."""

    def __init__(self, x, y, width, height, component_ids, load_callback):
        """
        Initialize component dropdown.

        Args:
            x, y: Top-left position
            width, height: Dropdown dimensions (height is for closed state)
            component_ids: List of component IDs to choose from
            load_callback: Function(component_id) -> Dict, called when selection changes
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.component_ids = component_ids if component_ids else ["No components"]
        self.selected_index = 0
        self.is_expanded = False
        self.load_callback = load_callback

        # Fonts & Colors
        self.font = pygame.font.SysFont(FONT_MAIN, 16)
        self.bg_color = (50, 50, 60)
        self.selected_bg_color = (70, 70, 85)
        self.hover_bg_color = (60, 60, 75)
        self.text_color = (255, 255, 255)
        self.border_color = (100, 100, 120)

        self.hovered_index = -1

    def handle_click(self, event):
        """Handle mouse clicks on dropdown."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos

            # Click on closed dropdown header
            if not self.is_expanded:
                if (self.x <= mouse_x <= self.x + self.width and
                    self.y <= mouse_y <= self.y + self.height):
                    self.is_expanded = True
                    return True

            # Click on expanded dropdown
            else:
                # Click on header closes it
                if (self.x <= mouse_x <= self.x + self.width and
                    self.y <= mouse_y <= self.y + self.height):
                    self.is_expanded = False
                    return True

                # Click on option
                dropdown_height = self.height * len(self.component_ids)
                if (self.x <= mouse_x <= self.x + self.width and
                    self.y + self.height <= mouse_y <= self.y + self.height + dropdown_height):

                    option_index = (mouse_y - self.y - self.height) // self.height
                    if 0 <= option_index < len(self.component_ids):
                        self.selected_index = option_index
                        self.is_expanded = False
                        return True

                # Click outside closes dropdown
                else:
                    self.is_expanded = False
                    return True

        return False

    def handle_hover(self):
        """Track hovered option for visual feedback."""
        if not self.is_expanded:
            self.hovered_index = -1
            return

        mouse_x, mouse_y = pygame.mouse.get_pos()
        dropdown_height = self.height * len(self.component_ids)

        if (self.x <= mouse_x <= self.x + self.width and
            self.y + self.height <= mouse_y <= self.y + self.height + dropdown_height):
            self.hovered_index = (mouse_y - self.y - self.height) // self.height
        else:
            self.hovered_index = -1

    def get_selected_component_id(self):
        """Get currently selected component ID."""
        if 0 <= self.selected_index < len(self.component_ids):
            comp_id = self.component_ids[self.selected_index]
            return comp_id if comp_id != "No components" else None
        return None

    def draw(self, surface):
        """Draw the dropdown menu."""
        # Draw closed header
        header_rect = (self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, self.bg_color, header_rect)
        pygame.draw.rect(surface, self.border_color, header_rect, 2)

        # Display selected component ID
        selected_text = self.component_ids[self.selected_index] if self.component_ids else "No components"
        text_surface = self.font.render(selected_text, True, self.text_color)
        text_x = self.x + 10
        text_y = self.y + (self.height - text_surface.get_height()) // 2
        surface.blit(text_surface, (text_x, text_y))

        # Draw dropdown arrow
        arrow_x = self.x + self.width - 25
        arrow_y = self.y + self.height // 2
        arrow_points = [
            (arrow_x, arrow_y - 5),
            (arrow_x + 10, arrow_y - 5),
            (arrow_x + 5, arrow_y + 5)
        ] if not self.is_expanded else [
            (arrow_x, arrow_y + 5),
            (arrow_x + 10, arrow_y + 5),
            (arrow_x + 5, arrow_y - 5)
        ]
        pygame.draw.polygon(surface, self.text_color, arrow_points)

        # Draw expanded options
        if self.is_expanded:
            for i, comp_id in enumerate(self.component_ids):
                option_y = self.y + self.height + (i * self.height)
                option_rect = (self.x, option_y, self.width, self.height)

                # Background color
                if i == self.hovered_index:
                    bg_color = self.hover_bg_color
                elif i == self.selected_index:
                    bg_color = self.selected_bg_color
                else:
                    bg_color = self.bg_color

                pygame.draw.rect(surface, bg_color, option_rect)
                pygame.draw.rect(surface, self.border_color, option_rect, 1)

                # Option text
                option_surface = self.font.render(comp_id, True, self.text_color)
                option_x = self.x + 10
                option_text_y = option_y + (self.height - option_surface.get_height()) // 2
                surface.blit(option_surface, (option_x, option_text_y))


class ShipPanel:
    """Panel showing ship JSON only (full height like Test Details)."""

    def __init__(self, x, y, width, height, ship_info):
        """
        Initialize ship panel.

        Args:
            x, y: Top-left position
            width, height: Panel dimensions
            ship_info: Dict with 'role', 'ship_data'
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.ship_info = ship_info

        # Ship JSON viewer (full height)
        self.ship_viewer = ScrollableJSONViewer(
            x=x,
            y=y,
            width=width,
            height=height,
            title=f"Ship: {ship_info['role']}",
            json_data=ship_info['ship_data']
        )

    def handle_event(self, event):
        """Handle input events (scrolling)."""
        return self.ship_viewer.handle_scroll(event)

    def update(self):
        """Update hover states."""
        pass

    def draw(self, surface):
        """Draw the ship panel."""
        self.ship_viewer.draw(surface)


class ComponentPanel:
    """Panel showing component dropdown + component JSON (full height)."""

    def __init__(self, x, y, width, height, component_ids, load_component_callback):
        """
        Initialize component panel.

        Args:
            x, y: Top-left position
            width, height: Panel dimensions
            component_ids: List of component IDs
            load_component_callback: Function(component_id) -> Dict
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.load_component_callback = load_component_callback

        # Component dropdown at top
        dropdown_height = 40
        self.component_dropdown = ComponentDropdown(
            x=x + 10,
            y=y + 10,
            width=width - 20,
            height=dropdown_height,
            component_ids=component_ids,
            load_callback=load_component_callback
        )

        # Component JSON viewer below dropdown
        component_viewer_y = y + dropdown_height + 20
        component_viewer_height = height - dropdown_height - 30
        selected_comp_id = self.component_dropdown.get_selected_component_id()
        component_data = load_component_callback(selected_comp_id) if selected_comp_id else {}

        self.component_viewer = ScrollableJSONViewer(
            x=x,
            y=component_viewer_y,
            width=width,
            height=component_viewer_height,
            title="Component JSON",
            json_data=component_data
        )

    def handle_event(self, event):
        """Handle input events (scrolling, dropdown clicks)."""
        # Try dropdown first
        if self.component_dropdown.handle_click(event):
            # Selection changed - update component viewer
            selected_comp_id = self.component_dropdown.get_selected_component_id()
            if selected_comp_id:
                component_data = self.load_component_callback(selected_comp_id)
                if component_data:
                    self.component_viewer.update_json(component_data)
            return True

        # Try scrolling on component viewer
        if self.component_viewer.handle_scroll(event):
            return True

        return False

    def update(self):
        """Update hover states."""
        self.component_dropdown.handle_hover()

    def draw(self, surface):
        """Draw the component panel."""
        self.component_viewer.draw(surface)
        self.component_dropdown.draw(surface)  # Draw dropdown last so it's on top when expanded


class TestRunCard:
    """Card displaying a single test run (collapsed view only for selection)."""

    def __init__(self, x, y, width, run_record, run_number, is_latest=False):
        """
        Initialize test run card.

        Args:
            x, y: Top-left position
            width: Card width
            run_record: TestRunRecord instance
            run_number: Display number for this run
            is_latest: True if this is the most recent run
        """
        self.x = x
        self.y = y
        self.width = width
        self.run_record = run_record
        self.run_number = run_number
        self.is_latest = is_latest

        self.card_height = 80  # Fixed height (no expansion)
        self.is_selected = False

        # Colors
        self.bg_color = (35, 35, 40)
        self.bg_hover_color = (45, 45, 50)
        self.bg_selected_color = (55, 100, 150)  # Blue tint for selected
        self.latest_bg_color = (40, 45, 50)  # Slightly different for latest
        self.pass_color = (80, 255, 120)
        self.fail_color = (255, 80, 80)
        self.text_color = (220, 220, 220)
        self.border_color = (100, 100, 120)
        self.border_pass_color = (80, 255, 120)
        self.border_fail_color = (255, 80, 80)
        self.border_selected_color = (100, 150, 255)

        # Fonts
        self.title_font = pygame.font.SysFont(FONT_MAIN, 16)
        self.body_font = pygame.font.SysFont(FONT_MAIN, 14)
        self.small_font = pygame.font.SysFont(FONT_MAIN, 12)

        self.is_hovered = False

    def get_height(self):
        """Get card height (always collapsed)."""
        return self.card_height

    def handle_click(self, mx, my):
        """Check if card was clicked."""
        rect = pygame.Rect(self.x, self.y, self.width, self.card_height)
        if rect.collidepoint(mx, my):
            return True
        return False

    def handle_hover(self, mx, my):
        """Update hover state."""
        rect = pygame.Rect(self.x, self.y, self.width, self.card_height)
        self.is_hovered = rect.collidepoint(mx, my)

    def draw(self, surface):
        """Draw the test run card."""
        height = self.card_height

        # Background (show selection state)
        if self.is_selected:
            bg_color = self.bg_selected_color
        elif self.is_latest:
            bg_color = self.latest_bg_color
        elif self.is_hovered:
            bg_color = self.bg_hover_color
        else:
            bg_color = self.bg_color

        pygame.draw.rect(surface, bg_color, (self.x, self.y, self.width, height), border_radius=5)

        # Border (colored based on pass/fail, or selection)
        if self.is_selected:
            border_color = self.border_selected_color
        else:
            border_color = self.border_pass_color if self.run_record.passed else self.border_fail_color
        pygame.draw.rect(surface, border_color, (self.x, self.y, self.width, height), 2, border_radius=5)

        # Header (compact view)
        self._draw_header(surface)

    def _draw_header(self, surface):
        """Draw collapsed header with key metrics."""
        # Run number and timestamp
        timestamp_str = self.run_record.get_formatted_timestamp()
        header_text = f"Run #{self.run_number} - {timestamp_str}"
        if self.is_latest:
            header_text += " (Latest)"

        header_surf = self.title_font.render(header_text, True, self.text_color)
        surface.blit(header_surf, (self.x + 10, self.y + 10))

        # Pass/Fail indicator
        status_text = "✓ PASS" if self.run_record.passed else "✗ FAIL"
        status_color = self.pass_color if self.run_record.passed else self.fail_color
        status_surf = self.title_font.render(status_text, True, status_color)
        status_x = self.x + self.width - status_surf.get_width() - 10
        surface.blit(status_surf, (status_x, self.y + 10))

        # Key metric: hit rate if available
        metrics = self.run_record.metrics
        if 'hit_rate' in metrics and 'expected_hit_chance' in metrics:
            hit_rate = metrics['hit_rate']
            expected = metrics['expected_hit_chance']
            damage = metrics.get('damage_dealt', 0)
            ticks = self.run_record.ticks_run

            # Hit rate line
            hit_text = f"Hit Rate: {hit_rate:.1%} ({damage}/{ticks})"
            exp_text = f"Expected: {expected:.1%}"
            hit_surf = self.body_font.render(hit_text, True, self.text_color)
            surface.blit(hit_surf, (self.x + 10, self.y + 35))

            exp_surf = self.body_font.render(exp_text, True, (180, 180, 180))
            surface.blit(exp_surf, (self.x + 260, self.y + 35))

        # P-value and validation summary
        p_value = self.run_record.get_p_value()
        val_summary = self.run_record.validation_summary

        if p_value is not None:
            # Color code p-value (TOST: p < 0.05 is green/PASS, p >= 0.05 is red/FAIL)
            p_color = self.pass_color if p_value < 0.05 else self.fail_color
            p_text = f"P-value: {p_value:.4f}"
            p_surf = self.body_font.render(p_text, True, p_color)
            surface.blit(p_surf, (self.x + 10, self.y + 57))

        if val_summary:
            pass_count = val_summary.get('pass', 0)
            fail_count = val_summary.get('fail', 0)
            warn_count = val_summary.get('warn', 0)
            summary_text = f"{pass_count}P {fail_count}F {warn_count}W"
            summary_surf = self.body_font.render(summary_text, True, (180, 180, 180))
            summary_x = self.x + self.width - summary_surf.get_width() - 10
            surface.blit(summary_surf, (summary_x, self.y + 57))


class TestRunDetailsPanel:
    """Panel showing detailed information for selected test run."""

    def __init__(self, x, y, width, height):
        """Initialize test run details panel."""
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # Colors
        self.bg_color = (30, 30, 35)
        self.border_color = (80, 80, 90)
        self.text_color = (220, 220, 220)
        self.pass_color = (80, 255, 120)
        self.fail_color = (255, 80, 80)
        self.header_color = (150, 200, 255)
        self.button_color = (60, 100, 160)
        self.button_hover_color = (80, 120, 180)

        # Fonts
        self.title_font = pygame.font.SysFont(FONT_MAIN, 20)
        self.header_font = pygame.font.SysFont(FONT_MAIN, 16)
        self.body_font = pygame.font.SysFont(FONT_MAIN, 14)
        self.small_font = pygame.font.SysFont(FONT_MAIN, 12)

        self.selected_run = None
        self.scroll_offset = 0
        self.max_scroll = 0

        # View States button
        self.view_states_button_rect = None
        self.on_view_states = None  # Callback when button clicked

    def set_run(self, run_record, run_number):
        """Set the run to display details for."""
        self.selected_run = (run_record, run_number)
        self.scroll_offset = 0
        self._calculate_scroll()

    def clear(self):
        """Clear selected run."""
        self.selected_run = None
        self.scroll_offset = 0

    def _calculate_scroll(self):
        """Calculate max scroll based on content height."""
        if not self.selected_run:
            self.max_scroll = 0
            return

        run_record, _ = self.selected_run
        content_height = 150 + len(run_record.metrics) * 20 + 50 + len(run_record.validation_results) * 40
        visible_height = self.height - 20
        self.max_scroll = max(0, content_height - visible_height)

    def handle_event(self, event):
        """Handle scroll and click events."""
        if not self.selected_run:
            return False

        # Handle View States button click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.view_states_button_rect and self.view_states_button_rect.collidepoint(event.pos):
                run_record, run_number = self.selected_run
                if self.on_view_states and run_record.has_battle_states():
                    self.on_view_states(run_record, run_number)
                return True

        if event.type == pygame.MOUSEWHEEL:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if self.x <= mouse_x <= self.x + self.width and self.y <= mouse_y <= self.y + self.height:
                self.scroll_offset -= event.y * 20
                self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))
                return True
        return False

    def draw(self, surface):
        """Draw the test run details panel."""
        pygame.draw.rect(surface, self.bg_color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surface, self.border_color, (self.x, self.y, self.width, self.height), 2)

        if not self.selected_run:
            msg = self.body_font.render("Select a test run to view details", True, (150, 150, 150))
            msg_x = self.x + (self.width - msg.get_width()) // 2
            msg_y = self.y + self.height // 2
            surface.blit(msg, (msg_x, msg_y))
            return

        run_record, run_number = self.selected_run
        clip_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        surface.set_clip(clip_rect)

        y_offset = self.y + 10 - self.scroll_offset

        # Header
        timestamp_str = run_record.get_formatted_timestamp()
        header_text = f"Run #{run_number} - {timestamp_str}"
        header_surf = self.title_font.render(header_text, True, self.text_color)
        surface.blit(header_surf, (self.x + 10, y_offset))
        y_offset += 35

        # Status
        status_text = "✓ PASSED" if run_record.passed else "✗ FAILED"
        status_color = self.pass_color if run_record.passed else self.fail_color
        status_surf = self.title_font.render(status_text, True, status_color)
        surface.blit(status_surf, (self.x + 10, y_offset))

        # View States button (if battle states are available)
        self.view_states_button_rect = None
        if run_record.has_battle_states():
            button_width = 110
            button_height = 26
            button_x = self.x + self.width - button_width - 15
            button_y = y_offset - 5 + self.scroll_offset  # Account for scroll in positioning

            # Only show button if it's in the visible area
            if button_y >= self.y and button_y + button_height <= self.y + self.height:
                self.view_states_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

                mouse_pos = pygame.mouse.get_pos()
                is_hovered = self.view_states_button_rect.collidepoint(mouse_pos)
                btn_color = self.button_hover_color if is_hovered else self.button_color

                pygame.draw.rect(surface, btn_color, self.view_states_button_rect, border_radius=4)
                pygame.draw.rect(surface, (100, 130, 180), self.view_states_button_rect, 1, border_radius=4)

                btn_text = self.small_font.render("View States", True, (255, 255, 255))
                text_x = button_x + (button_width - btn_text.get_width()) // 2
                text_y = button_y + (button_height - btn_text.get_height()) // 2
                surface.blit(btn_text, (text_x, text_y))

        y_offset += 40

        # Metrics
        metrics_title = self.header_font.render("Test Metrics", True, self.header_color)
        surface.blit(metrics_title, (self.x + 10, y_offset))
        y_offset += 25

        for key, value in run_record.metrics.items():
            if key not in ['validation_results', 'validation_summary']:
                if isinstance(value, float):
                    value_str = f"{value:.1%}" if 0 < value < 1 else f"{value:.2f}"
                else:
                    value_str = str(value)
                display_key = key.replace('_', ' ').title()
                metric_text = f"  {display_key}: {value_str}"
                metric_surf = self.small_font.render(metric_text, True, self.text_color)
                surface.blit(metric_surf, (self.x + 15, y_offset))
                y_offset += 20

        y_offset += 10

        # Validation Results
        if run_record.validation_results:
            val_title = self.header_font.render("Validation Results", True, self.header_color)
            surface.blit(val_title, (self.x + 10, y_offset))
            y_offset += 25

            for vr in run_record.validation_results:
                status = vr['status']
                name = vr['name']
                expected = vr.get('expected')
                actual = vr.get('actual')
                p_value = vr.get('p_value')

                if status == 'PASS':
                    color, symbol = self.pass_color, "✓"
                elif status == 'FAIL':
                    color, symbol = self.fail_color, "✗"
                else:
                    color, symbol = (255, 200, 100), "⚠"

                val_line = f"  {symbol} {name}"
                val_surf = self.small_font.render(val_line, True, color)
                surface.blit(val_surf, (self.x + 15, y_offset))
                y_offset += 18

                if expected is not None or actual is not None or p_value is not None:
                    details = []
                    if expected is not None:
                        details.append(f"Exp: {expected:.1%}" if isinstance(expected, float) and 0 < expected < 1 else f"Exp: {expected}")
                    if actual is not None:
                        details.append(f"Act: {actual:.1%}" if isinstance(actual, float) and 0 < actual < 1 else f"Act: {actual}")
                    if p_value is not None:
                        details.append(f"p={p_value:.4f}")
                    detail_line = "     " + ", ".join(details)
                    detail_surf = self.small_font.render(detail_line, True, (160, 160, 160))
                    surface.blit(detail_surf, (self.x + 15, y_offset))
                    y_offset += 20

        surface.set_clip(None)
        if self.max_scroll > 0:
            self._draw_scrollbar(surface)

    def _draw_scrollbar(self, surface):
        """Draw scrollbar indicator."""
        visible_height = self.height
        total_content_height = visible_height + self.max_scroll
        scrollbar_width = 8
        scrollbar_x = self.x + self.width - scrollbar_width - 5
        scrollbar_track_y = self.y + 5
        scrollbar_track_height = visible_height - 10
        thumb_height = max(30, int(visible_height * (visible_height / total_content_height)))
        thumb_y = scrollbar_track_y + int((self.scroll_offset / self.max_scroll) * (scrollbar_track_height - thumb_height))
        pygame.draw.rect(surface, (100, 100, 120), (scrollbar_x, thumb_y, scrollbar_width, thumb_height), border_radius=4)


class ResultsPanel:
    """Panel showing test run history for selected test."""

    def __init__(self, x, y, width, height, test_history):
        """
        Initialize results panel.

        Args:
            x, y: Top-left position
            width, height: Panel dimensions
            test_history: TestHistory instance
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.test_history = test_history

        self.current_test_id = None
        self.run_cards = []
        self.scroll_offset = 0
        self.max_scroll = 0
        self.selected_card_index = None
        self.details_panel = None  # Reference to TestRunDetailsPanel

        # Fonts
        self.title_font = pygame.font.SysFont(FONT_MAIN, 20)
        self.body_font = pygame.font.SysFont(FONT_MAIN, 14)
        self.small_font = pygame.font.SysFont(FONT_MAIN, 12)

        # Colors
        self.bg_color = (30, 30, 35)
        self.border_color = (100, 100, 120)
        self.title_color = (255, 255, 255)
        self.button_color = (60, 120, 200)
        self.button_hover_color = (80, 140, 220)

        # Buttons
        self.clear_test_button_rect = None
        self.clear_all_button_rect = None

    def set_details_panel(self, details_panel):
        """Set reference to details panel for displaying selected run."""
        self.details_panel = details_panel

    def set_test(self, test_id):
        """Update panel to show runs for specific test."""
        self.current_test_id = test_id
        self.scroll_offset = 0
        self.selected_card_index = None

        # Clear details panel
        if self.details_panel:
            self.details_panel.clear()

        # Create cards for all runs (newest first)
        runs = self.test_history.get_runs(test_id)
        self.run_cards = []

        y_offset = 90  # Space for header
        for i, run in enumerate(reversed(runs)):  # Newest first
            card = TestRunCard(
                x=self.x + 10,
                y=self.y + y_offset,
                width=self.width - 20,
                run_record=run,
                run_number=len(runs) - i,
                is_latest=(i == 0)
            )
            self.run_cards.append(card)
            y_offset += card.get_height() + 10

        # Calculate max scroll
        self._recalculate_scroll()

    def _recalculate_scroll(self):
        """Recalculate maximum scroll offset."""
        if not self.run_cards:
            self.max_scroll = 0
            return

        # Calculate total content height
        total_height = 90  # Header
        for card in self.run_cards:
            total_height += card.get_height() + 10

        # Max scroll is content height - visible height
        visible_height = self.height - 10
        self.max_scroll = max(0, total_height - visible_height)

    def handle_event(self, event):
        """Handle mouse events."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            # Check clear buttons
            if self.clear_test_button_rect and self.clear_test_button_rect.collidepoint(mx, my):
                if self.current_test_id:
                    self.test_history.clear_test(self.current_test_id)
                    self.set_test(self.current_test_id)  # Refresh display
                return True

            if self.clear_all_button_rect and self.clear_all_button_rect.collidepoint(mx, my):
                self.test_history.clear_all()
                self.set_test(self.current_test_id)  # Refresh display
                return True

            # Check card clicks (accounting for scroll)
            for i, card in enumerate(self.run_cards):
                adjusted_my = my + self.scroll_offset
                if card.handle_click(mx, adjusted_my):
                    # Update selection
                    self.selected_card_index = i
                    # Update all cards' selection state
                    for j, c in enumerate(self.run_cards):
                        c.is_selected = (j == i)
                    # Update details panel
                    if self.details_panel:
                        self.details_panel.set_run(card.run_record, card.run_number)
                    return True

        if event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            if self.x <= mx <= self.x + self.width and self.y <= my <= self.y + self.height:
                self.scroll_offset -= event.y * 20
                self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))
                return True

        return False

    def update(self):
        """Update hover states."""
        mx, my = pygame.mouse.get_pos()

        # Update card hover states (accounting for scroll)
        adjusted_my = my + self.scroll_offset
        for card in self.run_cards:
            card.handle_hover(mx, adjusted_my)

    def draw(self, surface):
        """Draw the results panel."""
        # Draw background
        pygame.draw.rect(surface, self.bg_color,
                        (self.x, self.y, self.width, self.height), border_radius=5)
        pygame.draw.rect(surface, self.border_color,
                        (self.x, self.y, self.width, self.height), 2, border_radius=5)

        # Draw header
        self._draw_header(surface)

        # Draw cards with scrolling and clipping
        clip_rect = pygame.Rect(self.x, self.y + 90, self.width, self.height - 90)
        surface.set_clip(clip_rect)

        for card in self.run_cards:
            # Adjust Y position for scrolling
            card_y = card.y - self.scroll_offset
            if self._is_card_visible(card_y, card.get_height()):
                # Temporarily adjust position for drawing
                original_y = card.y
                card.y = card_y
                card.draw(surface)
                card.y = original_y  # Restore original position

        surface.set_clip(None)

        # Draw scrollbar
        if self.max_scroll > 0:
            self._draw_scrollbar(surface)

    def _draw_header(self, surface):
        """Draw panel header."""
        # Title
        title_text = "Test Run History"
        title_surf = self.title_font.render(title_text, True, self.title_color)
        surface.blit(title_surf, (self.x + 10, self.y + 10))

        # Run count
        if self.current_test_id:
            run_count = self.test_history.get_run_count(self.current_test_id)
            count_text = f"{run_count} run{'s' if run_count != 1 else ''}"
            count_surf = self.body_font.render(count_text, True, (180, 180, 180))
            surface.blit(count_surf, (self.x + 10, self.y + 38))

        # Clear buttons
        button_y = self.y + 60
        button_height = 22
        button_spacing = 5

        # Clear This Test button
        button1_width = 110
        self.clear_test_button_rect = pygame.Rect(self.x + 10, button_y, button1_width, button_height)
        mouse_pos = pygame.mouse.get_pos()
        button1_hover = self.clear_test_button_rect.collidepoint(mouse_pos)
        button1_color = self.button_hover_color if button1_hover else self.button_color

        pygame.draw.rect(surface, button1_color, self.clear_test_button_rect, border_radius=3)
        button1_text = self.small_font.render("Clear This Test", True, (255, 255, 255))
        text1_x = self.clear_test_button_rect.x + (button1_width - button1_text.get_width()) // 2
        text1_y = self.clear_test_button_rect.y + (button_height - button1_text.get_height()) // 2
        surface.blit(button1_text, (text1_x, text1_y))

        # Clear All button
        button2_width = 80
        button2_x = self.x + 10 + button1_width + button_spacing
        self.clear_all_button_rect = pygame.Rect(button2_x, button_y, button2_width, button_height)
        button2_hover = self.clear_all_button_rect.collidepoint(mouse_pos)
        button2_color = self.button_hover_color if button2_hover else self.button_color

        pygame.draw.rect(surface, button2_color, self.clear_all_button_rect, border_radius=3)
        button2_text = self.small_font.render("Clear All", True, (255, 255, 255))
        text2_x = self.clear_all_button_rect.x + (button2_width - button2_text.get_width()) // 2
        text2_y = self.clear_all_button_rect.y + (button_height - button2_text.get_height()) // 2
        surface.blit(button2_text, (text2_x, text2_y))

    def _is_card_visible(self, card_y, card_height):
        """Check if card is visible in viewport."""
        visible_top = self.y + 90
        visible_bottom = self.y + self.height

        card_top = card_y
        card_bottom = card_y + card_height

        # Card is visible if it overlaps with visible area
        return card_bottom > visible_top and card_top < visible_bottom

    def _draw_scrollbar(self, surface):
        """Draw scrollbar indicator."""
        visible_height = self.height - 90
        total_content_height = visible_height + self.max_scroll

        # Scrollbar dimensions
        scrollbar_width = 8
        scrollbar_x = self.x + self.width - scrollbar_width - 5
        scrollbar_track_y = self.y + 90
        scrollbar_track_height = visible_height

        # Calculate thumb size and position
        thumb_height = max(30, int(visible_height * (visible_height / total_content_height)))
        thumb_y = scrollbar_track_y + int((self.scroll_offset / self.max_scroll) * (scrollbar_track_height - thumb_height))

        # Draw thumb
        pygame.draw.rect(surface, (100, 100, 120),
                        (scrollbar_x, thumb_y, scrollbar_width, thumb_height),
                        border_radius=4)


class TestLabScene:
    """
    Combat Lab UI - Enhanced with TestRegistry and rich metadata display.

    Layout:
    - Left: Category sidebar (220px wide)
    - Center: Test list (420px wide)
    - Right: Metadata panel (540px wide)
    """

    # Color scheme
    BG_COLOR = (20, 20, 25)
    PANEL_BG = (25, 25, 30)
    BORDER_COLOR = (80, 80, 90)
    TEXT_COLOR = (220, 220, 220)
    HEADER_COLOR = (100, 200, 255)
    SELECTED_COLOR = (0, 100, 200)
    HOVER_COLOR = (150, 150, 150)
    CATEGORY_BG = (35, 35, 40)

    def __init__(self, game):
        self.game = game

        # Fonts
        self.title_font = pygame.font.SysFont(FONT_MAIN, 48)
        self.header_font = pygame.font.SysFont(FONT_MAIN, 24)
        self.body_font = pygame.font.SysFont(FONT_MAIN, 18)
        self.small_font = pygame.font.SysFont(FONT_MAIN, 14)

        # Initialize controller (handles all business logic)
        from test_framework.services.test_lab_controller import TestLabUIController
        self.registry = TestRegistry()
        self.test_history = TestHistory()
        self.controller = TestLabUIController(game, self.registry, self.test_history)

        # Get categories for sidebar
        self.categories = self.registry.get_categories()

        # Layout dimensions
        self.category_width = 220
        self.test_list_width = 420
        self.metadata_width = 540
        self.header_height = 80

        # Scrolling state for test list panel
        self.test_list_scroll_offset = 0
        self.test_list_max_scroll = 0
        self.test_list_panel_rect = None  # Set in _draw_test_list for scroll event handling

        # Batch test execution state
        self.batch_running = False
        self.batch_tests = []  # List of test_ids to run
        self.batch_current_index = 0
        self.batch_total = 0
        self.run_all_tests_btn_rect = None

        # UI components
        self.buttons = []
        self.json_popup = None  # For displaying JSON data
        self.confirmation_dialog = None  # For confirming metadata updates
        self.ship_panels = []  # Ship JSON panels
        self.component_panels = []  # Component JSON panels
        self.results_panel = None  # Test run history panel
        self.test_details_panel = None  # Test run details panel

        # Update Expected Values button state
        self.update_expected_button_rect = None
        self.update_expected_button_visible = False

        # Component data cache for UI panels
        self._components_cache = None

        # Battle state viewer (for viewing initial/final JSON states)
        from ui.battle_state_viewer import BattleStateViewer
        self.battle_state_viewer = BattleStateViewer(WIDTH, HEIGHT)

        self._create_ui()


    @property
    def selected_category(self):
        return self.controller.ui_state.get_selected_category()

    @selected_category.setter
    def selected_category(self, value):
        self.controller.ui_state.select_category(value)

    @property
    def selected_test_id(self):
        return self.controller.ui_state.get_selected_test_id()

    @selected_test_id.setter
    def selected_test_id(self, value):
        self.controller.ui_state.select_test(value)

    @property
    def category_hover(self):
        return self.controller.ui_state.get_category_hover()

    @category_hover.setter
    def category_hover(self, value):
        self.controller.ui_state.set_category_hover(value)

    @property
    def test_hover(self):
        return self.controller.ui_state.get_test_hover()

    @test_hover.setter
    def test_hover(self, value):
        self.controller.ui_state.set_test_hover(value)

    @property
    def headless_running(self):
        return self.controller.ui_state.is_headless_running()

    @headless_running.setter
    def headless_running(self, value):
        self.controller.ui_state.set_headless_running(value)

    @property
    def output_log(self):
        return self.controller.output_log

    @property
    def all_scenarios(self):
        return self.controller.all_scenarios

    def _extract_ships_from_scenario(self, test_id):
        """
        Extract ship information from test scenario metadata.

        Args:
            test_id: Test ID (e.g., "BEAM360-001")

        Returns:
            List[Dict]: [
                {
                    'role': 'Attacker',  # or 'Target', 'Ship1', etc.
                    'filename': 'Test_Attacker_Beam360_Low.json',
                    'ship_data': {...},  # Full ship JSON
                    'component_ids': ['test_beam_low_acc_1dmg', ...]  # All component IDs
                }
            ]
        """
        scenario_info = self.registry.get_by_id(test_id)

        if not scenario_info:
            return []

        metadata = scenario_info['metadata']
        ships = []

        # Parse conditions for ship filenames
        # Format: "Attacker: Test_Attacker_Beam360_Low.json" or "Target: Test_Target_Stationary.json (mass=400)"
        for condition in metadata.conditions:
            if '.json' in condition and ':' in condition:
                parts = condition.split(':', 1)
                role = parts[0].strip()
                filename_part = parts[1].strip()

                # Extract only the .json filename (ignore anything after .json like "(mass=400)")
                json_end = filename_part.index('.json') + 5  # +5 for '.json'
                filename = filename_part[:json_end]

                # Load ship JSON file
                ship_path = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    'simulation_tests',
                    'data',
                    'ships',
                    filename
                )

                ship_data = load_json(ship_path)
                if ship_data is None:
                    logger.error(f"Failed to load ship file: {ship_path}")
                    continue

                # Extract component IDs from layers
                component_ids = []
                for layer_name in ['CORE', 'ARMOR', 'HULL']:
                    layer = ship_data.get('layers', {}).get(layer_name, [])
                    for component in layer:
                        comp_id = component.get('id')
                        if comp_id:
                            component_ids.append(comp_id)

                ships.append({
                    'role': role,
                    'filename': filename,
                    'ship_data': ship_data,
                    'component_ids': component_ids
                })

        return ships

    def _validate_all_scenarios(self):
        """
        Validate all test scenarios against component/ship data files.

        This performs static validation without running tests, checking if
        test metadata matches actual component data.
        """
        logger.info("\n=== Static Validation: Checking test metadata against component data ===")

        from simulation_tests.scenarios.validation import Validator

        for test_id, scenario_info in self.all_scenarios.items():
            metadata = scenario_info['metadata']

            # Skip scenarios without validation rules
            if not metadata.validation_rules:
                continue

            # Only validate ExactMatchRules (not StatisticalTestRules which need actual test runs)
            # Check by class name instead of isinstance due to import issues
            exact_match_rules = [
                rule for rule in metadata.validation_rules
                if rule.__class__.__name__ == 'ExactMatchRule'
            ]

            if not exact_match_rules:
                continue

            try:
                # Build validation context from file data
                context = self._build_validation_context_from_files(test_id, metadata)

                if not context:
                    logger.info(f"  {test_id}: Could not build validation context")
                    continue


                # Run validation
                validator = Validator(exact_match_rules)
                validation_results = validator.validate(context)

                # Store results
                results = {
                    'validation_results': [r.to_dict() for r in validation_results],
                    'validation_summary': validator.get_summary(validation_results),
                    'has_validation_failures': validator.has_failures(validation_results),
                    'has_validation_warnings': validator.has_warnings(validation_results)
                }

                # Update registry with validation results
                scenario_info['last_run_results'] = results

                # Log results
                summary = results['validation_summary']
                pass_count = summary.get('pass', 0)
                fail_count = summary.get('fail', 0)
                warn_count = summary.get('warn', 0)

                if fail_count > 0 or warn_count > 0:
                    logger.info(f"  {test_id}: {pass_count} pass, {fail_count} fail, {warn_count} warn")

            except Exception as e:
                logger.info(f"  {test_id}: Validation error - {e}")
                import traceback
                traceback.print_exc()

        logger.info("=== Static Validation Complete ===\n")

    def _build_validation_context_from_files(self, test_id, metadata):
        """
        Build validation context from ship and component JSON files.

        Args:
            test_id: Test ID
            metadata: TestMetadata object

        Returns:
            Dict with 'attacker', 'target', etc. containing component data
        """
        context = {}

        # Parse conditions for ship files
        ships = self._extract_ships_from_scenario(test_id)

        for ship_info in ships:
            role = ship_info['role'].lower()  # 'Attacker' -> 'attacker'
            ship_data = ship_info['ship_data']
            component_ids = ship_info['component_ids']

            # Build ship validation data structure
            ship_validation_data = {
                'mass': ship_data.get('expected_stats', {}).get('mass', 0)
            }

            # Extract weapon data from first component with BeamWeaponAbility
            if self._components_cache is None:
                # Load components.json
                self._load_component_data("dummy")  # This will populate cache

            for comp_id in component_ids:
                comp_data = self._components_cache.get(comp_id)
                if comp_data and 'abilities' in comp_data:
                    abilities = comp_data['abilities']

                    # Check for BeamWeaponAbility
                    if 'BeamWeaponAbility' in abilities:
                        weapon_ability = abilities['BeamWeaponAbility']
                        ship_validation_data['weapon'] = {
                            'damage': weapon_ability.get('damage'),
                            'range': weapon_ability.get('range'),
                            'base_accuracy': weapon_ability.get('base_accuracy'),
                            'accuracy_falloff': weapon_ability.get('accuracy_falloff'),
                            'reload': weapon_ability.get('reload'),
                            'firing_arc': weapon_ability.get('firing_arc')
                        }
                        break  # Found weapon, use first one

            context[role] = ship_validation_data

        return context

    def _load_component_data(self, component_id):
        """
        Load component JSON from components.json by ID.

        Args:
            component_id: Component ID (e.g., "test_beam_low_acc_1dmg")

        Returns:
            Dict: Component JSON data, or None if not found
        """
        # Load and cache components.json on first call
        if self._components_cache is None:
            components_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'simulation_tests',
                'data',
                'components.json'
            )

            components_data = load_json(components_path, default={})
            # Extract the components list from the wrapper object
            components_list = components_data.get('components', [])
            # Convert list to dict for faster lookup
            self._components_cache = {
                comp['id']: comp
                for comp in components_list
            }

        return self._components_cache.get(component_id)

    def _handle_update_expected_values(self):
        """Handle click on Update Expected Values button."""
        if not self.selected_test_id:
            return

        # Get the scenario and its last run results
        scenario_info = self.registry.get_by_id(self.selected_test_id)
        if not scenario_info:
            return

        last_run_results = scenario_info.get('last_run_results')
        if not last_run_results:
            logger.info("No test results available. Run the test first.")
            return

        validation_results = last_run_results.get('validation_results', [])
        if not validation_results:
            return

        # Collect failed ExactMatchRules
        changes = []
        for vr in validation_results:
            if vr['status'] == 'FAIL' and vr['expected'] is not None and vr['actual'] is not None:
                # This is a failed exact match rule
                field_name = vr['name']
                old_value = vr['expected']
                new_value = vr['actual']

                changes.append({
                    'field': field_name,
                    'old_value': old_value,
                    'new_value': new_value
                })

        if not changes:
            logger.info("No failed validation rules to update.")
            return

        # Show confirmation dialog
        self.confirmation_dialog = ConfirmationDialog(
            title="Update Expected Values",
            changes=changes,
            screen_width=self.game.screen.get_width(),
            screen_height=self.game.screen.get_height(),
            on_confirm=lambda: self._apply_metadata_updates(changes),
            on_cancel=lambda: logger.info("Update canceled")
        )

    def _apply_metadata_updates(self, changes):
        """
        Apply metadata updates to the test scenario file.

        Args:
            changes: List of dicts with 'field', 'old_value', 'new_value'
        """
        if not self.selected_test_id:
            return

        scenario_info = self.registry.get_by_id(self.selected_test_id)
        if not scenario_info:
            return

        # Get the file path for the scenario
        scenario_file = scenario_info['file']

        try:
            # Read the file
            with open(scenario_file, 'r') as f:
                content = f.read()

            # Apply changes using string replacement
            # Update both: 1) Conditions text, 2) ExactMatchRule expected values
            for change in changes:
                field = change['field']
                old_val = change['old_value']
                new_val = change['new_value']

                # 1. Update conditions text for display
                if "Damage" in field and "Beam" in field:
                    # Update condition line like "Beam Damage: 1 per hit"
                    old_pattern = f'"Beam Damage: {old_val}'
                    new_pattern = f'"Beam Damage: {new_val}'
                    content = content.replace(old_pattern, new_pattern)
                    logger.info(f"Updated condition text for {field}: {old_val} → {new_val}")
                elif "Base Accuracy" in field:
                    old_pattern = f'"Base Accuracy: {old_val}"'
                    new_pattern = f'"Base Accuracy: {new_val}"'
                    content = content.replace(old_pattern, new_pattern)
                    logger.info(f"Updated condition text for {field}: {old_val} → {new_val}")
                elif "Accuracy Falloff" in field:
                    old_pattern = f'"Accuracy Falloff: {old_val}'
                    new_pattern = f'"Accuracy Falloff: {new_val}'
                    content = content.replace(old_pattern, new_pattern)
                    logger.info(f"Updated condition text for {field}: {old_val} → {new_val}")

                # 2. Update ExactMatchRule expected value in validation_rules
                # Find the ExactMatchRule for this field and update its expected value
                if "Damage" in field and "Beam" in field:
                    # ExactMatchRule(name='Beam Weapon Damage', path='...', expected=1)
                    old_rule = f"ExactMatchRule(\n                name='Beam Weapon Damage',\n                path='attacker.weapon.damage',\n                expected={old_val}\n            )"
                    new_rule = f"ExactMatchRule(\n                name='Beam Weapon Damage',\n                path='attacker.weapon.damage',\n                expected={new_val}\n            )"
                    content = content.replace(old_rule, new_rule)
                    logger.info(f"Updated ExactMatchRule for {field}: expected={old_val} → {new_val}")
                elif "Base Accuracy" in field:
                    old_rule = f"ExactMatchRule(\n                name='Base Accuracy',\n                path='attacker.weapon.base_accuracy',\n                expected={old_val}\n            )"
                    new_rule = f"ExactMatchRule(\n                name='Base Accuracy',\n                path='attacker.weapon.base_accuracy',\n                expected={new_val}\n            )"
                    content = content.replace(old_rule, new_rule)
                    logger.info(f"Updated ExactMatchRule for {field}: expected={old_val} → {new_val}")
                elif "Accuracy Falloff" in field:
                    old_rule = f"ExactMatchRule(\n                name='Accuracy Falloff',\n                path='attacker.weapon.accuracy_falloff',\n                expected={old_val}\n            )"
                    new_rule = f"ExactMatchRule(\n                name='Accuracy Falloff',\n                path='attacker.weapon.accuracy_falloff',\n                expected={new_val}\n            )"
                    content = content.replace(old_rule, new_rule)
                    logger.info(f"Updated ExactMatchRule for {field}: expected={old_val} → {new_val}")
                elif "Weapon Range" in field or "Range" in field:
                    old_rule = f"ExactMatchRule(\n                name='Weapon Range',\n                path='attacker.weapon.range',\n                expected={old_val}\n            )"
                    new_rule = f"ExactMatchRule(\n                name='Weapon Range',\n                path='attacker.weapon.range',\n                expected={new_val}\n            )"
                    content = content.replace(old_rule, new_rule)
                    logger.info(f"Updated ExactMatchRule for {field}: expected={old_val} → {new_val}")
                elif "Target Mass" in field or "Mass" in field:
                    old_rule = f"ExactMatchRule(\n                name='Target Mass',\n                path='target.mass',\n                expected={old_val}\n            )"
                    new_rule = f"ExactMatchRule(\n                name='Target Mass',\n                path='target.mass',\n                expected={new_val}\n            )"
                    content = content.replace(old_rule, new_rule)
                    logger.info(f"Updated ExactMatchRule for {field}: expected={old_val} → {new_val}")

            # Write back to file
            with open(scenario_file, 'w') as f:
                f.write(content)

            logger.info(f"Successfully updated {scenario_file}")

            # Refresh the registry to reload the modified scenario
            self.registry.refresh()
            self.all_scenarios = self.registry.get_all_scenarios()

            logger.info("Registry refreshed. Metadata updated successfully!")

        except Exception as e:
            logger.error(f"Error updating metadata: {e}")
            import traceback
            traceback.print_exc()

    def _create_ship_panels(self, test_id):
        """
        Create ship panels and component panels for the selected test.

        Args:
            test_id: Test ID (e.g., "BEAM360-001")
        """
        self.ship_panels = []
        self.component_panels = []

        # Extract ships from scenario
        ships = self._extract_ships_from_scenario(test_id)

        if not ships:
            return

        # Panel dimensions
        base_x = 20 + self.category_width + 20 + self.test_list_width + 20 + self.metadata_width + 20
        panel_width = 540

        # Ship panel (top half) - ~960px tall (100-1060)
        ship_panel_y_start = self.header_height + 20  # 100px
        ship_panel_height = HEIGHT // 2 - ship_panel_y_start - 20  # Ends at ~1060px with 20px gap

        # Component panel (bottom half) - ~980px tall (1080-2060)
        component_panel_y_start = HEIGHT // 2 + 20  # 1080px (middle + 20px gap)
        component_panel_height = HEIGHT - component_panel_y_start - 100  # ~980px tall

        for i, ship_info in enumerate(ships):
            panel_x = base_x + (i * (panel_width + 20))

            # Create ship panel (top)
            ship_panel = ShipPanel(
                x=panel_x,
                y=ship_panel_y_start,
                width=panel_width,
                height=ship_panel_height,
                ship_info=ship_info
            )
            self.ship_panels.append(ship_panel)

            # Create component panel (bottom)
            component_panel = ComponentPanel(
                x=panel_x,
                y=component_panel_y_start,
                width=panel_width,
                height=component_panel_height,
                component_ids=ship_info['component_ids'],
                load_component_callback=self._load_component_data
            )
            self.component_panels.append(component_panel)

    def _create_results_panel(self, test_id):
        """
        Create results panel for selected test.

        Positions panel to the right of ship panels, using remaining 4K display space.

        Args:
            test_id: Test ID (e.g., "BEAM360-001")
        """
        # Calculate position: after last ship panel or after Test Details
        num_ships = len(self.ship_panels)
        if num_ships == 0:
            # No ships, place after Test Details panel
            base_x = 20 + self.category_width + 20 + self.test_list_width + 20 + self.metadata_width + 20
        else:
            # Place after last ship panel
            last_ship_panel = self.ship_panels[-1]
            base_x = last_ship_panel.x + last_ship_panel.width + 20

        # Create results panel (600px width)
        self.results_panel = ResultsPanel(
            x=base_x,
            y=self.header_height + 20,
            width=600,
            height=HEIGHT - self.header_height - 120,
            test_history=self.test_history
        )

        # Create test run details panel (to the right of results panel)
        details_x = base_x + 600 + 20
        self.test_details_panel = TestRunDetailsPanel(
            x=details_x,
            y=self.header_height + 20,
            width=600,
            height=HEIGHT - self.header_height - 120
        )

        # Link panels
        self.results_panel.set_details_panel(self.test_details_panel)

        # Set up View States callback
        self.test_details_panel.on_view_states = self._on_view_battle_states

        self.results_panel.set_test(test_id)

        logger.debug(f"Created results panel at x={base_x} and details panel at x={details_x} for test {test_id}")

    def _create_ui(self):
        """Create UI buttons."""
        self.buttons = []

        # Back Button
        self.btn_back = Button(20, 20, 100, 40, "Back", self._on_back)
        self.buttons.append(self.btn_back)

        # Run Test and Run Headless buttons are now drawn in _draw_metadata_panel()
        self.run_test_btn_rect = None
        self.run_headless_btn_rect = None

    def _get_filtered_scenarios(self):
        """Get scenarios filtered by selected category."""
        if self.selected_category is None:
            return self.all_scenarios
        else:
            return self.registry.get_by_category(self.selected_category)
        
    def reset_selection(self):
        """Clear test selection (called when returning from battle)."""
        # Store results from completed visual test before clearing
        if self.selected_test_id and hasattr(self.game.battle_scene, 'test_scenario'):
            scenario = self.game.battle_scene.test_scenario
            # Only capture results if test actually completed (not if user exited early)
            if scenario and self.game.battle_scene.test_completed:
                # Ensure results dict exists
                if not hasattr(scenario, 'results') or scenario.results is None:
                    scenario.results = {}

                # Ensure essential fields are populated
                if 'passed' not in scenario.results:
                    scenario.results['passed'] = getattr(scenario, 'passed', False)
                if 'ticks_run' not in scenario.results:
                    scenario.results['ticks_run'] = self.game.battle_scene.test_tick_count

                logger.debug(f"Storing visual test results for {self.selected_test_id}, keys: {list(scenario.results.keys())}")
                self.registry.update_last_run_results(self.selected_test_id, scenario.results)

                # Add to persistent test history
                self.test_history.add_run(self.selected_test_id, scenario.results)

                # Refresh results panel if it exists
                if self.results_panel:
                    self.results_panel.set_test(self.selected_test_id)
            else:
                logger.debug(f"No results to store - scenario={scenario}, test_completed={self.game.battle_scene.test_completed if scenario else 'N/A'}")

        # Clear battle scene test state
        if hasattr(self.game.battle_scene, 'test_completed'):
            self.game.battle_scene.test_completed = False
        if hasattr(self.game.battle_scene, 'test_scenario'):
            self.game.battle_scene.test_scenario = None

        self.selected_test_id = None
        logger.debug(f"Test selection cleared")

    def _on_back(self):
        """Return to main menu."""
        from game.core.constants import GameState
        self.game.state = GameState.MENU
        if hasattr(self.game, 'menu_screen') and hasattr(self.game.menu_screen, 'create_particles'):
            self.game.menu_screen.create_particles()

    def _on_view_battle_states(self, run_record, run_number):
        """
        Open the battle state viewer for a test run.

        Args:
            run_record: TestRunRecord with state file paths
            run_number: Display number for the run
        """
        from test_framework.battle_state_capture import load_battle_state_json

        initial_json = None
        final_json = None

        # Load initial state JSON
        if run_record.initial_state_file:
            initial_json = load_battle_state_json(run_record.initial_state_file)
            if initial_json is None:
                logger.warning(f"Could not load initial state from: {run_record.initial_state_file}")

        # Load final state JSON
        if run_record.final_state_file:
            final_json = load_battle_state_json(run_record.final_state_file)
            if final_json is None:
                logger.warning(f"Could not load final state from: {run_record.final_state_file}")

        if initial_json or final_json:
            self.battle_state_viewer.show(
                initial_json=initial_json,
                final_json=final_json,
                test_id=self.selected_test_id,
                run_number=run_number
            )
        else:
            self.output_log.append("ERROR: Could not load battle state files")

    def _on_run(self):
        """Run the selected test scenario visually in Combat Lab."""
        if self.selected_test_id is None:
            self.output_log.append("ERROR: No test selected!")
            return

        scenario_info = self.registry.get_by_id(self.selected_test_id)
        if scenario_info is None:
            self.output_log.append(f"ERROR: Test {self.selected_test_id} not found!")
            return

        metadata = scenario_info['metadata']
        self.output_log.append(f"Running {metadata.name}...")

        runner = TestRunner()

        try:
            # Instantiate scenario
            logger.debug(f" Instantiating scenario class")
            scenario_cls = scenario_info['class']
            scenario = scenario_cls()
            logger.debug(f" Scenario instantiated: {scenario.name}")

            # Load test data
            logger.debug(f" Loading test data for scenario")
            runner.load_data_for_scenario(scenario)
            logger.debug(f" Test data loaded successfully")

            # Ensure battle engine exists (may have been reset after previous test)
            if self.game.battle_scene.engine is None:
                self.game.battle_scene._battle_service.create_battle()

            # Clear battle engine
            logger.debug(f" Clearing battle engine")
            self.game.battle_scene.engine.start([], [])

            # Setup scenario
            logger.debug(f" Calling scenario.setup()")
            scenario.setup(self.game.battle_scene.engine)
            logger.debug(f" Scenario setup complete")

            # Configure battle scene for test mode
            logger.debug(f" Configuring battle scene for test mode")
            logger.debug(f" BEFORE: test_mode={self.game.battle_scene.test_mode}")
            self.game.battle_scene.headless_mode = False
            self.game.battle_scene.sim_paused = True  # Start paused
            self.game.battle_scene.test_mode = True   # Enable test mode
            self.game.battle_scene.test_scenario = scenario  # Pass scenario for update() calls
            self.game.battle_scene.test_tick_count = 0  # Reset tick counter
            self.game.battle_scene.test_completed = False  # Reset completed flag
            self.game.battle_scene.action_return_to_test_lab = False
            logger.debug(f" AFTER: test_mode={self.game.battle_scene.test_mode}")
            logger.debug(f" Battle scene configured (paused=True, test_mode=True, scenario={scenario.metadata.test_id})")

            # Fit camera to ships
            if self.game.battle_scene.engine.ships:
                self.game.battle_scene.camera.fit_objects(self.game.battle_scene.engine.ships)
                logger.debug(f" Camera fitted to ships")

            # Switch to battle state
            from game.core.constants import GameState
            logger.debug(f" Switching to BATTLE state")
            self.game.state = GameState.BATTLE

            self.output_log.append(f"Started test {self.selected_test_id}")

        except Exception as e:
            self.output_log.append(f"ERROR: {e}")
            import traceback
            traceback.print_exc()

    def _on_run_headless(self):
        """Run the selected test scenario in headless mode (fast, no visuals)."""
        if self.selected_test_id is None:
            self.output_log.append("ERROR: No test selected!")
            return

        scenario_info = self.registry.get_by_id(self.selected_test_id)
        if scenario_info is None:
            self.output_log.append(f"ERROR: Test {self.selected_test_id} not found!")
            return

        metadata = scenario_info['metadata']
        self.output_log.append(f"Running {metadata.name} (headless)...")

        runner = TestRunner()

        # Ensure battle engine exists (may have been reset after visual test)
        if self.game.battle_scene.engine is None:
            self.game.battle_scene._battle_service.create_battle()
        engine = self.game.battle_scene.engine

        try:
            # Instantiate scenario
            logger.debug(f" Instantiating scenario class for headless run")
            scenario_cls = scenario_info['class']
            scenario = scenario_cls()
            logger.debug(f" Scenario instantiated: {scenario.name}")

            # Load test data
            logger.debug(f" Loading test data for scenario")
            runner.load_data_for_scenario(scenario)
            logger.debug(f" Test data loaded successfully")

            # Clear battle engine
            logger.debug(f" Clearing battle engine")
            engine.start([], [])

            # Setup scenario
            logger.debug(f" Calling scenario.setup()")
            scenario.setup(engine)
            logger.debug(f" Scenario setup complete")

            # Show "Running Test..." message
            self.headless_running = True
            self.game.screen.fill((20, 20, 25))
            self.draw(self.game.screen)

            # Draw "Running Test..." overlay
            overlay = pygame.Surface((600, 200))
            overlay.fill((40, 40, 45))
            pygame.draw.rect(overlay, (100, 100, 120), overlay.get_rect(), 3)

            title_text = self.header_font.render("Running Test...", True, (255, 255, 255))
            test_text = self.body_font.render(f"{metadata.name}", True, (200, 200, 200))
            ticks_text = self.body_font.render(f"Max ticks: {scenario.max_ticks}", True, (180, 180, 180))

            overlay.blit(title_text, (300 - title_text.get_width()//2, 50))
            overlay.blit(test_text, (300 - test_text.get_width()//2, 90))
            overlay.blit(ticks_text, (300 - ticks_text.get_width()//2, 130))

            screen_center_x = self.game.screen.get_width() // 2
            screen_center_y = self.game.screen.get_height() // 2
            self.game.screen.blit(overlay, (screen_center_x - 300, screen_center_y - 100))
            pygame.display.flip()

            # Run simulation headless (stay on Combat Lab screen)
            start_time = time.time()
            tick_count = 0
            max_ticks = scenario.max_ticks

            logger.debug(f" Starting headless simulation loop (max_ticks={max_ticks})")

            # Capture battle states for later viewing
            from test_framework.battle_state_capture import BattleStateCapture
            import random
            seed = random.randint(0, 2**31 - 1)

            with BattleStateCapture(engine, self.selected_test_id, seed) as state_capture:
                # Run simulation as fast as possible
                while tick_count < max_ticks:
                    # Call scenario update for dynamic logic
                    scenario.update(engine)

                    # Update engine one tick
                    engine.update()
                    tick_count += 1

                    # Check if battle ended naturally
                    if engine.is_battle_over():
                        logger.debug(f" Battle ended naturally at tick {tick_count}")
                        break

            # Simulation complete - verify results
            elapsed_time = time.time() - start_time
            logger.debug(f" Simulation complete: {tick_count} ticks in {elapsed_time:.2f}s ({tick_count/elapsed_time:.0f} ticks/sec)")

            # Verify and collect results
            scenario.passed = scenario.verify(engine)
            logger.debug(f" Test {'PASSED' if scenario.passed else 'FAILED'}")

            # Store results including battle state file paths
            scenario.results['ticks_run'] = tick_count
            scenario.results['duration_real'] = elapsed_time
            scenario.results['ticks'] = tick_count  # Alias for consistency with runner
            scenario.results.update(state_capture.get_results_dict())  # Add state file paths and seed
            self.registry.update_last_run_results(self.selected_test_id, scenario.results)

            # Add to persistent test history
            self.test_history.add_run(self.selected_test_id, scenario.results)

            # Log test execution (for UI vs headless comparison)
            runner._log_test_execution(scenario, headless=True)

            # Refresh results panel if it exists
            if self.results_panel:
                self.results_panel.set_test(self.selected_test_id)

            # Update output log
            status = "PASSED" if scenario.passed else "FAILED"
            self.output_log.append(f"Test {self.selected_test_id} {status} ({tick_count} ticks, {elapsed_time:.2f}s)")

            # Clear running flag
            self.headless_running = False

        except Exception as e:
            self.headless_running = False
            self.output_log.append(f"ERROR: {e}")
            import traceback
            traceback.print_exc()

    def _on_run_all_tests(self):
        """Run all visible tests headlessly in sequence."""
        filtered_scenarios = self._get_filtered_scenarios()
        self.batch_tests = sorted(filtered_scenarios.keys())
        self.batch_total = len(self.batch_tests)

        if self.batch_total == 0:
            self.output_log.append("No tests to run!")
            return

        self.batch_current_index = 0
        self.batch_running = True
        self.output_log.append(f"Starting batch run of {self.batch_total} tests...")
        self._run_next_batch_test()

    def _run_next_batch_test(self):
        """Run the next test in the batch sequence."""
        if self.batch_current_index >= self.batch_total:
            # All tests complete
            self.batch_running = False
            self.output_log.append(f"Batch complete: {self.batch_total} tests run")
            return

        test_id = self.batch_tests[self.batch_current_index]
        scenario_info = self.registry.get_by_id(test_id)

        if scenario_info is None:
            self.output_log.append(f"ERROR: Test {test_id} not found, skipping")
            self.batch_current_index += 1
            self._run_next_batch_test()
            return

        metadata = scenario_info['metadata']
        runner = TestRunner()

        try:
            # Instantiate scenario
            scenario_cls = scenario_info['class']
            scenario = scenario_cls()

            # Load test data
            runner.load_data_for_scenario(scenario)

            # Ensure battle engine exists (may have been reset)
            if self.game.battle_scene.engine is None:
                self.game.battle_scene._battle_service.create_battle()

            # Get fresh battle engine
            engine = self.game.battle_scene.engine
            engine.start([], [])

            # Setup scenario
            scenario.setup(engine)

            # Draw progress overlay
            self.game.screen.fill((20, 20, 25))
            self.draw(self.game.screen)

            overlay = pygame.Surface((600, 200))
            overlay.fill((40, 40, 45))
            pygame.draw.rect(overlay, (100, 100, 120), overlay.get_rect(), 3)

            progress_text = f"Running test {self.batch_current_index + 1}/{self.batch_total}"
            title_text = self.header_font.render(progress_text, True, (255, 255, 255))
            test_text = self.body_font.render(f"{metadata.name}", True, (200, 200, 200))
            id_text = self.small_font.render(f"ID: {test_id}", True, (150, 150, 150))

            overlay.blit(title_text, (300 - title_text.get_width()//2, 50))
            overlay.blit(test_text, (300 - test_text.get_width()//2, 90))
            overlay.blit(id_text, (300 - id_text.get_width()//2, 125))

            screen_center_x = self.game.screen.get_width() // 2
            screen_center_y = self.game.screen.get_height() // 2
            self.game.screen.blit(overlay, (screen_center_x - 300, screen_center_y - 100))
            pygame.display.flip()

            # Run simulation headless with battle state capture
            from test_framework.battle_state_capture import BattleStateCapture
            import random
            seed = random.randint(0, 2**31 - 1)

            start_time = time.time()
            tick_count = 0
            max_ticks = scenario.max_ticks

            with BattleStateCapture(engine, test_id, seed) as state_capture:
                while tick_count < max_ticks:
                    scenario.update(engine)
                    engine.update()
                    tick_count += 1

                    if engine.is_battle_over():
                        break

            # Verify results
            elapsed_time = time.time() - start_time
            scenario.passed = scenario.verify(engine)

            # Store results including battle state file paths
            scenario.results['ticks_run'] = tick_count
            scenario.results['duration_real'] = elapsed_time
            scenario.results['ticks'] = tick_count
            scenario.results.update(state_capture.get_results_dict())  # Add state file paths and seed
            self.registry.update_last_run_results(test_id, scenario.results)

            # Add to persistent test history
            self.test_history.add_run(test_id, scenario.results)

            # Log test execution
            runner._log_test_execution(scenario, headless=True)

            # Update output log
            status = "PASSED" if scenario.passed else "FAILED"
            self.output_log.append(f"[{self.batch_current_index + 1}/{self.batch_total}] {test_id}: {status}")

        except Exception as e:
            self.output_log.append(f"[{self.batch_current_index + 1}/{self.batch_total}] {test_id}: ERROR - {e}")

        # Move to next test
        self.batch_current_index += 1
        # Use a small delay to allow UI updates, then continue
        pygame.time.set_timer(pygame.USEREVENT + 1, 50, loops=1)  # Trigger next test after 50ms

    def _continue_batch_test(self):
        """Continue batch execution (called from event handler)."""
        if self.batch_running:
            self._run_next_batch_test()

    def handle_input(self, events):
        """Handle user input for category selection, test selection, and buttons."""
        for event in events:
            # Handle batch test continuation timer
            if event.type == pygame.USEREVENT + 1:
                self._continue_batch_test()
                continue

            # Handle confirmation dialog first (if open)
            if self.confirmation_dialog and self.confirmation_dialog.is_open:
                self.confirmation_dialog.handle_event(event)
                if not self.confirmation_dialog.is_open:
                    self.confirmation_dialog = None
                continue  # Don't process other events while dialog is open

            # Handle JSON popup (if open)
            if self.json_popup and self.json_popup.is_open:
                self.json_popup.handle_event(event)
                if not self.json_popup.is_open:
                    self.json_popup = None
                continue  # Don't process other events while popup is open

            # Handle battle state viewer (if open)
            if self.battle_state_viewer and self.battle_state_viewer.visible:
                self.battle_state_viewer.handle_event(event)
                continue  # Don't process other events while viewer is open

            # Handle ship panel events (scrolling)
            for panel in self.ship_panels:
                if panel.handle_event(event):
                    continue  # Event consumed by panel

            # Handle component panel events (scrolling, dropdown clicks)
            for panel in self.component_panels:
                if panel.handle_event(event):
                    continue  # Event consumed by panel

            # Handle results panel events (scrolling, card selection, clear buttons)
            if self.results_panel:
                if self.results_panel.handle_event(event):
                    continue  # Event consumed by panel

            # Handle test details panel events (scrolling)
            if self.test_details_panel:
                if self.test_details_panel.handle_event(event):
                    continue  # Event consumed by panel

            # Handle mouse wheel for test list scrolling
            if event.type == pygame.MOUSEWHEEL:
                mx, my = pygame.mouse.get_pos()
                if self.test_list_panel_rect and self.test_list_panel_rect.collidepoint(mx, my):
                    self.test_list_scroll_offset -= event.y * 40  # 40px per scroll tick
                    self.test_list_scroll_offset = max(0, min(self.test_list_scroll_offset, self.test_list_max_scroll))
                    continue  # Event consumed

            # Handle mouse motion for hover effects
            if event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                self._update_hover_state(mx, my)

            # Handle mouse clicks
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                self._handle_click(mx, my)

            # Let buttons handle events
            for btn in self.buttons:
                btn.handle_event(event)

    def _update_hover_state(self, mx, my):
        """Update hover state for categories and tests."""
        # Reset hover
        self.category_hover = None
        self.test_hover = None

        # Check "All Tests" hover
        category_x = 20
        category_y = self.header_height + 20
        all_tests_y = category_y + 40
        all_tests_rect = pygame.Rect(category_x, all_tests_y, 200, 40)
        if all_tests_rect.collidepoint(mx, my):
            self.category_hover = "ALL"
            return

        # Check category hover (starts after "All Tests" button)
        category_start_y = all_tests_y + 50
        for i, category in enumerate(self.categories):
            rect = pygame.Rect(category_x, category_start_y + i * 50, 200, 40)
            if rect.collidepoint(mx, my):
                self.category_hover = category
                return

        # Check test hover (accounting for scroll offset)
        test_list_x = 20 + self.category_width + 20
        test_list_y = self.header_height + 20 + 40  # +40 for header offset

        # Check if mouse is within the test list panel visible area
        if self.test_list_panel_rect and self.test_list_panel_rect.collidepoint(mx, my):
            filtered_scenarios = self._get_filtered_scenarios()
            sorted_test_ids = sorted(filtered_scenarios.keys())

            for i, test_id in enumerate(sorted_test_ids):
                # Calculate item position with scroll offset
                item_y = test_list_y + i * 55 - self.test_list_scroll_offset
                rect = pygame.Rect(test_list_x, item_y, 400, 50)
                if rect.collidepoint(mx, my) and item_y >= test_list_y - 50 and item_y < test_list_y + (self.test_list_panel_rect.height - 50):
                    self.test_hover = test_id
                    break

    def _handle_click(self, mx, my):
        """Handle click events for categories and tests."""
        # Check "All Tests" click
        category_x = 20
        category_y = self.header_height + 20

        # Check header offset (40px for "CATEGORIES" header)
        all_tests_y = category_y + 40
        all_tests_rect = pygame.Rect(category_x, all_tests_y, 200, 40)
        if all_tests_rect.collidepoint(mx, my):
            self.selected_category = None
            self.selected_test_id = None
            return

        # Check category click (starts after "All Tests" button)
        category_start_y = all_tests_y + 50
        for i, category in enumerate(self.categories):
            rect = pygame.Rect(category_x, category_start_y + i * 50, 200, 40)
            if rect.collidepoint(mx, my):
                # Toggle category selection
                if self.selected_category == category:
                    self.selected_category = None  # Deselect - show all
                else:
                    self.selected_category = category
                self.selected_test_id = None  # Clear test selection
                return

        # Check "Run Tests" button click (in test list panel)
        if self.run_all_tests_btn_rect and self.run_all_tests_btn_rect.collidepoint(mx, my):
            if not self.batch_running:
                self._on_run_all_tests()
            return

        # Check test click (accounting for scroll offset)
        test_list_x = 20 + self.category_width + 20
        test_list_y = self.header_height + 20 + 40  # +40 for header offset

        # Only check test clicks if within the test list panel
        if self.test_list_panel_rect and self.test_list_panel_rect.collidepoint(mx, my):
            filtered_scenarios = self._get_filtered_scenarios()
            sorted_test_ids = sorted(filtered_scenarios.keys())

            for i, test_id in enumerate(sorted_test_ids):
                # Calculate item position with scroll offset
                item_y = test_list_y + i * 55 - self.test_list_scroll_offset
                rect = pygame.Rect(test_list_x, item_y, 400, 50)
                # Check if item is visible and clicked
                if rect.collidepoint(mx, my) and item_y >= test_list_y - 50 and item_y < test_list_y + (self.test_list_panel_rect.height - 50):
                    self.selected_test_id = test_id
                    # Create ship panels for the selected test
                    self._create_ship_panels(test_id)
                    # Create results panel for the selected test
                    self._create_results_panel(test_id)
                    return

        # Check Run Test button click (in metadata panel)
        if self.run_test_btn_rect and self.run_test_btn_rect.collidepoint(mx, my):
            self._on_run()
            return

        # Check Run Headless button click (in metadata panel)
        if self.run_headless_btn_rect and self.run_headless_btn_rect.collidepoint(mx, my):
            self._on_run_headless()
            return

        # Check "Update Expected Values" button click
        if self.update_expected_button_visible and self.update_expected_button_rect:
            if self.update_expected_button_rect.collidepoint(mx, my):
                self._handle_update_expected_values()
                return

    def update(self):
        """Update UI state."""
        # Update ship panels (hover states)
        for panel in self.ship_panels:
            panel.update()

        # Update component panels (hover states)
        for panel in self.component_panels:
            panel.update()

        # Update results panel (hover states for buttons/cards)
        if self.results_panel:
            self.results_panel.update()

    def draw(self, screen):
        """Draw the Combat Lab UI with category sidebar, test list, and metadata panel."""
        screen.fill(self.BG_COLOR)

        # Header
        self._draw_header(screen)

        # Three-column layout
        self._draw_category_sidebar(screen)
        self._draw_test_list(screen)
        self._draw_metadata_panel(screen)

        # Ship panels (drawn after metadata panel)
        for panel in self.ship_panels:
            panel.draw(screen)

        # Component panels (drawn after ship panels)
        for panel in self.component_panels:
            panel.draw(screen)

        # Results panel (drawn after component panels)
        if self.results_panel:
            self.results_panel.draw(screen)

        # Test details panel (drawn after results panel)
        if self.test_details_panel:
            self.test_details_panel.draw(screen)

        # Output log
        self._draw_output_log(screen)

        # Buttons
        for btn in self.buttons:
            btn.draw(screen)

        # JSON popup (drawn last, on top of everything)
        if self.json_popup and self.json_popup.is_open:
            self.json_popup.draw(screen)

        # Confirmation dialog (drawn last, on top of everything including popups)
        if self.confirmation_dialog and self.confirmation_dialog.is_open:
            self.confirmation_dialog.draw(screen)

        # Battle state viewer (drawn on top of everything)
        if self.battle_state_viewer and self.battle_state_viewer.visible:
            self.battle_state_viewer.draw(screen)

    def _draw_header(self, screen):
        """Draw the header with title."""
        title = self.title_font.render("COMBAT LAB - TEST VIEWER", True, self.HEADER_COLOR)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))

    def _draw_category_sidebar(self, screen):
        """Draw the category selection sidebar."""
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

        # "All Tests" option
        all_rect = pygame.Rect(x, y, 200, 40)
        if self.selected_category is None:
            color = self.SELECTED_COLOR
        elif self.category_hover == "ALL":
            color = (50, 50, 60)
        else:
            color = self.CATEGORY_BG

        pygame.draw.rect(screen, color, all_rect, border_radius=3)
        pygame.draw.rect(screen, self.BORDER_COLOR, all_rect, 1, border_radius=3)

        all_text = self.body_font.render(f"All Tests ({len(self.all_scenarios)})", True, self.TEXT_COLOR)
        screen.blit(all_text, (all_rect.x + 10, all_rect.y + 10))
        y += 50

        # Check hover for "All Tests"
        mx, my = pygame.mouse.get_pos()
        if all_rect.collidepoint(mx, my):
            self.category_hover = "ALL"

        # Category buttons
        for i, category in enumerate(self.categories):
            rect = pygame.Rect(x, y + i * 50, 200, 40)

            # Determine color
            if self.selected_category == category:
                color = self.SELECTED_COLOR
            elif self.category_hover == category:
                color = (50, 50, 60)
            else:
                color = self.CATEGORY_BG

            pygame.draw.rect(screen, color, rect, border_radius=3)
            pygame.draw.rect(screen, self.BORDER_COLOR, rect, 1, border_radius=3)

            # Count tests in category
            count = len(self.registry.get_by_category(category))
            text = self.body_font.render(f"{category} ({count})", True, self.TEXT_COLOR)
            screen.blit(text, (rect.x + 10, rect.y + 10))

    def _draw_test_list(self, screen):
        """Draw the test list panel with scrolling support."""
        x = 20 + self.category_width + 20
        y = self.header_height + 20

        # Draw panel background
        panel_rect = pygame.Rect(x - 10, y - 10, self.test_list_width, HEIGHT - y - 100)
        self.test_list_panel_rect = panel_rect  # Store for scroll event handling
        pygame.draw.rect(screen, self.PANEL_BG, panel_rect, border_radius=5)
        pygame.draw.rect(screen, self.BORDER_COLOR, panel_rect, 2, border_radius=5)

        # Header
        if self.selected_category:
            header_text = self.header_font.render(f"{self.selected_category.upper()} TESTS", True, self.HEADER_COLOR)
        else:
            header_text = self.header_font.render("ALL TESTS", True, self.HEADER_COLOR)
        screen.blit(header_text, (x, y - 5))
        y += 40

        # Get filtered scenarios
        filtered_scenarios = self._get_filtered_scenarios()
        sorted_test_ids = sorted(filtered_scenarios.keys())

        # Draw "Run Tests" button
        mouse_pos = pygame.mouse.get_pos()
        btn_width = 120
        btn_height = 32
        self.run_all_tests_btn_rect = pygame.Rect(x + self.test_list_width - btn_width - 30, y - 35, btn_width, btn_height)

        if self.batch_running:
            # Show progress during batch execution
            progress_text = f"{self.batch_current_index + 1}/{self.batch_total}"
            btn_color = (80, 80, 50)
            btn_border = (150, 150, 80)
            text_color = (255, 255, 150)
        else:
            btn_hover = self.run_all_tests_btn_rect.collidepoint(mouse_pos)
            btn_color = (60, 80, 60) if btn_hover else (40, 60, 40)
            btn_border = (80, 120, 80)
            progress_text = "Run Tests"
            text_color = (150, 200, 150)

        pygame.draw.rect(screen, btn_color, self.run_all_tests_btn_rect, border_radius=4)
        pygame.draw.rect(screen, btn_border, self.run_all_tests_btn_rect, 1, border_radius=4)
        btn_text = self.small_font.render(progress_text, True, text_color)
        text_rect = btn_text.get_rect(center=self.run_all_tests_btn_rect.center)
        screen.blit(btn_text, text_rect)

        if not sorted_test_ids:
            no_tests_text = self.body_font.render("No tests available", True, (150, 150, 150))
            screen.blit(no_tests_text, (x + 20, y + 20))
            return

        # Calculate scrolling dimensions
        item_height = 55
        content_height = len(sorted_test_ids) * item_height
        visible_height = panel_rect.height - 50  # Space for header
        self.test_list_max_scroll = max(0, content_height - visible_height)

        # Clamp scroll offset
        self.test_list_scroll_offset = max(0, min(self.test_list_scroll_offset, self.test_list_max_scroll))

        # Set clipping region for test items
        clip_rect = pygame.Rect(panel_rect.x, y, panel_rect.width, visible_height)
        screen.set_clip(clip_rect)

        # Draw test items with scroll offset
        for i, test_id in enumerate(sorted_test_ids):
            item_y = y + i * item_height - self.test_list_scroll_offset

            # Skip items outside visible area for performance
            if item_y + 50 < y or item_y > y + visible_height:
                continue

            scenario_info = filtered_scenarios[test_id]
            metadata = scenario_info['metadata']

            rect = pygame.Rect(x, item_y, 400, 50)

            # Determine color
            if self.selected_test_id == test_id:
                color = self.SELECTED_COLOR
            elif self.test_hover == test_id:
                color = (40, 40, 50)
            else:
                color = (30, 30, 35)

            pygame.draw.rect(screen, color, rect, border_radius=3)
            pygame.draw.rect(screen, self.BORDER_COLOR, rect, 1, border_radius=3)

            # Validation status flag (if available)
            flag_x = rect.x + rect.width - 30
            flag_y = rect.y + rect.height // 2  # Vertically centered
            self._draw_validation_flag(screen, flag_x, flag_y, scenario_info)

            # Test ID
            id_text = self.body_font.render(test_id, True, self.HEADER_COLOR)
            screen.blit(id_text, (rect.x + 10, rect.y + 5))

            # Test name
            name_text = self.small_font.render(metadata.name, True, self.TEXT_COLOR)
            screen.blit(name_text, (rect.x + 10, rect.y + 28))

        # Reset clipping
        screen.set_clip(None)

        # Draw scrollbar if needed
        if self.test_list_max_scroll > 0:
            self._draw_test_list_scrollbar(screen, panel_rect, y, visible_height)

    def _draw_test_list_scrollbar(self, screen, panel_rect, content_y, visible_height):
        """Draw scrollbar for the test list panel."""
        scrollbar_width = 8
        scrollbar_x = panel_rect.x + panel_rect.width - scrollbar_width - 5
        scrollbar_y = content_y
        scrollbar_height = visible_height

        # Draw track
        track_rect = pygame.Rect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height)
        pygame.draw.rect(screen, (40, 40, 50), track_rect, border_radius=4)

        # Calculate thumb size and position
        content_height = self.test_list_max_scroll + visible_height
        thumb_height = max(30, int(visible_height * visible_height / content_height))
        scroll_ratio = self.test_list_scroll_offset / self.test_list_max_scroll if self.test_list_max_scroll > 0 else 0
        thumb_y = scrollbar_y + int(scroll_ratio * (scrollbar_height - thumb_height))

        # Draw thumb
        thumb_rect = pygame.Rect(scrollbar_x, thumb_y, scrollbar_width, thumb_height)
        pygame.draw.rect(screen, (100, 100, 120), thumb_rect, border_radius=4)

    def _draw_metadata_panel(self, screen):
        """Draw the metadata panel showing rich test information."""
        x = 20 + self.category_width + 20 + self.test_list_width + 20
        y = self.header_height + 20

        # Draw panel background
        panel_rect = pygame.Rect(x - 10, y - 10, self.metadata_width, HEIGHT - y - 100)
        pygame.draw.rect(screen, self.PANEL_BG, panel_rect, border_radius=5)
        pygame.draw.rect(screen, self.BORDER_COLOR, panel_rect, 2, border_radius=5)

        # Header with run buttons
        header_text = self.header_font.render("TEST DETAILS", True, self.HEADER_COLOR)
        screen.blit(header_text, (x, y - 5))

        # Run buttons to the right of header (only if a test is selected)
        if self.selected_test_id is not None:
            mouse_pos = pygame.mouse.get_pos()
            btn_height = 26
            btn_spacing = 10
            header_btn_y = y - 8

            # Visual Run button (green)
            visual_btn_width = 90
            visual_btn_x = x + self.metadata_width - 220
            self.run_test_btn_rect = pygame.Rect(visual_btn_x, header_btn_y, visual_btn_width, btn_height)
            run_test_hover = self.run_test_btn_rect.collidepoint(mouse_pos)
            run_test_color = (70, 100, 70) if run_test_hover else (50, 80, 50)
            pygame.draw.rect(screen, run_test_color, self.run_test_btn_rect, border_radius=4)
            pygame.draw.rect(screen, (100, 150, 100), self.run_test_btn_rect, 1, border_radius=4)
            run_text = self.small_font.render("Visual Run", True, (200, 255, 200))
            text_rect = run_text.get_rect(center=self.run_test_btn_rect.center)
            screen.blit(run_text, text_rect)

            # Headless Run button (blue)
            headless_btn_width = 100
            headless_btn_x = visual_btn_x + visual_btn_width + btn_spacing
            self.run_headless_btn_rect = pygame.Rect(headless_btn_x, header_btn_y, headless_btn_width, btn_height)
            run_headless_hover = self.run_headless_btn_rect.collidepoint(mouse_pos)
            run_headless_color = (70, 70, 100) if run_headless_hover else (50, 50, 80)
            pygame.draw.rect(screen, run_headless_color, self.run_headless_btn_rect, border_radius=4)
            pygame.draw.rect(screen, (100, 100, 150), self.run_headless_btn_rect, 1, border_radius=4)
            headless_text = self.small_font.render("Headless Run", True, (200, 200, 255))
            text_rect = headless_text.get_rect(center=self.run_headless_btn_rect.center)
            screen.blit(headless_text, text_rect)

        y += 40

        if self.selected_test_id is None:
            hint_text = self.body_font.render("Select a test to view details", True, (150, 150, 150))
            screen.blit(hint_text, (x + 20, y + 20))
            return

        # Get selected test metadata
        scenario_info = self.registry.get_by_id(self.selected_test_id)
        if scenario_info is None:
            return

        metadata = scenario_info['metadata']

        # Test ID
        y = self._draw_section(screen, x, y, "Test ID", metadata.test_id, self.HEADER_COLOR)
        y += 10

        # Category
        category_text = f"{metadata.category} > {metadata.subcategory}"
        y = self._draw_section(screen, x, y, "Category", category_text, (200, 150, 100))
        y += 10

        # Summary
        y = self._draw_section_wrapped(screen, x, y, "Summary", metadata.summary, (100, 200, 150))
        y += 15

        # Get validation results if available
        validation_results = None
        if 'last_run_results' in scenario_info and scenario_info['last_run_results']:
            validation_results = scenario_info['last_run_results'].get('validation_results', None)

        # Conditions (with validation indicators)
        y = self._draw_bullet_list(screen, x, y, "Conditions", metadata.conditions, (150, 200, 255), validation_results)
        y += 15

        # Edge Cases
        y = self._draw_bullet_list(screen, x, y, "Edge Cases", metadata.edge_cases, (255, 200, 100))
        y += 15

        # Expected Outcome
        y = self._draw_section_wrapped(screen, x, y, "Expected Outcome", metadata.expected_outcome, (100, 255, 150))
        y += 15

        # Pass Criteria
        y = self._draw_section_wrapped(screen, x, y, "Pass Criteria", metadata.pass_criteria, (255, 150, 150))
        y += 15

        # Validation Results (from static validation or test run)
        if 'last_run_results' in scenario_info and scenario_info['last_run_results']:
            results = scenario_info['last_run_results']
            if 'validation_results' in results:
                y += 20
                y = self._draw_validation_section(screen, x, y, results)

        y += 20

        # Metadata footer
        footer_text = f"Max Ticks: {metadata.max_ticks} | Seed: {metadata.seed}"
        footer_surf = self.small_font.render(footer_text, True, (120, 120, 120))
        screen.blit(footer_surf, (x, y))

    def _draw_section(self, screen, x, y, label, text, color):
        """Draw a single-line metadata section."""
        # Label
        label_surf = self.body_font.render(f"{label}:", True, color)
        screen.blit(label_surf, (x, y))
        y += 25

        # Text
        text_surf = self.small_font.render(text, True, self.TEXT_COLOR)
        screen.blit(text_surf, (x + 10, y))
        y += 22

        return y

    def _draw_section_wrapped(self, screen, x, y, label, text, color):
        """Draw a metadata section with text wrapping."""
        # Label
        label_surf = self.body_font.render(f"{label}:", True, color)
        screen.blit(label_surf, (x, y))
        y += 25

        # Wrapped text
        y = self._draw_wrapped_text(screen, text, x + 10, y, self.metadata_width - 40, self.TEXT_COLOR)
        y += 5

        return y

    def _draw_bullet_list(self, screen, x, y, label, items, color, validation_results=None):
        """Draw a bullet list section with optional validation indicators."""
        # Label
        label_surf = self.body_font.render(f"{label}:", True, color)
        screen.blit(label_surf, (x, y))
        y += 25

        # Items
        if not items:
            none_surf = self.small_font.render("None", True, (120, 120, 120))
            screen.blit(none_surf, (x + 20, y))
            y += 22
        else:
            for item in items:
                bullet_surf = self.small_font.render(f"• {item}", True, self.TEXT_COLOR)
                screen.blit(bullet_surf, (x + 10, y))

                # Check if this item is verified by validation results
                if validation_results and self._is_condition_verified(item, validation_results):
                    # Draw green "V" on right edge
                    v_surf = self.body_font.render("V", True, (80, 255, 120))  # Green
                    v_x = x + self.metadata_width - 40  # Right edge with padding
                    screen.blit(v_surf, (v_x, y - 2))

                y += 22

        return y

    def _is_condition_verified(self, condition_text, validation_results):
        """
        Check if a condition is verified by a passing validation.

        Args:
            condition_text: Text like "Beam Damage: 5 per hit"
            validation_results: List of validation result dicts

        Returns:
            True if condition matches a PASS validation
        """
        # Map condition text patterns to validation rule names
        mappings = {
            'Beam Damage': 'Beam Weapon Damage',
            'Base Accuracy': 'Base Accuracy',
            'Accuracy Falloff': 'Accuracy Falloff',
            'Weapon Max Range': 'Weapon Range',
            'Distance': None,  # Distance is test setup, not component property
            'Net Score': None,  # Calculated value, complex validation
            'Test Duration': None  # Test parameter, not validated
        }

        # Check direct validations
        for pattern, validation_name in mappings.items():
            if validation_name and pattern in condition_text:
                # Find matching validation result
                for vr in validation_results:
                    if vr['name'] == validation_name and vr['status'] == 'PASS':
                        return True

        # Special case: Range Penalty (calculated from distance × accuracy_falloff)
        if 'Range Penalty' in condition_text:
            # Extract values from condition text like "Range Penalty: 50 * 0.002 = 0.1"
            try:
                import re
                # Match pattern: "Range Penalty: {distance} * {falloff} = {result}"
                match = re.search(r'Range Penalty:\s*(\d+\.?\d*)\s*\*\s*(\d+\.?\d*)\s*=\s*(\d+\.?\d*)', condition_text)
                if match:
                    distance_stated = float(match.group(1))
                    falloff_stated = float(match.group(2))
                    penalty_stated = float(match.group(3))

                    # Check if falloff is verified
                    falloff_verified = False
                    falloff_actual = None
                    for vr in validation_results:
                        if vr['name'] == 'Accuracy Falloff' and vr['status'] == 'PASS':
                            falloff_verified = True
                            falloff_actual = vr['actual']
                            break

                    if falloff_verified and falloff_actual is not None:
                        # Verify the calculation is correct
                        calculated_penalty = distance_stated * falloff_actual
                        if abs(calculated_penalty - penalty_stated) < 0.0001:  # Float comparison with tolerance
                            return True
            except (ValueError, TypeError):
                pass  # If parsing fails, don't show V

        return False

    def _draw_wrapped_text(self, screen, text, x, y, max_width, color):
        """Draw text with word wrapping."""
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surf = self.small_font.render(test_line, True, color)

            if test_surf.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        # Draw lines
        for line in lines:
            line_surf = self.small_font.render(line, True, color)
            screen.blit(line_surf, (x, y))
            y += 20

        return y

    def _draw_validation_section(self, screen, x, y, results):
        """Draw validation results section with color-coded status."""
        # Section header
        header_surf = self.body_font.render("Validation Results:", True, (255, 200, 100))
        screen.blit(header_surf, (x, y))
        y += 25

        validation_results = results.get('validation_results', [])
        validation_summary = results.get('validation_summary', {})

        if not validation_results:
            no_val_surf = self.small_font.render("No validation rules defined", True, (120, 120, 120))
            screen.blit(no_val_surf, (x + 10, y))
            return y + 22

        # Summary counts
        pass_count = validation_summary.get('pass', 0)
        fail_count = validation_summary.get('fail', 0)
        warn_count = validation_summary.get('warn', 0)

        # Determine overall status color
        if fail_count > 0:
            summary_color = (255, 80, 80)  # Red
            status_symbol = "✗"
        elif warn_count > 0:
            summary_color = (255, 200, 80)  # Yellow/Orange
            status_symbol = "⚠"
        else:
            summary_color = (80, 255, 120)  # Green
            status_symbol = "✓"

        # Summary line
        summary_text = f"{status_symbol} {pass_count} Pass, {fail_count} Fail, {warn_count} Warn"
        summary_surf = self.small_font.render(summary_text, True, summary_color)
        screen.blit(summary_surf, (x + 10, y))
        y += 25

        # Individual validation results
        for vr in validation_results:
            status = vr['status']
            name = vr['name']
            expected = vr['expected']
            actual = vr['actual']
            p_value = vr.get('p_value')

            # Status color
            if status == 'PASS':
                status_color = (80, 255, 120)
                symbol = "✓"
            elif status == 'FAIL':
                status_color = (255, 80, 80)
                symbol = "✗"
            elif status == 'WARN':
                status_color = (255, 200, 80)
                symbol = "⚠"
            else:
                status_color = (120, 120, 200)
                symbol = "ℹ"

            # Validation name with symbol
            name_surf = self.small_font.render(f"{symbol} {name}", True, status_color)
            screen.blit(name_surf, (x + 10, y))
            y += 20

            # Expected vs Actual
            if expected is not None and actual is not None:
                # Format as percentage if between 0 and 1
                if isinstance(expected, (int, float)) and 0 <= expected <= 1:
                    exp_str = f"{expected:.2%}"
                else:
                    exp_str = str(expected)

                if isinstance(actual, (int, float)) and 0 <= actual <= 1:
                    act_str = f"{actual:.2%}"
                else:
                    act_str = str(actual)

                exp_act_text = f"Expected: {exp_str} | Actual: {act_str}"
                exp_act_surf = self.small_font.render(exp_act_text, True, (180, 180, 180))
                screen.blit(exp_act_surf, (x + 25, y))
                y += 18

            # P-value (for statistical tests - TOST interpretation)
            if p_value is not None:
                p_text = f"p-value: {p_value:.4f}"
                if p_value < 0.05:
                    p_color = (100, 255, 150)  # Green - proven equivalent (PASS)
                else:
                    p_color = (255, 100, 100)  # Red - not proven equivalent (FAIL)

                p_surf = self.small_font.render(p_text, True, p_color)
                screen.blit(p_surf, (x + 25, y))
                y += 18

            y += 5  # Space between validation items

        # Add "Update Expected Values" button if there are failures
        if fail_count > 0:
            y += 10
            button_width = 200
            button_height = 35
            button_x = x + 10
            button_y = y

            # Store button rect for click detection
            self.update_expected_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            self.update_expected_button_visible = True

            # Draw button
            button_color = (60, 120, 200)  # Blue
            button_hover_color = (80, 140, 220)

            # Check if mouse is over button
            mouse_pos = pygame.mouse.get_pos()
            is_hover = self.update_expected_button_rect.collidepoint(mouse_pos)
            current_color = button_hover_color if is_hover else button_color

            # Draw button background
            pygame.draw.rect(screen, current_color, self.update_expected_button_rect)
            pygame.draw.rect(screen, (100, 140, 200), self.update_expected_button_rect, 2)

            # Draw button text
            button_text = "Update Expected Values"
            button_surf = self.small_font.render(button_text, True, (255, 255, 255))
            text_x = button_x + (button_width - button_surf.get_width()) // 2
            text_y = button_y + (button_height - button_surf.get_height()) // 2
            screen.blit(button_surf, (text_x, text_y))

            y += button_height + 10
        else:
            self.update_expected_button_visible = False

        return y

    def _draw_validation_flag(self, screen, x, y, scenario_info):
        """
        Draw a colored flag/circle indicating validation status.

        Green circle = All validations passed
        Yellow circle = Warnings present
        Red circle = Failures present
        Gray circle = No validation data (test not run yet)
        """
        radius = 10

        # Check for validation results
        last_run_results = scenario_info.get('last_run_results')

        if not last_run_results or 'validation_results' not in last_run_results:
            # No validation data - gray circle
            color = (100, 100, 100)
            symbol = None
        else:
            validation_summary = last_run_results.get('validation_summary', {})
            fail_count = validation_summary.get('fail', 0)
            warn_count = validation_summary.get('warn', 0)

            if fail_count > 0:
                # Failures - red circle with X
                color = (255, 80, 80)
                symbol = "✗"
            elif warn_count > 0:
                # Warnings - yellow circle with !
                color = (255, 200, 80)
                symbol = "⚠"
            else:
                # All passed - green circle with checkmark
                color = (80, 255, 120)
                symbol = "✓"

        # Draw circle
        pygame.draw.circle(screen, color, (x, y), radius)
        pygame.draw.circle(screen, (0, 0, 0), (x, y), radius, 2)  # Black outline

        # Draw symbol if present
        if symbol:
            symbol_surf = self.small_font.render(symbol, True, (0, 0, 0))
            symbol_rect = symbol_surf.get_rect(center=(x, y))
            screen.blit(symbol_surf, symbol_rect)

    def _show_ships_json(self, test_id):
        """Show JSON for all ships used in the test."""
        if test_id is None:
            return

        scenario_info = self.registry.get_by_id(test_id)
        if not scenario_info:
            return

        # Load ship JSON files from test data
        ships_data = {}

        # Get ship filenames from test scenario
        # This is a simplified approach - we'll try to find ship files mentioned in conditions
        metadata = scenario_info['metadata']

        # Extract ship filenames from conditions
        ship_files = []
        for condition in metadata.conditions:
            if '.json' in condition and ('Attacker:' in condition or 'Target:' in condition):
                parts = condition.split(':')
                if len(parts) > 1:
                    filename = parts[1].strip()
                    ship_files.append(filename)

        # Load ship JSON files
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'simulation_tests', 'data', 'ships')

        for ship_file in ship_files:
            ship_path = os.path.join(data_dir, ship_file)
            ship_data = load_json(ship_path)
            if ship_data is not None:
                ships_data[ship_file] = ship_data
            elif os.path.exists(ship_path):
                ships_data[ship_file] = "Error loading ship file"

        if not ships_data:
            ships_data = {"error": "No ship files found for this test"}

        self.json_popup = JSONPopup(f"Ships JSON - {test_id}", ships_data, WIDTH, HEIGHT)

    def _show_components_json(self):
        """Show JSON for all components in the test data."""
        # Load components.json from test data
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'simulation_tests', 'data')
        components_path = os.path.join(data_dir, 'components.json')

        components_data = load_json(components_path)
        if components_data is not None:
            self.json_popup = JSONPopup("Components JSON", components_data, WIDTH, HEIGHT)
        else:
            self.json_popup = JSONPopup("Components JSON", {"error": "components.json not found or invalid"}, WIDTH, HEIGHT)

    def _draw_output_log(self, screen):
        """Draw the output log at the bottom."""
        y = HEIGHT - 90
        for i, msg in enumerate(self.output_log[-3:]):
            color = (255, 100, 100) if "ERROR" in msg else (150, 150, 150)
            txt = self.small_font.render(msg, True, color)
            screen.blit(txt, (20, y + i * 20))
