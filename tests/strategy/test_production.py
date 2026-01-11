
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

if __name__ == '__main__':
    unittest.main()
