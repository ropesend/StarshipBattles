"""
Regression tests for utility modifiers (propulsion, facing, automation, efficiency).

Also includes formula verification tests to ensure mathematical correctness.

Agent Instructions:
- Run these tests BEFORE making any changes to verify they pass
- Run these tests AFTER each phase to verify no regressions
- If a test fails after refactoring, the refactored code has a bug that must be fixed
"""
import pytest
import math

from game.simulation.components.component import create_component

from .conftest import (
    snapshot_full_component, compare_snapshots, load_snapshot, save_snapshot
)


class TestPropulsionModifierRegression:
    """Regression tests for propulsion modifiers."""

    def test_standard_engine_no_modifiers(self, setup_registries):
        """Baseline: Standard engine with no modifiers."""
        engine = create_component('standard_engine', registries=setup_registries)
        engine.recalculate_stats()

        snapshot = snapshot_full_component(engine)
        expected = load_snapshot('standard_engine_no_modifiers')

        if expected is None:
            save_snapshot('standard_engine_no_modifiers', snapshot)
            pytest.skip("Baseline snapshot created - re-run test")

        diffs = compare_snapshots(snapshot, expected)
        assert not diffs, f"Regression detected:\n" + "\n".join(diffs)

    @pytest.mark.parametrize("scale", [1, 2, 4, 8, 16])
    def test_standard_engine_simple_size(self, setup_registries, scale):
        """Standard engine with simple_size_mount at different scales."""
        engine = create_component('standard_engine', registries=setup_registries)
        if scale > 1:
            engine.add_modifier('simple_size_mount', scale)
        engine.recalculate_stats()

        snapshot = snapshot_full_component(engine)
        snapshot_name = f'standard_engine_size_{scale}'
        expected = load_snapshot(snapshot_name)

        if expected is None:
            save_snapshot(snapshot_name, snapshot)
            pytest.skip(f"Baseline snapshot '{snapshot_name}' created - re-run test")

        diffs = compare_snapshots(snapshot, expected)
        assert not diffs, f"Regression detected:\n" + "\n".join(diffs)

    def test_thruster_no_modifiers(self, setup_registries):
        """Baseline: Thruster with no modifiers."""
        thruster = create_component('thruster', registries=setup_registries)
        thruster.recalculate_stats()

        snapshot = snapshot_full_component(thruster)
        expected = load_snapshot('thruster_no_modifiers')

        if expected is None:
            save_snapshot('thruster_no_modifiers', snapshot)
            pytest.skip("Baseline snapshot created - re-run test")

        diffs = compare_snapshots(snapshot, expected)
        assert not diffs, f"Regression detected:\n" + "\n".join(diffs)


class TestFacingModifierRegression:
    """Regression tests for facing modifier."""

    def test_railgun_no_facing(self, setup_registries):
        """Baseline: Railgun with no facing modifier (default forward)."""
        railgun = create_component('railgun', registries=setup_registries)
        railgun.recalculate_stats()

        snapshot = snapshot_full_component(railgun)
        expected = load_snapshot('railgun_facing_0')

        if expected is None:
            save_snapshot('railgun_facing_0', snapshot)
            pytest.skip("Baseline snapshot created - re-run test")

        diffs = compare_snapshots(snapshot, expected)
        assert not diffs, f"Regression detected:\n" + "\n".join(diffs)

    @pytest.mark.parametrize("angle", [0, 45, 90, 180, 270])
    def test_railgun_facing_angles(self, setup_registries, angle):
        """Railgun with facing modifier at different angles."""
        railgun = create_component('railgun', registries=setup_registries)
        if angle > 0:
            railgun.add_modifier('facing', angle)
        railgun.recalculate_stats()

        snapshot = snapshot_full_component(railgun)
        snapshot_name = f'railgun_facing_{angle}'
        expected = load_snapshot(snapshot_name)

        if expected is None:
            save_snapshot(snapshot_name, snapshot)
            pytest.skip(f"Baseline snapshot '{snapshot_name}' created - re-run test")

        diffs = compare_snapshots(snapshot, expected)
        assert not diffs, f"Regression detected:\n" + "\n".join(diffs)

    def test_laser_cannon_facing(self, setup_registries):
        """Laser cannon with facing modifier."""
        laser = create_component('laser_cannon', registries=setup_registries)
        laser.add_modifier('facing', 90)
        laser.recalculate_stats()

        snapshot = snapshot_full_component(laser)
        expected = load_snapshot('laser_cannon_facing_90')

        if expected is None:
            save_snapshot('laser_cannon_facing_90', snapshot)
            pytest.skip("Baseline snapshot created - re-run test")

        diffs = compare_snapshots(snapshot, expected)
        assert not diffs, f"Regression detected:\n" + "\n".join(diffs)


class TestUtilityModifierRegression:
    """Regression tests for utility modifiers (automation, efficiency)."""

    @pytest.mark.parametrize("reduction", [0.0, 0.25, 0.5, 0.75, 0.99])
    def test_crew_quarters_automation(self, setup_registries, reduction):
        """Crew quarters with automation at different reduction levels."""
        quarters = create_component('crew_quarters', registries=setup_registries)
        if reduction > 0.0:
            quarters.add_modifier('automation', reduction)
        quarters.recalculate_stats()

        snapshot = snapshot_full_component(quarters)
        snapshot_name = f'crew_quarters_automation_{reduction:.2f}'
        expected = load_snapshot(snapshot_name)

        if expected is None:
            save_snapshot(snapshot_name, snapshot)
            pytest.skip(f"Baseline snapshot '{snapshot_name}' created - re-run test")

        diffs = compare_snapshots(snapshot, expected)
        assert not diffs, f"Regression detected:\n" + "\n".join(diffs)

    @pytest.mark.parametrize("resource_mult", [1.0, 0.5, 0.25, 0.1])
    def test_generator_efficiency_mount(self, setup_registries, resource_mult):
        """Generator with efficiency_mount at different resource multipliers."""
        generator = create_component('generator', registries=setup_registries)
        if resource_mult < 1.0:
            generator.add_modifier('efficiency_mount', resource_mult)
        generator.recalculate_stats()

        snapshot = snapshot_full_component(generator)
        snapshot_name = f'generator_efficiency_{resource_mult:.2f}'
        expected = load_snapshot(snapshot_name)

        if expected is None:
            save_snapshot(snapshot_name, snapshot)
            pytest.skip(f"Baseline snapshot '{snapshot_name}' created - re-run test")

        diffs = compare_snapshots(snapshot, expected)
        assert not diffs, f"Regression detected:\n" + "\n".join(diffs)


class TestModifierFormulaVerification:
    """
    Direct verification of modifier formulas.
    These tests verify the mathematical correctness of each handler.
    """

    def test_hardened_mount_formula(self, setup_registries):
        """Verify hardened_mount: HP = mass^2"""
        railgun = create_component('railgun', registries=setup_registries)
        base_mass = railgun.base_mass
        base_hp = railgun.base_max_hp

        for mass_mult in [1.0, 2.0, 3.0, 5.0]:
            railgun = create_component('railgun', registries=setup_registries)
            if mass_mult > 1.0:
                railgun.add_modifier('hardened_mount', mass_mult)
            railgun.recalculate_stats()

            expected_mass = base_mass * mass_mult
            expected_hp = base_hp * (mass_mult ** 2)

            assert railgun.mass == pytest.approx(expected_mass, rel=1e-6), \
                f"Mass at {mass_mult}x: {railgun.mass} != {expected_mass}"
            assert railgun.max_hp == pytest.approx(expected_hp, rel=1e-6), \
                f"HP at {mass_mult}x: {railgun.max_hp} != {expected_hp}"

    def test_range_mount_formula(self, setup_registries):
        """Verify range_mount: range = 2^level, mass = 3.5^level"""
        railgun = create_component('railgun', registries=setup_registries)
        base_mass = railgun.base_mass
        weapon = railgun.get_ability('ProjectileWeaponAbility')
        base_range = weapon._base_range if hasattr(weapon, '_base_range') else weapon.range

        for level in [0, 1, 2, 3]:
            railgun = create_component('railgun', registries=setup_registries)
            if level > 0:
                railgun.add_modifier('range_mount', level)
            railgun.recalculate_stats()

            weapon = railgun.get_ability('ProjectileWeaponAbility')
            expected_range_mult = 2.0 ** level
            expected_mass_mult = 3.5 ** level

            expected_range = base_range * expected_range_mult
            expected_mass = base_mass * expected_mass_mult

            assert weapon.range == pytest.approx(expected_range, rel=1e-6), \
                f"Range at level {level}: {weapon.range} != {expected_range}"
            assert railgun.mass == pytest.approx(expected_mass, rel=1e-6), \
                f"Mass at level {level}: {railgun.mass} != {expected_mass}"

    def test_turret_mount_formula(self, setup_registries):
        """Verify turret_mount: mass_mult = 1.0 + 0.514 * ln(1 + arc/30)"""
        railgun = create_component('railgun', registries=setup_registries)
        base_mass = railgun.base_mass

        for arc in [0, 30, 45, 90, 180]:
            railgun = create_component('railgun', registries=setup_registries)
            if arc > 0:
                railgun.add_modifier('turret_mount', arc)
            railgun.recalculate_stats()

            if arc > 0:
                expected_mult = 1.0 + 0.514 * math.log(1.0 + arc / 30.0)
            else:
                expected_mult = 1.0
            expected_mass = base_mass * expected_mult

            assert railgun.mass == pytest.approx(expected_mass, rel=1e-6), \
                f"Mass at arc {arc}: {railgun.mass} != {expected_mass}"

            weapon = railgun.get_ability('ProjectileWeaponAbility')
            if arc > 0:
                assert weapon.firing_arc == pytest.approx(float(arc), rel=1e-6), \
                    f"Arc at {arc}: {weapon.firing_arc} != {arc}"

    def test_rapid_fire_formula(self, setup_registries):
        """Verify rapid_fire: reload = 1/rate, mass += (rate-1)*2"""
        railgun = create_component('railgun', registries=setup_registries)
        base_mass = railgun.base_mass
        weapon = railgun.get_ability('ProjectileWeaponAbility')
        base_reload = weapon._base_reload if hasattr(weapon, '_base_reload') else weapon.reload_time

        for rate in [1.0, 2.0, 3.0, 5.0]:
            railgun = create_component('railgun', registries=setup_registries)
            if rate > 1.0:
                railgun.add_modifier('rapid_fire', rate)
            railgun.recalculate_stats()

            weapon = railgun.get_ability('ProjectileWeaponAbility')
            expected_reload = base_reload * (1.0 / rate)
            # Note: mass_mult ADDS (rate-1)*2, not multiplies
            expected_mass = base_mass * (1.0 + (rate - 1.0) * 2.0)

            assert weapon.reload_time == pytest.approx(expected_reload, rel=1e-6), \
                f"Reload at rate {rate}: {weapon.reload_time} != {expected_reload}"
            assert railgun.mass == pytest.approx(expected_mass, rel=1e-6), \
                f"Mass at rate {rate}: {railgun.mass} != {expected_mass}"
