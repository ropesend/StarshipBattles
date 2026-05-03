"""
Tests for SeekerWeaponAbility STAT_BINDINGS - Phase 3 Task 3.4

TDD: Write tests FIRST, then implement to make them pass.

SeekerWeaponAbility needs bindings for:
- All WeaponAbility stats (damage, range, reload, arc)
- ENDURANCE_MULT for seeker endurance
- PROJECTILE_DAMAGE_MULT for seeker warhead damage
- PROJECTILE_HP_MULT for seeker hull points
- PROJECTILE_STEALTH_LEVEL (add) for seeker stealth

Note: Some seeker stats (like projectile_hp, projectile_stealth) may not have
base attributes defined yet. We track what the bindings SHOULD be for the
declarative contract, even if recalculate() doesn't fully use them yet.
"""
from game.simulation.components.abilities.stat_keys import StatKey, AbilityStatBinding


class TestSeekerWeaponAbilityStatBindings:
    """Tests for SeekerWeaponAbility STAT_BINDINGS declarations."""

    def test_seeker_weapon_inherits_weapon_bindings(self):
        """SeekerWeaponAbility should inherit all WeaponAbility bindings."""
        from game.simulation.components.abilities.weapons import SeekerWeaponAbility, WeaponAbility

        seeker_stats = SeekerWeaponAbility.get_consumed_stats()
        weapon_stats = WeaponAbility.get_consumed_stats()

        for stat in weapon_stats:
            assert stat in seeker_stats

    def test_seeker_weapon_has_endurance_binding(self):
        """SeekerWeaponAbility should have ENDURANCE_MULT binding for 'endurance'."""
        from game.simulation.components.abilities.weapons import SeekerWeaponAbility

        endurance_bindings = [b for b in SeekerWeaponAbility.STAT_BINDINGS
                             if b.stat_key == StatKey.ENDURANCE_MULT]
        assert len(endurance_bindings) == 1

        binding = endurance_bindings[0]
        assert binding.attribute_name == 'endurance'
        assert binding.operation == 'multiply'

    def test_seeker_weapon_has_projectile_damage_binding(self):
        """SeekerWeaponAbility should have PROJECTILE_DAMAGE_MULT binding."""
        from game.simulation.components.abilities.weapons import SeekerWeaponAbility

        pd_bindings = [b for b in SeekerWeaponAbility.STAT_BINDINGS
                      if b.stat_key == StatKey.PROJECTILE_DAMAGE_MULT]
        assert len(pd_bindings) == 1

        binding = pd_bindings[0]
        assert binding.attribute_name == 'projectile_damage'
        assert binding.operation == 'multiply'

    def test_seeker_weapon_has_projectile_hp_binding(self):
        """SeekerWeaponAbility should have PROJECTILE_HP_MULT binding."""
        from game.simulation.components.abilities.weapons import SeekerWeaponAbility

        hp_bindings = [b for b in SeekerWeaponAbility.STAT_BINDINGS
                      if b.stat_key == StatKey.PROJECTILE_HP_MULT]
        assert len(hp_bindings) == 1

        binding = hp_bindings[0]
        assert binding.attribute_name == 'projectile_hp'
        assert binding.operation == 'multiply'

    def test_seeker_weapon_has_projectile_stealth_binding(self):
        """SeekerWeaponAbility should have PROJECTILE_STEALTH_LEVEL binding (add)."""
        from game.simulation.components.abilities.weapons import SeekerWeaponAbility

        stealth_bindings = [b for b in SeekerWeaponAbility.STAT_BINDINGS
                           if b.stat_key == StatKey.PROJECTILE_STEALTH_LEVEL]
        assert len(stealth_bindings) == 1

        binding = stealth_bindings[0]
        assert binding.attribute_name == 'projectile_stealth'
        assert binding.operation == 'add'

    def test_seeker_weapon_get_consumed_stats(self):
        """get_consumed_stats() should include all seeker-specific stats."""
        from game.simulation.components.abilities.weapons import SeekerWeaponAbility

        consumed = SeekerWeaponAbility.get_consumed_stats()

        # Inherited weapon stats
        assert StatKey.DAMAGE_MULT in consumed
        assert StatKey.RANGE_MULT in consumed
        assert StatKey.RELOAD_MULT in consumed

        # Seeker-specific stats
        assert StatKey.ENDURANCE_MULT in consumed
        assert StatKey.PROJECTILE_DAMAGE_MULT in consumed
        assert StatKey.PROJECTILE_HP_MULT in consumed
        assert StatKey.PROJECTILE_STEALTH_LEVEL in consumed


# NOTE: SeekerWeaponAbility.recalculate() coverage lives in
# tests/unit/simulation/components/abilities/test_weapons_isolation.py
# (TestSeekerWeapon::test_recalculate_applies_seeker_modifiers, lines ~1011-1026),
# which exercises endurance / projectile_damage / projectile_hp / projectile_stealth
# in a single consolidated test. Per PROJ-322 Task 1.2 (S09-CAT4-002) the four
# duplicated individual recalculate tests previously here have been removed.
