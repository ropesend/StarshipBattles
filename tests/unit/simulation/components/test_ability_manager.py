"""Tests for AbilityManager - extracted from Component god class.

PROJ-44 Phase 4: Tests ability instantiation, querying, and management.
PROJ-50 Phase 8: Updated to use fresh_registries for strict DI.
"""
import pytest
from game.simulation.components.component import create_component
from game.simulation.components.ability_manager import AbilityManager


class TestAbilityManagerInstantiation:
    """Test ability instantiation from component data."""

    def test_instantiate_abilities_creates_instances(self, fresh_registries):
        """Verify abilities are instantiated from component data."""
        railgun = create_component('railgun', registries=fresh_registries)

        # Should have weapon ability instance
        assert len(railgun.ability_instances) > 0

    def test_instantiate_abilities_preserves_state_on_sync(self, fresh_registries):
        """Verify sync doesn't destroy existing ability state."""
        railgun = create_component('railgun', registries=fresh_registries)
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

    def test_get_abilities_returns_all_matching(self, fresh_registries):
        """get_abilities should return all instances of a type."""
        railgun = create_component('railgun', registries=fresh_registries)

        weapons = railgun.get_abilities('WeaponAbility')
        assert len(weapons) >= 1

    def test_get_abilities_polymorphic_match(self, fresh_registries):
        """get_abilities should match subclasses."""
        railgun = create_component('railgun', registries=fresh_registries)

        # ProjectileWeaponAbility is a subclass of WeaponAbility
        weapons = railgun.get_abilities('WeaponAbility')
        projectile_weapons = railgun.get_abilities('ProjectileWeaponAbility')

        # Both should find the weapon
        assert len(weapons) >= 1
        assert len(projectile_weapons) >= 1

    def test_get_ability_returns_first_match(self, fresh_registries):
        """get_ability should return first matching instance."""
        railgun = create_component('railgun', registries=fresh_registries)

        weapon = railgun.get_ability('WeaponAbility')
        assert weapon is not None

    def test_get_ability_returns_none_when_not_found(self, fresh_registries):
        """get_ability should return None for missing ability."""
        railgun = create_component('railgun', registries=fresh_registries)

        result = railgun.get_ability('NonexistentAbility')
        assert result is None

    def test_has_ability_returns_true_for_existing(self, fresh_registries):
        """has_ability should return True for existing ability."""
        railgun = create_component('railgun', registries=fresh_registries)

        assert railgun.has_ability('WeaponAbility') is True

    def test_has_ability_returns_false_for_missing(self, fresh_registries):
        """has_ability should return False for missing ability."""
        railgun = create_component('railgun', registries=fresh_registries)

        assert railgun.has_ability('NonexistentAbility') is False


class TestAbilityManagerPDC:
    """Test PDC (Point Defense) ability detection."""

    def test_has_pdc_ability_true_for_pdc_weapon(self, fresh_registries):
        """has_pdc_ability should return True for PDC weapons."""
        pdc = create_component('point_defence_cannon', registries=fresh_registries)

        assert pdc.has_pdc_ability() is True

    def test_has_pdc_ability_false_for_regular_weapon(self, fresh_registries):
        """has_pdc_ability should return False for non-PDC weapons."""
        railgun = create_component('railgun', registries=fresh_registries)

        assert railgun.has_pdc_ability() is False


class TestAbilityManagerUIRows:
    """Test UI row generation from abilities."""

    def test_get_ui_rows_aggregates_all_abilities(self, fresh_registries):
        """get_ui_rows should collect rows from all abilities."""
        railgun = create_component('railgun', registries=fresh_registries)

        rows = railgun.get_ui_rows()

        # Should return a list of dicts
        assert isinstance(rows, list)
        # Weapon should have some UI rows (damage, cooldown, etc.)
        assert len(rows) >= 1

    def test_get_ui_rows_structure(self, fresh_registries):
        """UI rows should have label and value keys."""
        railgun = create_component('railgun', registries=fresh_registries)

        rows = railgun.get_ui_rows()

        if rows:
            for row in rows:
                assert 'label' in row
                assert 'value' in row


class TestAbilityManagerStandalone:
    """Test AbilityManager deprecated static methods (legacy API)."""

    def test_manager_get_abilities_static(self, fresh_registries):
        """AbilityManager.get_abilities_static should work on instance list."""
        railgun = create_component('railgun', registries=fresh_registries)

        weapons = AbilityManager.get_abilities_static('WeaponAbility', railgun.ability_instances)

        assert len(weapons) >= 1

    def test_manager_has_ability_static(self, fresh_registries):
        """AbilityManager.has_ability_static should work on instance list."""
        railgun = create_component('railgun', registries=fresh_registries)

        result = AbilityManager.has_ability_static('WeaponAbility', railgun.ability_instances)

        assert result is True

    def test_manager_get_ui_rows_static(self, fresh_registries):
        """AbilityManager.get_ui_rows_static should aggregate from instances."""
        railgun = create_component('railgun', registries=fresh_registries)

        rows = AbilityManager.get_ui_rows_static(railgun.ability_instances)

        assert isinstance(rows, list)


class TestStatefulAbilityManagerConstruction:
    """Test stateful AbilityManager delegate construction (PROJ-241)."""

    def test_construction_instantiates_and_builds_index(self, fresh_registries):
        """AbilityManager(component) should instantiate abilities and build index."""
        railgun = create_component('railgun', registries=fresh_registries)

        mgr = AbilityManager(railgun)

        assert len(mgr.ability_instances) > 0
        # Index should contain at least the concrete class name
        assert 'ProjectileWeaponAbility' in mgr._index

    def test_index_includes_mro_parents(self, fresh_registries):
        """Index should include MRO parents for polymorphic lookup."""
        railgun = create_component('railgun', registries=fresh_registries)

        mgr = AbilityManager(railgun)

        # ProjectileWeaponAbility inherits from WeaponAbility
        assert 'WeaponAbility' in mgr._index
        # Both should find the same weapon instance
        assert mgr._index['WeaponAbility'][0] is mgr._index['ProjectileWeaponAbility'][0]

    def test_index_stops_at_object(self, fresh_registries):
        """Index should not include 'object' as a key."""
        railgun = create_component('railgun', registries=fresh_registries)

        mgr = AbilityManager(railgun)

        assert 'object' not in mgr._index


class TestStatefulAbilityManagerQuery:
    """Test stateful AbilityManager query methods (PROJ-241)."""

    def test_get_abilities_returns_matching(self, fresh_registries):
        """get_abilities(name) should return correct instances via index."""
        railgun = create_component('railgun', registries=fresh_registries)
        mgr = AbilityManager(railgun)

        weapons = mgr.get_abilities('WeaponAbility')

        assert len(weapons) >= 1

    def test_get_abilities_polymorphic(self, fresh_registries):
        """get_abilities should match parent class names via index."""
        railgun = create_component('railgun', registries=fresh_registries)
        mgr = AbilityManager(railgun)

        weapons = mgr.get_abilities('WeaponAbility')
        projectile_weapons = mgr.get_abilities('ProjectileWeaponAbility')

        assert len(weapons) >= 1
        assert len(projectile_weapons) >= 1

    def test_get_abilities_returns_empty_for_missing(self, fresh_registries):
        """get_abilities should return empty list for non-existent ability."""
        railgun = create_component('railgun', registries=fresh_registries)
        mgr = AbilityManager(railgun)

        result = mgr.get_abilities('NonexistentAbility')

        assert result == []

    def test_get_ability_returns_first_match(self, fresh_registries):
        """get_ability(name) should return first match via index."""
        railgun = create_component('railgun', registries=fresh_registries)
        mgr = AbilityManager(railgun)

        weapon = mgr.get_ability('WeaponAbility')

        assert weapon is not None

    def test_get_ability_returns_none_for_missing(self, fresh_registries):
        """get_ability should return None for non-existent ability."""
        railgun = create_component('railgun', registries=fresh_registries)
        mgr = AbilityManager(railgun)

        result = mgr.get_ability('NonexistentAbility')

        assert result is None

    def test_has_ability_true(self, fresh_registries):
        """has_ability(name) should return True for existing ability."""
        railgun = create_component('railgun', registries=fresh_registries)
        mgr = AbilityManager(railgun)

        assert mgr.has_ability('WeaponAbility') is True

    def test_has_ability_false(self, fresh_registries):
        """has_ability(name) should return False for missing ability."""
        railgun = create_component('railgun', registries=fresh_registries)
        mgr = AbilityManager(railgun)

        assert mgr.has_ability('NonexistentAbility') is False


class TestStatefulAbilityManagerTags:
    """Test stateful AbilityManager tag-based queries (PROJ-241)."""

    def test_has_ability_with_tag_pdc_true(self, fresh_registries):
        """has_ability_with_tag('pdc') should return True for PDC components."""
        pdc = create_component('point_defence_cannon', registries=fresh_registries)
        mgr = AbilityManager(pdc)

        assert mgr.has_ability_with_tag('pdc') is True

    def test_has_ability_with_tag_pdc_false(self, fresh_registries):
        """has_ability_with_tag('pdc') should return False for non-PDC components."""
        railgun = create_component('railgun', registries=fresh_registries)
        mgr = AbilityManager(railgun)

        assert mgr.has_ability_with_tag('pdc') is False

    def test_has_ability_with_tag_nonexistent(self, fresh_registries):
        """has_ability_with_tag should return False for non-existent tag."""
        railgun = create_component('railgun', registries=fresh_registries)
        mgr = AbilityManager(railgun)

        assert mgr.has_ability_with_tag('nonexistent') is False

    def test_has_pdc_ability_delegates_to_tag(self, fresh_registries):
        """has_pdc_ability should use has_ability_with_tag('pdc')."""
        pdc = create_component('point_defence_cannon', registries=fresh_registries)
        mgr = AbilityManager(pdc)

        assert mgr.has_pdc_ability() is True

        railgun = create_component('railgun', registries=fresh_registries)
        mgr2 = AbilityManager(railgun)

        assert mgr2.has_pdc_ability() is False


class TestStatefulAbilityManagerPreservation:
    """Test stateful AbilityManager preserves existing instances (PROJ-241)."""

    def test_instantiate_preserves_existing_state(self, fresh_registries):
        """instantiate_and_index should preserve existing instances (cooldown state)."""
        railgun = create_component('railgun', registries=fresh_registries)
        mgr = AbilityManager(railgun)

        weapon = mgr.get_ability('WeaponAbility')
        if weapon:
            weapon.cooldown_timer = 5.0

            # Re-instantiate
            mgr.instantiate_and_index()

            weapon_after = mgr.get_ability('WeaponAbility')
            assert weapon_after.cooldown_timer == 5.0


class TestStatefulAbilityManagerUIRows:
    """Test stateful AbilityManager UI row aggregation (PROJ-241)."""

    def test_get_ui_rows_returns_list(self, fresh_registries):
        """get_ui_rows should return aggregated UI rows from all instances."""
        railgun = create_component('railgun', registries=fresh_registries)
        mgr = AbilityManager(railgun)

        rows = mgr.get_ui_rows()

        assert isinstance(rows, list)
        assert len(rows) >= 1


class TestStatefulAbilityManagerProperty:
    """Test stateful AbilityManager.ability_instances property (PROJ-241)."""

    def test_ability_instances_property_returns_list(self, fresh_registries):
        """ability_instances property should return the current list."""
        railgun = create_component('railgun', registries=fresh_registries)
        mgr = AbilityManager(railgun)

        instances = mgr.ability_instances

        assert isinstance(instances, list)
        assert len(instances) > 0
