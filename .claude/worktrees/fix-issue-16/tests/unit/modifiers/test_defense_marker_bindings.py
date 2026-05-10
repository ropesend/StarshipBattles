"""
Tests for Defense and Marker Ability STAT_BINDINGS - Phase 3 Task 3.11

TDD: Write tests FIRST, then implement to make them pass.
"""
import pytest
from game.simulation.components.abilities.stat_keys import StatKey, AbilityStatBinding


class TestShieldProjectionBindings:
    """Tests for ShieldProjection STAT_BINDINGS."""

    def test_shield_projection_has_capacity_binding(self):
        """ShieldProjection should have CAPACITY_MULT binding."""
        from game.simulation.components.abilities.defense import ShieldProjection

        bindings = [b for b in ShieldProjection.STAT_BINDINGS
                   if b.stat_key == StatKey.CAPACITY_MULT]
        assert len(bindings) == 1

        binding = bindings[0]
        assert binding.attribute_name == 'capacity'
        assert binding.operation == 'multiply'


class TestShieldRegenerationBindings:
    """Tests for ShieldRegeneration STAT_BINDINGS."""

    def test_shield_regeneration_has_energy_gen_binding(self):
        """ShieldRegeneration should have ENERGY_GEN_MULT binding."""
        from game.simulation.components.abilities.defense import ShieldRegeneration

        bindings = [b for b in ShieldRegeneration.STAT_BINDINGS
                   if b.stat_key == StatKey.ENERGY_GEN_MULT]
        assert len(bindings) == 1

        binding = bindings[0]
        assert binding.attribute_name == 'rate'
        assert binding.operation == 'multiply'


class TestVehicleLaunchBindings:
    """Tests for VehicleLaunchAbility STAT_BINDINGS."""

    def test_vehicle_launch_has_capacity_binding(self):
        """VehicleLaunchAbility should have CAPACITY_MULT binding."""
        from game.simulation.components.abilities.markers import VehicleLaunchAbility

        bindings = [b for b in VehicleLaunchAbility.STAT_BINDINGS
                   if b.stat_key == StatKey.CAPACITY_MULT]
        assert len(bindings) == 1

        binding = bindings[0]
        assert binding.attribute_name == 'capacity'
        assert binding.operation == 'multiply'


class TestMarkerAbilitiesHaveEmptyBindings:
    """Tests for marker abilities that don't consume any stats."""

    def test_command_control_empty_bindings(self):
        """CommandAndControl should have empty STAT_BINDINGS."""
        from game.simulation.components.abilities.markers import CommandAndControl

        assert hasattr(CommandAndControl, 'STAT_BINDINGS')
        assert len(CommandAndControl.STAT_BINDINGS) == 0

    def test_to_hit_attack_empty_bindings(self):
        """ToHitAttackModifier should have empty STAT_BINDINGS."""
        from game.simulation.components.abilities.defense import ToHitAttackModifier

        assert hasattr(ToHitAttackModifier, 'STAT_BINDINGS')
        assert len(ToHitAttackModifier.STAT_BINDINGS) == 0

    def test_to_hit_defense_empty_bindings(self):
        """ToHitDefenseModifier should have empty STAT_BINDINGS."""
        from game.simulation.components.abilities.defense import ToHitDefenseModifier

        assert hasattr(ToHitDefenseModifier, 'STAT_BINDINGS')
        assert len(ToHitDefenseModifier.STAT_BINDINGS) == 0

    def test_emissive_armor_empty_bindings(self):
        """EmissiveArmor should have empty STAT_BINDINGS."""
        from game.simulation.components.abilities.defense import EmissiveArmor

        assert hasattr(EmissiveArmor, 'STAT_BINDINGS')
        assert len(EmissiveArmor.STAT_BINDINGS) == 0

    def test_harvester_empty_bindings(self):
        """ResourceHarvesterAbility should have empty STAT_BINDINGS."""
        from game.simulation.components.abilities.harvester import ResourceHarvesterAbility

        assert hasattr(ResourceHarvesterAbility, 'STAT_BINDINGS')
        assert len(ResourceHarvesterAbility.STAT_BINDINGS) == 0

    def test_shipyard_empty_bindings(self):
        """SpaceShipyardAbility should have empty STAT_BINDINGS."""
        from game.simulation.components.abilities.harvester import SpaceShipyardAbility

        assert hasattr(SpaceShipyardAbility, 'STAT_BINDINGS')
        assert len(SpaceShipyardAbility.STAT_BINDINGS) == 0
