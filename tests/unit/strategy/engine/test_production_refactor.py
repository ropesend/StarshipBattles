"""
PROJ-191 Phase 3: Updated mocks to use spec= for type safety.
"""
import pytest
from unittest.mock import MagicMock
from game.strategy.engine.production_engine import ProductionEngine
from game.strategy.data.build_queue_source import BuildQueueSource
from game.strategy.data.empire import Empire
from game.strategy.data.planet import Planet

class TestProductionEngineRefactor:
    @pytest.fixture
    def engine(self):
        return ProductionEngine()

    @pytest.fixture
    def mock_empire(self):
        emp = MagicMock(spec=Empire)
        emp.id = "emp1"
        emp.has_resources.return_value = True
        emp.consume_resources = MagicMock()
        return emp

    @pytest.fixture
    def mock_colony(self, mock_empire):
        colony = MagicMock(spec=Planet)
        colony.construction_queue = []
        colony.facilities = []
        return colony

    def test_dynamic_consumption_limiting_resource(self, engine, mock_empire, mock_colony):
        """Test that consumption is based on the limiting resource."""
        # Item: Cost A=100, B=200.
        # Rate: A=500/turn (5/tick), B=500/turn (5/tick).
        # Limiting resource is B (needs 200/5 = 40 ticks).
        # A needs 100/5 = 20 ticks.
        # So full build takes 40 ticks (0.4 turns).
        # In 1 tick (100% capacity), we should process 1.0 tick worth of production.
        # Consumption per tick: 
        # B: 5/tick.
        # A: Should be proportional?
        # Logic: 
        # Max needed = 40 ticks.
        # Ticks to spend = 1.0.
        # Fraction = 1/40? No, Ticks to spend is time.
        # We spend 1 tick of time.
        # Resources consumed = Rate * Time.
        # B: 5 * 1 = 5.
        # A: 5 * 1 = 5.
        # After 20 ticks: A consumed 100 (done). B consumed 100 (half).
        # After 40 ticks: A consumed 200? NO. A should stop consuming?
        # My logic determines `ticks_remaining` based on current state.
        # If A is done, remaining cost A=0. Ticks needed for A=0.
        # So it correctly identifies B as limiting (20 ticks left).
        # So yes, in the first 20 ticks, both consume at full rate.
        
        item = {
            "design_id": "test_ship",
            "type": "ship",
            "total_cost": {"A": 100, "B": 200},
            "resources_consumed": {"A": 0, "B": 0},
            "turns_remaining": 0.4
        }
        mock_colony.construction_queue = [item]
        
        # Rate per turn = 100 ticks
        # 500 / 100 = 5 per tick
        rates = {"A": 500, "B": 500}
        
        # Test 1 tick
        engine._process_queue_tick_dynamic(
            mock_colony.construction_queue, mock_empire, 1, MagicMock(), None,
            rates, mock_colony, None
        )
        
        assert item["resources_consumed"]["A"] == 5.0
        assert item["resources_consumed"]["B"] == 5.0
        
        # Simulate moving to tick 21 (after 20 ticks processed)
        item["resources_consumed"]["A"] = 100.0 # Done
        item["resources_consumed"]["B"] = 100.0 # Half done
        
        engine._process_queue_tick_dynamic(
            mock_colony.construction_queue, mock_empire, 2, MagicMock(), None,
            rates, mock_colony, None
        )
        
        # A should not consume more (remaining 0)
        assert item["resources_consumed"]["A"] == 100.0
        # B should consume 5 more
        assert item["resources_consumed"]["B"] == 105.0

    def test_carry_over_capacity(self, engine, mock_empire, mock_colony):
        """Test that production capacity carries over to the next item in the same tick."""
        # Rate: 1000/turn (10/tick).
        # Item 1: Cost 5. (Takes 0.5 ticks).
        # Item 2: Cost 5.
        # In 1 tick, both should finish?
        # Tick 1 starts with capacity 1.0.
        # Item 1 needs 0.5 ticks. Spends 0.5. Capacity -> 0.5. Finishes.
        # Item 2 needs 0.5 ticks. Spends 0.5. Capacity -> 0.0. Finishes.
        
        item1 = {
            "design_id": "ship1",
            "type": "ship",
            "total_cost": {"A": 5},
            "resources_consumed": {"A": 0}
        }
        item2 = {
            "design_id": "ship2",
            "type": "ship",
            "total_cost": {"A": 5},
            "resources_consumed": {"A": 0}
        }
        mock_colony.construction_queue = [item1, item2]
        rates = {"A": 1000}
        
        # Mock spawning to avoid errors
        engine._spawn_ship = MagicMock()
        
        engine._process_queue_tick_dynamic(
            mock_colony.construction_queue, mock_empire, 1, MagicMock(), None,
            rates, mock_colony, None
        )
        
        # Queue should be empty (both finished)
        assert len(mock_colony.construction_queue) == 0
        
        # Verify spawns
        assert engine._spawn_ship.call_count == 2

