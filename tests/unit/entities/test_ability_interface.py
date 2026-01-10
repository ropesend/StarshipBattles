"""Test polymorphic get_primary_value() interface for abilities."""
import unittest
from unittest.mock import patch
from game.simulation.components.abilities import (
    Ability, CombatPropulsion, ManeuveringThruster, ShieldProjection,
    ShieldRegeneration, CrewCapacity, LifeSupportCapacity, CrewRequired,
    ResourceStorage, ResourceGeneration, ResourceConsumption,
    ToHitAttackModifier, ToHitDefenseModifier, EmissiveArmor,
    WeaponAbility, CommandAndControl, VehicleLaunchAbility
)
from game.core.registry import RegistryManager


class MockComponent:
    """Minimal mock component for testing abilities."""
    def __init__(self):
        self.stats = {}
        self.data = {}
        self.ship = None


class TestAbilityPrimaryValueInterface(unittest.TestCase):
    """Test that all ability classes implement get_primary_value() correctly."""
    
    def setUp(self):
        self.mock_comp = MockComponent()
        RegistryManager.instance().clear()
    
    def tearDown(self):
        RegistryManager.instance().clear()
        patch.stopall()
    
    # --- Base Ability ---
    def test_base_ability_returns_zero(self):
        """Base Ability class returns 0.0 (marker ability default)."""
        ab = Ability(self.mock_comp, {})
        self.assertEqual(ab.get_primary_value(), 0.0)
    
    # --- Propulsion/Defense ---
    def test_combat_propulsion_returns_thrust_force(self):
        ab = CombatPropulsion(self.mock_comp, {'value': 1500})
        self.assertEqual(ab.get_primary_value(), 1500.0)
    
    def test_maneuvering_thruster_returns_turn_rate(self):
        ab = ManeuveringThruster(self.mock_comp, {'value': 45})
        self.assertEqual(ab.get_primary_value(), 45.0)
    
    def test_shield_projection_returns_capacity(self):
        ab = ShieldProjection(self.mock_comp, {'value': 500})
        self.assertEqual(ab.get_primary_value(), 500.0)
    
    def test_shield_regeneration_returns_rate(self):
        ab = ShieldRegeneration(self.mock_comp, {'value': 10})
        self.assertEqual(ab.get_primary_value(), 10.0)
    
    # --- Crew ---
    def test_crew_capacity_returns_amount(self):
        ab = CrewCapacity(self.mock_comp, {'value': 10})
        self.assertEqual(ab.get_primary_value(), 10.0)
    
    def test_life_support_capacity_returns_amount(self):
        ab = LifeSupportCapacity(self.mock_comp, {'value': 20})
        self.assertEqual(ab.get_primary_value(), 20.0)
    
    def test_crew_required_returns_amount(self):
        ab = CrewRequired(self.mock_comp, {'value': 5})
        self.assertEqual(ab.get_primary_value(), 5.0)
    
    # --- Resources ---
    def test_resource_storage_returns_max_amount(self):
        ab = ResourceStorage(self.mock_comp, {'resource': 'fuel', 'amount': 100})
        self.assertEqual(ab.get_primary_value(), 100.0)
    
    def test_resource_generation_returns_rate(self):
        ab = ResourceGeneration(self.mock_comp, {'resource': 'energy', 'amount': 25})
        self.assertEqual(ab.get_primary_value(), 25.0)
    
    def test_resource_consumption_returns_amount(self):
        ab = ResourceConsumption(self.mock_comp, {'resource': 'fuel', 'amount': 5, 'trigger': 'constant'})
        self.assertEqual(ab.get_primary_value(), 5.0)
    
    # --- Combat Modifiers ---
    def test_to_hit_attack_modifier_returns_value(self):
        ab = ToHitAttackModifier(self.mock_comp, {'value': 2.5})
        self.assertEqual(ab.get_primary_value(), 2.5)
    
    def test_to_hit_defense_modifier_returns_value(self):
        ab = ToHitDefenseModifier(self.mock_comp, {'value': 1.5})
        self.assertEqual(ab.get_primary_value(), 1.5)
    
    def test_emissive_armor_returns_amount(self):
        ab = EmissiveArmor(self.mock_comp, {'value': 3})
        self.assertEqual(ab.get_primary_value(), 3.0)
    
    # --- Weapons ---
    def test_weapon_ability_returns_damage(self):
        ab = WeaponAbility(self.mock_comp, {'damage': 25, 'range': 500, 'reload': 2.0})
        self.assertEqual(ab.get_primary_value(), 25.0)
    
    # --- Markers ---
    def test_command_and_control_returns_zero(self):
        """Marker abilities return 0.0 (boolean semantics handled separately)."""
        ab = CommandAndControl(self.mock_comp, {})
        self.assertEqual(ab.get_primary_value(), 0.0)
    
    # --- Hangar ---
    def test_vehicle_launch_returns_capacity(self):
        ab = VehicleLaunchAbility(self.mock_comp, {'capacity': 4, 'cycle_time': 5.0})
        self.assertEqual(ab.get_primary_value(), 4.0)


if __name__ == '__main__':
    unittest.main()
