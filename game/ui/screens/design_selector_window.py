"""
Design Selector Window - UI for browsing and selecting ship designs

This module provides the DesignSelectorWindow class for browsing the design
library in integrated mode. It supports filtering by class, type, and obsolete
status, as well as text search.
"""
import pygame
import pygame_gui
from pygame_gui.elements import (
    UIWindow, UIPanel, UILabel, UIButton, UIScrollingContainer,
    UITextEntryLine, UIDropDownMenu
)
from typing import Optional, Callable, List
from game.strategy.systems.design_library import DesignLibrary
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
            text="<b>Filters</b>",
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

        type_options = ["All Types", "Ship", "Fighter", "Satellite", "Planetary Complex"]
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
        class_filter = None
        if self.class_dropdown.selected_option != "All Classes":
            class_filter = self.class_dropdown.selected_option

        type_filter = None
        if self.type_dropdown.selected_option != "All Types":
            type_filter = self.type_dropdown.selected_option

        # Search designs
        self.filtered_designs = self.design_library.search_designs(
            name_query=self.filter_name,
            filters={
                'ship_class': class_filter,
                'vehicle_type': type_filter,
                'show_obsolete': self.show_obsolete
            }
        )

        # Sort by name
        self.filtered_designs.sort(key=lambda d: d.name)

        # Rebuild UI
        self._rebuild_design_list()

    def _rebuild_design_list(self):
        """Rebuild the design list UI"""
        # Clear existing rows
        if hasattr(self, 'design_rows'):
            for row in self.design_rows:
                row.kill()

        self.design_rows = []

        # Create rows for each design
        y_offset = 10
        row_width = self.list_container.get_container().get_rect().width - 20

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

        # Icon placeholder (future: actual ship sprite)
        UILabel(
            relative_rect=pygame.Rect(5, 5, 50, 50),
            text="🚀",  # Emoji placeholder
            manager=self.ui_manager,
            container=row
        )

        # Design name
        name_text = design.name
        if design.is_obsolete:
            name_text += " [OBSOLETE]"

        UILabel(
            relative_rect=pygame.Rect(65, 5, 200, 25),
            text=f"<b>{name_text}</b>",
            manager=self.ui_manager,
            container=row
        )

        # Ship class
        UILabel(
            relative_rect=pygame.Rect(65, 30, 150, 20),
            text=f"Class: {design.ship_class}",
            manager=self.ui_manager,
            container=row
        )

        # Vehicle type
        UILabel(
            relative_rect=pygame.Rect(220, 30, 150, 20),
            text=f"Type: {design.vehicle_type}",
            manager=self.ui_manager,
            container=row
        )

        # Mass
        UILabel(
            relative_rect=pygame.Rect(380, 30, 100, 20),
            text=f"Mass: {design.mass:.0f}",
            manager=self.ui_manager,
            container=row
        )

        # Select button
        select_btn = UIButton(
            relative_rect=pygame.Rect(width - 90, 15, 80, 30),
            text="Select",
            manager=self.ui_manager,
            container=row,
            object_id=f"#select_{design.design_id}"
        )

        # Store design_id on button for event handling
        select_btn.design_id = design.design_id

        return row

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

            # Check if it's a design row select button
            elif hasattr(event.ui_element, 'design_id'):
                self._on_design_selected(event.ui_element.design_id)
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

    def _on_design_selected(self, design_id: str):
        """
        Handle design row selection.

        Args:
            design_id: ID of selected design
        """
        self.selected_design_id = design_id
        self.select_button.enable()

    def _on_select(self):
        """Handle main Select button click"""
        if self.selected_design_id and self.on_select_callback:
            self.on_select_callback(self.selected_design_id)
            self.kill()

    def update(self, time_delta: float):
        """
        Update window.

        Args:
            time_delta: Time since last update in seconds
        """
        super().update(time_delta)
