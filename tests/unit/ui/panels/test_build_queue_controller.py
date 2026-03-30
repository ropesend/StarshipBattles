"""
Tests for BuildQueueController multi-queue operations.

PROJ-69 Phase 6: Verifies single-queue, multi-queue, and fallback add behavior,
including can_build_ships/can_build_complexes compatibility filtering.

PROJ-79 Phase 2: Added tests for build time calculation and cost tracking.
PROJ-208 Phase 2: Updated to use command callback pattern for queue mutations.
"""
import pytest
from unittest.mock import MagicMock
from typing import Optional

from game.ui.panels.build_queue_controller import BuildQueueController
from game.strategy.data.build_queue_source import BuildQueueSource, get_default_production_rates


# PROJ-208: Registry for tracking entities by ID for callback resolution
_entity_registry = {}


def _make_add_callback(entity_registry: dict):
    """Create a callback that adds items to queues via entity registry.

    PROJ-208: Simulates the command handler behavior for testing.
    """
    def add_to_queue_callback(
        entity_id: int,
        entity_type: str,
        design_id: str,
        category: str,
        index: Optional[int],
        target_planet_id: Optional[int],
        queue_id: Optional[str] = None,
    ) -> None:
        # Find entity in registry
        key = (entity_type, entity_id)
        entity = entity_registry.get(key)
        if entity and hasattr(entity, 'construction_queue'):
            queue_item = {
                "design_id": design_id,
                "type": category,
                "turns_remaining": 1.0,  # Handler default
                "total_cost": {},
                "resources_consumed": {},
            }
            if target_planet_id is not None:
                queue_item["target_planet_id"] = target_planet_id
            if index is not None:
                entity.construction_queue.insert(index, queue_item)
            else:
                entity.construction_queue.append(queue_item)
    return add_to_queue_callback


def _make_controller(build_context=None, entity_registry=None) -> BuildQueueController:
    """Create a controller with mock dependencies.

    PROJ-208: Now includes add_to_queue_callback for command pattern.
    """
    if entity_registry is None:
        entity_registry = {}

    if build_context is None:
        build_context = MagicMock()
        build_context.context_type = "planet"
        build_context.has_space_shipyard = True
        build_context.can_build_type.return_value = True
        build_context.construction_queue = []
        build_context.id = 1
        # Register in entity registry
        entity_registry[("planet", 1)] = build_context

    mock_library = MagicMock()
    mock_loader = MagicMock()
    mock_report = MagicMock()
    on_changed = MagicMock()

    return BuildQueueController(
        build_context=build_context,
        design_library=mock_library,
        design_loader=mock_loader,
        design_report=mock_report,
        on_queue_changed=on_changed,
        add_to_queue_callback=_make_add_callback(entity_registry),
    )


def _default_build_rate() -> dict:
    """Return default build rate dict for testing."""
    return {"metals": 2000.0, "organics": 2000.0, "radioactives": 2000.0, "vapors": 2000.0, "exotics": 2000.0}


# PROJ-208: Counter for generating unique entity IDs
_entity_id_counter = 0


def _make_source(
    queue_id: str = "test_queue",
    display_name: str = "Test Queue",
    can_build_ships: bool = True,
    can_build_complexes: bool = True,
    queue: list = None,
    build_rate: dict = None,
    context_type: str = "planet",
    planet_id: int = None,
    entity_registry: dict = None,
) -> BuildQueueSource:
    """Create a BuildQueueSource with a real mutable queue.

    PROJ-208: If entity_registry is provided, registers the owner_entity
    so the command callback can find it. For planet sources, register
    using planet_id as the key (matching _get_entity_info behavior).
    """
    global _entity_id_counter
    _entity_id_counter += 1

    actual_queue = queue if queue is not None else []
    actual_rate = build_rate if build_rate is not None else _default_build_rate()

    # Create owner_entity with construction_queue and id
    owner_entity = MagicMock()
    owner_entity.construction_queue = actual_queue
    owner_entity.id = _entity_id_counter

    # For planet sources, use planet_id or generated id
    effective_planet_id = planet_id if planet_id is not None else (
        _entity_id_counter if context_type == "planet" else None
    )

    source = BuildQueueSource(
        queue_id=queue_id,
        display_name=display_name,
        owner_entity=owner_entity,
        construction_queue=actual_queue,
        can_build_ships=can_build_ships,
        can_build_complexes=can_build_complexes,
        context_type=context_type,
        build_rate=actual_rate,
        planet_id=effective_planet_id,
    )

    # PROJ-208: Register entity for command callback resolution
    # For planets, use planet_id; for fleets, use owner_entity.id
    # This matches _get_entity_info behavior
    if entity_registry is not None:
        if context_type == "planet":
            entity_registry[(context_type, effective_planet_id)] = owner_entity
        else:
            entity_registry[(context_type, owner_entity.id)] = owner_entity

    return source


class TestControllerSingleQueueAdd:
    """Tests for single-queue add behavior.

    PROJ-208: Tests updated to use entity_registry for command callback resolution.
    turns_remaining now uses handler default (1.0) instead of UI-provided value.
    """

    def test_add_to_single_active_queue(self):
        """Adding to queue when active_queue_source is set targets that source."""
        entity_registry = {}
        controller = _make_controller(entity_registry=entity_registry)
        source = _make_source(queue_id="yard_1", display_name="Shipyard 1", entity_registry=entity_registry)
        controller.set_active_queue(source)

        controller.add_to_queue("scout_ship", turns=3, category="ship")

        assert len(source.construction_queue) == 1
        item = source.construction_queue[0]
        assert item["design_id"] == "scout_ship"
        assert item["type"] == "ship"
        # PROJ-208: Handler uses default turns_remaining (1.0)
        assert item["turns_remaining"] == 1.0

    def test_add_incompatible_category_to_single_queue_rejected(self):
        """Ship category rejected by queue that can't build ships."""
        entity_registry = {}
        controller = _make_controller(entity_registry=entity_registry)
        source = _make_source(can_build_ships=False, can_build_complexes=True, entity_registry=entity_registry)
        controller.set_active_queue(source)

        controller.add_to_queue("scout_ship", turns=3, category="ship")

        assert len(source.construction_queue) == 0  # Rejected

    def test_add_complex_to_base_queue(self):
        """Complex category accepted by base queue (ships=False, complexes=True)."""
        entity_registry = {}
        controller = _make_controller(entity_registry=entity_registry)
        source = _make_source(
            queue_id="base",
            can_build_ships=False,
            can_build_complexes=True,
            entity_registry=entity_registry,
        )
        controller.set_active_queue(source)

        controller.add_to_queue("factory", turns=5, category="complex")

        assert len(source.construction_queue) == 1
        assert source.construction_queue[0]["type"] == "complex"

    def test_add_with_index_inserts_at_position(self):
        """Adding with index inserts at specified position."""
        entity_registry = {}
        controller = _make_controller(entity_registry=entity_registry)
        existing_queue = [
            {"design_id": "item_a", "type": "ship", "turns_remaining": 3},
            {"design_id": "item_b", "type": "ship", "turns_remaining": 5},
        ]
        source = _make_source(queue=existing_queue, entity_registry=entity_registry)
        controller.set_active_queue(source)

        controller.add_to_queue("item_c", turns=2, category="ship", index=1)

        assert len(source.construction_queue) == 3
        assert source.construction_queue[1]["design_id"] == "item_c"


class TestControllerMultiQueueAdd:
    """Tests for multi-queue add behavior.

    PROJ-208: Tests updated to use entity_registry for command callback resolution.
    """

    def test_add_to_all_selected_queues(self):
        """Adding in multi-select mode adds to all selected queues."""
        entity_registry = {}
        controller = _make_controller(entity_registry=entity_registry)
        source1 = _make_source(queue_id="yard_1", entity_registry=entity_registry)
        source2 = _make_source(queue_id="yard_2", entity_registry=entity_registry)
        controller.set_selected_queues([source1, source2])

        controller.add_to_queue("cruiser", turns=8, category="ship")

        assert len(source1.construction_queue) == 1
        assert len(source2.construction_queue) == 1
        assert source1.construction_queue[0]["design_id"] == "cruiser"
        assert source2.construction_queue[0]["design_id"] == "cruiser"

    def test_multi_add_skips_incompatible_queues(self):
        """Multi-add skips queues that can't build the category."""
        entity_registry = {}
        controller = _make_controller(entity_registry=entity_registry)
        base_queue = _make_source(
            queue_id="base",
            display_name="Base",
            can_build_ships=False,
            can_build_complexes=True,
            entity_registry=entity_registry,
        )
        yard_queue = _make_source(
            queue_id="yard_1",
            display_name="Shipyard 1",
            can_build_ships=True,
            can_build_complexes=True,
            entity_registry=entity_registry,
        )
        controller.set_selected_queues([base_queue, yard_queue])

        controller.add_to_queue("destroyer", turns=6, category="ship")

        # Base queue can't build ships - skipped
        assert len(base_queue.construction_queue) == 0
        # Shipyard queue can build ships - added
        assert len(yard_queue.construction_queue) == 1

    def test_multi_add_complex_to_all_compatible(self):
        """Multi-add complex adds to all queues that support complexes."""
        entity_registry = {}
        controller = _make_controller(entity_registry=entity_registry)
        base_queue = _make_source(
            queue_id="base",
            can_build_ships=False,
            can_build_complexes=True,
            entity_registry=entity_registry,
        )
        yard_queue = _make_source(
            queue_id="yard_1",
            can_build_ships=True,
            can_build_complexes=True,
            entity_registry=entity_registry,
        )
        controller.set_selected_queues([base_queue, yard_queue])

        controller.add_to_queue("factory", turns=4, category="complex")

        # Both can build complexes
        assert len(base_queue.construction_queue) == 1
        assert len(yard_queue.construction_queue) == 1

    def test_multi_add_fighter_respects_ship_flag(self):
        """Fighter category uses can_build_ships flag."""
        entity_registry = {}
        controller = _make_controller(entity_registry=entity_registry)
        base_queue = _make_source(can_build_ships=False, can_build_complexes=True, entity_registry=entity_registry)
        yard_queue = _make_source(can_build_ships=True, can_build_complexes=True, entity_registry=entity_registry)
        controller.set_selected_queues([base_queue, yard_queue])

        controller.add_to_queue("interceptor", turns=2, category="fighter")

        assert len(base_queue.construction_queue) == 0  # Skipped
        assert len(yard_queue.construction_queue) == 1  # Added

    def test_multi_add_satellite_respects_ship_flag(self):
        """Satellite category uses can_build_ships flag."""
        entity_registry = {}
        controller = _make_controller(entity_registry=entity_registry)
        base_queue = _make_source(can_build_ships=False, can_build_complexes=True, entity_registry=entity_registry)
        yard_queue = _make_source(can_build_ships=True, can_build_complexes=True, entity_registry=entity_registry)
        controller.set_selected_queues([base_queue, yard_queue])

        controller.add_to_queue("comm_sat", turns=1, category="satellite")

        assert len(base_queue.construction_queue) == 0
        assert len(yard_queue.construction_queue) == 1


class TestControllerModeTransitions:
    """Tests for controller mode transitions."""

    def test_set_active_queue_clears_multi_select(self):
        """Setting active queue clears multi-select."""
        entity_registry = {}
        controller = _make_controller(entity_registry=entity_registry)
        controller.set_selected_queues([_make_source(entity_registry=entity_registry), _make_source(entity_registry=entity_registry)])
        assert len(controller.selected_queue_sources) == 2

        controller.set_active_queue(_make_source(entity_registry=entity_registry))

        assert controller.active_queue_source is not None
        assert len(controller.selected_queue_sources) == 0

    def test_set_selected_queues_clears_active(self):
        """Setting multi-select clears active queue."""
        entity_registry = {}
        controller = _make_controller(entity_registry=entity_registry)
        controller.set_active_queue(_make_source(entity_registry=entity_registry))
        assert controller.active_queue_source is not None

        controller.set_selected_queues([_make_source(entity_registry=entity_registry)])

        assert controller.active_queue_source is None
        assert len(controller.selected_queue_sources) == 1

    def test_fallback_to_build_context_when_no_source(self):
        """Falls back to build_context when neither source is set.

        PROJ-208: Fallback mode now uses command callback pattern.
        """
        entity_registry = {}
        build_context = MagicMock()
        build_context.context_type = "planet"
        build_context.has_space_shipyard = True
        build_context.can_build_type.return_value = True
        build_context.construction_queue = []
        build_context.id = 999
        entity_registry[("planet", 999)] = build_context

        controller = _make_controller(build_context=build_context, entity_registry=entity_registry)
        # No active_queue_source, no selected_queue_sources

        controller.add_to_queue("factory", turns=3, category="complex")

        assert len(build_context.construction_queue) == 1
        assert build_context.construction_queue[0]["design_id"] == "factory"


class TestBuildTimeCalculation:
    """PROJ-79 Phase 2: Tests for build time calculation from resource cost."""

    def _make_controller_with_designs(self, designs: list) -> BuildQueueController:
        """Create a controller with mock design library returning given designs.

        Updated in PROJ-81: Mocks load_design_data and load_ship_from_design_data
        to return ships with construction_cost (used by _get_design_cost).
        """
        build_context = MagicMock()
        build_context.context_type = "planet"
        build_context.has_space_shipyard = True
        build_context.can_build_type.return_value = True
        build_context.construction_queue = []

        mock_library = MagicMock()
        mock_library.scan_designs.return_value = designs

        # Build design_id -> construction_cost map for mocking
        design_costs = {}
        for d in designs:
            design_costs[d.design_id] = d.construction_cost

        # Mock load_design_data to return a dict with design_id
        def mock_load_design_data(design_id):
            if design_id in design_costs:
                return {"design_id": design_id}
            return None
        mock_library.load_design_data.side_effect = mock_load_design_data

        # Mock load_ship_from_design_data to return a ship with construction_cost
        mock_loader = MagicMock()
        def mock_load_ship(design_data, x, y):
            if design_data is None:
                return None
            design_id = design_data.get("design_id")
            cost = design_costs.get(design_id)
            if cost is None:
                return None
            ship = MagicMock()
            ship.construction_cost = cost
            return ship
        mock_loader.load_ship_from_design_data.side_effect = mock_load_ship

        mock_report = MagicMock()
        on_changed = MagicMock()

        return BuildQueueController(
            build_context=build_context,
            design_library=mock_library,
            design_loader=mock_loader,
            design_report=mock_report,
            on_queue_changed=on_changed,
        )

    def test_calculate_build_turns_high_cost_planetary_yard(self):
        """100000 Metals at 2000/turn = 50 turns."""
        design = MagicMock()
        design.design_id = "big_complex"
        design.construction_cost = {"metals": 100000, "organics": 10000}

        controller = self._make_controller_with_designs([design])
        build_rate = {"metals": 2000.0, "organics": 2000.0}
        turns = controller._calculate_build_turns("big_complex", build_rate)

        assert turns == 50  # ceil(100000/2000) = 50, ceil(10000/2000) = 5 → max = 50

    def test_calculate_build_turns_shipyard_rate(self):
        """6000 Metals at 3000/turn = 2 turns."""
        design = MagicMock()
        design.design_id = "cruiser"
        design.construction_cost = {"metals": 6000}

        controller = self._make_controller_with_designs([design])
        build_rate = {"metals": 3000.0}
        turns = controller._calculate_build_turns("cruiser", build_rate)

        assert turns == 2  # 6000 / 3000 = 2

    def test_calculate_build_turns_zero_cost_returns_1(self):
        """Zero-cost design returns 1 turn minimum."""
        design = MagicMock()
        design.design_id = "free_stuff"
        design.construction_cost = {}

        controller = self._make_controller_with_designs([design])
        build_rate = {"metals": 2000.0}
        turns = controller._calculate_build_turns("free_stuff", build_rate)

        assert turns == 1

    def test_calculate_build_turns_no_construction_cost_returns_1(self):
        """Design with no construction_cost attribute returns 1 turn."""
        design = MagicMock()
        design.design_id = "no_cost"
        design.construction_cost = None

        controller = self._make_controller_with_designs([design])
        build_rate = {"metals": 2000.0}
        turns = controller._calculate_build_turns("no_cost", build_rate)

        assert turns == 1

    def test_calculate_build_turns_unknown_design_returns_1(self):
        """Unknown design ID returns 1 turn."""
        controller = self._make_controller_with_designs([])
        build_rate = {"metals": 2000.0}
        turns = controller._calculate_build_turns("unknown", build_rate)

        assert turns == 1

    def test_build_cost_tracking_fields_created(self):
        """_build_cost_tracking creates required fields for dynamic engine."""
        design = MagicMock()
        design.design_id = "factory"
        design.construction_cost = {"metals": 4000, "organics": 2000}

        controller = self._make_controller_with_designs([design])
        tracking = controller._build_cost_tracking("factory")

        # Dynamic engine uses total_cost and resources_consumed
        # Per-tick rates calculated dynamically from production_rates.json
        assert tracking["total_cost"] == {"metals": 4000, "organics": 2000}
        assert tracking["resources_consumed"] == {"metals": 0.0, "organics": 0.0}

    def test_add_to_queue_creates_cost_tracking(self):
        """Adding to queue creates required fields via command callback.

        PROJ-208: Cost tracking is now handled by command handler, which
        creates items with total_cost and resources_consumed fields.
        """
        design = MagicMock()
        design.design_id = "factory"
        design.construction_cost = {"metals": 4000}

        entity_registry = {}
        controller = self._make_controller_with_designs([design])
        controller._add_to_queue_callback = _make_add_callback(entity_registry)

        source = _make_source(build_rate={"metals": 2000.0}, entity_registry=entity_registry)
        controller.set_active_queue(source)

        controller.add_to_queue("factory", category="complex")

        item = source.construction_queue[0]
        # PROJ-208: Handler uses default turns_remaining (1.0)
        assert item["turns_remaining"] == 1.0
        assert "total_cost" in item
        assert "resources_consumed" in item

    def test_add_to_queue_uses_source_build_rate(self):
        """Items are added via command callback.

        PROJ-208: Build time is now set by handler (default 1.0),
        not calculated from source build_rate.
        """
        design = MagicMock()
        design.design_id = "cruiser"
        design.construction_cost = {"metals": 9000}

        entity_registry = {}
        controller = self._make_controller_with_designs([design])
        controller._add_to_queue_callback = _make_add_callback(entity_registry)

        source = _make_source(build_rate={"metals": 3000.0}, entity_registry=entity_registry)
        controller.set_active_queue(source)

        controller.add_to_queue("cruiser", category="ship")

        item = source.construction_queue[0]
        # PROJ-208: Handler uses default turns_remaining (1.0)
        assert item["turns_remaining"] == 1.0

    def test_multi_queue_add_uses_per_source_build_rate(self):
        """Multi-queue add adds items to all selected queues.

        PROJ-208: Test updated to verify command callback pattern.
        turns_remaining is now set by handler (default 1.0), not calculated per-source.
        """
        design = MagicMock()
        design.design_id = "cruiser"
        design.construction_cost = {"metals": 6000}

        entity_registry = {}
        controller = self._make_controller_with_designs([design])
        # Inject callback with entity registry
        controller._add_to_queue_callback = _make_add_callback(entity_registry)

        slow_source = _make_source(queue_id="slow", build_rate={"metals": 2000.0}, entity_registry=entity_registry)
        fast_source = _make_source(queue_id="fast", build_rate={"metals": 3000.0}, entity_registry=entity_registry)
        controller.set_selected_queues([slow_source, fast_source])

        controller.add_to_queue("cruiser", category="ship")

        # PROJ-208: Items added via command, handler uses default turns_remaining
        assert len(slow_source.construction_queue) == 1
        assert len(fast_source.construction_queue) == 1
        assert slow_source.construction_queue[0]["turns_remaining"] == 1.0
        assert fast_source.construction_queue[0]["turns_remaining"] == 1.0

    def test_fallback_uses_planetary_yard_rate(self):
        """Fallback mode adds item to build_context queue.

        PROJ-208: Test updated to verify command callback pattern.
        turns_remaining is now set by handler (default 1.0), not calculated.
        """
        design = MagicMock()
        design.design_id = "factory"
        design.construction_cost = {"metals": 4000}

        entity_registry = {}
        build_context = MagicMock()
        build_context.context_type = "planet"
        build_context.has_space_shipyard = True
        build_context.can_build_type.return_value = True
        build_context.construction_queue = []
        build_context.id = 999
        entity_registry[("planet", 999)] = build_context

        mock_library = MagicMock()
        mock_library.scan_designs.return_value = [design]
        mock_library.load_design_data.return_value = {"design_id": "factory"}

        # Mock loader to return ship with construction_cost
        mock_loader = MagicMock()
        mock_ship = MagicMock()
        mock_ship.construction_cost = {"metals": 4000}
        mock_loader.load_ship_from_design_data.return_value = mock_ship

        controller = BuildQueueController(
            build_context=build_context,
            design_library=mock_library,
            design_loader=mock_loader,
            design_report=MagicMock(),
            on_queue_changed=MagicMock(),
            add_to_queue_callback=_make_add_callback(entity_registry),
        )

        controller.add_to_queue("factory", category="complex")

        # PROJ-208: Handler uses default turns_remaining (1.0)
        item = build_context.construction_queue[0]
        assert item["turns_remaining"] == 1.0


class TestPlanetSelectionForFleetComplexes:
    """PROJ-79 Phase 4: Tests for planet selection when fleet adds complex at multi-colony hex."""

    def _make_fleet_controller_with_galaxy(
        self,
        hex_coord,
        galaxy,
        empire,
        planets_at_hex: list,
        entity_registry: dict = None,
    ) -> BuildQueueController:
        """Create controller with fleet source and galaxy context.

        PROJ-208: Now accepts entity_registry for command callback pattern.
        """
        if entity_registry is None:
            entity_registry = {}

        build_context = MagicMock()
        build_context.context_type = "fleet"
        build_context.has_space_shipyard = True
        build_context.can_build_type.return_value = True
        build_context.construction_queue = []

        mock_library = MagicMock()
        mock_library.scan_designs.return_value = []
        mock_loader = MagicMock()
        mock_report = MagicMock()
        on_changed = MagicMock()
        on_planet_selection = MagicMock()

        # Mock galaxy.get_planets_at_global_hex
        galaxy.get_planets_at_global_hex.return_value = planets_at_hex

        controller = BuildQueueController(
            build_context=build_context,
            design_library=mock_library,
            design_loader=mock_loader,
            design_report=mock_report,
            on_queue_changed=on_changed,
            hex_coord=hex_coord,
            galaxy=galaxy,
            empire=empire,
            on_planet_selection_needed=on_planet_selection,
            add_to_queue_callback=_make_add_callback(entity_registry),
        )
        return controller

    def test_needs_planet_selection_true_for_fleet_complex_multi_colony(self):
        """_needs_planet_selection returns True for fleet+complex at multi-colony hex."""
        hex_coord = MagicMock()
        galaxy = MagicMock()
        empire = MagicMock()
        empire.id = 1

        planet1 = MagicMock()
        planet1.id = 10
        planet1.owner_id = 1
        planet2 = MagicMock()
        planet2.id = 20
        planet2.owner_id = 1

        controller = self._make_fleet_controller_with_galaxy(
            hex_coord, galaxy, empire, [planet1, planet2]
        )

        source = _make_source(context_type="fleet")
        source.context_type = "fleet"
        source.planet_id = None
        controller.set_active_queue(source)

        result = controller._needs_planet_selection(source, "complex")
        assert result is True

    def test_needs_planet_selection_false_for_planet_source(self):
        """_needs_planet_selection returns False when source has planet_id."""
        hex_coord = MagicMock()
        galaxy = MagicMock()
        empire = MagicMock()
        empire.id = 1

        planet1 = MagicMock()
        planet1.id = 10
        planet1.owner_id = 1
        planet2 = MagicMock()
        planet2.id = 20
        planet2.owner_id = 1

        controller = self._make_fleet_controller_with_galaxy(
            hex_coord, galaxy, empire, [planet1, planet2]
        )

        source = _make_source(context_type="planet")
        source.context_type = "planet"
        source.planet_id = 10  # Has fixed planet
        controller.set_active_queue(source)

        result = controller._needs_planet_selection(source, "complex")
        assert result is False

    def test_needs_planet_selection_false_for_ship_category(self):
        """_needs_planet_selection returns False for non-complex categories."""
        hex_coord = MagicMock()
        galaxy = MagicMock()
        empire = MagicMock()
        empire.id = 1

        planet1 = MagicMock()
        planet1.id = 10
        planet1.owner_id = 1
        planet2 = MagicMock()
        planet2.id = 20
        planet2.owner_id = 1

        controller = self._make_fleet_controller_with_galaxy(
            hex_coord, galaxy, empire, [planet1, planet2]
        )

        source = _make_source(context_type="fleet")
        source.context_type = "fleet"
        source.planet_id = None
        controller.set_active_queue(source)

        result = controller._needs_planet_selection(source, "ship")
        assert result is False

    def test_needs_planet_selection_false_for_single_colony(self):
        """_needs_planet_selection returns False when only one planet at hex."""
        hex_coord = MagicMock()
        galaxy = MagicMock()
        empire = MagicMock()
        empire.id = 1

        planet1 = MagicMock()
        planet1.id = 10
        planet1.owner_id = 1

        controller = self._make_fleet_controller_with_galaxy(
            hex_coord, galaxy, empire, [planet1]
        )

        source = _make_source(context_type="fleet")
        source.context_type = "fleet"
        source.planet_id = None
        controller.set_active_queue(source)

        result = controller._needs_planet_selection(source, "complex")
        assert result is False

    def test_add_complex_triggers_planet_selection_callback(self):
        """Adding complex to fleet at multi-colony hex triggers callback."""
        hex_coord = MagicMock()
        galaxy = MagicMock()
        empire = MagicMock()
        empire.id = 1

        planet1 = MagicMock()
        planet1.id = 10
        planet1.owner_id = 1
        planet2 = MagicMock()
        planet2.id = 20
        planet2.owner_id = 1

        controller = self._make_fleet_controller_with_galaxy(
            hex_coord, galaxy, empire, [planet1, planet2]
        )

        source = _make_source(context_type="fleet")
        source.context_type = "fleet"
        source.planet_id = None
        controller.set_active_queue(source)

        controller.add_to_queue("factory", category="complex")

        # Callback should have been called
        controller.on_planet_selection_needed.assert_called_once()
        call_args = controller.on_planet_selection_needed.call_args
        planets_arg = call_args[0][0]
        assert planet1 in planets_arg
        assert planet2 in planets_arg

    def test_add_complex_single_colony_auto_sets_target_planet_id(self):
        """Adding complex at single-colony hex auto-sets target_planet_id.

        PROJ-208: Updated to use entity_registry for command callback pattern.
        """
        hex_coord = MagicMock()
        galaxy = MagicMock()
        empire = MagicMock()
        empire.id = 1

        planet1 = MagicMock()
        planet1.id = 10
        planet1.owner_id = 1

        entity_registry = {}
        controller = self._make_fleet_controller_with_galaxy(
            hex_coord, galaxy, empire, [planet1], entity_registry=entity_registry
        )

        source = _make_source(context_type="fleet", build_rate={"metals": 2000.0}, entity_registry=entity_registry)
        source.context_type = "fleet"
        source.planet_id = None
        controller.set_active_queue(source)

        controller.add_to_queue("factory", category="complex")

        # Should have added directly with target_planet_id
        assert len(source.construction_queue) == 1
        item = source.construction_queue[0]
        assert item.get("target_planet_id") == 10

    def test_add_complex_planet_source_uses_planet_id(self):
        """Adding complex via planet source uses source.planet_id.

        PROJ-208: Updated to use entity_registry for command callback pattern.
        """
        hex_coord = MagicMock()
        galaxy = MagicMock()
        empire = MagicMock()
        empire.id = 1

        planet1 = MagicMock()
        planet1.id = 10
        planet1.owner_id = 1

        entity_registry = {}
        controller = self._make_fleet_controller_with_galaxy(
            hex_coord, galaxy, empire, [planet1], entity_registry=entity_registry
        )

        source = _make_source(context_type="planet", build_rate={"metals": 2000.0}, entity_registry=entity_registry, planet_id=10)
        source.context_type = "planet"
        controller.set_active_queue(source)

        controller.add_to_queue("factory", category="complex")

        # Should add directly with target_planet_id = source.planet_id
        assert len(source.construction_queue) == 1
        item = source.construction_queue[0]
        assert item.get("target_planet_id") == 10


class TestPerResourceBuildRates:
    """PROJ-97 Phase 3: Tests for per-resource production rate limits."""

    def _make_controller_with_designs(self, designs: list) -> BuildQueueController:
        """Create a controller with mock design library returning given designs."""
        build_context = MagicMock()
        build_context.context_type = "planet"
        build_context.has_space_shipyard = True
        build_context.can_build_type.return_value = True
        build_context.construction_queue = []

        mock_library = MagicMock()
        mock_library.scan_designs.return_value = designs

        # Build design_id -> construction_cost map for mocking
        design_costs = {}
        for d in designs:
            design_costs[d.design_id] = d.construction_cost

        def mock_load_design_data(design_id):
            if design_id in design_costs:
                return {"design_id": design_id}
            return None
        mock_library.load_design_data.side_effect = mock_load_design_data

        mock_loader = MagicMock()
        def mock_load_ship(design_data, x, y):
            if design_data is None:
                return None
            design_id = design_data.get("design_id")
            cost = design_costs.get(design_id)
            if cost is None:
                return None
            ship = MagicMock()
            ship.construction_cost = cost
            return ship
        mock_loader.load_ship_from_design_data.side_effect = mock_load_ship

        mock_report = MagicMock()
        on_changed = MagicMock()

        return BuildQueueController(
            build_context=build_context,
            design_library=mock_library,
            design_loader=mock_loader,
            design_report=mock_report,
            on_queue_changed=on_changed,
        )

    def test_per_resource_bottleneck_metals(self):
        """5500 Metals at 3000/turn, 1000 Organics at 3000/turn → ~1.83 turns from Metals."""
        design = MagicMock()
        design.design_id = "cruiser"
        design.construction_cost = {"metals": 5500, "organics": 1000}

        controller = self._make_controller_with_designs([design])
        build_rate = {"metals": 3000.0, "organics": 3000.0}
        turns = controller._calculate_build_turns("cruiser", build_rate)

        # 5500/3000 = 1.833..., 1000/3000 = 0.333... → max = 1.833...
        assert turns == pytest.approx(5500 / 3000)

    def test_per_resource_bottleneck_exotics(self):
        """Metals 3000/turn, Exotics 1500/turn with 3000 of each → Exotics bottleneck."""
        design = MagicMock()
        design.design_id = "advanced_ship"
        design.construction_cost = {"metals": 3000, "exotics": 3000}

        controller = self._make_controller_with_designs([design])
        build_rate = {"metals": 3000.0, "exotics": 1500.0}
        turns = controller._calculate_build_turns("advanced_ship", build_rate)

        # ceil(3000/3000) = 1, ceil(3000/1500) = 2 → max = 2
        assert turns == 2

    def test_resource_in_cost_not_in_rates_treated_as_unbounded(self):
        """Resource in cost but not in rates → only rated resources count."""
        design = MagicMock()
        design.design_id = "exotic_ship"
        design.construction_cost = {"metals": 2000, "vapors": 1000}

        controller = self._make_controller_with_designs([design])
        build_rate = {"metals": 3000.0}  # No Vapors rate
        turns = controller._calculate_build_turns("exotic_ship", build_rate)

        # Metals: 2000/3000 = 0.667, Vapors: not in rates (skipped) → max = 0.667
        assert turns == pytest.approx(2000 / 3000)

    def test_empty_build_rate_returns_1(self):
        """Empty build_rate dict returns 1 turn."""
        design = MagicMock()
        design.design_id = "ship"
        design.construction_cost = {"metals": 5000}

        controller = self._make_controller_with_designs([design])
        turns = controller._calculate_build_turns("ship", {})

        assert turns == 1

    def test_zero_rate_skipped_no_divide_by_zero(self):
        """Rate of 0 is skipped (no divide by zero)."""
        design = MagicMock()
        design.design_id = "ship"
        design.construction_cost = {"metals": 3000, "organics": 1000}

        controller = self._make_controller_with_designs([design])
        build_rate = {"metals": 3000.0, "organics": 0.0}
        turns = controller._calculate_build_turns("ship", build_rate)

        # Metals: ceil(3000/3000) = 1, Organics: rate 0 skipped → max = 1
        assert turns == 1

    def test_add_to_queue_with_dict_build_rate(self):
        """Adding to queue adds item via command callback.

        PROJ-208: Turns calculation moved to handler (default 1.0).
        """
        design = MagicMock()
        design.design_id = "cruiser"
        design.construction_cost = {"metals": 5500, "organics": 1000}

        entity_registry = {}
        controller = self._make_controller_with_designs([design])
        controller._add_to_queue_callback = _make_add_callback(entity_registry)

        source = _make_source(build_rate={"metals": 3000.0, "organics": 3000.0}, entity_registry=entity_registry)
        controller.set_active_queue(source)

        controller.add_to_queue("cruiser", category="ship")

        item = source.construction_queue[0]
        # PROJ-208: Handler uses default turns_remaining (1.0)
        assert item["turns_remaining"] == 1.0

    def test_multi_queue_different_per_resource_rates(self):
        """Multi-queue adds items to all selected queues.

        PROJ-208: Turns calculation moved to handler (default 1.0).
        """
        design = MagicMock()
        design.design_id = "cruiser"
        design.construction_cost = {"metals": 6000, "exotics": 3000}

        entity_registry = {}
        controller = self._make_controller_with_designs([design])
        controller._add_to_queue_callback = _make_add_callback(entity_registry)

        # Standard yard: all at 3000
        standard = _make_source(
            queue_id="standard",
            build_rate={"metals": 3000.0, "exotics": 3000.0},
            entity_registry=entity_registry,
        )
        # Advanced yard: Metals 3000, but Exotics 1500
        advanced = _make_source(
            queue_id="advanced",
            build_rate={"metals": 3000.0, "exotics": 1500.0},
            entity_registry=entity_registry,
        )
        controller.set_selected_queues([standard, advanced])

        controller.add_to_queue("cruiser", category="ship")

        # PROJ-208: Handler uses default turns_remaining (1.0) for all queues
        assert standard.construction_queue[0]["turns_remaining"] == 1.0
        assert advanced.construction_queue[0]["turns_remaining"] == 1.0
