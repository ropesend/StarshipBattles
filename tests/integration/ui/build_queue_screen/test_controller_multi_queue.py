"""
Tests for BuildQueueController multi-queue support (PROJ-69 Phase 4).

Tests cover:
- Single-queue add via active_queue_source
- Multi-queue add to multiple selected queue sources
- Multi-queue add skips queues that can't build the selected type
- set_active_queue and set_selected_queues methods
"""

import pytest
from unittest.mock import MagicMock, call
from game.ui.panels.build_queue_controller import BuildQueueController
from game.strategy.data.build_queue_source import BuildQueueSource


@pytest.fixture
def mock_dependencies():
    """Create mock dependencies for BuildQueueController."""
    build_context = MagicMock()
    build_context.context_type = "planet"
    build_context.has_space_shipyard = True
    build_context.construction_queue = []
    build_context.facilities = []
    build_context.can_build_type.return_value = True

    design_library = MagicMock()
    design_library.scan_designs.return_value = []
    design_library.designs_folder = "test"

    design_loader = MagicMock()
    design_report = MagicMock()
    on_queue_changed = MagicMock()

    return {
        "build_context": build_context,
        "design_library": design_library,
        "design_loader": design_loader,
        "design_report": design_report,
        "on_queue_changed": on_queue_changed,
    }


@pytest.fixture
def controller(mock_dependencies):
    """Create a BuildQueueController instance."""
    return BuildQueueController(
        build_context=mock_dependencies["build_context"],
        design_library=mock_dependencies["design_library"],
        design_loader=mock_dependencies["design_loader"],
        design_report=mock_dependencies["design_report"],
        on_queue_changed=mock_dependencies["on_queue_changed"],
    )


@pytest.fixture
def queue_sources():
    """Create test BuildQueueSource instances."""
    base_queue = []
    shipyard_queue = []
    fleet_queue = []

    base_source = BuildQueueSource(
        queue_id="planet_1_base",
        display_name="Colony - Base",
        owner_entity=MagicMock(),
        construction_queue=base_queue,
        can_build_ships=False,
        can_build_complexes=True,
        context_type="planet",
    )

    shipyard_source = BuildQueueSource(
        queue_id="shipyard_1",
        display_name="Colony - Shipyard 1",
        owner_entity=MagicMock(),
        construction_queue=shipyard_queue,
        can_build_ships=True,
        can_build_complexes=True,
        context_type="planet",
    )

    fleet_source = BuildQueueSource(
        queue_id="fleet_1",
        display_name="Fleet Alpha - Space Yard",
        owner_entity=MagicMock(),
        construction_queue=fleet_queue,
        can_build_ships=True,
        can_build_complexes=True,
        context_type="fleet",
    )

    return base_source, shipyard_source, fleet_source


# --- Single-queue add tests ---

def test_add_to_single_queue_source(controller, queue_sources):
    """Test adding to a single active queue source."""
    base_source, shipyard_source, _ = queue_sources
    controller.set_active_queue(shipyard_source)

    controller.add_to_queue("frigate_mk1", turns=3, category="ship")

    assert len(shipyard_source.construction_queue) == 1
    assert shipyard_source.construction_queue[0]["design_id"] == "frigate_mk1"
    assert shipyard_source.construction_queue[0]["turns_remaining"] == 3


def test_add_to_single_queue_source_complex(controller, queue_sources):
    """Test adding a complex to a base queue source."""
    base_source, _, _ = queue_sources
    controller.set_active_queue(base_source)

    controller.add_to_queue("mining_complex_mk1", turns=5, category="complex")

    assert len(base_source.construction_queue) == 1
    assert base_source.construction_queue[0]["design_id"] == "mining_complex_mk1"


def test_add_to_single_queue_source_with_index(controller, queue_sources):
    """Test inserting at a specific position in the queue."""
    _, shipyard_source, _ = queue_sources
    controller.set_active_queue(shipyard_source)

    # Add two items, then insert at position 0
    controller.add_to_queue("frigate_mk1", turns=3, category="ship")
    controller.add_to_queue("cruiser_mk1", turns=5, category="ship")
    controller.add_to_queue("destroyer_mk1", turns=2, category="ship", index=0)

    assert shipyard_source.construction_queue[0]["design_id"] == "destroyer_mk1"
    assert len(shipyard_source.construction_queue) == 3


# --- Multi-queue add tests ---

def test_add_to_multiple_queue_sources(controller, queue_sources):
    """Test adding to all selected queue sources in multi-select mode."""
    _, shipyard_source, fleet_source = queue_sources
    controller.set_selected_queues([shipyard_source, fleet_source])

    controller.add_to_queue("frigate_mk1", turns=3, category="ship")

    assert len(shipyard_source.construction_queue) == 1
    assert len(fleet_source.construction_queue) == 1
    assert shipyard_source.construction_queue[0]["design_id"] == "frigate_mk1"
    assert fleet_source.construction_queue[0]["design_id"] == "frigate_mk1"


def test_multi_queue_add_skips_incompatible_queues(controller, queue_sources):
    """Test that multi-queue add skips queues that can't build the selected type."""
    base_source, shipyard_source, _ = queue_sources
    # Base queue can't build ships
    controller.set_selected_queues([base_source, shipyard_source])

    controller.add_to_queue("frigate_mk1", turns=3, category="ship")

    # Base queue should be skipped (can_build_ships=False)
    assert len(base_source.construction_queue) == 0
    # Shipyard should receive the item
    assert len(shipyard_source.construction_queue) == 1


def test_multi_queue_add_complexes_to_all(controller, queue_sources):
    """Test that all queues can receive complexes when they support it."""
    base_source, shipyard_source, fleet_source = queue_sources
    controller.set_selected_queues([base_source, shipyard_source, fleet_source])

    controller.add_to_queue("mining_complex_mk1", turns=5, category="complex")

    # All sources can build complexes
    assert len(base_source.construction_queue) == 1
    assert len(shipyard_source.construction_queue) == 1
    assert len(fleet_source.construction_queue) == 1


def test_multi_queue_add_triggers_callback(controller, mock_dependencies, queue_sources):
    """Test that on_queue_changed is called after multi-queue add."""
    _, shipyard_source, fleet_source = queue_sources
    controller.set_selected_queues([shipyard_source, fleet_source])

    mock_dependencies["on_queue_changed"].reset_mock()
    controller.add_to_queue("frigate_mk1", turns=3, category="ship")

    mock_dependencies["on_queue_changed"].assert_called()


# --- set_active_queue / set_selected_queues tests ---

def test_set_active_queue(controller, queue_sources):
    """Test set_active_queue sets the active source and clears multi-select."""
    base_source, shipyard_source, _ = queue_sources
    controller.set_active_queue(base_source)

    assert controller.active_queue_source is base_source
    assert controller.selected_queue_sources == []


def test_set_selected_queues(controller, queue_sources):
    """Test set_selected_queues sets multi-select list and clears active."""
    _, shipyard_source, fleet_source = queue_sources
    controller.set_selected_queues([shipyard_source, fleet_source])

    assert controller.active_queue_source is None
    assert len(controller.selected_queue_sources) == 2


def test_fallback_to_build_context_when_no_queue_source(controller, mock_dependencies):
    """Test that add_to_queue falls back to build_context when no queue source is set."""
    # Initially no active_queue_source and no selected_queue_sources
    # Should fall back to build_context
    controller.add_to_queue("mining_complex_mk1", turns=5, category="complex")

    assert len(mock_dependencies["build_context"].construction_queue) == 1
