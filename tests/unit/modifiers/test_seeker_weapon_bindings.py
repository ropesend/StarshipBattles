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
import pytest
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


class TestSeekerWeaponAbilityRecalculate:
    """Tests for SeekerWeaponAbility.recalculate() with seeker stats."""

    def test_recalculate_applies_endurance_mult(self):
        """recalculate() should apply endurance_mult from stats."""
        from game.simulation.components.abilities.weapons import SeekerWeaponAbility

        class MockComponent:
            def __init__(self):
                self.stats = {'endurance_mult': 2.0}
                self.ability_stats = {}
                self.data = {}

        component = MockComponent()
        ability = SeekerWeaponAbility(component, {
            'damage': 100,
            'range': 0,  # Will be calculated from endurance
            'reload': 2.0,
            'endurance': 5.0,
            'projectile_speed': 500
        })

        assert ability._base_endurance == 5.0
        ability.recalculate()
        assert ability.endurance == pytest.approx(10.0)

    def test_recalculate_applies_projectile_damage_mult(self):
        """recalculate() should apply projectile_damage_mult from stats."""
        from game.simulation.components.abilities.weapons import SeekerWeaponAbility

        class MockComponent:
            def __init__(self):
                self.stats = {'projectile_damage_mult': 3.0}
                self.ability_stats = {}
                self.data = {}

        component = MockComponent()
        ability = SeekerWeaponAbility(component, {
            'damage': 100,
            'range': 1000,
            'reload': 2.0,
            'endurance': 5.0,
            'projectile_speed': 500,
            'projectile_damage': 50
        })

        ability.recalculate()
        assert ability.projectile_damage == pytest.approx(150)

    def test_recalculate_applies_projectile_hp_mult(self):
        """recalculate() should apply projectile_hp_mult from stats."""
        from game.simulation.components.abilities.weapons import SeekerWeaponAbility

        class MockComponent:
            def __init__(self):
                self.stats = {'projectile_hp_mult': 5.0}
                self.ability_stats = {}
                self.data = {}

        component = MockComponent()
        ability = SeekerWeaponAbility(component, {
            'damage': 100,
            'range': 1000,
            'reload': 2.0,
            'endurance': 5.0,
            'projectile_speed': 500,
            'projectile_hp': 10
        })

        ability.recalculate()
        assert ability.projectile_hp == pytest.approx(50)

    def test_recalculate_applies_projectile_stealth_add(self):
        """recalculate() should apply projectile_stealth_level (add) from stats."""
        from game.simulation.components.abilities.weapons import SeekerWeaponAbility

        class MockComponent:
            def __init__(self):
                self.stats = {'projectile_stealth_level': 3}
                self.ability_stats = {}
                self.data = {}

        component = MockComponent()
        ability = SeekerWeaponAbility(component, {
            'damage': 100,
            'range': 1000,
            'reload': 2.0,
            'endurance': 5.0,
            'projectile_speed': 500,
            'projectile_stealth': 0
        })

        ability.recalculate()
        assert ability.projectile_stealth == 3
