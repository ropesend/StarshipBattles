"""Tests for ship loading and expected_stats validation.

These tests ensure that ships loaded from JSON files have stats that match
the expected_stats saved by the ship builder, validating that modifier
stacking is working correctly in the simulator.
"""
import pytest

from game.simulation.components.component import create_component


class TestModifierStacking:
    """Test that modifier stacking calculates HP correctly."""

    def test_simple_size_mount_hp_multiplier(self, fresh_registries):
        """simple_size_mount should multiply HP by the scale value."""
        laser = create_component('laser_cannon', registries=fresh_registries)
        base_hp = laser.max_hp

        # Add 8x size mount
        laser.add_modifier('simple_size_mount', 8)
        laser.recalculate_stats()

        expected_hp = base_hp * 8
        assert laser.max_hp == expected_hp, \
            f"Size mount 8x: expected {expected_hp}, got {laser.max_hp}"

    def test_range_mount_hp_multiplier(self, fresh_registries):
        """range_mount should multiply HP by 3.5^level."""
        laser = create_component('laser_cannon', registries=fresh_registries)
        base_hp = laser.max_hp

        # Add range mount level 2
        laser.add_modifier('range_mount', 2)
        laser.recalculate_stats()

        expected_multiplier = 3.5 ** 2  # 12.25
        expected_hp = int(base_hp * expected_multiplier)
        assert laser.max_hp == expected_hp, \
            f"Range mount level 2: expected {expected_hp}, got {laser.max_hp}"

    def test_stacked_modifiers_multiplicative(self, fresh_registries):
        """Multiple modifiers should stack multiplicatively."""
        laser = create_component('laser_cannon', registries=fresh_registries)
        base_hp = laser.max_hp

        # Add both size_mount(8) and range_mount(2)
        laser.add_modifier('simple_size_mount', 8)
        laser.add_modifier('range_mount', 2)
        laser.recalculate_stats()

        # 8 * 3.5^2 = 8 * 12.25 = 98
        expected_multiplier = 8 * (3.5 ** 2)
        expected_hp = int(base_hp * expected_multiplier)
        assert laser.max_hp == expected_hp, \
            f"Stacked modifiers: expected {expected_hp}, got {laser.max_hp}"

    def test_turret_mount_no_hp_change(self, fresh_registries):
        """turret_mount should not affect HP (only mass)."""
        laser = create_component('laser_cannon', registries=fresh_registries)
        base_hp = laser.max_hp
        base_mass = laser.mass

        laser.add_modifier('turret_mount', 180)
        laser.recalculate_stats()

        assert laser.max_hp == base_hp, \
            f"Turret mount should not change HP: expected {base_hp}, got {laser.max_hp}"
        assert laser.mass > base_mass, \
            "Turret mount should increase mass"


class TestAllShipDesigns:
    """Test all ship designs in the ships/ folder."""

    def test_all_ships_match_expected_stats(self, fresh_registries):
        """All ships should match their expected_stats if present.

        PROJ-478 Phase 1 Task 1.10 added the ``len(ship_files) >= 1`` guard
        below to make the test fail-loud instead of passing vacuously when
        the directory is empty. Adding the guard surfaced a separate latent
        issue: the intended fixtures directory ``tests/unit/ships/`` has
        never existed in this repo. Nearby fixtures under
        ``tests/unit/data/ships/`` cannot be used because they reference
        the test-only component registry (``test_engine_no_fuel`` etc.) and
        fail to load against the production ``fresh_registries`` fixture.

        Skipping so the suite stays green while the gap is recorded; see
        Projects/active_projects/PROJ-478/phase_1_checklist.md Task 1.10
        notes for the full discovered-issue handoff.
        """
        pytest.skip(
            "PROJ-478 discovered-issue: no real-ship fixtures exist for "
            "tests/unit/ships/; tests/unit/data/ships/ ships need the "
            "test-only component registry. Needs fixture sourcing or test "
            "redesign — surface to project."
        )
