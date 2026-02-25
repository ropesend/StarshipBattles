"""Test run card component for Combat Lab UI.

Displays a single test run in collapsed card form.
"""

import pygame

from game.ui.colors import TEST_PASS, TEST_FAIL
from game.ui.fonts import get_font
from game.ui.screens.test_lab import theme
from game.ui.screens.test_lab.formatting_utils import format_value


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
        self.bg_color = theme.BG_CATEGORY
        self.bg_hover_color = (45, 45, 50)  # Unique hover state
        self.bg_selected_color = theme.SELECTED_CARD_BG
        self.latest_bg_color = (40, 45, 50)  # Slightly different for latest
        self.pass_color = TEST_PASS
        self.fail_color = TEST_FAIL
        self.text_color = theme.TEXT
        self.border_color = theme.BORDER_ACTIVE
        self.border_pass_color = TEST_PASS
        self.border_fail_color = TEST_FAIL
        self.border_selected_color = theme.SELECTED_BORDER

        # Fonts
        self.title_font = get_font(16)
        self.body_font = get_font(14)
        self.small_font = get_font(12)

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
        status_text = "PASS" if self.run_record.passed else "FAIL"
        status_color = self.pass_color if self.run_record.passed else self.fail_color
        status_surf = self.title_font.render(status_text, True, status_color)
        status_x = self.x + self.width - status_surf.get_width() - 10
        surface.blit(status_surf, (status_x, self.y + 10))

        # Check if this is a propulsion test - show propulsion-specific metrics
        metrics = self.run_record.metrics
        test_id = metrics.get('test_id', '')
        if test_id.startswith('PROP-'):
            self._draw_propulsion_metrics(surface, metrics)
            return  # Skip validation/hit_rate display for propulsion tests

        # Check if this is a resource test - show resource-specific metrics
        if test_id.startswith('RESOURCE-'):
            self._draw_resource_metrics(surface, metrics)
            return  # Skip validation/hit_rate display for resource tests

        # Show first key validation result (expected vs actual)
        key_validation_shown = False
        if self.run_record.validation_results:
            # Find first validation with expected/actual (prioritize failures)
            key_val = None
            for vr in self.run_record.validation_results:
                if vr.get('expected') is not None and vr.get('actual') is not None:
                    if vr['status'] == 'FAIL':
                        key_val = vr
                        break
                    elif key_val is None:
                        key_val = vr

            if key_val:
                name = key_val['name']
                expected = key_val['expected']
                actual = key_val['actual']
                val_status = key_val['status']

                # Truncate name if too long
                if len(name) > 25:
                    name = name[:22] + "..."

                # Format values
                exp_str = format_value(expected, precision="compact")
                act_str = format_value(actual, precision="compact")

                # Color-code actual based on status
                actual_color = self.pass_color if val_status == 'PASS' else self.fail_color

                # Display: "Name: Expected=X Actual=Y"
                name_surf = self.body_font.render(f"{name}:", True, self.text_color)
                surface.blit(name_surf, (self.x + 10, self.y + 35))

                exp_label = self.small_font.render("Exp:", True, theme.TEXT_LABEL)
                exp_value = self.small_font.render(exp_str, True, theme.TEXT_EXPECTED)
                act_label = self.small_font.render("Act:", True, theme.TEXT_LABEL)
                act_value = self.small_font.render(act_str, True, actual_color)

                # Position: Name: | Exp: X | Act: Y
                x_pos = self.x + 10
                surface.blit(exp_label, (x_pos, self.y + 55))
                surface.blit(exp_value, (x_pos + 30, self.y + 55))
                surface.blit(act_label, (x_pos + 100, self.y + 55))
                surface.blit(act_value, (x_pos + 130, self.y + 55))

                key_validation_shown = True

        # Fallback: show hit rate for beam tests if no validation results
        if not key_validation_shown:
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

                exp_surf = self.body_font.render(exp_text, True, theme.TEXT_MUTED)
                surface.blit(exp_surf, (self.x + 260, self.y + 35))

        # Validation summary on bottom right
        val_summary = self.run_record.validation_summary
        if val_summary:
            pass_count = val_summary.get('pass', 0)
            fail_count = val_summary.get('fail', 0)
            warn_count = val_summary.get('warn', 0)
            summary_text = f"{pass_count}P {fail_count}F {warn_count}W"
            summary_surf = self.body_font.render(summary_text, True, theme.TEXT_MUTED)
            summary_x = self.x + self.width - summary_surf.get_width() - 10
            surface.blit(summary_surf, (summary_x, self.y + 57))

        # P-value if present (statistical tests)
        p_value = self.run_record.get_p_value()
        if p_value is not None and not key_validation_shown:
            # Color code p-value (TOST: p < 0.05 is green/PASS, p >= 0.05 is red/FAIL)
            p_color = self.pass_color if p_value < 0.05 else self.fail_color
            p_text = f"p={p_value:.4f}"
            p_surf = self.small_font.render(p_text, True, p_color)
            surface.blit(p_surf, (self.x + 10, self.y + 57))

    def _draw_propulsion_metrics(self, surface, metrics):
        """Draw propulsion-specific metrics on the card."""
        # Determine if this is a motion test or turn test
        is_turn_test = (
            metrics.get('angle_change', 0) > 0.01 and
            metrics.get('turn_speed', 0) > 0
        )
        has_motion = metrics.get('final_velocity_magnitude', 0) > 0.1

        if is_turn_test:
            # Turn test: show angle data
            start_angle = metrics.get('initial_angle', 0)
            end_angle = metrics.get('final_angle', 0)
            expected_change = metrics.get('expected_angle_change', 0)
            actual_change = metrics.get('angle_change', 0)

            # Angle line
            angle_text = f"Angle: {start_angle:.1f} -> {end_angle:.1f}"
            angle_surf = self.body_font.render(angle_text, True, self.text_color)
            surface.blit(angle_surf, (self.x + 10, self.y + 35))

            # Expected vs Actual
            if expected_change > 0:
                angle_match = abs(actual_change - expected_change) < 0.5
                act_color = self.pass_color if angle_match else self.fail_color
                exp_text = f"Exp: {expected_change:.2f}"
                act_text = f"Act: {actual_change:.2f}"
                exp_surf = self.small_font.render(exp_text, True, theme.TEXT_EXPECTED)
                act_surf = self.small_font.render(act_text, True, act_color)
                surface.blit(exp_surf, (self.x + 10, self.y + 55))
                surface.blit(act_surf, (self.x + 100, self.y + 55))

        elif has_motion:
            # Motion test: show velocity and distance
            start_vel = metrics.get('initial_velocity_magnitude', 0)
            end_vel = metrics.get('final_velocity_magnitude', 0)
            max_speed = metrics.get('expected_max_speed', 0)
            distance = metrics.get('distance_traveled', 0)

            # Velocity line
            vel_text = f"Velocity: {start_vel:.1f} -> {end_vel:.2f}"
            if max_speed > 0:
                vel_text += f" (max: {max_speed:.1f})"
            vel_surf = self.body_font.render(vel_text, True, self.text_color)
            surface.blit(vel_surf, (self.x + 10, self.y + 35))

            # Distance line
            dist_text = f"Distance: {distance:.1f} px"
            dist_surf = self.small_font.render(dist_text, True, theme.TEXT_MUTED)
            surface.blit(dist_surf, (self.x + 10, self.y + 55))

        else:
            # Stationary test (no motion, no turn)
            vel_text = "Velocity: 0 (no engine)"
            vel_surf = self.body_font.render(vel_text, True, self.text_color)
            surface.blit(vel_surf, (self.x + 10, self.y + 35))

            distance = metrics.get('distance_traveled', 0)
            dist_text = f"Distance: {distance:.1f} px"
            dist_surf = self.small_font.render(dist_text, True, theme.TEXT_MUTED)
            surface.blit(dist_surf, (self.x + 10, self.y + 55))

        # Validation summary on bottom right
        val_summary = self.run_record.validation_summary
        if val_summary:
            pass_count = val_summary.get('pass', 0)
            fail_count = val_summary.get('fail', 0)
            warn_count = val_summary.get('warn', 0)
            summary_text = f"{pass_count}P {fail_count}F {warn_count}W"
            summary_surf = self.body_font.render(summary_text, True, theme.TEXT_MUTED)
            summary_x = self.x + self.width - summary_surf.get_width() - 10
            surface.blit(summary_surf, (summary_x, self.y + 57))

    def _draw_resource_metrics(self, surface, metrics):
        """Draw resource-specific metrics on the card (brief display)."""
        test_id = metrics.get('test_id', '')

        # Determine resource type based on test ID
        if 'RESOURCE-001' <= test_id <= 'RESOURCE-003':
            # Fuel tests
            initial_fuel = metrics.get('initial_fuel', 0)
            final_fuel = metrics.get('final_fuel', 0)
            fuel_consumed = initial_fuel - final_fuel

            # Fuel line
            fuel_text = f"Fuel: {initial_fuel:.0f} -> {final_fuel:.1f} ({fuel_consumed:+.1f})"
            fuel_surf = self.body_font.render(fuel_text, True, self.text_color)
            surface.blit(fuel_surf, (self.x + 10, self.y + 35))

            # Velocity/status line
            final_velocity = metrics.get('final_velocity', 0)
            if final_velocity > 0.1:
                vel_text = f"Velocity: {final_velocity:.2f} (moving)"
                vel_color = self.pass_color
            else:
                vel_text = "Velocity: 0 (stopped)"
                vel_color = theme.STATUS_WARNING if test_id == 'RESOURCE-002' else self.fail_color
            vel_surf = self.small_font.render(vel_text, True, vel_color)
            surface.blit(vel_surf, (self.x + 10, self.y + 55))

        elif 'RESOURCE-004' <= test_id <= 'RESOURCE-005a':
            # Energy tests
            initial_energy = metrics.get('initial_energy', 0)
            final_energy = metrics.get('final_energy', 0)
            shots_fired = metrics.get('shots_fired', 0)
            damage_dealt = metrics.get('damage_dealt', 0)

            # Energy line
            energy_text = f"Energy: {initial_energy:.0f} -> {final_energy:.1f}"
            if final_energy <= 0:
                energy_text += " (depleted)"
            energy_surf = self.body_font.render(energy_text, True, self.text_color)
            surface.blit(energy_surf, (self.x + 10, self.y + 35))

            # Shots/Hits line
            shots_text = f"Shots: {shots_fired}, Damage: {damage_dealt:.0f}"
            shots_surf = self.small_font.render(shots_text, True, theme.TEXT_MUTED)
            surface.blit(shots_surf, (self.x + 10, self.y + 55))

        else:
            # Ammo tests (RESOURCE-006 to RESOURCE-008)
            initial_ammo = metrics.get('initial_ammo', 0)
            final_ammo = metrics.get('final_ammo', 0)
            shots_fired = metrics.get('shots_fired', metrics.get('launches', 0))

            # Ammo line
            ammo_text = f"Ammo: {initial_ammo:.0f} -> {final_ammo:.1f}"
            if final_ammo <= 0:
                ammo_text += " (depleted)"
            ammo_surf = self.body_font.render(ammo_text, True, self.text_color)
            surface.blit(ammo_surf, (self.x + 10, self.y + 35))

            # Shots/damage line (for projectile/seeker)
            if test_id == 'RESOURCE-008':
                # Seeker test - show launches only
                shots_text = f"Launches: {shots_fired}"
            else:
                damage_dealt = metrics.get('damage_dealt', 0)
                shots_text = f"Shots: {shots_fired}, Damage: {damage_dealt:.0f}"
            shots_surf = self.small_font.render(shots_text, True, theme.TEXT_MUTED)
            surface.blit(shots_surf, (self.x + 10, self.y + 55))

        # Validation summary on bottom right
        val_summary = self.run_record.validation_summary
        if val_summary:
            pass_count = val_summary.get('pass', 0)
            fail_count = val_summary.get('fail', 0)
            warn_count = val_summary.get('warn', 0)
            summary_text = f"{pass_count}P {fail_count}F {warn_count}W"
            summary_surf = self.body_font.render(summary_text, True, theme.TEXT_MUTED)
            summary_x = self.x + self.width - summary_surf.get_width() - 10
            surface.blit(summary_surf, (summary_x, self.y + 57))
