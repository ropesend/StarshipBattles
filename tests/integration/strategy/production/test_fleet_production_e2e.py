"""
End-to-end integration tests for fleet production system.

PROJ-67 Phase 6: Full integration tests for fleet space yards.
PROJ-158 Phase 4: Updated to use tick-based production API instead of dead
process_fleet_production() method.
"""

import pytest
import tempfile
import os
import json
import shutil
from unittest.mock import MagicMock, patch, PropertyMock

from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import FleetOrder, OrderType
from game.core.hex_math import HexCoord
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.engine.production_engine import ProductionEngine
from game.strategy.engine.fleet_movement_engine import FleetMovementEngine


def _process_fleet_turn(engine, empires, galaxy=None, save_path=None):
    """Process 100 ticks of construction for one turn.

    Uses the live tick-based API instead of the dead process_fleet_production().
    """
    for tick in range(1, 101):
        engine.process_construction_tick(
            tick, empires, galaxy, save_path=save_path
        )


class TestFleetProductionE2E:
    """End-to-end tests for fleet production system."""

    @pytest.fixture
    def temp_save_dir(self):
        """Create a temporary directory for save files with test designs."""
        temp_dir = tempfile.mkdtemp()
        designs_dir = os.path.join(temp_dir, "designs", "empire_0")
        os.makedirs(designs_dir, exist_ok=True)

        # Create test ship design
        test_ship_design = {
            "name": "Test Fighter",
            "ship_class": "Fighter",
            "vehicle_type": "Ship",
            "layers": {"CORE": [], "INNER": [], "OUTER": [], "ARMOR": []},
            "resources": {"fuel": 0.0, "energy": 0.0, "ammo": 0.0},
            "expected_stats": {"max_hp": 50, "max_speed": 15, "mass": 20.0},
            "_metadata": {"is_obsolete": False, "times_built": 0}
        }

        # Create test complex design
        test_complex_design = {
            "name": "Test Factory",
            "vehicle_type": "Planetary Complex",
            "layers": {"CORE": [], "INNER": []},
            "_metadata": {"is_obsolete": False, "times_built": 0}
        }

        with open(os.path.join(designs_dir, "test_fighter.json"), 'w') as f:
            json.dump(test_ship_design, f)
        with open(os.path.join(designs_dir, "test_factory.json"), 'w') as f:
            json.dump(test_complex_design, f)

        yield temp_dir

        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    @pytest.fixture
    def mock_galaxy_at_planet(self):
        """Create a mock galaxy with a planet at a specific hex."""
        mock_planet = MagicMock(spec=Planet)
        mock_planet.name = "Test Planet"
        mock_planet.facilities = []

        mock_galaxy = MagicMock()
        # Returns planet at hex (5, 5), empty elsewhere
        def get_planets(hex_coord):
            if hex_coord == HexCoord(5, 5):
                return [mock_planet]
            return []
        mock_galaxy.get_planets_at_global_hex = MagicMock(side_effect=get_planets)

        return mock_galaxy, mock_planet

    def test_e2e_fleet_with_yard_builds_ship_that_spawns_in_fleet(self, temp_save_dir, fresh_registries):
        """E2E: Create fleet with yard → issue BUILD → advance turns → ship spawns in fleet."""
        # PROJ-211: Pass registries for DI compliance when spawning ships
        engine = ProductionEngine(registries=fresh_registries)

        # Create fleet with space yard capability
        # At 30/tick fleet yard rate, 6000 Metals = 200 ticks = 2 turns
        fleet = Fleet(1, 0, HexCoord(5, 5))
        fleet.construction_queue = [
            {
                "design_id": "test_fighter",
                "type": "ship",
                "turns_remaining": 2,
                "total_cost": {"Metals": 6000.0},
                "resources_consumed": {"Metals": 0.0}
            }
        ]
        fleet.orders = [FleetOrder(OrderType.BUILD)]

        initial_ship_count = len(fleet.ships)

        empire = MagicMock()
        empire.id = 0
        empire.fleets = [fleet]
        empire.colonies = []  # No colonies
        # Give empire resources
        empire.resource_pool = {"Metals": 100000.0}

        # Simulate fleet having a shipyard with count
        with patch.object(Fleet, 'has_space_shipyard', new_callable=lambda: property(lambda self: True)), \
             patch.object(Fleet, 'space_shipyard_count', new_callable=lambda: property(lambda self: 1)):
            # Turn 1: progress but not complete
            _process_fleet_turn(engine, [empire], None, temp_save_dir)
            assert len(fleet.construction_queue) == 1
            assert fleet.construction_queue[0]["resources_consumed"]["Metals"] > 0
            assert len(fleet.ships) == initial_ship_count  # Not yet spawned

            # Turn 2: ship completes and spawns
            _process_fleet_turn(engine, [empire], None, temp_save_dir)
            assert len(fleet.construction_queue) == 0  # Queue empty
            assert len(fleet.ships) == initial_ship_count + 1  # Ship spawned

    def test_e2e_fleet_at_planet_builds_complex_that_appears_on_planet(
        self, temp_save_dir, mock_galaxy_at_planet
    ):
        """E2E: Fleet at planet → build complex → complex appears on planet."""
        mock_galaxy, mock_planet = mock_galaxy_at_planet
        engine = ProductionEngine()

        # Create fleet at planet hex with space yard
        # At 30/tick fleet yard rate, 100 Metals = 4 ticks, completes in 1 turn
        fleet = Fleet(1, 0, HexCoord(5, 5))  # Same as planet
        fleet.construction_queue = [
            {
                "design_id": "test_factory",
                "type": "complex",
                "turns_remaining": 1,
                "total_cost": {"Metals": 100.0},
                "resources_consumed": {"Metals": 0.0}
            }
        ]
        fleet.orders = [FleetOrder(OrderType.BUILD)]

        initial_facility_count = len(mock_planet.facilities)

        empire = MagicMock()
        empire.id = 0
        empire.fleets = [fleet]
        empire.colonies = []
        empire.resource_pool = {"Metals": 100000.0}

        with patch.object(Fleet, 'has_space_shipyard', new_callable=lambda: property(lambda self: True)), \
             patch.object(Fleet, 'space_shipyard_count', new_callable=lambda: property(lambda self: 1)):
            _process_fleet_turn(engine, [empire], mock_galaxy, temp_save_dir)

        # Queue should be empty
        assert len(fleet.construction_queue) == 0
        # Complex should appear on planet
        assert len(mock_planet.facilities) == initial_facility_count + 1

    def test_e2e_fleet_with_build_order_cannot_move(self):
        """E2E: Fleet with BUILD order → try to move → blocked."""
        movement_engine = FleetMovementEngine()

        # Create fleet with BUILD order
        fleet = Fleet(1, 0, HexCoord(0, 0))
        fleet.speed = 10.0  # Needs speed to be considered for movement
        fleet.orders = [FleetOrder(OrderType.BUILD)]
        fleet.construction_queue = [
            {"design_id": "test_ship", "type": "ship", "turns_remaining": 5}
        ]

        empire = MagicMock()
        empire.id = 0
        empire.fleets = [fleet]

        mock_galaxy = MagicMock()

        # Collect movements at tick 10 (when fleet would move based on speed)
        movements = movement_engine.collect_movements([empire], mock_galaxy, tick=10)

        # Fleet should NOT be in movements (blocked by BUILD order)
        fleet_ids = [m[0].id for m in movements]
        assert fleet.id not in fleet_ids

    def test_e2e_fleet_without_build_order_can_move(self):
        """E2E: Fleet without BUILD order can still move."""
        movement_engine = FleetMovementEngine()

        # Create fleet with MOVE order (not BUILD)
        fleet = Fleet(1, 0, HexCoord(0, 0))
        fleet.speed = 10.0  # Needs speed
        fleet.orders = [FleetOrder(OrderType.MOVE, HexCoord(5, 5))]
        fleet.path = [HexCoord(1, 0), HexCoord(2, 0)]

        empire = MagicMock()
        empire.id = 0
        empire.fleets = [fleet]

        mock_galaxy = MagicMock()

        # Collect movements at tick 10
        movements = movement_engine.collect_movements([empire], mock_galaxy, tick=10)

        # Fleet should be in movements
        fleet_ids = [m[0].id for m in movements]
        assert fleet.id in fleet_ids

    def test_e2e_save_load_preserves_build_state(self, temp_save_dir):
        """E2E: Save game with building fleet → load → state preserved."""
        # Create fleet with full build state
        original_fleet = Fleet("test_fleet", 0, HexCoord(10, -5))
        original_fleet.add_order(FleetOrder(OrderType.BUILD))
        original_fleet.construction_queue = [
            {"design_id": "destroyer", "type": "ship", "turns_remaining": 5},
            {"design_id": "frigate", "type": "ship", "turns_remaining": 3},
        ]

        # Serialize
        d = original_fleet.to_dict()
        d['location'] = [10, -5]  # Fix HexCoord

        # Simulate save to file
        save_file = os.path.join(temp_save_dir, "test_fleet.json")
        with open(save_file, 'w') as f:
            json.dump(d, f)

        # Load from file
        with open(save_file, 'r') as f:
            loaded_data = json.load(f)

        restored_fleet = Fleet.from_dict(loaded_data)

        # Verify full state preserved
        assert restored_fleet.id == original_fleet.id
        assert restored_fleet.is_building is True
        assert len(restored_fleet.construction_queue) == 2
        assert restored_fleet.construction_queue[0]["design_id"] == "destroyer"
        assert restored_fleet.construction_queue[0]["turns_remaining"] == 5

    def test_e2e_complex_pauses_when_fleet_moves_away_from_planet(
        self, temp_save_dir, mock_galaxy_at_planet
    ):
        """E2E: Fleet at planet with complex in queue → fleet moves → complex pauses."""
        mock_galaxy, mock_planet = mock_galaxy_at_planet
        engine = ProductionEngine()

        # Start at planet hex
        # At 30/tick fleet yard rate, 9000 Metals = 300 ticks = 3 turns
        fleet = Fleet(1, 0, HexCoord(5, 5))
        fleet.construction_queue = [
            {
                "design_id": "test_factory",
                "type": "complex",
                "turns_remaining": 3,
                "total_cost": {"Metals": 9000.0},
                "resources_consumed": {"Metals": 0.0}
            }
        ]
        fleet.orders = [FleetOrder(OrderType.BUILD)]

        empire = MagicMock()
        empire.id = 0
        empire.fleets = [fleet]
        empire.colonies = []
        empire.resource_pool = {"Metals": 100000.0}

        with patch.object(Fleet, 'has_space_shipyard', new_callable=lambda: property(lambda self: True)), \
             patch.object(Fleet, 'space_shipyard_count', new_callable=lambda: property(lambda self: 1)):
            # Turn 1: at planet - production proceeds
            _process_fleet_turn(engine, [empire], mock_galaxy, temp_save_dir)
            consumed_turn1 = fleet.construction_queue[0]["resources_consumed"]["Metals"]
            assert consumed_turn1 > 0  # Made progress

            # "Move" fleet away from planet
            fleet.location = HexCoord(10, 10)

            # Turn 2: not at planet - production pauses for complex
            _process_fleet_turn(engine, [empire], mock_galaxy, temp_save_dir)
            consumed_turn2 = fleet.construction_queue[0]["resources_consumed"]["Metals"]
            assert consumed_turn2 == consumed_turn1  # No additional progress

            # "Move" fleet back to planet
            fleet.location = HexCoord(5, 5)

            # Turn 3: at planet - production resumes
            _process_fleet_turn(engine, [empire], mock_galaxy, temp_save_dir)
            consumed_turn3 = fleet.construction_queue[0]["resources_consumed"]["Metals"]
            assert consumed_turn3 > consumed_turn2  # Made progress again


class TestFleetProductionMultiQueue:
    """Tests for fleets with multiple items in queue."""

    @pytest.fixture
    def temp_save_dir(self):
        """Create a temporary directory for save files."""
        temp_dir = tempfile.mkdtemp()
        designs_dir = os.path.join(temp_dir, "designs", "empire_0")
        os.makedirs(designs_dir, exist_ok=True)

        # Create test designs
        for name in ["ship_a", "ship_b", "ship_c"]:
            design = {
                "name": name,
                "vehicle_type": "Ship",
                "layers": {"CORE": []},
                "_metadata": {"times_built": 0}
            }
            with open(os.path.join(designs_dir, f"{name}.json"), 'w') as f:
                json.dump(design, f)

        yield temp_dir

        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    def test_queue_items_processed_in_order(self, temp_save_dir, fresh_registries):
        """Queue items are processed one at a time in FIFO order."""
        # PROJ-211: Pass registries for DI compliance when spawning ships
        engine = ProductionEngine(registries=fresh_registries)

        # At 30/tick fleet yard rate:
        # ship_a: 3000 Metals = 100 ticks = 1 turn
        # ship_b: 6000 Metals = 200 ticks = 2 turns
        # ship_c: 3000 Metals = 100 ticks = 1 turn
        fleet = Fleet(1, 0, HexCoord(5, 5))
        fleet.construction_queue = [
            {
                "design_id": "ship_a",
                "type": "ship",
                "turns_remaining": 1,
                "total_cost": {"Metals": 3000.0},
                "resources_consumed": {"Metals": 0.0}
            },
            {
                "design_id": "ship_b",
                "type": "ship",
                "turns_remaining": 2,
                "total_cost": {"Metals": 6000.0},
                "resources_consumed": {"Metals": 0.0}
            },
            {
                "design_id": "ship_c",
                "type": "ship",
                "turns_remaining": 1,
                "total_cost": {"Metals": 3000.0},
                "resources_consumed": {"Metals": 0.0}
            },
        ]
        fleet.orders = [FleetOrder(OrderType.BUILD)]

        empire = MagicMock()
        empire.id = 0
        empire.fleets = [fleet]
        empire.colonies = []
        empire.resource_pool = {"Metals": 100000.0}

        with patch.object(Fleet, 'has_space_shipyard', new_callable=lambda: property(lambda self: True)), \
             patch.object(Fleet, 'space_shipyard_count', new_callable=lambda: property(lambda self: 1)):
            # Turn 1: ship_a completes
            _process_fleet_turn(engine, [empire], None, temp_save_dir)
            assert len(fleet.construction_queue) == 2
            assert fleet.construction_queue[0]["design_id"] == "ship_b"

            # Turn 2: ship_b progress
            _process_fleet_turn(engine, [empire], None, temp_save_dir)
            assert fleet.construction_queue[0]["resources_consumed"]["Metals"] > 0

            # Turn 3: ship_b completes
            _process_fleet_turn(engine, [empire], None, temp_save_dir)
            assert len(fleet.construction_queue) == 1
            assert fleet.construction_queue[0]["design_id"] == "ship_c"

            # Turn 4: ship_c completes
            _process_fleet_turn(engine, [empire], None, temp_save_dir)
            assert len(fleet.construction_queue) == 0
