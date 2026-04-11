"""
Design Selector Window - UI for browsing and selecting ship designs

This module provides the DesignSelectorWindow class for browsing the design
library in integrated mode. It supports filtering by class, type, and obsolete
status, as well as text search.

Cross-layer imports (acceptable for UI):
- DesignLibrary: Runtime - required for browsing and selecting designs
- DesignMetadata: TYPE_CHECKING only - used for type hints
"""
from __future__ import annotations

import pygame
import pygame_gui
from pygame_gui.elements import (
    UIWindow, UIPanel, UILabel, UIButton, UIScrollingContainer,
    UITextEntryLine, UIDropDownMenu, UIImage
)
from typing import Optional, Callable, List, Dict, Set, TYPE_CHECKING
from game.strategy.systems.design_library import DesignLibrary
import logging
from game.ui.screens.design_image_helper import load_portrait_thumbnail, load_topdown_thumbnail

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.data.design_metadata import DesignMetadata


class DesignSelectorWindow(UIWindow):
    """Window for selecting ship designs from the design library"""

    def __init__(self,
                 rect: pygame.Rect,
                 manager: pygame_gui.UIManager,
                 design_library: DesignLibrary,
                 mode: str = "load",
                 on_select_callback: Optional[Callable[[str], None]] = None):
        """
        Initialize design selector window.

        Args:
            rect: Window rectangle
            manager: UIManager instance
            design_library: DesignLibrary to browse
            mode: "load" (for loading designs) or "target" (for selecting targets)
            on_select_callback: Callback function when design is selected
        """
        title = "Load Design" if mode == "load" else "Select Target"
        super().__init__(rect, manager, window_display_title=title, resizable=True)

        self.design_library = design_library
        self.mode = mode
        self.on_select_callback = on_select_callback

        # State
        self.all_designs = []
        self.filtered_designs = []
        self.selected_design_id = None

        # Filter state
        self.filter_name = ""
        self.filter_ship_class = None
        self.filter_vehicle_type = None
        self.show_obsolete = False

        # Layout constants
        self.sidebar_width = 250
        self.row_height = 60

        # Design row UI elements (populated by _rebuild_design_list)
        self.design_rows = []

        # Button-to-data mappings (replaces monkey-patching on UIButton objects)
        self._button_design_map: Dict[UIButton, str] = {}
        self._obsolete_buttons: Set[UIButton] = set()
        self._obsolete_state_map: Dict[UIButton, bool] = {}

        # Create UI
        self._create_sidebar()
        self._create_main_list()
        self._create_bottom_buttons()

        # Initial load
        self._refresh_designs()

    def _create_sidebar(self):
        """Create the left sidebar with filters"""
        content_rect = self.get_container().get_rect()

        # Sidebar panel
        self.sidebar_panel = UIPanel(
            relative_rect=pygame.Rect(0, 0, self.sidebar_width, content_rect.height - 60),
            manager=self.ui_manager,
            container=self,
            anchors={'left': 'left', 'top': 'top', 'bottom': 'bottom'}
        )

        y_offset = 10

        # Title
        UILabel(
            relative_rect=pygame.Rect(10, y_offset, self.sidebar_width - 20, 30),
            text="Filters",
            manager=self.ui_manager,
            container=self.sidebar_panel
        )
        y_offset += 40

        # Name search
        UILabel(
            relative_rect=pygame.Rect(10, y_offset, self.sidebar_width - 20, 25),
            text="Search Name:",
            manager=self.ui_manager,
            container=self.sidebar_panel
        )
        y_offset += 30

        self.name_search_entry = UITextEntryLine(
            relative_rect=pygame.Rect(10, y_offset, self.sidebar_width - 20, 30),
            manager=self.ui_manager,
            container=self.sidebar_panel
        )
        y_offset += 40

        # Ship class filter
        UILabel(
            relative_rect=pygame.Rect(10, y_offset, self.sidebar_width - 20, 25),
            text="Ship Class:",
            manager=self.ui_manager,
            container=self.sidebar_panel
        )
        y_offset += 30

        class_options = ["All Classes", "Escort", "Frigate", "Destroyer", "Cruiser",
                        "Battlecruiser", "Battleship", "Carrier", "Dreadnought"]
        self.class_dropdown = UIDropDownMenu(
            options_list=class_options,
            starting_option="All Classes",
            relative_rect=pygame.Rect(10, y_offset, self.sidebar_width - 20, 30),
            manager=self.ui_manager,
            container=self.sidebar_panel
        )
        y_offset += 40

        # Vehicle type filter
        UILabel(
            relative_rect=pygame.Rect(10, y_offset, self.sidebar_width - 20, 25),
            text="Vehicle Type:",
            manager=self.ui_manager,
            container=self.sidebar_panel
        )
        y_offset += 30

        type_options = ["All Types", "Ship", "Fighter", "Satellite", "Planetary Complex", "Drop Pod"]
        self.type_dropdown = UIDropDownMenu(
            options_list=type_options,
            starting_option="All Types",
            relative_rect=pygame.Rect(10, y_offset, self.sidebar_width - 20, 30),
            manager=self.ui_manager,
            container=self.sidebar_panel
        )
        y_offset += 40

        # Show obsolete checkbox (as button for now)
        self.obsolete_button = UIButton(
            relative_rect=pygame.Rect(10, y_offset, self.sidebar_width - 20, 35),
            text="☐ Show Obsolete",
            manager=self.ui_manager,
            container=self.sidebar_panel,
            object_id="#obsolete_toggle"
        )
        y_offset += 45

        # Apply filters button
        self.apply_filters_button = UIButton(
            relative_rect=pygame.Rect(10, y_offset, self.sidebar_width - 20, 40),
            text="Apply Filters",
            manager=self.ui_manager,
            container=self.sidebar_panel
        )

    def _create_main_list(self):
        """Create the main scrolling list of designs"""
        content_rect = self.get_container().get_rect()

        # Main panel
        main_width = content_rect.width - self.sidebar_width - 10
        self.main_panel = UIPanel(
            relative_rect=pygame.Rect(self.sidebar_width, 0, main_width, content_rect.height - 60),
            manager=self.ui_manager,
            container=self,
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
        )

        # Scrolling container for design list
        self.list_container = UIScrollingContainer(
            relative_rect=pygame.Rect(5, 5, main_width - 10, content_rect.height - 70),
            manager=self.ui_manager,
            container=self.main_panel,
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
        )

        # Design rows will be created dynamically

    def _create_bottom_buttons(self):
        """Create bottom action buttons"""
        content_rect = self.get_container().get_rect()

        # Bottom button panel
        self.button_panel = UIPanel(
            relative_rect=pygame.Rect(0, content_rect.height - 60, content_rect.width, 60),
            manager=self.ui_manager,
            container=self,
            anchors={'left': 'left', 'right': 'right', 'bottom': 'bottom'}
        )

        button_width = 120
        button_y = 10

        # Select button
        self.select_button = UIButton(
            relative_rect=pygame.Rect(content_rect.width - button_width - 150, button_y, button_width, 40),
            text="Select",
            manager=self.ui_manager,
            container=self.button_panel,
            anchors={'right': 'right'}
        )
        self.select_button.disable()  # Disabled until a design is selected

        # Cancel button
        self.cancel_button = UIButton(
            relative_rect=pygame.Rect(content_rect.width - button_width - 20, button_y, button_width, 40),
            text="Cancel",
            manager=self.ui_manager,
            container=self.button_panel,
            anchors={'right': 'right'}
        )

    def _refresh_designs(self):
        """Refresh the design list based on current filters"""
        # Get filter values
        # Note: pygame_gui dropdowns return tuples (current_value, previous_value)
        # We need to extract just the current value (first element)
        class_option = self.class_dropdown.selected_option
        if isinstance(class_option, tuple):
            class_option = class_option[0]  # Extract current value from tuple

        class_filter = None
        if class_option != "All Classes":
            class_filter = class_option

        type_option = self.type_dropdown.selected_option
        if isinstance(type_option, tuple):
            type_option = type_option[0]  # Extract current value from tuple

        type_filter = None
        if type_option != "All Types":
            type_filter = type_option

        logger.info(f"DesignSelector: Refreshing design list (mode={self.mode})")
        logger.debug(f"  design_library.designs_folder: {self.design_library.designs_folder}")
        logger.debug(f"  filter_name: '{self.filter_name}'")
        logger.debug(f"  class_filter: {class_filter}")
        logger.debug(f"  type_filter: {type_filter}")
        logger.debug(f"  show_obsolete: {self.show_obsolete}")

        # Search designs
        self.filtered_designs = self.design_library.search_designs(
            name_query=self.filter_name,
            filters={
                'ship_class': class_filter,
                'vehicle_type': type_filter,
                'show_obsolete': self.show_obsolete
            }
        )

        logger.info(f"DesignSelector: Found {len(self.filtered_designs)} designs after filtering")
        if self.filtered_designs:
            for d in self.filtered_designs[:5]:  # Log first 5
                logger.debug(f"    - {d.name} (class={d.ship_class}, type={d.vehicle_type})")

        # Sort by name
        self.filtered_designs.sort(key=lambda d: d.name)

        # Rebuild UI
        self._rebuild_design_list()

    def _rebuild_design_list(self):
        """Rebuild the design list UI"""
        # Clear existing rows
        for row in self.design_rows:
            row.kill()
        self.design_rows = []

        # Clear button-to-data mappings
        self._button_design_map.clear()
        self._obsolete_buttons.clear()
        self._obsolete_state_map.clear()

        # Create rows for each design
        y_offset = 10
        # Use list container width minus scrollbar width (20px) and margins
        # This ensures rows don't get clipped by the scrollbar
        row_width = self.list_container.get_container().get_rect().width - 25

        for design in self.filtered_designs:
            row = self._create_design_row(design, y_offset, row_width)
            self.design_rows.append(row)
            y_offset += self.row_height + 5

        # Update container size
        self.list_container.set_scrollable_area_dimensions((row_width, max(y_offset, self.list_container.get_container().get_rect().height)))

    def _create_design_row(self, design: DesignMetadata, y_offset: int, width: int) -> UIPanel:
        """
        Create a single design row.

        Args:
            design: Design metadata
            y_offset: Y position in container
            width: Row width

        Returns:
            UIPanel for the row
        """
        # Row panel
        row = UIPanel(
            relative_rect=pygame.Rect(10, y_offset, width, self.row_height),
            manager=self.ui_manager,
            container=self.list_container,
            object_id=f"#design_row_{design.design_id}"
        )

        # Obsolete indicator (visual marker on left side)
        current_x = 5
        if design.is_obsolete:
            UILabel(
                relative_rect=pygame.Rect(current_x, 5, 40, 50),
                text="[OBS]",
                manager=self.ui_manager,
                container=row,
                object_id="#obsolete_indicator"
            )
            current_x += 45

        # Portrait thumbnail
        portrait_surface = self._load_portrait_thumbnail(design, 50)
        UIImage(
            relative_rect=pygame.Rect(current_x, 5, 50, 50),
            image_surface=portrait_surface,
            manager=self.ui_manager,
            container=row
        )
        current_x += 55

        # Top-down thumbnail (sized to match portrait height)
        topdown_surface = self._load_topdown_thumbnail(design, 50)
        if topdown_surface:
            topdown_width = topdown_surface.get_width()
            UIImage(
                relative_rect=pygame.Rect(current_x, 5, topdown_width, 50),
                image_surface=topdown_surface,
                manager=self.ui_manager,
                container=row
            )
            current_x += topdown_width + 5

        # Design name
        name_x = current_x
        name_text = design.name

        UILabel(
            relative_rect=pygame.Rect(name_x, 5, 350, 30),
            text=name_text,
            manager=self.ui_manager,
            container=row
        )

        # Ship class
        UILabel(
            relative_rect=pygame.Rect(name_x, 35, 250, 20),
            text=f"Class: {design.ship_class}",
            manager=self.ui_manager,
            container=row
        )

        # Vehicle type
        UILabel(
            relative_rect=pygame.Rect(name_x + 255, 35, 180, 20),
            text=f"Type: {design.vehicle_type}",
            manager=self.ui_manager,
            container=row
        )

        # Mass
        UILabel(
            relative_rect=pygame.Rect(name_x + 440, 35, 100, 20),
            text=f"Mass: {design.mass:.0f}",
            manager=self.ui_manager,
            container=row
        )

        # Mark Obsolete button (to the left of Select button)
        obsolete_text = "Restore" if design.is_obsolete else "Obsolete"
        obsolete_btn = UIButton(
            relative_rect=pygame.Rect(width - 180, 15, 80, 30),
            text=obsolete_text,
            manager=self.ui_manager,
            container=row,
            object_id=f"#obsolete_{design.design_id}"
        )
        self._button_design_map[obsolete_btn] = design.design_id
        self._obsolete_buttons.add(obsolete_btn)
        self._obsolete_state_map[obsolete_btn] = design.is_obsolete

        # Select button
        select_btn = UIButton(
            relative_rect=pygame.Rect(width - 90, 15, 80, 30),
            text="Select",
            manager=self.ui_manager,
            container=row,
            object_id=f"#select_{design.design_id}"
        )

        # Store design_id in map for event handling
        self._button_design_map[select_btn] = design.design_id

        return row

    def _load_portrait_thumbnail(self, design: DesignMetadata, size: int = 50) -> pygame.Surface:
        """Load a portrait thumbnail for the design. Delegates to design_image_helper."""
        return load_portrait_thumbnail(design, size)

    def _load_topdown_thumbnail(self, design: DesignMetadata, target_height: int = 50) -> Optional[pygame.Surface]:
        """Load a top-down thumbnail for the design. Delegates to design_image_helper."""
        return load_topdown_thumbnail(design, target_height)

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Process pygame events.

        Args:
            event: Event to process

        Returns:
            True if event was handled
        """
        handled = super().process_event(event)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.apply_filters_button:
                self._on_apply_filters()
                return True

            elif event.ui_element == self.obsolete_button:
                self._toggle_obsolete()
                return True

            elif event.ui_element == self.select_button:
                self._on_select()
                return True

            elif event.ui_element == self.cancel_button:
                self.kill()
                return True

            # Check if it's an obsolete toggle button
            elif event.ui_element in self._obsolete_buttons:
                design_id = self._button_design_map[event.ui_element]
                current_state = self._obsolete_state_map[event.ui_element]
                self._on_toggle_obsolete(design_id, current_state)
                return True

            # Check if it's a design row select button
            elif event.ui_element in self._button_design_map:
                self._on_design_selected(self._button_design_map[event.ui_element])
                return True

        elif event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            if event.ui_element == self.name_search_entry:
                self.filter_name = event.text
                self._refresh_designs()
                return True

        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element in (self.class_dropdown, self.type_dropdown):
                self._refresh_designs()
                return True

        return handled

    def _on_apply_filters(self):
        """Handle apply filters button click"""
        self.filter_name = self.name_search_entry.get_text()
        self._refresh_designs()

    def _toggle_obsolete(self):
        """Toggle show obsolete filter"""
        self.show_obsolete = not self.show_obsolete

        # Update button text
        checkbox = "☑" if self.show_obsolete else "☐"
        self.obsolete_button.set_text(f"{checkbox} Show Obsolete")

        self._refresh_designs()

    def _on_toggle_obsolete(self, design_id: str, current_state: bool):
        """
        Handle obsolete toggle button click.

        Args:
            design_id: ID of design to toggle
            current_state: Current obsolete state (True = obsolete)
        """
        new_state = not current_state
        logger.info(f"DesignSelector: Toggling obsolete for {design_id}: {current_state} -> {new_state}")

        # Call design library to mark obsolete
        success, message = self.design_library.mark_obsolete(design_id, new_state)
        logger.info(f"DesignSelector: mark_obsolete result: {success}, {message}")

        if success:
            # Refresh the list to show updated state
            self._refresh_designs()

    def _on_design_selected(self, design_id: str):
        """
        Handle design row selection.

        Args:
            design_id: ID of selected design
        """
        logger.info(f"DesignSelector: Design selected: {design_id}")
        self.selected_design_id = design_id
        self.select_button.enable()
        logger.info(f"DesignSelector: Main Select button enabled")

        # Immediately trigger selection (double-click behavior)
        # This makes it more user-friendly - clicking a row's Select button
        # directly loads the design instead of requiring a second click
        self._on_select()

    def _on_select(self):
        """Handle main Select button click"""
        logger.info(f"DesignSelector: Main Select button clicked")
        if self.selected_design_id and self.on_select_callback:
            logger.info(f"DesignSelector: Calling callback with design_id={self.selected_design_id}")
            self.on_select_callback(self.selected_design_id)
            self.kill()
        else:
            logger.warning(f"DesignSelector: Cannot select - selected_design_id={self.selected_design_id}, callback={self.on_select_callback is not None}")

    def update(self, time_delta: float):
        """
        Update window.

        Args:
            time_delta: Time since last update in seconds
        """
        super().update(time_delta)
