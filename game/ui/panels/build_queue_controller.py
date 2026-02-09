"""
Build Queue Controller - Business logic for queue operations.

Extracted from build_queue_screen.py (PROJ-63 Phase 3).
Manages category filtering, queue additions, and design report updates.

Updated in PROJ-67 Phase 4 to support BuildContext protocol (Planet or Fleet).
Updated in PROJ-69 Phase 4 to support multi-queue operations via BuildQueueSource.
"""
from __future__ import annotations

import math
from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Union

from game.core.logger import log_info, log_warning, log_error, log_debug

# Build rate constants (units per turn)
PLANETARY_YARD_BUILD_RATE = 2000.0

if TYPE_CHECKING:
    from game.strategy.data.build_context import BuildContext
    from game.strategy.data.build_queue_source import BuildQueueSource
    from game.strategy.data.planet import Planet
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.galaxy import Galaxy
    from game.strategy.data.empire import Empire
    from game.strategy.data.hex_math import HexCoord
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
        on_queue_changed: Callable[[], None],
        hex_coord: Optional['HexCoord'] = None,
        galaxy: Optional['Galaxy'] = None,
        empire: Optional['Empire'] = None,
        on_planet_selection_needed: Optional[Callable] = None,
    ):
        """
        Initialize the controller.

        Args:
            build_context: Planet or Fleet whose construction_queue is managed (fallback)
            design_library: For scanning/loading designs
            design_loader: SimulationDesignLoader for creating ship objects
            design_report: DesignReportPanel for updating display
            on_queue_changed: Callback to trigger queue display refresh
            hex_coord: Hex coordinate for planet lookup (PROJ-79)
            galaxy: Galaxy instance for planet lookup (PROJ-79)
            empire: Empire instance for ownership check (PROJ-79)
            on_planet_selection_needed: Callback when planet selection is needed (PROJ-79)
        """
        self.build_context = build_context
        self.design_library = design_library
        self.design_loader = design_loader
        self.design_report = design_report
        self.on_queue_changed = on_queue_changed

        # PROJ-79: Galaxy context for planet selection
        self.hex_coord = hex_coord
        self.galaxy = galaxy
        self.empire = empire
        self.on_planet_selection_needed = on_planet_selection_needed

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

    def _calculate_build_turns(self, design_id: str, build_rate: float) -> int:
        """Calculate build turns from design resource cost and build rate.

        Formula: turns = max(1, ceil(max_resource_cost / build_rate))

        Args:
            design_id: ID of the design to calculate for.
            build_rate: Build rate in resource units per turn.

        Returns:
            Number of turns required to build the design.
        """
        designs = self.design_library.scan_designs()
        design = next((d for d in designs if d.design_id == design_id), None)
        if not design or not design.resource_cost:
            return 1
        max_cost = max(design.resource_cost.values()) if design.resource_cost else 0
        if max_cost <= 0:
            return 1
        return max(1, math.ceil(max_cost / build_rate))

    def _build_cost_tracking(self, design_id: str, turns: int) -> Dict[str, float]:
        """Create cost tracking fields for a queue item.

        Args:
            design_id: ID of the design to track costs for.
            turns: Number of turns for the build.

        Returns:
            Dict with total_cost, cost_per_tick, resources_consumed, ticks_in_current_turn.
        """
        designs = self.design_library.scan_designs()
        design = next((d for d in designs if d.design_id == design_id), None)
        total_cost = dict(design.resource_cost) if design and design.resource_cost else {}
        total_ticks = turns * 100
        cost_per_tick = {res: amount / total_ticks for res, amount in total_cost.items()} if total_ticks > 0 else {}
        return {
            "total_cost": total_cost,
            "cost_per_tick": cost_per_tick,
            "resources_consumed": {res: 0.0 for res in total_cost},
            "ticks_in_current_turn": 0,
        }

    def add_to_queue(self, design_id: str, turns: Optional[int] = None, category: str = None, index: int = None):
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

    def _needs_planet_selection(self, source: 'BuildQueueSource', category: str) -> bool:
        """Check if adding a complex to this source requires planet selection.

        PROJ-79: Fleet shipyards at multi-colony hexes must prompt for target planet.

        Args:
            source: The BuildQueueSource being added to.
            category: Design category.

        Returns:
            True if planet selection popup is needed.
        """
        if category != "complex":
            return False
        if source.context_type != "fleet":
            return False
        if getattr(source, 'planet_id', None) is not None:
            return False  # Already has a fixed planet
        if not self.hex_coord or not self.galaxy or not self.empire:
            return False  # No galaxy context

        planets = [
            p for p in self.galaxy.get_planets_at_global_hex(self.hex_coord)
            if p.owner_id == self.empire.id
        ]
        return len(planets) > 1

    def _get_target_planet_id(self, source: 'BuildQueueSource', category: str) -> Optional[int]:
        """Get target_planet_id for a queue item.

        PROJ-79: For planet sources, uses source.planet_id. For fleet sources
        at single-colony hexes, uses that planet's ID. For multi-colony hexes,
        returns None (caller should trigger planet selection).

        Args:
            source: The BuildQueueSource being added to.
            category: Design category.

        Returns:
            Planet ID if determinable, None if selection needed.
        """
        if category != "complex":
            return None

        # Planet source: use source's planet_id
        if source.context_type == "planet":
            return getattr(source, 'planet_id', None)

        # Fleet source: check for single colony at hex
        if source.context_type == "fleet":
            if getattr(source, 'planet_id', None) is not None:
                return source.planet_id

            if self.hex_coord and self.galaxy and self.empire:
                planets = [
                    p for p in self.galaxy.get_planets_at_global_hex(self.hex_coord)
                    if p.owner_id == self.empire.id
                ]
                if len(planets) == 1:
                    return planets[0].id

        return None

    def _add_to_single_queue(
        self, design_id: str, turns: Optional[int], category: str, index: Optional[int]
    ) -> None:
        """Add item to the active queue source.

        Args:
            design_id: ID of the design to build.
            turns: Number of turns to complete (calculated if None).
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

        # PROJ-79: Check if planet selection is needed for fleet+complex at multi-colony hex
        if self._needs_planet_selection(source, category):
            if self.on_planet_selection_needed:
                planets = [
                    p for p in self.galaxy.get_planets_at_global_hex(self.hex_coord)
                    if p.owner_id == self.empire.id
                ]

                def on_planet_selected(planet):
                    """Callback when planet is selected."""
                    self._add_item_with_target_planet(
                        source, design_id, category, planet.id, index
                    )
                    self.on_queue_changed()

                self.on_planet_selection_needed(planets, on_planet_selected)
                return  # Don't add directly - callback will do it
            else:
                log_warning("Planet selection needed but no callback provided")
                return

        # Calculate build time if not provided
        build_rate = source.build_rate
        if turns is None:
            turns = self._calculate_build_turns(design_id, build_rate)

        queue_item = {
            "design_id": design_id,
            "type": category,
            "turns_remaining": turns
        }
        # Add cost tracking fields
        queue_item.update(self._build_cost_tracking(design_id, turns))

        # PROJ-79: Add target_planet_id for complexes
        target_planet_id = self._get_target_planet_id(source, category)
        if target_planet_id is not None:
            queue_item["target_planet_id"] = target_planet_id

        if index is not None:
            source.construction_queue.insert(index, queue_item)
            log_info(f"Inserted {design_id} into '{source.display_name}' at position {index}")
        else:
            source.construction_queue.append(queue_item)
            log_info(f"Added {design_id} to '{source.display_name}' ({turns} turns)")

    def _add_item_with_target_planet(
        self,
        source: 'BuildQueueSource',
        design_id: str,
        category: str,
        target_planet_id: int,
        index: Optional[int] = None
    ) -> None:
        """Add item with specified target_planet_id.

        PROJ-79: Called after planet selection callback.

        Args:
            source: The BuildQueueSource to add to.
            design_id: ID of the design to build.
            category: Design category.
            target_planet_id: ID of the planet to receive the complex.
            index: Optional insertion index.
        """
        build_rate = source.build_rate
        turns = self._calculate_build_turns(design_id, build_rate)

        queue_item = {
            "design_id": design_id,
            "type": category,
            "turns_remaining": turns,
            "target_planet_id": target_planet_id,
        }
        queue_item.update(self._build_cost_tracking(design_id, turns))

        if index is not None:
            source.construction_queue.insert(index, queue_item)
            log_info(f"Inserted {design_id} into '{source.display_name}' at position {index} (target: planet {target_planet_id})")
        else:
            source.construction_queue.append(queue_item)
            log_info(f"Added {design_id} to '{source.display_name}' ({turns} turns, target: planet {target_planet_id})")

    def _add_to_multiple_queues(self, design_id: str, turns: Optional[int], category: str) -> None:
        """Add item to all compatible selected queue sources.

        Skips sources that cannot build the given category. Index is not
        supported in multi-queue mode (always appends).

        Args:
            design_id: ID of the design to build.
            turns: Number of turns to complete (calculated per-source if None).
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

            # Calculate build time per-source if not provided
            source_turns = turns
            if source_turns is None:
                source_turns = self._calculate_build_turns(design_id, source.build_rate)

            queue_item = {
                "design_id": design_id,
                "type": category,
                "turns_remaining": source_turns
            }
            # Add cost tracking fields
            queue_item.update(self._build_cost_tracking(design_id, source_turns))
            source.construction_queue.append(queue_item)
            added_count += 1

        log_info(
            f"Multi-queue add: {design_id} added to {added_count} queue(s), "
            f"{skipped_count} skipped"
        )

    def _add_to_fallback(
        self, design_id: str, turns: Optional[int], category: str, index: Optional[int]
    ) -> None:
        """Add item to build_context.construction_queue (fallback mode).

        Used when no queue source is explicitly set.

        Args:
            design_id: ID of the design to build.
            turns: Number of turns to complete (calculated if None).
            category: Design category.
            index: Optional insertion index.
        """
        log_info(f"  build_context.type = {self.build_context.context_type}")
        log_info(f"  build_context.has_space_shipyard = {self.build_context.has_space_shipyard}")

        # Validate build capability using protocol method
        if not self.build_context.can_build_type(category):
            log_warning(f"Cannot build {category}: build context cannot build this type")
            return

        # Calculate build time if not provided
        if turns is None:
            turns = self._calculate_build_turns(design_id, PLANETARY_YARD_BUILD_RATE)

        queue_item = {
            "design_id": design_id,
            "type": category,
            "turns_remaining": turns
        }
        # Add cost tracking fields
        queue_item.update(self._build_cost_tracking(design_id, turns))

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
