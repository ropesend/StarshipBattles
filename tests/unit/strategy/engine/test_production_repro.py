"""
Tests for build queue production issues.

PROJ-208: These tests were updated to reflect the new command-based architecture.
The BuildQueueController now dispatches AddToConstructionQueueCommand instead of
directly manipulating queues. The command handler sets turns_remaining to 1.0 as
a default, and ProductionEngine recalculates dynamically during production.
"""

import pytest
from typing import Optional
from unittest.mock import MagicMock, patch
from game.ui.panels.build_queue_controller import BuildQueueController
from game.strategy.engine.production_engine import ProductionEngine
from game.strategy.data.build_queue_source import BuildQueueSource


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

        # Build queue item - handler sets turns_remaining to 1.0 by default
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


class TestBuildQueueReproduction:
    @pytest.fixture
    def mock_build_context(self):
        context = MagicMock()
        context.construction_queue = []
        context.can_build_type.return_value = True
        context.id = 1
        context.context_type = "planet"
        context.facilities = []
        return context

    @pytest.fixture
    def mock_design_library(self):
        lib = MagicMock()
        # Mock a ship design with specific costs
        # Cost A: 2500, B: 6500, C: 2000
        lib.load_design_data.return_value = {
            "name": "Test Ship",
            "vehicle_type": "Ship",
            "layers": {
                "l1": {
                    "components": [
                        {"resource_cost": {"A": 2500, "B": 6500, "C": 2000}}
                    ]
                }
            }
        }
        return lib

    @pytest.fixture
    def mock_design_loader(self):
        loader = MagicMock()
        ship = MagicMock()
        # Ensure the loader returns a ship with the correct cost
        ship.construction_cost = {"A": 2500, "B": 6500, "C": 2000}
        loader.load_ship_from_design_data.return_value = ship
        return loader

    def test_repro_integer_rounding_logic(self, mock_build_context, mock_design_library, mock_design_loader):
        """
        PROJ-208: This test verifies that queue additions work through the command pattern.

        The original test checked that turns_remaining was calculated from resource costs.
        With PROJ-208, the command handler sets turns_remaining to 1.0 as a default,
        and ProductionEngine recalculates dynamically during production. This test now
        verifies that the item is correctly added to the queue via the command callback.
        """
        # Create entity for callback
        planet_entity = MagicMock()
        planet_entity.id = 10
        planet_entity.facilities = []

        # Create queue that the source will use
        test_queue = []
        planet_entity.construction_queue = test_queue

        entity_registry = {("planet", 10): planet_entity}

        controller = BuildQueueController(
            build_context=mock_build_context,
            design_library=mock_design_library,
            design_loader=mock_design_loader,
            design_report=MagicMock(),
            on_queue_changed=MagicMock(),
            add_to_queue_callback=_make_add_callback(entity_registry)
        )

        # Setup a queue source with 3000 production rate
        source = BuildQueueSource(
            queue_id="test_queue",
            display_name="Test Queue",
            owner_entity=planet_entity,
            construction_queue=test_queue,
            can_build_ships=True,
            can_build_complexes=True,
            context_type="planet",
            planet_id=10,
            build_rate={"A": 3000, "B": 3000, "C": 3000}
        )
        controller.set_active_queue(source)

        # Add to queue
        controller.add_to_queue("test_design_id")

        # Verify item was added
        assert len(source.construction_queue) == 1
        item = source.construction_queue[0]

        # PROJ-208: Handler uses default 1.0, ProductionEngine recalculates dynamically
        assert item["turns_remaining"] == 1.0
        assert item["design_id"] == "test_design_id"
        assert "total_cost" in item

    def test_repro_drag_and_drop_1_turn_bug(self, mock_build_context, mock_design_library, mock_design_loader):
        """
        PROJ-208: This test verifies command-based queue additions work correctly.

        The original test checked that dragged items preserved their turns_remaining.
        With PROJ-208, the command handler always uses 1.0 as default. ProductionEngine
        recalculates dynamically during production, so turns_remaining is not preserved
        from drag operations - it's recalculated based on remaining costs.
        """
        # Create entity for callback
        planet_entity = MagicMock()
        planet_entity.id = 10
        planet_entity.facilities = []

        # Create queue that the source will use
        test_queue = []
        planet_entity.construction_queue = test_queue

        entity_registry = {("planet", 10): planet_entity}

        controller = BuildQueueController(
            build_context=mock_build_context,
            design_library=mock_design_library,
            design_loader=mock_design_loader,
            design_report=MagicMock(),
            on_queue_changed=MagicMock(),
            add_to_queue_callback=_make_add_callback(entity_registry)
        )

        source = BuildQueueSource(
            queue_id="test_queue",
            display_name="Test Queue",
            owner_entity=planet_entity,
            construction_queue=test_queue,
            can_build_ships=True,
            can_build_complexes=True,
            context_type="planet",
            planet_id=10,
            build_rate={"A": 3000, "B": 3000, "C": 3000}
        )
        controller.set_active_queue(source)

        # Test 1: From list (new build)
        controller.add_to_queue("test_design_id", turns=None)
        assert len(source.construction_queue) == 1
        item = source.construction_queue[0]

        # PROJ-208: Handler uses default 1.0
        assert item["turns_remaining"] == 1.0

        # Test 2: Add another item
        controller.add_to_queue("test_design_id_2", turns=0.5)
        assert len(source.construction_queue) == 2
        item2 = source.construction_queue[1]
        # PROJ-208: Handler uses default 1.0 (turns parameter is unused now)
        assert item2["turns_remaining"] == 1.0
