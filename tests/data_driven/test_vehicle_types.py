"""
Comprehensive unit tests for vehicle type implementation.
Tests Fighters, Satellites, component restrictions, and AI behavior.
"""
import unittest
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from ship import Ship, initialize_ship_data, load_vehicle_classes, VEHICLE_CLASSES, LayerType
from components import load_components, load_modifiers, get_all_components, COMPONENT_REGISTRY, Bridge, Weapon
from ai import AIController, load_combat_strategies
import pygame


class TestVehicleClassLoading(unittest.TestCase):
    """Test vehicle class definitions load correctly."""
    
    @classmethod
    def setUpClass(cls):
        # Load from TEST data explicitly
        load_vehicle_classes("tests/data/test_vehicleclasses.json")
        load_components("tests/data/test_components.json")
        # Modifiers don't have a test file yet, assume production or none needed?
        # Many tests need modifiers loaded. 
        # For now, load production modifiers if no test modifiers exist.
        try:
            load_modifiers("tests/data/test_modifiers.json")
        except:
            load_modifiers() # Fallback
            
        load_combat_strategies()

    def test_ship_types_defined(self):
        """Verify all expected types exist."""
        types = set(c.get('type', 'Ship') for c in VEHICLE_CLASSES.values())
        self.assertIn("Ship", types)
        self.assertIn("Fighter", types)
        self.assertIn("Satellite", types)

    def test_fighter_classes_loaded(self):
        """Verify Fighter class variants are loaded."""
        fighter_classes = [n for n, c in VEHICLE_CLASSES.items() if c.get('type') == 'Fighter']
        self.assertGreater(len(fighter_classes), 0, "At least one Fighter class should exist")
        # Check specific variants
        self.assertIn("TestFighter_S", VEHICLE_CLASSES)
    
    def test_satellite_classes_loaded(self):
        """Verify Satellite class variants are loaded."""
        sat_classes = [n for n, c in VEHICLE_CLASSES.items() if c.get('type') == 'Satellite']
        self.assertGreater(len(sat_classes), 0, "At least one Satellite class should exist")
        self.assertIn("TestSat_S", VEHICLE_CLASSES)

    def test_fighter_mass_ranges(self):
        """Check Fighter mass ranges are appropriate."""
        small = VEHICLE_CLASSES.get("TestFighter_S", {})
        # Fighters should be light
        self.assertLessEqual(small.get('max_mass', 0), 100)  

    def test_satellite_has_no_propulsion_requirement(self):
        """Verify Satellites do NOT require propulsion."""
        sat = VEHICLE_CLASSES.get("TestSat_S", {})
        # Our test class explicitly has no requirements defined in JSON, so this passes implicitly
        reqs = sat.get('requirements', {})
        # Should NOT have CombatPropulsion requirement
        for req_name, req_def in reqs.items():
            ability = req_def.get('ability', '')
            self.assertNotEqual(ability, 'CombatPropulsion', 
                               "Satellites should not require propulsion")


class TestShipVehicleType(unittest.TestCase):
    """Test Ship class vehicle type handling."""
    
    @classmethod
    def setUpClass(cls):
        load_vehicle_classes("tests/data/test_vehicleclasses.json")
        load_components("tests/data/test_components.json")
        load_modifiers()
        pygame.init()

    def test_ship_vehicle_type_assignment(self):
        """Ship gets correct vehicle type from class."""
        ship = Ship("Test Ship", 0, 0, (255, 0, 0), ship_class="TestShip_S_2L")
        self.assertEqual(ship.vehicle_type, "Ship")
        
        fighter = Ship("Test Fighter", 0, 0, (255, 0, 0), ship_class="TestFighter_S")
        self.assertEqual(fighter.vehicle_type, "Fighter")
        
        sat = Ship("Test Satellite", 0, 0, (255, 0, 0), ship_class="TestSat_S")
        self.assertEqual(sat.vehicle_type, "Satellite")

    def test_default_vehicle_type(self):
        """Unknown class defaults to Ship type."""
        ship = Ship("Test", 0, 0, (255, 0, 0), ship_class="UnknownClass")
        self.assertEqual(ship.vehicle_type, "Ship")


class TestComponentRestrictions(unittest.TestCase):
    """Test component allowed_vehicle_types enforcement."""
    
    @classmethod
    def setUpClass(cls):
        load_vehicle_classes("tests/data/test_vehicleclasses.json")
        load_components("tests/data/test_components.json")
        load_modifiers()
        pygame.init()

    def test_fighter_accepts_fighter_components(self):
        """Fighter can add Fighter-specific components."""
        fighter = Ship("Test", 0, 0, (255, 0, 0), ship_class="TestFighter_S")
        cockpit = COMPONENT_REGISTRY["test_cockpit_fighter"].clone()
        result = fighter.add_component(cockpit, LayerType.CORE)
        self.assertTrue(result, "Fighter should accept Fighter Cockpit")

    def test_fighter_rejects_ship_components(self):
        """Fighter cannot add Ship-only components."""
        fighter = Ship("Test", 0, 0, (255, 0, 0), ship_class="TestFighter_S")
        bridge = COMPONENT_REGISTRY["test_bridge_basic"].clone()
        result = fighter.add_component(bridge, LayerType.CORE)
        self.assertFalse(result, "Fighter should reject standard Bridge")

    def test_satellite_rejects_engines_and_thrusters(self):
        """Satellites cannot add propulsion components."""
        sat = Ship("Test", 0, 0, (255, 0, 0), ship_class="TestSat_S")
        
        engine = COMPONENT_REGISTRY["test_engine_std"].clone()
        # Satellite S only has CORE ("radius_pct": 1.0). 
        # But wait, layer defs matter? No, add_component checks allowed_vehicle_types.
        # Ensure we add to a valid layer. TestSat_S has only CORE.
        result = sat.add_component(engine, LayerType.CORE)
        self.assertFalse(result, "Satellite should reject Engine")
        
        thruster = COMPONENT_REGISTRY["test_thruster_std"].clone()
        result = sat.add_component(thruster, LayerType.CORE)
        self.assertFalse(result, "Satellite should reject Thruster")

    def test_satellite_accepts_weapons(self):
        """Satellites can add allowed weapons."""
        sat = Ship("Test", 0, 0, (255, 0, 0), ship_class="TestSat_S")
        
        railgun = COMPONENT_REGISTRY["test_weapon_proj_fixed"].clone()
        result = sat.add_component(railgun, LayerType.CORE)
        self.assertTrue(result, "Satellite should accept Railgun (Fixed)")
        
        laser = COMPONENT_REGISTRY["test_weapon_beam_std"].clone()
        result = sat.add_component(laser, LayerType.CORE)
        self.assertTrue(result, "Satellite should accept Laser Cannon")

    def test_ship_accepts_ship_components(self):
        """Standard Ship can add Ship components."""
        ship = Ship("Test", 0, 0, (255, 0, 0), ship_class="TestShip_S_2L")
        bridge = COMPONENT_REGISTRY["test_bridge_basic"].clone()
        result = ship.add_component(bridge, LayerType.CORE)
        self.assertTrue(result, "Ship should accept standard Bridge")

    def test_ship_rejects_fighter_components(self):
        """Standard Ship cannot add Fighter-only components."""
        ship = Ship("Test", 0, 0, (255, 0, 0), ship_class="TestShip_S_2L")
        cockpit = COMPONENT_REGISTRY["test_cockpit_fighter"].clone()
        result = ship.add_component(cockpit, LayerType.CORE)
        self.assertFalse(result, "Ship should reject Fighter Cockpit")

    def test_component_allowed_vehicle_types_list(self):
        """Check component has correct allowed_vehicle_types."""
        bridge = COMPONENT_REGISTRY["test_bridge_basic"]
        self.assertIn("Ship", bridge.allowed_vehicle_types)
        self.assertNotIn("Fighter", bridge.allowed_vehicle_types)
        
        sat_core = COMPONENT_REGISTRY["test_core_satellite"]
        self.assertIn("Satellite", sat_core.allowed_vehicle_types)
        self.assertNotIn("Ship", sat_core.allowed_vehicle_types)


class TestSatelliteLogic(unittest.TestCase):
    """Test Satellite-specific game logic."""
    
    @classmethod
    def setUpClass(cls):
        load_vehicle_classes("tests/data/test_vehicleclasses.json")
        load_components("tests/data/test_components.json")
        load_modifiers()
        pygame.init()

    def test_satellite_ignores_crew_requirements(self):
        """Satellite components ignore crew requirements."""
        sat = Ship("Test", 0, 0, (255, 0, 0), ship_class="TestSat_S")
        
        # Railgun normally requires crew (if defined in test data? test_weapon_proj_fixed doesn't have crew reqs currently?)
        # Let's check test_weapon_proj_fixed ability definitions.
        # Wait, my added definitions for test components didn't include CrewRequired logic explicitly for weapons?
        # test_weapon_proj_fixed abilities: {"ProjectileWeapon": true}
        # It needs CrewRequired ability to test this.
        # I should probably use a mocked component or ensure the test component has crew reqs.
        # Or I can clone and add the requirement manually for the test?
        
        railgun = COMPONENT_REGISTRY["test_weapon_proj_fixed"].clone()
        railgun.abilities["CrewRequired"] = 5
        
        sat.add_component(railgun, LayerType.CORE)
        sat.recalculate_stats()
        
        # Crew required should be 0 for satellite
        self.assertEqual(sat.crew_required, 0, 
                        "Satellite should have 0 crew required")
        # Weapon should be active
        self.assertTrue(railgun.is_active, 
                       "Railgun on Satellite should be active despite no crew")


class TestSatelliteAI(unittest.TestCase):
    """Test AI behavior specific to Satellites."""
    
    @classmethod
    def setUpClass(cls):
        load_vehicle_classes("tests/data/test_vehicleclasses.json")
        load_components("tests/data/test_components.json")
        load_modifiers()
        load_combat_strategies()
        pygame.init()

    def setUp(self):
        # Create a basic spatial grid mock
        class MockGrid:
            def query_radius(self, pos, radius):
                return []
        self.grid = MockGrid()

    def test_satellite_ai_does_not_navigate(self):
        """Satellite AI should NOT call navigation/movement methods."""
        sat = Ship("Test Sat", 0, 0, (255, 0, 0), ship_class="TestSat_S")
        core = COMPONENT_REGISTRY["test_core_satellite"].clone()
        sat.add_component(core, LayerType.CORE)
        sat.recalculate_stats()
        
        ai = AIController(sat, self.grid, enemy_team_id=1)
        
        # Run AI update
        original_position = pygame.math.Vector2(sat.position)
        original_angle = sat.angle
        original_velocity = pygame.math.Vector2(sat.velocity)
        
        ai.update()
        
        # Position, angle, velocity should NOT change
        self.assertEqual(sat.position.x, original_position.x)
        self.assertEqual(sat.position.y, original_position.y)
        self.assertEqual(sat.angle, original_angle)
        self.assertEqual(sat.velocity.x, original_velocity.x)
        self.assertEqual(sat.velocity.y, original_velocity.y)

    def test_satellite_ai_still_targets(self):
        """Satellite AI should still acquire targets."""
        sat = Ship("Test Sat", 100, 100, (255, 0, 0), team_id=0, 
                   ship_class="TestSat_S")
        core = COMPONENT_REGISTRY["test_core_satellite"].clone()
        sat.add_component(core, LayerType.CORE)
        sat.recalculate_stats()
        
        # Create enemy
        enemy = Ship("Enemy", 200, 200, (0, 255, 0), team_id=1, ship_class="TestShip_S_2L")
        enemy.is_alive = True
        
        class MockGridWithEnemy:
            def query_radius(self, pos, radius):
                return [enemy]
        
        ai = AIController(sat, MockGridWithEnemy(), enemy_team_id=1)
        ai.update()
        
        # Satellite should find and target enemy
        self.assertEqual(sat.current_target, enemy)

    def test_satellite_ai_fires_when_has_target(self):
        """Satellite AI should set comp_trigger_pulled when target exists."""
        sat = Ship("Test Sat", 100, 100, (255, 0, 0), team_id=0,
                   ship_class="TestSat_S")
        core = COMPONENT_REGISTRY["test_core_satellite"].clone()
        sat.add_component(core, LayerType.CORE)
        
        railgun = COMPONENT_REGISTRY["test_weapon_proj_fixed"].clone()
        sat.add_component(railgun, LayerType.CORE)
        sat.recalculate_stats()
        
        # Create enemy
        enemy = Ship("Enemy", 200, 200, (0, 255, 0), team_id=1, ship_class="TestShip_S_2L")
        enemy.is_alive = True
        
        class MockGridWithEnemy:
            def query_radius(self, pos, radius):
                return [enemy]
        
        ai = AIController(sat, MockGridWithEnemy(), enemy_team_id=1)
        ai.update()
        
        # Trigger should be pulled
        self.assertTrue(sat.comp_trigger_pulled, 
                       "Satellite AI should pull trigger when target exists")


class TestFighterLogic(unittest.TestCase):
    """Test Fighter-specific game logic."""
    
    @classmethod
    def setUpClass(cls):
        load_vehicle_classes("tests/data/test_vehicleclasses.json")
        load_components("tests/data/test_components.json")
        load_modifiers()
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()


if __name__ == '__main__':
    unittest.main()
