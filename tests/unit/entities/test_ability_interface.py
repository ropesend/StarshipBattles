"""Test polymorphic get_primary_value() interface for abilities."""
import pytest
from unittest.mock import patch
from game.simulation.components.abilities import (
    Ability, CombatPropulsion, ManeuveringThruster, ShieldProjection,
    ShieldRegeneration, CrewCapacity, LifeSupportCapacity, CrewRequired,
    ResourceStorage, ResourceGeneration, ResourceConsumption,
    ToHitAttackModifier, ToHitDefenseModifier, EmissiveArmor,
    WeaponAbility, CommandAndControl,
)


class MockComponent:
    """Minimal mock component for testing abilities."""
    def __init__(self):
        self.stats = {}
        self.data = {}
        self.ship = None


class TestAbilityPrimaryValueInterface:
    """Test that all ability classes implement get_primary_value() correctly."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.mock_comp = MockComponent()

        yield

        patch.stopall()

    # --- Base Ability ---
    def test_base_ability_returns_zero(self):
        """Base Ability class returns 0.0 (marker ability default)."""
        ab = Ability(self.mock_comp, {})
        assert ab.get_primary_value() == 0.0

    # --- Propulsion/Defense ---
    def test_combat_propulsion_returns_thrust_force(self):
        ab = CombatPropulsion(self.mock_comp, {'value': 1500})
        assert ab.get_primary_value() == 1500.0

    def test_maneuvering_thruster_returns_turn_rate(self):
        ab = ManeuveringThruster(self.mock_comp, {'value': 45})
        assert ab.get_primary_value() == 45.0

    def test_shield_projection_returns_capacity(self):
        ab = ShieldProjection(self.mock_comp, {'value': 500})
        assert ab.get_primary_value() == 500.0

    def test_shield_regeneration_returns_rate(self):
        ab = ShieldRegeneration(self.mock_comp, {'value': 10})
        assert ab.get_primary_value() == 10.0

    # --- Crew ---
    def test_crew_capacity_returns_amount(self):
        ab = CrewCapacity(self.mock_comp, {'value': 10})
        assert ab.get_primary_value() == 10.0

    def test_life_support_capacity_returns_amount(self):
        ab = LifeSupportCapacity(self.mock_comp, {'value': 20})
        assert ab.get_primary_value() == 20.0

    def test_crew_required_returns_amount(self):
        ab = CrewRequired(self.mock_comp, {'value': 5})
        assert ab.get_primary_value() == 5.0

    # --- Resources ---
    def test_resource_storage_returns_max_amount(self):
        ab = ResourceStorage(self.mock_comp, {'resource': 'fuel', 'amount': 100})
        assert ab.get_primary_value() == 100.0

    def test_resource_generation_returns_rate(self):
        ab = ResourceGeneration(self.mock_comp, {'resource': 'energy', 'amount': 25})
        assert ab.get_primary_value() == 25.0

    def test_resource_consumption_returns_amount(self):
        ab = ResourceConsumption(self.mock_comp, {'resource': 'fuel', 'amount': 5, 'trigger': 'constant'})
        assert ab.get_primary_value() == 5.0

    # --- Combat Modifiers ---
    def test_to_hit_attack_modifier_returns_value(self):
        ab = ToHitAttackModifier(self.mock_comp, {'value': 2.5})
        assert ab.get_primary_value() == 2.5

    def test_to_hit_defense_modifier_returns_value(self):
        ab = ToHitDefenseModifier(self.mock_comp, {'value': 1.5})
        assert ab.get_primary_value() == 1.5

    def test_emissive_armor_returns_amount(self):
        ab = EmissiveArmor(self.mock_comp, {'value': 3})
        assert ab.get_primary_value() == 3.0

    # --- Weapons ---
    def test_weapon_ability_returns_damage(self):
        ab = WeaponAbility(self.mock_comp, {'damage': 25, 'range': 500, 'reload': 2.0})
        assert ab.get_primary_value() == 25.0

    # --- Markers ---
    def test_command_and_control_returns_one(self):
        """Marker abilities return 1.0 for boolean presence checks."""
        ab = CommandAndControl(self.mock_comp, {})
        assert ab.get_primary_value() == 1.0

    # --- Hangar ---
    # PROJ-FMS-C audit Fix 1: ``test_vehicle_launch_returns_capacity`` removed.
    # The legacy ``VehicleLaunchAbility`` was deleted in favor of
    # ``TacticalFighterLaunchAbility`` (PROJ-FMS-A Phase 5).
