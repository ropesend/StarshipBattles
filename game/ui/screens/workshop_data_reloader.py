"""PROJ-61: Workshop Data Reloader - Handles data reload orchestration.

This module extracts data reload logic from DesignWorkshopScreen to reduce
its line count and improve separation of concerns.
"""
import logging
import os
from tkinter import filedialog

from game.core.profiling import profile_block
from game.ui.screens.workshop_data_loader import WorkshopDataLoader

logger = logging.getLogger(__name__)
from game.ui.screens.builder_utils import BuilderEvents


# Try to get tk_root for file dialogs
try:
    import tkinter as tk
    tk_root = tk.Tk()
    tk_root.withdraw()
except Exception:  # Intentional broad catch: Tkinter init is platform-dependent
    tk_root = None


class WorkshopDataReloader:
    """Handles data directory selection and reload orchestration.

    Extracted from DesignWorkshopScreen to reduce complexity and improve
    maintainability. Coordinates between data loading and UI refresh.

    Args:
        context: WorkshopContext with registries and mode info
        ship_io_adapter: Adapter for ship I/O operations
        viewmodel: WorkshopViewModel for state management
        show_error_callback: Callback to display error messages
        refresh_ui_callback: Callback to refresh UI after data reload
        get_vehicle_classes_callback: Callback to get vehicle classes from registries
        event_bus: EventBus for emitting events
        right_panel_ref: Lambda returning the right panel instance
        left_panel_ref: Lambda returning the left panel instance
        view_ref: Lambda returning the schematic view instance
        controller_ref: Lambda returning the interaction controller instance
        rebuild_modifier_ui_callback: Callback to rebuild modifier UI
        update_stats_callback: Callback to update stats display
    """

    def __init__(
        self,
        context,
        ship_io_adapter,
        viewmodel,
        show_error_callback,
        get_vehicle_classes_callback,
        event_bus,
        right_panel_ref,
        left_panel_ref,
        view_ref,
        controller_ref,
        rebuild_modifier_ui_callback,
        update_stats_callback
    ):
        self.context = context
        self._ship_io_adapter = ship_io_adapter
        self.viewmodel = viewmodel
        self.show_error = show_error_callback
        self._get_vehicle_classes = get_vehicle_classes_callback
        self.event_bus = event_bus
        self._right_panel_ref = right_panel_ref
        self._left_panel_ref = left_panel_ref
        self._view_ref = view_ref
        self._controller_ref = controller_ref
        self._rebuild_modifier_ui = rebuild_modifier_ui_callback
        self._update_stats = update_stats_callback

    @property
    def right_panel(self):
        """Get right panel via deferred reference."""
        return self._right_panel_ref()

    @property
    def left_panel(self):
        """Get left panel via deferred reference."""
        return self._left_panel_ref()

    @property
    def view(self):
        """Get schematic view via deferred reference."""
        return self._view_ref()

    @property
    def controller(self):
        """Get interaction controller via deferred reference."""
        return self._controller_ref()

    def on_select_data_pressed(self):
        """Open dialog to select a data directory and reload game data."""
        if not tk_root:
            self.show_error("Tkinter not initialized, cannot open dialog")
            return

        initial_dir = os.path.join(os.getcwd(), "data")
        directory = filedialog.askdirectory(
            initialdir=initial_dir,
            title="Select Data Directory"
        )

        if directory:
            with profile_block(f"Builder: Reload Data from {os.path.basename(directory)}"):
                self.reload_data(directory)

    def load_standard_data(self):
        """Load standard data from 'data/' directory and set ship directory to 'ships/'."""
        with profile_block("Builder: Load Standard Data"):
            directory = os.path.join(os.getcwd(), "data")
            self.reload_data(directory)
            self._ship_io_adapter.set_ships_folder("ships")
            self.show_error("Loaded Standard Data • Ships: ships/")

    def load_test_data(self):
        """Load test data from 'tests/data/' directory and set ship directory to 'tests/data/ships/'."""
        with profile_block("Builder: Load Test Data"):
            directory = os.path.join(os.getcwd(), "tests", "data")
            self.reload_data(directory)
            self._ship_io_adapter.set_ships_folder(os.path.join("tests", "data", "ships"))
            self.show_error("Loaded Test Data • Ships: tests/data/ships/")

    def reload_data(self, directory: str):
        """Reload global game data from the specified directory.

        Data loading is delegated to WorkshopDataLoader for better testability.
        UI refresh logic uses callbacks to the main screen.

        Args:
            directory: Path to the data directory to load from
        """
        try:
            # 1. Load data via dedicated loader (PROJ-50: pass registries)
            loader = WorkshopDataLoader(directory, registries=self.context.registries)
            result = loader.load_all()

            if not result.success:
                for error in result.errors:
                    logger.error(error)
                self.show_error(f"Data loading failed: {result.errors[0] if result.errors else 'Unknown error'}")
                return

            # 2. Refresh UI
            self._refresh_ui_after_data_reload(result.default_class)

            # Show success
            self.show_error(f"Reloaded data from {os.path.basename(directory)}")

        except (OSError, ValueError, KeyError) as e:
            logger.exception(f"Failed to reload data: {e}")
            self.show_error(f"Error reloading data: {e}")

    def _refresh_ui_after_data_reload(self, default_class: str):
        """Refresh all UI panels after data reload.

        Extracted from _reload_data to separate data loading from UI concerns.

        Args:
            default_class: The default ship class to use after reload
        """
        # Refresh UI panels
        self.right_panel.refresh_controls()
        self.left_panel.update_component_list()
        self._rebuild_modifier_ui()

        # Refresh Builder State (PROJ-43: Use viewmodel instead of direct get_all_components)
        self.viewmodel.refresh_available_components()

        # Reset Ship with new default class (using service layer via viewmodel)
        self.viewmodel.ship = self.viewmodel.create_default_ship(ship_class=default_class)

        # Reset UI Panels
        self.left_panel.update_component_list()

        # Center View
        self.view.selected_component = None
        self.controller.selected_component = None
        self.viewmodel.clear_selection()

        # Update dropdowns via right_panel method
        classes = self._get_vehicle_classes()
        self.right_panel.update_dropdowns_for_data_reload(default_class, classes)

        self._update_stats()
        self._rebuild_modifier_ui()

        # Emit registry reload event for decoupled UI sync
        self.event_bus.emit(BuilderEvents.REGISTRY_RELOADED, None)
