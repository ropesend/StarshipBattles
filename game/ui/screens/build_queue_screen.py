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
from game.core.constants import PLANET_RESOURCES
from game.core.input_actions import InputAction
from game.core.logger import log_info, log_warning, log_debug
from game.core.screenshot_manager import ScreenshotManager
from game.ui.panels.planet_report_panel import PlanetReportPanel
from game.ui.panels.design_report_panel import DesignReportPanel
from game.ui.panels.build_queue_portraits import BuildQueuePortraitLoader
from game.ui.panels.build_queue_drag_handler import BuildQueueDragHandler
from game.ui.panels.build_queue_controller import BuildQueueController
from game.strategy.data.build_queue_source import BuildQueueSource, collect_build_queues_at_hex
from game.ui.screens.planet_selection_window import PlanetSelectionWindow
from game.ui.screens.build_queue_helpers import format_empire_resources, format_resource_cost
from game.ui.screens.build_queue_selector import BuildQueueSelector

if TYPE_CHECKING:
    from game.core.input_mapper import InputMapper
    from game.strategy.data.build_context import BuildContext
    from game.strategy.data.planet import Planet
    from game.strategy.data.fleet import Fleet
    from game.core.hex_math import HexCoord
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
        empire: Optional['Empire'] = None,
        input_mapper: Optional['InputMapper'] = None
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
        self._mapper = input_mapper
        self.queue_items = []  # List of UI elements for queue display
        self.selected_queue_index = None  # Currently selected item in queue

        # PROJ-40: Use injected dependencies
        self.design_library = design_library
        self.design_loader = design_loader

        # PROJ-79: Store galaxy context for planet selection
        self.hex_coord = hex_coord
        self.galaxy = galaxy
        self.empire = empire
        self.planet_selection_window = None  # Active planet selection popup

        # PROJ-63: Portrait loading extracted to dedicated class
        self.portrait_loader = BuildQueuePortraitLoader(design_library, session)

        # PROJ-79: Load resource icons for column headers
        self.resource_icons = self.portrait_loader.load_resource_icons(icon_size=20)

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

        # PROJ-69: Queue selection state (updated by BuildQueueSelector)
        self.selected_queue_indices: Set[int] = {0} if self.queue_sources else set()
        self.active_queue_source: Optional[BuildQueueSource] = (
            self.queue_sources[0] if self.queue_sources else None
        )
        self._queue_selector: Optional[BuildQueueSelector] = None  # Set in _create_queue_selector_panel

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
        # PROJ-79: Added hex_coord, galaxy, empire for planet selection
        self.controller = BuildQueueController(
            build_context=self.build_context,
            design_library=self.design_library,
            design_loader=self.design_loader,
            design_report=self.design_report,
            on_queue_changed=self._refresh_queue_display,
            hex_coord=self.hex_coord,
            galaxy=self.galaxy,
            empire=self.empire,
            on_planet_selection_needed=self._prompt_target_planet
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

        # Apply hotkey tooltips
        self._apply_tooltips()

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

        PROJ-69: Delegates to BuildQueueSelector helper class.
        PROJ-86 Phase 8: Extracted to build_queue_selector.py.
        """
        # Position: right of context report, full height
        panel_x = 10 + 480 + 10  # After context report (480w) + gap
        panel_y = 10
        panel_width = 700  # PROJ-81: Widened from 280px for better readability
        panel_height = self.screen_height - 10 - 80  # Full height minus bottom bar

        self._queue_selector = BuildQueueSelector(
            manager=self.manager,
            container=self.background,
            rect=pygame.Rect(panel_x, panel_y, panel_width, panel_height),
            queue_sources=self.queue_sources,
            on_selection_changed=self._on_queue_selection_changed,
        )
        # Alias for backward compatibility with tests
        self.queue_selector_panel = self._queue_selector.panel
        self.queue_selector_scrollable = self._queue_selector.scrollable
        self.queue_selector_buttons = self._queue_selector.buttons

    def _refresh_queue_selector(self):
        """Rebuild queue selector UI elements to reflect current selection state."""
        if self._queue_selector:
            self._queue_selector.refresh()
            # Sync buttons list for backward compatibility
            self.queue_selector_buttons = self._queue_selector.buttons

    def _on_queue_selection_changed(
        self, active_source: Optional[BuildQueueSource], selected_indices: Set[int]
    ) -> None:
        """Handle selection change from BuildQueueSelector.

        Syncs controller queue source state and refreshes display.

        Args:
            active_source: The single active source, or None for multi-select.
            selected_indices: Set of selected queue indices.
        """
        self.active_queue_source = active_source
        self.selected_queue_indices = selected_indices

        # Sync controller with selection
        if active_source is not None:
            self.controller.set_active_queue(active_source)
        else:
            selected_sources = [
                self.queue_sources[i] for i in sorted(selected_indices)
            ]
            self.controller.set_selected_queues(selected_sources)

        self._refresh_queue_display()
        self._update_queue_header()

    def _update_queue_header(self):
        """Update build queue header to show active queue name.

        PROJ-81: Header shows "Build Queue - [name]" when a queue is selected,
        or just "Build Queue" when none/multi selected.
        """
        if self.active_queue_source is not None:
            header_text = f"<b>Build Queue - {self.active_queue_source.display_name}</b>"
        else:
            header_text = "<b>Build Queue</b>"
        self.queue_header_text.set_text(header_text)

    def _create_design_report_panel(self):
        """Create right column showing selected design information."""
        # Design panel is a tall column on the far right
        design_report_width = 750  # Two-column width (matches design workshop)
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
        # PROJ-81: Position after context report (480) + gap + queue selector (700) + gap
        panel_left = 10 + 480 + 10 + 700 + 10  # = 1210

        # Width: remaining space between queue selector and design report
        design_details_width = 750
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

        # Header (PROJ-81: stored for dynamic update, text changed to "Build Queue")
        self.queue_header_text = ui.UITextBox(
            relative_rect=pygame.Rect(10, 10, panel_width - 20, 30),
            html_text="<b>Build Queue</b>",
            manager=self.manager,
            container=self.build_queue_panel
        )

        # PROJ-79: Column header row with resource icons
        header_y = 42
        header_height = 22
        col_x = 10

        # "Item" column label (aligned with portrait + name)
        ui.UILabel(
            relative_rect=pygame.Rect(col_x, header_y, 150, header_height),
            text="Item",
            manager=self.manager,
            container=self.build_queue_panel
        )
        col_x += 155

        # "Turns" column label
        ui.UILabel(
            relative_rect=pygame.Rect(col_x, header_y, 45, header_height),
            text="Turns",
            manager=self.manager,
            container=self.build_queue_panel
        )
        col_x += 50

        # Resource icon columns (PROJ-81: increased spacing from 28 to 55px)
        self.queue_column_positions = {"Item": 10, "Turns": 165}
        for resource in PLANET_RESOURCES:
            icon = self.resource_icons.get(resource)
            if icon:
                ui.UIImage(
                    relative_rect=pygame.Rect(col_x, header_y + 1, 20, 20),
                    image_surface=icon,
                    manager=self.manager,
                    container=self.build_queue_panel
                )
            self.queue_column_positions[resource] = col_x
            col_x += 55

        # Scrollable queue - shifted down to accommodate header row
        self.queue_scrollable = ui.UIScrollingContainer(
            relative_rect=pygame.Rect(10, 68, panel_width - 20, panel_height - 78),
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

    @staticmethod
    def _format_empire_resources(empire) -> str:
        """Format empire resource pool for display in build queue bottom bar.

        PROJ-86 Phase 8: Delegates to build_queue_helpers module.
        """
        return format_empire_resources(empire)

    @staticmethod
    def _format_resource_cost(cost: dict) -> str:
        """Format resource cost dict into compact display string.

        PROJ-86 Phase 8: Delegates to build_queue_helpers module.
        """
        return format_resource_cost(cost)

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

        # Empire resource summary in bottom bar
        empire = getattr(self.session, 'current_empire', None)
        if empire and hasattr(empire, 'resource_pool'):
            resource_text = self._format_empire_resources(empire)
        else:
            resource_text = ""
        ui.UILabel(
            relative_rect=pygame.Rect(150, 10, self.screen_width - 400, 40),
            text=resource_text,
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
            # Determine row height: taller when resource costs exist
            raw_cost = getattr(design, 'resource_cost', None)
            cost = raw_cost if isinstance(raw_cost, dict) else {}
            row_height = btn_height + (18 if cost else 0)

            # Create horizontal container panel for icon + button
            row_panel = ui.UIPanel(
                relative_rect=pygame.Rect(0, y_offset, 260, row_height),
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

            # Resource cost label (compact format below button)
            if cost:
                cost_str = self._format_resource_cost(cost)
                ui.UILabel(
                    relative_rect=pygame.Rect(icon_size + 4, btn_height, 260 - icon_size - 8, 16),
                    text=cost_str,
                    manager=self.manager,
                    container=row_panel
                )

            y_offset += row_height + 5

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
        icon_size = 40  # Portrait icon size for queue items
        for idx, item in enumerate(queue):
            # Dict format: {"design_id": ..., "type": ..., "turns_remaining": N}
            design_id = item.get("design_id", "Unknown")
            turns = item.get("turns_remaining", 0)
            item_type = item.get("type", "ship")

            # Queue item panel - highlight if selected
            is_selected = (idx == self.selected_queue_index)
            panel_object_id = "#queue_item_selected" if is_selected else "#queue_item"

            # PROJ-79: Consistent panel height with columnar layout
            total_cost = item.get("total_cost")
            panel_height = 48

            item_panel = ui.UIPanel(
                relative_rect=pygame.Rect(0, y_offset, self.queue_scrollable.get_container().get_size()[0] - 20, panel_height),
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
                    relative_rect=pygame.Rect(4, 4, icon_size, icon_size),
                    image_surface=portrait_surface,
                    manager=self.manager,
                    container=item_panel
                )

            # PROJ-79: Columnar layout aligned with headers
            # Design name (aligned with "Item" column)
            name_x = icon_size + 8
            ui.UILabel(
                relative_rect=pygame.Rect(name_x, 4, 110, 20),
                text=f"{design_id[:12]}",  # Truncate to fit 110px
                manager=self.manager,
                container=item_panel
            )

            # Type on second line
            ui.UILabel(
                relative_rect=pygame.Rect(name_x, 24, 110, 20),
                text=f"{item_type}",
                manager=self.manager,
                container=item_panel
            )

            # Turns column (aligned with "Turns" header)
            turns_x = self.queue_column_positions.get("Turns", 165) - 10
            ui.UILabel(
                relative_rect=pygame.Rect(turns_x, 14, 45, 20),
                text=f"{turns}",
                manager=self.manager,
                container=item_panel
            )

            # PROJ-79: Per-turn resource cost columns (aligned under resource icons)
            if total_cost and turns > 0:
                for resource in PLANET_RESOURCES:
                    total_amt = total_cost.get(resource, 0)
                    if total_amt > 0:
                        per_turn = total_amt / turns
                        col_x = self.queue_column_positions.get(resource, 0) - 10
                        # Format: show as int if >= 1, else show one decimal
                        if per_turn >= 1:
                            cost_text = f"{int(per_turn)}"
                        else:
                            cost_text = f"{per_turn:.1f}"
                        ui.UILabel(
                            relative_rect=pygame.Rect(col_x, 14, 50, 20),
                            text=cost_text,
                            manager=self.manager,
                            container=item_panel
                        )

            self.queue_items.append(item_panel)
            y_offset += panel_height + 3

        if not queue:
            ui.UILabel(
                relative_rect=pygame.Rect(10, 10, 300, 30),
                text="Queue is empty",
                manager=self.manager,
                container=self.queue_scrollable
            )

        # Refresh queue selector to update item counts
        self._refresh_queue_selector()

    def _apply_tooltips(self) -> None:
        """Enrich buttons with hotkey hint tooltips from InputMapper."""
        if not self._mapper:
            return
        _hint = self._mapper.get_display_text
        close_hint = _hint(InputAction.BUILD_QUEUE_CLOSE)
        if close_hint:
            self.btn_close.set_tooltip(f"Close ({close_hint})")
        add_hint = _hint(InputAction.BUILD_QUEUE_ADD)
        if add_hint:
            self.btn_add_to_queue.set_tooltip(f"Add to Queue ({add_hint})")
        remove_hint = _hint(InputAction.BUILD_QUEUE_REMOVE)
        if remove_hint:
            self.btn_remove_from_queue.set_tooltip(f"Remove Selected ({remove_hint})")
        cat_c = _hint(InputAction.BUILD_QUEUE_CAT_COMPLEXES)
        if cat_c:
            self.btn_category_complex.set_tooltip(f"Complexes ({cat_c})")
        cat_s = _hint(InputAction.BUILD_QUEUE_CAT_SHIPS)
        if cat_s:
            self.btn_category_ship.set_tooltip(f"Ships ({cat_s})")
        cat_sat = _hint(InputAction.BUILD_QUEUE_CAT_SATELLITES)
        if cat_sat:
            self.btn_category_satellite.set_tooltip(f"Satellites ({cat_sat})")
        cat_f = _hint(InputAction.BUILD_QUEUE_CAT_FIGHTERS)
        if cat_f:
            self.btn_category_fighter.set_tooltip(f"Fighters ({cat_f})")

    def _handle_keydown(self, event: pygame.event.Event) -> bool:
        """Dispatch keyboard events via InputMapper.

        Args:
            event: A pygame KEYDOWN event.

        Returns:
            True if the event was handled.
        """
        if not self._mapper:
            return False
        action = self._mapper.resolve(event, contexts=["build_queue"])
        if action == InputAction.BUILD_QUEUE_CLOSE:
            self._close()
            return True
        if action == InputAction.BUILD_QUEUE_ADD:
            if self.drag_handler.selected_design:
                self.controller.add_to_queue(self.drag_handler.selected_design)
            return True
        if action == InputAction.BUILD_QUEUE_REMOVE:
            self._handle_remove_hotkey()
            return True
        if action == InputAction.BUILD_QUEUE_CAT_COMPLEXES:
            self.controller.set_category("complex")
            self._refresh_items_list()
            return True
        if action == InputAction.BUILD_QUEUE_CAT_SHIPS:
            self.controller.set_category("ship")
            self._refresh_items_list()
            return True
        if action == InputAction.BUILD_QUEUE_CAT_SATELLITES:
            self.controller.set_category("satellite")
            self._refresh_items_list()
            return True
        if action == InputAction.BUILD_QUEUE_CAT_FIGHTERS:
            self.controller.set_category("fighter")
            self._refresh_items_list()
            return True
        return False

    def _handle_remove_hotkey(self) -> None:
        """Handle remove-from-queue via hotkey."""
        if len(self.selected_queue_indices) > 1:
            log_warning("Cannot remove items in multi-select mode")
            return
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

    def _prompt_target_planet(self, planets, on_selected):
        """Open planet selection window for complex target planet.

        PROJ-79: Called by controller when fleet+complex at multi-colony hex.

        Args:
            planets: List of Planet objects to choose from.
            on_selected: Callback receiving the selected Planet.
        """
        rect = pygame.Rect(200, 100, 950, 650)
        self.planet_selection_window = PlanetSelectionWindow(
            rect,
            self.manager,
            planets,
            on_selected,
            window_title="Select Target Planet",
            list_label="Colonies in sector:",
            show_any_button=False
        )
        log_info(f"BuildQueue: Opened planet selection for {len(planets)} colonies")

    def _close(self):
        """Close the build queue screen."""
        # PROJ-79: Kill planet selection window if open
        if self.planet_selection_window:
            self.planet_selection_window.kill()
            self.planet_selection_window = None

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
                    self.controller.add_to_queue(self.drag_handler.selected_design)

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

            # PROJ-69/PROJ-86: Queue selector button clicks (delegated to selector)
            elif self._queue_selector and self._queue_selector.handle_button_click(
                event.ui_element, bool(pygame.key.get_mods() & pygame.KMOD_CTRL)
            ):
                pass  # Handled by selector
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
                # PROJ-81 Phase 4: Update design report on queue item click
                if result < len(active_queue):
                    design_id = active_queue[result].get('design_id')
                    if design_id:
                        self.controller.refresh_design_report(design_id)

        # Handle keyboard events via InputMapper, then screenshots
        if event.type == pygame.KEYDOWN:
            if self._handle_keydown(event):
                return
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
