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


# PROJ-FMS-C audit Fix 1: ``TestVehicleLaunchBindings`` removed — the
# ``VehicleLaunchAbility`` class itself was deleted in favor of the
# PROJ-FMS-A Phase 5 ``TacticalFighterLaunchAbility`` /
# ``StrategicFighterLaunchAbility`` pair. Those abilities are additive
# (capacity_per_action / cycle_time) and carry no ``CAPACITY_MULT``
# binding — there is nothing for this test to pin.


class TestMarkerAbilitiesHaveEmptyBindings:
    """Tests for marker abilities that don't consume any stats.

    PROJ-323 Task 3.10: 6 individual tests parametrized into one.
    """

    @pytest.mark.parametrize("ability_class", [
        pytest.param(
            __import__('game.simulation.components.abilities.markers', fromlist=['CommandAndControl']).CommandAndControl,
            id='CommandAndControl',
        ),
        pytest.param(
            __import__('game.simulation.components.abilities.defense', fromlist=['ToHitAttackModifier']).ToHitAttackModifier,
            id='ToHitAttackModifier',
        ),
        pytest.param(
            __import__('game.simulation.components.abilities.defense', fromlist=['ToHitDefenseModifier']).ToHitDefenseModifier,
            id='ToHitDefenseModifier',
        ),
        pytest.param(
            __import__('game.simulation.components.abilities.defense', fromlist=['EmissiveArmor']).EmissiveArmor,
            id='EmissiveArmor',
        ),
        pytest.param(
            __import__('game.simulation.components.abilities.harvester', fromlist=['ResourceHarvesterAbility']).ResourceHarvesterAbility,
            id='ResourceHarvesterAbility',
        ),
        pytest.param(
            __import__('game.simulation.components.abilities.harvester', fromlist=['SpaceShipyardAbility']).SpaceShipyardAbility,
            id='SpaceShipyardAbility',
        ),
    ])
    def test_marker_ability_has_empty_bindings(self, ability_class):
        """Marker abilities should have empty STAT_BINDINGS."""
        assert hasattr(ability_class, 'STAT_BINDINGS')
        assert len(ability_class.STAT_BINDINGS) == 0
