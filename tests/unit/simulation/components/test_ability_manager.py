"""Tests for AbilityManager - extracted from Component god class.

PROJ-44 Phase 4: Tests ability instantiation, querying, and management.
"""
import pytest
from game.simulation.components.component import create_component
from game.simulation.components.ability_manager import AbilityManager


class TestAbilityManagerInstantiation:
    """Test ability instantiation from component data."""

    def test_instantiate_abilities_creates_instances(self):
        """Verify abilities are instantiated from component data."""
        railgun = create_component('railgun')

        # Should have weapon ability instance
        assert len(railgun.ability_instances) > 0

    def test_instantiate_abilities_preserves_state_on_sync(self):
        """Verify sync doesn't destroy existing ability state."""
        railgun = create_component('railgun')
        weapon = railgun.get_ability('WeaponAbility')

        # Simulate cooldown state
        if weapon:
            original_timer = weapon.cooldown_timer
            weapon.cooldown_timer = 5.0

            # Re-instantiate (simulates recalculate_stats)
            railgun._instantiate_abilities()

            # State should be preserved
            weapon_after = railgun.get_ability('WeaponAbility')
            assert weapon_after.cooldown_timer == 5.0


class TestAbilityManagerQuerying:
    """Test ability querying methods."""

    def test_get_abilities_returns_all_matching(self):
        """get_abilities should return all instances of a type."""
        railgun = create_component('railgun')

        weapons = railgun.get_abilities('WeaponAbility')
        assert len(weapons) >= 1

    def test_get_abilities_polymorphic_match(self):
        """get_abilities should match subclasses."""
        railgun = create_component('railgun')

        # ProjectileWeaponAbility is a subclass of WeaponAbility
        weapons = railgun.get_abilities('WeaponAbility')
        projectile_weapons = railgun.get_abilities('ProjectileWeaponAbility')

        # Both should find the weapon
        assert len(weapons) >= 1
        assert len(projectile_weapons) >= 1

    def test_get_ability_returns_first_match(self):
        """get_ability should return first matching instance."""
        railgun = create_component('railgun')

        weapon = railgun.get_ability('WeaponAbility')
        assert weapon is not None

    def test_get_ability_returns_none_when_not_found(self):
        """get_ability should return None for missing ability."""
        railgun = create_component('railgun')

        result = railgun.get_ability('NonexistentAbility')
        assert result is None

    def test_has_ability_returns_true_for_existing(self):
        """has_ability should return True for existing ability."""
        railgun = create_component('railgun')

        assert railgun.has_ability('WeaponAbility') is True

    def test_has_ability_returns_false_for_missing(self):
        """has_ability should return False for missing ability."""
        railgun = create_component('railgun')

        assert railgun.has_ability('NonexistentAbility') is False


class TestAbilityManagerPDC:
    """Test PDC (Point Defense) ability detection."""

    def test_has_pdc_ability_true_for_pdc_weapon(self):
        """has_pdc_ability should return True for PDC weapons."""
        pdc = create_component('point_defence_cannon')

        assert pdc.has_pdc_ability() is True

    def test_has_pdc_ability_false_for_regular_weapon(self):
        """has_pdc_ability should return False for non-PDC weapons."""
        railgun = create_component('railgun')

        assert railgun.has_pdc_ability() is False


class TestAbilityManagerUIRows:
    """Test UI row generation from abilities."""

    def test_get_ui_rows_aggregates_all_abilities(self):
        """get_ui_rows should collect rows from all abilities."""
        railgun = create_component('railgun')

        rows = railgun.get_ui_rows()

        # Should return a list of dicts
        assert isinstance(rows, list)
        # Weapon should have some UI rows (damage, cooldown, etc.)
        assert len(rows) >= 1

    def test_get_ui_rows_structure(self):
        """UI rows should have label and value keys."""
        railgun = create_component('railgun')

        rows = railgun.get_ui_rows()

        if rows:
            for row in rows:
                assert 'label' in row
                assert 'value' in row


class TestAbilityManagerStandalone:
    """Test AbilityManager as standalone utility class."""

    def test_manager_get_abilities(self):
        """AbilityManager.get_abilities should work on instance list."""
        railgun = create_component('railgun')

        # Use standalone manager function
        weapons = AbilityManager.get_abilities('WeaponAbility', railgun.ability_instances)

        assert len(weapons) >= 1

    def test_manager_has_ability(self):
        """AbilityManager.has_ability should work on instance list."""
        railgun = create_component('railgun')

        result = AbilityManager.has_ability('WeaponAbility', railgun.ability_instances)

        assert result is True

    def test_manager_get_ui_rows(self):
        """AbilityManager.get_ui_rows should aggregate from instances."""
        railgun = create_component('railgun')

        rows = AbilityManager.get_ui_rows(railgun.ability_instances)

        assert isinstance(rows, list)
