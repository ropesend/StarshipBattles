"""
Tests for BuildQueueController multi-queue operations.

PROJ-69 Phase 6: Verifies single-queue, multi-queue, and fallback add behavior,
including can_build_ships/can_build_complexes compatibility filtering.

PROJ-79 Phase 2: Added tests for build time calculation and cost tracking.
"""
import pytest
from unittest.mock import MagicMock

from game.ui.panels.build_queue_controller import BuildQueueController
from game.strategy.data.build_queue_source import BuildQueueSource, get_default_production_rates


def _make_controller(build_context=None) -> BuildQueueController:
    """Create a controller with mock dependencies."""
    if build_context is None:
        build_context = MagicMock()
        build_context.context_type = "planet"
        build_context.has_space_shipyard = True
        build_context.can_build_type.return_value = True
        build_context.construction_queue = []

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
    )


def _default_build_rate() -> dict:
    """Return default build rate dict for testing."""
    return {"Metals": 2000.0, "Organics": 2000.0, "Radioactives": 2000.0, "Vapors": 2000.0, "Exotics": 2000.0}


def _make_source(
    queue_id: str = "test_queue",
    display_name: str = "Test Queue",
    can_build_ships: bool = True,
    can_build_complexes: bool = True,
    queue: list = None,
    build_rate: dict = None,
    context_type: str = "planet",
    planet_id: int = None,
) -> BuildQueueSource:
    """Create a BuildQueueSource with a real mutable queue."""
    actual_queue = queue if queue is not None else []
    actual_rate = build_rate if build_rate is not None else _default_build_rate()
    source = BuildQueueSource(
        queue_id=queue_id,
        display_name=display_name,
        owner_entity=MagicMock(),
        construction_queue=actual_queue,
        can_build_ships=can_build_ships,
        can_build_complexes=can_build_complexes,
        context_type=context_type,
        build_rate=actual_rate,
        planet_id=planet_id,
    )
    return source


class TestControllerSingleQueueAdd:
    """Tests for single-queue add behavior."""

    def test_add_to_single_active_queue(self):
        """Adding to queue when active_queue_source is set targets that source."""
        controller = _make_controller()
        source = _make_source(queue_id="yard_1", display_name="Shipyard 1")
        controller.set_active_queue(source)

        controller.add_to_queue("scout_ship", turns=3, category="ship")

        assert len(source.construction_queue) == 1
        item = source.construction_queue[0]
        assert item["design_id"] == "scout_ship"
        assert item["type"] == "ship"
        assert item["turns_remaining"] == 3

    def test_add_incompatible_category_to_single_queue_rejected(self):
        """Ship category rejected by queue that can't build ships."""
        controller = _make_controller()
        source = _make_source(can_build_ships=False, can_build_complexes=True)
        controller.set_active_queue(source)

        controller.add_to_queue("scout_ship", turns=3, category="ship")

        assert len(source.construction_queue) == 0  # Rejected

    def test_add_complex_to_base_queue(self):
        """Complex category accepted by base queue (ships=False, complexes=True)."""
        controller = _make_controller()
        source = _make_source(
            queue_id="base",
            can_build_ships=False,
            can_build_complexes=True,
        )
        controller.set_active_queue(source)

        controller.add_to_queue("factory", turns=5, category="complex")

        assert len(source.construction_queue) == 1
        assert source.construction_queue[0]["type"] == "complex"

    def test_add_with_index_inserts_at_position(self):
        """Adding with index inserts at specified position."""
        controller = _make_controller()
        existing_queue = [
            {"design_id": "item_a", "type": "ship", "turns_remaining": 3},
            {"design_id": "item_b", "type": "ship", "turns_remaining": 5},
        ]
        source = _make_source(queue=existing_queue)
        controller.set_active_queue(source)

        controller.add_to_queue("item_c", turns=2, category="ship", index=1)

        assert len(source.construction_queue) == 3
        assert source.construction_queue[1]["design_id"] == "item_c"


class TestControllerMultiQueueAdd:
    """Tests for multi-queue add behavior."""

    def test_add_to_all_selected_queues(self):
        """Adding in multi-select mode adds to all selected queues."""
        controller = _make_controller()
        source1 = _make_source(queue_id="yard_1")
        source2 = _make_source(queue_id="yard_2")
        controller.set_selected_queues([source1, source2])

        controller.add_to_queue("cruiser", turns=8, category="ship")

        assert len(source1.construction_queue) == 1
        assert len(source2.construction_queue) == 1
        assert source1.construction_queue[0]["design_id"] == "cruiser"
        assert source2.construction_queue[0]["design_id"] == "cruiser"

    def test_multi_add_skips_incompatible_queues(self):
        """Multi-add skips queues that can't build the category."""
        controller = _make_controller()
        base_queue = _make_source(
            queue_id="base",
            display_name="Base",
            can_build_ships=False,
            can_build_complexes=True,
        )
        yard_queue = _make_source(
            queue_id="yard_1",
            display_name="Shipyard 1",
            can_build_ships=True,
            can_build_complexes=True,
        )
        controller.set_selected_queues([base_queue, yard_queue])

        controller.add_to_queue("destroyer", turns=6, category="ship")

        # Base queue can't build ships - skipped
        assert len(base_queue.construction_queue) == 0
        # Shipyard queue can build ships - added
        assert len(yard_queue.construction_queue) == 1

    def test_multi_add_complex_to_all_compatible(self):
        """Multi-add complex adds to all queues that support complexes."""
        controller = _make_controller()
        base_queue = _make_source(
            queue_id="base",
            can_build_ships=False,
            can_build_complexes=True,
        )
        yard_queue = _make_source(
            queue_id="yard_1",
            can_build_ships=True,
            can_build_complexes=True,
        )
        controller.set_selected_queues([base_queue, yard_queue])

        controller.add_to_queue("factory", turns=4, category="complex")

        # Both can build complexes
        assert len(base_queue.construction_queue) == 1
        assert len(yard_queue.construction_queue) == 1

    def test_multi_add_fighter_respects_ship_flag(self):
        """Fighter category uses can_build_ships flag."""
        controller = _make_controller()
        base_queue = _make_source(can_build_ships=False, can_build_complexes=True)
        yard_queue = _make_source(can_build_ships=True, can_build_complexes=True)
        controller.set_selected_queues([base_queue, yard_queue])

        controller.add_to_queue("interceptor", turns=2, category="fighter")

        assert len(base_queue.construction_queue) == 0  # Skipped
        assert len(yard_queue.construction_queue) == 1  # Added

    def test_multi_add_satellite_respects_ship_flag(self):
        """Satellite category uses can_build_ships flag."""
        controller = _make_controller()
        base_queue = _make_source(can_build_ships=False, can_build_complexes=True)
        yard_queue = _make_source(can_build_ships=True, can_build_complexes=True)
        controller.set_selected_queues([base_queue, yard_queue])

        controller.add_to_queue("comm_sat", turns=1, category="satellite")

        assert len(base_queue.construction_queue) == 0
        assert len(yard_queue.construction_queue) == 1


class TestControllerModeTransitions:
    """Tests for controller mode transitions."""

    def test_set_active_queue_clears_multi_select(self):
        """Setting active queue clears multi-select."""
        controller = _make_controller()
        controller.set_selected_queues([_make_source(), _make_source()])
        assert len(controller.selected_queue_sources) == 2

        controller.set_active_queue(_make_source())

        assert controller.active_queue_source is not None
        assert len(controller.selected_queue_sources) == 0

    def test_set_selected_queues_clears_active(self):
        """Setting multi-select clears active queue."""
        controller = _make_controller()
        controller.set_active_queue(_make_source())
        assert controller.active_queue_source is not None

        controller.set_selected_queues([_make_source()])

        assert controller.active_queue_source is None
        assert len(controller.selected_queue_sources) == 1

    def test_fallback_to_build_context_when_no_source(self):
        """Falls back to build_context when neither source is set."""
        build_context = MagicMock()
        build_context.context_type = "planet"
        build_context.has_space_shipyard = True
        build_context.can_build_type.return_value = True
        build_context.construction_queue = []

        controller = _make_controller(build_context=build_context)
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

        # Build design_id -> resource_cost map for mocking
        design_costs = {}
        for d in designs:
            design_costs[d.design_id] = d.resource_cost

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
        design.resource_cost = {"Metals": 100000, "Organics": 10000}

        controller = self._make_controller_with_designs([design])
        build_rate = {"Metals": 2000.0, "Organics": 2000.0}
        turns = controller._calculate_build_turns("big_complex", build_rate)

        assert turns == 50  # ceil(100000/2000) = 50, ceil(10000/2000) = 5 → max = 50

    def test_calculate_build_turns_shipyard_rate(self):
        """6000 Metals at 3000/turn = 2 turns."""
        design = MagicMock()
        design.design_id = "cruiser"
        design.resource_cost = {"Metals": 6000}

        controller = self._make_controller_with_designs([design])
        build_rate = {"Metals": 3000.0}
        turns = controller._calculate_build_turns("cruiser", build_rate)

        assert turns == 2  # 6000 / 3000 = 2

    def test_calculate_build_turns_zero_cost_returns_1(self):
        """Zero-cost design returns 1 turn minimum."""
        design = MagicMock()
        design.design_id = "free_stuff"
        design.resource_cost = {}

        controller = self._make_controller_with_designs([design])
        build_rate = {"Metals": 2000.0}
        turns = controller._calculate_build_turns("free_stuff", build_rate)

        assert turns == 1

    def test_calculate_build_turns_no_resource_cost_returns_1(self):
        """Design with no resource_cost attribute returns 1 turn."""
        design = MagicMock()
        design.design_id = "no_cost"
        design.resource_cost = None

        controller = self._make_controller_with_designs([design])
        build_rate = {"Metals": 2000.0}
        turns = controller._calculate_build_turns("no_cost", build_rate)

        assert turns == 1

    def test_calculate_build_turns_unknown_design_returns_1(self):
        """Unknown design ID returns 1 turn."""
        controller = self._make_controller_with_designs([])
        build_rate = {"Metals": 2000.0}
        turns = controller._calculate_build_turns("unknown", build_rate)

        assert turns == 1

    def test_build_cost_tracking_fields_created(self):
        """_build_cost_tracking creates required fields for dynamic engine."""
        design = MagicMock()
        design.design_id = "factory"
        design.resource_cost = {"Metals": 4000, "Organics": 2000}

        controller = self._make_controller_with_designs([design])
        tracking = controller._build_cost_tracking("factory")

        # Dynamic engine uses total_cost and resources_consumed
        # Per-tick rates calculated dynamically from production_rates.json
        assert tracking["total_cost"] == {"Metals": 4000, "Organics": 2000}
        assert tracking["resources_consumed"] == {"Metals": 0.0, "Organics": 0.0}

    def test_add_to_queue_creates_cost_tracking(self):
        """Adding to queue without turns creates cost tracking fields."""
        design = MagicMock()
        design.design_id = "factory"
        design.resource_cost = {"Metals": 4000}

        controller = self._make_controller_with_designs([design])
        source = _make_source(build_rate={"Metals": 2000.0})
        controller.set_active_queue(source)

        controller.add_to_queue("factory", category="complex")

        item = source.construction_queue[0]
        assert item["turns_remaining"] == 2.0  # 4000 / 2000 = 2.0 (exact float)
        assert "total_cost" in item
        assert "resources_consumed" in item

    def test_add_to_queue_uses_source_build_rate(self):
        """Build time calculated using source's build_rate."""
        design = MagicMock()
        design.design_id = "cruiser"
        design.resource_cost = {"Metals": 9000}

        controller = self._make_controller_with_designs([design])
        source = _make_source(build_rate={"Metals": 3000.0})  # Shipyard rate
        controller.set_active_queue(source)

        controller.add_to_queue("cruiser", category="ship")

        item = source.construction_queue[0]
        assert item["turns_remaining"] == 3  # 9000 / 3000 = 3

    def test_multi_queue_add_uses_per_source_build_rate(self):
        """Multi-queue add calculates turns per source."""
        design = MagicMock()
        design.design_id = "cruiser"
        design.resource_cost = {"Metals": 6000}

        controller = self._make_controller_with_designs([design])
        slow_source = _make_source(queue_id="slow", build_rate={"Metals": 2000.0})
        fast_source = _make_source(queue_id="fast", build_rate={"Metals": 3000.0})
        controller.set_selected_queues([slow_source, fast_source])

        controller.add_to_queue("cruiser", category="ship")

        assert slow_source.construction_queue[0]["turns_remaining"] == 3  # 6000/2000
        assert fast_source.construction_queue[0]["turns_remaining"] == 2  # 6000/3000

    def test_fallback_uses_planetary_yard_rate(self):
        """Fallback mode uses PLANETARY_YARD_BUILD_RATE."""
        design = MagicMock()
        design.design_id = "factory"
        design.resource_cost = {"Metals": 4000}

        build_context = MagicMock()
        build_context.context_type = "planet"
        build_context.has_space_shipyard = True
        build_context.can_build_type.return_value = True
        build_context.construction_queue = []

        mock_library = MagicMock()
        mock_library.scan_designs.return_value = [design]
        mock_library.load_design_data.return_value = {"design_id": "factory"}

        # Mock loader to return ship with construction_cost
        mock_loader = MagicMock()
        mock_ship = MagicMock()
        mock_ship.construction_cost = {"Metals": 4000}
        mock_loader.load_ship_from_design_data.return_value = mock_ship

        controller = BuildQueueController(
            build_context=build_context,
            design_library=mock_library,
            design_loader=mock_loader,
            design_report=MagicMock(),
            on_queue_changed=MagicMock(),
        )

        controller.add_to_queue("factory", category="complex")

        item = build_context.construction_queue[0]
        assert item["turns_remaining"] == 2  # 4000 / 2000 = 2


class TestPlanetSelectionForFleetComplexes:
    """PROJ-79 Phase 4: Tests for planet selection when fleet adds complex at multi-colony hex."""

    def _make_fleet_controller_with_galaxy(
        self,
        hex_coord,
        galaxy,
        empire,
        planets_at_hex: list,
    ) -> BuildQueueController:
        """Create controller with fleet source and galaxy context."""
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
        """Adding complex at single-colony hex auto-sets target_planet_id."""
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

        source = _make_source(context_type="fleet", build_rate={"Metals": 2000.0})
        source.context_type = "fleet"
        source.planet_id = None
        controller.set_active_queue(source)

        controller.add_to_queue("factory", category="complex")

        # Should have added directly with target_planet_id
        assert len(source.construction_queue) == 1
        item = source.construction_queue[0]
        assert item.get("target_planet_id") == 10

    def test_add_complex_planet_source_uses_planet_id(self):
        """Adding complex via planet source uses source.planet_id."""
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

        source = _make_source(context_type="planet", build_rate={"Metals": 2000.0})
        source.context_type = "planet"
        source.planet_id = 10
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

        # Build design_id -> resource_cost map for mocking
        design_costs = {}
        for d in designs:
            design_costs[d.design_id] = d.resource_cost

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
        design.resource_cost = {"Metals": 5500, "Organics": 1000}

        controller = self._make_controller_with_designs([design])
        build_rate = {"Metals": 3000.0, "Organics": 3000.0}
        turns = controller._calculate_build_turns("cruiser", build_rate)

        # 5500/3000 = 1.833..., 1000/3000 = 0.333... → max = 1.833...
        assert turns == pytest.approx(5500 / 3000)

    def test_per_resource_bottleneck_exotics(self):
        """Metals 3000/turn, Exotics 1500/turn with 3000 of each → Exotics bottleneck."""
        design = MagicMock()
        design.design_id = "advanced_ship"
        design.resource_cost = {"Metals": 3000, "Exotics": 3000}

        controller = self._make_controller_with_designs([design])
        build_rate = {"Metals": 3000.0, "Exotics": 1500.0}
        turns = controller._calculate_build_turns("advanced_ship", build_rate)

        # ceil(3000/3000) = 1, ceil(3000/1500) = 2 → max = 2
        assert turns == 2

    def test_resource_in_cost_not_in_rates_treated_as_unbounded(self):
        """Resource in cost but not in rates → only rated resources count."""
        design = MagicMock()
        design.design_id = "exotic_ship"
        design.resource_cost = {"Metals": 2000, "Vapors": 1000}

        controller = self._make_controller_with_designs([design])
        build_rate = {"Metals": 3000.0}  # No Vapors rate
        turns = controller._calculate_build_turns("exotic_ship", build_rate)

        # Metals: 2000/3000 = 0.667, Vapors: not in rates (skipped) → max = 0.667
        assert turns == pytest.approx(2000 / 3000)

    def test_empty_build_rate_returns_1(self):
        """Empty build_rate dict returns 1 turn."""
        design = MagicMock()
        design.design_id = "ship"
        design.resource_cost = {"Metals": 5000}

        controller = self._make_controller_with_designs([design])
        turns = controller._calculate_build_turns("ship", {})

        assert turns == 1

    def test_zero_rate_skipped_no_divide_by_zero(self):
        """Rate of 0 is skipped (no divide by zero)."""
        design = MagicMock()
        design.design_id = "ship"
        design.resource_cost = {"Metals": 3000, "Organics": 1000}

        controller = self._make_controller_with_designs([design])
        build_rate = {"Metals": 3000.0, "Organics": 0.0}
        turns = controller._calculate_build_turns("ship", build_rate)

        # Metals: ceil(3000/3000) = 1, Organics: rate 0 skipped → max = 1
        assert turns == 1

    def test_add_to_queue_with_dict_build_rate(self):
        """Adding to queue calculates turns using Dict build_rate."""
        design = MagicMock()
        design.design_id = "cruiser"
        design.resource_cost = {"Metals": 5500, "Organics": 1000}

        controller = self._make_controller_with_designs([design])
        source = _make_source(build_rate={"Metals": 3000.0, "Organics": 3000.0})
        controller.set_active_queue(source)

        controller.add_to_queue("cruiser", category="ship")

        item = source.construction_queue[0]
        # 5500 Metals / 3000 = 1.833... turns (exact float for tick-based production)
        assert item["turns_remaining"] == pytest.approx(5500 / 3000)

    def test_multi_queue_different_per_resource_rates(self):
        """Multi-queue with different per-resource rates."""
        design = MagicMock()
        design.design_id = "cruiser"
        design.resource_cost = {"Metals": 6000, "Exotics": 3000}

        controller = self._make_controller_with_designs([design])
        # Standard yard: all at 3000
        standard = _make_source(
            queue_id="standard",
            build_rate={"Metals": 3000.0, "Exotics": 3000.0}
        )
        # Advanced yard: Metals 3000, but Exotics 1500
        advanced = _make_source(
            queue_id="advanced",
            build_rate={"Metals": 3000.0, "Exotics": 1500.0}
        )
        controller.set_selected_queues([standard, advanced])

        controller.add_to_queue("cruiser", category="ship")

        # Standard: Metals ceil(6000/3000)=2, Exotics ceil(3000/3000)=1 → 2 turns
        assert standard.construction_queue[0]["turns_remaining"] == 2
        # Advanced: Metals ceil(6000/3000)=2, Exotics ceil(3000/1500)=2 → 2 turns
        assert advanced.construction_queue[0]["turns_remaining"] == 2
