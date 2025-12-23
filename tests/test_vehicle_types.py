"""
Comprehensive unit tests for vehicle type implementation.
Tests Fighters, Satellites, component restrictions, and AI behavior.
"""
import unittest
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from ship import Ship, initialize_ship_data, VEHICLE_CLASSES, LayerType
from components import load_components, load_modifiers, get_all_components, COMPONENT_REGISTRY, Bridge, Weapon
from ai import AIController, load_combat_strategies
import pygame


class TestVehicleClassLoading(unittest.TestCase):
    """Test vehicle class definitions load correctly."""
    
    @classmethod
    def setUpClass(cls):
        initialize_ship_data()
        load_components()
        load_modifiers()
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
        self.assertIn("Fighter (Small)", VEHICLE_CLASSES)
        self.assertIn("Fighter (Heavy)", VEHICLE_CLASSES)
    
    def test_satellite_classes_loaded(self):
        """Verify Satellite class variants are loaded."""
        sat_classes = [n for n, c in VEHICLE_CLASSES.items() if c.get('type') == 'Satellite']
        self.assertGreater(len(sat_classes), 0, "At least one Satellite class should exist")
        self.assertIn("Satellite (Small)", VEHICLE_CLASSES)
        self.assertIn("Satellite (Heavy)", VEHICLE_CLASSES)

    def test_fighter_mass_ranges(self):
        """Check Fighter mass ranges are appropriate."""
        small = VEHICLE_CLASSES.get("Fighter (Small)", {})
        heavy = VEHICLE_CLASSES.get("Fighter (Heavy)", {})
        # Fighters should be light
        self.assertLessEqual(small.get('max_mass', 0), 100)  
        self.assertLessEqual(heavy.get('max_mass', 0), 200)

    def test_satellite_has_no_propulsion_requirement(self):
        """Verify Satellites do NOT require propulsion."""
        sat = VEHICLE_CLASSES.get("Satellite (Small)", {})
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
        initialize_ship_data()
        load_components()
        load_modifiers()
        pygame.init()

    def test_ship_vehicle_type_assignment(self):
        """Ship gets correct vehicle type from class."""
        ship = Ship("Test Ship", 0, 0, (255, 0, 0), ship_class="Escort")
        self.assertEqual(ship.vehicle_type, "Ship")
        
        fighter = Ship("Test Fighter", 0, 0, (255, 0, 0), ship_class="Fighter (Small)")
        self.assertEqual(fighter.vehicle_type, "Fighter")
        
        sat = Ship("Test Satellite", 0, 0, (255, 0, 0), ship_class="Satellite (Small)")
        self.assertEqual(sat.vehicle_type, "Satellite")

    def test_default_vehicle_type(self):
        """Unknown class defaults to Ship type."""
        ship = Ship("Test", 0, 0, (255, 0, 0), ship_class="UnknownClass")
        self.assertEqual(ship.vehicle_type, "Ship")


class TestComponentRestrictions(unittest.TestCase):
    """Test component allowed_vehicle_types enforcement."""
    
    @classmethod
    def setUpClass(cls):
        initialize_ship_data()
        load_components()
        load_modifiers()
        pygame.init()

    def test_fighter_accepts_fighter_components(self):
        """Fighter can add Fighter-specific components."""
        fighter = Ship("Test", 0, 0, (255, 0, 0), ship_class="Fighter (Small)")
        cockpit = COMPONENT_REGISTRY["fighter_cockpit"].clone()
        result = fighter.add_component(cockpit, LayerType.CORE)
        self.assertTrue(result, "Fighter should accept Fighter Cockpit")

    def test_fighter_rejects_ship_components(self):
        """Fighter cannot add Ship-only components."""
        fighter = Ship("Test", 0, 0, (255, 0, 0), ship_class="Fighter (Small)")
        bridge = COMPONENT_REGISTRY["bridge"].clone()
        result = fighter.add_component(bridge, LayerType.CORE)
        self.assertFalse(result, "Fighter should reject standard Bridge")

    def test_satellite_rejects_engines_and_thrusters(self):
        """Satellites cannot add propulsion components."""
        sat = Ship("Test", 0, 0, (255, 0, 0), ship_class="Satellite (Small)")
        
        engine = COMPONENT_REGISTRY["standard_engine"].clone()
        result = sat.add_component(engine, LayerType.INNER)
        self.assertFalse(result, "Satellite should reject Engine")
        
        thruster = COMPONENT_REGISTRY["thruster"].clone()
        result = sat.add_component(thruster, LayerType.OUTER)
        self.assertFalse(result, "Satellite should reject Thruster")

    def test_satellite_accepts_weapons(self):
        """Satellites can add allowed weapons."""
        sat = Ship("Test", 0, 0, (255, 0, 0), ship_class="Satellite (Small)")
        
        railgun = COMPONENT_REGISTRY["railgun"].clone()
        result = sat.add_component(railgun, LayerType.OUTER)
        self.assertTrue(result, "Satellite should accept Railgun")
        
        laser = COMPONENT_REGISTRY["laser_cannon"].clone()
        result = sat.add_component(laser, LayerType.OUTER)
        self.assertTrue(result, "Satellite should accept Laser Cannon")

    def test_ship_accepts_ship_components(self):
        """Standard Ship can add Ship components."""
        ship = Ship("Test", 0, 0, (255, 0, 0), ship_class="Escort")
        bridge = COMPONENT_REGISTRY["bridge"].clone()
        result = ship.add_component(bridge, LayerType.CORE)
        self.assertTrue(result, "Ship should accept standard Bridge")

    def test_ship_rejects_fighter_components(self):
        """Standard Ship cannot add Fighter-only components."""
        ship = Ship("Test", 0, 0, (255, 0, 0), ship_class="Escort")
        cockpit = COMPONENT_REGISTRY["fighter_cockpit"].clone()
        result = ship.add_component(cockpit, LayerType.CORE)
        self.assertFalse(result, "Ship should reject Fighter Cockpit")

    def test_component_allowed_vehicle_types_list(self):
        """Check component has correct allowed_vehicle_types."""
        bridge = COMPONENT_REGISTRY["bridge"]
        self.assertIn("Ship", bridge.allowed_vehicle_types)
        self.assertNotIn("Fighter", bridge.allowed_vehicle_types)
        
        sat_core = COMPONENT_REGISTRY["satellite_core"]
        self.assertIn("Satellite", sat_core.allowed_vehicle_types)
        self.assertNotIn("Ship", sat_core.allowed_vehicle_types)


class TestSatelliteLogic(unittest.TestCase):
    """Test Satellite-specific game logic."""
    
    @classmethod
    def setUpClass(cls):
        initialize_ship_data()
        load_components()
        load_modifiers()
        pygame.init()

    def test_satellite_not_derelict_without_engines(self):
        """Satellite with Core is NOT derelict even without propulsion."""
        sat = Ship("Test Sat", 0, 0, (255, 0, 0), ship_class="Satellite (Small)")
        
        # Add satellite core (command)
        core = COMPONENT_REGISTRY["satellite_core"].clone()
        sat.add_component(core, LayerType.CORE)
        sat.recalculate_stats()
        
        # Should have 0 thrust but NOT be derelict
        self.assertEqual(sat.total_thrust, 0)
        self.assertFalse(sat.is_derelict, 
                        "Satellite with Core should NOT be derelict")

    def test_ship_is_derelict_without_engines(self):
        """Standard Ship WITH bridge but NO engines IS derelict."""
        ship = Ship("Test", 0, 0, (255, 0, 0), ship_class="Escort")
        bridge = COMPONENT_REGISTRY["bridge"].clone()
        ship.add_component(bridge, LayerType.CORE)
        ship.recalculate_stats()
        
        self.assertEqual(ship.total_thrust, 0)
        self.assertTrue(ship.is_derelict, 
                       "Ship with 0 thrust SHOULD be derelict")

    def test_satellite_derelict_without_core(self):
        """Satellite WITHOUT command is derelict."""
        sat = Ship("Test", 0, 0, (255, 0, 0), ship_class="Satellite (Small)")
        # Don't add core
        sat.recalculate_stats()
        
        self.assertTrue(sat.is_derelict, 
                       "Satellite without Core SHOULD be derelict")

    def test_satellite_ignores_crew_requirements(self):
        """Satellite components ignore crew requirements."""
        sat = Ship("Test", 0, 0, (255, 0, 0), ship_class="Satellite (Small)")
        
        # Railgun normally requires 5 crew
        railgun = COMPONENT_REGISTRY["railgun"].clone()
        sat.add_component(railgun, LayerType.OUTER)
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
        initialize_ship_data()
        load_components()
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
        sat = Ship("Test Sat", 0, 0, (255, 0, 0), ship_class="Satellite (Small)")
        core = COMPONENT_REGISTRY["satellite_core"].clone()
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
                   ship_class="Satellite (Small)")
        core = COMPONENT_REGISTRY["satellite_core"].clone()
        sat.add_component(core, LayerType.CORE)
        sat.recalculate_stats()
        
        # Create enemy
        enemy = Ship("Enemy", 200, 200, (0, 255, 0), team_id=1, ship_class="Escort")
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
                   ship_class="Satellite (Small)")
        core = COMPONENT_REGISTRY["satellite_core"].clone()
        sat.add_component(core, LayerType.CORE)
        
        railgun = COMPONENT_REGISTRY["railgun"].clone()
        sat.add_component(railgun, LayerType.OUTER)
        sat.recalculate_stats()
        
        # Create enemy
        enemy = Ship("Enemy", 200, 200, (0, 255, 0), team_id=1, ship_class="Escort")
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
        initialize_ship_data()
        load_components()
        load_modifiers()
        pygame.init()

    def test_fighter_requires_propulsion(self):
        """Fighter without propulsion is derelict."""
        fighter = Ship("Test", 0, 0, (255, 0, 0), ship_class="Fighter (Small)")
        cockpit = COMPONENT_REGISTRY["fighter_cockpit"].clone()
        fighter.add_component(cockpit, LayerType.CORE)
        fighter.recalculate_stats()
        
        # No engine = derelict
        self.assertTrue(fighter.is_derelict, 
                       "Fighter without engine SHOULD be derelict")

    def test_fighter_with_engine_not_derelict(self):
        """Fighter with cockpit AND engine is NOT derelict."""
        fighter = Ship("Test", 0, 0, (255, 0, 0), ship_class="Fighter (Small)")
        cockpit = COMPONENT_REGISTRY["fighter_cockpit"].clone()
        engine = COMPONENT_REGISTRY["mini_engine"].clone()
        
        fighter.add_component(cockpit, LayerType.CORE)
        fighter.add_component(engine, LayerType.INNER)
        fighter.recalculate_stats()
        
        self.assertFalse(fighter.is_derelict)
        self.assertGreater(fighter.total_thrust, 0)


class TestTargetingExclusion(unittest.TestCase):
    """Test that derelict ships are excluded from targeting."""
    
    @classmethod
    def setUpClass(cls):
        initialize_ship_data()
        load_components()
        load_modifiers()
        load_combat_strategies()
        pygame.init()

    def test_derelict_excluded_from_targeting(self):
        """Derelict ships should not be targeted."""
        attacker = Ship("Attacker", 0, 0, (255, 0, 0), team_id=0, ship_class="Escort")
        
        # Create a derelict enemy (no bridge)
        derelict = Ship("Derelict", 100, 100, (0, 255, 0), team_id=1, ship_class="Escort")
        derelict.is_alive = True
        derelict.is_derelict = True
        
        class MockGrid:
            def query_radius(self, pos, radius):
                return [derelict]
        
        ai = AIController(attacker, MockGrid(), enemy_team_id=1)
        target = ai.find_target()
        
        # Should NOT target derelict
        self.assertIsNone(target, "AI should not target derelict ships")

    def test_active_satellite_can_be_targeted(self):
        """Active (non-derelict) Satellite CAN be targeted."""
        attacker = Ship("Attacker", 0, 0, (255, 0, 0), team_id=0, ship_class="Escort")
        
        # Create active satellite
        sat = Ship("Enemy Sat", 100, 100, (0, 255, 0), team_id=1, 
                   ship_class="Satellite (Small)")
        core = COMPONENT_REGISTRY["satellite_core"].clone()
        sat.add_component(core, LayerType.CORE)
        sat.recalculate_stats()
        sat.is_alive = True
        
        class MockGrid:
            def query_radius(self, pos, radius):
                return [sat]
        
        ai = AIController(attacker, MockGrid(), enemy_team_id=1)
        target = ai.find_target()
        
        # SHOULD target active satellite
        self.assertEqual(target, sat, 
                        "AI should target active Satellite")


if __name__ == '__main__':
    unittest.main()
