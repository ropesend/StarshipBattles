"""Ship I/O handler for Design Workshop.

Handles save/load/target workflows extracted from workshop_screen.py.
PROJ-61 Phase 1.

DUP-UI2-001: Tkinter initialization now uses shared tkinter_utils module.
"""
from __future__ import annotations

import logging

from game.core.profiling import profile_action

logger = logging.getLogger(__name__)
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

    def _design_catalog(self):
        """Resolve the per-empire ``DesignCatalog`` via ``facade_state``.

        PROJ-434 Phase 2: replaces the previous
        ``DesignLibrary(context.savegame_path, context.empire_id,
        facade_state=context.facade_state)`` construction. The catalog
        is bootstrapped per-empire and owns the in-memory list view +
        the QA-Obs-3 cache contract; writes flow through
        ``catalog.save_design`` which delegates to the bound
        ``DesignRepository`` then refreshes the in-memory entry so the
        Build Queue sees the new design on the next read without a
        turn advance. Falls back to ``None`` if the session is not
        wired (legacy / partial-init paths).

        PROJ-475 Phase 4: resolves through the public
        ``FacadeSessionState.get_design_catalog_for_empire`` accessor
        instead of reaching the now-private ``facade_state.session.services``
        chain directly — the live session is no longer publicly reachable.
        """
        facade_state = self.context.facade_state
        if facade_state is None:
            return None
        return facade_state.get_design_catalog_for_empire(self.context.empire_id)

    @profile_action("Builder: Save Ship")
    def save_ship(self) -> None:
        """Save ship design (context-aware)."""
        if self.context.mode == WorkshopMode.STANDALONE:
            # Use adapter for file-based I/O
            success, message = self._ship_io_adapter.save_ship(self.viewmodel.ship)
            if success:
                logger.info(message)
            elif message:
                self._show_error(message)
        else:
            # Use integrated design library
            logger.info("Workshop: Initiating SAVE operation")
            logger.debug(f"  context.savegame_path: {self.context.savegame_path}")
            logger.debug(f"  context.empire_id: {self.context.empire_id}")
            logger.debug(f"  context.mode: {self.context.mode}")

            # PROJ-434 Phase 2: route through DesignCatalog.save_design,
            # which orchestrates DesignRepository.save_design + the
            # QA-Obs-3 cache invalidation (workshop save -> next Build
            # Queue read sees the new design, same turn).
            catalog = self._design_catalog()
            if catalog is None:
                logger.error("Workshop Save: no DesignCatalog for empire "
                             f"{self.context.empire_id}")
                self._show_error(
                    "Internal error: design catalog not initialized"
                )
                return

            # Show save dialog to get design name
            design_name = self._prompt_design_name(self.viewmodel.ship.name)
            if not design_name:
                logger.info("Workshop Save: User cancelled design name prompt")
                return  # Cancelled

            logger.info(f"Workshop Save: Saving design as '{design_name}'")

            # Get built designs from context (always present, default_factory=set)
            built_designs = self.context.built_designs
            logger.debug(f"  built_designs count: {len(built_designs)}")

            success, message = catalog.save_design(
                self.viewmodel.ship,
                design_name,
                built_designs,
            )

            if message:
                if success:
                    logger.info(f"Workshop Save: SUCCESS - {message}")
                else:
                    logger.error(f"Workshop Save: FAILED - {message}")
                    self._show_error(message)

    @profile_action("Builder: Load Ship")
    def load_ship(self) -> None:
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
            logger.info("Workshop: Opening design selector for LOAD operation")
            logger.debug(f"  context.savegame_path: {self.context.savegame_path}")
            logger.debug(f"  context.empire_id: {self.context.empire_id}")
            logger.debug(f"  context.mode: {self.context.mode}")

            # PROJ-434 Phase 2: read through DesignCatalog (shared with
            # Build Queue so cache stays coherent intra-turn).
            catalog = self._design_catalog()
            if catalog is None:
                logger.error("Workshop Load: no DesignCatalog for empire "
                             f"{self.context.empire_id}")
                self._show_error(
                    "Internal error: design catalog not initialized"
                )
                return

            try:
                designs = catalog.scan_designs()
                logger.info(
                    f"Workshop Load: DesignCatalog scanned {len(designs)} designs"
                )
                if designs:
                    for d in designs[:5]:  # Log first 5 designs
                        logger.debug(f"    - {d.name} (design_id={d.design_id})")
                else:
                    logger.warning(
                        "Workshop Load: scan_designs() returned an empty list!"
                    )
            except (OSError, ValueError, KeyError) as e:
                logger.exception(f"Workshop Load: Exception during scan_designs(): {e}")

            def on_design_selected(design_id: str) -> None:
                logger.info(f"Workshop: User selected design_id='{design_id}'")
                load_result = catalog.load_design_data(design_id)
                if load_result.success:
                    # Use adapter to create ship from design data
                    ship = self._design_loader_adapter.load_ship_from_design_data(
                        load_result.data, self.width // 2, self.height // 2
                    )
                    if ship:
                        logger.info(f"Workshop: Successfully loaded design '{ship.name}'")
                        self._apply_loaded_ship(ship, f"Loaded design: {ship.name}")
                    else:
                        logger.error(f"Workshop: Failed to create ship from design '{design_id}'")
                        self._show_error("Failed to create ship from design data")
                else:
                    logger.error(f"Workshop: Failed to load design '{design_id}': {load_result.error}")
                    self._show_error(f"Design not found: {design_id}")

            # Open design selector window
            window_rect = create_centered_rect(1200, 800, self.width, self.height)
            _selector = DesignSelectorWindow(
                rect=window_rect,
                manager=self.ui_manager,
                design_catalog=catalog,
                mode="load",
                on_select_callback=on_design_selected
            )

    def select_target(self) -> None:
        """Select target ship for weapons comparison (context-aware)."""
        if self.context.mode == WorkshopMode.STANDALONE:
            # Use adapter for file-based I/O
            target_ship, message = self._ship_io_adapter.load_ship(self.width, self.height)
            if target_ship:
                self._get_weapons_report_panel().set_target(target_ship)
                logger.info(f"Selected target: {target_ship.name}")
            elif message and "Cancelled" not in message:
                self._show_error(message)
        else:
            # PROJ-434 Phase 2: read through DesignCatalog (shared with
            # Build Queue so cache stays coherent intra-turn).
            catalog = self._design_catalog()
            if catalog is None:
                logger.error("Workshop Target: no DesignCatalog for empire "
                             f"{self.context.empire_id}")
                self._show_error(
                    "Internal error: design catalog not initialized"
                )
                return

            def on_target_selected(design_id: str) -> None:
                load_result = catalog.load_design_data(design_id)
                if load_result.success:
                    # Use adapter to create ship from design data
                    ship = self._design_loader_adapter.load_ship_from_design_data(
                        load_result.data, self.width // 2, self.height // 2
                    )
                    if ship:
                        self._get_weapons_report_panel().set_target(ship)
                        logger.info(f"Selected target: {ship.name}")
                    else:
                        self._show_error("Failed to create ship from design data")
                else:
                    self._show_error(f"Design not found: {design_id}")

            # Open design selector window
            window_rect = create_centered_rect(1200, 800, self.width, self.height)
            _selector = DesignSelectorWindow(
                rect=window_rect,
                manager=self.ui_manager,
                design_catalog=catalog,
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
