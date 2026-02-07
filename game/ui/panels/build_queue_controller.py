"""
Build Queue Controller - Business logic for queue operations.

Extracted from build_queue_screen.py (PROJ-63 Phase 3).
Manages category filtering, queue additions, and design report updates.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional

from game.core.logger import log_info, log_warning, log_error, log_debug

if TYPE_CHECKING:
    from game.strategy.data.planet import Planet
    from game.strategy.systems.design_library import DesignLibrary
    from game.simulation.services.design_loader import SimulationDesignLoader
    from game.ui.panels.design_report_panel import DesignReportPanel


class BuildQueueController:
    """
    Manages build queue business logic.

    Responsibilities:
    - Category filtering for design lists
    - Adding items to planet construction queue
    - Updating design report panel with selected design info

    This class is stateless except for selected_category tracking.
    All queue modifications happen on the injected planet object.
    """

    def __init__(
        self,
        planet: Planet,
        design_library: DesignLibrary,
        design_loader: SimulationDesignLoader,
        design_report: DesignReportPanel,
        on_queue_changed: Callable[[], None]
    ):
        """
        Initialize the controller.

        Args:
            planet: Planet object whose construction_queue is managed
            design_library: For scanning/loading designs
            design_loader: SimulationDesignLoader for creating ship objects
            design_report: DesignReportPanel for updating display
            on_queue_changed: Callback to trigger queue display refresh
        """
        self.planet = planet
        self.design_library = design_library
        self.design_loader = design_loader
        self.design_report = design_report
        self.on_queue_changed = on_queue_changed

        # Category filter state
        self.selected_category = "complex"

    def load_designs_by_category(self, category: str):
        """
        Load designs filtered by vehicle type.

        Args:
            category: One of "complex", "ship", "satellite", "fighter"

        Returns:
            List of design objects matching the category
        """
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

    def set_category(self, category: str):
        """
        Set the active category filter.

        Args:
            category: Category to filter by ("complex", "ship", "satellite", "fighter")
        """
        self.selected_category = category
        self.on_queue_changed()
        log_info(f"Build queue category changed to: {category}")

    def add_to_queue(self, design_id: str, turns: int = 1, category: str = None, index: int = None):
        """
        Add a design to the planet's construction queue.

        Args:
            design_id: ID of the design to build
            turns: Number of turns to complete (default 1)
            category: Design category (uses self.selected_category if None)
            index: Optional insertion index
        """
        cat = category if category is not None else self.selected_category

        # DIAGNOSTIC LOGGING for BUG-24 investigation
        log_info(f"add_to_queue called: design_id={design_id}, category={cat}")
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
        self.on_queue_changed()

    def refresh_design_report(self, design_id: str):
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

            # Use injected design_loader instead of creating new instance
            ship = self.design_loader.load_ship_from_design_data(
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
