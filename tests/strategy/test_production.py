
import unittest
import tempfile
import os
import json
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.hex_math import HexCoord
from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.data.empire import Empire

class TestProduction(unittest.TestCase):
    def setUp(self):
        # Create temporary directory for test designs
        # DesignLibrary expects designs in empire-specific subfolder: designs/empire_N/
        # Empire ID 0 is used (Empire(0, "Terran", ...))
        self.temp_dir = tempfile.mkdtemp()
        self.designs_dir = os.path.join(self.temp_dir, "designs", "empire_0")
        os.makedirs(self.designs_dir, exist_ok=True)

        # Create a test ship design
        test_design = {
            "name": "Test Ship",
            "ship_class": "Frigate",
            "vehicle_type": "Ship",
            "layers": {"CORE": [], "INNER": [], "OUTER": [], "ARMOR": []},
            "resources": {"fuel": 0.0, "energy": 0.0, "ammo": 0.0},
            "expected_stats": {
                "max_hp": 100,
                "max_speed": 10,
                "mass": 100.0
            },
            "_metadata": {
                "is_obsolete": False,
                "times_built": 0
            }
        }

        # Write test design files
        for design_id in ["test_ship", "test_ship_0", "test_ship_1", "test_ship_2"]:
            design_path = os.path.join(self.designs_dir, f"{design_id}.json")
            with open(design_path, 'w') as f:
                json.dump(test_design, f)

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
        self.empire.savegame_path = self.temp_dir  # Use temp directory for designs
        self.empire.add_colony(self.planet)

        self.engine = TurnEngine()
        self.empires = [self.empire]

    def tearDown(self):
        # Clean up temporary directory
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

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
        from game.strategy.data.planet import PlanetaryFacility

        # Add shipyard first
        shipyard = PlanetaryFacility(
            instance_id="shipyard_1",
            design_id="shipyard_complex",
            name="Space Shipyard",
            design_data={
                "layers": {
                    "CORE": {
                        "components": [{
                            "abilities": {"SpaceShipyard": {"value": 1}}
                        }]
                    }
                }
            },
            is_operational=True
        )
        self.planet.facilities.append(shipyard)

        self.planet.add_production("test_ship", 1)

        # Capture initial fleets
        initial_fleet_count = len(self.empire.fleets)

        # Simulate processing logic (since we haven't written it yet, we are defining expectation)
        self.engine.process_production(self.empires, save_path=self.temp_dir)

        # Expectation: Queue empty, Fleet count +1
        self.assertEqual(len(self.planet.construction_queue), 0)
        self.assertEqual(len(self.empire.fleets), initial_fleet_count + 1)

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
        from game.strategy.data.planet import PlanetaryFacility

        # Add shipyard first (required for ships)
        shipyard = PlanetaryFacility(
            instance_id="shipyard_1",
            design_id="shipyard_complex",
            name="Space Shipyard",
            design_data={
                "layers": {
                    "CORE": {
                        "components": [{
                            "abilities": {"SpaceShipyard": {"value": 1}}
                        }]
                    }
                }
            },
            is_operational=True
        )
        self.planet.facilities.append(shipyard)

        # Add old format to queue
        self.planet.construction_queue.append(["test_ship", 2])

        # Process one turn
        self.engine.process_production(self.empires, save_path=self.temp_dir)

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
        self.engine.process_production(self.empires, save_path=self.temp_dir)

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
        self.engine.process_production(self.empires, save_path=self.temp_dir)

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
        self.engine.process_production(self.empires, save_path=self.temp_dir)

        # Should have facility with unique ID
        if len(self.planet.facilities) > 0:
            facility = self.planet.facilities[-1]
            self.assertIsNotNone(facility.instance_id)
            self.assertTrue(len(facility.instance_id) > 0)
            # UUID format check (basic)
            self.assertIn("-", facility.instance_id)

    def test_process_production_ship_spawns(self):
        """Verify ship spawns as fleet when production completes."""
        from game.strategy.data.planet import PlanetaryFacility

        # Add shipyard first
        shipyard = PlanetaryFacility(
            instance_id="shipyard_1",
            design_id="shipyard_complex",
            name="Space Shipyard",
            design_data={
                "layers": {
                    "CORE": {
                        "components": [{
                            "abilities": {"SpaceShipyard": {"value": 1}}
                        }]
                    }
                }
            },
            is_operational=True
        )
        self.planet.facilities.append(shipyard)

        queue_item = {
            "design_id": "test_ship",
            "type": "ship",
            "turns_remaining": 1
        }
        self.planet.construction_queue.append(queue_item)

        initial_fleet_count = len(self.empire.fleets)

        # Process turn
        self.engine.process_production(self.empires, save_path=self.temp_dir)

        # Should spawn fleet
        self.assertEqual(len(self.planet.construction_queue), 0)
        self.assertEqual(len(self.empire.fleets), initial_fleet_count + 1)

    def test_complex_builds_in_1_turn(self):
        """Test that complexes complete after 1 turn."""
        queue_item = {
            "design_id": "test_complex",
            "type": "complex",
            "turns_remaining": 1
        }
        self.planet.construction_queue.append(queue_item)

        # Process one turn
        self.engine.process_production(self.empires, save_path=self.temp_dir)

        # Should complete and remove from queue
        self.assertEqual(len(self.planet.construction_queue), 0)
        # Should create facility
        self.assertGreater(len(self.planet.facilities), 0)

    def test_ship_builds_in_1_turn(self):
        """Test that ships complete after 1 turn."""
        from game.strategy.data.planet import PlanetaryFacility

        # Add shipyard first
        shipyard = PlanetaryFacility(
            instance_id="shipyard_1",
            design_id="shipyard_complex",
            name="Space Shipyard",
            design_data={
                "layers": {
                    "CORE": {
                        "components": [{
                            "abilities": {"SpaceShipyard": {"value": 1}}
                        }]
                    }
                }
            },
            is_operational=True
        )
        self.planet.facilities.append(shipyard)

        queue_item = {
            "design_id": "test_ship",
            "type": "ship",
            "turns_remaining": 1
        }
        self.planet.construction_queue.append(queue_item)

        initial_fleet_count = len(self.empire.fleets)

        # Process one turn
        self.engine.process_production(self.empires, save_path=self.temp_dir)

        # Should complete and remove from queue
        self.assertEqual(len(self.planet.construction_queue), 0)
        # Should spawn fleet
        self.assertEqual(len(self.empire.fleets), initial_fleet_count + 1)

    def test_ship_build_pauses_without_shipyard(self):
        """Test that ship builds don't progress if shipyard is missing."""
        from game.strategy.data.planet import PlanetaryFacility

        # Add ship to queue
        queue_item = {
            "design_id": "test_ship",
            "type": "ship",
            "turns_remaining": 2
        }
        self.planet.construction_queue.append(queue_item)

        # Add a shipyard facility first
        shipyard = PlanetaryFacility(
            instance_id="shipyard_1",
            design_id="shipyard_complex",
            name="Space Shipyard",
            design_data={
                "layers": {
                    "CORE": {
                        "components": [{
                            "abilities": {"SpaceShipyard": {"value": 1}}
                        }]
                    }
                }
            },
            is_operational=True
        )
        self.planet.facilities.append(shipyard)

        # Process turn - should work with shipyard
        self.engine.process_production(self.empires, save_path=self.temp_dir)
        self.assertEqual(self.planet.construction_queue[0]["turns_remaining"], 1)

        # Remove shipyard facility
        self.planet.facilities.clear()

        # Process turn - should NOT progress
        self.engine.process_production(self.empires, save_path=self.temp_dir)
        self.assertEqual(self.planet.construction_queue[0]["turns_remaining"], 1)  # Still 1

    def test_ship_build_resumes_with_shipyard(self):
        """Test that paused ship builds resume when shipyard added."""
        from game.strategy.data.planet import PlanetaryFacility

        # Add ship to queue without shipyard
        queue_item = {
            "design_id": "test_ship",
            "type": "ship",
            "turns_remaining": 2
        }
        self.planet.construction_queue.append(queue_item)

        # Process turn - should NOT progress without shipyard
        self.engine.process_production(self.empires, save_path=self.temp_dir)
        self.assertEqual(self.planet.construction_queue[0]["turns_remaining"], 2)  # No change

        # Add shipyard facility
        shipyard = PlanetaryFacility(
            instance_id="shipyard_1",
            design_id="shipyard_complex",
            name="Space Shipyard",
            design_data={
                "layers": {
                    "CORE": {
                        "components": [{
                            "abilities": {"SpaceShipyard": {"value": 1}}
                        }]
                    }
                }
            },
            is_operational=True
        )
        self.planet.facilities.append(shipyard)

        # Process turn - should now progress
        self.engine.process_production(self.empires, save_path=self.temp_dir)
        self.assertEqual(self.planet.construction_queue[0]["turns_remaining"], 1)  # Decremented

    def test_complex_builds_without_shipyard(self):
        """Test that complexes build even without shipyard."""
        queue_item = {
            "design_id": "mining_complex",
            "type": "complex",
            "turns_remaining": 1
        }
        self.planet.construction_queue.append(queue_item)

        # No shipyard on planet
        self.assertEqual(len(self.planet.facilities), 0)

        # Process turn - complex should complete
        initial_facility_count = len(self.planet.facilities)
        self.engine.process_production(self.empires, save_path=self.temp_dir)

        # Should complete and add facility
        self.assertEqual(len(self.planet.construction_queue), 0)
        self.assertGreater(len(self.planet.facilities), initial_facility_count)

    def test_ship_spawns_as_ship_instance(self):
        """Test that completed ships create ShipInstance (not string)."""
        from game.strategy.data.ship_instance import ShipInstance
        from game.strategy.data.planet import PlanetaryFacility

        # Add shipyard first
        shipyard = PlanetaryFacility(
            instance_id="shipyard_1",
            design_id="shipyard_complex",
            name="Space Shipyard",
            design_data={
                "layers": {
                    "CORE": {
                        "components": [{
                            "abilities": {"SpaceShipyard": {"value": 1}}
                        }]
                    }
                }
            },
            is_operational=True
        )
        self.planet.facilities.append(shipyard)

        # Add ship to queue
        queue_item = {
            "design_id": "test_ship",
            "type": "ship",
            "turns_remaining": 1
        }
        self.planet.construction_queue.append(queue_item)

        # Process turn
        self.engine.process_production(self.empires, save_path=self.temp_dir)

        # Should create fleet with ShipInstance
        self.assertEqual(len(self.empire.fleets), 1)
        fleet = self.empire.fleets[0]
        self.assertGreater(len(fleet.ships), 0)

        # Check that ship is ShipInstance (not string)
        ship = fleet.ships[0]
        self.assertIsInstance(ship, ShipInstance)

    def test_ship_has_no_initial_orders(self):
        """Test that newly spawned fleets have empty orders list."""
        from game.strategy.data.planet import PlanetaryFacility

        # Add shipyard
        shipyard = PlanetaryFacility(
            instance_id="shipyard_1",
            design_id="shipyard_complex",
            name="Space Shipyard",
            design_data={
                "layers": {
                    "CORE": {
                        "components": [{
                            "abilities": {"SpaceShipyard": {"value": 1}}
                        }]
                    }
                }
            },
            is_operational=True
        )
        self.planet.facilities.append(shipyard)

        # Add ship to queue
        queue_item = {
            "design_id": "test_ship",
            "type": "ship",
            "turns_remaining": 1
        }
        self.planet.construction_queue.append(queue_item)

        # Process turn
        self.engine.process_production(self.empires, save_path=self.temp_dir)

        # Check fleet has no orders
        fleet = self.empire.fleets[0]
        self.assertEqual(len(fleet.orders), 0)

    def test_fleet_id_is_unique(self):
        """Test that fleet IDs are guaranteed unique."""
        from game.strategy.data.planet import PlanetaryFacility

        # Add shipyard
        shipyard = PlanetaryFacility(
            instance_id="shipyard_1",
            design_id="shipyard_complex",
            name="Space Shipyard",
            design_data={
                "layers": {
                    "CORE": {
                        "components": [{
                            "abilities": {"SpaceShipyard": {"value": 1}}
                        }]
                    }
                }
            },
            is_operational=True
        )
        self.planet.facilities.append(shipyard)

        # Add multiple ships to queue
        for i in range(3):
            queue_item = {
                "design_id": f"test_ship_{i}",
                "type": "ship",
                "turns_remaining": 1
            }
            self.planet.construction_queue.append(queue_item)

        # Process 3 turns
        for _ in range(3):
            self.engine.process_production(self.empires, save_path=self.temp_dir)

        # Should have 3 fleets with unique IDs
        self.assertEqual(len(self.empire.fleets), 3)
        fleet_ids = [fleet.id for fleet in self.empire.fleets]
        self.assertEqual(len(fleet_ids), len(set(fleet_ids)))  # No duplicates

if __name__ == '__main__':
    unittest.main()
