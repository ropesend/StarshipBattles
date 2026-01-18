"""
Build Queue Screen - Full-screen interface for managing planetary construction.
"""

import pygame
import pygame_gui
import pygame_gui.elements as ui
from typing import Optional, Callable
from game.strategy.data.planet import Planet
from game.strategy.systems.design_library import DesignLibrary
from game.core.logger import log_info, log_warning


class BuildQueueScreen:
    """Full-screen modal interface for managing build queues on planets."""

    def __init__(self, manager: pygame_gui.UIManager, planet: Planet, session, on_close_callback: Callable):
        """
        Initialize the build queue screen.

        Args:
            manager: pygame_gui UIManager
            planet: Planet object to manage build queue for
            session: Game session with current_empire and savegame_path
            on_close_callback: Function to call when screen closes
        """
        self.manager = manager
        self.planet = planet
        self.session = session
        self.on_close = on_close_callback
        self.selected_design = None
        self.selected_category = "complex"
        self.queue_items = []  # List of UI elements for queue display

        # Load design library
        from game.core.logger import log_debug

        savegame_path = getattr(session, 'save_path', None)  # FIXED: was 'savegame_path', should be 'save_path'

        # FIXED: Use planet's owner_id to determine which empire's designs to load
        # session.current_empire doesn't exist - planet.owner_id tells us who owns this planet
        empire_id = planet.owner_id

        log_debug(f"BuildQueue: Initializing DesignLibrary for planet '{planet.name}' (owner_id={empire_id})")
        log_debug(f"BuildQueue: save_path='{savegame_path}', empire_id={empire_id}")

        self.design_library = DesignLibrary(savegame_path, empire_id)

        # Get screen dimensions
        screen_size = manager.get_root_container().get_container().get_size()
        self.screen_width = screen_size[0]
        self.screen_height = screen_size[1]

        # Create UI panels
        self._create_background()
        self._create_planet_report_panel()
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
        """Create top panel showing planet information."""
        panel_height = 150
        self.planet_report_panel = ui.UIPanel(
            relative_rect=pygame.Rect(10, 10, self.screen_width - 20, panel_height),
            manager=self.manager,
            container=self.background
        )

        # Planet name
        ui.UILabel(
            relative_rect=pygame.Rect(10, 10, 400, 30),
            text=f"<b>{self.planet.name}</b>",
            manager=self.manager,
            container=self.planet_report_panel
        )

        # Planet type
        ui.UILabel(
            relative_rect=pygame.Rect(10, 45, 400, 25),
            text=f"Type: {self.planet.planet_type.name}",
            manager=self.manager,
            container=self.planet_report_panel
        )

        # Resources (if any)
        resources_text = "Resources: "
        if self.planet.resources:
            resources_list = [f"{name}: {data.get('quantity', 0)}"
                            for name, data in self.planet.resources.items()]
            resources_text += ", ".join(resources_list[:3])  # Show first 3
        else:
            resources_text += "None"

        ui.UILabel(
            relative_rect=pygame.Rect(10, 75, 600, 25),
            text=resources_text,
            manager=self.manager,
            container=self.planet_report_panel
        )

        # Facilities count
        facilities_text = f"Facilities: {len(self.planet.facilities)}"
        if self.planet.has_space_shipyard:
            facilities_text += " [Shipyard Active]"

        ui.UILabel(
            relative_rect=pygame.Rect(10, 105, 400, 25),
            text=facilities_text,
            manager=self.manager,
            container=self.planet_report_panel
        )

    def _create_items_list_panel(self):
        """Create left panel showing available designs."""
        panel_width = 300
        panel_height = self.screen_height - 350
        panel_top = 170

        self.items_list_panel = ui.UIPanel(
            relative_rect=pygame.Rect(10, panel_top, panel_width, panel_height),
            manager=self.manager,
            container=self.background
        )

        # Header
        ui.UILabel(
            relative_rect=pygame.Rect(10, 10, panel_width - 20, 30),
            text="<b>Available Designs</b>",
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
        """Create center panel showing current build queue."""
        panel_left = 320
        panel_width = self.screen_width - 320 - 270
        panel_height = self.screen_height - 350
        panel_top = 170

        self.build_queue_panel = ui.UIPanel(
            relative_rect=pygame.Rect(panel_left, panel_top, panel_width, panel_height),
            manager=self.manager,
            container=self.background
        )

        # Header
        ui.UILabel(
            relative_rect=pygame.Rect(10, 10, panel_width - 20, 30),
            text="<b>Build Queue</b>",
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
        """Create right panel with category filters and action buttons."""
        panel_width = 250
        panel_height = self.screen_height - 350
        panel_top = 170
        panel_left = self.screen_width - panel_width - 10

        self.filter_panel = ui.UIPanel(
            relative_rect=pygame.Rect(panel_left, panel_top, panel_width, panel_height),
            manager=self.manager,
            container=self.background
        )

        # Category buttons
        ui.UILabel(
            relative_rect=pygame.Rect(10, 10, panel_width - 20, 30),
            text="<b>Categories</b>",
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
        ui.UILabel(
            relative_rect=pygame.Rect(10, 260, panel_width - 20, 30),
            text="<b>Actions</b>",
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
        for element in self.items_scrollable.get_container().elements:
            element.kill()

        # Load designs for current category
        designs = self._load_designs_by_category(self.selected_category)

        # Create UI elements for each design
        y_offset = 0
        for design in designs:
            btn = ui.UIButton(
                relative_rect=pygame.Rect(0, y_offset, 260, 40),
                text=design.name,
                manager=self.manager,
                container=self.items_scrollable
            )
            btn.design_id = design.design_id  # Store design_id on button
            y_offset += 45

        if not designs:
            ui.UILabel(
                relative_rect=pygame.Rect(10, 10, 240, 30),
                text="No designs available",
                manager=self.manager,
                container=self.items_scrollable
            )

    def _refresh_queue_display(self):
        """Refresh the build queue display."""
        # Clear existing queue items - kill all children
        for element in self.queue_scrollable.get_container().elements:
            element.kill()
        self.queue_items = []

        # Display each item in the queue
        y_offset = 0
        for idx, item in enumerate(self.planet.construction_queue):
            # Handle both dict and legacy list format
            if isinstance(item, dict):
                design_id = item.get("design_id", "Unknown")
                turns = item.get("turns_remaining", 0)
                item_type = item.get("type", "unknown")
            else:
                # Legacy format: ["Ship Name", 5]
                design_id = item[0]
                turns = item[1]
                item_type = "ship"

            # Queue item panel
            item_panel = ui.UIPanel(
                relative_rect=pygame.Rect(0, y_offset, self.queue_scrollable.get_container().get_size()[0] - 20, 60),
                manager=self.manager,
                container=self.queue_scrollable
            )

            # Design name and turns
            ui.UILabel(
                relative_rect=pygame.Rect(10, 10, 300, 25),
                text=f"{design_id}",
                manager=self.manager,
                container=item_panel
            )

            ui.UILabel(
                relative_rect=pygame.Rect(10, 35, 200, 20),
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

    def _set_category(self, category: str):
        """Set the active category filter."""
        self.selected_category = category
        self._refresh_items_list()
        log_info(f"Build queue category changed to: {category}")

    def _add_to_queue(self, design_id: str, turns: int = 5):
        """
        Add a design to the planet's construction queue.

        Args:
            design_id: ID of the design to build
            turns: Number of turns to complete (default 5)
        """
        # Validate shipyard requirement for ships
        if self.selected_category == "ship" and not self.planet.has_space_shipyard:
            log_warning("Cannot build ships without a space shipyard")
            return

        # Add to queue using new dict format
        self.planet.add_production(design_id, turns=turns, vehicle_type=self.selected_category)

        log_info(f"Added {design_id} to build queue ({turns} turns)")

        # Refresh display
        self._refresh_queue_display()

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
                    self._add_to_queue(self.selected_design, turns=5)

            # Design selection from items list
            elif hasattr(event.ui_element, 'design_id'):
                self.selected_design = event.ui_element.design_id
                log_info(f"Selected design: {self.selected_design}")

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
