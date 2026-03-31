"""
PROJ-191 Phase 3: Updated mocks to use spec= for type safety.
"""
import pytest
from unittest.mock import MagicMock, patch
from game.strategy.engine.production_engine import ProductionEngine
from game.strategy.data.build_queue_source import BuildQueueSource
from game.strategy.data.empire import Empire
from game.strategy.data.planet import Planet
from game.strategy.events.event_types import EventType, EventCategory

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
        engine._spawner._spawn_ship = MagicMock()
        
        engine._process_queue_tick_dynamic(
            mock_colony.construction_queue, mock_empire, 1, MagicMock(), None,
            rates, mock_colony, None
        )
        
        # Queue should be empty (both finished)
        assert len(mock_colony.construction_queue) == 0

        # Verify spawns
        assert engine._spawner._spawn_ship.call_count == 2


class TestProductionEngineEdgeCases:
    """PROJ-209 Phase 2: Test coverage for edge cases (AR-01, TC-001, TC-002, TC-005, TC-009)."""

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
    def mock_colony(self):
        colony = MagicMock(spec=Planet)
        colony.construction_queue = []
        colony.facilities = []
        return colony

    def test_item_without_total_cost_is_skipped_with_warning(
        self, engine, mock_empire, mock_colony, caplog
    ):
        """AR-01: Queue item missing 'total_cost' should be skipped with warning."""
        # Item missing total_cost key
        item_without_cost = {
            "design_id": "broken_ship",
            "type": "ship",
            # Deliberately missing 'total_cost'
            "resources_consumed": {}
        }
        # Valid item after it
        valid_item = {
            "design_id": "valid_ship",
            "type": "ship",
            "total_cost": {"A": 5},
            "resources_consumed": {"A": 0}
        }
        mock_colony.construction_queue = [item_without_cost, valid_item]
        rates = {"A": 1000}

        engine._spawner._spawn_ship = MagicMock()

        import logging
        with caplog.at_level(logging.WARNING):
            engine._process_queue_tick_dynamic(
                mock_colony.construction_queue, mock_empire, 1, MagicMock(), None,
                rates, mock_colony, False
            )

        # Broken item should be removed, valid item should complete
        assert len(mock_colony.construction_queue) == 0
        assert "broken_ship" in caplog.text
        assert "missing 'total_cost'" in caplog.text
        assert engine._spawner._spawn_ship.call_count == 1

    def test_non_dict_item_is_removed_and_processing_continues(
        self, engine, mock_empire, mock_colony
    ):
        """TC-001: Non-dict item in queue should be removed, processing continues."""
        invalid_item = "not_a_dict"  # String instead of dict
        valid_item = {
            "design_id": "valid_ship",
            "type": "ship",
            "total_cost": {"A": 5},
            "resources_consumed": {"A": 0}
        }
        mock_colony.construction_queue = [invalid_item, valid_item]
        rates = {"A": 1000}

        engine._spawner._spawn_ship = MagicMock()

        engine._process_queue_tick_dynamic(
            mock_colony.construction_queue, mock_empire, 1, MagicMock(), None,
            rates, mock_colony, False
        )

        # Both should be removed (invalid popped, valid completed)
        assert len(mock_colony.construction_queue) == 0
        assert engine._spawner._spawn_ship.call_count == 1

    def test_zero_production_rate_for_required_resource_stops_queue(
        self, engine, mock_empire, mock_colony
    ):
        """TC-002: Zero production rate for a required resource should stop processing."""
        item = {
            "design_id": "test_ship",
            "type": "ship",
            "total_cost": {"A": 100, "B": 50},
            "resources_consumed": {"A": 0, "B": 0}
        }
        mock_colony.construction_queue = [item]
        # Rate has 0 for resource B
        rates = {"A": 500, "B": 0}

        engine._spawner._spawn_ship = MagicMock()

        engine._process_queue_tick_dynamic(
            mock_colony.construction_queue, mock_empire, 1, MagicMock(), None,
            rates, mock_colony, False
        )

        # Item should still be in queue (cannot be built)
        assert len(mock_colony.construction_queue) == 1
        # No spawning should occur
        assert engine._spawner._spawn_ship.call_count == 0
        # No resources should have been consumed
        assert item["resources_consumed"]["A"] == 0
        assert item["resources_consumed"]["B"] == 0

    def test_complex_only_filter_blocks_ship_items(
        self, engine, mock_empire, mock_colony
    ):
        """TC-005: When is_complex_only=True, ship items should block the queue."""
        ship_item = {
            "design_id": "test_ship",
            "type": "ship",
            "total_cost": {"A": 100},
            "resources_consumed": {"A": 0}
        }
        mock_colony.construction_queue = [ship_item]
        rates = {"A": 500}

        engine._spawner._spawn_ship = MagicMock()

        engine._process_queue_tick_dynamic(
            mock_colony.construction_queue, mock_empire, 1, MagicMock(), None,
            rates, mock_colony, is_complex_only=True
        )

        # Ship item should still be in queue (can't build ships in complex-only queue)
        assert len(mock_colony.construction_queue) == 1
        # No spawning
        assert engine._spawner._spawn_ship.call_count == 0

    def test_iteration_safety_guard_prevents_infinite_loop(
        self, engine, mock_empire, mock_colony
    ):
        """TC-009: Iteration safety guard should prevent infinite loops."""
        # Create items that complete but somehow don't get popped
        # This tests the safety guard by creating many quick-completing items
        items = []
        for i in range(15):  # More than the 10 iteration limit
            items.append({
                "design_id": f"ship_{i}",
                "type": "ship",
                "total_cost": {"A": 0.1},  # Very cheap items
                "resources_consumed": {"A": 0}
            })
        mock_colony.construction_queue = items
        rates = {"A": 100000}  # Very high rate - can complete many per tick

        engine._spawner._spawn_ship = MagicMock()

        # Should not hang - safety guard limits to 10 iterations
        engine._process_queue_tick_dynamic(
            mock_colony.construction_queue, mock_empire, 1, MagicMock(), None,
            rates, mock_colony, False
        )

        # Should have processed at most 10 items (safety guard)
        # Some items may remain due to iteration limit
        assert engine._spawner._spawn_ship.call_count <= 10


class TestResourceShortageEventLogging:
    """FEAT-09: Test that RESOURCE_SHORTAGE events are logged when production pauses."""

    @pytest.fixture
    def engine(self):
        return ProductionEngine()

    @pytest.fixture
    def empire(self):
        emp = MagicMock(spec=Empire)
        emp.id = 1
        emp.resource_pool = {"metals": 10.0, "organics": 2.0}
        emp.has_resources.return_value = False  # Cannot afford
        emp.consume_resources = MagicMock()
        return emp

    @pytest.fixture
    def colony(self):
        colony = MagicMock(spec=Planet)
        colony.construction_queue = []
        colony.facilities = []
        # Default: insufficient stockpile (triggers shortage)
        colony.stockpile = {"metals": 10.0, "organics": 2.0}
        colony.has_stockpile.return_value = False
        colony.get_stockpile.side_effect = lambda res: colony.stockpile.get(res, 0.0)
        return colony

    def test_shortage_event_logged_on_affordability_failure(self, engine, empire, colony):
        """A RESOURCE_SHORTAGE event should be logged when affordability check fails."""
        item = {
            "design_id": "frigate_mk1",
            "type": "ship",
            "total_cost": {"metals": 100, "organics": 50},
            "resources_consumed": {"metals": 0, "organics": 0},
        }
        colony.construction_queue = [item]
        rates = {"metals": 500, "organics": 500}

        with patch("game.strategy.engine.production_engine.log_event") as mock_log:
            engine._process_queue_tick_dynamic(
                colony.construction_queue, empire, 1, MagicMock(), None,
                rates, colony, False
            )

            # Should have logged a RESOURCE_SHORTAGE event
            shortage_calls = [
                c for c in mock_log.call_args_list
                if c[0][0] == EventType.RESOURCE_SHORTAGE
            ]
            assert len(shortage_calls) == 1

            call_kwargs = shortage_calls[0][1]
            assert call_kwargs["category"] == EventCategory.PRODUCTION
            assert call_kwargs["empire_id"] == 1
            assert call_kwargs["design_id"] == "frigate_mk1"
            assert "limiting_resource" in call_kwargs
            assert "available" in call_kwargs
            assert "needed" in call_kwargs

    def test_shortage_event_identifies_limiting_resource(self, engine, empire, colony):
        """The event should identify which resource is the bottleneck."""
        item = {
            "design_id": "cruiser_mk1",
            "type": "ship",
            "total_cost": {"metals": 100, "organics": 50},
            "resources_consumed": {"metals": 0, "organics": 0},
        }
        colony.construction_queue = [item]
        rates = {"metals": 500, "organics": 500}

        # Planet stockpile has plenty of Metals but almost no Organics
        colony.stockpile = {"metals": 1000.0, "organics": 0.5}
        colony.get_stockpile.side_effect = lambda res: colony.stockpile.get(res, 0.0)

        with patch("game.strategy.engine.production_engine.log_event") as mock_log:
            engine._process_queue_tick_dynamic(
                colony.construction_queue, empire, 1, MagicMock(), None,
                rates, colony, False
            )

            shortage_calls = [
                c for c in mock_log.call_args_list
                if c[0][0] == EventType.RESOURCE_SHORTAGE
            ]
            assert len(shortage_calls) == 1

            call_kwargs = shortage_calls[0][1]
            assert call_kwargs["limiting_resource"] == "organics"
            assert call_kwargs["available"] == 0.5
            assert call_kwargs["needed"] == 5.0  # 500/100 = 5 per tick

    def test_shortage_event_logged_once_per_item_per_turn(self, engine, empire, colony):
        """Only one RESOURCE_SHORTAGE event per item per turn, not every tick."""
        item = {
            "design_id": "frigate_mk1",
            "type": "ship",
            "total_cost": {"metals": 100},
            "resources_consumed": {"metals": 0},
        }
        colony.construction_queue = [item]
        rates = {"metals": 500}

        with patch("game.strategy.engine.production_engine.log_event") as mock_log:
            # Simulate multiple ticks within the same turn
            for tick in range(1, 4):
                engine._process_queue_tick_dynamic(
                    colony.construction_queue, empire, tick, MagicMock(), None,
                    rates, colony, False
                )

            shortage_calls = [
                c for c in mock_log.call_args_list
                if c[0][0] == EventType.RESOURCE_SHORTAGE
            ]
            # Should only be logged once, not three times
            assert len(shortage_calls) == 1

    def test_shortage_flag_resets_between_turns(self, engine, colony):
        """If shortage persists across turns, it should log again in the next turn."""
        empire_poor = MagicMock(spec=Empire)
        empire_poor.id = 1
        empire_poor.resource_pool = {"metals": 0.0}
        empire_poor.has_resources.return_value = False
        # Set planet stockpile to empty so affordability check fails
        colony.stockpile = {"metals": 0.0}
        colony.has_stockpile.return_value = False
        colony.get_stockpile.side_effect = lambda res: colony.stockpile.get(res, 0.0)

        item = {
            "design_id": "frigate_mk1",
            "type": "ship",
            "total_cost": {"metals": 100},
            "resources_consumed": {"metals": 0},
        }
        colony.construction_queue = [item]
        rates = {"metals": 500}

        with patch("game.strategy.engine.production_engine.log_event") as mock_log:
            # Turn 1: tick 1 logs shortage, tick 2 does not
            engine._process_queue_tick_dynamic(
                colony.construction_queue, empire_poor, 1, MagicMock(), None,
                rates, colony, False
            )
            engine._process_queue_tick_dynamic(
                colony.construction_queue, empire_poor, 2, MagicMock(), None,
                rates, colony, False
            )

            shortage_calls_turn1 = [
                c for c in mock_log.call_args_list
                if c[0][0] == EventType.RESOURCE_SHORTAGE
            ]
            assert len(shortage_calls_turn1) == 1

        # Clear the flag for next turn (tick == 1 resets)
        with patch("game.strategy.engine.production_engine.log_event") as mock_log:
            # Turn 2: tick 1 should log again
            engine._process_queue_tick_dynamic(
                colony.construction_queue, empire_poor, 1, MagicMock(), None,
                rates, colony, False
            )

            shortage_calls_turn2 = [
                c for c in mock_log.call_args_list
                if c[0][0] == EventType.RESOURCE_SHORTAGE
            ]
            assert len(shortage_calls_turn2) == 1

    def test_no_shortage_event_when_affordable(self, engine, colony):
        """No shortage event should be logged when empire can afford production."""
        empire_rich = MagicMock(spec=Empire)
        empire_rich.id = 1
        empire_rich.resource_pool = {"metals": 10000.0}
        empire_rich.has_resources.return_value = True
        empire_rich.consume_resources = MagicMock(return_value=True)
        # Planet stockpile is rich - affordability check passes
        colony.stockpile = {"metals": 10000.0}
        colony.has_stockpile.return_value = True
        colony.get_stockpile.side_effect = lambda res: colony.stockpile.get(res, 0.0)

        item = {
            "design_id": "frigate_mk1",
            "type": "ship",
            "total_cost": {"metals": 100},
            "resources_consumed": {"metals": 0},
        }
        colony.construction_queue = [item]
        rates = {"metals": 500}

        with patch("game.strategy.engine.production_engine.log_event") as mock_log:
            engine._process_queue_tick_dynamic(
                colony.construction_queue, empire_rich, 1, MagicMock(), None,
                rates, colony, False
            )

            shortage_calls = [
                c for c in mock_log.call_args_list
                if c[0][0] == EventType.RESOURCE_SHORTAGE
            ]
            assert len(shortage_calls) == 0

