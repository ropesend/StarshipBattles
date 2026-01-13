import pygame
import os
import sys

from game.core.constants import WHITE, BLACK, BLUE, WIDTH, HEIGHT, FONT_MAIN
from ui.components import Button
from test_framework.runner import TestRunner
from test_framework.registry import TestRegistry

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

        # Get all scenarios from registry
        self.registry = TestRegistry()
        self.all_scenarios = self.registry.get_all_scenarios()
        self.categories = self.registry.get_categories()

        # UI State
        self.selected_category = None  # None = show all
        self.selected_test_id = None
        self.category_hover = None
        self.test_hover = None

        # Layout dimensions
        self.category_width = 220
        self.test_list_width = 420
        self.metadata_width = 540
        self.header_height = 80

        # Scrolling state (for future enhancement)
        self.test_scroll_offset = 0
        self.metadata_scroll_offset = 0

        # Output log
        self.output_log = ["Select a test to view details..."]

        self.buttons = []
        self._create_ui()

    def _create_ui(self):
        """Create UI buttons."""
        self.buttons = []

        # Back Button
        self.btn_back = Button(20, 20, 100, 40, "Back", self._on_back)
        self.buttons.append(self.btn_back)

        # Run Button
        self.btn_run = Button(WIDTH - 150, HEIGHT - 80, 120, 50, "RUN TEST", self._on_run)
        self.buttons.append(self.btn_run)

    def _get_filtered_scenarios(self):
        """Get scenarios filtered by selected category."""
        if self.selected_category is None:
            return self.all_scenarios
        else:
            return self.registry.get_by_category(self.selected_category)
        
    def reset_selection(self):
        """Clear test selection (called when returning from battle)."""
        self.selected_test_id = None
        print(f"DEBUG: Test selection cleared")

    def _on_back(self):
        """Return to main menu."""
        from game.core.constants import GameState
        self.game.state = GameState.MENU
        if hasattr(self.game, 'menu_screen') and hasattr(self.game.menu_screen, 'create_particles'):
            self.game.menu_screen.create_particles()

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
            print(f"DEBUG: Instantiating scenario class")
            scenario_cls = scenario_info['class']
            scenario = scenario_cls()
            print(f"DEBUG: Scenario instantiated: {scenario.name}")

            # Load test data
            print(f"DEBUG: Loading test data for scenario")
            runner.load_data_for_scenario(scenario)
            print(f"DEBUG: Test data loaded successfully")

            # Clear battle engine
            print(f"DEBUG: Clearing battle engine")
            self.game.battle_scene.engine.start([], [])

            # Setup scenario
            print(f"DEBUG: Calling scenario.setup()")
            scenario.setup(self.game.battle_scene.engine)
            print(f"DEBUG: Scenario setup complete")

            # Configure battle scene for test mode
            print(f"DEBUG: Configuring battle scene for test mode")
            print(f"DEBUG: BEFORE: test_mode={self.game.battle_scene.test_mode}")
            self.game.battle_scene.headless_mode = False
            self.game.battle_scene.sim_paused = True  # Start paused
            self.game.battle_scene.test_mode = True   # Enable test mode
            self.game.battle_scene.test_scenario = scenario  # Pass scenario for update() calls
            self.game.battle_scene.test_tick_count = 0  # Reset tick counter
            self.game.battle_scene.action_return_to_test_lab = False
            print(f"DEBUG: AFTER: test_mode={self.game.battle_scene.test_mode}")
            print(f"DEBUG: Battle scene configured (paused=True, test_mode=True, scenario={scenario.metadata.test_id})")

            # Fit camera to ships
            if self.game.battle_scene.engine.ships:
                self.game.battle_scene.camera.fit_objects(self.game.battle_scene.engine.ships)
                print(f"DEBUG: Camera fitted to ships")

            # Switch to battle state
            from game.core.constants import GameState
            print(f"DEBUG: Switching to BATTLE state")
            self.game.state = GameState.BATTLE

            self.output_log.append(f"Started test {self.selected_test_id}")

        except Exception as e:
            self.output_log.append(f"ERROR: {e}")
            import traceback
            traceback.print_exc()

    def handle_input(self, events):
        """Handle user input for category selection, test selection, and buttons."""
        for event in events:
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

        # Check test hover
        test_list_x = 20 + self.category_width + 20
        test_list_y = self.header_height + 20

        filtered_scenarios = self._get_filtered_scenarios()
        sorted_test_ids = sorted(filtered_scenarios.keys())

        for i, test_id in enumerate(sorted_test_ids):
            rect = pygame.Rect(test_list_x, test_list_y + i * 55, 400, 50)
            if rect.collidepoint(mx, my):
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

        # Check test click
        test_list_x = 20 + self.category_width + 20
        test_list_y = self.header_height + 20

        filtered_scenarios = self._get_filtered_scenarios()
        sorted_test_ids = sorted(filtered_scenarios.keys())

        for i, test_id in enumerate(sorted_test_ids):
            rect = pygame.Rect(test_list_x, test_list_y + i * 55, 400, 50)
            if rect.collidepoint(mx, my):
                self.selected_test_id = test_id
                return

    def draw(self, screen):
        """Draw the Combat Lab UI with category sidebar, test list, and metadata panel."""
        screen.fill(self.BG_COLOR)

        # Header
        self._draw_header(screen)

        # Three-column layout
        self._draw_category_sidebar(screen)
        self._draw_test_list(screen)
        self._draw_metadata_panel(screen)

        # Output log
        self._draw_output_log(screen)

        # Buttons
        for btn in self.buttons:
            btn.draw(screen)

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
        """Draw the test list panel."""
        x = 20 + self.category_width + 20
        y = self.header_height + 20

        # Draw panel background
        panel_rect = pygame.Rect(x - 10, y - 10, self.test_list_width, HEIGHT - y - 100)
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

        if not sorted_test_ids:
            no_tests_text = self.body_font.render("No tests available", True, (150, 150, 150))
            screen.blit(no_tests_text, (x + 20, y + 20))
            return

        # Draw test items
        for i, test_id in enumerate(sorted_test_ids):
            scenario_info = filtered_scenarios[test_id]
            metadata = scenario_info['metadata']

            rect = pygame.Rect(x, y + i * 55, 400, 50)

            # Determine color
            if self.selected_test_id == test_id:
                color = self.SELECTED_COLOR
            elif self.test_hover == test_id:
                color = (40, 40, 50)
            else:
                color = (30, 30, 35)

            pygame.draw.rect(screen, color, rect, border_radius=3)
            pygame.draw.rect(screen, self.BORDER_COLOR, rect, 1, border_radius=3)

            # Test ID
            id_text = self.body_font.render(test_id, True, self.HEADER_COLOR)
            screen.blit(id_text, (rect.x + 10, rect.y + 5))

            # Test name
            name_text = self.small_font.render(metadata.name, True, self.TEXT_COLOR)
            screen.blit(name_text, (rect.x + 10, rect.y + 28))

    def _draw_metadata_panel(self, screen):
        """Draw the metadata panel showing rich test information."""
        x = 20 + self.category_width + 20 + self.test_list_width + 20
        y = self.header_height + 20

        # Draw panel background
        panel_rect = pygame.Rect(x - 10, y - 10, self.metadata_width, HEIGHT - y - 100)
        pygame.draw.rect(screen, self.PANEL_BG, panel_rect, border_radius=5)
        pygame.draw.rect(screen, self.BORDER_COLOR, panel_rect, 2, border_radius=5)

        # Header
        header_text = self.header_font.render("TEST DETAILS", True, self.HEADER_COLOR)
        screen.blit(header_text, (x, y - 5))
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

        # Conditions
        y = self._draw_bullet_list(screen, x, y, "Conditions", metadata.conditions, (150, 200, 255))
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

    def _draw_bullet_list(self, screen, x, y, label, items, color):
        """Draw a bullet list section."""
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
                y += 22

        return y

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

    def _draw_output_log(self, screen):
        """Draw the output log at the bottom."""
        y = HEIGHT - 90
        for i, msg in enumerate(self.output_log[-3:]):
            color = (255, 100, 100) if "ERROR" in msg else (150, 150, 150)
            txt = self.small_font.render(msg, True, color)
            screen.blit(txt, (20, y + i * 20))
