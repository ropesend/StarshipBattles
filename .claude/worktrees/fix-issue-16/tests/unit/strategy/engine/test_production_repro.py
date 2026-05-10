"""
Tests for build queue production issues.

PROJ-208: These tests were updated to reflect the new command-based architecture.
PROJ-213: Updated to verify that queue items have populated total_cost and
resources_consumed fields, matching the fixed AddToConstructionQueueCommandHandler.
"""

import pytest
from typing import Optional
from unittest.mock import MagicMock, patch
from game.ui.panels.build_queue_controller import BuildQueueController
from game.strategy.engine.production_engine import ProductionEngine
from game.strategy.data.build_queue_source import BuildQueueSource
from game.strategy.services.design_cost_calculator import DesignCostCalculator
from game.strategy.systems.design_library import DesignLoadResult


def _make_add_callback(entity_registry: dict, design_data_registry: dict = None):
    """Create an add_to_queue_callback that resolves queues from a registry.

    PROJ-213: Updated to populate total_cost from design data, matching the
    fixed AddToConstructionQueueCommandHandler behavior.

    Args:
        entity_registry: Maps (entity_type, entity_id) to entity objects.
        design_data_registry: Maps design_id to design_data dicts for cost calculation.
            If None, total_cost defaults to empty (legacy behavior for backward compat tests).
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

        # PROJ-213: Calculate design cost from design data
        # PROJ-218: Pass None for registries to use inline fallback
        total_cost = {}
        if design_data_registry and design_id in design_data_registry:
            total_cost = DesignCostCalculator.calculate_total_cost(
                design_data_registry[design_id], None
            )

        # Build queue item with populated cost tracking
        item = {
            "design_id": design_id,
            "type": category,
            "turns_remaining": 1.0,
            "total_cost": total_cost,
            "resources_consumed": {res: 0.0 for res in total_cost},
        }
        if target_planet_id is not None:
            item["target_planet_id"] = target_planet_id

        # Insert or append
        if index is not None:
            queue.insert(index, item)
        else:
            queue.append(item)

    return callback


_TEST_DESIGN_DATA = {
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
        lib.load_design_data.return_value = DesignLoadResult.ok(_TEST_DESIGN_DATA)
        return lib

    @pytest.fixture
    def mock_design_loader(self):
        loader = MagicMock()
        ship = MagicMock()
        ship.construction_cost = {"A": 2500, "B": 6500, "C": 2000}
        loader.load_ship_from_design_data.return_value = ship
        return loader

    @pytest.fixture
    def design_data_registry(self):
        """Registry mapping design_id to design_data for cost calculation."""
        return {
            "test_design_id": _TEST_DESIGN_DATA,
            "test_design_id_2": _TEST_DESIGN_DATA,
        }

    def test_queue_item_has_populated_cost(self, mock_build_context, mock_design_library, mock_design_loader, design_data_registry):
        """
        PROJ-213: Verify that queue items are created with populated total_cost
        and zero-initialized resources_consumed, not empty dicts.
        """
        planet_entity = MagicMock()
        planet_entity.id = 10
        planet_entity.facilities = []

        test_queue = []
        planet_entity.construction_queue = test_queue

        entity_registry = {("planet", 10): planet_entity}

        controller = BuildQueueController(
            build_context=mock_build_context,
            design_library=mock_design_library,
            design_loader=mock_design_loader,
            design_report=MagicMock(),
            on_queue_changed=MagicMock(),
            add_to_queue_callback=_make_add_callback(entity_registry, design_data_registry)
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

        # Add to queue
        controller.add_to_queue("test_design_id")

        # Verify item was added with correct cost data
        assert len(source.construction_queue) == 1
        item = source.construction_queue[0]

        assert item["design_id"] == "test_design_id"
        assert item["turns_remaining"] == 1.0  # ProductionEngine recalculates dynamically

        # PROJ-213: total_cost must be populated with actual design costs
        assert item["total_cost"] == {"A": 2500, "B": 6500, "C": 2000}

        # PROJ-213: resources_consumed must be zero-initialized for each resource
        assert item["resources_consumed"] == {"A": 0.0, "B": 0.0, "C": 0.0}

    def test_multiple_queue_additions_have_cost(self, mock_build_context, mock_design_library, mock_design_loader, design_data_registry):
        """
        PROJ-213: Verify that multiple queue additions all get populated costs.
        """
        planet_entity = MagicMock()
        planet_entity.id = 10
        planet_entity.facilities = []

        test_queue = []
        planet_entity.construction_queue = test_queue

        entity_registry = {("planet", 10): planet_entity}

        controller = BuildQueueController(
            build_context=mock_build_context,
            design_library=mock_design_library,
            design_loader=mock_design_loader,
            design_report=MagicMock(),
            on_queue_changed=MagicMock(),
            add_to_queue_callback=_make_add_callback(entity_registry, design_data_registry)
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

        # Add two items
        controller.add_to_queue("test_design_id", turns=None)
        controller.add_to_queue("test_design_id_2", turns=0.5)

        assert len(source.construction_queue) == 2

        # Both items should have populated cost data
        for item in source.construction_queue:
            assert item["total_cost"] == {"A": 2500, "B": 6500, "C": 2000}
            assert item["resources_consumed"] == {"A": 0.0, "B": 0.0, "C": 0.0}
