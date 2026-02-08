"""
Tests for BuildQueueController multi-queue operations.

PROJ-69 Phase 6: Verifies single-queue, multi-queue, and fallback add behavior,
including can_build_ships/can_build_complexes compatibility filtering.
"""
import pytest
from unittest.mock import MagicMock

from game.ui.panels.build_queue_controller import BuildQueueController
from game.strategy.data.build_queue_source import BuildQueueSource


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


def _make_source(
    queue_id: str = "test_queue",
    display_name: str = "Test Queue",
    can_build_ships: bool = True,
    can_build_complexes: bool = True,
    queue: list = None,
) -> BuildQueueSource:
    """Create a BuildQueueSource with a real mutable queue."""
    actual_queue = queue if queue is not None else []
    return BuildQueueSource(
        queue_id=queue_id,
        display_name=display_name,
        owner_entity=MagicMock(),
        construction_queue=actual_queue,
        can_build_ships=can_build_ships,
        can_build_complexes=can_build_complexes,
        context_type="planet",
    )


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
