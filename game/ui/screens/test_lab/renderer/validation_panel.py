"""Validation results sub-panel.

Extracted from `renderer.py` by PROJ-309 sub-phase 3.3.

This module must NOT import from any sibling panel — only from
`_draw_helpers` and `_condition_logic`. (Avoids cycle with metadata_panel.)

Viewmodel writes:
- ``viewmodel.update_expected_button_rect`` — pygame.Rect
- ``viewmodel.update_expected_button_visible`` — bool
"""
from __future__ import annotations

from typing import Any, Dict

import pygame

from game.ui.colors import TEST_PASS, TEST_FAIL
from game.ui.screens.test_lab import theme

from ._condition_logic import format_check_pair


class ValidationPanel:
    """Renders the Validation Results sub-section of the metadata panel."""

    def __init__(
        self,
        body_font: pygame.font.Font,
        small_font: pygame.font.Font,
    ) -> None:
        self.body_font = body_font
        self.small_font = small_font

    def draw(
        self,
        screen: pygame.Surface,
        x: int,
        y: int,
        results: Dict[str, Any],
        viewmodel,
    ) -> int:
        """Draw validation results section grouped by phase with color-coded status."""
        # Section header
        header_surf = self.body_font.render("Validation Results:", True, theme.STATUS_HIGHLIGHT)
        screen.blit(header_surf, (x, y))
        y += 25

        validation_results = results.get('validation_results', [])
        validation_summary = results.get('validation_summary', {})

        if not validation_results:
            no_val_surf = self.small_font.render("No validation rules defined", True, theme.TEXT_VERY_DIM)
            screen.blit(no_val_surf, (x + 10, y))
            return y + 22

        # Summary counts
        pass_count = validation_summary.get('pass', 0)
        fail_count = validation_summary.get('fail', 0)
        warn_count = validation_summary.get('warn', 0)

        # Determine overall status color
        if fail_count > 0:
            summary_color = TEST_FAIL
            status_symbol = "X"
        elif warn_count > 0:
            summary_color = theme.STATUS_WARNING
            status_symbol = "!"
        else:
            summary_color = TEST_PASS
            status_symbol = "V"

        # Summary line
        summary_text = f"{status_symbol} {pass_count} Pass, {fail_count} Fail, {warn_count} Warn"
        summary_surf = self.small_font.render(summary_text, True, summary_color)
        screen.blit(summary_surf, (x + 10, y))
        y += 25

        # Group validation results by phase
        phase_order = ['data', 'precondition', 'outcome']
        phase_labels = {
            'data': 'DATA CHECKS',
            'precondition': 'PRECONDITION CHECKS',
            'outcome': 'OUTCOME CHECKS',
        }
        phase_colors = {
            'data': theme.PHASE_DATA,
            'precondition': theme.PHASE_PRECONDITION,
            'outcome': theme.PHASE_OUTCOME,
        }

        grouped: Dict[str, list] = {p: [] for p in phase_order}
        for vr in validation_results:
            phase = vr.get('phase', 'outcome')
            if phase not in grouped:
                phase = 'outcome'
            grouped[phase].append(vr)

        # Draw each phase group
        for phase in phase_order:
            checks = grouped[phase]
            if not checks:
                continue

            # Phase header
            phase_label = phase_labels[phase]
            phase_color = phase_colors[phase]
            phase_surf = self.small_font.render(phase_label, True, phase_color)
            screen.blit(phase_surf, (x + 10, y))
            y += 20

            # Individual checks in this phase
            for vr in checks:
                y = self._draw_check_compact(screen, x, y, vr)

            y += 5  # Space between phase groups

        # Add "Update Expected Values" button if there are failures
        if fail_count > 0:
            y += 10
            button_width = 200
            button_height = 35
            button_x = x + 10
            button_y = y

            # Store button rect for click detection
            viewmodel.update_expected_button_rect = pygame.Rect(
                button_x, button_y, button_width, button_height
            )
            viewmodel.update_expected_button_visible = True

            # Draw button
            button_color = theme.BUTTON_BLUE
            button_hover_color = theme.BUTTON_BLUE_HOVER

            # Check if mouse is over button
            mouse_pos = pygame.mouse.get_pos()
            is_hover = viewmodel.update_expected_button_rect.collidepoint(mouse_pos)
            current_color = button_hover_color if is_hover else button_color

            # Draw button background
            pygame.draw.rect(screen, current_color, viewmodel.update_expected_button_rect)
            pygame.draw.rect(
                screen, theme.BUTTON_BLUE_BORDER, viewmodel.update_expected_button_rect, 2
            )

            # Draw button text
            button_text = "Update Expected Values"
            button_surf = self.small_font.render(button_text, True, theme.TEXT_WHITE)
            text_x = button_x + (button_width - button_surf.get_width()) // 2
            text_y = button_y + (button_height - button_surf.get_height()) // 2
            screen.blit(button_surf, (text_x, text_y))

            y += button_height + 10
        else:
            viewmodel.update_expected_button_visible = False

        return y

    def _draw_check_compact(
        self, screen: pygame.Surface, x: int, y: int, vr: Dict[str, Any]
    ) -> int:
        """Draw a single validation check with expected/actual on separate lines.

        Format:
            [symbol] Name:
                Expected: X
                Actual:   Y   (green if pass, red if fail)

        Returns updated y position.
        """
        status = vr.get('status', 'PASS')
        name = vr.get('name', '')
        expected = vr.get('expected')
        actual = vr.get('actual')
        detail = vr.get('detail')

        # Determine symbol and colors
        if status == 'PASS':
            symbol = "V"
            name_color = TEST_PASS
            actual_color = TEST_PASS
        elif status == 'FAIL':
            symbol = "X"
            name_color = TEST_FAIL
            actual_color = TEST_FAIL
        elif status == 'WARN':
            symbol = "!"
            name_color = theme.STATUS_WARNING
            actual_color = theme.STATUS_WARNING
        else:
            symbol = "i"
            name_color = theme.STATUS_INFO
            actual_color = theme.STATUS_INFO

        expected_color = (180, 200, 220)  # Light blue-gray for expected values

        # Line 1: Symbol + Name
        header = f"  {symbol} {name}:"
        screen.blit(self.small_font.render(header, True, name_color), (x + 15, y))
        y += 17

        # Format both values with identical precision
        exp_str, act_str = format_check_pair(expected, actual)

        # Use fixed label width so numbers start at the same X position
        # "Expected: " and "Actual:   " are padded to same visual width
        label_x = x + 50
        value_x = x + 145  # Numbers start here for both lines

        # Line 2: Expected value
        if expected is not None:
            screen.blit(self.small_font.render("Expected:", True, expected_color), (label_x, y))
            screen.blit(self.small_font.render(exp_str, True, expected_color), (value_x, y))
            y += 16

        # Line 3: Actual value (color-coded green/red)
        if actual is not None:
            screen.blit(self.small_font.render("Actual:", True, actual_color), (label_x, y))
            screen.blit(self.small_font.render(act_str, True, actual_color), (value_x, y))
            y += 16

        # Line 4: Detail (if any, e.g. TOST p-value)
        if detail:
            det_line = f"      {detail}"
            screen.blit(self.small_font.render(det_line, True, (140, 140, 160)), (x + 15, y))
            y += 16

        y += 4  # Spacing between checks
        return y
