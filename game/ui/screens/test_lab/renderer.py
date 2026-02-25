"""
TestLabRenderer - Rendering logic for Combat Lab UI.

Handles all drawing operations for TestLabScreen. Reads state from ViewModel
and controller, but does NOT mutate any state.

PROJ-172: Extracted from screen.py as part of MVVM decomposition.
"""
import pygame
import re
from typing import Tuple, List, Dict, Any, Optional

from game.ui.colors import TEST_PASS, TEST_FAIL
from game.ui.fonts import get_font
from game.core.config import DisplayConfig

WIDTH, HEIGHT = DisplayConfig.DEFAULT_WIDTH, DisplayConfig.DEFAULT_HEIGHT


class TestLabRenderer:
    """
    Renders the Combat Lab UI.

    All draw methods read from ViewModel/controller state and render to the screen.
    Button rects computed during rendering are stored back to the ViewModel for
    input handler use.

    This renderer does NOT mutate business state - only rect positions in ViewModel.
    """

    # Color scheme (matches original)
    BG_COLOR = (20, 20, 25)
    PANEL_BG = (25, 25, 30)
    BORDER_COLOR = (80, 80, 90)
    TEXT_COLOR = (220, 220, 220)
    HEADER_COLOR = (100, 200, 255)
    SELECTED_COLOR = (0, 100, 200)
    HOVER_COLOR = (150, 150, 150)
    CATEGORY_BG = (35, 35, 40)

    def __init__(self):
        """Initialize the renderer with fonts."""
        self.title_font = get_font(48)
        self.header_font = get_font(24)
        self.body_font = get_font(18)
        self.small_font = get_font(14)

        # Layout dimensions
        self.category_width = 220
        self.test_list_width = 420
        self.metadata_width = 540
        self.header_height = 80

    def draw(
        self,
        surface: pygame.Surface,
        viewmodel,
        controller,
        registry,
        categories: List[str],
        filtered_scenarios: Dict[str, Any],
        executor,
        ui_manager
    ) -> None:
        """
        Main draw method - renders the entire Combat Lab UI.

        Args:
            surface: Pygame surface to draw on
            viewmodel: TestLabViewModel with UI state
            controller: TestLabUIController with business state
            registry: TestRegistry for test data
            categories: List of category names
            filtered_scenarios: Dict of test_id -> scenario_info
            executor: TestLabExecutor for batch state
            ui_manager: pygame_gui UIManager
        """
        surface.fill(self.BG_COLOR)

        # Header
        self._draw_header(surface, controller, registry, viewmodel)

        # Three-column layout
        self._draw_category_sidebar(
            surface, controller, registry, categories, viewmodel
        )
        self._draw_test_list(
            surface, controller, filtered_scenarios, viewmodel, executor
        )
        self._draw_metadata_panel(
            surface, controller, registry, viewmodel
        )

        # Panels (from ViewModel)
        if viewmodel.tabbed_ship_panel:
            viewmodel.tabbed_ship_panel.draw(surface)
        for panel in viewmodel.ship_panels:
            panel.draw(surface)
        for panel in viewmodel.component_panels:
            panel.draw(surface)
        if viewmodel.results_panel:
            viewmodel.results_panel.draw(surface)
        if viewmodel.test_details_panel:
            viewmodel.test_details_panel.draw(surface)

        # Output log
        self._draw_output_log(surface, controller.output_log)

        # Update and draw pygame_gui UIManager
        ui_manager.update(1.0 / 60.0)
        ui_manager.draw_ui(surface)

        # Dialogs (drawn on top)
        if viewmodel.json_popup and viewmodel.json_popup.is_open:
            viewmodel.json_popup.draw(surface)
        if viewmodel.confirmation_dialog and viewmodel.confirmation_dialog.is_open:
            viewmodel.confirmation_dialog.draw(surface)

    def _draw_header(self, screen, controller, registry, viewmodel) -> None:
        """Draw the header with title and global seed controls."""
        title = self.title_font.render("COMBAT LAB - TEST VIEWER", True, self.HEADER_COLOR)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))

        # Draw seed controls on the right side of header
        self._draw_header_seed_controls(screen, controller, registry, viewmodel)

    def _draw_header_seed_controls(self, screen, controller, registry, viewmodel) -> None:
        """Draw global seed controls in the header area (upper right)."""
        mx, my = pygame.mouse.get_pos()

        # Position in upper right
        x = WIDTH - 450
        y = 15

        # Seed label
        seed_label = self.body_font.render("Seed Mode:", True, (180, 180, 180))
        screen.blit(seed_label, (x, y))

        # Seed mode buttons
        mode_x = x + 100
        btn_height = 24
        btn_spacing = 8

        current_mode = controller.ui_state.get_seed_mode()
        seed_mode_rects = {}

        modes = [
            ("random", "Random", 65),
            ("metadata", "Fixed", 55),
            ("custom", "Custom", 60)
        ]

        for mode_id, mode_label, btn_width in modes:
            rect = pygame.Rect(mode_x, y - 2, btn_width, btn_height)
            seed_mode_rects[mode_id] = rect

            is_active = current_mode == mode_id
            is_hovered = rect.collidepoint(mx, my)

            if is_active:
                bg_color = (40, 80, 120)
                border_color = (80, 140, 200)
                text_color = (200, 220, 255)
            elif is_hovered:
                bg_color = (50, 50, 60)
                border_color = (100, 100, 110)
                text_color = self.TEXT_COLOR
            else:
                bg_color = self.CATEGORY_BG
                border_color = self.BORDER_COLOR
                text_color = (150, 150, 150)

            pygame.draw.rect(screen, bg_color, rect, border_radius=3)
            pygame.draw.rect(screen, border_color, rect, 1, border_radius=3)

            mode_text = self.small_font.render(mode_label, True, text_color)
            text_x = rect.x + (btn_width - mode_text.get_width()) // 2
            screen.blit(mode_text, (text_x, rect.y + 4))

            mode_x += btn_width + btn_spacing

        # Store rects in viewmodel for input handler
        viewmodel.seed_mode_rects = seed_mode_rects

        # Show current seed value / input area
        seed_x = mode_x + 10
        custom_seed = controller.ui_state.get_custom_seed()
        selected_test_id = controller.ui_state.get_selected_test_id()

        if current_mode == "random":
            seed_text = "(new each run)"
            seed_color = (100, 100, 100)
        elif current_mode == "metadata":
            # Show the metadata seed if we have a selected test
            if selected_test_id:
                scenario_info = registry.get_by_id(selected_test_id)
                if scenario_info:
                    seed_text = f"= {scenario_info['metadata'].seed}"
                else:
                    seed_text = "(select test)"
            else:
                seed_text = "(select test)"
            seed_color = (100, 140, 100)
        else:  # custom
            if custom_seed is not None:
                seed_text = f"= {custom_seed}"
                seed_color = (100, 180, 255)
            else:
                seed_text = "[click to enter]"
                seed_color = (180, 140, 100)

        # Draw seed value/input area as clickable region for custom mode
        seed_surf = self.small_font.render(seed_text, True, seed_color)
        seed_rect = pygame.Rect(seed_x, y, max(seed_surf.get_width() + 10, 120), btn_height)

        if current_mode == "custom":
            # Make it look clickable
            is_hovered = seed_rect.collidepoint(mx, my)
            if is_hovered:
                pygame.draw.rect(screen, (40, 50, 60), seed_rect, border_radius=3)
            pygame.draw.rect(screen, (80, 100, 120), seed_rect, 1, border_radius=3)
            viewmodel.seed_input_rect = seed_rect
        else:
            viewmodel.seed_input_rect = None

        screen.blit(seed_surf, (seed_x + 5, y + 4))

    def _draw_category_sidebar(
        self, screen, controller, registry, categories: List[str], viewmodel
    ) -> None:
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

        selected_category = controller.ui_state.get_selected_category()
        category_hover = controller.ui_state.get_category_hover()
        all_scenarios = controller.all_scenarios

        # "All Tests" option
        all_rect = pygame.Rect(x, y, 200, 40)
        if selected_category is None:
            color = self.SELECTED_COLOR
        elif category_hover == "ALL":
            color = (50, 50, 60)
        else:
            color = self.CATEGORY_BG

        pygame.draw.rect(screen, color, all_rect, border_radius=3)
        pygame.draw.rect(screen, self.BORDER_COLOR, all_rect, 1, border_radius=3)

        all_text = self.body_font.render(f"All Tests ({len(all_scenarios)})", True, self.TEXT_COLOR)
        screen.blit(all_text, (all_rect.x + 10, all_rect.y + 10))
        y += 50

        # Category buttons
        for i, category in enumerate(categories):
            rect = pygame.Rect(x, y + i * 50, 200, 40)

            # Determine color
            if selected_category == category:
                color = self.SELECTED_COLOR
            elif category_hover == category:
                color = (50, 50, 60)
            else:
                color = self.CATEGORY_BG

            pygame.draw.rect(screen, color, rect, border_radius=3)
            pygame.draw.rect(screen, self.BORDER_COLOR, rect, 1, border_radius=3)

            # Count tests in category
            count = len(registry.get_by_category(category))
            text = self.body_font.render(f"{category} ({count})", True, self.TEXT_COLOR)
            screen.blit(text, (rect.x + 10, rect.y + 10))

        # Draw tag filter section below categories
        tag_section_y = y + len(categories) * 50 + 20
        self._draw_tag_filters(screen, x, tag_section_y, controller, registry, viewmodel)

    def _draw_tag_filters(
        self, screen, x: int, y: int, controller, registry, viewmodel
    ) -> None:
        """Draw tag filter buttons for quick filtering."""
        # Header
        header_text = self.small_font.render("TAG FILTERS", True, self.HEADER_COLOR)
        screen.blit(header_text, (x, y))
        y += 25

        # Get all unique tags from registry
        all_tags = registry.get_all_tags()

        # Prioritize common filter tags at the top
        priority_tags = ['high-tick', 'precision', 'quick']
        sorted_tags = [t for t in priority_tags if t in all_tags]
        sorted_tags += [t for t in sorted(all_tags) if t not in priority_tags]

        # Limit display to avoid overcrowding
        display_tags = sorted_tags[:8]  # Show top 8 tags

        tag_filter_rects = {}
        mx, my = pygame.mouse.get_pos()

        for i, tag in enumerate(display_tags):
            # Create tag button
            btn_width = 95
            btn_height = 24
            col = i % 2
            row = i // 2
            btn_x = x + col * (btn_width + 5)
            btn_y = y + row * (btn_height + 4)

            rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)
            tag_filter_rects[tag] = rect

            # Determine state and color
            is_active = controller.ui_state.is_tag_active(tag)
            is_excluded = controller.ui_state.is_tag_excluded(tag)
            is_hovered = rect.collidepoint(mx, my)

            if is_excluded:
                bg_color = (100, 40, 40)  # Red for excluded
                border_color = (180, 80, 80)
                text_color = (255, 150, 150)
                prefix = "X "
            elif is_active:
                bg_color = (40, 80, 40)  # Green for active
                border_color = (80, 150, 80)
                text_color = (150, 255, 150)
                prefix = "V "
            elif is_hovered:
                bg_color = (50, 50, 60)
                border_color = (100, 100, 110)
                text_color = self.TEXT_COLOR
                prefix = ""
            else:
                bg_color = self.CATEGORY_BG
                border_color = self.BORDER_COLOR
                text_color = (180, 180, 180)
                prefix = ""

            pygame.draw.rect(screen, bg_color, rect, border_radius=3)
            pygame.draw.rect(screen, border_color, rect, 1, border_radius=3)

            # Truncate tag text if needed
            display_tag = prefix + tag
            if len(display_tag) > 12:
                display_tag = display_tag[:11] + "..."
            tag_text = self.small_font.render(display_tag, True, text_color)
            screen.blit(tag_text, (rect.x + 4, rect.y + 4))

        # Store rects in viewmodel
        viewmodel.tag_filter_rects = tag_filter_rects

        # Show filter count if active
        active_count = len(controller.ui_state.get_active_tag_filters())
        excluded_count = len(controller.ui_state.get_excluded_tags())
        if active_count > 0 or excluded_count > 0:
            filter_y = y + ((len(display_tags) + 1) // 2) * 28 + 5
            if active_count > 0 and excluded_count > 0:
                filter_text = f"+{active_count} / -{excluded_count}"
            elif active_count > 0:
                filter_text = f"+{active_count} tags"
            else:
                filter_text = f"-{excluded_count} tags"

            # Clear filters button
            clear_rect = pygame.Rect(x, filter_y, 80, 20)
            is_clear_hovered = clear_rect.collidepoint(mx, my)
            clear_bg = (80, 60, 60) if is_clear_hovered else (60, 50, 50)
            pygame.draw.rect(screen, clear_bg, clear_rect, border_radius=3)
            pygame.draw.rect(screen, (120, 80, 80), clear_rect, 1, border_radius=3)
            clear_text = self.small_font.render("Clear", True, (255, 180, 180))
            screen.blit(clear_text, (clear_rect.x + 22, clear_rect.y + 3))

            # Store for click handling
            viewmodel.tag_clear_rect = clear_rect

            # Filter count display
            count_text = self.small_font.render(filter_text, True, (150, 150, 150))
            screen.blit(count_text, (x + 90, filter_y + 3))
        else:
            viewmodel.tag_clear_rect = None

    def _draw_test_list(
        self, screen, controller, filtered_scenarios: Dict[str, Any], viewmodel, executor
    ) -> None:
        """Draw the test list panel with scrolling support."""
        x = 20 + self.category_width + 20
        y = self.header_height + 20

        # Draw panel background
        panel_rect = pygame.Rect(x - 10, y - 10, self.test_list_width, HEIGHT - y - 100)
        viewmodel.test_list_panel_rect = panel_rect  # Store for scroll event handling
        pygame.draw.rect(screen, self.PANEL_BG, panel_rect, border_radius=5)
        pygame.draw.rect(screen, self.BORDER_COLOR, panel_rect, 2, border_radius=5)

        # Header - always say "TESTS" for consistency
        header_text = self.header_font.render("TESTS", True, self.HEADER_COLOR)
        screen.blit(header_text, (x, y - 5))
        y += 40

        # Get filtered scenarios
        sorted_test_ids = sorted(filtered_scenarios.keys())

        # Draw "Run Tests" button
        mouse_pos = pygame.mouse.get_pos()
        btn_width = 120
        btn_height = 32
        run_all_btn_rect = pygame.Rect(
            x + self.test_list_width - btn_width - 30, y - 35, btn_width, btn_height
        )
        viewmodel.run_all_tests_btn_rect = run_all_btn_rect

        if executor.batch_running:
            # Show progress during batch execution
            progress_text = f"{executor.batch_current_index + 1}/{executor.batch_total}"
            btn_color = (80, 80, 50)
            btn_border = (150, 150, 80)
            text_color = (255, 255, 150)
        else:
            btn_hover = run_all_btn_rect.collidepoint(mouse_pos)
            btn_color = (60, 80, 60) if btn_hover else (40, 60, 40)
            btn_border = (80, 120, 80)
            progress_text = "Run Tests"
            text_color = (150, 200, 150)

        pygame.draw.rect(screen, btn_color, run_all_btn_rect, border_radius=4)
        pygame.draw.rect(screen, btn_border, run_all_btn_rect, 1, border_radius=4)
        btn_text = self.small_font.render(progress_text, True, text_color)
        text_rect = btn_text.get_rect(center=run_all_btn_rect.center)
        screen.blit(btn_text, text_rect)

        if not sorted_test_ids:
            no_tests_text = self.body_font.render("No tests available", True, (150, 150, 150))
            screen.blit(no_tests_text, (x + 20, y + 20))
            return

        # Calculate scrolling dimensions
        item_height = 55
        content_height = len(sorted_test_ids) * item_height
        visible_height = panel_rect.height - 50  # Space for header
        max_scroll = max(0, content_height - visible_height)

        # Update viewmodel max_scroll (for clamping)
        viewmodel.set_max_scroll(max_scroll)
        scroll_offset = viewmodel.scroll_offset

        # Set clipping region for test items
        clip_rect = pygame.Rect(panel_rect.x, y, panel_rect.width, visible_height)
        screen.set_clip(clip_rect)

        selected_test_id = controller.ui_state.get_selected_test_id()
        test_hover = controller.ui_state.get_test_hover()

        # Draw test items with scroll offset
        for i, test_id in enumerate(sorted_test_ids):
            item_y = y + i * item_height - scroll_offset

            # Skip items outside visible area for performance
            if item_y + 50 < y or item_y > y + visible_height:
                continue

            scenario_info = filtered_scenarios[test_id]
            metadata = scenario_info['metadata']

            rect = pygame.Rect(x, item_y, 400, 50)

            # Determine color
            if selected_test_id == test_id:
                color = self.SELECTED_COLOR
            elif test_hover == test_id:
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
        if max_scroll > 0:
            self._draw_test_list_scrollbar(
                screen, panel_rect, y, visible_height, scroll_offset, max_scroll
            )

    def _draw_test_list_scrollbar(
        self,
        screen,
        panel_rect: pygame.Rect,
        content_y: int,
        visible_height: int,
        scroll_offset: int,
        max_scroll: int
    ) -> None:
        """Draw scrollbar for the test list panel."""
        scrollbar_width = 8
        scrollbar_x = panel_rect.x + panel_rect.width - scrollbar_width - 5
        scrollbar_y = content_y
        scrollbar_height = visible_height

        # Draw track
        track_rect = pygame.Rect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height)
        pygame.draw.rect(screen, (40, 40, 50), track_rect, border_radius=4)

        # Calculate thumb size and position
        content_height = max_scroll + visible_height
        thumb_height = max(30, int(visible_height * visible_height / content_height))
        scroll_ratio = scroll_offset / max_scroll if max_scroll > 0 else 0
        thumb_y = scrollbar_y + int(scroll_ratio * (scrollbar_height - thumb_height))

        # Draw thumb
        thumb_rect = pygame.Rect(scrollbar_x, thumb_y, scrollbar_width, thumb_height)
        pygame.draw.rect(screen, (100, 100, 120), thumb_rect, border_radius=4)

    def _draw_metadata_panel(self, screen, controller, registry, viewmodel) -> None:
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
            run_test_color = (70, 100, 70) if run_test_hover else (50, 80, 50)
            pygame.draw.rect(screen, run_test_color, run_test_btn_rect, border_radius=4)
            pygame.draw.rect(screen, (100, 150, 100), run_test_btn_rect, 1, border_radius=4)
            run_text = self.small_font.render("Visual Run", True, (200, 255, 200))
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
            run_headless_color = (70, 70, 100) if run_headless_hover else (50, 50, 80)
            pygame.draw.rect(screen, run_headless_color, run_headless_btn_rect, border_radius=4)
            pygame.draw.rect(screen, (100, 100, 150), run_headless_btn_rect, 1, border_radius=4)
            headless_text = self.small_font.render("Headless Run", True, (200, 200, 255))
            text_rect = headless_text.get_rect(center=run_headless_btn_rect.center)
            screen.blit(headless_text, text_rect)

        y += 40

        if selected_test_id is None:
            hint_text = self.body_font.render("Select a test to view details", True, (150, 150, 150))
            screen.blit(hint_text, (x + 20, y + 20))
            return

        # Get selected test metadata
        scenario_info = registry.get_by_id(selected_test_id)
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
        y = self._draw_bullet_list(
            screen, x, y, "Conditions", metadata.conditions, (150, 200, 255), validation_results
        )
        y += 15

        # Edge Cases
        y = self._draw_bullet_list(screen, x, y, "Edge Cases", metadata.edge_cases, (255, 200, 100))
        y += 15

        # Expected Outcome
        y = self._draw_section_wrapped(
            screen, x, y, "Expected Outcome", metadata.expected_outcome, (100, 255, 150)
        )
        y += 15

        # Pass Criteria
        y = self._draw_section_wrapped(
            screen, x, y, "Pass Criteria", metadata.pass_criteria, (255, 150, 150)
        )
        y += 15

        # Validation Results (from static validation or test run)
        if 'last_run_results' in scenario_info and scenario_info['last_run_results']:
            results = scenario_info['last_run_results']
            if 'validation_results' in results:
                y += 20
                y = self._draw_validation_section(screen, x, y, results, viewmodel)

        y += 20

        # Metadata footer - just show max ticks (seed controls are now in header)
        ticks_text = f"Max Ticks: {metadata.max_ticks}    |    Test Seed: {metadata.seed}"
        ticks_surf = self.small_font.render(ticks_text, True, (120, 120, 120))
        screen.blit(ticks_surf, (x, y))

    def _draw_section(
        self, screen, x: int, y: int, label: str, text: str, color: Tuple[int, int, int]
    ) -> int:
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

    def _draw_section_wrapped(
        self, screen, x: int, y: int, label: str, text: str, color: Tuple[int, int, int]
    ) -> int:
        """Draw a metadata section with text wrapping."""
        # Label
        label_surf = self.body_font.render(f"{label}:", True, color)
        screen.blit(label_surf, (x, y))
        y += 25

        # Wrapped text
        y = self._draw_wrapped_text(screen, text, x + 10, y, self.metadata_width - 40, self.TEXT_COLOR)
        y += 5

        return y

    def _draw_bullet_list(
        self,
        screen,
        x: int,
        y: int,
        label: str,
        items: List[str],
        color: Tuple[int, int, int],
        validation_results: Optional[List[Dict]] = None
    ) -> int:
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
                bullet_surf = self.small_font.render(f"* {item}", True, self.TEXT_COLOR)
                screen.blit(bullet_surf, (x + 10, y))

                # Check if this item is verified by validation results
                if validation_results and self._is_condition_verified(item, validation_results):
                    # Draw green "V" on right edge
                    v_surf = self.body_font.render("V", True, TEST_PASS)
                    v_x = x + self.metadata_width - 40  # Right edge with padding
                    screen.blit(v_surf, (v_x, y - 2))

                y += 22

        return y

    def _is_condition_verified(self, condition_text: str, validation_results: List[Dict]) -> bool:
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
            # Beam weapon mappings
            'Beam Damage': 'Beam Weapon Damage',
            'Base Accuracy': 'Base Accuracy',
            'Accuracy Falloff': 'Accuracy Falloff',
            'Weapon Max Range': 'Weapon Range',
            'Distance': None,  # Distance is test setup, not component property
            'Net Score': None,  # Calculated value, complex validation
            'Test Duration': None,  # Test parameter, not validated
            'Test duration': None,  # Test parameter, not validated

            # Propulsion test mappings
            'Engine thrust': 'Engine Thrust',
            'Ship mass': 'Ship Mass',
            'Expected max_speed': 'Max Speed (Formula)',
            'Expected acceleration_rate': 'Acceleration Rate (Formula)',
            'Initial velocity': 'Initial Velocity',
            'Initial angle': 'Initial Angle',
            'Total thrust': 'Total Thrust',
            'turn_speed': 'Turn Speed',
            'Turn speed': 'Turn Speed (Formula)',
            'raw_turn_rate': 'Raw Turn Rate',
            'Expected turn_speed': 'Turn Speed (Formula)',
            'No engine component': 'Total Thrust (Should be 0)',
            'No thruster component': None,  # Not directly validated
            'thrust = 0': 'Total Thrust (Should be 0)',
            'Expected: No movement': 'Distance Traveled',
            'Expected: Rotation but no translation': 'Final Velocity',
        }

        # Check direct validations
        for pattern, validation_name in mappings.items():
            if validation_name and pattern in condition_text:
                # Find matching validation result
                for vr in validation_results:
                    if vr['name'] == validation_name and vr['status'] == 'PASS':
                        return True

        # Special case: Range Penalty (calculated from distance x accuracy_falloff)
        if 'Range Penalty' in condition_text:
            # Extract values from condition text like "Range Penalty: 50 * 0.002 = 0.1"
            try:
                # Match pattern: "Range Penalty: {distance} * {falloff} = {result}"
                match = re.search(
                    r'Range Penalty:\s*(\d+\.?\d*)\s*\*\s*(\d+\.?\d*)\s*=\s*(\d+\.?\d*)',
                    condition_text
                )
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
                        if abs(calculated_penalty - penalty_stated) < 0.0001:  # Float comparison
                            return True
            except (ValueError, TypeError):
                pass  # If parsing fails, don't show V

        return False

    def _draw_wrapped_text(
        self,
        screen,
        text: str,
        x: int,
        y: int,
        max_width: int,
        color: Tuple[int, int, int]
    ) -> int:
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

    def _draw_validation_section(
        self, screen, x: int, y: int, results: Dict[str, Any], viewmodel
    ) -> int:
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
            summary_color = TEST_FAIL
            status_symbol = "X"
        elif warn_count > 0:
            summary_color = (255, 200, 80)  # Yellow/Orange (unique)
            status_symbol = "!"
        else:
            summary_color = TEST_PASS
            status_symbol = "V"

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
                status_color = TEST_PASS
                symbol = "V"
            elif status == 'FAIL':
                status_color = TEST_FAIL
                symbol = "X"
            elif status == 'WARN':
                status_color = (255, 200, 80)
                symbol = "!"
            else:
                status_color = (120, 120, 200)
                symbol = "i"

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
            viewmodel.update_expected_button_rect = pygame.Rect(
                button_x, button_y, button_width, button_height
            )
            viewmodel.update_expected_button_visible = True

            # Draw button
            button_color = (60, 120, 200)  # Blue
            button_hover_color = (80, 140, 220)

            # Check if mouse is over button
            mouse_pos = pygame.mouse.get_pos()
            is_hover = viewmodel.update_expected_button_rect.collidepoint(mouse_pos)
            current_color = button_hover_color if is_hover else button_color

            # Draw button background
            pygame.draw.rect(screen, current_color, viewmodel.update_expected_button_rect)
            pygame.draw.rect(
                screen, (100, 140, 200), viewmodel.update_expected_button_rect, 2
            )

            # Draw button text
            button_text = "Update Expected Values"
            button_surf = self.small_font.render(button_text, True, (255, 255, 255))
            text_x = button_x + (button_width - button_surf.get_width()) // 2
            text_y = button_y + (button_height - button_surf.get_height()) // 2
            screen.blit(button_surf, (text_x, text_y))

            y += button_height + 10
        else:
            viewmodel.update_expected_button_visible = False

        return y

    def _draw_validation_flag(
        self, screen, x: int, y: int, scenario_info: Dict[str, Any]
    ) -> None:
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
                color = TEST_FAIL
                symbol = "X"
            elif warn_count > 0:
                # Warnings - yellow circle with !
                color = (255, 200, 80)  # Yellow/Orange (unique)
                symbol = "!"
            else:
                # All passed - green circle with checkmark
                color = TEST_PASS
                symbol = "V"

        # Draw circle
        pygame.draw.circle(screen, color, (x, y), radius)
        pygame.draw.circle(screen, (0, 0, 0), (x, y), radius, 2)  # Black outline

        # Draw symbol if present
        if symbol:
            symbol_surf = self.small_font.render(symbol, True, (0, 0, 0))
            symbol_rect = symbol_surf.get_rect(center=(x, y))
            screen.blit(symbol_surf, symbol_rect)

    def _draw_output_log(self, screen, output_log: List[str]) -> None:
        """Draw the output log at the bottom."""
        y = HEIGHT - 90
        for i, msg in enumerate(output_log[-3:]):
            color = (255, 100, 100) if "ERROR" in msg else (150, 150, 150)
            txt = self.small_font.render(msg, True, color)
            screen.blit(txt, (20, y + i * 20))
