"""
Build Queue Screen - Full-screen interface for managing build queues.

Supports both Planet and Fleet build contexts (PROJ-67 Phase 4).
Updated in PROJ-69 Phase 3 to support multiple queue sources at a hex.
"""
from __future__ import annotations

import pygame
import pygame_gui
import pygame_gui.elements as ui
import pygame_gui.windows
from typing import TYPE_CHECKING, List, Optional, Callable, Set, Union

from game.core.config import UIConfig
from game.core.logger import log_info, log_warning, log_error, log_debug
from game.core.screenshot_manager import ScreenshotManager
from game.ui.panels.planet_report_panel import PlanetReportPanel
from game.ui.panels.design_report_panel import DesignReportPanel
from game.ui.panels.build_queue_portraits import BuildQueuePortraitLoader
from game.ui.panels.build_queue_drag_handler import BuildQueueDragHandler
from game.ui.panels.build_queue_controller import BuildQueueController
from game.strategy.data.build_queue_source import BuildQueueSource, collect_build_queues_at_hex

if TYPE_CHECKING:
    from game.strategy.data.build_context import BuildContext
    from game.strategy.data.planet import Planet
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.hex_math import HexCoord
    from game.strategy.data.galaxy import Galaxy
    from game.strategy.data.empire import Empire
    from game.strategy.systems.design_library import DesignLibrary
    from game.simulation.services.design_loader import SimulationDesignLoader


class BuildQueueScreen:
    """Full-screen modal interface for managing build queues on planets or fleets."""

    def __init__(
        self,
        manager: pygame_gui.UIManager,
        build_context: Union['Planet', 'Fleet', 'BuildContext'],
        session,
        on_close_callback: Callable,
        portrait_surface: Optional[pygame.Surface] = None,
        design_library: 'DesignLibrary' = None,
        design_loader: 'SimulationDesignLoader' = None,
        hex_coord: Optional['HexCoord'] = None,
        galaxy: Optional['Galaxy'] = None,
        empire: Optional['Empire'] = None
    ):
        """
        Initialize the build queue screen.

        Args:
            manager: pygame_gui UIManager
            build_context: Planet or Fleet whose build queue is being managed
            session: Game session with current_empire and savegame_path
            on_close_callback: Function to call when screen closes
            portrait_surface: Optional pygame Surface for context portrait
            design_library: Injected DesignLibrary instance (PROJ-40: DI pattern)
            design_loader: Injected SimulationDesignLoader instance (PROJ-40: DI pattern)
            hex_coord: Hex coordinate for multi-queue discovery (PROJ-69)
            galaxy: Galaxy instance for planet lookup (PROJ-69)
            empire: Empire instance for ownership check (PROJ-69)
        """
        self.manager = manager
        self.build_context = build_context
        self.session = session
        self.on_close = on_close_callback
        self.portrait_surface = portrait_surface
        self.queue_items = []  # List of UI elements for queue display
        self.selected_queue_index = None  # Currently selected item in queue

        # PROJ-40: Use injected dependencies
        self.design_library = design_library
        self.design_loader = design_loader

        # PROJ-63: Portrait loading extracted to dedicated class
        self.portrait_loader = BuildQueuePortraitLoader(design_library, session)

        # Validate required attributes
        if not hasattr(build_context, 'owner_id'):
            raise ValueError(f"BuildQueueScreen: build_context '{getattr(build_context, 'name', 'unknown')}' missing required 'owner_id' attribute")
        if not hasattr(build_context, 'name'):
            log_warning("BuildQueueScreen: build_context missing 'name' attribute")

        # PROJ-69: Populate queue sources from hex context or single build_context
        if hex_coord is not None and galaxy is not None and empire is not None:
            self.queue_sources: List[BuildQueueSource] = collect_build_queues_at_hex(
                hex_coord, galaxy, empire
            )
        else:
            # Backward compat: wrap single build_context as a BuildQueueSource
            self.queue_sources = [BuildQueueSource(
                queue_id=f"{build_context.context_type}_{getattr(build_context, 'id', 0)}_legacy",
                display_name=getattr(build_context, 'name', 'Unknown'),
                owner_entity=build_context,
                construction_queue=build_context.construction_queue,
                can_build_ships=build_context.has_space_shipyard,
                can_build_complexes=True,
                context_type=build_context.context_type,
            )]

        # PROJ-69: Queue selection state
        self.selected_queue_indices: Set[int] = {0} if self.queue_sources else set()
        self.active_queue_source: Optional[BuildQueueSource] = (
            self.queue_sources[0] if self.queue_sources else None
        )

        log_info(f"BuildQueue: Initialized for {build_context.context_type} '{build_context.name}' (owner_id={build_context.owner_id})")
        log_info(f"BuildQueue: {len(self.queue_sources)} queue source(s) discovered")
        if self.design_library:
            log_info(f"BuildQueue: DesignLibrary with designs_folder: {self.design_library.designs_folder}")

        # Get screen dimensions
        screen_size = manager.get_root_container().get_container().get_size()
        self.screen_width = screen_size[0]
        self.screen_height = screen_size[1]

        # Create UI panels
        self._create_background()
        self._create_planet_report_panel()
        self._create_queue_selector_panel()  # PROJ-69: New queue selector column
        self._create_design_report_panel()
        self._create_items_list_panel()
        self._create_build_queue_panel()
        self._create_filter_panel()
        self._create_bottom_bar()

        # PROJ-63: Controller for queue business logic (after design_report is created)
        # PROJ-67: Updated to use build_context (supports Planet or Fleet)
        self.controller = BuildQueueController(
            build_context=self.build_context,
            design_library=self.design_library,
            design_loader=self.design_loader,
            design_report=self.design_report,
            on_queue_changed=self._refresh_queue_display
        )

        # PROJ-69: Sync controller with initial queue selection
        # Only set active queue source on controller when using hex-based multi-queue mode.
        # In legacy mode (single build_context), the controller falls back to build_context
        # which provides dynamic can_build_type() checks.
        if hex_coord is not None and self.active_queue_source is not None:
            self.controller.set_active_queue(self.active_queue_source)

        # PROJ-63: Drag-drop handling extracted to dedicated class
        self.drag_handler = BuildQueueDragHandler(
            portrait_loader=self.portrait_loader,
            design_library=self.design_library,
            on_add_to_queue=self.controller.add_to_queue,
            on_refresh_queue=self._refresh_queue_display,
            on_refresh_design_report=self.controller.refresh_design_report
        )

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
        """Create top-left panel showing context information (planet or fleet)."""
        # PROJ-69: Narrower to make room for queue selector column
        report_width = 480
        report_height = int((self.screen_height - 20) / 3)  # Strategy screen calculation

        # Ensure minimum height
        if report_height < 350:
            report_height = 350

        # PROJ-67: Show appropriate panel based on context type
        if self.build_context.context_type == "planet":
            self.planet_report = PlanetReportPanel(
                manager=self.manager,
                rect=pygame.Rect(10, 10, report_width, report_height),
                planet=self.build_context,
                container=self.background,
                portrait_surface=self.portrait_surface,
                show_complexes=False  # Match strategy UI - no separate complexes column
            )
            self.context_report = self.planet_report
        else:
            # Fleet context: create simple info panel
            self._create_fleet_info_panel(report_width, report_height)
            self.planet_report = None  # No planet report for fleets
            # self.context_report set by _create_fleet_info_panel

    def _create_fleet_info_panel(self, width: int, height: int):
        """Create simple info panel for fleet context."""
        self.context_report = ui.UIPanel(
            relative_rect=pygame.Rect(10, 10, width, height),
            manager=self.manager,
            container=self.background
        )

        # Fleet name header
        ui.UITextBox(
            relative_rect=pygame.Rect(10, 10, width - 20, 40),
            html_text=f"<b>{self.build_context.name}</b>",
            manager=self.manager,
            container=self.context_report
        )

        # Fleet info
        ship_count = len(self.build_context.ships) if hasattr(self.build_context, 'ships') else 0
        has_yard = self.build_context.has_space_shipyard
        queue_size = len(self.build_context.construction_queue)

        info_text = f"""
        <b>Ships:</b> {ship_count}<br>
        <b>Space Yard:</b> {'Yes' if has_yard else 'No'}<br>
        <b>Queue Size:</b> {queue_size} items<br>
        """

        ui.UITextBox(
            relative_rect=pygame.Rect(10, 60, width - 20, height - 80),
            html_text=info_text,
            manager=self.manager,
            container=self.context_report
        )

    def _create_queue_selector_panel(self):
        """Create queue selector column for choosing active build queue(s).

        PROJ-69: New panel showing all build queue sources at the hex,
        allowing single-click selection or ctrl+click multi-selection.
        """
        # Position: right of context report, full height
        panel_x = 10 + 480 + 10  # After context report (480w) + gap
        panel_y = 10
        panel_width = 200
        panel_height = self.screen_height - 10 - 80  # Full height minus bottom bar

        self.queue_selector_panel = ui.UIPanel(
            relative_rect=pygame.Rect(panel_x, panel_y, panel_width, panel_height),
            manager=self.manager,
            container=self.background
        )

        # Header
        ui.UITextBox(
            relative_rect=pygame.Rect(10, 10, panel_width - 20, 30),
            html_text="<b>Build Queues</b>",
            manager=self.manager,
            container=self.queue_selector_panel
        )

        # Scrollable container for queue entries
        self.queue_selector_scrollable = ui.UIScrollingContainer(
            relative_rect=pygame.Rect(5, 45, panel_width - 10, panel_height - 55),
            manager=self.manager,
            container=self.queue_selector_panel
        )

        # Store queue selector buttons for event handling
        self.queue_selector_buttons: List[ui.UIButton] = []

        self._refresh_queue_selector()

    def _refresh_queue_selector(self):
        """Rebuild queue selector UI elements to reflect current selection state."""
        # Clear existing selector entries
        elements_to_kill = list(self.queue_selector_scrollable.get_container().elements)
        for element in elements_to_kill:
            element.kill()
        self.queue_selector_buttons.clear()

        row_height = 45
        row_width = 180  # Fits inside scrollable with margin
        y_offset = 0

        for idx, source in enumerate(self.queue_sources):
            is_selected = idx in self.selected_queue_indices
            item_count = len(source.construction_queue)

            # Display name with item count
            label_text = f"{source.display_name} ({item_count})"

            # Use object_id to distinguish selected vs unselected visually
            object_id = "#queue_selector_selected" if is_selected else "#queue_selector_item"

            btn = ui.UIButton(
                relative_rect=pygame.Rect(0, y_offset, row_width, row_height),
                text=label_text,
                manager=self.manager,
                container=self.queue_selector_scrollable,
                object_id=object_id
            )
            btn.queue_source_index = idx  # Tag button with source index

            self.queue_selector_buttons.append(btn)
            y_offset += row_height + 5

        if not self.queue_sources:
            ui.UILabel(
                relative_rect=pygame.Rect(10, 10, row_width, 30),
                text="No queues available",
                manager=self.manager,
                container=self.queue_selector_scrollable
            )

    def _on_queue_selected(self, index: int):
        """Handle single-click queue selection (deselects others).

        Syncs the controller's active_queue_source for add operations.

        Args:
            index: Index into self.queue_sources to select.
        """
        self.selected_queue_indices = {index}
        self.active_queue_source = self.queue_sources[index]
        # PROJ-69: Sync controller queue source
        self.controller.set_active_queue(self.active_queue_source)
        log_info(f"BuildQueue: Selected queue '{self.active_queue_source.display_name}'")
        self._refresh_queue_selector()
        self._refresh_queue_display()

    def _on_queue_toggled(self, index: int):
        """Handle ctrl+click queue toggle for multi-select.

        Syncs the controller's queue source state for add operations.

        Args:
            index: Index into self.queue_sources to toggle.
        """
        if index in self.selected_queue_indices:
            self.selected_queue_indices.discard(index)
        else:
            self.selected_queue_indices.add(index)

        # Prevent empty selection
        if not self.selected_queue_indices:
            self.selected_queue_indices = {0}

        # Set active queue source based on selection count
        if len(self.selected_queue_indices) == 1:
            sole_idx = next(iter(self.selected_queue_indices))
            self.active_queue_source = self.queue_sources[sole_idx]
            # PROJ-69: Sync controller to single-queue mode
            self.controller.set_active_queue(self.active_queue_source)
            log_info(f"BuildQueue: Single queue selected: '{self.active_queue_source.display_name}'")
        else:
            self.active_queue_source = None
            # PROJ-69: Sync controller to multi-queue mode
            selected_sources = [
                self.queue_sources[i] for i in sorted(self.selected_queue_indices)
            ]
            self.controller.set_selected_queues(selected_sources)
            log_info(f"BuildQueue: Multi-select mode: {len(self.selected_queue_indices)} queues")

        self._refresh_queue_selector()
        self._refresh_queue_display()

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
        panel_width = 280  # PROJ-69: Narrowed to fit queue selector column

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
        # PROJ-69: Position after context report (480) + gap + queue selector (200) + gap
        panel_left = 10 + 480 + 10 + 200 + 10  # = 710

        # Width: remaining space between queue selector and design report
        design_details_width = 400
        panel_width = self.screen_width - panel_left - design_details_width - 20

        # Ensure minimum width
        if panel_width < 250:
            panel_width = 250

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

    def _refresh_items_list(self):
        """Refresh the items list based on selected category."""
        # Clear existing items - kill all children
        # BUG-25: Copy list to avoid mutation during iteration
        elements_to_kill = list(self.items_scrollable.get_container().elements)
        for element in elements_to_kill:
            element.kill()

        # Load designs for current category via controller
        designs = self.controller.load_designs_by_category(self.controller.selected_category)

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
            portrait_surface = self.portrait_loader.load_design_portrait(design, icon_size)
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

    def _refresh_queue_display(self):
        """Refresh the build queue display.

        PROJ-69: Uses active_queue_source when set (single selection),
        or shows multi-select message when multiple queues are selected.
        Also refreshes queue selector item counts.
        """
        # Clear existing queue items - copy list to avoid mutation during iteration (BUG-26)
        elements_to_kill = list(self.queue_scrollable.get_container().elements)
        for element in elements_to_kill:
            element.kill()
        self.queue_items = []

        # PROJ-69: Multi-select mode - show message instead of queue contents
        if self.active_queue_source is None and len(self.selected_queue_indices) > 1:
            selected_names = [
                self.queue_sources[i].display_name
                for i in sorted(self.selected_queue_indices)
            ]
            msg_lines = "<br>".join(f"- {name}" for name in selected_names)
            ui.UITextBox(
                relative_rect=pygame.Rect(10, 10, self.queue_scrollable.get_container().get_size()[0] - 20, 200),
                html_text=f"<b>Adding to {len(self.selected_queue_indices)} queues:</b><br>{msg_lines}",
                manager=self.manager,
                container=self.queue_scrollable
            )
            # Refresh queue selector to update item counts
            self._refresh_queue_selector()
            return

        # Determine which queue to display
        if self.active_queue_source is not None:
            queue = self.active_queue_source.construction_queue
        else:
            queue = self.build_context.construction_queue

        # Display each item in the queue
        y_offset = 0
        icon_size = 50  # Portrait icon size for queue items
        for idx, item in enumerate(queue):
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
            portrait_surface = self.portrait_loader.load_queue_item_portrait(design_id, item_type, icon_size)
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

        if not queue:
            ui.UILabel(
                relative_rect=pygame.Rect(10, 10, 300, 30),
                text="Queue is empty",
                manager=self.manager,
                container=self.queue_scrollable
            )

        # Refresh queue selector to update item counts
        self._refresh_queue_selector()

    def _close(self):
        """Close the build queue screen."""
        # Kill the background panel - this cascades to all children
        self.background.kill()

        # Force UIManager to process the kill queue
        self.manager.update(0)

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
            # Category buttons - delegate to controller
            if event.ui_element == self.btn_category_complex:
                self.controller.set_category("complex")
                self._refresh_items_list()
            elif event.ui_element == self.btn_category_ship:
                self.controller.set_category("ship")
                self._refresh_items_list()
            elif event.ui_element == self.btn_category_satellite:
                self.controller.set_category("satellite")
                self._refresh_items_list()
            elif event.ui_element == self.btn_category_fighter:
                self.controller.set_category("fighter")
                self._refresh_items_list()

            # Close button
            elif event.ui_element == self.btn_close:
                self._close()

            # Add to queue button - delegate to controller
            elif event.ui_element == self.btn_add_to_queue:
                if self.drag_handler.selected_design:
                    self.controller.add_to_queue(self.drag_handler.selected_design, turns=1)

            # Remove selected from queue button
            elif event.ui_element == self.btn_remove_from_queue:
                # PROJ-69: Disable remove in multi-select mode
                if len(self.selected_queue_indices) > 1:
                    log_warning("Cannot remove items in multi-select mode")
                else:
                    # Use active queue source's construction_queue
                    remove_queue = (
                        self.active_queue_source.construction_queue
                        if self.active_queue_source is not None
                        else self.build_context.construction_queue
                    )
                    if self.selected_queue_index is not None and self.selected_queue_index < len(remove_queue):
                        removed_item = remove_queue.pop(self.selected_queue_index)
                        design_id = removed_item.get('design_id', 'Unknown')
                        log_info(f"Removed {design_id} from queue at index {self.selected_queue_index}")
                        self.selected_queue_index = None
                        self._refresh_queue_display()
                    else:
                        log_warning("No queue item selected to remove")

            # PROJ-69: Queue selector button clicks
            elif hasattr(event.ui_element, 'queue_source_index'):
                idx = event.ui_element.queue_source_index
                # Check for ctrl held for multi-select toggle
                mods = pygame.key.get_mods()
                if mods & pygame.KMOD_CTRL:
                    self._on_queue_toggled(idx)
                else:
                    self._on_queue_selected(idx)
        # Design selection and drag handled via drag_handler

        # PROJ-69: Determine active queue and multi-select state for drag handler
        multi_select = len(self.selected_queue_indices) > 1
        active_queue = (
            self.active_queue_source.construction_queue
            if self.active_queue_source is not None
            else self.build_context.construction_queue
        )

        # Handle Drag Start (on mouse down for immediate dragging)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.drag_handler.handle_mouse_down(
                event, self.items_scrollable, self.queue_items,
                active_queue, self.controller.selected_category,
                multi_select_active=multi_select
            )

        # Handle Mouse Motion for drag threshold check
        if event.type == pygame.MOUSEMOTION and event.buttons[0]:
            self.drag_handler.handle_mouse_motion(
                event, active_queue, multi_select_active=multi_select
            )

        # Handle Drag End / Click Selection
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            result = self.drag_handler.handle_mouse_up(
                event, self.build_queue_panel, self.queue_scrollable,
                active_queue, multi_select_active=multi_select
            )
            if result is not None:
                self.selected_queue_index = result

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
            toast_rect = pygame.Rect(0, 0, UIConfig.TOAST_WIDTH, UIConfig.TOAST_HEIGHT)
            toast_rect.center = (self.screen_width // 2, 80)
            pygame_gui.windows.UIMessageWindow(
                rect=toast_rect,
                html_message="<b>Screenshot saved!</b><br>Path copied to clipboard",
                manager=self.manager,
                window_title="Screenshot"
            )
        except (AttributeError, pygame.error) as e:
            # UI element creation may fail if manager not ready
            log_debug(f"Could not show screenshot toast: {e}")

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

        # Draw drag preview via handler
        self.drag_handler.draw_drag_preview(screen)
