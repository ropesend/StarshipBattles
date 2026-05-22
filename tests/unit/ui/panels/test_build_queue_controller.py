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
from game.strategy.data.build_queue_source import get_default_production_rates
# PROJ-472 Phase 1B: controller consumes BuildQueueSourceDTO from the facade.
from game.strategy.facade.dto import BuildQueueSourceDTO as BuildQueueSource
from game.strategy.systems.design_repository import DesignLoadResult


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
        design_catalog=mock_library,
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
    """Create a BuildQueueSourceDTO with a real mutable queue.

    PROJ-472 Phase 1B: the controller consumes the DTO, so this builds a
    ``BuildQueueSourceDTO`` directly. ``entity_id`` is the owner id; planet
    sources also carry ``planet_id``. The entity_registry contract is kept
    (keyed by planet_id for planets / entity_id for fleets) to match
    ``_get_entity_info``.
    """
    global _entity_id_counter
    _entity_id_counter += 1

    actual_queue = queue if queue is not None else []
    actual_rate = build_rate if build_rate is not None else _default_build_rate()

    entity_id = _entity_id_counter

    # For planet sources, use planet_id or generated id
    effective_planet_id = planet_id if planet_id is not None else (
        _entity_id_counter if context_type == "planet" else None
    )

    source = BuildQueueSource(
        queue_id=queue_id,
        display_name=display_name,
        entity_id=entity_id,
        construction_queue=actual_queue,
        can_build_ships=can_build_ships,
        can_build_complexes=can_build_complexes,
        context_type=context_type,
        build_rate=actual_rate,
        planet_id=effective_planet_id,
    )

    # PROJ-208: Register a stand-in entity for command-callback resolution.
    # For planets, key by planet_id; for fleets, key by entity_id —
    # matching _get_entity_info behavior.
    if entity_registry is not None:
        owner_entity = MagicMock()
        owner_entity.construction_queue = actual_queue
        owner_entity.id = entity_id
        if context_type == "planet":
            entity_registry[(context_type, effective_planet_id)] = owner_entity
        else:
            entity_registry[(context_type, entity_id)] = owner_entity

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


class TestMineRoutingToCorrectYard:
    """QA-OBS-4 secondary fix: mines must not be queued onto complex-only yards.

    Prior to this fix, the category 'mine' was in neither _SHIP_CATEGORIES
    nor _COMPLEX_CATEGORIES, so `_source_can_build_category` fell through to
    `return True` and the controller silently accepted the queue add. The
    production engine then stopped the queue with a STOP action at
    `_validate_queue_item` without emitting any event - the player saw
    nothing happen.
    """

    def test_mine_rejected_on_complex_only_yard(self):
        """A mine queued onto a base (complex-only) planetary yard must be
        rejected by the controller before reaching the engine."""
        entity_registry = {}
        controller = _make_controller(entity_registry=entity_registry)
        base_yard = _make_source(
            queue_id="base",
            display_name="Base Planetary Yard",
            can_build_ships=False,
            can_build_complexes=True,
            entity_registry=entity_registry,
        )
        controller.set_active_queue(base_yard)

        controller.add_to_queue("mine_mk1", turns=1, category="mine")

        # Rejection: nothing was added to the queue
        assert len(base_yard.construction_queue) == 0

    def test_mine_accepted_on_shipyard(self):
        """A mine queued onto a shipyard (can_build_ships=True) is accepted."""
        entity_registry = {}
        controller = _make_controller(entity_registry=entity_registry)
        shipyard = _make_source(
            queue_id="shipyard_1",
            display_name="Shipyard 1",
            can_build_ships=True,
            can_build_complexes=True,
            entity_registry=entity_registry,
        )
        controller.set_active_queue(shipyard)

        controller.add_to_queue("mine_mk1", turns=1, category="mine")

        assert len(shipyard.construction_queue) == 1
        assert shipyard.construction_queue[0]["design_id"] == "mine_mk1"

    def test_source_can_build_category_rejects_mine_on_complex_only(self):
        """Direct unit test on the predicate the controller uses for routing."""
        entity_registry = {}
        controller = _make_controller(entity_registry=entity_registry)
        base_yard = _make_source(
            can_build_ships=False,
            can_build_complexes=True,
            entity_registry=entity_registry,
        )
        assert controller._source_can_build_category(base_yard, "mine") is False

    def test_source_can_build_category_accepts_mine_on_shipyard(self):
        entity_registry = {}
        controller = _make_controller(entity_registry=entity_registry)
        yard = _make_source(
            can_build_ships=True,
            can_build_complexes=False,
            entity_registry=entity_registry,
        )
        assert controller._source_can_build_category(yard, "mine") is True

    def test_multi_add_mine_skips_complex_only_yard(self):
        """In multi-queue mode, a mine add must skip complex-only sources
        (same shape as fighter/satellite tests above)."""
        entity_registry = {}
        controller = _make_controller(entity_registry=entity_registry)
        base_queue = _make_source(
            can_build_ships=False, can_build_complexes=True,
            entity_registry=entity_registry,
        )
        yard_queue = _make_source(
            can_build_ships=True, can_build_complexes=True,
            entity_registry=entity_registry,
        )
        controller.set_selected_queues([base_queue, yard_queue])

        controller.add_to_queue("mine_mk1", turns=1, category="mine")

        assert len(base_queue.construction_queue) == 0
        assert len(yard_queue.construction_queue) == 1


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

        # Mock load_design_data to return DesignLoadResult
        def mock_load_design_data(design_id):
            if design_id in design_costs:
                return DesignLoadResult.ok({"design_id": design_id})
            return DesignLoadResult.not_found(design_id)
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
            design_catalog=mock_library,
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
        mock_library.load_design_data.return_value = DesignLoadResult.ok({"design_id": "factory"})

        # Mock loader to return ship with construction_cost
        mock_loader = MagicMock()
        mock_ship = MagicMock()
        mock_ship.construction_cost = {"metals": 4000}
        mock_loader.load_ship_from_design_data.return_value = mock_ship

        controller = BuildQueueController(
            build_context=build_context,
            design_catalog=mock_library,
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
            design_catalog=mock_library,
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
                return DesignLoadResult.ok({"design_id": design_id})
            return DesignLoadResult.not_found(design_id)
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
            design_catalog=mock_library,
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

class TestControllerRoleFiltering:
    """Tests for role filtering logic."""

    def _make_controller_with_designs(self, designs: list) -> BuildQueueController:
        build_context = MagicMock()
        build_context.context_type = "planet"
        build_context.has_space_shipyard = True
        build_context.can_build_type.return_value = True

        mock_library = MagicMock()
        mock_library.scan_designs.return_value = designs

        return BuildQueueController(
            build_context=build_context,
            design_catalog=mock_library,
            design_loader=MagicMock(),
            design_report=MagicMock(),
            on_queue_changed=MagicMock(),
        )

    def test_load_designs_returns_tuple_and_extracts_roles(self):
        """load_designs_by_category should return (designs, roles_list) and extract roles."""
        design1 = MagicMock()
        design1.design_role = "Escort"
        design1.vehicle_type = "Ship"
        design2 = MagicMock()
        design2.design_role = "Capital"
        design2.vehicle_type = "Ship"
        design3 = MagicMock()
        design3.design_role = "Escort"
        design3.vehicle_type = "Ship"
        
        controller = self._make_controller_with_designs([design1, design2, design3])
        
        # Act
        result = controller.load_designs_by_category("ship")
        
        # Assert - Result is a tuple now
        assert isinstance(result, tuple)
        assert len(result) == 2
        
        filtered_designs, roles = result
        assert len(filtered_designs) == 3
        # Should be sorted: ["Any", "Capital", "Escort"]
        assert roles == ["Any", "Capital", "Escort"]

    def test_load_designs_filters_by_selected_role(self):
        """If selected_role is not 'Any', it should filter the designs list."""
        design1 = MagicMock()
        design1.design_role = "Escort"
        design1.vehicle_type = "Ship"
        design2 = MagicMock()
        design2.design_role = "Capital"
        design2.vehicle_type = "Ship"
        
        controller = self._make_controller_with_designs([design1, design2])
        
        # Attempt to filter by "Capital"
        controller.set_role("Capital")
        filtered_designs, roles = controller.load_designs_by_category("ship")
        
        # The list should still contain all available roles
        assert roles == ["Any", "Capital", "Escort"]
        
        # But the design list should ONLY contain the Capital ship
        assert len(filtered_designs) == 1
        assert filtered_designs[0].design_role == "Capital"

    def test_load_designs_ignore_no_role(self):
        """Designs without a role are put under 'None' role behind the scenes but filter correctly under 'Any'."""
        design1 = MagicMock()
        design1.design_role = None
        design1.vehicle_type = "Ship"
        
        controller = self._make_controller_with_designs([design1])
        
        filtered_designs, roles = controller.load_designs_by_category("ship")
        assert "None" in roles
        assert "Any" in roles
        assert len(roles) == 2
        assert len(filtered_designs) == 1


# ===========================================================================
# PROJ-338 — Characterization Coverage Gaps
#
# These tests pin observable behavior in helper methods that the existing
# coverage skips: category-to-vehicle-type mapping defaults, _validate_designs
# branches, _calculate_build_turns formula corners, _get_design_cost error
# handling, refresh_design_report happy/error paths.
# ===========================================================================


class TestCharacterizationCoverageGaps:
    """PROJ-338: pin behavior in helper paths that the legacy tests skip."""

    @staticmethod
    def _make_controller(scan_designs=None, registries=None) -> BuildQueueController:
        build_context = MagicMock()
        build_context.context_type = "planet"
        build_context.has_space_shipyard = True
        build_context.can_build_type.return_value = True
        build_context.id = 1

        mock_library = MagicMock()
        mock_library.scan_designs.return_value = scan_designs or []

        return BuildQueueController(
            build_context=build_context,
            design_catalog=mock_library,
            design_loader=MagicMock(),
            design_report=MagicMock(),
            on_queue_changed=MagicMock(),
            registries=registries,
        )

    # --- B.1 — category / role filtering -----------------------------------

    def test_load_designs_filters_by_vehicle_type_complex(self):
        d1 = MagicMock()
        d1.vehicle_type = "Planetary Complex"
        d1.design_role = None
        d2 = MagicMock()
        d2.vehicle_type = "Ship"
        d2.design_role = None
        controller = self._make_controller([d1, d2])
        filtered, _roles = controller.load_designs_by_category("complex")
        assert filtered == [d1]

    def test_load_designs_filters_by_vehicle_type_mine(self):
        """PROJ-FMS-A Phase 1: mine category maps to vehicle_type='Mine'."""
        d_mine = MagicMock()
        d_mine.vehicle_type = "Mine"
        d_mine.design_role = None
        d_ship = MagicMock()
        d_ship.vehicle_type = "Ship"
        d_ship.design_role = None
        controller = self._make_controller([d_mine, d_ship])
        filtered, _roles = controller.load_designs_by_category("mine")
        assert filtered == [d_mine]

    def test_load_designs_unknown_category_defaults_to_ship(self):
        d_ship = MagicMock()
        d_ship.vehicle_type = "Ship"
        d_ship.design_role = None
        d_complex = MagicMock()
        d_complex.vehicle_type = "Planetary Complex"
        d_complex.design_role = None
        controller = self._make_controller([d_ship, d_complex])
        filtered, _ = controller.load_designs_by_category("not-a-real-category")
        # Type map fallback: unknown → "Ship"
        assert filtered == [d_ship]

    def test_load_designs_filters_by_role_when_not_any(self):
        d1 = MagicMock()
        d1.vehicle_type = "Ship"
        d1.design_role = "Capital"
        d2 = MagicMock()
        d2.vehicle_type = "Ship"
        d2.design_role = "Escort"
        controller = self._make_controller([d1, d2])
        controller.selected_role = "Capital"
        filtered, _ = controller.load_designs_by_category("ship")
        assert filtered == [d1]

    def test_load_designs_role_none_string_matches_designs_with_no_role(self):
        d_role = MagicMock()
        d_role.vehicle_type = "Ship"
        d_role.design_role = "Capital"
        d_no_role = MagicMock()
        d_no_role.vehicle_type = "Ship"
        d_no_role.design_role = None
        controller = self._make_controller([d_role, d_no_role])
        controller.selected_role = "None"
        filtered, _ = controller.load_designs_by_category("ship")
        # Special "None" path matches designs with no role
        assert filtered == [d_no_role]

    def test_set_category_resets_role_to_any_and_fires_callback(self):
        controller = self._make_controller([])
        controller.selected_role = "Capital"
        controller.set_category("complex")
        assert controller.selected_category == "complex"
        assert controller.selected_role == "Any"
        controller.on_queue_changed.assert_called()

    def test_set_role_fires_callback_does_not_reset_category(self):
        controller = self._make_controller([])
        controller.selected_category = "complex"
        controller.set_role("Capital")
        assert controller.selected_role == "Capital"
        # Category is preserved
        assert controller.selected_category == "complex"
        controller.on_queue_changed.assert_called()

    # --- B.2 — _validate_designs paths -------------------------------------

    def test_validate_designs_without_registries_marks_all_valid(self):
        controller = self._make_controller([], registries=None)
        d = MagicMock()
        controller._validate_designs([d])
        assert d.design_valid is True

    def test_validate_designs_with_load_failure_marks_invalid(self):
        registries = MagicMock()
        controller = self._make_controller([], registries=registries)
        d = MagicMock()
        d.design_id = "DSN-X"
        load_result = MagicMock()
        load_result.success = False
        controller.design_catalog.load_design_data.return_value = load_result
        # Patch DesignValidator so __init__ succeeds; validate is never reached
        # because load_result.success is False.
        from unittest.mock import patch
        with patch("game.strategy.services.design_validator.DesignValidator"):
            controller._validate_designs([d])
        assert d.design_valid is False

    def test_validate_designs_with_validator_exception_assumes_valid(self):
        """Broad-catch path: exception during validation falls back to True."""
        registries = MagicMock()
        controller = self._make_controller([], registries=registries)
        d = MagicMock()
        d.design_id = "DSN-X"
        # load_design_data raises → broad-catch sets design_valid=True
        controller.design_catalog.load_design_data.side_effect = RuntimeError("boom")
        from unittest.mock import patch
        with patch("game.strategy.services.design_validator.DesignValidator"):
            controller._validate_designs([d])
        assert d.design_valid is True

    # --- B.3 — _calculate_build_turns / _get_design_cost -------------------

    def test_calculate_build_turns_no_cost_returns_one(self):
        controller = self._make_controller([])
        # Make _get_design_cost return empty
        controller.design_catalog.load_design_data.return_value = MagicMock(success=False)
        turns = controller._calculate_build_turns("DSN-X", {"metals": 100.0})
        assert turns == 1.0

    def test_calculate_build_turns_no_rate_returns_one(self):
        controller = self._make_controller([])
        # Cost present but build_rate empty
        load_result = MagicMock()
        load_result.success = True
        load_result.data = {}
        controller.design_catalog.load_design_data.return_value = load_result
        ship = MagicMock()
        ship.construction_cost = {"metals": 100}
        controller.design_loader.load_ship_from_design_data.return_value = ship
        turns = controller._calculate_build_turns("DSN-X", {})
        assert turns == 1.0

    def test_calculate_build_turns_max_across_resources(self):
        """The bottleneck resource determines total turns."""
        controller = self._make_controller([])
        load_result = MagicMock()
        load_result.success = True
        load_result.data = {}
        controller.design_catalog.load_design_data.return_value = load_result
        ship = MagicMock()
        ship.construction_cost = {"metals": 100, "exotics": 50}
        controller.design_loader.load_ship_from_design_data.return_value = ship
        # metals: 100/10=10 turns, exotics: 50/100=0.5 turns → max=10
        turns = controller._calculate_build_turns("DSN-X", {"metals": 10.0, "exotics": 100.0})
        assert turns == 10.0

    def test_calculate_build_turns_zero_floor_at_001(self):
        """Tiny but >0 turns are floored at 0.01 by the max(0.01, ...) clamp."""
        controller = self._make_controller([])
        load_result = MagicMock()
        load_result.success = True
        load_result.data = {}
        controller.design_catalog.load_design_data.return_value = load_result
        ship = MagicMock()
        ship.construction_cost = {"metals": 1}
        controller.design_loader.load_ship_from_design_data.return_value = ship
        # cost=1, rate=10000 → 0.0001 turns → clamped to 0.01
        turns = controller._calculate_build_turns("DSN-X", {"metals": 10000.0})
        assert turns == 0.01

    def test_get_design_cost_load_failure_returns_empty_dict(self):
        controller = self._make_controller([])
        controller.design_catalog.load_design_data.return_value = MagicMock(success=False)
        cost = controller._get_design_cost("DSN-X")
        assert cost == {}

    def test_get_design_cost_oserror_caught_returns_empty_dict(self):
        """Broad-catch path on (OSError, ValueError, KeyError)."""
        controller = self._make_controller([])
        controller.design_catalog.load_design_data.side_effect = OSError("disk")
        cost = controller._get_design_cost("DSN-X")
        assert cost == {}

    # --- B.4 — refresh_design_report ---------------------------------------

    def test_refresh_design_report_load_failure_shows_placeholder(self):
        controller = self._make_controller([])
        controller.design_catalog.load_design_data.return_value = MagicMock(
            success=False, error="not found"
        )
        controller.refresh_design_report("DSN-X")
        controller.design_report.show_placeholder.assert_called_once()
        controller.design_report.update_design.assert_not_called()

    def test_refresh_design_report_ship_load_returns_none_shows_placeholder(self):
        controller = self._make_controller([])
        controller.design_catalog.load_design_data.return_value = MagicMock(success=True, data={})
        controller.design_loader.load_ship_from_design_data.return_value = None
        controller.refresh_design_report("DSN-X")
        controller.design_report.show_placeholder.assert_called_once()

    def test_refresh_design_report_success_calls_update_design(self):
        controller = self._make_controller([])
        controller.design_catalog.load_design_data.return_value = MagicMock(success=True, data={})
        ship = MagicMock()
        ship.name = "Frigate"
        controller.design_loader.load_ship_from_design_data.return_value = ship
        controller.refresh_design_report("DSN-X")
        controller.design_report.update_design.assert_called_once_with(ship)
        controller.design_report.show_placeholder.assert_not_called()

    def test_refresh_design_report_exception_shows_placeholder(self):
        """OSError/ValueError/KeyError inside the try-block triggers placeholder."""
        controller = self._make_controller([])
        controller.design_catalog.load_design_data.side_effect = ValueError("bad data")
        controller.refresh_design_report("DSN-X")
        controller.design_report.show_placeholder.assert_called_once()


# ===========================================================================
# PROJ-373 Phase 1 — Validation cache
#
# Cache `_validate_designs` results keyed by (design_id, file_mtime).
# Repeat calls hit the cache and skip both Ship.from_dict and validator.validate.
# ===========================================================================


class TestValidationCache:
    """PROJ-373 Phase 1: validation result cache on BuildQueueController."""

    @staticmethod
    def _make_controller_with_validator_spy(monkeypatch):
        """Build a controller and replace DesignValidator with a counted stub.

        Returns (controller, validator_call_counter) where the counter is a
        mutable dict {"count": int} incremented every time
        validator.validate(...) is called. Each `validate` call returns a
        result with `has_issues=False` so designs come back as valid.
        """
        from unittest.mock import patch
        from game.ui.panels.build_queue_controller import BuildQueueController

        registries = MagicMock()

        build_context = MagicMock()
        build_context.context_type = "planet"
        build_context.has_space_shipyard = True
        build_context.can_build_type.return_value = True
        build_context.id = 1

        mock_library = MagicMock()
        # Default load_design_data returns success with empty data
        mock_library.load_design_data.return_value = MagicMock(success=True, data={})
        # Sensible default fingerprint for the path-resolution helper
        mock_library.get_design_path.side_effect = lambda did: f"/fake/{did}.json"

        controller = BuildQueueController(
            build_context=build_context,
            design_catalog=mock_library,
            design_loader=MagicMock(),
            design_report=MagicMock(),
            on_queue_changed=MagicMock(),
            registries=registries,
        )

        counter = {"count": 0, "constructed": 0}

        class _StubValidator:
            def __init__(self, _registries):
                counter["constructed"] += 1

            def validate(self, _data):
                counter["count"] += 1
                return MagicMock(has_issues=False)

        # Patch the symbol *inside* the controller's import path (the
        # function-local `from ... import` creates a fresh binding each call).
        monkeypatch.setattr(
            "game.strategy.services.design_validator.DesignValidator",
            _StubValidator,
        )

        return controller, counter

    @staticmethod
    def _design(design_id: str):
        d = MagicMock()
        d.design_id = design_id
        return d

    # -- fingerprint helper --------------------------------------------------

    def test_fingerprint_returns_mtime_ns_for_existing_path(self, monkeypatch):
        controller, _ = self._make_controller_with_validator_spy(monkeypatch)
        fake_stat = MagicMock(st_mtime_ns=12345)
        monkeypatch.setattr("os.stat", lambda _path: fake_stat)
        assert controller._design_fingerprint("DSN-A") == 12345

    def test_fingerprint_returns_none_for_missing_file(self, monkeypatch):
        controller, _ = self._make_controller_with_validator_spy(monkeypatch)

        def _raise(_path):
            raise FileNotFoundError("nope")

        monkeypatch.setattr("os.stat", _raise)
        assert controller._design_fingerprint("DSN-A") is None

    def test_fingerprint_changes_when_mtime_changes(self, monkeypatch):
        controller, _ = self._make_controller_with_validator_spy(monkeypatch)
        current = {"mtime": 100}
        monkeypatch.setattr("os.stat", lambda _path: MagicMock(st_mtime_ns=current["mtime"]))
        first = controller._design_fingerprint("DSN-A")
        current["mtime"] = 200
        second = controller._design_fingerprint("DSN-A")
        assert first != second

    # -- validation cache ----------------------------------------------------

    def test_first_call_validates_each_design(self, monkeypatch):
        controller, counter = self._make_controller_with_validator_spy(monkeypatch)
        monkeypatch.setattr("os.stat", lambda _path: MagicMock(st_mtime_ns=1))
        d1 = self._design("DSN-1")
        d2 = self._design("DSN-2")
        controller._validate_designs([d1, d2])
        assert counter["count"] == 2
        assert d1.design_valid is True
        assert d2.design_valid is True

    def test_repeat_call_uses_cache(self, monkeypatch):
        controller, counter = self._make_controller_with_validator_spy(monkeypatch)
        monkeypatch.setattr("os.stat", lambda _path: MagicMock(st_mtime_ns=1))
        d1 = self._design("DSN-1")
        d2 = self._design("DSN-2")
        controller._validate_designs([d1, d2])
        controller._validate_designs([d1, d2])
        assert counter["count"] == 2  # Not 4
        assert d1.design_valid is True
        assert d2.design_valid is True

    def test_mtime_change_invalidates_one_entry(self, monkeypatch):
        controller, counter = self._make_controller_with_validator_spy(monkeypatch)
        # Per-design mtime: DSN-1 mtime stays at 1, DSN-2 changes from 1 → 2
        mtimes = {"DSN-1": 1, "DSN-2": 1}

        def _stat(path):
            for did, mt in mtimes.items():
                if did in path:
                    return MagicMock(st_mtime_ns=mt)
            return MagicMock(st_mtime_ns=0)

        monkeypatch.setattr("os.stat", _stat)
        d1 = self._design("DSN-1")
        d2 = self._design("DSN-2")
        controller._validate_designs([d1, d2])
        # First pass: 2 validate calls
        assert counter["count"] == 2
        # Mutate mtime for DSN-2
        mtimes["DSN-2"] = 2
        controller._validate_designs([d1, d2])
        # Only DSN-2 is re-validated
        assert counter["count"] == 3

    def test_validator_exception_does_not_poison_cache(self, monkeypatch):
        controller, counter = self._make_controller_with_validator_spy(monkeypatch)
        monkeypatch.setattr("os.stat", lambda _path: MagicMock(st_mtime_ns=1))

        # First call: load_design_data raises → broad-catch fallback (design_valid=True)
        controller.design_catalog.load_design_data.side_effect = RuntimeError("boom")
        d = self._design("DSN-1")
        controller._validate_designs([d])
        assert d.design_valid is True

        # Second call: load_design_data succeeds → must run validator (no stale cache)
        controller.design_catalog.load_design_data.side_effect = None
        controller.design_catalog.load_design_data.return_value = MagicMock(success=True, data={})
        d2 = self._design("DSN-1")
        controller._validate_designs([d2])
        assert counter["count"] == 1  # Validator ran on the second call only
        assert d2.design_valid is True

    def test_cache_survives_category_switch(self, monkeypatch):
        controller, counter = self._make_controller_with_validator_spy(monkeypatch)
        monkeypatch.setattr("os.stat", lambda _path: MagicMock(st_mtime_ns=1))
        # Simulate two category lists with overlap
        a = self._design("DSN-A")
        b = self._design("DSN-B")
        c = self._design("DSN-C")
        controller._validate_designs([a, b])
        controller._validate_designs([b, c])
        # Unique design_ids: A, B, C → 3 validate calls total
        assert counter["count"] == 3

    def test_load_failure_caches_invalid_result(self, monkeypatch):
        """Cache load-failure as design_valid=False so repeats don't re-attempt."""
        controller, counter = self._make_controller_with_validator_spy(monkeypatch)
        monkeypatch.setattr("os.stat", lambda _path: MagicMock(st_mtime_ns=1))
        controller.design_catalog.load_design_data.return_value = MagicMock(success=False)
        d1 = self._design("DSN-1")
        controller._validate_designs([d1])
        d2 = self._design("DSN-1")
        controller._validate_designs([d2])
        assert d1.design_valid is False
        assert d2.design_valid is False
        # load_design_data should be called once (cache hit on second call)
        assert controller.design_catalog.load_design_data.call_count == 1

    def test_validator_constructed_lazily_on_first_miss_only(self, monkeypatch):
        """DesignValidator is constructed at most once per controller, lazily."""
        controller, counter = self._make_controller_with_validator_spy(monkeypatch)
        monkeypatch.setattr("os.stat", lambda _path: MagicMock(st_mtime_ns=1))
        d1 = self._design("DSN-1")
        d2 = self._design("DSN-2")
        controller._validate_designs([d1, d2])
        controller._validate_designs([d1, d2])  # All cache hits
        # Only one DesignValidator instance constructed across both calls
        assert counter["constructed"] == 1

    def test_cache_hit_path_does_not_construct_validator(self, monkeypatch):
        """A pure cache-hit call must not construct a validator at all."""
        controller, counter = self._make_controller_with_validator_spy(monkeypatch)
        monkeypatch.setattr("os.stat", lambda _path: MagicMock(st_mtime_ns=1))
        d1 = self._design("DSN-1")
        controller._validate_designs([d1])
        assert counter["constructed"] == 1
        # Reset the controller's lazy validator and confirm a pure cache-hit
        # call doesn't reconstruct it.
        controller._validator = None
        controller._validate_designs([d1])
        assert counter["constructed"] == 1

    # -- reset_filters (Phase 2 prerequisite) -------------------------------

    def test_reset_filters_restores_defaults(self, monkeypatch):
        controller, _ = self._make_controller_with_validator_spy(monkeypatch)
        controller.selected_category = "ship"
        controller.selected_role = "Capital"
        controller.reset_filters()
        assert controller.selected_category == "complex"
        assert controller.selected_role == "Any"

    def test_reset_filters_does_not_fire_callback(self, monkeypatch):
        controller, _ = self._make_controller_with_validator_spy(monkeypatch)
        controller.on_queue_changed.reset_mock()
        controller.reset_filters()
        controller.on_queue_changed.assert_not_called()
