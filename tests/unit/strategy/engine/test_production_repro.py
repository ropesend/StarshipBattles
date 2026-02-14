
import pytest
from unittest.mock import MagicMock, patch
from game.ui.panels.build_queue_controller import BuildQueueController
from game.strategy.engine.production_engine import ProductionEngine
from game.strategy.data.build_queue_source import BuildQueueSource

class TestBuildQueueReproduction:
    @pytest.fixture
    def mock_build_context(self):
        context = MagicMock()
        context.construction_queue = []
        context.can_build_type.return_value = True
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
        Reproduce the issue where turns are rounded up, causing inaccurate resource distribution.
        Build Rate: 3000 per turn for all resources.
        Cost B (Limiting): 6500.
        Expected Turns (Exact): 6500 / 3000 = 2.1666...
        Current Logic (Rounded): ceil(2.166...) = 3 turns.
        
        Effect on Resource Consumption:
        Current: Cost / (3 * 100) = 6500 / 300 = 21.66 per tick.
        Desired: Cost / (2.166 * 100) = 3000 / 100 = 30 per tick (max rate).
        """
        controller = BuildQueueController(
            build_context=mock_build_context,
            design_library=mock_design_library,
            design_loader=mock_design_loader,
            design_report=MagicMock(),
            on_queue_changed=MagicMock()
        )
        
        # Setup a queue source with 3000 production rate
        source = BuildQueueSource(
            queue_id="test_queue",
            display_name="Test Queue",
            owner_entity=MagicMock(),
            construction_queue=[],
            can_build_ships=True,
            can_build_complexes=True,
            context_type="planet",
            build_rate={"A": 3000, "B": 3000, "C": 3000}
        )
        controller.set_active_queue(source)
        
        # Add to queue
        controller.add_to_queue("test_design_id")
        
        item = source.construction_queue[0]
        
        # Check turns remaining - should now be float ~2.17
        # 6500 / 3000 = 2.1666...
        expected_turns = 6500 / 3000
        assert abs(item["turns_remaining"] - expected_turns) < 0.01, f"Turns should be approx {expected_turns}, got {item['turns_remaining']}"
        
        # Check cost per tick (should be removed from item, handled by engine)
        # But 'total_cost' should be there.
        assert "total_cost" in item
        assert item["total_cost"]["B"] == 6500

    def test_repro_drag_and_drop_1_turn_bug(self, mock_build_context, mock_design_library, mock_design_loader):
        """
        Reproduce the bug where dragging and dropping often defaults to 1 turn if not carefully handled.
        """
        controller = BuildQueueController(
            build_context=mock_build_context,
            design_library=mock_design_library,
            design_loader=mock_design_loader,
            design_report=MagicMock(),
            on_queue_changed=MagicMock()
        )
        
        source = BuildQueueSource(
            queue_id="test_queue",
            display_name="Test Queue",
            owner_entity=MagicMock(),
            construction_queue=[],
            can_build_ships=True,
            can_build_complexes=True,
            context_type="planet",
            build_rate={"A": 3000, "B": 3000, "C": 3000}
        )
        controller.set_active_queue(source)
        
        # Simulate Drag Handler passing turns=None (fix applied) or calculated value
        # The drag handler now passes turns=None if it was a fresh drag, 
        # or it passes the stored 'turns' from the dragged item. 
        # But if the dragged item came from the queue, it has turns. 
        # If it came from the list, it didn't have turns.
        
        # Test 1: From list (new build)
        controller.add_to_queue("test_design_id", turns=None)
        item = source.construction_queue[0]
        
        # Should calculate correct turns, NOT 1.
        expected_turns = 6500 / 3000
        assert abs(item["turns_remaining"] - expected_turns) < 0.01
        
        # Test 2: explicit turns (if dragged from queue) - simulating moving an item
        # If I drag an item with 0.5 turns remaining, it should stay 0.5
        controller.add_to_queue("test_design_id", turns=0.5)
        item2 = source.construction_queue[1]
        assert item2["turns_remaining"] == 0.5
