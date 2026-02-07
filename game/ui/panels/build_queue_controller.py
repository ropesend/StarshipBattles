"""
Build Queue Controller - Business logic for queue operations.

Extracted from build_queue_screen.py (PROJ-63 Phase 3).
Manages category filtering, queue additions, and design report updates.

Updated in PROJ-67 Phase 4 to support BuildContext protocol (Planet or Fleet).
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional, Union

from game.core.logger import log_info, log_warning, log_error, log_debug

if TYPE_CHECKING:
    from game.strategy.data.build_context import BuildContext
    from game.strategy.data.planet import Planet
    from game.strategy.data.fleet import Fleet
    from game.strategy.systems.design_library import DesignLibrary
    from game.simulation.services.design_loader import SimulationDesignLoader
    from game.ui.panels.design_report_panel import DesignReportPanel


class BuildQueueController:
    """
    Manages build queue business logic.

    Responsibilities:
    - Category filtering for design lists
    - Adding items to build context's construction queue
    - Updating design report panel with selected design info

    This class is stateless except for selected_category tracking.
    All queue modifications happen on the injected build context object.

    Updated in PROJ-67 to support BuildContext protocol (Planet or Fleet).
    """

    def __init__(
        self,
        build_context: Union['Planet', 'Fleet', 'BuildContext'],
        design_library: 'DesignLibrary',
        design_loader: 'SimulationDesignLoader',
        design_report: 'DesignReportPanel',
        on_queue_changed: Callable[[], None]
    ):
        """
        Initialize the controller.

        Args:
            build_context: Planet or Fleet whose construction_queue is managed
            design_library: For scanning/loading designs
            design_loader: SimulationDesignLoader for creating ship objects
            design_report: DesignReportPanel for updating display
            on_queue_changed: Callback to trigger queue display refresh
        """
        self.build_context = build_context
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
        Add a design to the build context's construction queue.

        Args:
            design_id: ID of the design to build
            turns: Number of turns to complete (default 1)
            category: Design category (uses self.selected_category if None)
            index: Optional insertion index
        """
        cat = category if category is not None else self.selected_category

        # DIAGNOSTIC LOGGING
        log_info(f"add_to_queue called: design_id={design_id}, category={cat}")
        log_info(f"  build_context.type = {self.build_context.context_type}")
        log_info(f"  build_context.has_space_shipyard = {self.build_context.has_space_shipyard}")

        # Log facility details for planets only
        if self.build_context.context_type == "planet":
            log_info(f"  planet.facilities count = {len(self.build_context.facilities)}")
            for i, f in enumerate(self.build_context.facilities):
                log_info(f"    [{i}] {f.name} (operational={f.is_operational})")
                log_info(f"        design_data layers: {list(f.design_data.get('layers', {}).keys())}")
                # Show component IDs in each layer
                for layer_name, layer_data in f.design_data.get('layers', {}).items():
                    if isinstance(layer_data, list):
                        comp_ids = [c.get('id', 'unknown') for c in layer_data if isinstance(c, dict)]
                        log_info(f"        {layer_name} components: {comp_ids}")

        # Validate build capability using protocol method
        if not self.build_context.can_build_type(cat):
            log_warning(f"Cannot build {cat}: build context cannot build this type")
            return

        # Prepare queue item
        queue_item = {
            "design_id": design_id,
            "type": cat,
            "turns_remaining": turns
        }

        # Add to queue
        if index is not None:
            self.build_context.construction_queue.insert(index, queue_item)
            log_info(f"Inserted {design_id} into build queue at position {index}")
        else:
            self.build_context.construction_queue.append(queue_item)
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

        except (OSError, ValueError, KeyError) as e:
            log_error(f"Error loading design {design_id}: {e}")
            import traceback
            log_error(traceback.format_exc())
            self.design_report.show_placeholder()
