"""
Build Queue Controller - Business logic for queue operations.

Extracted from build_queue_screen.py (PROJ-63 Phase 3).
Manages category filtering, queue additions, and design report updates.

Updated in PROJ-67 Phase 4 to support BuildContext protocol (Planet or Fleet).
Updated in PROJ-69 Phase 4 to support multi-queue operations via BuildQueueSource.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Union

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.data.build_context import BuildContext
    from game.strategy.data.build_queue_source import BuildQueueSource
    from game.strategy.data.planet import Planet
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.galaxy import Galaxy
    from game.strategy.data.empire import Empire
    from game.core.hex_math import HexCoord
    from game.strategy.systems.design_library import DesignLibrary
    from game.ui.services.design_loader_adapter import DesignLoaderAdapter
    from game.ui.panels.design_report_panel import DesignReportPanel

# Type alias for the add-to-queue callback
# Signature: (entity_id, entity_type, design_id, category, index, target_planet_id, queue_id) -> None
AddToQueueCallback = Callable[[int, str, str, str, Optional[int], Optional[int], Optional[str]], None]

# Category-to-build-capability mapping
_SHIP_CATEGORIES = {"ship", "satellite", "fighter"}
_COMPLEX_CATEGORIES = {"complex", "drop_pod"}


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
        design_loader: 'DesignLoaderAdapter',
        design_report: 'DesignReportPanel',
        on_queue_changed: Callable[[], None],
        hex_coord: Optional['HexCoord'] = None,
        galaxy: Optional['Galaxy'] = None,
        empire: Optional['Empire'] = None,
        on_planet_selection_needed: Optional[Callable] = None,
        add_to_queue_callback: Optional['AddToQueueCallback'] = None,
        registries=None,
    ):
        """
        Initialize the controller.

        Args:
            build_context: Planet or Fleet whose construction_queue is managed (fallback)
            design_library: For scanning/loading designs
            design_loader: DesignLoaderAdapter for creating ship objects
            design_report: DesignReportPanel for updating display
            on_queue_changed: Callback to trigger queue display refresh
            hex_coord: Hex coordinate for planet lookup (PROJ-79)
            galaxy: Galaxy instance for planet lookup (PROJ-79)
            empire: Empire instance for ownership check (PROJ-79)
            on_planet_selection_needed: Callback when planet selection is needed (PROJ-79)
            add_to_queue_callback: PROJ-208 callback to dispatch AddToConstructionQueueCommand
            registries: GameRegistries for design validation
        """
        self.build_context = build_context
        self.design_library = design_library
        self._registries = registries
        self.design_loader = design_loader
        self.design_report = design_report
        self.on_queue_changed = on_queue_changed

        # PROJ-79: Galaxy context for planet selection
        self.hex_coord = hex_coord
        self.galaxy = galaxy
        self.empire = empire
        self.on_planet_selection_needed = on_planet_selection_needed

        # PROJ-208: Command dispatch callback
        self._add_to_queue_callback = add_to_queue_callback

        # Category filter state
        self.selected_category = "complex"
        self.selected_role = "Any"

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
        logger.info(f"Controller: Active queue set to '{source.display_name}'")

    def set_selected_queues(self, sources: List['BuildQueueSource']) -> None:
        """Set multiple queue sources for multi-queue mode.

        Clears active_queue_source. Subsequent add_to_queue calls will
        add to all compatible queues in the list.

        Args:
            sources: List of BuildQueueSource instances to target.
        """
        self.active_queue_source = None
        self.selected_queue_sources = list(sources)
        logger.info(f"Controller: Multi-select mode with {len(sources)} queues")

    def load_designs_by_category(self, category: str):
        """
        Load designs filtered by vehicle type.

        Args:
            category: One of "complex", "ship", "satellite", "fighter"

        Returns:
            List of design objects matching the category
        """
        all_designs = self.design_library.scan_designs()
        logger.debug(f"BuildQueue: Scanned {len(all_designs)} total designs from {self.design_library.designs_folder}")

        type_map = {
            "complex": "Planetary Complex",
            "ship": "Ship",
            "satellite": "Satellite",
            "fighter": "Fighter",
            "drop_pod": "Drop Pod"
        }

        target_type = type_map.get(category, "Ship")
        logger.debug(f"BuildQueue: Filtering for category '{category}' (vehicle_type='{target_type}')")

        filtered = [d for d in all_designs if d.vehicle_type == target_type]

        # Extra roles extraction and filtering
        roles_set = set()
        for d in filtered:
            role = getattr(d, 'design_role', None)
            if not role:
                role = "None"
            roles_set.add(role)
            
        roles_list = sorted(list(roles_set))
        if "Any" not in roles_list:
            roles_list.insert(0, "Any")
            
        if hasattr(self, 'selected_role') and self.selected_role != "Any":
            filtered = [
                d for d in filtered 
                if (getattr(d, 'design_role', None) == self.selected_role) 
                or (not getattr(d, 'design_role', None) and self.selected_role == "None")
            ]

        # Mark designs as valid/invalid using full validation
        self._validate_designs(filtered)

        logger.debug(f"BuildQueue: Found {len(filtered)} designs matching category '{category}' and role '{getattr(self, 'selected_role', 'Any')}'")

        if filtered:
            for d in filtered:
                logger.debug(f"  - {d.name} (vehicle_type={d.vehicle_type}, design_id={d.design_id})")

        return filtered, roles_list

    def _validate_designs(self, designs) -> None:
        """Run full validation on each design and set design_valid flag.

        Loads each design's data and runs DesignValidator to check all rules
        (crew, C&C, combat movement, mass budgets, etc.). Sets a `design_valid`
        attribute on each DesignMetadata object.
        """
        if not self._registries:
            for d in designs:
                d.design_valid = True
            return

        from game.strategy.services.design_validator import DesignValidator
        validator = DesignValidator(self._registries)

        for d in designs:
            try:
                load_result = self.design_library.load_design_data(d.design_id)
                if not load_result.success:
                    d.design_valid = False
                    continue

                result = validator.validate(load_result.data)
                d.design_valid = not result.has_issues
            except Exception:
                d.design_valid = True  # Can't validate, assume valid

    def set_category(self, category: str):
        """
        Set the active category filter.

        Args:
            category: Category to filter by ("complex", "ship", "satellite", "fighter")
        """
        self.selected_category = category
        self.selected_role = "Any"  # Reset role when switching categories
        self.on_queue_changed()
        logger.info(f"Build queue category changed to: {category}")

    def set_role(self, role: str):
        """
        Set the active role filter.

        Args:
            role: Role to filter by (e.g., "Capital", "Escort", "Any")
        """
        self.selected_role = role
        self.on_queue_changed()
        logger.info(f"Build queue role changed to: {role}")

    def _get_design_cost(self, design_id: str) -> Dict[str, int]:
        """Load design as ship and return its construction cost.

        This loads the design and creates a Ship object, whose
        construction_cost is populated during stat aggregation in
        Ship.recalculate_stats(). More reliable than reading from
        design metadata which may not have cost data.

        Args:
            design_id: ID of the design to get cost for.

        Returns:
            Dict of resource type -> amount, empty dict on error.
        """
        try:
            load_result = self.design_library.load_design_data(design_id)
            if not load_result.success:
                return {}
            ship = self.design_loader.load_ship_from_design_data(load_result.data, 0, 0)
            if ship is None:
                return {}
            return dict(ship.construction_cost) if ship.construction_cost else {}
        except (OSError, ValueError, KeyError) as e:
            logger.warning(f"Failed to load design cost for {design_id}: {e}")
            return {}

    def _calculate_build_turns(self, design_id: str, build_rate: Dict[str, float]) -> float:
        """Calculate build turns from design resource cost and per-resource rates.

        Formula: For each resource, turns_for_res = cost / rate.
        Total turns = max(resource_turns).
        Returns exact float value (e.g. 2.5 turns for tick-based granular production).

        Args:
            design_id: ID of the design to calculate for.
            build_rate: Per-resource production rates (resource -> units/turn).

        Returns:
            Number of turns required to build the design (float).
        """
        cost = self._get_design_cost(design_id)
        if not cost:
            return 1.0
        if not build_rate:
            return 1.0

        turns_per_resource = []
        for res, rate in build_rate.items():
            res_cost = cost.get(res, 0)
            if res_cost > 0 and rate > 0:
                turns_per_resource.append(res_cost / rate)

        if not turns_per_resource:
            return 1.0
        return max(0.01, max(turns_per_resource))

    def _build_cost_tracking(self, design_id: str) -> Dict[str, Any]:
        """Create cost tracking fields for a queue item.

        PROJ-79: Only sets initial state. Per-tick consumption is calculated
        dynamically by ProductionEngine from production_rates.json.

        Args:
            design_id: ID of the design to track costs for.

        Returns:
            Dict with total_cost and resources_consumed.
        """
        total_cost = self._get_design_cost(design_id)

        return {
            "total_cost": total_cost,
            "resources_consumed": {res: 0.0 for res in total_cost},
        }

    def add_to_queue(self, design_id: str, turns: Optional[float] = None, category: str = None, index: int = None):
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

        logger.info(f"add_to_queue called: design_id={design_id}, category={cat}")

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

    def _get_entity_info(self, source: 'BuildQueueSource') -> tuple:
        """Extract entity_id, entity_type, and queue_id from a BuildQueueSource.

        PROJ-208: Used to construct AddToConstructionQueueCommand.

        Args:
            source: The BuildQueueSource to extract info from.

        Returns:
            Tuple of (entity_id, entity_type, queue_id).
        """
        entity_type = source.context_type
        queue_id = source.queue_id  # For multi-queue support (e.g., shipyard facilities)
        if entity_type == "planet":
            # For planet sources, use the planet_id
            entity_id = source.planet_id
            if entity_id is None:
                # Fallback to owner_entity.id
                entity_id = getattr(source.owner_entity, 'id', None)
        else:  # fleet
            entity_id = getattr(source.owner_entity, 'id', None)
        return entity_id, entity_type, queue_id

    def _add_to_single_queue(
        self, design_id: str, turns: Optional[float], category: str, index: Optional[int]
    ) -> None:
        """Add item to the active queue source.

        PROJ-208: Routes through AddToConstructionQueueCommand via callback.

        Args:
            design_id: ID of the design to build.
            turns: Number of turns to complete (unused, handler calculates).
            category: Design category.
            index: Optional insertion index.
        """
        source = self.active_queue_source
        if not self._source_can_build_category(source, category):
            logger.warning(
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
                logger.warning("Planet selection needed but no callback provided")
                return

        # PROJ-208: Get entity info and dispatch via command callback
        entity_id, entity_type, queue_id = self._get_entity_info(source)
        target_planet_id = self._get_target_planet_id(source, category)

        if self._add_to_queue_callback and entity_id is not None:
            self._add_to_queue_callback(
                entity_id, entity_type, design_id, category, index, target_planet_id, queue_id
            )
            action = "Inserted" if index is not None else "Added"
            logger.info(f"{action} {design_id} to '{source.display_name}' via command")
        else:
            logger.warning(f"Cannot add to queue: callback={self._add_to_queue_callback}, entity_id={entity_id}")

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
        PROJ-208: Routes through AddToConstructionQueueCommand via callback.

        Args:
            source: The BuildQueueSource to add to.
            design_id: ID of the design to build.
            category: Design category.
            target_planet_id: ID of the planet to receive the complex.
            index: Optional insertion index.
        """
        # PROJ-208: Get entity info and dispatch via command callback
        entity_id, entity_type, queue_id = self._get_entity_info(source)

        if self._add_to_queue_callback and entity_id is not None:
            self._add_to_queue_callback(
                entity_id, entity_type, design_id, category, index, target_planet_id, queue_id
            )
            action = "Inserted" if index is not None else "Added"
            logger.info(f"{action} {design_id} to '{source.display_name}' via command (target: planet {target_planet_id})")
        else:
            logger.warning(f"Cannot add to queue with target planet: callback={self._add_to_queue_callback}, entity_id={entity_id}")

    def _add_to_multiple_queues(self, design_id: str, turns: Optional[float], category: str) -> None:
        """Add item to all compatible selected queue sources.

        PROJ-208: Routes through AddToConstructionQueueCommand via callback.
        Skips sources that cannot build the given category. Index is not
        supported in multi-queue mode (always appends).

        Args:
            design_id: ID of the design to build.
            turns: Number of turns to complete (unused, handler calculates).
            category: Design category.
        """
        added_count = 0
        skipped_count = 0

        for source in self.selected_queue_sources:
            if not self._source_can_build_category(source, category):
                logger.warning(
                    f"Skipping queue '{source.display_name}': "
                    f"cannot build {category}"
                )
                skipped_count += 1
                continue

            # PROJ-208: Get entity info and dispatch via command callback
            entity_id, entity_type, queue_id = self._get_entity_info(source)

            if self._add_to_queue_callback and entity_id is not None:
                # Multi-queue mode: always appends (index=None), no target_planet_id
                self._add_to_queue_callback(
                    entity_id, entity_type, design_id, category, None, None, queue_id
                )
                added_count += 1
            else:
                logger.warning(f"Cannot add to queue '{source.display_name}': callback={self._add_to_queue_callback}, entity_id={entity_id}")
                skipped_count += 1

        logger.info(
            f"Multi-queue add: {design_id} added to {added_count} queue(s) via command, "
            f"{skipped_count} skipped"
        )

    def _add_to_fallback(
        self, design_id: str, turns: Optional[float], category: str, index: Optional[int]
    ) -> None:
        """Add item to build_context.construction_queue (fallback mode).

        PROJ-208: Routes through AddToConstructionQueueCommand via callback.
        Used when no queue source is explicitly set.

        Args:
            design_id: ID of the design to build.
            turns: Number of turns to complete (unused, handler calculates).
            category: Design category.
            index: Optional insertion index.
        """
        logger.info(f"  build_context.type = {self.build_context.context_type}")
        logger.info(f"  build_context.has_space_shipyard = {self.build_context.has_space_shipyard}")

        # Validate build capability using protocol method
        if not self.build_context.can_build_type(category):
            logger.warning(f"Cannot build {category}: build context cannot build this type")
            return

        # PROJ-208: Get entity info from build_context and dispatch via command callback
        # Fallback mode: no queue_id (uses entity's main queue)
        entity_type = self.build_context.context_type
        entity_id = getattr(self.build_context, 'id', None)

        if self._add_to_queue_callback and entity_id is not None:
            self._add_to_queue_callback(
                entity_id, entity_type, design_id, category, index, None, None
            )
            action = "Inserted" if index is not None else "Added"
            logger.info(f"{action} {design_id} to build queue via command (fallback mode)")
        else:
            logger.warning(f"Cannot add to fallback queue: callback={self._add_to_queue_callback}, entity_id={entity_id}")

    def refresh_design_report(self, design_id: str):
        """
        Update design report panel with selected design.

        Args:
            design_id: Design ID to load and display
        """
        try:
            # Load design data using DesignLibrary (strategy layer)
            load_result = self.design_library.load_design_data(design_id)

            if not load_result.success:
                logger.warning(f"Could not load design {design_id}: {load_result.error}")
                self.design_report.show_placeholder()
                return

            # Use injected design_loader instead of creating new instance
            ship = self.design_loader.load_ship_from_design_data(
                load_result.data,
                center_x=1920 // 2,
                center_y=1080 // 2
            )

            if ship is None:
                logger.warning(f"Could not create ship from design {design_id}")
                self.design_report.show_placeholder()
                return

            # Update design report panel with ship data
            self.design_report.update_design(ship)
            logger.debug(f"Design report updated: {ship.name}")

        except (OSError, ValueError, KeyError) as e:
            logger.exception(f"Error loading design {design_id}: {e}")
            self.design_report.show_placeholder()
