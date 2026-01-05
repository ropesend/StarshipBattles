import unittest
import pygame
import math
import sys
import os

# Adjust path to find modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from game.simulation.entities.ship import Ship, LayerType, initialize_ship_data, load_vehicle_classes
from game.simulation.components.component import Weapon, BeamWeapon, ProjectileWeapon, SeekerWeapon, create_component, load_components
from ship_combat import ShipCombatMixin
from game.core.constants import AttackType

import pytest

@pytest.mark.use_custom_data
class TestCombatTargeting(unittest.TestCase):
    """
    Test suite for combat targeting logic in ship_combat.py.
    Covers:
    1. Lead Calculation (solve_lead)
    2. Firing Arc Validation
    3. Target Prioritization
    4. Point Defense (PDC) Logic
    5. Resource Consumption
    """

    @classmethod
    def setUpClass(cls):
        # pygame.init() removed for session isolation
        pass

    @classmethod
    def tearDownClass(cls):
        pass # pygame.quit() removed for session isolation

    def setUp(self):
        # 1. Reload CUSTOM test data
        try:
            load_vehicle_classes("tests/unit/data/test_vehicleclasses.json")
            load_components("tests/unit/data/test_components.json")
            from game.core.registry import RegistryManager
            print(f"DEBUG: Registry has {len(RegistryManager.instance().components)} components")
        except Exception as e:
            print(f"DEBUG: Error loading components: {e}")
            # Fallback (shouldn't be reached if paths are correct)
            load_vehicle_classes("tests/unit/data/test_vehicleclasses.json")
            load_components("tests/unit/data/test_components.json")

        # 2. Create ships
        self.attacker = Ship("Attacker", 0, 0, (255, 0, 0))
        bridge = create_component('test_bridge_basic')
        print(f"DEBUG: create_component('test_bridge_basic') -> {bridge}")
        if bridge:
             success = self.attacker.add_component(bridge, LayerType.CORE)
             print(f"DEBUG: Add bridge success: {success}, total core: {len(self.attacker.layers[LayerType.CORE]['components'])}")
        
        self.attacker.team_id = 0
        self.attacker.recalculate_stats() # Init basic stats
        self.attacker.is_alive = True
        self.attacker.is_derelict = False
        self.attacker.current_energy = 1000
        self.attacker.max_energy = 1000
        self.attacker.current_ammo = 100
        self.attacker.velocity = pygame.math.Vector2(0, 0)
        
        # Create target ship
        self.target = Ship("Target", 200, 0, (0, 0, 255))
        self.target.team_id = 1
        self.target.add_component(create_component('test_bridge_basic'), LayerType.CORE)
        self.target.recalculate_stats()
        self.target.is_alive = True
        self.target.velocity = pygame.math.Vector2(0, 0)
        self.target.position = pygame.math.Vector2(200, 0)

    # --- Lead Calculation Tests ---

    def test_solve_lead_stationary(self):
        """Test lead calculation against a stationary target."""
        # Target stationary at 200,0. Proj speed 10/tick. Should take 20 ticks.
        t = self.attacker.solve_lead(
            pygame.math.Vector2(0, 0), pygame.math.Vector2(0, 0),
            pygame.math.Vector2(200, 0), pygame.math.Vector2(0, 0),
            10.0
        )
        self.assertAlmostEqual(t, 20.0)

    def test_solve_lead_moving_target(self):
        """Test lead calculation against a moving target (90 degree intercept)."""
        # Attacker at 0,0. Target at 100,0 moving UP (0,10). Proj speed 20.
        t = self.attacker.solve_lead(
            pygame.math.Vector2(0, 0), pygame.math.Vector2(0, 0),
            pygame.math.Vector2(100, 0), pygame.math.Vector2(0, 10),
            20.0
        )
        self.assertGreater(t, 0)
        self.assertAlmostEqual(t, 10.0 / math.sqrt(3), places=4)

    def test_move_head_on_collision(self):
         """Test lead calculation for head-on collision course."""
         # Attacker 0,0. Target 100,0 moving Left (-10,0). Proj Speed 10 (Right).
         t = self.attacker.solve_lead(
             pygame.math.Vector2(0, 0), pygame.math.Vector2(0, 0),
             pygame.math.Vector2(100, 0), pygame.math.Vector2(-10, 0),
             10.0
         )
         self.assertAlmostEqual(t, 5.0)

    def test_solve_lead_impossible(self):
        """Test lead calculation when target cannot be hit (too fast)."""
        t = self.attacker.solve_lead(
            pygame.math.Vector2(0, 0), pygame.math.Vector2(0, 0),
            pygame.math.Vector2(100, 0), pygame.math.Vector2(20, 0),
            10.0 
        )
        self.assertEqual(t, 0)

    # --- Firing Arc Validation Tests ---

    def test_firing_arc_validation(self):
        """Test that weapons do not fire if target is outside firing arc."""
        weapon = ProjectileWeapon({
            'name': 'TestGun', 'id':'test_gun', 'firing_arc': 45, 'range': 500,
            'projectile_speed': 1000, 'damage': 10, 'ammo_cost': 1, 'cooldown': 0,
            'mass': 1, 'hp': 1, 'allowed_layers': ['OUTER'], 'type': 'Weapon'
        })
        weapon.facing_angle = 0 # Right
        weapon.is_active = True
        weapon.cooldown_timer = 0
        self.attacker.add_component(weapon, LayerType.OUTER)
        self.attacker.angle = 0 

        # Case 1: Target directly ahead (Valid)
        self.target.position = pygame.math.Vector2(200, 0) # 0 degrees
        self.attacker.current_target = self.target
        self.attacker.is_derelict = False
        attacks = self.attacker.fire_weapons()
        self.assertEqual(len(attacks), 1, "Should fire at target directly ahead")

        # Case 2: Target at 90 degrees (Invalid)
        # Reset cooldown
        weapon.cooldown_timer = 0
        weapon.shots_fired = 0
        self.target.position = pygame.math.Vector2(0, 200) # 90 degrees
        self.attacker.is_derelict = False
        attacks = self.attacker.fire_weapons()
        self.assertEqual(len(attacks), 0, "Should not fire at target outside arc (90 > 45)")

        # Case 3: Target at 45 degrees (Boundary Valid)
        # With new "Total Arc" logic, 45 deg target requires 90 deg arc (±45)
        weapon.firing_arc = 90 
        weapon.cooldown_timer = 0
        self.target.position = pygame.math.Vector2(100, 100) 
        self.attacker.is_derelict = False
        attacks = self.attacker.fire_weapons()
        self.assertEqual(len(attacks), 1, "Should fire at target exactly on arc boundary (45 deg) with 90 deg arc")

    def test_seeker_ignores_arc(self):
        """Verify SeekerWeapon fires even if target is outside arc."""
        missile_launcher = SeekerWeapon({
            'name': 'Missile', 'id':'test_missile', 'firing_arc': 10, 'range': 1000,
            'projectile_speed': 500, 'ammo_cost': 1, 'damage': 10, 'endurance': 100,
            'mass': 1, 'hp': 1, 'allowed_layers': ['OUTER'], 'type': 'Weapon'
        })
        missile_launcher.facing_angle = 0
        missile_launcher.is_active = True
        self.attacker.add_component(missile_launcher, LayerType.OUTER)
        
        # Target behind
        self.target.position = pygame.math.Vector2(-200, 0) 
        self.attacker.current_target = self.target
        self.attacker.is_derelict = False
        
        attacks = self.attacker.fire_weapons()
        self.assertEqual(len(attacks), 1, "Seeker weapon should fire regardless of arc")
        self.assertEqual(attacks[0].type, AttackType.MISSILE)

    # --- Target Prioritization Tests ---

    def test_target_prioritization(self):
        """Test that secondary targets are checked if current target is invalid or out of arc."""
        self.attacker.max_targets = 2
        
        # Weapon with narrow arc
        weapon = ProjectileWeapon({
            'name': 'Gun', 'id':'gun', 'firing_arc': 45, 'range': 500,
            'projectile_speed': 1000, 'damage':10, 'ammo_cost':1,
             'mass': 1, 'hp': 1, 'allowed_layers': ['OUTER'], 'type': 'Weapon'
        })
        weapon.facing_angle = 0      
        weapon.is_active = True
        self.attacker.add_component(weapon, LayerType.OUTER)

        # Target 1: Out of Arc (Behind)
        t1 = Ship("T1", -200, 0, (0,0,0)) 
        t1.is_alive = True
        t1.team_id = 1
        t1.add_component(create_component('test_bridge_basic'), LayerType.CORE)
        
        # Target 2: Valid (In front)
        t2 = Ship("T2", 200, 0, (0,0,0)) 
        t2.is_alive = True
        t2.team_id = 1
        t2.add_component(create_component('test_bridge_basic'), LayerType.CORE)

        self.attacker.current_target = t1
        self.attacker.secondary_targets = [t2]

        self.attacker.is_derelict = False
        self.attacker.max_targets = 2
        attacks = self.attacker.fire_weapons()
        self.assertEqual(len(attacks), 1)
        self.assertEqual(attacks[0].target.name, "T2", "Should skip T1 (out of arc) and shoot T2")

    # --- PDC Logic Tests ---

    def test_pdc_selection_logic(self):
        """Test _find_pdc_target logic for selecting closest enemy missile."""
        # Setup projectiles context
        # Closest missile
        p1 = type('obj', (object,), {'position': pygame.math.Vector2(100,0), 'team_id': 1, 'is_alive': True, 'type': 'missile'})
        # Farther missile
        p2 = type('obj', (object,), {'position': pygame.math.Vector2(300,0), 'team_id': 1, 'is_alive': True, 'type': 'missile'})
        # Friendly missile
        p3 = type('obj', (object,), {'position': pygame.math.Vector2(50,0), 'team_id': 0, 'is_alive': True, 'type': 'missile'})
        
        context = {'projectiles': [p1, p2, p3]}
        
        # Dummy PDC component
        pdc = type('obj', (object,), {'range': 500})
        
        self.attacker.team_id = 0
        
        target = self.attacker._find_pdc_target(pdc, context)
        self.assertEqual(target, p1, "Should select closest enemy missile (p1)")
        
        # Verify range check
        pdc.range = 50 
        target = self.attacker._find_pdc_target(pdc, context)
        self.assertIsNone(target, "Should find no targets within range 50")

    # --- Resource Consumption Tests ---

    def test_resource_consumption_beam(self):
        """Verify energy consumption for BeamWeapon."""
        beam = BeamWeapon({
            'name': 'Laser', 'id':'laser', 'energy_cost': 50, 'range': 500,
            'damage': 10, 'firing_arc': 360, 'cooldown': 0,
            'mass': 1, 'hp': 1, 'allowed_layers': ['OUTER'], 'type': 'Weapon'
        })
        beam.is_active = True
        self.attacker.add_component(beam, LayerType.OUTER)
        self.attacker.current_energy = 100
        
        self.attacker.current_target = self.target
        self.attacker.is_derelict = False
        self.attacker.fire_weapons()
        self.assertEqual(self.attacker.current_energy, 50, "Should consume 50 energy")
        
        # Fire again
        beam.cooldown_timer = 0
        self.attacker.is_derelict = False
        self.attacker.fire_weapons()
        self.assertEqual(self.attacker.current_energy, 0)
        
        # Fire again (Empty)
        beam.cooldown_timer = 0
        self.attacker.is_derelict = False
        attacks = self.attacker.fire_weapons()
        self.assertEqual(len(attacks), 0, "Should not fire without energy")

    def test_resource_consumption_ammo(self):
        """Verify ammo consumption for ProjectileWeapon."""
        gun = ProjectileWeapon({
             'name': 'Cannon', 'id':'cannon', 'ammo_cost': 5, 'range': 500,
            'damage': 10, 'firing_arc': 360, 'cooldown': 0, 'projectile_speed': 1000,
             'mass': 1, 'hp': 1, 'allowed_layers': ['OUTER'], 'type': 'Weapon'
        })
        gun.is_active = True
        self.attacker.add_component(gun, LayerType.OUTER)
        self.attacker.current_ammo = 10
        self.attacker.current_energy = 1000 
        
        self.attacker.current_target = self.target
        self.attacker.is_derelict = False
        self.attacker.fire_weapons()
        self.assertEqual(self.attacker.current_ammo, 5)

if __name__ == '__main__':
    unittest.main()
