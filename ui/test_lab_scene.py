import pygame
import os
import sys
import json

from game.core.constants import WHITE, BLACK, BLUE, WIDTH, HEIGHT, FONT_MAIN
from ui.components import Button
from test_framework.runner import TestRunner
from test_framework.registry import TestRegistry


class JSONPopup:
    """Popup window for displaying JSON data."""

    def __init__(self, title, json_data, screen_width, screen_height):
        """
        Create JSON popup.

        Args:
            title: Title for the popup
            json_data: Dictionary or string to display as JSON
            screen_width: Screen width
            screen_height: Screen height
        """
        self.title = title
        self.json_text = json.dumps(json_data, indent=2) if isinstance(json_data, dict) else str(json_data)
        self.screen_width = screen_width
        self.screen_height = screen_height

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

        # Close button
        self.close_button = Button(self.x + self.width - 120, self.y + 10, 100, 40, "Close", self.close)
        self.is_open = True

    def close(self):
        """Close the popup."""
        self.is_open = False

    def handle_event(self, event):
        """Handle user input."""
        # Handle close button
        self.close_button.handle_event(event)

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

        # Close button
        self.close_button.draw(screen)

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


class ScrollableJSONViewer:
    """Scrollable panel for displaying formatted JSON with syntax highlighting."""

    def __init__(self, x, y, width, height, title, json_data):
        """
        Initialize JSON viewer.

        Args:
            x, y: Top-left position
            width, height: Panel dimensions
            title: Panel title (e.g., "Ship: Attacker")
            json_data: Dictionary to display as JSON
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.title = title

        # Format JSON with 2-space indentation
        self.json_text = json.dumps(json_data, indent=2) if json_data else "{}"
        self.lines = self.json_text.split('\n')

        # Scrolling state
        self.scroll_offset = 0
        self.line_height = 18
        self.title_height = 30
        self.content_height = height - self.title_height
        self.visible_lines = max(1, self.content_height // self.line_height)
        self.max_scroll = max(0, len(self.lines) - self.visible_lines)

        # Fonts
        self.body_font = pygame.font.SysFont('Courier New', 14)
        self.title_font = pygame.font.SysFont(FONT_MAIN, 18)

        # Colors
        self.bg_color = (30, 30, 35)
        self.title_bg_color = (45, 45, 50)
        self.text_color = (220, 220, 220)
        self.title_color = (255, 255, 255)
        self.border_color = (100, 100, 120)

    def update_json(self, json_data):
        """Update displayed JSON data."""
        self.json_text = json.dumps(json_data, indent=2) if json_data else "{}"
        self.lines = self.json_text.split('\n')
        self.max_scroll = max(0, len(self.lines) - self.visible_lines)
        self.scroll_offset = min(self.scroll_offset, self.max_scroll)

    def handle_scroll(self, event):
        """Handle mouse wheel scrolling."""
        if event.type == pygame.MOUSEWHEEL:
            # Check if mouse is over this panel
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if (self.x <= mouse_x <= self.x + self.width and
                self.y <= mouse_y <= self.y + self.height):

                # Scroll up/down
                self.scroll_offset -= event.y * 3  # 3 lines per wheel tick
                self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))
                return True
        return False

    def draw(self, surface):
        """Draw the JSON viewer panel."""
        # Draw border
        pygame.draw.rect(surface, self.border_color,
                        (self.x, self.y, self.width, self.height), 2)

        # Draw title bar
        title_rect = (self.x + 2, self.y + 2, self.width - 4, self.title_height - 4)
        pygame.draw.rect(surface, self.title_bg_color, title_rect)

        title_surface = self.title_font.render(self.title, True, self.title_color)
        title_x = self.x + 10
        title_y = self.y + (self.title_height - title_surface.get_height()) // 2
        surface.blit(title_surface, (title_x, title_y))

        # Draw content background
        content_rect = (self.x + 2, self.y + self.title_height,
                       self.width - 4, self.content_height)
        pygame.draw.rect(surface, self.bg_color, content_rect)

        # Draw JSON lines (visible range only)
        start_line = self.scroll_offset
        end_line = min(start_line + self.visible_lines, len(self.lines))

        for i in range(start_line, end_line):
            line = self.lines[i]
            text_surface = self.body_font.render(line, True, self.text_color)

            text_x = self.x + 10
            text_y = self.y + self.title_height + ((i - start_line) * self.line_height) + 5

            surface.blit(text_surface, (text_x, text_y))

        # Draw scrollbar if needed
        if self.max_scroll > 0:
            scrollbar_x = self.x + self.width - 15
            scrollbar_y = self.y + self.title_height + 5
            scrollbar_height = self.content_height - 10

            # Scrollbar track
            pygame.draw.rect(surface, (60, 60, 70),
                           (scrollbar_x, scrollbar_y, 10, scrollbar_height))

            # Scrollbar thumb
            thumb_height = max(20, int(scrollbar_height * self.visible_lines / len(self.lines)))
            thumb_y = scrollbar_y + int((scrollbar_height - thumb_height) * (self.scroll_offset / self.max_scroll))
            pygame.draw.rect(surface, (120, 120, 140),
                           (scrollbar_x, thumb_y, 10, thumb_height))


class ComponentDropdown:
    """Dropdown menu for selecting components from a ship's component list."""

    def __init__(self, x, y, width, height, component_ids, load_callback):
        """
        Initialize component dropdown.

        Args:
            x, y: Top-left position
            width, height: Dropdown dimensions (height is for closed state)
            component_ids: List of component IDs to choose from
            load_callback: Function(component_id) -> Dict, called when selection changes
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.component_ids = component_ids if component_ids else ["No components"]
        self.selected_index = 0
        self.is_expanded = False
        self.load_callback = load_callback

        # Fonts & Colors
        self.font = pygame.font.SysFont(FONT_MAIN, 16)
        self.bg_color = (50, 50, 60)
        self.selected_bg_color = (70, 70, 85)
        self.hover_bg_color = (60, 60, 75)
        self.text_color = (255, 255, 255)
        self.border_color = (100, 100, 120)

        self.hovered_index = -1

    def handle_click(self, event):
        """Handle mouse clicks on dropdown."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos

            # Click on closed dropdown header
            if not self.is_expanded:
                if (self.x <= mouse_x <= self.x + self.width and
                    self.y <= mouse_y <= self.y + self.height):
                    self.is_expanded = True
                    return True

            # Click on expanded dropdown
            else:
                # Click on header closes it
                if (self.x <= mouse_x <= self.x + self.width and
                    self.y <= mouse_y <= self.y + self.height):
                    self.is_expanded = False
                    return True

                # Click on option
                dropdown_height = self.height * len(self.component_ids)
                if (self.x <= mouse_x <= self.x + self.width and
                    self.y + self.height <= mouse_y <= self.y + self.height + dropdown_height):

                    option_index = (mouse_y - self.y - self.height) // self.height
                    if 0 <= option_index < len(self.component_ids):
                        self.selected_index = option_index
                        self.is_expanded = False
                        return True

                # Click outside closes dropdown
                else:
                    self.is_expanded = False
                    return True

        return False

    def handle_hover(self):
        """Track hovered option for visual feedback."""
        if not self.is_expanded:
            self.hovered_index = -1
            return

        mouse_x, mouse_y = pygame.mouse.get_pos()
        dropdown_height = self.height * len(self.component_ids)

        if (self.x <= mouse_x <= self.x + self.width and
            self.y + self.height <= mouse_y <= self.y + self.height + dropdown_height):
            self.hovered_index = (mouse_y - self.y - self.height) // self.height
        else:
            self.hovered_index = -1

    def get_selected_component_id(self):
        """Get currently selected component ID."""
        if 0 <= self.selected_index < len(self.component_ids):
            comp_id = self.component_ids[self.selected_index]
            return comp_id if comp_id != "No components" else None
        return None

    def draw(self, surface):
        """Draw the dropdown menu."""
        # Draw closed header
        header_rect = (self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, self.bg_color, header_rect)
        pygame.draw.rect(surface, self.border_color, header_rect, 2)

        # Display selected component ID
        selected_text = self.component_ids[self.selected_index] if self.component_ids else "No components"
        text_surface = self.font.render(selected_text, True, self.text_color)
        text_x = self.x + 10
        text_y = self.y + (self.height - text_surface.get_height()) // 2
        surface.blit(text_surface, (text_x, text_y))

        # Draw dropdown arrow
        arrow_x = self.x + self.width - 25
        arrow_y = self.y + self.height // 2
        arrow_points = [
            (arrow_x, arrow_y - 5),
            (arrow_x + 10, arrow_y - 5),
            (arrow_x + 5, arrow_y + 5)
        ] if not self.is_expanded else [
            (arrow_x, arrow_y + 5),
            (arrow_x + 10, arrow_y + 5),
            (arrow_x + 5, arrow_y - 5)
        ]
        pygame.draw.polygon(surface, self.text_color, arrow_points)

        # Draw expanded options
        if self.is_expanded:
            for i, comp_id in enumerate(self.component_ids):
                option_y = self.y + self.height + (i * self.height)
                option_rect = (self.x, option_y, self.width, self.height)

                # Background color
                if i == self.hovered_index:
                    bg_color = self.hover_bg_color
                elif i == self.selected_index:
                    bg_color = self.selected_bg_color
                else:
                    bg_color = self.bg_color

                pygame.draw.rect(surface, bg_color, option_rect)
                pygame.draw.rect(surface, self.border_color, option_rect, 1)

                # Option text
                option_surface = self.font.render(comp_id, True, self.text_color)
                option_x = self.x + 10
                option_text_y = option_y + (self.height - option_surface.get_height()) // 2
                surface.blit(option_surface, (option_x, option_text_y))


class ShipPanel:
    """Combined panel showing ship JSON + component dropdown + component JSON."""

    def __init__(self, x, y, width, height, ship_info, load_component_callback):
        """
        Initialize ship panel.

        Args:
            x, y: Top-left position
            width, height: Panel dimensions
            ship_info: Dict with 'role', 'ship_data', 'component_ids'
            load_component_callback: Function(component_id) -> Dict
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.ship_info = ship_info
        self.load_component_callback = load_component_callback

        # Layout: 55% ship, dropdown, 40% component
        ship_height = int(height * 0.55)
        dropdown_height = 40
        component_height = height - ship_height - dropdown_height - 20  # 20px spacing

        # Ship JSON viewer (top 55%)
        self.ship_viewer = ScrollableJSONViewer(
            x=x,
            y=y,
            width=width,
            height=ship_height,
            title=f"Ship: {ship_info['role']}",
            json_data=ship_info['ship_data']
        )

        # Component dropdown (middle)
        dropdown_y = y + ship_height + 10
        self.component_dropdown = ComponentDropdown(
            x=x + 10,
            y=dropdown_y,
            width=width - 20,
            height=dropdown_height,
            component_ids=ship_info['component_ids'],
            load_callback=load_component_callback
        )

        # Component JSON viewer (bottom 40%)
        component_y = dropdown_y + dropdown_height + 10
        selected_comp_id = self.component_dropdown.get_selected_component_id()
        component_data = load_component_callback(selected_comp_id) if selected_comp_id else {}

        self.component_viewer = ScrollableJSONViewer(
            x=x,
            y=component_y,
            width=width,
            height=component_height,
            title="Component JSON",
            json_data=component_data
        )

    def handle_event(self, event):
        """Handle input events (scrolling, dropdown clicks)."""
        # Try dropdown first
        if self.component_dropdown.handle_click(event):
            # Selection changed - update component viewer
            selected_comp_id = self.component_dropdown.get_selected_component_id()
            if selected_comp_id:
                component_data = self.load_component_callback(selected_comp_id)
                if component_data:
                    self.component_viewer.update_json(component_data)
            return True

        # Try scrolling on ship viewer
        if self.ship_viewer.handle_scroll(event):
            return True

        # Try scrolling on component viewer
        if self.component_viewer.handle_scroll(event):
            return True

        return False

    def update(self):
        """Update hover states."""
        self.component_dropdown.handle_hover()

    def draw(self, surface):
        """Draw the complete ship panel."""
        self.ship_viewer.draw(surface)
        self.component_dropdown.draw(surface)
        self.component_viewer.draw(surface)


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
        self.json_popup = None  # For displaying JSON data
        self.ship_panels = []  # Ship JSON panels
        self._components_cache = None  # Cache for components.json
        self._create_ui()

    def _extract_ships_from_scenario(self, test_id):
        """
        Extract ship information from test scenario metadata.

        Args:
            test_id: Test ID (e.g., "BEAM360-001")

        Returns:
            List[Dict]: [
                {
                    'role': 'Attacker',  # or 'Target', 'Ship1', etc.
                    'filename': 'Test_Attacker_Beam360_Low.json',
                    'ship_data': {...},  # Full ship JSON
                    'component_ids': ['test_beam_low_acc_1dmg', ...]  # All component IDs
                }
            ]
        """
        scenario_info = self.registry.get_by_id(test_id)

        if not scenario_info:
            return []

        metadata = scenario_info['metadata']
        ships = []

        # Parse conditions for ship filenames
        # Format: "Attacker: Test_Attacker_Beam360_Low.json"
        for condition in metadata.conditions:
            if '.json' in condition and ':' in condition:
                parts = condition.split(':', 1)
                role = parts[0].strip()
                filename = parts[1].strip()

                # Load ship JSON file
                ship_path = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    'simulation_tests',
                    'data',
                    'ships',
                    filename
                )

                try:
                    with open(ship_path, 'r') as f:
                        ship_data = json.load(f)

                    # Extract component IDs from layers
                    component_ids = []
                    for layer_name in ['CORE', 'ARMOR', 'HULL']:
                        layer = ship_data.get('layers', {}).get(layer_name, [])
                        for component in layer:
                            comp_id = component.get('id')
                            if comp_id:
                                component_ids.append(comp_id)

                    ships.append({
                        'role': role,
                        'filename': filename,
                        'ship_data': ship_data,
                        'component_ids': component_ids
                    })

                except Exception as e:
                    print(f"Error loading ship {filename}: {e}")

        return ships

    def _load_component_data(self, component_id):
        """
        Load component JSON from components.json by ID.

        Args:
            component_id: Component ID (e.g., "test_beam_low_acc_1dmg")

        Returns:
            Dict: Component JSON data, or None if not found
        """
        # Load and cache components.json on first call
        if self._components_cache is None:
            components_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'simulation_tests',
                'data',
                'components.json'
            )

            try:
                with open(components_path, 'r') as f:
                    components_data = json.load(f)
                    # Extract the components list from the wrapper object
                    components_list = components_data.get('components', [])
                    # Convert list to dict for faster lookup
                    self._components_cache = {
                        comp['id']: comp
                        for comp in components_list
                    }
            except Exception as e:
                print(f"Error loading components.json: {e}")
                self._components_cache = {}

        return self._components_cache.get(component_id)

    def _create_ship_panels(self, test_id):
        """
        Create ship panels for the selected test.

        Args:
            test_id: Test ID (e.g., "BEAM360-001")
        """
        self.ship_panels = []

        # Extract ships from scenario
        ships = self._extract_ships_from_scenario(test_id)

        if not ships:
            return

        # Create panel for each ship
        base_x = 20 + self.category_width + 20 + self.test_list_width + 20 + self.metadata_width + 20
        panel_width = 540
        panel_height = HEIGHT - self.header_height - 40

        for i, ship_info in enumerate(ships):
            panel_x = base_x + (i * (panel_width + 20))
            panel_y = self.header_height + 20

            panel = ShipPanel(
                x=panel_x,
                y=panel_y,
                width=panel_width,
                height=panel_height,
                ship_info=ship_info,
                load_component_callback=self._load_component_data
            )

            self.ship_panels.append(panel)

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
        # Store results from completed test before clearing
        if self.selected_test_id and hasattr(self.game.battle_scene, 'test_scenario'):
            scenario = self.game.battle_scene.test_scenario
            if hasattr(scenario, 'results') and scenario.results:
                print(f"DEBUG: Storing results for {self.selected_test_id}")
                self.registry.update_last_run_results(self.selected_test_id, scenario.results)

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
            # Handle JSON popup first (if open)
            if self.json_popup and self.json_popup.is_open:
                self.json_popup.handle_event(event)
                if not self.json_popup.is_open:
                    self.json_popup = None
                continue  # Don't process other events while popup is open

            # Handle ship panel events (scrolling, dropdown clicks)
            for panel in self.ship_panels:
                if panel.handle_event(event):
                    continue  # Event consumed by panel

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
                # Create ship panels for the selected test
                self._create_ship_panels(test_id)
                return

    def update(self):
        """Update UI state."""
        # Update ship panels (hover states)
        for panel in self.ship_panels:
            panel.update()

    def draw(self, screen):
        """Draw the Combat Lab UI with category sidebar, test list, and metadata panel."""
        screen.fill(self.BG_COLOR)

        # Header
        self._draw_header(screen)

        # Three-column layout
        self._draw_category_sidebar(screen)
        self._draw_test_list(screen)
        self._draw_metadata_panel(screen)

        # Ship panels (drawn after metadata panel)
        for panel in self.ship_panels:
            panel.draw(screen)

        # Output log
        self._draw_output_log(screen)

        # Buttons
        for btn in self.buttons:
            btn.draw(screen)

        # JSON popup (drawn last, on top of everything)
        if self.json_popup and self.json_popup.is_open:
            self.json_popup.draw(screen)

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

            # Validation status flag (if available)
            flag_x = rect.x + rect.width - 30
            flag_y = rect.y + 10
            self._draw_validation_flag(screen, flag_x, flag_y, scenario_info)

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

        # Validation Results (if available from last run)
        if hasattr(scenario_info, 'last_run_results') and scenario_info['last_run_results']:
            results = scenario_info['last_run_results']
            if 'validation_results' in results:
                y += 20
                y = self._draw_validation_section(screen, x, y, results)

        y += 20

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

    def _draw_validation_section(self, screen, x, y, results):
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
            summary_color = (255, 80, 80)  # Red
            status_symbol = "✗"
        elif warn_count > 0:
            summary_color = (255, 200, 80)  # Yellow/Orange
            status_symbol = "⚠"
        else:
            summary_color = (80, 255, 120)  # Green
            status_symbol = "✓"

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
                status_color = (80, 255, 120)
                symbol = "✓"
            elif status == 'FAIL':
                status_color = (255, 80, 80)
                symbol = "✗"
            elif status == 'WARN':
                status_color = (255, 200, 80)
                symbol = "⚠"
            else:
                status_color = (120, 120, 200)
                symbol = "ℹ"

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

            # P-value (for statistical tests)
            if p_value is not None:
                p_text = f"p-value: {p_value:.4f}"
                if p_value < 0.05:
                    p_color = (255, 100, 100)  # Red - significant difference
                else:
                    p_color = (100, 255, 150)  # Green - consistent

                p_surf = self.small_font.render(p_text, True, p_color)
                screen.blit(p_surf, (x + 25, y))
                y += 18

            y += 5  # Space between validation items

        return y

    def _draw_validation_flag(self, screen, x, y, scenario_info):
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
                color = (255, 80, 80)
                symbol = "✗"
            elif warn_count > 0:
                # Warnings - yellow circle with !
                color = (255, 200, 80)
                symbol = "⚠"
            else:
                # All passed - green circle with checkmark
                color = (80, 255, 120)
                symbol = "✓"

        # Draw circle
        pygame.draw.circle(screen, color, (x, y), radius)
        pygame.draw.circle(screen, (0, 0, 0), (x, y), radius, 2)  # Black outline

        # Draw symbol if present
        if symbol:
            symbol_surf = self.small_font.render(symbol, True, (0, 0, 0))
            symbol_rect = symbol_surf.get_rect(center=(x, y))
            screen.blit(symbol_surf, symbol_rect)

    def _show_ships_json(self, test_id):
        """Show JSON for all ships used in the test."""
        if test_id is None:
            return

        scenario_info = self.registry.get_by_id(test_id)
        if not scenario_info:
            return

        # Load ship JSON files from test data
        ships_data = {}

        # Get ship filenames from test scenario
        # This is a simplified approach - we'll try to find ship files mentioned in conditions
        metadata = scenario_info['metadata']

        # Extract ship filenames from conditions
        ship_files = []
        for condition in metadata.conditions:
            if '.json' in condition and ('Attacker:' in condition or 'Target:' in condition):
                parts = condition.split(':')
                if len(parts) > 1:
                    filename = parts[1].strip()
                    ship_files.append(filename)

        # Load ship JSON files
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'simulation_tests', 'data', 'ships')

        for ship_file in ship_files:
            ship_path = os.path.join(data_dir, ship_file)
            if os.path.exists(ship_path):
                try:
                    with open(ship_path, 'r') as f:
                        ship_data = json.load(f)
                        ships_data[ship_file] = ship_data
                except Exception as e:
                    ships_data[ship_file] = f"Error loading: {e}"

        if not ships_data:
            ships_data = {"error": "No ship files found for this test"}

        self.json_popup = JSONPopup(f"Ships JSON - {test_id}", ships_data, WIDTH, HEIGHT)

    def _show_components_json(self):
        """Show JSON for all components in the test data."""
        # Load components.json from test data
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'simulation_tests', 'data')
        components_path = os.path.join(data_dir, 'components.json')

        if os.path.exists(components_path):
            try:
                with open(components_path, 'r') as f:
                    components_data = json.load(f)
                self.json_popup = JSONPopup("Components JSON", components_data, WIDTH, HEIGHT)
            except Exception as e:
                self.json_popup = JSONPopup("Components JSON", {"error": f"Failed to load: {e}"}, WIDTH, HEIGHT)
        else:
            self.json_popup = JSONPopup("Components JSON", {"error": "components.json not found"}, WIDTH, HEIGHT)

    def _draw_output_log(self, screen):
        """Draw the output log at the bottom."""
        y = HEIGHT - 90
        for i, msg in enumerate(self.output_log[-3:]):
            color = (255, 100, 100) if "ERROR" in msg else (150, 150, 150)
            txt = self.small_font.render(msg, True, color)
            screen.blit(txt, (20, y + i * 20))
