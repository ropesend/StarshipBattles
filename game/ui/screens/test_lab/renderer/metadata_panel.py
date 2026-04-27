"""Metadata / Test Details panel.

Extracted from `renderer.py` by PROJ-309 sub-phase 3.3.

Viewmodel writes:
- ``viewmodel.run_test_btn_rect`` — pygame.Rect
- ``viewmodel.run_headless_btn_rect`` — pygame.Rect
- ``viewmodel.run_baseline_btn_rect`` — pygame.Rect | None
"""
from __future__ import annotations

import pygame

from game.ui.screens.test_lab import theme
from game.core.config import DisplayConfig

from ._draw_helpers import draw_section, draw_section_wrapped, draw_bullet_list
from .validation_panel import ValidationPanel

WIDTH, HEIGHT = DisplayConfig.DEFAULT_WIDTH, DisplayConfig.DEFAULT_HEIGHT


class MetadataPanel:
    """Renders the Test Details panel: run buttons + metadata sections."""

    def __init__(
        self,
        header_font: pygame.font.Font,
        body_font: pygame.font.Font,
        small_font: pygame.font.Font,
        header_color: tuple,
        text_color: tuple,
        panel_bg: tuple,
        border_color: tuple,
        category_width: int,
        test_list_width: int,
        metadata_width: int,
        header_height: int,
        validation_panel: ValidationPanel,
    ) -> None:
        self.header_font = header_font
        self.body_font = body_font
        self.small_font = small_font
        self.HEADER_COLOR = header_color
        self.TEXT_COLOR = text_color
        self.PANEL_BG = panel_bg
        self.BORDER_COLOR = border_color
        self.category_width = category_width
        self.test_list_width = test_list_width
        self.metadata_width = metadata_width
        self.header_height = header_height
        self.validation_panel = validation_panel

    def draw(self, screen: pygame.Surface, controller, registry, viewmodel) -> None:
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

        selected_test_id = controller.ui_state.get_selected_test_id()

        # Run buttons to the right of header (only if a test is selected)
        if selected_test_id is not None:
            self._draw_run_buttons(screen, x, y, selected_test_id, registry, viewmodel)

        y += 40

        if selected_test_id is None:
            hint_text = self.body_font.render("Select a test to view details", True, theme.TEXT_DIM)
            screen.blit(hint_text, (x + 20, y + 20))
            return

        # Get selected test metadata
        scenario_info = registry.get_by_id(selected_test_id)
        if scenario_info is None:
            return

        metadata = scenario_info['metadata']

        # Test ID
        y = draw_section(
            screen, self.body_font, self.small_font, x, y,
            "Test ID", metadata.test_id, self.HEADER_COLOR,
        )
        y += 10

        # Category
        category_text = f"{metadata.category} > {metadata.subcategory}"
        y = draw_section(
            screen, self.body_font, self.small_font, x, y,
            "Category", category_text, theme.SECTION_CATEGORY,
        )
        y += 10

        # Summary
        y = draw_section_wrapped(
            screen, self.body_font, self.small_font, x, y,
            "Summary", metadata.summary, theme.SECTION_SUMMARY, self.metadata_width,
        )
        y += 15

        # Get validation results if available
        validation_results = None
        if 'last_run_results' in scenario_info and scenario_info['last_run_results']:
            validation_results = scenario_info['last_run_results'].get('validation_results', None)

        # Conditions (with validation indicators)
        y = draw_bullet_list(
            screen, self.body_font, self.small_font, x, y,
            "Conditions", metadata.conditions, theme.SECTION_CONDITIONS,
            self.metadata_width, validation_results,
        )
        y += 15

        # Edge Cases
        y = draw_bullet_list(
            screen, self.body_font, self.small_font, x, y,
            "Edge Cases", metadata.edge_cases, theme.SECTION_EDGE_CASES,
            self.metadata_width,
        )
        y += 15

        # Expected Outcome
        y = draw_section_wrapped(
            screen, self.body_font, self.small_font, x, y,
            "Expected Outcome", metadata.expected_outcome, theme.SECTION_OUTCOME,
            self.metadata_width,
        )
        y += 15

        # Pass Criteria
        y = draw_section_wrapped(
            screen, self.body_font, self.small_font, x, y,
            "Pass Criteria", metadata.pass_criteria, theme.SECTION_CRITERIA,
            self.metadata_width,
        )
        y += 15

        # Validation Results (from static validation or test run)
        if 'last_run_results' in scenario_info and scenario_info['last_run_results']:
            results = scenario_info['last_run_results']
            if 'validation_results' in results:
                y += 20
                y = self.validation_panel.draw(screen, x, y, results, viewmodel)

        y += 20

        # Metadata footer - just show max ticks (seed controls are now in header)
        ticks_text = f"Max Ticks: {metadata.max_ticks}    |    Test Seed: {metadata.seed}"
        ticks_surf = self.small_font.render(ticks_text, True, theme.TEXT_VERY_DIM)
        screen.blit(ticks_surf, (x, y))

    def _draw_run_buttons(
        self,
        screen: pygame.Surface,
        x: int,
        y: int,
        selected_test_id: str,
        registry,
        viewmodel,
    ) -> None:
        """Draw the Visual Run / Headless Run / Visual Baseline buttons."""
        mouse_pos = pygame.mouse.get_pos()
        btn_height = 26
        btn_spacing = 10
        header_btn_y = y - 8

        # Visual Run button (green)
        visual_btn_width = 90
        visual_btn_x = x + self.metadata_width - 220
        run_test_btn_rect = pygame.Rect(visual_btn_x, header_btn_y, visual_btn_width, btn_height)
        viewmodel.run_test_btn_rect = run_test_btn_rect
        run_test_hover = run_test_btn_rect.collidepoint(mouse_pos)
        run_test_color = theme.BUTTON_RUN_HOVER if run_test_hover else theme.BUTTON_RUN_BG
        pygame.draw.rect(screen, run_test_color, run_test_btn_rect, border_radius=4)
        pygame.draw.rect(screen, theme.BUTTON_RUN_BORDER, run_test_btn_rect, 1, border_radius=4)
        run_text = self.small_font.render("Visual Run", True, theme.BUTTON_RUN_TEXT)
        text_rect = run_text.get_rect(center=run_test_btn_rect.center)
        screen.blit(run_text, text_rect)

        # Headless Run button (blue)
        headless_btn_width = 100
        headless_btn_x = visual_btn_x + visual_btn_width + btn_spacing
        run_headless_btn_rect = pygame.Rect(
            headless_btn_x, header_btn_y, headless_btn_width, btn_height
        )
        viewmodel.run_headless_btn_rect = run_headless_btn_rect
        run_headless_hover = run_headless_btn_rect.collidepoint(mouse_pos)
        run_headless_color = theme.BUTTON_HEADLESS_HOVER if run_headless_hover else theme.BUTTON_HEADLESS_BG
        pygame.draw.rect(screen, run_headless_color, run_headless_btn_rect, border_radius=4)
        pygame.draw.rect(screen, theme.BUTTON_HEADLESS_BORDER, run_headless_btn_rect, 1, border_radius=4)
        headless_text = self.small_font.render("Headless Run", True, theme.BUTTON_HEADLESS_TEXT)
        text_rect = headless_text.get_rect(center=run_headless_btn_rect.center)
        screen.blit(headless_text, text_rect)

        # Visual Baseline button (amber) — second row, only for ComparisonScenario
        scenario_info = registry.get_by_id(selected_test_id)
        if scenario_info and scenario_info.get('is_comparison'):
            baseline_btn_width = 120
            baseline_btn_y = header_btn_y + btn_height + 4
            run_baseline_btn_rect = pygame.Rect(
                visual_btn_x, baseline_btn_y, baseline_btn_width, btn_height
            )
            viewmodel.run_baseline_btn_rect = run_baseline_btn_rect
            baseline_hover = run_baseline_btn_rect.collidepoint(mouse_pos)
            baseline_color = theme.BUTTON_BASELINE_HOVER if baseline_hover else theme.BUTTON_BASELINE_BG
            pygame.draw.rect(screen, baseline_color, run_baseline_btn_rect, border_radius=4)
            pygame.draw.rect(screen, theme.BUTTON_BASELINE_BORDER, run_baseline_btn_rect, 1, border_radius=4)
            baseline_text = self.small_font.render("Visual Baseline", True, theme.BUTTON_BASELINE_TEXT)
            text_rect = baseline_text.get_rect(center=run_baseline_btn_rect.center)
            screen.blit(baseline_text, text_rect)
        else:
            viewmodel.run_baseline_btn_rect = None
