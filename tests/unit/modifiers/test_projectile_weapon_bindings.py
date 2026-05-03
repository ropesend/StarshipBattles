"""
Tests for ProjectileWeaponAbility STAT_BINDINGS - Phase 3 Task 3.3

TDD: Write tests FIRST, then implement to make them pass.

Note: ProjectileWeaponAbility doesn't add new stats beyond WeaponAbility,
but it should inherit all parent bindings.
"""
import pytest

from game.simulation.components.abilities.weapons import (
    ProjectileWeaponAbility,
    WeaponAbility,
)


class _MockComponent:
    def __init__(self, stats):
        self.stats = stats
        self.ability_stats = {}
        self.data = {}


class TestProjectileWeaponAbilityStatBindings:
    """Tests for ProjectileWeaponAbility STAT_BINDINGS declarations."""

    def test_projectile_weapon_inherits_weapon_bindings(self):
        """ProjectileWeaponAbility should inherit all WeaponAbility bindings."""
        projectile_stats = ProjectileWeaponAbility.get_consumed_stats()
        weapon_stats = WeaponAbility.get_consumed_stats()

        # Projectile should consume at least all weapon stats
        for stat in weapon_stats:
            assert stat in projectile_stats

    def test_projectile_weapon_has_stat_bindings(self):
        """ProjectileWeaponAbility should have STAT_BINDINGS attribute."""
        assert hasattr(ProjectileWeaponAbility, 'STAT_BINDINGS')
        assert isinstance(ProjectileWeaponAbility.STAT_BINDINGS, list)
        # Should have at least the 5 weapon bindings
        assert len(ProjectileWeaponAbility.STAT_BINDINGS) >= 5


class TestProjectileWeaponAbilityRecalculate:
    """Tests for ProjectileWeaponAbility.recalculate() with weapon stats."""

    def test_recalculate_applies_damage_mult(self):
        """recalculate() should apply damage_mult from stats."""
        component = _MockComponent({'damage_mult': 2.0})
        ability = ProjectileWeaponAbility(component, {
            'damage': 75,
            'range': 800,
            'reload': 1.5,
            'projectile_speed': 500
        })

        ability.recalculate()
        assert ability.damage == pytest.approx(150)

    def test_recalculate_applies_range_mult(self):
        """recalculate() should apply range_mult from stats."""
        component = _MockComponent({'range_mult': 4.0})
        ability = ProjectileWeaponAbility(component, {
            'damage': 75,
            'range': 1000,
            'reload': 1.5,
            'projectile_speed': 500
        })

        ability.recalculate()
        assert ability.range == pytest.approx(4000)
