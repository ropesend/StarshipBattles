"""
Build Queue Screen - Full-screen interface for managing planetary construction.
"""

import pygame
import pygame_gui
import pygame_gui.elements as ui
import pygame_gui.windows
from typing import Optional, Callable
from game.strategy.data.planet import Planet
from game.strategy.systems.design_library import DesignLibrary
from game.simulation.services.design_loader import SimulationDesignLoader
from game.core.logger import log_info, log_warning, log_error, log_debug
from game.core.screenshot_manager import ScreenshotManager
from game.ui.panels.planet_report_panel import PlanetReportPanel
from game.ui.panels.design_report_panel import DesignReportPanel


class BuildQueueScreen:
    """Full-screen modal interface for managing build queues on planets."""

    def __init__(self, manager: pygame_gui.UIManager, planet: Planet, session, on_close_callback: Callable, portrait_surface: Optional[pygame.Surface] = None):
        """
        Initialize the build queue screen.

        Args:
            manager: pygame_gui UIManager
            planet: Planet object to manage build queue for
            session: Game session with current_empire and savegame_path
            on_close_callback: Function to call when screen closes
            portrait_surface: Optional pygame Surface for planet portrait
        """
        self.manager = manager
        self.planet = planet
        self.session = session
        self.on_close = on_close_callback
        self.portrait_surface = portrait_surface
        self.selected_design = None
        self.selected_category = "complex"
        self.queue_items = []  # List of UI elements for queue display
        self.dragged_item = None  # Storage for item being dragged
        self.drag_preview = None  # Preview element following cursor
        self.selected_queue_index = None  # Currently selected item in queue
        self.drag_start_pos = None  # Track mouse position for drag threshold
        self.drag_threshold = 10  # Pixels to move before starting drag

        # Load design library
        from game.core.logger import log_debug, log_info

        # Validate required attributes
        if not hasattr(planet, 'owner_id'):
            raise ValueError(f"BuildQueueScreen: planet '{getattr(planet, 'name', 'unknown')}' missing required 'owner_id' attribute")
        if not hasattr(planet, 'name'):
            log_warning("BuildQueueScreen: planet missing 'name' attribute")

        savegame_path = getattr(session, 'save_path', None)  # FIXED: was 'savegame_path', should be 'save_path'

        # FIXED: Use planet's owner_id to determine which empire's designs to load
        # session.current_empire doesn't exist - planet.owner_id tells us who owns this planet
        empire_id = planet.owner_id

        log_info(f"BuildQueue: Initializing DesignLibrary for planet '{planet.name}' (owner_id={empire_id})")
        log_debug(f"BuildQueue: save_path='{savegame_path}', empire_id={empire_id}")

        self.design_library = DesignLibrary(savegame_path, empire_id)

        log_info(f"BuildQueue: DesignLibrary created with designs_folder: {self.design_library.designs_folder}")

        # Get screen dimensions
        screen_size = manager.get_root_container().get_container().get_size()
        self.screen_width = screen_size[0]
        self.screen_height = screen_size[1]

        # Create UI panels
        self._create_background()
        self._create_planet_report_panel()
        self._create_design_report_panel()
        self._create_items_list_panel()
        self._create_build_queue_panel()
        self._create_filter_panel()
        self._create_bottom_bar()

        # Load initial designs
        self._refresh_items_list()
        self._refresh_queue_display()

    def _create_background(self):
        """Create semi-transparent background overlay."""
        self.background = ui.UIPanel(
            relative_rect=pygame.Rect(0, 0, self.screen_width, self.screen_height),
            manager=self.manager
        )

    def _create_planet_report_panel(self):
        """Create top-left panel showing comprehensive planet information."""
        # Match strategy screen dimensions exactly
        planet_report_width = 580  # Strategy screen sidebar width (600) - margins (20)
        planet_report_height = int((self.screen_height - 20) / 3)  # Strategy screen calculation

        # Ensure minimum height
        if planet_report_height < 350:
            planet_report_height = 350

        self.planet_report = PlanetReportPanel(
            manager=self.manager,
            rect=pygame.Rect(10, 10, planet_report_width, planet_report_height),
            planet=self.planet,
            container=self.background
        )

        # Update with portrait surface if provided
        if self.portrait_surface:
            self.planet_report.update_planet(self.planet, self.portrait_surface)

    def _create_design_report_panel(self):
        """Create right column showing selected design information."""
        # Design panel is a tall column on the far right
        design_report_width = 400  # Single column width
        design_report_x = self.screen_width - design_report_width - 10  # Far right
        design_report_height = self.screen_height - 90  # Nearly full height (leave room for bottom bar)

        self.design_report = DesignReportPanel(
            manager=self.manager,
            rect=pygame.Rect(design_report_x, 10, design_report_width, design_report_height),
            container=self.background
        )

    def _create_items_list_panel(self):
        """Create available designs panel to the right of categories, below planet report."""
        # Position to the right of categories panel
        categories_width = 200
        panel_left = 10 + categories_width + 10  # Right of categories with gap
        panel_width = 360  # Wider to fit under planet report

        # Position below planet report (aligned with categories)
        planet_report_height = int((self.screen_height - 20) / 3)
        if planet_report_height < 350:
            planet_report_height = 350
        panel_top = 10 + planet_report_height + 10  # Below planet report with gap

        # Height matches categories panel
        panel_height = self.screen_height - panel_top - 80  # Leave room for bottom bar

        self.items_list_panel = ui.UIPanel(
            relative_rect=pygame.Rect(panel_left, panel_top, panel_width, panel_height),
            manager=self.manager,
            container=self.background
        )

        # Header
        ui.UITextBox(
            relative_rect=pygame.Rect(10, 10, panel_width - 20, 30),
            html_text="<b>Available Designs</b>",
            manager=self.manager,
            container=self.items_list_panel
        )

        # Scrollable list
        self.items_scrollable = ui.UIScrollingContainer(
            relative_rect=pygame.Rect(10, 45, panel_width - 20, panel_height - 55),
            manager=self.manager,
            container=self.items_list_panel
        )

    def _create_build_queue_panel(self):
        """Create build queue panel in the middle column."""
        # Position: right of available designs panel
        categories_width = 200
        available_designs_width = 360
        panel_left = 10 + categories_width + 10 + available_designs_width + 10  # After categories and available designs

        # Width: remaining space between available designs and design details
        design_details_width = 400
        panel_width = self.screen_width - panel_left - design_details_width - 20  # Space between panels

        # Ensure minimum width
        if panel_width < 300:
            panel_width = 300

        # Nearly full height (starts at top)
        panel_top = 10
        panel_height = self.screen_height - panel_top - 80  # Leave room for bottom bar

        self.build_queue_panel = ui.UIPanel(
            relative_rect=pygame.Rect(panel_left, panel_top, panel_width, panel_height),
            manager=self.manager,
            container=self.background
        )

        # Header
        ui.UITextBox(
            relative_rect=pygame.Rect(10, 10, panel_width - 20, 30),
            html_text="<b>Build Queue</b>",
            manager=self.manager,
            container=self.build_queue_panel
        )

        # Scrollable queue
        self.queue_scrollable = ui.UIScrollingContainer(
            relative_rect=pygame.Rect(10, 45, panel_width - 20, panel_height - 55),
            manager=self.manager,
            container=self.build_queue_panel
        )

    def _create_filter_panel(self):
        """Create categories panel below planet report on far left."""
        panel_width = 200  # Width for categories
        panel_left = 10  # Far left, below planet report

        # Position below planet report
        planet_report_height = int((self.screen_height - 20) / 3)
        if planet_report_height < 350:
            planet_report_height = 350
        panel_top = 10 + planet_report_height + 10  # Below planet report with gap

        # Height matches available designs panel
        panel_height = self.screen_height - panel_top - 80  # Leave room for bottom bar

        self.filter_panel = ui.UIPanel(
            relative_rect=pygame.Rect(panel_left, panel_top, panel_width, panel_height),
            manager=self.manager,
            container=self.background
        )

        # Category buttons
        ui.UITextBox(
            relative_rect=pygame.Rect(10, 10, panel_width - 20, 30),
            html_text="<b>Categories</b>",
            manager=self.manager,
            container=self.filter_panel
        )

        self.btn_category_complex = ui.UIButton(
            relative_rect=pygame.Rect(10, 45, panel_width - 20, 40),
            text="Complexes",
            manager=self.manager,
            container=self.filter_panel
        )

        self.btn_category_ship = ui.UIButton(
            relative_rect=pygame.Rect(10, 95, panel_width - 20, 40),
            text="Ships",
            manager=self.manager,
            container=self.filter_panel
        )

        self.btn_category_satellite = ui.UIButton(
            relative_rect=pygame.Rect(10, 145, panel_width - 20, 40),
            text="Satellites",
            manager=self.manager,
            container=self.filter_panel
        )

        self.btn_category_fighter = ui.UIButton(
            relative_rect=pygame.Rect(10, 195, panel_width - 20, 40),
            text="Fighters",
            manager=self.manager,
            container=self.filter_panel
        )

        # Action buttons
        ui.UITextBox(
            relative_rect=pygame.Rect(10, 260, panel_width - 20, 30),
            html_text="<b>Actions</b>",
            manager=self.manager,
            container=self.filter_panel
        )

        self.btn_add_to_queue = ui.UIButton(
            relative_rect=pygame.Rect(10, 295, panel_width - 20, 40),
            text="Add to Queue",
            manager=self.manager,
            container=self.filter_panel
        )

        self.btn_remove_from_queue = ui.UIButton(
            relative_rect=pygame.Rect(10, 345, panel_width - 20, 40),
            text="Remove Selected",
            manager=self.manager,
            container=self.filter_panel
        )

    def _create_bottom_bar(self):
        """Create bottom bar with close button and turn info."""
        bar_height = 60
        bar_top = self.screen_height - bar_height - 10

        self.bottom_bar = ui.UIPanel(
            relative_rect=pygame.Rect(10, bar_top, self.screen_width - 20, bar_height),
            manager=self.manager,
            container=self.background
        )

        self.btn_close = ui.UIButton(
            relative_rect=pygame.Rect(10, 10, 120, 40),
            text="Close",
            manager=self.manager,
            container=self.bottom_bar
        )

        # Turn info
        turn_number = getattr(self.session, 'turn', 0)
        ui.UILabel(
            relative_rect=pygame.Rect(self.screen_width - 200, 10, 180, 40),
            text=f"Turn: {turn_number}",
            manager=self.manager,
            container=self.bottom_bar
        )

    def _load_designs_by_category(self, category: str):
        """
        Load designs filtered by vehicle type.

        Args:
            category: One of "complex", "ship", "satellite", "fighter"

        Returns:
            List of design objects matching the category
        """
        from game.core.logger import log_debug

        all_designs = self.design_library.scan_designs()
        log_debug(f"BuildQueue: Scanned {len(all_designs)} total designs from {self.design_library.designs_folder}")

        type_map = {
            "complex": "Planetary Complex",
            "ship": "Ship",
            "satellite": "Satellite",
            "fighter": "Fighter"
        }

        target_type = type_map.get(category, "Ship")
        log_debug(f"BuildQueue: Filtering for category '{category}' (vehicle_type='{target_type}')")

        filtered = [d for d in all_designs if d.vehicle_type == target_type]
        log_debug(f"BuildQueue: Found {len(filtered)} designs matching category '{category}'")

        if filtered:
            for d in filtered:
                log_debug(f"  - {d.name} (vehicle_type={d.vehicle_type}, design_id={d.design_id})")

        return filtered

    def _refresh_items_list(self):
        """Refresh the items list based on selected category."""
        # Clear existing items - kill all children
        # BUG-25: Copy list to avoid mutation during iteration
        elements_to_kill = list(self.items_scrollable.get_container().elements)
        for element in elements_to_kill:
            element.kill()

        # Load designs for current category
        designs = self._load_designs_by_category(self.selected_category)

        # Create UI elements for each design with portrait icons
        y_offset = 0
        icon_size = 36  # Small icon size
        btn_height = 40
        for design in designs:
            # Create horizontal container panel for icon + button
            row_panel = ui.UIPanel(
                relative_rect=pygame.Rect(0, y_offset, 260, btn_height),
                manager=self.manager,
                container=self.items_scrollable,
                object_id="#design_row_panel"
            )

            # Load miniature portrait icon
            portrait_surface = self._load_design_portrait(design, icon_size)
            if portrait_surface:
                icon_img = ui.UIImage(
                    relative_rect=pygame.Rect(2, 2, icon_size, icon_size),
                    image_surface=portrait_surface,
                    manager=self.manager,
                    container=row_panel
                )

            # Button positioned to the right of the icon
            btn = ui.UIButton(
                relative_rect=pygame.Rect(icon_size + 4, 0, 260 - icon_size - 8, btn_height),
                text=design.name,
                manager=self.manager,
                container=row_panel
            )
            btn.design_id = design.design_id  # Store design_id on button
            row_panel.design_id = design.design_id  # Also store on panel for hit testing

            y_offset += btn_height + 5

        if not designs:
            ui.UILabel(
                relative_rect=pygame.Rect(10, 10, 240, 30),
                text="No designs available",
                manager=self.manager,
                container=self.items_scrollable
            )

    def _load_design_portrait(self, design, size: int) -> Optional[pygame.Surface]:
        """
        Load a miniature portrait for a design.

        Args:
            design: DesignMetadata object
            size: Size of the square icon in pixels

        Returns:
            Scaled pygame.Surface or None if not found
        """
        import os
        import re

        # Get theme from session's player empire
        theme = "Federation"  # Default
        if hasattr(self.session, 'player_empire') and hasattr(self.session.player_empire, 'empire_theme_id'):
            theme = self.session.player_empire.empire_theme_id

        ship_class = getattr(design, 'ship_class', 'Unknown')
        if not isinstance(ship_class, str):
            ship_class = str(ship_class) if ship_class else 'Unknown'

        # Parse ship class name (handle formats like "Large Escort (Scout)")
        match = re.match(r"(.*)\s+\((.*)\)", ship_class)
        if match:
            base = match.group(1).strip().replace(" ", "")
            sub = match.group(2).strip().replace(" ", "")
            class_clean = f"{sub}{base}"
        else:
            class_clean = ship_class.replace(" ", "")

        filename = f"{class_clean}_Portrait.jpg"

        # Try multiple locations for portrait image
        portrait_paths = [
            os.path.join("assets", "ShipThemes", theme, "Portraits", filename),
            os.path.join("resources", "Portraits", theme, filename),
            os.path.join("assets", "Images", "Default_Ship_Portrait.png")
        ]

        for path in portrait_paths:
            if os.path.exists(path):
                try:
                    loaded_img = pygame.image.load(path)
                    return pygame.transform.smoothscale(loaded_img, (size, size))
                except Exception as e:
                    log_warning(f"Failed to load portrait from '{path}': {e}")
                    continue

        # Fallback: Create a colored placeholder based on vehicle type
        placeholder = pygame.Surface((size, size))
        vehicle_type = getattr(design, 'vehicle_type', 'Ship')
        color_map = {
            'Ship': (80, 100, 180),      # Blue for ships
            'Complex': (80, 180, 100),   # Green for complexes/facilities
            'Station': (180, 100, 80),   # Red for stations
            'Fighter': (180, 180, 80),   # Yellow for fighters
        }
        color = color_map.get(vehicle_type, (100, 100, 100))
        placeholder.fill(color)

        # Draw simple icon shape
        pygame.draw.rect(placeholder, (255, 255, 255), placeholder.get_rect(), 1)

        return placeholder

    def _refresh_queue_display(self):
        """Refresh the build queue display."""
        # Clear existing queue items - copy list to avoid mutation during iteration (BUG-26)
        elements_to_kill = list(self.queue_scrollable.get_container().elements)
        for element in elements_to_kill:
            element.kill()
        self.queue_items = []

        # Display each item in the queue
        y_offset = 0
        icon_size = 50  # Portrait icon size for queue items
        for idx, item in enumerate(self.planet.construction_queue):
            # Dict format: {"design_id": ..., "type": ..., "turns_remaining": N}
            design_id = item.get("design_id", "Unknown")
            turns = item.get("turns_remaining", 0)
            item_type = item.get("type", "ship")

            # Queue item panel - highlight if selected
            is_selected = (idx == self.selected_queue_index)
            panel_object_id = "#queue_item_selected" if is_selected else "#queue_item"

            item_panel = ui.UIPanel(
                relative_rect=pygame.Rect(0, y_offset, self.queue_scrollable.get_container().get_size()[0] - 20, 60),
                manager=self.manager,
                container=self.queue_scrollable,
                object_id=panel_object_id
            )
            item_panel.queue_index = idx  # Tag for reordering
            item_panel.item_data = item   # Store original data
            item_panel.is_selected = is_selected  # Track selection state

            # Load and display portrait icon
            portrait_surface = self._load_queue_item_portrait(design_id, item_type, icon_size)
            if portrait_surface:
                ui.UIImage(
                    relative_rect=pygame.Rect(5, 5, icon_size, icon_size),
                    image_surface=portrait_surface,
                    manager=self.manager,
                    container=item_panel
                )

            # Design name and turns (offset to right of icon)
            label_x = icon_size + 15
            ui.UILabel(
                relative_rect=pygame.Rect(label_x, 10, 250, 25),
                text=f"{design_id}",
                manager=self.manager,
                container=item_panel
            )

            ui.UILabel(
                relative_rect=pygame.Rect(label_x, 35, 200, 20),
                text=f"{turns} turns remaining | Type: {item_type}",
                manager=self.manager,
                container=item_panel
            )

            self.queue_items.append(item_panel)
            y_offset += 65

        if not self.planet.construction_queue:
            ui.UILabel(
                relative_rect=pygame.Rect(10, 10, 300, 30),
                text="Queue is empty",
                manager=self.manager,
                container=self.queue_scrollable
            )

    def _load_queue_item_portrait(self, design_id: str, item_type: str, size: int) -> Optional[pygame.Surface]:
        """
        Load a miniature portrait for a queue item.

        Args:
            design_id: ID of the design
            item_type: Type of item (ship, complex, etc.)
            size: Size of the square icon in pixels

        Returns:
            Scaled pygame.Surface or None if not found
        """
        # Try to find design metadata for this design_id
        designs = self.design_library.scan_designs()
        design = next((d for d in designs if d.design_id == design_id), None)

        if design:
            return self._load_design_portrait(design, size)

        # Fallback: Create a colored placeholder based on item type
        placeholder = pygame.Surface((size, size))
        type_lower = item_type.lower() if item_type else 'unknown'
        color_map = {
            'ship': (80, 100, 180),      # Blue for ships
            'complex': (80, 180, 100),   # Green for complexes/facilities
            'station': (180, 100, 80),   # Red for stations
            'fighter': (180, 180, 80),   # Yellow for fighters
            'planetary complex': (80, 180, 100),  # Green
        }
        color = color_map.get(type_lower, (100, 100, 100))
        placeholder.fill(color)
        pygame.draw.rect(placeholder, (255, 255, 255), placeholder.get_rect(), 1)

        return placeholder

    def _set_category(self, category: str):
        """Set the active category filter."""
        self.selected_category = category
        self._refresh_items_list()
        log_info(f"Build queue category changed to: {category}")

    def _add_to_queue(self, design_id: str, turns: int = 1, category: str = None, index: int = None):
        """
        Add a design to the planet's construction queue.

        Args:
            design_id: ID of the design to build
            turns: Number of turns to complete (default 5)
            category: Design category (uses self.selected_category if None)
            index: Optional insertion index
        """
        cat = category if category is not None else self.selected_category

        # DIAGNOSTIC LOGGING for BUG-24 investigation
        log_info(f"_add_to_queue called: design_id={design_id}, category={cat}")
        log_info(f"  planet.has_space_shipyard = {self.planet.has_space_shipyard}")
        log_info(f"  planet.facilities count = {len(self.planet.facilities)}")
        for i, f in enumerate(self.planet.facilities):
            log_info(f"    [{i}] {f.name} (operational={f.is_operational})")
            log_info(f"        design_data layers: {list(f.design_data.get('layers', {}).keys())}")
            # Show component IDs in each layer
            for layer_name, layer_data in f.design_data.get('layers', {}).items():
                if isinstance(layer_data, list):
                    comp_ids = [c.get('id', 'unknown') for c in layer_data if isinstance(c, dict)]
                    log_info(f"        {layer_name} components: {comp_ids}")

        # Validate shipyard requirement for ships
        if cat == "ship" and not self.planet.has_space_shipyard:
            log_warning("Cannot build ships without a space shipyard")
            return

        # Prepare queue item
        queue_item = {
            "design_id": design_id,
            "type": cat,
            "turns_remaining": turns
        }

        # Add to queue
        if index is not None:
            self.planet.construction_queue.insert(index, queue_item)
            log_info(f"Inserted {design_id} into build queue at position {index}")
        else:
            self.planet.construction_queue.append(queue_item)
            log_info(f"Added {design_id} to build queue ({turns} turns)")

        # Refresh display
        self._refresh_queue_display()

    def _refresh_design_report(self, design_id: str):
        """
        Update design report panel with selected design.

        Args:
            design_id: Design ID to load and display
        """
        try:
            # Load design data using DesignLibrary (strategy layer)
            design_data = self.design_library.load_design_data(design_id)

            if design_data is None:
                log_warning(f"Could not load design {design_id}: Design not found")
                self.design_report.show_placeholder()
                return

            # Create Ship using SimulationDesignLoader (simulation layer)
            loader = SimulationDesignLoader()
            ship = loader.load_ship_from_design_data(
                design_data,
                center_x=1920 // 2,
                center_y=1080 // 2
            )

            if ship is None:
                log_warning(f"Could not create ship from design {design_id}")
                self.design_report.show_placeholder()
                return

            # Update design report panel with ship data
            self.design_report.update_design(ship)
            log_debug(f"Design report updated: {ship.name}")

        except Exception as e:
            log_error(f"Error loading design {design_id}: {e}")
            import traceback
            log_error(traceback.format_exc())
            self.design_report.show_placeholder()

    def _close(self):
        """Close the build queue screen."""
        # Kill all UI elements
        self.background.kill()

        # Call close callback
        if self.on_close:
            self.on_close()

    def handle_event(self, event: pygame.event.Event):
        """
        Handle UI events for the build queue screen.

        Args:
            event: pygame event
        """
        # BUG-15 DEBUG: Log all keyboard events to trace screenshot issue
        if event.type == pygame.KEYDOWN:
            log_debug(f"BuildQueueScreen.handle_event: KEYDOWN received, key={event.key}, K_F12={pygame.K_F12}")
            if event.key == pygame.K_F12:
                log_info("BuildQueueScreen: F12 detected BEFORE manager.process_events()")

        # Pass event to UIManager first so it can process it
        self.manager.process_events(event)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            # Category buttons
            if event.ui_element == self.btn_category_complex:
                self._set_category("complex")
            elif event.ui_element == self.btn_category_ship:
                self._set_category("ship")
            elif event.ui_element == self.btn_category_satellite:
                self._set_category("satellite")
            elif event.ui_element == self.btn_category_fighter:
                self._set_category("fighter")

            # Close button
            elif event.ui_element == self.btn_close:
                self._close()

            # Add to queue button
            elif event.ui_element == self.btn_add_to_queue:
                if self.selected_design:
                    self._add_to_queue(self.selected_design, turns=1)

            # Remove selected from queue button
            elif event.ui_element == self.btn_remove_from_queue:
                if self.selected_queue_index is not None and self.selected_queue_index < len(self.planet.construction_queue):
                    removed_item = self.planet.construction_queue.pop(self.selected_queue_index)
                    design_id = removed_item.get('design_id', 'Unknown')
                    log_info(f"Removed {design_id} from queue at index {self.selected_queue_index}")
                    self.selected_queue_index = None
                    self._refresh_queue_display()
                else:
                    log_warning("No queue item selected to remove")
        # Design selection and drag handled in MOUSEBUTTONDOWN/UP below

        # Handle Drag Start (on mouse down for immediate dragging)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if mouse is over a design button in the items list
            # We use absolute rects for reliable hit testing with event.pos
            for element in self.items_scrollable.get_container().elements:
                if hasattr(element, 'design_id'):
                    abs_rect = element.get_abs_rect()
                    if abs_rect.collidepoint(event.pos):
                        design_id = element.design_id
                        self.selected_design = design_id

                        # Update design report panel
                        self._refresh_design_report(design_id)

                        # Start dragging
                        designs = self.design_library.scan_designs()
                        design = next((d for d in designs if d.design_id == design_id), None)
                        if design:
                            # Load portrait icon for drag preview (48px for cursor visibility)
                            portrait = self._load_design_portrait(design, 48)
                            self.dragged_item = {
                                'design_id': design.design_id,
                                'name': design.name,
                                'category': self.selected_category,
                                'portrait': portrait
                            }
                        log_info(f"Started drag from mouse down: {self.selected_design}")
                        break
                
            # Check if mouse is over a queue item panel - track for potential drag
            for element in self.queue_items:
                if element.get_abs_rect().collidepoint(event.pos):
                    idx = getattr(element, 'queue_index', -1)
                    if idx != -1:
                        # Store start position for drag threshold check
                        self.drag_start_pos = event.pos
                        self._pending_queue_index = idx  # Track which item might be dragged
                    break

        # Handle Mouse Motion for drag threshold check
        if event.type == pygame.MOUSEMOTION and event.buttons[0]:
            if self.drag_start_pos and hasattr(self, '_pending_queue_index') and self._pending_queue_index is not None:
                # Check if we've moved past drag threshold
                dx = abs(event.pos[0] - self.drag_start_pos[0])
                dy = abs(event.pos[1] - self.drag_start_pos[1])
                if dx > self.drag_threshold or dy > self.drag_threshold:
                    # Start actual drag - pick up from queue
                    idx = self._pending_queue_index
                    if idx < len(self.planet.construction_queue):
                        item = self.planet.construction_queue.pop(idx)
                        design_id = item.get('design_id', 'Unknown')
                        item_type = item.get('type', 'ship')

                        # Load portrait icon for drag preview
                        portrait = self._load_queue_item_portrait(design_id, item_type, 48)

                        self.dragged_item = {
                            'design_id': design_id,
                            'name': design_id,
                            'category': item_type,
                            'turns': item.get('turns_remaining', 0),
                            'source': 'queue',
                            'portrait': portrait
                        }
                        log_info(f"Picked up {self.dragged_item['design_id']} from queue at pos {idx}")
                        self._refresh_queue_display()
                    # Clear pending state
                    self._pending_queue_index = None
                    self.drag_start_pos = None

        # Handle Drag End / Click Selection
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            # Check if this was a click (not a drag) on a queue item - select it
            if hasattr(self, '_pending_queue_index') and self._pending_queue_index is not None and not self.dragged_item:
                # This was a click without dragging - select the item
                self.selected_queue_index = self._pending_queue_index
                log_info(f"Selected queue item at index {self.selected_queue_index}")
                self._refresh_queue_display()  # Refresh to show selection highlight

            # Clear pending drag state
            self._pending_queue_index = None
            self.drag_start_pos = None

            if self.dragged_item:
                # Track if we need to refresh (item came from queue)
                came_from_queue = self.dragged_item.get('source') == 'queue'

                # Check if dropped over build queue panel
                if self.build_queue_panel.rect.collidepoint(event.pos):
                    # Calculate insertion index based on vertical mouse position
                    rel_y = event.pos[1] - self.queue_scrollable.get_abs_rect().top

                    # Estimate index: each item is ~65 pixels high
                    estimated_idx = rel_y // 65
                    insert_idx = max(0, min(int(estimated_idx), len(self.planet.construction_queue)))

                    turns = self.dragged_item.get('turns', 1)
                    self._add_to_queue(
                        self.dragged_item['design_id'],
                        turns=turns,
                        category=self.dragged_item['category'],
                        index=insert_idx
                    )
                    log_info(f"Dropped {self.dragged_item['design_id']} into queue at index {insert_idx}")
                else:
                    log_info(f"Dropped {self.dragged_item['design_id']} outside - removed from queue or cancelled drag")
                    # If item came from queue and dropped outside, refresh to show removal
                    if came_from_queue:
                        self._refresh_queue_display()

                # Clear drag state
                self.dragged_item = None

        # Handle keyboard events for screenshots
        if event.type == pygame.KEYDOWN:
            log_debug(f"BuildQueueScreen: Reached keyboard handler section, key={event.key}")
            if event.key == pygame.K_F12:
                log_info("BuildQueueScreen: F12 matched, calling _take_screenshot()")
                self._take_screenshot()
            elif event.key == pygame.K_F11:
                log_info("BuildQueueScreen: F11 matched, calling _take_screenshot()")
                self._take_screenshot()

    def _take_screenshot(self):
        """Take a screenshot of the current screen including the build queue."""
        log_info("BuildQueueScreen._take_screenshot() ENTERED")
        sm = ScreenshotManager.instance()
        log_info(f"BuildQueueScreen: ScreenshotManager.enabled = {sm.enabled}")
        log_info(f"BuildQueueScreen: ScreenshotManager.base_dir = {sm.base_dir}")
        sm.capture(label="build_queue")
        log_info("BuildQueueScreen: sm.capture() completed")
        self._show_screenshot_toast()
        log_info("BuildQueueScreen._take_screenshot() EXITING")

    def _show_screenshot_toast(self):
        """Show a brief toast notification for screenshot feedback."""
        try:
            toast_rect = pygame.Rect(0, 0, 300, 60)
            toast_rect.center = (self.screen_width // 2, 80)
            pygame_gui.windows.UIMessageWindow(
                rect=toast_rect,
                html_message="<b>Screenshot saved!</b><br>Path copied to clipboard",
                manager=self.manager,
                window_title="Screenshot"
            )
        except Exception:
            pass

    def update(self, time_delta: float):
        """
        Update the UI manager.

        Args:
            time_delta: Time since last update
        """
        self.manager.update(time_delta)

    def draw(self, screen: pygame.Surface):
        """
        Draw the UI.

        Args:
            screen: pygame surface to draw on
        """
        self.manager.draw_ui(screen)

        # Draw selection highlight on selected queue item
        if self.selected_queue_index is not None:
            for item_panel in self.queue_items:
                if getattr(item_panel, 'queue_index', -1) == self.selected_queue_index:
                    # Draw bright border around selected item
                    abs_rect = item_panel.get_abs_rect()
                    pygame.draw.rect(screen, (100, 180, 255), abs_rect, 3)  # Blue highlight border
                    break

        # Draw drag preview - using portrait icon attached to cursor
        if self.dragged_item:
            mouse_pos = pygame.mouse.get_pos()
            portrait = self.dragged_item.get('portrait')

            if portrait:
                # Icon follows cursor - offset slightly so icon is visible
                icon_x = mouse_pos[0] + 8
                icon_y = mouse_pos[1] + 8
                icon_size = portrait.get_width()

                # Draw drop shadow for depth
                shadow_surf = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
                shadow_surf.fill((0, 0, 0, 100))
                screen.blit(shadow_surf, (icon_x + 3, icon_y + 3))

                # Draw the portrait icon
                screen.blit(portrait, (icon_x, icon_y))

                # Draw bright border around icon
                icon_rect = pygame.Rect(icon_x, icon_y, icon_size, icon_size)
                pygame.draw.rect(screen, (150, 220, 255), icon_rect, 2)
            else:
                # Fallback: simple colored square with name if no portrait
                icon_size = 48
                icon_x = mouse_pos[0] + 8
                icon_y = mouse_pos[1] + 8

                # Draw colored placeholder
                color_map = {
                    'ship': (80, 100, 180),
                    'complex': (80, 180, 100),
                    'satellite': (180, 100, 80),
                    'fighter': (180, 180, 80),
                }
                color = color_map.get(self.dragged_item.get('category', 'ship'), (100, 100, 100))

                placeholder = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
                placeholder.fill(color)
                screen.blit(placeholder, (icon_x, icon_y))

                # Draw border
                icon_rect = pygame.Rect(icon_x, icon_y, icon_size, icon_size)
                pygame.draw.rect(screen, (150, 220, 255), icon_rect, 2)
