
import unittest
from unittest.mock import MagicMock
from components import Component, Engine, Weapon
from abilities import CombatPropulsion, WeaponAbility, ManeuveringThruster

class TestLegacyShim(unittest.TestCase):
    def test_legacy_engine_shim(self):
        # Data representing a legacy engine (no 'abilities' dict)
        data = {
            "id": "engine_1",
            "name": "Legacy Engine",
            "type": "Engine",
            "mass": 100,
            "hp": 50,
            "thrust_force": 2500,
            "turn_speed": 45
        }
        
        # Instantiate Component (using Engine subclass to trigger any existing logic, though we aim for generic)
        # We will use base Component to test generic shim, or Engine if we want to ensure subclass compatibility.
        # Ideally, even a generic Component with this data should have the abilities if we want full decouple.
        # But for now, let's test specific requirements.
        
        comp = Engine(data)
        
        # Helper to find ability
        def get_ability(c, ability_type):
            for ab in c.ability_instances:
                if isinstance(ab, ability_type):
                    return ab
            return None
            
        # Assertion: Currently should fail or pass depending on state.
        # We expect it to FAIL or return None before we implement the shim.
        # actually, before shim, ability_instances will be empty.
        
        propulsion = get_ability(comp, CombatPropulsion)
        maneuver = get_ability(comp, ManeuveringThruster)
        
        self.assertIsNotNone(propulsion, "Legacy Engine should have CombatPropulsion ability auto-generated")
        self.assertEqual(propulsion.thrust_force, 2500, "Thrust force should match legacy data")
        
        self.assertIsNotNone(maneuver, "Legacy Engine should have ManeuveringThruster ability auto-generated")
        self.assertEqual(maneuver.turn_rate, 45, "Turn rate should match legacy data")

    def test_legacy_weapon_shim(self):
        data = {
            "id": "wep_1",
            "name": "Legacy Gun",
            "type": "ProjectileWeapon",
            "mass": 50,
            "hp": 20,
            "damage": 50,
            "range": 1000,
            "reload": 2.0,
            "projectile_speed": 800
        }
        
        # Using generic Component to see if Shim works based on Type/Data
        # Or Weapon subclass
        comp = Component(data) 
        
        # We need the shim to detect "ProjectileWeapon" type OR "damage" field?
        # Plan says: "If damage in data, create appropriate WeaponAbility"
        
        def get_ability(c, ability_type):
            for ab in c.ability_instances:
                if isinstance(ab, ability_type):
                    return ab
            return None
            
        weapon_ab = get_ability(comp, WeaponAbility)
        self.assertIsNotNone(weapon_ab, "Legacy Weapon should have WeaponAbility")
        self.assertEqual(weapon_ab.damage, 50)
        self.assertEqual(weapon_ab.range, 1000)

    def test_legacy_shield_shim(self):
        data = {
            "id": "shield_1",
            "name": "Legacy Shield",
            "type": "Shield",
            "mass": 100,
            "hp": 50,
            "shield_capacity": 500
        }
        
        comp = Component(data)
        
        def get_ability(c, ability_name):
            for ab in c.ability_instances:
                if ab.__class__.__name__ == ability_name:
                    return ab
            return None
            
        shield_ab = get_ability(comp, "ShieldProjection")
        self.assertIsNotNone(shield_ab, "Legacy Shield should have ShieldProjection ability")
        self.assertEqual(shield_ab.capacity, 500)

    def test_legacy_shield_regen_shim(self):
        data = {
            "id": "regen_1",
            "name": "Legacy Regen",
            "type": "ShieldRegenerator",
            "mass": 50,
            "hp": 20,
            "shield_recharge_rate": 5.0
        }
        
        comp = Component(data)
        
        def get_ability(c, ability_name):
            for ab in c.ability_instances:
                if ab.__class__.__name__ == ability_name:
                    return ab
            return None
            
        regen_ab = get_ability(comp, "ShieldRegeneration")
        self.assertIsNotNone(regen_ab, "Legacy Regenerator should have ShieldRegeneration ability")
        self.assertEqual(regen_ab.rate, 5.0)
