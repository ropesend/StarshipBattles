"""Results panel component for Combat Lab UI.

Displays test run history with run selection.
"""

import pygame

from game.ui.fonts import get_font
from .test_run_card import TestRunCard


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
        self.title_font = get_font(20)
        self.body_font = get_font(14)
        self.small_font = get_font(12)

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
        title_text = "TEST RUN HISTORY"
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
