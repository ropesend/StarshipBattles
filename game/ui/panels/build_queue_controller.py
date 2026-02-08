"""
Build Queue Controller - Business logic for queue operations.

Extracted from build_queue_screen.py (PROJ-63 Phase 3).
Manages category filtering, queue additions, and design report updates.

Updated in PROJ-67 Phase 4 to support BuildContext protocol (Planet or Fleet).
Updated in PROJ-69 Phase 4 to support multi-queue operations via BuildQueueSource.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Callable, List, Optional, Union

from game.core.logger import log_info, log_warning, log_error, log_debug

if TYPE_CHECKING:
    from game.strategy.data.build_context import BuildContext
    from game.strategy.data.build_queue_source import BuildQueueSource
    from game.strategy.data.planet import Planet
    from game.strategy.data.fleet import Fleet
    from game.strategy.systems.design_library import DesignLibrary
    from game.simulation.services.design_loader import SimulationDesignLoader
    from game.ui.panels.design_report_panel import DesignReportPanel

# Category-to-build-capability mapping
_SHIP_CATEGORIES = {"ship", "satellite", "fighter"}
_COMPLEX_CATEGORIES = {"complex"}


class BuildQueueController:
    """
    Manages build queue business logic.

    Responsibilities:
    - Category filtering for design lists
    - Adding items to queue source(s) or build context's construction queue
    - Updating design report panel with selected design info

    Supports two modes:
    - **Single-queue mode:** active_queue_source is set, adds go to that queue.
    - **Multi-queue mode:** selected_queue_sources is non-empty, adds go to all
      compatible queues in the list.

    When neither is set, falls back to the injected build_context.

    Updated in PROJ-69 to support multi-queue operations via BuildQueueSource.
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
            build_context: Planet or Fleet whose construction_queue is managed (fallback)
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

        # PROJ-69: Multi-queue state
        self.active_queue_source: Optional['BuildQueueSource'] = None
        self.selected_queue_sources: List['BuildQueueSource'] = []

    def set_active_queue(self, source: 'BuildQueueSource') -> None:
        """Set the active queue source for single-queue mode.

        Clears multi-select. Subsequent add_to_queue calls will target
        this single queue source.

        Args:
            source: The BuildQueueSource to make active.
        """
        self.active_queue_source = source
        self.selected_queue_sources = []
        log_info(f"Controller: Active queue set to '{source.display_name}'")

    def set_selected_queues(self, sources: List['BuildQueueSource']) -> None:
        """Set multiple queue sources for multi-queue mode.

        Clears active_queue_source. Subsequent add_to_queue calls will
        add to all compatible queues in the list.

        Args:
            sources: List of BuildQueueSource instances to target.
        """
        self.active_queue_source = None
        self.selected_queue_sources = list(sources)
        log_info(f"Controller: Multi-select mode with {len(sources)} queues")

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
        Add a design to the appropriate queue(s).

        Routing logic:
        1. If selected_queue_sources is non-empty (multi-select mode),
           add to all compatible sources, skipping incompatible ones.
        2. If active_queue_source is set (single-select mode),
           add to that source if compatible.
        3. Otherwise, fall back to build_context.construction_queue.

        Args:
            design_id: ID of the design to build
            turns: Number of turns to complete (default 1)
            category: Design category (uses self.selected_category if None)
            index: Optional insertion index (only used in single-queue/fallback modes)
        """
        cat = category if category is not None else self.selected_category

        log_info(f"add_to_queue called: design_id={design_id}, category={cat}")

        # Route to multi-queue, single-queue, or fallback
        if self.selected_queue_sources:
            self._add_to_multiple_queues(design_id, turns, cat)
        elif self.active_queue_source is not None:
            self._add_to_single_queue(design_id, turns, cat, index)
        else:
            self._add_to_fallback(design_id, turns, cat, index)

        # Refresh display
        self.on_queue_changed()

    def _source_can_build_category(self, source: 'BuildQueueSource', category: str) -> bool:
        """Check if a queue source can build items of the given category.

        Args:
            source: The BuildQueueSource to check.
            category: Design category ("complex", "ship", "satellite", "fighter").

        Returns:
            True if the source can build items of this category.
        """
        if category in _SHIP_CATEGORIES:
            return source.can_build_ships
        if category in _COMPLEX_CATEGORIES:
            return source.can_build_complexes
        # Unknown category - allow by default
        return True

    def _add_to_single_queue(
        self, design_id: str, turns: int, category: str, index: Optional[int]
    ) -> None:
        """Add item to the active queue source.

        Args:
            design_id: ID of the design to build.
            turns: Number of turns to complete.
            category: Design category.
            index: Optional insertion index.
        """
        source = self.active_queue_source
        if not self._source_can_build_category(source, category):
            log_warning(
                f"Cannot build {category} in queue '{source.display_name}': "
                f"incompatible build type"
            )
            return

        queue_item = {
            "design_id": design_id,
            "type": category,
            "turns_remaining": turns
        }

        if index is not None:
            source.construction_queue.insert(index, queue_item)
            log_info(f"Inserted {design_id} into '{source.display_name}' at position {index}")
        else:
            source.construction_queue.append(queue_item)
            log_info(f"Added {design_id} to '{source.display_name}' ({turns} turns)")

    def _add_to_multiple_queues(self, design_id: str, turns: int, category: str) -> None:
        """Add item to all compatible selected queue sources.

        Skips sources that cannot build the given category. Index is not
        supported in multi-queue mode (always appends).

        Args:
            design_id: ID of the design to build.
            turns: Number of turns to complete.
            category: Design category.
        """
        added_count = 0
        skipped_count = 0

        for source in self.selected_queue_sources:
            if not self._source_can_build_category(source, category):
                log_warning(
                    f"Skipping queue '{source.display_name}': "
                    f"cannot build {category}"
                )
                skipped_count += 1
                continue

            queue_item = {
                "design_id": design_id,
                "type": category,
                "turns_remaining": turns
            }
            source.construction_queue.append(queue_item)
            added_count += 1

        log_info(
            f"Multi-queue add: {design_id} added to {added_count} queue(s), "
            f"{skipped_count} skipped"
        )

    def _add_to_fallback(
        self, design_id: str, turns: int, category: str, index: Optional[int]
    ) -> None:
        """Add item to build_context.construction_queue (fallback mode).

        Used when no queue source is explicitly set.

        Args:
            design_id: ID of the design to build.
            turns: Number of turns to complete.
            category: Design category.
            index: Optional insertion index.
        """
        log_info(f"  build_context.type = {self.build_context.context_type}")
        log_info(f"  build_context.has_space_shipyard = {self.build_context.has_space_shipyard}")

        # Validate build capability using protocol method
        if not self.build_context.can_build_type(category):
            log_warning(f"Cannot build {category}: build context cannot build this type")
            return

        queue_item = {
            "design_id": design_id,
            "type": category,
            "turns_remaining": turns
        }

        if index is not None:
            self.build_context.construction_queue.insert(index, queue_item)
            log_info(f"Inserted {design_id} into build queue at position {index}")
        else:
            self.build_context.construction_queue.append(queue_item)
            log_info(f"Added {design_id} to build queue ({turns} turns)")

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
