"""Tests for ship loading and expected_stats validation.

These tests ensure that ships loaded from JSON files have stats that match
the expected_stats saved by the ship builder, validating that modifier
stacking is working correctly in the simulator.
"""
import unittest
import sys
import os
import json
import glob

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from game.simulation.entities.ship import Ship, load_vehicle_classes
from game.simulation.components.component import (
    load_components, load_modifiers, create_component,
    MODIFIER_REGISTRY, COMPONENT_REGISTRY
)


class TestModifierStacking(unittest.TestCase):
    """Test that modifier stacking calculates HP correctly."""
    
    @classmethod
    def setUpClass(cls):
        load_components("data/components.json")
        load_modifiers("data/modifiers.json")
    
    def test_simple_size_mount_hp_multiplier(self):
        """simple_size_mount should multiply HP by the scale value."""
        laser = create_component('laser_cannon')
        base_hp = laser.max_hp
        
        # Add 8x size mount
        laser.add_modifier('simple_size_mount', 8)
        laser.recalculate_stats()
        
        expected_hp = base_hp * 8
        self.assertEqual(laser.max_hp, expected_hp,
                        f"Size mount 8x: expected {expected_hp}, got {laser.max_hp}")
    
    def test_range_mount_hp_multiplier(self):
        """range_mount should multiply HP by 3.5^level."""
        laser = create_component('laser_cannon')
        base_hp = laser.max_hp
        
        # Add range mount level 2
        laser.add_modifier('range_mount', 2)
        laser.recalculate_stats()
        
        expected_multiplier = 3.5 ** 2  # 12.25
        expected_hp = int(base_hp * expected_multiplier)
        self.assertEqual(laser.max_hp, expected_hp,
                        f"Range mount level 2: expected {expected_hp}, got {laser.max_hp}")
    
    def test_stacked_modifiers_multiplicative(self):
        """Multiple modifiers should stack multiplicatively."""
        laser = create_component('laser_cannon')
        base_hp = laser.max_hp
        
        # Add both size_mount(8) and range_mount(2)
        laser.add_modifier('simple_size_mount', 8)
        laser.add_modifier('range_mount', 2)
        laser.recalculate_stats()
        
        # 8 * 3.5^2 = 8 * 12.25 = 98
        expected_multiplier = 8 * (3.5 ** 2)
        expected_hp = int(base_hp * expected_multiplier)
        self.assertEqual(laser.max_hp, expected_hp,
                        f"Stacked modifiers: expected {expected_hp}, got {laser.max_hp}")
    
    def test_turret_mount_no_hp_change(self):
        """turret_mount should not affect HP (only mass)."""
        laser = create_component('laser_cannon')
        base_hp = laser.max_hp
        base_mass = laser.mass
        
        laser.add_modifier('turret_mount', 180)
        laser.recalculate_stats()
        
        self.assertEqual(laser.max_hp, base_hp,
                        f"Turret mount should not change HP: expected {base_hp}, got {laser.max_hp}")
        self.assertGreater(laser.mass, base_mass,
                          "Turret mount should increase mass")


class TestShipExpectedStats(unittest.TestCase):
    """Test that loaded ships match their expected_stats."""
    
    @classmethod
    def setUpClass(cls):
        load_components("data/components.json")
        load_modifiers("data/modifiers.json")
        load_vehicle_classes()
    
    


class TestAllShipDesigns(unittest.TestCase):
    """Test all ship designs in the ships/ folder."""
    
    @classmethod
    def setUpClass(cls):
        load_components("data/components.json")
        load_modifiers("data/modifiers.json")
        from game.simulation.entities.ship import load_vehicle_classes
        load_vehicle_classes("data/vehicleclasses.json")
        
        # Find all ship JSON files
        ships_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ships")
        cls.ship_files = glob.glob(os.path.join(ships_dir, "*.json"))
    
    def test_all_ships_match_expected_stats(self):
        """All ships should match their expected_stats if present."""
        failures = []
        
        for ship_path in self.ship_files:
            try:
                with open(ship_path, 'r') as f:
                    data = json.load(f)
                
                expected = data.get('expected_stats', {})
                if not expected:
                    continue  # Skip ships without expected_stats
                
                ship = Ship.from_dict(data)
                ship.recalculate_stats()
                
                ship_name = data.get('name', os.path.basename(ship_path))
                
                # Check HP
                if 'max_hp' in expected:
                    if abs(ship.max_hp - expected['max_hp']) > 1:
                        failures.append(f"{ship_name}: max_hp expected {expected['max_hp']}, got {ship.max_hp}")
                
                # Check fuel
                if 'max_fuel' in expected:
                    val = ship.resources.get_max_value("fuel")
                    if abs(val - expected['max_fuel']) > 1:
                        failures.append(f"{ship_name}: max_fuel expected {expected['max_fuel']}, got {val}")
                
                # Check ammo
                if 'max_ammo' in expected:
                    val = ship.resources.get_max_value("ammo")
                    if abs(val - expected['max_ammo']) > 1:
                        failures.append(f"{ship_name}: max_ammo expected {expected['max_ammo']}, got {val}")
                
                # Check energy
                if 'max_energy' in expected:
                    val = ship.resources.get_max_value("energy")
                    if abs(val - expected['max_energy']) > 1:
                        failures.append(f"{ship_name}: max_energy expected {expected['max_energy']}, got {val}")
                        
            except Exception as e:
                failures.append(f"{os.path.basename(ship_path)}: Error loading - {e}")
        
        if failures:
            self.fail("Ships with stat mismatches:\n" + "\n".join(failures))


if __name__ == '__main__':
    unittest.main()
