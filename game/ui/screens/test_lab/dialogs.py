"""Dialog components for Combat Lab UI.

Contains popup dialogs for displaying JSON data and confirming changes.
"""

import json
import pygame
import pygame_gui
from pygame_gui.elements import UIButton

from game.core.constants import FONT_MAIN


class JSONPopup:
    """Popup window for displaying JSON data."""

    def __init__(self, title, json_data, screen_width, screen_height, ui_manager):
        """
        Create JSON popup.

        Args:
            title: Title for the popup
            json_data: Dictionary or string to display as JSON
            screen_width: Screen width
            screen_height: Screen height
            ui_manager: pygame_gui UIManager for button rendering
        """
        self.title = title
        self.json_text = json.dumps(json_data, indent=2) if isinstance(json_data, dict) else str(json_data)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.ui_manager = ui_manager

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

        # Close button (pygame_gui UIButton)
        self.close_button = UIButton(
            relative_rect=pygame.Rect(self.x + self.width - 110, self.y + 10, 100, 40),
            text="Close",
            manager=self.ui_manager
        )
        self.is_open = True

    def close(self):
        """Close the popup."""
        self.is_open = False
        if hasattr(self, 'close_button') and self.close_button:
            self.close_button.kill()

    def handle_event(self, event):
        """Handle user input."""
        # Handle pygame_gui button press
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.close_button:
                self.close()
                return True

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

        # Close button is drawn by UIManager in the main draw loop

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

    def __init__(self, title, changes, screen_width, screen_height, on_confirm, on_cancel, ui_manager):
        """
        Create confirmation dialog.

        Args:
            title: Dialog title
            changes: List of dicts with 'field', 'old_value', 'new_value'
            screen_width: Screen width
            screen_height: Screen height
            on_confirm: Callback function when confirmed
            on_cancel: Callback function when canceled
            ui_manager: pygame_gui UIManager for button rendering
        """
        self.title = title
        self.changes = changes
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.ui_manager = ui_manager

        # Dialog dimensions (60% of screen, but smaller than JSON popup)
        self.width = min(800, int(screen_width * 0.6))
        self.height = min(600, int(screen_height * 0.6))
        self.x = (screen_width - self.width) // 2
        self.y = (screen_height - self.height) // 2

        # Fonts
        self.title_font = pygame.font.SysFont(FONT_MAIN, 24)
        self.body_font = pygame.font.SysFont(FONT_MAIN, 16)
        self.small_font = pygame.font.SysFont(FONT_MAIN, 14)

        # Buttons (pygame_gui UIButton)
        button_y = self.y + self.height - 60
        button_width = 120
        button_spacing = 20
        total_button_width = button_width * 2 + button_spacing
        button_start_x = self.x + (self.width - total_button_width) // 2

        self.confirm_button = UIButton(
            relative_rect=pygame.Rect(button_start_x, button_y, button_width, 40),
            text="Confirm",
            manager=self.ui_manager
        )
        self.cancel_button = UIButton(
            relative_rect=pygame.Rect(button_start_x + button_width + button_spacing, button_y, button_width, 40),
            text="Cancel",
            manager=self.ui_manager
        )

        self.is_open = True
        self.result = None  # Will be 'confirm' or 'cancel'

    def _handle_confirm(self):
        """User confirmed changes."""
        self.result = 'confirm'
        self.is_open = False
        self._kill_buttons()
        if self.on_confirm:
            self.on_confirm()

    def _handle_cancel(self):
        """User canceled changes."""
        self.result = 'cancel'
        self.is_open = False
        self._kill_buttons()
        if self.on_cancel:
            self.on_cancel()

    def _kill_buttons(self):
        """Kill UIButtons when dialog closes."""
        if hasattr(self, 'confirm_button') and self.confirm_button:
            self.confirm_button.kill()
        if hasattr(self, 'cancel_button') and self.cancel_button:
            self.cancel_button.kill()

    def handle_event(self, event):
        """Handle user input."""
        # Handle pygame_gui button presses
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.confirm_button:
                self._handle_confirm()
                return True
            elif event.ui_element == self.cancel_button:
                self._handle_cancel()
                return True

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

        # Buttons are drawn by UIManager in the main draw loop
