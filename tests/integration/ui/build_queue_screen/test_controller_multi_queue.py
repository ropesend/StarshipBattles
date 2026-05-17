"""
Tests for BuildQueueController multi-queue support (PROJ-69 Phase 4).

Tests cover:
- Single-queue add via active_queue_source
- Multi-queue add to multiple selected queue sources
- Multi-queue add skips queues that can't build the selected type
- set_active_queue and set_selected_queues methods

PROJ-208: Updated to inject add_to_queue_callback for command-based mutation.
"""

import pytest
from unittest.mock import MagicMock, call
from game.ui.panels.build_queue_controller import BuildQueueController
from game.strategy.data.build_queue_source import BuildQueueSource
from typing import Optional


def _make_add_callback(entity_registry: dict):
    """Create an add_to_queue_callback that resolves queues from a registry.

    PROJ-208: Simulates what session.handle_command does for AddToConstructionQueueCommand.
    """
    def callback(
        entity_id: int,
        entity_type: str,
        design_id: str,
        category: str,
        index: Optional[int],
        target_planet_id: Optional[int],
        queue_id: Optional[str],
    ) -> None:
        # Lookup entity from registry
        entity = entity_registry.get((entity_type, entity_id))
        if entity is None:
            return  # Entity not found

        # Resolve queue
        queue = None
        if queue_id is None:
            queue = getattr(entity, 'construction_queue', None)
        else:
            # Check facilities for matching instance_id
            if hasattr(entity, 'facilities'):
                for fac in entity.facilities:
                    if getattr(fac, 'instance_id', None) == queue_id:
                        queue = getattr(fac, 'construction_queue', None)
                        break
            # Fallback to entity's main queue
            if queue is None:
                queue = getattr(entity, 'construction_queue', None)

        if queue is None:
            return

        # Build queue item
        item = {
            "design_id": design_id,
            "type": category,
            "turns_remaining": 1.0,
            "total_cost": {},
            "resources_consumed": {},
        }
        if target_planet_id is not None:
            item["target_planet_id"] = target_planet_id

        # Insert or append
        if index is not None:
            queue.insert(index, item)
        else:
            queue.append(item)

    return callback


@pytest.fixture
def mock_dependencies():
    """Create mock dependencies for BuildQueueController."""
    build_context = MagicMock()
    build_context.context_type = "planet"
    build_context.has_space_shipyard = True
    build_context.construction_queue = []
    build_context.facilities = []
    build_context.can_build_type.return_value = True
    build_context.id = 1  # PROJ-208: Needed for callback

    design_catalog = MagicMock()
    design_catalog.scan_designs.return_value = []
    design_catalog.designs_folder = "test"

    design_loader = MagicMock()
    design_report = MagicMock()
    on_queue_changed = MagicMock()

    # PROJ-208: Entity registry for callback
    entity_registry = {("planet", 1): build_context}

    return {
        "build_context": build_context,
        "design_catalog": design_catalog,
        "design_loader": design_loader,
        "design_report": design_report,
        "on_queue_changed": on_queue_changed,
        "entity_registry": entity_registry,
    }


@pytest.fixture
def controller(mock_dependencies):
    """Create a BuildQueueController instance."""
    return BuildQueueController(
        build_context=mock_dependencies["build_context"],
        design_catalog=mock_dependencies["design_catalog"],
        design_loader=mock_dependencies["design_loader"],
        design_report=mock_dependencies["design_report"],
        on_queue_changed=mock_dependencies["on_queue_changed"],
        add_to_queue_callback=_make_add_callback(mock_dependencies["entity_registry"]),
    )


@pytest.fixture
def queue_sources(mock_dependencies):
    """Create test BuildQueueSource instances.

    PROJ-208: Set up owner_entity with IDs and register in entity_registry.
    """
    base_queue = []
    shipyard_queue = []
    fleet_queue = []

    # Create owner entities with IDs
    planet_entity = MagicMock()
    planet_entity.id = 10
    planet_entity.construction_queue = base_queue
    planet_entity.facilities = []

    fleet_entity = MagicMock()
    fleet_entity.id = 20
    fleet_entity.construction_queue = fleet_queue
    fleet_entity.facilities = []

    # Register in entity_registry for callback lookup
    entity_registry = mock_dependencies["entity_registry"]
    entity_registry[("planet", 10)] = planet_entity
    entity_registry[("fleet", 20)] = fleet_entity

    base_source = BuildQueueSource(
        queue_id="planet_10_base",
        display_name="Colony - Base",
        owner_entity=planet_entity,
        construction_queue=base_queue,
        can_build_ships=False,
        can_build_complexes=True,
        context_type="planet",
        planet_id=10,
    )

    # Shipyard source shares the same planet entity but has its own queue
    shipyard_source = BuildQueueSource(
        queue_id="shipyard_1",
        display_name="Colony - Shipyard 1",
        owner_entity=planet_entity,
        construction_queue=shipyard_queue,
        can_build_ships=True,
        can_build_complexes=True,
        context_type="planet",
        planet_id=10,
    )
    # Add shipyard as a facility so callback can resolve it
    shipyard_facility = MagicMock()
    shipyard_facility.instance_id = "shipyard_1"
    shipyard_facility.construction_queue = shipyard_queue
    planet_entity.facilities.append(shipyard_facility)

    fleet_source = BuildQueueSource(
        queue_id="fleet_1",
        display_name="Fleet Alpha - Space Yard",
        owner_entity=fleet_entity,
        construction_queue=fleet_queue,
        can_build_ships=True,
        can_build_complexes=True,
        context_type="fleet",
    )

    return base_source, shipyard_source, fleet_source


# --- Single-queue add tests ---

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


def test_add_to_single_queue_source(controller, queue_sources):
    """Test adding to a single active queue source."""
    base_source, shipyard_source, _ = queue_sources
    controller.set_active_queue(shipyard_source)

    controller.add_to_queue("frigate_mk1", turns=3, category="ship")

    assert len(shipyard_source.construction_queue) == 1
    assert shipyard_source.construction_queue[0]["design_id"] == "frigate_mk1"
    # PROJ-208: Handler uses default 1.0 turns
    assert shipyard_source.construction_queue[0]["turns_remaining"] == 1.0


def test_add_to_single_queue_source_complex(controller, queue_sources):
    """Test adding a complex to a base queue source."""
    base_source, _, _ = queue_sources
    controller.set_active_queue(base_source)

    controller.add_to_queue("mining_complex_mk1", turns=5, category="complex")

    assert len(base_source.construction_queue) == 1
    assert base_source.construction_queue[0]["design_id"] == "mining_complex_mk1"


# --- Multi-queue add tests ---

def test_add_to_multiple_queue_sources(controller, queue_sources):
    """Test adding to all selected queue sources in multi-select mode."""
    _, shipyard_source, fleet_source = queue_sources
    controller.set_selected_queues([shipyard_source, fleet_source])

    controller.add_to_queue("frigate_mk1", turns=3, category="ship")

    # Both queues should have the item
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
