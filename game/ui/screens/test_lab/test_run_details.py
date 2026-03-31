"""Test run details panel for Combat Lab UI.

Displays detailed information for a selected test run.
"""

import pygame

from game.core.string_utils import display_name
from game.ui.colors import TEST_PASS, TEST_FAIL
from game.ui.fonts import get_font
from game.ui.screens.test_lab import theme
from game.ui.widgets.scroll_state import ScrollState
from game.ui.screens.test_lab.formatting_utils import format_value


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

    def set_run(self, run_record, run_number):
        """Set the run to display details for."""
        self.selected_run = (run_record, run_number)
        self.scroll.reset()
        self._calculate_scroll()

    def clear(self):
        """Clear selected run."""
        self.selected_run = None
        self.scroll.reset()

    def _calculate_scroll(self):
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

    def handle_event(self, event):
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

    def draw(self, surface):
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

        # Run info header and status
        y_offset = self._draw_header_and_status(surface, run_record, run_number, y_offset)

        # Seed and Ticks info
        y_offset = self._draw_metadata(surface, run_record, y_offset)

        # Action buttons (View States, Use Seed, Copy Results)
        y_offset = self._draw_action_buttons(surface, run_record, y_offset)

        # TEST OUTCOMES section for propulsion tests
        if self._is_propulsion_test(run_record):
            y_offset = self._draw_propulsion_outcomes(surface, run_record, y_offset)
            y_offset += 10

        # RESOURCE CONSUMPTION section for resource tests
        if self._is_resource_test(run_record):
            y_offset = self._draw_resource_outcomes(surface, run_record, y_offset)
            y_offset += 10

        # Metrics
        y_offset = self._draw_metrics(surface, run_record, y_offset)

        # Validation Results
        y_offset = self._draw_validation_results(surface, run_record, y_offset)

        surface.set_clip(None)
        if self.scroll.can_scroll:
            self._draw_scrollbar(surface)

    def _draw_header_and_status(self, surface, run_record, run_number, y_offset):
        """Draw run info header and pass/fail status.

        Returns updated y_offset.
        """
        # Run info header
        timestamp_str = run_record.get_formatted_timestamp()
        header_text = f"Run #{run_number} - {timestamp_str}"
        header_surf = self.header_font.render(header_text, True, self.text_color)
        surface.blit(header_surf, (self.x + 10, y_offset))
        y_offset += 30

        # Status
        status_text = "PASSED" if run_record.passed else "FAILED"
        status_color = self.pass_color if run_record.passed else self.fail_color
        status_surf = self.title_font.render(status_text, True, status_color)
        surface.blit(status_surf, (self.x + 10, y_offset))
        y_offset += 25

        return y_offset

    def _draw_metadata(self, surface, run_record, y_offset):
        """Draw seed and ticks information.

        Returns updated y_offset.
        """
        if run_record.seed is not None:
            seed_text = f"Seed: {run_record.seed}"
            seed_surf = self.small_font.render(seed_text, True, theme.TEXT_SECONDARY)
            surface.blit(seed_surf, (self.x + 15, y_offset))

        ticks_run = run_record.metrics.get('ticks_run')
        if ticks_run is not None:
            ticks_text = f"Ticks: {ticks_run}"
            ticks_surf = self.small_font.render(ticks_text, True, theme.TEXT_SECONDARY)
            # Position ticks to the right of seed (or at start if no seed)
            ticks_x = self.x + 180 if run_record.seed is not None else self.x + 15
            surface.blit(ticks_surf, (ticks_x, y_offset))

        return y_offset

    def _draw_action_buttons(self, surface, run_record, y_offset):
        """Draw View States, Use Seed, and Copy Results buttons.

        Returns updated y_offset.
        """
        y_offset -= 25  # Reset for button positioning

        # View States button (if battle states are available)
        self.view_states_button_rect = None
        if run_record.has_battle_states():
            button_width = 110
            button_height = 26
            button_x = self.x + self.width - button_width - 15
            button_y = y_offset - 5 + self.scroll.offset  # Account for scroll in positioning

            # Only show button if it's in the visible area
            if button_y >= self.y and button_y + button_height <= self.y + self.height:
                self.view_states_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

                mouse_pos = pygame.mouse.get_pos()
                is_hovered = self.view_states_button_rect.collidepoint(mouse_pos)
                btn_color = self.button_hover_color if is_hovered else self.button_color

                pygame.draw.rect(surface, btn_color, self.view_states_button_rect, border_radius=4)
                pygame.draw.rect(surface, theme.BUTTON_VIEW_STATES_BORDER, self.view_states_button_rect, 1, border_radius=4)

                btn_text = self.small_font.render("View States", True, theme.TEXT_WHITE)
                text_x = button_x + (button_width - btn_text.get_width()) // 2
                text_y = button_y + (button_height - btn_text.get_height()) // 2
                surface.blit(btn_text, (text_x, text_y))

        # Use Seed button (always show if seed is available)
        self.use_seed_button_rect = None
        if run_record.seed is not None:
            button_width = 80
            button_height = 26
            # Position to the left of View States button (or at the right if no View States)
            if self.view_states_button_rect:
                button_x = self.view_states_button_rect.x - button_width - 10
            else:
                button_x = self.x + self.width - button_width - 15
            button_y = y_offset - 5 + self.scroll.offset

            # Only show button if it's in the visible area
            if button_y >= self.y and button_y + button_height <= self.y + self.height:
                self.use_seed_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

                mouse_pos = pygame.mouse.get_pos()
                is_hovered = self.use_seed_button_rect.collidepoint(mouse_pos)
                btn_color = self.button_hover_color if is_hovered else self.button_color

                pygame.draw.rect(surface, btn_color, self.use_seed_button_rect, border_radius=4)
                pygame.draw.rect(surface, theme.BUTTON_USE_SEED_BORDER, self.use_seed_button_rect, 1, border_radius=4)

                btn_text = self.small_font.render("Use Seed", True, theme.TEXT_WHITE)
                text_x = button_x + (button_width - btn_text.get_width()) // 2
                text_y = button_y + (button_height - btn_text.get_height()) // 2
                surface.blit(btn_text, (text_x, text_y))

        # Copy Results button (always show)
        self.copy_results_button_rect = None
        button_width = 90
        button_height = 26
        # Position to the left of Use Seed button (or at the right if no Use Seed)
        if self.use_seed_button_rect:
            button_x = self.use_seed_button_rect.x - button_width - 10
        elif self.view_states_button_rect:
            button_x = self.view_states_button_rect.x - button_width - 10
        else:
            button_x = self.x + self.width - button_width - 15
        button_y = y_offset - 5 + self.scroll.offset

        # Only show button if it's in the visible area
        if button_y >= self.y and button_y + button_height <= self.y + self.height:
            self.copy_results_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

            mouse_pos = pygame.mouse.get_pos()
            is_hovered = self.copy_results_button_rect.collidepoint(mouse_pos)
            btn_color = self.button_hover_color if is_hovered else self.button_color

            pygame.draw.rect(surface, btn_color, self.copy_results_button_rect, border_radius=4)
            pygame.draw.rect(surface, theme.BUTTON_COPY_BORDER, self.copy_results_button_rect, 1, border_radius=4)

            btn_text = self.small_font.render("Copy Results", True, theme.TEXT_WHITE)
            text_x = button_x + (button_width - btn_text.get_width()) // 2
            text_y = button_y + (button_height - btn_text.get_height()) // 2
            surface.blit(btn_text, (text_x, text_y))

        y_offset += 40

        return y_offset

    def _draw_metrics(self, surface, run_record, y_offset):
        """Draw test metrics section.

        Returns updated y_offset.
        """
        metrics_title = self.header_font.render("Test Metrics", True, self.header_color)
        surface.blit(metrics_title, (self.x + 10, y_offset))
        y_offset += 25

        for key, value in run_record.metrics.items():
            if key not in ['validation_results', 'validation_summary']:
                if isinstance(value, float):
                    value_str = f"{value:.1%}" if 0 < value < 1 else f"{value:.2f}"
                else:
                    value_str = str(value)
                display_key = display_name(key)
                metric_text = f"  {display_key}: {value_str}"
                metric_surf = self.small_font.render(metric_text, True, self.text_color)
                surface.blit(metric_surf, (self.x + 15, y_offset))
                y_offset += 20

        y_offset += 10

        return y_offset

    def _draw_validation_results(self, surface, run_record, y_offset):
        """Draw validation results section grouped by phase with expected/actual/status.

        Checks are grouped into DATA, PRECONDITION, and OUTCOME phases.
        Each check shows a green/red indicator, name, expected, actual, and detail.

        Returns updated y_offset.
        """
        if not run_record.validation_results:
            return y_offset

        val_title = self.header_font.render("VALIDATION RESULTS", True, self.header_color)
        surface.blit(val_title, (self.x + 10, y_offset))
        y_offset += 25

        # Draw separator line
        pygame.draw.line(surface, theme.SEPARATOR_LINE,
                       (self.x + 10, y_offset), (self.x + self.width - 20, y_offset))
        y_offset += 8

        # Group by phase
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

        grouped = {p: [] for p in phase_order}
        for vr in run_record.validation_results:
            phase = vr.get('phase', 'outcome')
            if phase not in grouped:
                phase = 'outcome'
            grouped[phase].append(vr)

        for phase in phase_order:
            checks = grouped[phase]
            if not checks:
                continue

            # Phase header
            phase_label = phase_labels[phase]
            phase_color = phase_colors[phase]
            phase_surf = self.body_font.render(phase_label, True, phase_color)
            surface.blit(phase_surf, (self.x + 15, y_offset))
            y_offset += 22

            # Individual checks
            for vr in checks:
                y_offset = self._draw_single_validation(surface, vr, y_offset)

            y_offset += 5  # Space between phase groups

        return y_offset

    def _draw_single_validation(self, surface, vr, y_offset):
        """Draw a single validation result item.

        Returns updated y_offset.
        """
        status = vr.get('status', 'PASS')
        name = vr.get('name', '')
        expected = vr.get('expected')
        actual = vr.get('actual')
        detail = vr.get('detail')
        p_value = vr.get('p_value')

        # Determine colors based on status
        if status == 'PASS':
            status_color = self.pass_color
            symbol = "V"
            actual_color = self.pass_color
        elif status == 'FAIL':
            status_color = self.fail_color
            symbol = "X"
            actual_color = self.fail_color
        else:
            status_color = theme.STATUS_WARNING
            symbol = "!"
            actual_color = theme.STATUS_WARNING

        # Validation name with symbol (color-coded)
        val_line = f"{symbol} {name}"
        val_surf = self.small_font.render(val_line, True, status_color)
        surface.blit(val_surf, (self.x + 20, y_offset))
        y_offset += 18

        # Define layout constants
        label_color = theme.TEXT_LABEL
        expected_color = theme.TEXT_EXPECTED
        indent = 30
        label_width = 75

        # Show expected value (if present)
        if expected is not None:
            exp_str = format_value(expected, precision="full")
            exp_label = self.small_font.render("Expected:", True, label_color)
            exp_value = self.small_font.render(exp_str, True, expected_color)
            surface.blit(exp_label, (self.x + indent, y_offset))
            surface.blit(exp_value, (self.x + indent + label_width, y_offset))
            y_offset += 16

        # Show actual value (color-coded green/red based on status)
        if actual is not None:
            act_str = format_value(actual, precision="full")
            act_label = self.small_font.render("Actual:", True, label_color)
            act_value = self.small_font.render(act_str, True, actual_color)
            surface.blit(act_label, (self.x + indent, y_offset))
            surface.blit(act_value, (self.x + indent + label_width, y_offset))
            y_offset += 16

        # Show difference/percentage (if both values are numeric)
        if expected is not None and actual is not None:
            y_offset = self._draw_numeric_difference(
                surface, expected, actual, status, y_offset, indent, label_width
            )

        # P-value (for statistical tests)
        if p_value is not None:
            label_color = theme.TEXT_LABEL
            p_color = self.pass_color if p_value < 0.05 else self.fail_color
            p_str = f"{p_value:.6f}"
            if p_value < 0.05:
                p_str += " (proven equivalent)"
            else:
                p_str += " (not proven equivalent)"
            p_label = self.small_font.render("p-value:", True, label_color)
            p_value_surf = self.small_font.render(p_str, True, p_color)
            surface.blit(p_label, (self.x + indent, y_offset))
            surface.blit(p_value_surf, (self.x + indent + label_width, y_offset))
            y_offset += 16

        # Detail string (e.g. TOST info, tolerance)
        if detail:
            detail_label = self.small_font.render("Detail:", True, label_color)
            detail_value = self.small_font.render(str(detail), True, theme.TEXT_MUTED)
            surface.blit(detail_label, (self.x + indent, y_offset))
            surface.blit(detail_value, (self.x + indent + label_width, y_offset))
            y_offset += 16

        y_offset += 10  # Space between validation items

        # Draw subtle separator between validation items
        pygame.draw.line(surface, theme.SEPARATOR_SUBTLE,
                       (self.x + 20, y_offset - 5), (self.x + self.width - 30, y_offset - 5))

        return y_offset

    def _draw_numeric_difference(self, surface, expected, actual, status, y_offset, indent, label_width):
        """Draw the difference/percentage line for numeric values.

        Returns updated y_offset.
        """
        if not (isinstance(expected, (int, float)) and isinstance(actual, (int, float))):
            return y_offset
        # Skip difference for boolean checks — True/False are int subclasses
        # but computing "1000 vs True = +99900%" is meaningless
        if isinstance(expected, bool) or isinstance(actual, bool):
            return y_offset

        label_color = theme.TEXT_LABEL
        diff = actual - expected
        abs_diff = abs(diff)

        if expected != 0:
            pct_diff = (diff / expected) * 100
            abs_pct_diff = abs(pct_diff)

            if abs_pct_diff < 1e-9:
                diff_str = "EXACT MATCH"
                diff_color = self.pass_color
            elif abs_pct_diff < 0.01:
                diff_str = f"{pct_diff:+.6f}% (essentially exact)"
                diff_color = self.pass_color
            else:
                diff_str = f"{pct_diff:+.4f}%"
                diff_color = self.pass_color if status == 'PASS' else self.fail_color
        else:
            if abs_diff < 1e-9:
                diff_str = "EXACT MATCH"
                diff_color = self.pass_color
            else:
                diff_str = f"Diff: {diff:+.6f}"
                diff_color = self.pass_color if status == 'PASS' else self.fail_color

        diff_label = self.small_font.render("Difference:", True, label_color)
        diff_value = self.small_font.render(diff_str, True, diff_color)
        surface.blit(diff_label, (self.x + indent, y_offset))
        surface.blit(diff_value, (self.x + indent + label_width, y_offset))
        y_offset += 16

        return y_offset

    def _is_propulsion_test(self, run_record):
        """Check if this run record is from a propulsion test."""
        test_id = run_record.metrics.get('test_id', '')
        return test_id.startswith('PROP-')

    def _is_resource_test(self, run_record):
        """Check if this run record is from a resource test."""
        test_id = run_record.metrics.get('test_id', '')
        return test_id.startswith('RESOURCE-')

    def _draw_resource_outcomes(self, surface, run_record, y_offset):
        """Draw resource test outcomes section (detailed view)."""
        metrics = run_record.metrics
        test_id = metrics.get('test_id', '')

        # Section header
        outcomes_title = self.header_font.render("RESOURCE CONSUMPTION", True, self.header_color)
        surface.blit(outcomes_title, (self.x + 10, y_offset))
        y_offset += 25

        # Draw separator line
        pygame.draw.line(surface, theme.SEPARATOR_LINE,
                        (self.x + 10, y_offset), (self.x + self.width - 20, y_offset))
        y_offset += 8

        # Define colors
        label_color = theme.TEXT_LABEL
        value_color = theme.TEXT_EXPECTED
        highlight_color = theme.STATUS_HIGHLIGHT
        indent = 15
        label_width = 100

        # Determine resource type and draw appropriate outcomes
        if 'RESOURCE-001' <= test_id <= 'RESOURCE-003':
            # Fuel tests
            y_offset = self._draw_fuel_outcomes(surface, metrics, y_offset,
                                                 label_color, value_color, highlight_color,
                                                 indent, label_width)
        elif 'RESOURCE-004' <= test_id <= 'RESOURCE-005a':
            # Energy tests
            y_offset = self._draw_energy_outcomes(surface, metrics, y_offset,
                                                   label_color, value_color, highlight_color,
                                                   indent, label_width)
        else:
            # Ammo tests (RESOURCE-006 to RESOURCE-008)
            y_offset = self._draw_ammo_outcomes(surface, metrics, y_offset,
                                                 label_color, value_color, highlight_color,
                                                 indent, label_width, test_id)

        return y_offset

    def _draw_fuel_outcomes(self, surface, metrics, y_offset, label_color, value_color,
                            highlight_color, indent, label_width):
        """Draw fuel test outcomes."""
        initial_fuel = metrics.get('initial_fuel', 0)
        final_fuel = metrics.get('final_fuel', 0)
        fuel_consumed = initial_fuel - final_fuel
        expected_consumed = metrics.get('expected_fuel_consumed', fuel_consumed)

        # Initial Fuel
        label = self.small_font.render("Initial Fuel:", True, label_color)
        value = self.small_font.render(f"{initial_fuel:.1f} units", True, value_color)
        surface.blit(label, (self.x + indent, y_offset))
        surface.blit(value, (self.x + indent + label_width, y_offset))
        y_offset += 18

        # Final Fuel
        label = self.small_font.render("Final Fuel:", True, label_color)
        value = self.small_font.render(f"{final_fuel:.1f} units", True, value_color)
        surface.blit(label, (self.x + indent, y_offset))
        surface.blit(value, (self.x + indent + label_width, y_offset))
        y_offset += 18

        # Consumed
        label = self.small_font.render("Consumed:", True, label_color)
        value = self.small_font.render(f"{fuel_consumed:.2f} units", True, highlight_color)
        surface.blit(label, (self.x + indent, y_offset))
        surface.blit(value, (self.x + indent + label_width, y_offset))
        y_offset += 18

        # Expected
        label = self.small_font.render("Expected:", True, label_color)
        expected_text = f"{expected_consumed:.2f} units"
        value = self.small_font.render(expected_text, True, value_color)
        surface.blit(label, (self.x + indent, y_offset))
        surface.blit(value, (self.x + indent + label_width, y_offset))
        y_offset += 18

        # Tolerance check
        tolerance = abs(fuel_consumed - expected_consumed)
        if tolerance < 0.5:
            status_text = "Within tolerance"
            status_color = self.pass_color
        else:
            status_text = f"Difference: {tolerance:.2f}"
            status_color = self.fail_color
        status_surf = self.small_font.render(status_text, True, status_color)
        surface.blit(status_surf, (self.x + indent, y_offset))
        y_offset += 18

        # Velocity status
        final_velocity = metrics.get('final_velocity', 0)
        label = self.small_font.render("Final Velocity:", True, label_color)
        if final_velocity > 0.1:
            vel_text = f"{final_velocity:.2f} (moving)"
            vel_color = self.pass_color
        else:
            vel_text = "0 (stopped)"
            vel_color = theme.STATUS_WARNING
        value = self.small_font.render(vel_text, True, vel_color)
        surface.blit(label, (self.x + indent, y_offset))
        surface.blit(value, (self.x + indent + label_width, y_offset))
        y_offset += 18

        return y_offset

    def _draw_energy_outcomes(self, surface, metrics, y_offset, label_color, value_color,
                               highlight_color, indent, label_width):
        """Draw energy test outcomes."""
        initial_energy = metrics.get('initial_energy', 0)
        final_energy = metrics.get('final_energy', 0)
        energy_consumed = initial_energy - final_energy
        shots_fired = metrics.get('shots_fired', 0)
        damage_dealt = metrics.get('damage_dealt', 0)

        # Initial Energy
        label = self.small_font.render("Initial Energy:", True, label_color)
        value = self.small_font.render(f"{initial_energy:.1f} units", True, value_color)
        surface.blit(label, (self.x + indent, y_offset))
        surface.blit(value, (self.x + indent + label_width, y_offset))
        y_offset += 18

        # Final Energy
        label = self.small_font.render("Final Energy:", True, label_color)
        if final_energy <= 0:
            energy_text = "0 (depleted)"
            energy_color = theme.STATUS_WARNING
        else:
            energy_text = f"{final_energy:.1f} units"
            energy_color = value_color
        value = self.small_font.render(energy_text, True, energy_color)
        surface.blit(label, (self.x + indent, y_offset))
        surface.blit(value, (self.x + indent + label_width, y_offset))
        y_offset += 18

        # Energy Consumed
        label = self.small_font.render("Consumed:", True, label_color)
        value = self.small_font.render(f"{energy_consumed:.1f} units", True, highlight_color)
        surface.blit(label, (self.x + indent, y_offset))
        surface.blit(value, (self.x + indent + label_width, y_offset))
        y_offset += 18

        # Shots Fired
        label = self.small_font.render("Shots Fired:", True, label_color)
        value = self.small_font.render(f"{shots_fired}", True, value_color)
        surface.blit(label, (self.x + indent, y_offset))
        surface.blit(value, (self.x + indent + label_width, y_offset))
        y_offset += 18

        # Damage Dealt
        label = self.small_font.render("Damage Dealt:", True, label_color)
        value = self.small_font.render(f"{damage_dealt:.0f}", True, highlight_color)
        surface.blit(label, (self.x + indent, y_offset))
        surface.blit(value, (self.x + indent + label_width, y_offset))
        y_offset += 18

        # Efficiency (energy per damage)
        if damage_dealt > 0:
            efficiency = energy_consumed / damage_dealt
            label = self.small_font.render("Energy/Damage:", True, label_color)
            value = self.small_font.render(f"{efficiency:.2f}", True, value_color)
            surface.blit(label, (self.x + indent, y_offset))
            surface.blit(value, (self.x + indent + label_width, y_offset))
            y_offset += 18

        return y_offset

    def _draw_ammo_outcomes(self, surface, metrics, y_offset, label_color, value_color,
                             highlight_color, indent, label_width, test_id):
        """Draw ammo test outcomes."""
        initial_ammo = metrics.get('initial_ammo', 0)
        final_ammo = metrics.get('final_ammo', 0)
        ammo_consumed = initial_ammo - final_ammo

        is_seeker = test_id == 'RESOURCE-008'
        shots_fired = metrics.get('launches' if is_seeker else 'shots_fired', 0)

        # Initial Ammo
        label = self.small_font.render("Initial Ammo:", True, label_color)
        value = self.small_font.render(f"{initial_ammo:.0f} units", True, value_color)
        surface.blit(label, (self.x + indent, y_offset))
        surface.blit(value, (self.x + indent + label_width, y_offset))
        y_offset += 18

        # Final Ammo
        label = self.small_font.render("Final Ammo:", True, label_color)
        if final_ammo <= 0:
            ammo_text = "0 (depleted)"
            ammo_color = theme.STATUS_WARNING
        else:
            ammo_text = f"{final_ammo:.0f} units"
            ammo_color = value_color
        value = self.small_font.render(ammo_text, True, ammo_color)
        surface.blit(label, (self.x + indent, y_offset))
        surface.blit(value, (self.x + indent + label_width, y_offset))
        y_offset += 18

        # Ammo Consumed
        label = self.small_font.render("Consumed:", True, label_color)
        value = self.small_font.render(f"{ammo_consumed:.0f} units", True, highlight_color)
        surface.blit(label, (self.x + indent, y_offset))
        surface.blit(value, (self.x + indent + label_width, y_offset))
        y_offset += 18

        # Shots/Launches
        if is_seeker:
            label = self.small_font.render("Launches:", True, label_color)
            value = self.small_font.render(f"{shots_fired}", True, value_color)
            surface.blit(label, (self.x + indent, y_offset))
            surface.blit(value, (self.x + indent + label_width, y_offset))
            y_offset += 18

            # Note about seeker hits
            note = self.small_font.render("(Hits not tracked - seekers in flight)", True, theme.TEXT_DIM_BLUE)
            surface.blit(note, (self.x + indent, y_offset))
            y_offset += 18
        else:
            # Shots Fired
            label = self.small_font.render("Shots Fired:", True, label_color)
            value = self.small_font.render(f"{shots_fired}", True, value_color)
            surface.blit(label, (self.x + indent, y_offset))
            surface.blit(value, (self.x + indent + label_width, y_offset))
            y_offset += 18

            # Damage Dealt
            damage_dealt = metrics.get('damage_dealt', 0)
            label = self.small_font.render("Damage Dealt:", True, label_color)
            value = self.small_font.render(f"{damage_dealt:.0f}", True, highlight_color)
            surface.blit(label, (self.x + indent, y_offset))
            surface.blit(value, (self.x + indent + label_width, y_offset))
            y_offset += 18

        return y_offset

    def _draw_propulsion_outcomes(self, surface, run_record, y_offset):
        """Draw propulsion test outcomes section."""
        metrics = run_record.metrics

        # Section header
        outcomes_title = self.header_font.render("TEST OUTCOMES", True, self.header_color)
        surface.blit(outcomes_title, (self.x + 10, y_offset))
        y_offset += 25

        # Draw separator line
        pygame.draw.line(surface, theme.SEPARATOR_LINE,
                        (self.x + 10, y_offset), (self.x + self.width - 20, y_offset))
        y_offset += 8

        # Determine test type based on metrics
        is_turn_test = (
            metrics.get('angle_change', 0) > 0.01 and
            metrics.get('turn_speed', 0) > 0
        )
        has_motion = metrics.get('final_velocity_magnitude', 0) > 0.1

        # Define colors
        label_color = theme.TEXT_LABEL
        value_color = theme.TEXT_EXPECTED
        highlight_color = theme.STATUS_HIGHLIGHT

        if is_turn_test:
            # Turn test outcomes
            y_offset = self._draw_turn_outcomes(surface, metrics, y_offset,
                                                label_color, value_color, highlight_color)
        elif has_motion:
            # Motion test outcomes
            y_offset = self._draw_motion_outcomes(surface, metrics, y_offset,
                                                   label_color, value_color, highlight_color)
        else:
            # Stationary test
            y_offset = self._draw_stationary_outcomes(surface, metrics, y_offset,
                                                       label_color, value_color)

        return y_offset

    def _draw_motion_outcomes(self, surface, metrics, y_offset, label_color, value_color, highlight_color):
        """Draw motion test outcomes (velocity, position, distance)."""
        indent = 15

        # Velocity
        start_vel = metrics.get('initial_velocity_magnitude', 0)
        end_vel = metrics.get('final_velocity_magnitude', 0)
        max_speed = metrics.get('expected_max_speed')

        vel_label = self.small_font.render("Velocity:", True, label_color)
        surface.blit(vel_label, (self.x + indent, y_offset))

        vel_text = f"{start_vel:.1f} -> {end_vel:.2f}"
        if max_speed is not None:
            vel_text += f" (max: {max_speed:.2f})"
        vel_surf = self.small_font.render(vel_text, True, value_color)
        surface.blit(vel_surf, (self.x + indent + 75, y_offset))
        y_offset += 18

        # Position
        start_pos = metrics.get('initial_position')
        end_pos = metrics.get('final_position')
        if start_pos and end_pos:
            pos_label = self.small_font.render("Position:", True, label_color)
            surface.blit(pos_label, (self.x + indent, y_offset))

            start_str = f"({start_pos[0]:.1f}, {start_pos[1]:.1f})"
            end_str = f"({end_pos[0]:.1f}, {end_pos[1]:.1f})"
            pos_text = f"{start_str} -> {end_str}"
            pos_surf = self.small_font.render(pos_text, True, value_color)
            surface.blit(pos_surf, (self.x + indent + 75, y_offset))
            y_offset += 18

        # Distance
        distance = metrics.get('distance_traveled')
        if distance is not None:
            dist_label = self.small_font.render("Distance:", True, label_color)
            surface.blit(dist_label, (self.x + indent, y_offset))

            dist_surf = self.small_font.render(f"{distance:.1f} px", True, highlight_color)
            surface.blit(dist_surf, (self.x + indent + 75, y_offset))
            y_offset += 18

        return y_offset

    def _draw_turn_outcomes(self, surface, metrics, y_offset, label_color, value_color, highlight_color):
        """Draw turn test outcomes (angles, expected vs actual)."""
        indent = 15

        # Angle change
        start_angle = metrics.get('initial_angle', 0)
        end_angle = metrics.get('final_angle', 0)
        angle_change = metrics.get('angle_change', 0)

        angle_label = self.small_font.render("Angle:", True, label_color)
        surface.blit(angle_label, (self.x + indent, y_offset))

        angle_text = f"{start_angle:.1f} -> {end_angle:.1f} deg (change: {angle_change:.2f})"
        angle_surf = self.small_font.render(angle_text, True, value_color)
        surface.blit(angle_surf, (self.x + indent + 75, y_offset))
        y_offset += 18

        # Expected vs actual angle change
        expected_angle = metrics.get('expected_angle_change')
        if expected_angle is not None:
            exp_label = self.small_font.render("Expected:", True, label_color)
            surface.blit(exp_label, (self.x + indent, y_offset))

            exp_text = f"{expected_angle:.2f} deg"
            exp_surf = self.small_font.render(exp_text, True, value_color)
            surface.blit(exp_surf, (self.x + indent + 75, y_offset))
            y_offset += 18

            act_label = self.small_font.render("Actual:", True, label_color)
            surface.blit(act_label, (self.x + indent, y_offset))

            # Color code based on accuracy
            error = abs(angle_change - expected_angle)
            actual_color = self.pass_color if error < 0.1 else self.fail_color
            act_text = f"{angle_change:.2f} deg"
            act_surf = self.small_font.render(act_text, True, actual_color)
            surface.blit(act_surf, (self.x + indent + 75, y_offset))
            y_offset += 18

            # Show error
            err_label = self.small_font.render("Error:", True, label_color)
            surface.blit(err_label, (self.x + indent, y_offset))

            err_text = f"{error:.4f} deg"
            err_color = self.pass_color if error < 0.1 else self.fail_color
            err_surf = self.small_font.render(err_text, True, err_color)
            surface.blit(err_surf, (self.x + indent + 75, y_offset))
            y_offset += 18

        # Turn speed
        turn_speed = metrics.get('turn_speed')
        if turn_speed is not None:
            ts_label = self.small_font.render("Turn Speed:", True, label_color)
            surface.blit(ts_label, (self.x + indent, y_offset))

            ts_text = f"{turn_speed:.4f} deg/100 ticks"
            ts_surf = self.small_font.render(ts_text, True, highlight_color)
            surface.blit(ts_surf, (self.x + indent + 75, y_offset))
            y_offset += 18

        return y_offset

    def _draw_stationary_outcomes(self, surface, metrics, y_offset, label_color, value_color):
        """Draw stationary test outcomes (no motion)."""
        indent = 15

        # Show that velocity is zero
        vel_label = self.small_font.render("Velocity:", True, label_color)
        surface.blit(vel_label, (self.x + indent, y_offset))

        vel_surf = self.small_font.render("0.0 (stationary)", True, value_color)
        surface.blit(vel_surf, (self.x + indent + 75, y_offset))
        y_offset += 18

        # Distance should be zero
        distance = metrics.get('distance_traveled', 0)
        dist_label = self.small_font.render("Distance:", True, label_color)
        surface.blit(dist_label, (self.x + indent, y_offset))

        dist_surf = self.small_font.render(f"{distance:.1f} px", True, value_color)
        surface.blit(dist_surf, (self.x + indent + 75, y_offset))
        y_offset += 18

        return y_offset

    def _draw_scrollbar(self, surface):
        """Draw scrollbar indicator."""
        visible_height = self.height
        total_content_height = visible_height + self.scroll.max_offset
        scrollbar_width = 8
        scrollbar_x = self.x + self.width - scrollbar_width - 5
        scrollbar_track_y = self.y + 5
        scrollbar_track_height = visible_height - 10
        thumb_height = max(30, int(visible_height * (visible_height / total_content_height)))
        thumb_y = scrollbar_track_y + int(self.scroll.scroll_ratio * (scrollbar_track_height - thumb_height))
        pygame.draw.rect(surface, theme.SCROLLBAR_THUMB, (scrollbar_x, thumb_y, scrollbar_width, thumb_height), border_radius=4)
