"""
Integration tests for weapon ability classes.

PROJ-118: Phase 2 - Tasks 2.25-2.27

These tests verify weapon ability behavior in integration scenarios:
- Multiple weapons on same component
- Weapon abilities with modifier stacking
- Cross-ability interactions
- Component-to-ship stat flow
- Formula evaluation with runtime context
- Real component integration

These complement the isolation tests in test_weapons_isolation.py.
"""

import math
import pytest
from unittest.mock import Mock, MagicMock
from pygame import Vector2

from game.simulation.components.abilities.weapons import (
    WeaponAbility,
    ProjectileWeaponAbility,
    BeamWeaponAbility,
    SeekerWeaponAbility,
)
from game.simulation.components.abilities.stat_keys import StatKey
from game.core.config import PhysicsConfig


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def component_with_modifiers():
    """Create a mock component with modifier stat support."""
    component = Mock()
    component.stats = {}
    component.ability_stats = {}
    component.data = {}
    component.consume_activation = Mock()
    return component


@pytest.fixture
def multi_weapon_component():
    """Create a mock component with multiple weapon abilities."""
    component = Mock()
    component.stats = {}
    component.ability_stats = {}
    component.data = {}
    component.consume_activation = Mock()
    return component


# =============================================================================
# Multi-Weapon Integration Tests
# =============================================================================

class TestMultiWeaponComponent:
    """Test multiple weapon abilities on the same component."""

    def test_two_weapons_with_shared_damage_mult(self, multi_weapon_component):
        """Two weapons sharing damage_mult should both be affected."""
        multi_weapon_component.stats = {'damage_mult': 1.5}

        weapon1_data = {'damage': 100, 'range': 1000, 'reload': 2.0}
        weapon2_data = {'damage': 50, 'range': 500, 'reload': 1.0}

        weapon1 = WeaponAbility(multi_weapon_component, weapon1_data)
        weapon2 = WeaponAbility(multi_weapon_component, weapon2_data)

        weapon1.recalculate()
        weapon2.recalculate()

        assert weapon1.damage == pytest.approx(150.0, rel=1e-6)  # 100 * 1.5
        assert weapon2.damage == pytest.approx(75.0, rel=1e-6)   # 50 * 1.5

    def test_two_weapons_with_independent_firing(self, multi_weapon_component):
        """Two weapons should have independent cooldown timers."""
        weapon1_data = {'damage': 100, 'range': 1000, 'reload': 2.0}
        weapon2_data = {'damage': 50, 'range': 500, 'reload': 1.0}

        weapon1 = WeaponAbility(multi_weapon_component, weapon1_data)
        weapon2 = WeaponAbility(multi_weapon_component, weapon2_data)

        # Fire weapon 1
        weapon1.fire(Mock())

        # Weapon 1 on cooldown, weapon 2 still ready
        assert weapon1.can_fire() is False
        assert weapon2.can_fire() is True

        # Fire weapon 2
        weapon2.fire(Mock())

        # Both on cooldown
        assert weapon1.can_fire() is False
        assert weapon2.can_fire() is False

    def test_weapons_with_different_ability_specific_stats(self, multi_weapon_component):
        """Each weapon type can have its own ability-specific modifiers."""
        multi_weapon_component.ability_stats = {
            'ProjectileWeaponAbility': {'damage_mult': 2.0},
            'BeamWeaponAbility': {'damage_mult': 1.5},
        }

        proj_data = {'damage': 100, 'range': 1000, 'reload': 2.0, 'projectile_speed': 500}
        beam_data = {'damage': 100, 'range': 2000, 'reload': 0.5, 'base_accuracy': 1.0}

        projectile = ProjectileWeaponAbility(multi_weapon_component, proj_data)
        beam = BeamWeaponAbility(multi_weapon_component, beam_data)

        projectile.recalculate()
        beam.recalculate()

        assert projectile.damage == pytest.approx(200.0, rel=1e-6)  # 100 * 2.0
        assert beam.damage == pytest.approx(150.0, rel=1e-6)        # 100 * 1.5


# =============================================================================
# Modifier Stacking Tests
# =============================================================================

class TestModifierStacking:
    """Test stacking behavior of weapon modifiers."""

    def test_multiple_modifiers_applied_multiplicatively(self, component_with_modifiers):
        """Multiple multiplier modifiers should stack multiplicatively."""
        component_with_modifiers.stats = {
            'damage_mult': 1.5,
            'range_mult': 1.2,
            'reload_mult': 0.8,
        }

        weapon_data = {'damage': 100, 'range': 1000, 'reload': 2.0}
        weapon = WeaponAbility(component_with_modifiers, weapon_data)
        weapon.recalculate()

        assert weapon.damage == pytest.approx(150.0, rel=1e-6)   # 100 * 1.5
        assert weapon.range == pytest.approx(1200.0, rel=1e-6)   # 1000 * 1.2
        assert weapon.reload_time == pytest.approx(1.6, rel=1e-6)  # 2.0 * 0.8

    def test_modifier_changes_propagate_on_recalculate(self, component_with_modifiers):
        """Changing modifiers should update weapon stats on recalculate."""
        component_with_modifiers.stats = {'damage_mult': 1.0}

        weapon_data = {'damage': 100, 'range': 1000, 'reload': 1.0}
        weapon = WeaponAbility(component_with_modifiers, weapon_data)

        # Initial state
        weapon.recalculate()
        assert weapon.damage == 100.0

        # Apply modifier
        component_with_modifiers.stats['damage_mult'] = 2.0
        weapon.recalculate()
        assert weapon.damage == 200.0

        # Remove modifier
        component_with_modifiers.stats['damage_mult'] = 1.0
        weapon.recalculate()
        assert weapon.damage == 100.0

    def test_arc_set_priority_over_arc_add(self, component_with_modifiers):
        """arc_set should always override arc_add."""
        component_with_modifiers.stats = {
            'arc_set': 60.0,
            'arc_add': 30.0,
        }

        weapon_data = {'damage': 100, 'range': 1000, 'reload': 1.0, 'firing_arc': 90}
        weapon = WeaponAbility(component_with_modifiers, weapon_data)
        weapon.recalculate()

        # arc_set should be used (60.0), not base + arc_add (90 + 30 = 120)
        assert weapon.firing_arc == 60.0

    def test_arc_add_with_negative_value(self, component_with_modifiers):
        """arc_add with negative value should reduce firing arc."""
        component_with_modifiers.stats = {'arc_add': -30.0}

        weapon_data = {'damage': 100, 'range': 1000, 'reload': 1.0, 'firing_arc': 90}
        weapon = WeaponAbility(component_with_modifiers, weapon_data)
        weapon.recalculate()

        assert weapon.firing_arc == 60.0  # 90 - 30


# =============================================================================
# BeamWeaponAbility Hit Chance Integration Tests
# =============================================================================

class TestBeamWeaponHitChanceIntegration:
    """Integration tests for BeamWeaponAbility hit chance calculations."""

    def test_hit_chance_with_attack_and_defense_modifiers(self, component_with_modifiers):
        """Hit chance should account for both attack bonus and defense penalty."""
        beam_data = {
            'damage': 100,
            'range': 2000,
            'reload': 0.5,
            'accuracy_falloff': 0.001,
            'base_accuracy': 1.0,
        }
        beam = BeamWeaponAbility(component_with_modifiers, beam_data)

        # Balanced case: attack bonus = defense penalty
        balanced = beam.calculate_hit_chance(500, attack_score_bonus=1.0, defense_score_penalty=1.0)

        # Attack advantage: more attack than defense
        advantage = beam.calculate_hit_chance(500, attack_score_bonus=2.0, defense_score_penalty=1.0)

        # Defense advantage: more defense than attack
        disadvantage = beam.calculate_hit_chance(500, attack_score_bonus=1.0, defense_score_penalty=2.0)

        assert advantage > balanced
        assert balanced > disadvantage

    def test_hit_chance_progression_over_distance(self, component_with_modifiers):
        """Hit chance should decrease smoothly over distance."""
        beam_data = {
            'damage': 100,
            'range': 2000,
            'reload': 0.5,
            'accuracy_falloff': 0.002,
            'base_accuracy': 2.0,
        }
        beam = BeamWeaponAbility(component_with_modifiers, beam_data)

        chances = [beam.calculate_hit_chance(d) for d in range(0, 2001, 200)]

        # Verify monotonically decreasing
        for i in range(1, len(chances)):
            assert chances[i] <= chances[i - 1], f"Hit chance should decrease with distance"

    def test_high_accuracy_beam_at_max_range(self, component_with_modifiers):
        """High-accuracy beam should still have reasonable hit chance at max range."""
        beam_data = {
            'damage': 100,
            'range': 1000,
            'reload': 0.5,
            'accuracy_falloff': 0.0005,  # Low falloff = accurate at range
            'base_accuracy': 3.0,        # High base = accurate
        }
        beam = BeamWeaponAbility(component_with_modifiers, beam_data)

        max_range_chance = beam.calculate_hit_chance(1000)

        # With these stats, should still have decent hit chance at max range
        assert max_range_chance > 0.5


# =============================================================================
# SeekerWeaponAbility Integration Tests
# =============================================================================

class TestSeekerWeaponIntegration:
    """Integration tests for SeekerWeaponAbility."""

    def test_seeker_range_calculation_from_endurance(self, component_with_modifiers):
        """Seeker range should be calculated from speed and endurance."""
        seeker_data = {
            'damage': 0,
            'range': 0,  # Not set - should be calculated
            'reload': 3.0,
            'projectile_speed': 500,
            'endurance': 10.0,
            'projectile_damage': 100,
        }
        seeker = SeekerWeaponAbility(component_with_modifiers, seeker_data)

        # Range = speed * endurance * 0.8 = 500 * 10 * 0.8 = 4000
        assert seeker.range == 4000

    def test_seeker_modifier_chain(self, component_with_modifiers):
        """Seeker should apply modifier chain correctly."""
        component_with_modifiers.stats = {
            'damage_mult': 1.5,
            'endurance_mult': 2.0,
            'projectile_damage_mult': 1.2,
            'projectile_hp_mult': 1.5,
        }

        seeker_data = {
            'damage': 50,
            'range': 2000,
            'reload': 3.0,
            'projectile_speed': 500,
            'endurance': 5.0,
            'projectile_damage': 100,
            'projectile_hp': 10,
        }
        seeker = SeekerWeaponAbility(component_with_modifiers, seeker_data)
        seeker.recalculate()

        # Base weapon damage modified
        assert seeker.damage == pytest.approx(75.0, rel=1e-6)  # 50 * 1.5

        # Seeker-specific stats modified
        assert seeker.endurance == pytest.approx(10.0, rel=1e-6)  # 5.0 * 2.0
        assert seeker.projectile_damage == pytest.approx(120.0, rel=1e-6)  # 100 * 1.2
        assert seeker.projectile_hp == pytest.approx(15.0, rel=1e-6)  # 10 * 1.5

    def test_seeker_ignores_arc_for_all_directions(self, component_with_modifiers):
        """Seeker should be able to fire in all directions regardless of facing."""
        seeker_data = {
            'damage': 100,
            'range': 1000,
            'reload': 3.0,
            'projectile_speed': 500,
            'endurance': 5.0,
            'projectile_damage': 100,
            'firing_arc': 30,  # Very narrow arc - should be ignored
        }
        seeker = SeekerWeaponAbility(component_with_modifiers, seeker_data)

        ship_pos = Vector2(0, 0)
        ship_angle = 0  # Facing right

        # Test all cardinal directions
        directions = [
            Vector2(500, 0),    # Right (forward)
            Vector2(-500, 0),   # Left (behind)
            Vector2(0, 500),    # Down
            Vector2(0, -500),   # Up
            Vector2(400, 400),  # Diagonal
        ]

        for target_pos in directions:
            assert seeker.check_firing_solution(ship_pos, ship_angle, target_pos) is True


# =============================================================================
# Weapon Formula Integration Tests
# =============================================================================

class TestWeaponFormulaIntegration:
    """Integration tests for formula-based weapon stats."""

    def test_range_dependent_damage(self, component_with_modifiers):
        """Damage formula should calculate correctly at different ranges."""
        # Close-range weapon: more damage up close
        weapon_data = {
            'damage': '=200 - range_to_target * 0.1',
            'range': 1000,
            'reload': 1.0,
        }
        weapon = WeaponAbility(component_with_modifiers, weapon_data)

        assert weapon.get_damage(0) == 200.0       # Close range
        assert weapon.get_damage(500) == 150.0     # Mid range
        assert weapon.get_damage(1000) == 100.0    # Max range
        assert weapon.get_damage(2000) == 0.0      # Beyond range (clamped)

    def test_formula_damage_with_modifier(self, component_with_modifiers):
        """Formula base damage should still work with modifiers."""
        component_with_modifiers.stats = {'damage_mult': 2.0}

        weapon_data = {
            'damage': '=100',  # Formula that evaluates to 100
            'range': 1000,
            'reload': 1.0,
        }
        weapon = WeaponAbility(component_with_modifiers, weapon_data)
        weapon.recalculate()

        # The modifier applies to both static damage and formula-based get_damage()
        assert weapon.damage == pytest.approx(200.0, rel=1e-6)  # 100 * 2.0
        # get_damage() now also applies damage_mult to the formula result
        assert weapon.get_damage(0) == pytest.approx(200.0, rel=1e-6)  # 100 * 2.0

    def test_formula_with_complex_math(self, component_with_modifiers):
        """Formulas with complex math should evaluate correctly."""
        weapon_data = {
            'damage': '=50 + 100 * (1 - range_to_target / 2000)',
            'range': 2000,
            'reload': 1.0,
        }
        weapon = WeaponAbility(component_with_modifiers, weapon_data)

        # At range 0: 50 + 100 * 1 = 150
        assert weapon.get_damage(0) == pytest.approx(150.0, rel=1e-6)

        # At range 1000: 50 + 100 * 0.5 = 100
        assert weapon.get_damage(1000) == pytest.approx(100.0, rel=1e-6)

        # At range 2000: 50 + 100 * 0 = 50
        assert weapon.get_damage(2000) == pytest.approx(50.0, rel=1e-6)


# =============================================================================
# Firing Solution Geometry Integration Tests
# =============================================================================

class TestFiringSolutionGeometry:
    """Integration tests for firing solution geometry calculations."""

    def test_rotating_ship_firing_solution(self, component_with_modifiers):
        """Weapon should track target as ship rotates."""
        weapon_data = {
            'damage': 100,
            'range': 1000,
            'reload': 1.0,
            'firing_arc': 90,
            'facing_angle': 0,
        }
        weapon = WeaponAbility(component_with_modifiers, weapon_data)

        ship_pos = Vector2(0, 0)
        target_pos = Vector2(500, 0)  # Target to the right

        # Ship facing right (0 degrees) - target in arc
        assert weapon.check_firing_solution(ship_pos, 0, target_pos) is True

        # Ship facing up (90 degrees) - target behind
        assert weapon.check_firing_solution(ship_pos, 90, target_pos) is False

        # Ship facing left (180 degrees) - target behind
        assert weapon.check_firing_solution(ship_pos, 180, target_pos) is False

        # Ship facing down (270 degrees) - target behind
        assert weapon.check_firing_solution(ship_pos, 270, target_pos) is False

    def test_turret_tracking_independent_of_ship_angle(self, component_with_modifiers):
        """Full-arc turret should hit targets regardless of ship facing."""
        weapon_data = {
            'damage': 100,
            'range': 1000,
            'reload': 1.0,
            'firing_arc': 360,  # Full turret
            'facing_angle': 0,
        }
        weapon = WeaponAbility(component_with_modifiers, weapon_data)

        ship_pos = Vector2(0, 0)
        target_pos = Vector2(500, 0)

        # Should hit regardless of ship angle
        for ship_angle in range(0, 360, 45):
            assert weapon.check_firing_solution(ship_pos, ship_angle, target_pos) is True

    def test_fixed_mount_weapon(self, component_with_modifiers):
        """Fixed-mount weapon with very narrow arc."""
        weapon_data = {
            'damage': 100,
            'range': 1000,
            'reload': 1.0,
            'firing_arc': 10,  # Very narrow
            'facing_angle': 0,
        }
        weapon = WeaponAbility(component_with_modifiers, weapon_data)

        ship_pos = Vector2(0, 0)
        ship_angle = 0  # Facing right

        # Target directly ahead - should hit
        assert weapon.check_firing_solution(ship_pos, ship_angle, Vector2(500, 0)) is True

        # Target slightly off-center - should miss
        # 10 degree arc = 5 degrees each side
        # At 500 units, 6 degrees offset = sin(6) * 500 ~ 52 units
        assert weapon.check_firing_solution(ship_pos, ship_angle, Vector2(500, 60)) is False

    def test_rear_facing_weapon(self, component_with_modifiers):
        """Weapon mounted facing backwards."""
        weapon_data = {
            'damage': 100,
            'range': 1000,
            'reload': 1.0,
            'firing_arc': 90,
            'facing_angle': 180,  # Facing backwards
        }
        weapon = WeaponAbility(component_with_modifiers, weapon_data)

        ship_pos = Vector2(0, 0)
        ship_angle = 0  # Ship facing right

        # Target behind ship - weapon can hit
        assert weapon.check_firing_solution(ship_pos, ship_angle, Vector2(-500, 0)) is True

        # Target ahead of ship - weapon cannot hit
        assert weapon.check_firing_solution(ship_pos, ship_angle, Vector2(500, 0)) is False


# =============================================================================
# Stat Binding Introspection Tests
# =============================================================================

class TestWeaponStatBindingIntrospection:
    """Test stat binding introspection for weapon abilities."""

    def test_weapon_ability_consumed_stats(self):
        """WeaponAbility should declare its consumed stats."""
        consumed = WeaponAbility.get_consumed_stats()

        assert StatKey.DAMAGE_MULT in consumed
        assert StatKey.RANGE_MULT in consumed
        assert StatKey.RELOAD_MULT in consumed
        assert StatKey.ARC_SET in consumed
        assert StatKey.ARC_ADD in consumed

    def test_beam_weapon_includes_accuracy(self):
        """BeamWeaponAbility should include accuracy binding."""
        consumed = BeamWeaponAbility.get_consumed_stats()

        # Should include parent bindings
        assert StatKey.DAMAGE_MULT in consumed

        # Plus beam-specific
        assert StatKey.ACCURACY_ADD in consumed

    def test_seeker_weapon_includes_projectile_stats(self):
        """SeekerWeaponAbility should include projectile stat bindings."""
        consumed = SeekerWeaponAbility.get_consumed_stats()

        # Should include parent bindings
        assert StatKey.DAMAGE_MULT in consumed

        # Plus seeker-specific
        assert StatKey.ENDURANCE_MULT in consumed
        assert StatKey.PROJECTILE_DAMAGE_MULT in consumed
        assert StatKey.PROJECTILE_HP_MULT in consumed
        assert StatKey.PROJECTILE_STEALTH_LEVEL in consumed

    def test_get_effect_summary_with_active_modifiers(self, component_with_modifiers):
        """get_effect_summary should list active modifiers."""
        component_with_modifiers.stats = {
            'damage_mult': 1.5,
            'range_mult': 1.0,  # Default - should be skipped
        }

        weapon_data = {'damage': 100, 'range': 1000, 'reload': 1.0}
        weapon = WeaponAbility(component_with_modifiers, weapon_data)
        weapon.recalculate()

        summary = weapon.get_effect_summary()

        # Should include damage_mult (not at default 1.0)
        damage_effects = [e for e in summary if e['attribute'] == 'damage']
        assert len(damage_effects) == 1
        assert damage_effects[0]['stat_value'] == 1.5
        assert damage_effects[0]['base'] == 100.0
        assert damage_effects[0]['current'] == 150.0

        # Should NOT include range_mult (at default 1.0)
        range_effects = [e for e in summary if e['attribute'] == 'range']
        assert len(range_effects) == 0


# =============================================================================
# Cooldown Timing Integration Tests
# =============================================================================

class TestCooldownTimingIntegration:
    """Integration tests for weapon cooldown timing."""

    def test_fast_firing_weapon_timing(self, component_with_modifiers):
        """Fast-firing weapon should recover quickly."""
        weapon_data = {
            'damage': 10,
            'range': 500,
            'reload': 0.1,  # 100ms reload
        }
        weapon = WeaponAbility(component_with_modifiers, weapon_data)

        weapon.fire(Mock())
        assert weapon.can_fire() is False

        # Simulate 5 ticks (at default TICK_RATE)
        for _ in range(5):
            weapon.update()

        # Should be closer to ready (0.1 - 5 * TICK_RATE)
        expected_cooldown = 0.1 - (5 * PhysicsConfig.TICK_RATE)
        assert weapon.cooldown_timer == pytest.approx(expected_cooldown, abs=0.001)

    def test_reload_modifier_affects_cooldown(self, component_with_modifiers):
        """Reload modifier should affect actual cooldown set on fire."""
        component_with_modifiers.stats = {'reload_mult': 0.5}  # 50% faster reload

        weapon_data = {
            'damage': 100,
            'range': 1000,
            'reload': 2.0,
        }
        weapon = WeaponAbility(component_with_modifiers, weapon_data)
        weapon.recalculate()

        weapon.fire(Mock())

        assert weapon.cooldown_timer == pytest.approx(1.0, rel=1e-6)  # 2.0 * 0.5


# =============================================================================
# Resource Consumption Integration Tests
# =============================================================================

class TestResourceConsumptionIntegration:
    """Test weapon integration with resource consumption."""

    def test_fire_calls_consume_activation(self, component_with_modifiers):
        """Firing weapon should trigger component resource consumption."""
        weapon_data = {'damage': 100, 'range': 1000, 'reload': 1.0}
        weapon = WeaponAbility(component_with_modifiers, weapon_data)

        weapon.fire(Mock())

        component_with_modifiers.consume_activation.assert_called_once()

    def test_fire_blocked_does_not_consume(self, component_with_modifiers):
        """Blocked fire attempt should not consume resources."""
        weapon_data = {'damage': 100, 'range': 1000, 'reload': 1.0}
        weapon = WeaponAbility(component_with_modifiers, weapon_data)

        # Fire once to start cooldown
        weapon.fire(Mock())
        component_with_modifiers.consume_activation.reset_mock()

        # Try to fire again while on cooldown
        result = weapon.fire(Mock())

        assert result is False
        component_with_modifiers.consume_activation.assert_not_called()
