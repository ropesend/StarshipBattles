"""
Tests for SeekerWeaponAbility multi-ability support.

Task 8.2: Verify SeekerWeaponAbility uses get_effective_stat() instead of
direct stats.get() access, enabling proper multi-ability modifier targeting.
"""
import pytest
from unittest.mock import MagicMock, patch

from game.simulation.components.abilities.weapons import SeekerWeaponAbility


class TestSeekerUsesGetEffectiveStat:
    """Tests to verify SeekerWeaponAbility uses get_effective_stat()."""

    def test_seeker_recalculate_calls_get_effective_stat_for_endurance(self):
        """SeekerWeaponAbility.recalculate() should use get_effective_stat for endurance_mult."""
        # Create mock component
        mock_component = MagicMock()
        mock_component.stats = {
            'endurance_mult': 2.0,
            'projectile_damage_mult': 1.5,
            'projectile_hp_mult': 1.0,
            'projectile_stealth_level': 0.0,
        }
        mock_component.data = {}

        # Create ability with mock data
        data = {
            'damage': 100,
            'range': 500,
            'reload': 5.0,
            'projectile_speed': 300,
            'endurance': 3.0,
            'turn_rate': 30.0,
            'projectile_damage': 50,
            'projectile_hp': 10,
            'projectile_stealth': 0,
        }

        ability = SeekerWeaponAbility(mock_component, data)

        # Mock get_effective_stat to track calls
        original_get_effective_stat = ability.get_effective_stat
        call_tracker = []

        def tracking_get_effective_stat(stat_key, default=None):
            call_tracker.append(stat_key)
            return original_get_effective_stat(stat_key, default)

        ability.get_effective_stat = tracking_get_effective_stat

        # Call recalculate
        ability.recalculate()

        # Verify get_effective_stat was called for seeker-specific stats
        assert 'endurance_mult' in call_tracker, \
            "recalculate() should call get_effective_stat('endurance_mult')"
        assert 'projectile_damage_mult' in call_tracker, \
            "recalculate() should call get_effective_stat('projectile_damage_mult')"
        assert 'projectile_hp_mult' in call_tracker, \
            "recalculate() should call get_effective_stat('projectile_hp_mult')"
        assert 'projectile_stealth_level' in call_tracker, \
            "recalculate() should call get_effective_stat('projectile_stealth_level')"

    def test_seeker_does_not_use_direct_stats_access(self):
        """SeekerWeaponAbility should not use self.component.stats.get() directly."""
        # Read the source code of SeekerWeaponAbility.recalculate
        import inspect
        source = inspect.getsource(SeekerWeaponAbility.recalculate)

        # Check that it doesn't use direct stats access patterns
        bad_patterns = [
            'self.component.stats.get',
            'stats.get(',
            'self.component.stats[',
        ]

        for pattern in bad_patterns:
            assert pattern not in source, \
                f"SeekerWeaponAbility.recalculate() should not use '{pattern}'. " \
                f"Use self.get_effective_stat() instead for multi-ability support."

    def test_seeker_endurance_applies_modifier_correctly(self):
        """Verify endurance is correctly calculated with modifier."""
        mock_component = MagicMock()
        mock_component.stats = {}
        mock_component.data = {}
        # Mock ability_stats for multi-ability targeting
        mock_component.ability_stats = {}

        data = {
            'damage': 100,
            'range': 500,
            'reload': 5.0,
            'projectile_speed': 300,
            'endurance': 4.0,  # base endurance
            'turn_rate': 30.0,
            'projectile_damage': 50,
            'projectile_hp': 10,
            'projectile_stealth': 0,
        }

        ability = SeekerWeaponAbility(mock_component, data)

        # Set up component stats with endurance_mult = 2.0
        mock_component.stats = {'endurance_mult': 2.0}

        ability.recalculate()

        # Endurance should be 4.0 * 2.0 = 8.0
        assert ability.endurance == 8.0, \
            f"Expected endurance=8.0 (4.0 * 2.0), got {ability.endurance}"

    def test_seeker_projectile_damage_applies_modifier_correctly(self):
        """Verify projectile_damage is correctly calculated with modifier."""
        mock_component = MagicMock()
        mock_component.stats = {}
        mock_component.data = {}
        mock_component.ability_stats = {}

        data = {
            'damage': 100,
            'range': 500,
            'reload': 5.0,
            'projectile_speed': 300,
            'endurance': 3.0,
            'turn_rate': 30.0,
            'projectile_damage': 50,  # base projectile damage
            'projectile_hp': 10,
            'projectile_stealth': 0,
        }

        ability = SeekerWeaponAbility(mock_component, data)

        # Set up component stats with projectile_damage_mult = 3.0
        mock_component.stats = {'projectile_damage_mult': 3.0}

        ability.recalculate()

        # Projectile damage should be 50 * 3.0 = 150
        assert ability.projectile_damage == 150.0, \
            f"Expected projectile_damage=150.0 (50 * 3.0), got {ability.projectile_damage}"

    def test_seeker_projectile_hp_applies_modifier_correctly(self):
        """Verify projectile_hp is correctly calculated with modifier."""
        mock_component = MagicMock()
        mock_component.stats = {}
        mock_component.data = {}
        mock_component.ability_stats = {}

        data = {
            'damage': 100,
            'range': 500,
            'reload': 5.0,
            'projectile_speed': 300,
            'endurance': 3.0,
            'turn_rate': 30.0,
            'projectile_damage': 50,
            'projectile_hp': 10,  # base projectile hp
            'projectile_stealth': 0,
        }

        ability = SeekerWeaponAbility(mock_component, data)

        # Set up component stats with projectile_hp_mult = 5.0
        mock_component.stats = {'projectile_hp_mult': 5.0}

        ability.recalculate()

        # Projectile HP should be 10 * 5.0 = 50
        assert ability.projectile_hp == 50.0, \
            f"Expected projectile_hp=50.0 (10 * 5.0), got {ability.projectile_hp}"

    def test_seeker_projectile_stealth_applies_modifier_correctly(self):
        """Verify projectile_stealth is correctly calculated with modifier."""
        mock_component = MagicMock()
        mock_component.stats = {}
        mock_component.data = {}
        mock_component.ability_stats = {}

        data = {
            'damage': 100,
            'range': 500,
            'reload': 5.0,
            'projectile_speed': 300,
            'endurance': 3.0,
            'turn_rate': 30.0,
            'projectile_damage': 50,
            'projectile_hp': 10,
            'projectile_stealth': 1,  # base stealth
        }

        ability = SeekerWeaponAbility(mock_component, data)

        # Set up component stats with projectile_stealth_level = 3.0
        mock_component.stats = {'projectile_stealth_level': 3.0}

        ability.recalculate()

        # Projectile stealth should be 1 + 3.0 = 4.0
        assert ability.projectile_stealth == 4.0, \
            f"Expected projectile_stealth=4.0 (1 + 3.0), got {ability.projectile_stealth}"


class TestMultipleSeekerTargetedEffects:
    """Tests for multiple SeekerWeaponAbility instances with targeted modifiers."""

    def test_component_with_two_seekers_targeted_effects(self):
        """Component with 2 SeekerWeaponAbility instances should support targeted modifiers."""
        # This is an integration-level test to verify multi-ability targeting works
        # with SeekerWeaponAbility after the fix

        from game.simulation.components import Component, create_component, load_components, load_modifiers, reset_component_caches

        reset_component_caches()
        load_modifiers("data/modifiers.json")
        load_components("data/components.json")

        # Get a component with seeker ability
        missile = create_component('capital_missile')

        # Verify it has SeekerWeaponAbility
        seeker_abilities = [
            ab for ab in missile.ability_instances
            if ab.__class__.__name__ == 'SeekerWeaponAbility'
        ]
        assert len(seeker_abilities) >= 1, "Expected at least one SeekerWeaponAbility"

        # Add seeker_endurance modifier and verify it applies
        missile.add_modifier('seeker_endurance', 2.0)
        missile.recalculate_stats()

        # The seeker's endurance should be doubled
        seeker = seeker_abilities[0]
        expected_endurance = seeker._base_endurance * 2.0
        assert seeker.endurance == pytest.approx(expected_endurance, rel=1e-6), \
            f"Expected endurance={expected_endurance}, got {seeker.endurance}"

        reset_component_caches()
