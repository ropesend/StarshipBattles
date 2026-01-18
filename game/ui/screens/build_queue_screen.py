"""
Build Queue Screen - Full-screen interface for managing planetary construction.
"""

import pygame
import pygame_gui
import pygame_gui.elements as ui
from typing import Optional, Callable
from game.strategy.data.planet import Planet
from game.strategy.systems.design_library import DesignLibrary
from game.core.logger import log_info, log_warning, log_error, log_debug
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

        # Load design library
        from game.core.logger import log_debug, log_info

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
            item_panel.queue_index = idx  # Tag for reordering
            item_panel.item_data = item   # Store original data

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

    def _add_to_queue(self, design_id: str, turns: int = 5, category: str = None, index: int = None):
        """
        Add a design to the planet's construction queue.

        Args:
            design_id: ID of the design to build
            turns: Number of turns to complete (default 5)
            category: Design category (uses self.selected_category if None)
            index: Optional insertion index
        """
        cat = category if category is not None else self.selected_category
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
            # Load design using DesignLibrary
            ship, message = self.design_library.load_design(design_id, width=1920, height=1080)

            if ship is None:
                log_warning(f"Could not load design {design_id}: {message}")
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
                            self.dragged_item = {
                                'design_id': design.design_id,
                                'name': design.name,
                                'category': self.selected_category
                            }
                        log_info(f"Started drag from mouse down: {self.selected_design}")
                        break
                
            # Check if mouse is over a queue item panel
            for element in self.queue_items:
                if element.get_abs_rect().collidepoint(event.pos):
                    # Pick up from queue
                    idx = getattr(element, 'queue_index', -1)
                    if idx != -1:
                        item = self.planet.construction_queue.pop(idx)
                        
                        self.dragged_item = {
                            'design_id': item.get('design_id') if isinstance(item, dict) else item[0],
                            'name': item.get('design_id') if isinstance(item, dict) else item[0],
                            'category': item.get('type') if isinstance(item, dict) else 'ship',
                            'turns': item.get('turns_remaining') if isinstance(item, dict) else item[1],
                            'source': 'queue'
                        }
                        log_info(f"Picked up {self.dragged_item['design_id']} from queue at pos {idx}")
                        self._refresh_queue_display()
                    break

        # Handle Drag End
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragged_item:
                # Check if dropped over build queue panel
                if self.build_queue_panel.rect.collidepoint(event.pos):
                    # Calculate insertion index based on vertical mouse position
                    rel_y = event.pos[1] - self.queue_scrollable.get_abs_rect().top
                    
                    # Estimate index: each item is ~65 pixels high
                    estimated_idx = rel_y // 65
                    insert_idx = max(0, min(int(estimated_idx), len(self.planet.construction_queue)))

                    turns = self.dragged_item.get('turns', 5)
                    self._add_to_queue(
                        self.dragged_item['design_id'], 
                        turns=turns, 
                        category=self.dragged_item['category'],
                        index=insert_idx
                    )
                    log_info(f"Dropped {self.dragged_item['design_id']} into queue at index {insert_idx}")
                else:
                    log_info(f"Dropped {self.dragged_item['design_id']} outside - removed from queue or cancelled drag")
                
                # Clear drag state
                self.dragged_item = None

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

        # Draw drag preview
        if self.dragged_item:
            mouse_pos = pygame.mouse.get_pos()
            
            # Draw semi-transparent background for preview
            preview_rect = pygame.Rect(mouse_pos[0] + 10, mouse_pos[1] + 10, 150, 30)
            overlay = pygame.Surface((preview_rect.width, preview_rect.height), pygame.SRCALPHA)
            overlay.fill((100, 100, 255, 128))  # Semi-transparent blue
            screen.blit(overlay, preview_rect.topleft)
            
            # Draw text
            font = pygame.font.SysFont(None, 24)
            text_surf = font.render(self.dragged_item['name'], True, (255, 255, 255))
            screen.blit(text_surf, (preview_rect.x + 5, preview_rect.y + 5))
            
            # Draw border
            pygame.draw.rect(screen, (255, 255, 255), preview_rect, 1)
