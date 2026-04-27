"""
Battle State Viewer - Side-by-side JSON viewer with diff highlighting.

Displays initial and final battle states in two independently scrollable columns
with visual highlighting of changed, added, and removed values.

This is a thin coordinator that:
- Creates two ScrollableJsonPanel widgets
- Computes the diff between initial and final states
- Handles layout and close button
- Draws the legend
"""
from __future__ import annotations

import pygame
import json
from typing import Optional

from game.ui.utils.json_diff import compute_json_diff, DiffResult
from game.ui.widgets.scrollable_json_panel import ScrollableJsonPanel
from game.ui.fonts import get_font, FONT_MONO
from game.ui.colors import (
    WHITE, DIFF_CHANGED_BG, DIFF_CHANGED_TEXT, DIFF_ADDED_BG, DIFF_ADDED_TEXT,
    DIFF_REMOVED_BG, DIFF_REMOVED_TEXT, VIEWER_BTN_BG, VIEWER_BTN_HOVER,
    VIEWER_BTN_BORDER, SWATCH_BORDER
)


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
        self.header_font = get_font(24, FONT_MONO)
        self.button_font = get_font(16, FONT_MONO)
        self.legend_font = get_font(14, FONT_MONO)

        # Colors
        self.overlay_color = (0, 0, 0, 200)
        self.header_color = WHITE
        self.button_color = VIEWER_BTN_BG
        self.button_hover_color = VIEWER_BTN_HOVER

        # State info
        self.test_id = None
        self.run_number = None

        # Stats
        self.diff_stats = {'changed': 0, 'added': 0, 'removed': 0}

    def show(self, initial_json: Optional[str], final_json: Optional[str],
             test_id: str = None, run_number: int = None) -> None:
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

    def hide(self) -> None:
        """Hide the viewer."""
        self.visible = False

    def handle_resize(self, width: int, height: int) -> None:
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

        self.initial_panel.scroll.reset()
        self.final_panel.scroll.reset()

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

    def draw(self, surface) -> None:
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
        pygame.draw.rect(surface, VIEWER_BTN_BORDER, self.close_button_rect, 2, border_radius=5)

        button_text = self.button_font.render("Close (ESC)", True, WHITE)
        text_x = self.close_button_rect.x + (self.close_button_rect.width - button_text.get_width()) // 2
        text_y = self.close_button_rect.y + (self.close_button_rect.height - button_text.get_height()) // 2
        surface.blit(button_text, (text_x, text_y))

    def _draw_legend(self, surface) -> None:
        """Draw the diff legend at the bottom."""
        legend_y = self.screen_height - self.margin - 70

        # Legend items
        items = [
            (DIFF_CHANGED_BG, DIFF_CHANGED_TEXT, f"Changed ({self.diff_stats['changed']})"),
            (DIFF_ADDED_BG, DIFF_ADDED_TEXT, f"Added ({self.diff_stats['added']})"),
            (DIFF_REMOVED_BG, DIFF_REMOVED_TEXT, f"Removed ({self.diff_stats['removed']})"),
        ]

        total_width = sum(100 + self.legend_font.size(text)[0] for _, _, text in items) + 40
        start_x = (self.screen_width - total_width) // 2

        x = start_x
        for bg_color, text_color, label in items:
            # Color swatch
            swatch_rect = pygame.Rect(x, legend_y + 2, 20, 16)
            pygame.draw.rect(surface, bg_color, swatch_rect)
            pygame.draw.rect(surface, SWATCH_BORDER, swatch_rect, 1)

            # Label
            label_surf = self.legend_font.render(label, True, text_color)
            surface.blit(label_surf, (x + 28, legend_y))

            x += 28 + label_surf.get_width() + 30
