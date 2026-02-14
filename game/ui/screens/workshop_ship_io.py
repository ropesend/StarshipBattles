"""Ship I/O handler for Design Workshop.

Handles save/load/target workflows extracted from workshop_screen.py.
PROJ-61 Phase 1.

DUP-UI2-001: Tkinter initialization now uses shared tkinter_utils module.
"""
import os

from game.core.logger import log_debug, log_error, log_info, log_warning
from game.core.profiling import profile_action
from game.strategy.systems.design_library import DesignLibrary
from game.ui.screens.design_selector_window import DesignSelectorWindow
from game.ui.screens.workshop_context import WorkshopMode
from game.ui.services.tkinter_utils import prompt_string
from game.ui.utils import create_centered_rect


class WorkshopShipIO:
    """Handles save/load/target workflows for the Design Workshop.

    This class encapsulates all ship I/O operations including:
    - Saving designs (standalone file-based or integrated design library)
    - Loading designs (standalone file-based or integrated design library)
    - Selecting target ships for weapons comparison
    - Prompting for design names via tkinter dialogs

    Args:
        context: WorkshopContext defining launch mode and configuration
        ui_manager: pygame_gui UIManager for creating windows
        screen_width: Screen width in pixels
        screen_height: Screen height in pixels
        ship_io_adapter: Adapter for standalone file-based ship I/O
        design_loader_adapter: Adapter for loading ships from design data
        viewmodel: WorkshopViewModel for accessing ship state
        weapons_report_panel_ref: Callable returning WeaponsReportPanel for target setting
        show_error_callback: Callback to display error messages
        apply_loaded_ship_callback: Callback to apply a loaded ship to the workshop
    """

    def __init__(
        self,
        context,
        ui_manager,
        screen_width: int,
        screen_height: int,
        ship_io_adapter,
        design_loader_adapter,
        viewmodel,
        weapons_report_panel_ref,
        show_error_callback,
        apply_loaded_ship_callback
    ):
        self.context = context
        self.ui_manager = ui_manager
        self.width = screen_width
        self.height = screen_height
        self._ship_io_adapter = ship_io_adapter
        self._design_loader_adapter = design_loader_adapter
        self.viewmodel = viewmodel
        self._get_weapons_report_panel = weapons_report_panel_ref
        self._show_error = show_error_callback
        self._apply_loaded_ship = apply_loaded_ship_callback

    @profile_action("Builder: Save Ship")
    def save_ship(self):
        """Save ship design (context-aware)."""
        if self.context.mode == WorkshopMode.STANDALONE:
            # Use adapter for file-based I/O
            success, message = self._ship_io_adapter.save_ship(self.viewmodel.ship)
            if success:
                log_info(message)
            elif message:
                self._show_error(message)
        else:
            # Use integrated design library
            log_info("Workshop: Initiating SAVE operation")
            log_debug(f"  context.savegame_path: {self.context.savegame_path}")
            log_debug(f"  context.empire_id: {self.context.empire_id}")
            log_debug(f"  context.mode: {self.context.mode}")

            library = DesignLibrary(
                self.context.savegame_path,
                self.context.empire_id
            )

            log_debug(f"  library.designs_folder: {library.designs_folder}")

            # Show save dialog to get design name
            design_name = self._prompt_design_name(self.viewmodel.ship.name)
            if not design_name:
                log_info("Workshop Save: User cancelled design name prompt")
                return  # Cancelled

            log_info(f"Workshop Save: Saving design as '{design_name}'")

            # Get built designs from context (will be set by strategy layer)
            built_designs = getattr(self.context, 'built_designs', set())
            log_debug(f"  built_designs count: {len(built_designs)}")

            success, message = library.save_design(
                self.viewmodel.ship,
                design_name,
                built_designs
            )

            if message:
                if success:
                    log_info(f"Workshop Save: SUCCESS - {message}")
                else:
                    log_error(f"Workshop Save: FAILED - {message}")
                    self._show_error(message)

    @profile_action("Builder: Load Ship")
    def load_ship(self):
        """Load ship design (context-aware)."""
        if self.context.mode == WorkshopMode.STANDALONE:
            # Use adapter for file-based I/O
            new_ship, message = self._ship_io_adapter.load_ship(self.width, self.height)
            if new_ship:
                self._apply_loaded_ship(new_ship, message)
            elif message:
                self._show_error(message)
        else:
            # Show design selector window
            log_info("Workshop: Opening design selector for LOAD operation")
            log_debug(f"  context.savegame_path: {self.context.savegame_path}")
            log_debug(f"  context.empire_id: {self.context.empire_id}")
            log_debug(f"  context.mode: {self.context.mode}")

            library = DesignLibrary(
                self.context.savegame_path,
                self.context.empire_id
            )

            log_debug(f"  library.designs_folder: {library.designs_folder}")

            # Immediate scan to diagnose
            try:
                designs = library.scan_designs()
                log_info(f"Workshop Load: DesignLibrary scanned {len(designs)} designs")
                if designs:
                    for d in designs[:5]:  # Log first 5 designs
                        log_debug(f"    - {d.name} (design_id={d.design_id})")
                else:
                    log_warning("Workshop Load: scan_designs() returned an empty list!")
                    log_warning(f"  Checked folder: {library.designs_folder}")
                    if os.path.exists(library.designs_folder):
                        files = os.listdir(library.designs_folder)
                        log_warning(f"  Folder exists with {len(files)} files: {files}")
                    else:
                        log_error(f"  Folder does not exist!")
            except (OSError, ValueError, KeyError) as e:
                log_error(f"Workshop Load: Exception during scan_designs(): {e}")
                import traceback
                log_error(traceback.format_exc())

            def on_design_selected(design_id: str):
                log_info(f"Workshop: User selected design_id='{design_id}'")
                design_data = library.load_design_data(design_id)
                if design_data:
                    # Use adapter to create ship from design data
                    ship = self._design_loader_adapter.load_ship_from_design_data(
                        design_data, self.width // 2, self.height // 2
                    )
                    if ship:
                        log_info(f"Workshop: Successfully loaded design '{ship.name}'")
                        self._apply_loaded_ship(ship, f"Loaded design: {ship.name}")
                    else:
                        log_error(f"Workshop: Failed to create ship from design '{design_id}'")
                        self._show_error("Failed to create ship from design data")
                else:
                    log_error(f"Workshop: Failed to load design '{design_id}'")
                    self._show_error(f"Design not found: {design_id}")

            # Open design selector window
            window_rect = create_centered_rect(1200, 800, self.width, self.height)
            _selector = DesignSelectorWindow(
                rect=window_rect,
                manager=self.ui_manager,
                design_library=library,
                mode="load",
                on_select_callback=on_design_selected
            )

    def select_target(self):
        """Select target ship for weapons comparison (context-aware)."""
        if self.context.mode == WorkshopMode.STANDALONE:
            # Use adapter for file-based I/O
            target_ship, message = self._ship_io_adapter.load_ship(self.width, self.height)
            if target_ship:
                self._get_weapons_report_panel().set_target(target_ship)
                log_info(f"Selected target: {target_ship.name}")
            elif message and "Cancelled" not in message:
                self._show_error(message)
        else:
            # Use design selector with ALL designs (player + AI)
            library = DesignLibrary(
                self.context.savegame_path,
                self.context.empire_id
            )

            def on_target_selected(design_id: str):
                design_data = library.load_design_data(design_id)
                if design_data:
                    # Use adapter to create ship from design data
                    ship = self._design_loader_adapter.load_ship_from_design_data(
                        design_data, self.width // 2, self.height // 2
                    )
                    if ship:
                        self._weapons_report_panel_ref.set_target(ship)
                        log_info(f"Selected target: {ship.name}")
                    else:
                        self._show_error("Failed to create ship from design data")
                else:
                    self._show_error(f"Design not found: {design_id}")

            # Open design selector window
            window_rect = create_centered_rect(1200, 800, self.width, self.height)
            _selector = DesignSelectorWindow(
                rect=window_rect,
                manager=self.ui_manager,
                design_library=library,
                mode="target",
                on_select_callback=on_target_selected
            )

    def _prompt_design_name(self, default_name: str) -> str:
        """Prompt user for design name.

        Args:
            default_name: Default name to suggest

        Returns:
            Design name or empty string if cancelled
        """
        result = prompt_string(
            "Save Design",
            "Enter design name:",
            initialvalue=default_name
        )
        return result if result else ""
