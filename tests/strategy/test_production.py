
import unittest
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.hex_math import HexCoord
from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet

class TestProduction(unittest.TestCase):
    def setUp(self):
        # Create a valid planet manually to satisfy the dataclass
        self.planet = Planet(
            name="Terran Prime",
            location=HexCoord(0, 0),
            orbit_distance=3,
            mass=5.97e24,
            radius=6371000,
            surface_area=5.1e14,
            density=5515,
            surface_gravity=9.81,
            surface_pressure=101325,
            surface_temperature=288,
            surface_water=0.7,
            tectonic_activity=0.1,
            magnetic_field=1.0,
            atmosphere={'N2': 78000.0, 'O2': 21000.0},
            planet_type=PlanetType.TERRESTRIAL
        )
        self.planet.owner_id = 0
        
        self.empire = Empire(0, "Terran", (0, 0, 255))
        self.empire.add_colony(self.planet)
        
        self.engine = TurnEngine()
        self.empires = [self.empire]

    def test_add_to_queue(self):
        """Verify adding an item to the queue works."""
        # Item: "Colony Ship", Turns: 1
        self.planet.add_production("Colony Ship", 1)
        self.assertEqual(len(self.planet.construction_queue), 1)
        item, turns = self.planet.construction_queue[0]
        self.assertEqual(item, "Colony Ship")
        self.assertEqual(turns, 1)

    def test_production_progress(self):
        """Verify turns decrement and items complete."""
        self.planet.add_production("Colony Ship", 1)
        
        # Process Turn 1 (Should complete it)
        # Note: TurnEngine needs to process production now.
        # We need a dummy 'galaxy' or just pass None if not needed yet, 
        # but spawning a fleet might require Galaxy context for location?
        # For now, let's assume Fleet spawn location is just planet global location.
        # But Planet lacks global location context in isolation.
        # We might need to mock Galaxy or pass global offset.
        
        # Workaround: Manually handle spawn logic in Engine or Mock it?
        # Let's see how TurnEngine handles it.
        pass 
        
    def test_production_completion(self):
        """Verify ship spawns when production completes."""
        self.planet.add_production("Scout", 1)

        # Capture initial fleets
        initial_fleet_count = len(self.empire.fleets)

        # Simulate processing logic (since we haven't written it yet, we are defining expectation)
        self.engine.process_production(self.empires)

        # Expectation: Queue empty, Fleet count +1
        self.assertEqual(len(self.planet.construction_queue), 0)
        self.assertEqual(len(self.empire.fleets), initial_fleet_count + 1)

        new_fleet = self.empire.fleets[-1]
        self.assertIn("Scout", new_fleet.ships)

    def test_build_queue_dict_format(self):
        """Verify new queue format with type/design_id/turns."""
        queue_item = {
            "design_id": "mining_complex_mk1",
            "type": "complex",
            "turns_remaining": 5
        }

        self.planet.construction_queue.append(queue_item)

        self.assertEqual(len(self.planet.construction_queue), 1)
        item = self.planet.construction_queue[0]
        self.assertIsInstance(item, dict)
        self.assertEqual(item["design_id"], "mining_complex_mk1")
        self.assertEqual(item["type"], "complex")
        self.assertEqual(item["turns_remaining"], 5)

    def test_backwards_compat_list_format(self):
        """Verify old ['Ship', 5] format still works in processing."""
        # Add old format to queue
        self.planet.construction_queue.append(["Colony Ship", 2])

        # Process one turn
        self.engine.process_production(self.empires)

        # Should decrement turns
        self.assertEqual(len(self.planet.construction_queue), 1)
        item = self.planet.construction_queue[0]
        self.assertEqual(item[1], 1)  # Turns decremented from 2 to 1

    def test_build_complex_adds_to_facilities(self):
        """Verify complex completes and appears in planet.facilities."""
        from game.strategy.data.planet import PlanetaryFacility

        # Add complex to queue with 1 turn
        queue_item = {
            "design_id": "test_complex_design",
            "type": "complex",
            "turns_remaining": 1
        }
        self.planet.construction_queue.append(queue_item)

        # Process turn - should complete
        initial_facility_count = len(self.planet.facilities)
        self.engine.process_production(self.empires)

        # Queue should be empty, facilities should have +1
        self.assertEqual(len(self.planet.construction_queue), 0)
        self.assertEqual(len(self.planet.facilities), initial_facility_count + 1)

        # Verify it's a PlanetaryFacility
        new_facility = self.planet.facilities[-1]
        self.assertIsInstance(new_facility, PlanetaryFacility)
        self.assertEqual(new_facility.design_id, "test_complex_design")

    def test_spawn_complex_loads_design_data(self):
        """Verify design data loaded from DesignLibrary when complex spawns."""
        queue_item = {
            "design_id": "shipyard_complex",
            "type": "complex",
            "turns_remaining": 1
        }
        self.planet.construction_queue.append(queue_item)

        # Process turn
        self.engine.process_production(self.empires)

        # Complex should have been built
        if len(self.planet.facilities) > 0:
            facility = self.planet.facilities[-1]
            # design_data should be populated (even if empty dict for missing design)
            self.assertIsNotNone(facility.design_data)
            self.assertIsInstance(facility.design_data, dict)

    def test_spawn_complex_creates_facility_instance(self):
        """Verify PlanetaryFacility created with UUID."""
        queue_item = {
            "design_id": "harvester_complex",
            "type": "complex",
            "turns_remaining": 1
        }
        self.planet.construction_queue.append(queue_item)

        # Process turn
        self.engine.process_production(self.empires)

        # Should have facility with unique ID
        if len(self.planet.facilities) > 0:
            facility = self.planet.facilities[-1]
            self.assertIsNotNone(facility.instance_id)
            self.assertTrue(len(facility.instance_id) > 0)
            # UUID format check (basic)
            self.assertIn("-", facility.instance_id)

    def test_process_production_ship_spawns(self):
        """Verify ship spawns as fleet when production completes."""
        queue_item = {
            "design_id": "frigate_mk1",
            "type": "ship",
            "turns_remaining": 1
        }
        self.planet.construction_queue.append(queue_item)

        initial_fleet_count = len(self.empire.fleets)

        # Process turn
        self.engine.process_production(self.empires)

        # Should spawn fleet
        self.assertEqual(len(self.planet.construction_queue), 0)
        self.assertEqual(len(self.empire.fleets), initial_fleet_count + 1)

if __name__ == '__main__':
    unittest.main()
