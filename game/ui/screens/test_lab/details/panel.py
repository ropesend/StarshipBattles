"""TestRunDetailsPanel — orchestrator for the Combat Lab test-run-details view.

PROJ-309 sub-phase 3.6 — split from a 960-line `test_run_details.py` into
this `details/` subpackage. The class owns all state (selected run, scroll,
button rects, callbacks) and dispatches per-section drawing to module-level
helpers in `chrome`, `validation`, `resource_outcomes`, `propulsion_outcomes`.

Public API is preserved exactly:
    * `__init__(x, y, width, height)`
    * `set_run(run_record, run_number)`
    * `clear()`
    * `handle_event(event) -> bool`
    * `draw(surface) -> None`
    * Attributes: `on_view_states`, `on_use_seed`, `on_copy_results`
    * Attributes: `view_states_button_rect`, `use_seed_button_rect`,
      `copy_results_button_rect` (read by `handle_event`)
"""
from __future__ import annotations

import pygame

from game.ui.colors import TEST_PASS, TEST_FAIL
from game.ui.fonts import get_font
from game.ui.screens.test_lab import theme
from game.ui.widgets.scroll_state import ScrollState

from . import chrome, validation, resource_outcomes, propulsion_outcomes
from .draw_context import DetailsDrawContext


class TestRunDetailsPanel:
    """Panel showing detailed information for selected test run."""

    def __init__(self, x, y, width, height):
        """Initialize test run details panel."""
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # Colors
        self.bg_color = theme.BG_CONTENT
        self.border_color = theme.BORDER
        self.text_color = theme.TEXT
        self.pass_color = TEST_PASS
        self.fail_color = TEST_FAIL
        self.header_color = theme.TEXT_HEADER
        self.button_color = theme.BUTTON_BLUE
        self.button_hover_color = theme.BUTTON_BLUE_HOVER

        # Fonts
        self.title_font = get_font(20)
        self.header_font = get_font(16)
        self.body_font = get_font(14)
        self.small_font = get_font(12)

        self.selected_run = None
        self.scroll = ScrollState(step=20)

        # View States button
        self.view_states_button_rect = None
        self.on_view_states = None  # Callback when button clicked

        # Use Seed button (copies seed from this run to seed control)
        self.use_seed_button_rect = None
        self.on_use_seed = None  # Callback with seed value

        # Copy Results button
        self.copy_results_button_rect = None
        self.on_copy_results = None  # Callback for copying results to clipboard

    def set_run(self, run_record, run_number) -> None:
        """Set the run to display details for."""
        self.selected_run = (run_record, run_number)
        self.scroll.reset()
        self._calculate_scroll()

    def clear(self) -> None:
        """Clear selected run."""
        self.selected_run = None
        self.scroll.reset()

    def _calculate_scroll(self) -> None:
        """Calculate max scroll based on content height."""
        if not self.selected_run:
            self.scroll.content_height = 0
            self.scroll.viewport_height = 0
            return

        run_record, _ = self.selected_run
        # Account for phase headers (~27px each, up to 3 phases)
        phase_header_height = 0
        if run_record.validation_results:
            phases_present = set(
                vr.get('phase', 'outcome') for vr in run_record.validation_results
            )
            phase_header_height = len(phases_present) * 27
        self.scroll.content_height = (
            150 + len(run_record.metrics) * 20 + 50
            + phase_header_height + len(run_record.validation_results) * 40
        )
        self.scroll.viewport_height = self.height - 20
        self.scroll.clamp()

    def handle_event(self, event) -> bool:
        """Handle scroll and click events."""
        if not self.selected_run:
            return False

        # Handle button clicks
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # View States button
            if self.view_states_button_rect and self.view_states_button_rect.collidepoint(event.pos):
                run_record, run_number = self.selected_run
                if self.on_view_states and run_record.has_battle_states():
                    self.on_view_states(run_record, run_number)
                return True

            # Use Seed button
            if self.use_seed_button_rect and self.use_seed_button_rect.collidepoint(event.pos):
                run_record, _ = self.selected_run
                if self.on_use_seed and run_record.seed is not None:
                    self.on_use_seed(run_record.seed)
                return True

            # Copy Results button
            if self.copy_results_button_rect and self.copy_results_button_rect.collidepoint(event.pos):
                run_record, run_number = self.selected_run
                if self.on_copy_results:
                    self.on_copy_results(run_record, run_number)
                return True

        if event.type == pygame.MOUSEWHEEL:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if self.x <= mouse_x <= self.x + self.width and self.y <= mouse_y <= self.y + self.height:
                if self.scroll.handle_mousewheel(event):
                    return True
        return False

    def _build_ctx(self, surface) -> DetailsDrawContext:
        """Construct a frozen draw context for the section helpers."""
        return DetailsDrawContext(
            surface=surface,
            x=self.x,
            y=self.y,
            width=self.width,
            height=self.height,
            scroll_offset=self.scroll.offset,
            title_font=self.title_font,
            header_font=self.header_font,
            body_font=self.body_font,
            small_font=self.small_font,
            pass_color=self.pass_color,
            fail_color=self.fail_color,
            header_color=self.header_color,
            text_color=self.text_color,
            button_color=self.button_color,
            button_hover_color=self.button_hover_color,
        )

    def draw(self, surface) -> None:
        """Draw the test run details panel."""
        pygame.draw.rect(surface, self.bg_color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surface, self.border_color, (self.x, self.y, self.width, self.height), 2)

        # Panel title (fixed, not scrollable)
        panel_title = self.title_font.render("DETAILED TEST RESULTS", True, self.header_color)
        surface.blit(panel_title, (self.x + 10, self.y + 10))

        if not self.selected_run:
            msg = self.body_font.render("Select a test run to view details", True, theme.TEXT_DIM)
            msg_x = self.x + (self.width - msg.get_width()) // 2
            msg_y = self.y + self.height // 2
            surface.blit(msg, (msg_x, msg_y))
            return

        run_record, run_number = self.selected_run
        clip_rect = pygame.Rect(self.x, self.y + 35, self.width, self.height - 35)
        surface.set_clip(clip_rect)

        y_offset = self.y + 40 - self.scroll.offset

        ctx = self._build_ctx(surface)

        # Run info header and status
        y_offset = chrome.draw_header_and_status(ctx, run_record, run_number, y_offset)

        # Seed and Ticks info
        y_offset = chrome.draw_metadata(ctx, run_record, y_offset)

        # Action buttons (View States, Use Seed, Copy Results)
        y_offset, button_rects = chrome.draw_action_buttons(ctx, run_record, y_offset)
        # Mirror button rects onto the panel so handle_event can hit-test them.
        self.view_states_button_rect = button_rects.view_states
        self.use_seed_button_rect = button_rects.use_seed
        self.copy_results_button_rect = button_rects.copy_results

        # TEST OUTCOMES section for propulsion tests
        if propulsion_outcomes.is_propulsion_test(run_record):
            y_offset = propulsion_outcomes.draw_propulsion_outcomes(ctx, run_record, y_offset)
            y_offset += 10

        # RESOURCE CONSUMPTION section for resource tests
        if resource_outcomes.is_resource_test(run_record):
            y_offset = resource_outcomes.draw_resource_outcomes(ctx, run_record, y_offset)
            y_offset += 10

        # Metrics
        y_offset = chrome.draw_metrics(ctx, run_record, y_offset)

        # Validation Results
        y_offset = validation.draw_validation_results(ctx, run_record, y_offset)

        surface.set_clip(None)
        if self.scroll.can_scroll:
            chrome.draw_scrollbar(ctx, self.scroll)
