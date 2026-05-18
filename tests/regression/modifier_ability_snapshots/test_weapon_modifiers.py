"""
Regression tests for weapon-related modifiers (railgun, laser, missiles).

Agent Instructions:
- Run these tests BEFORE making any changes to verify they pass
- Run these tests AFTER each phase to verify no regressions
- If a test fails after refactoring, the refactored code has a bug that must be fixed
"""
import pytest

from game.simulation.components.component import create_component

from .conftest import (
    snapshot_full_component, compare_snapshots, load_snapshot, fail_missing_baseline
)


class TestWeaponModifierRegression:
    """Regression tests for weapon-related modifiers."""

    def test_railgun_no_modifiers(self, setup_registries):
        """Baseline: Railgun with no modifiers."""
        railgun = create_component('railgun', registries=setup_registries)
        railgun.recalculate_stats()

        snapshot = snapshot_full_component(railgun)
        expected = load_snapshot('railgun_no_modifiers')

        if expected is None:
            fail_missing_baseline('railgun_no_modifiers', snapshot)

        diffs = compare_snapshots(snapshot, expected)
        assert not diffs, f"Regression detected:\n" + "\n".join(diffs)

    @pytest.mark.parametrize("level", [0, 1, 2, 3])
    def test_railgun_range_mount(self, setup_registries, level):
        """Railgun with range_mount at different levels."""
        railgun = create_component('railgun', registries=setup_registries)
        if level > 0:
            railgun.add_modifier('range_mount', level)
        railgun.recalculate_stats()

        snapshot = snapshot_full_component(railgun)
        snapshot_name = f'railgun_range_mount_level_{level}'
        expected = load_snapshot(snapshot_name)

        if expected is None:
            fail_missing_baseline(snapshot_name, snapshot)

        diffs = compare_snapshots(snapshot, expected)
        assert not diffs, f"Regression detected:\n" + "\n".join(diffs)

    @pytest.mark.parametrize("rate", [1.0, 1.5, 2.0, 3.0, 5.0])
    def test_railgun_rapid_fire(self, setup_registries, rate):
        """Railgun with rapid_fire at different rates."""
        railgun = create_component('railgun', registries=setup_registries)
        if rate > 1.0:
            railgun.add_modifier('rapid_fire', rate)
        railgun.recalculate_stats()

        snapshot = snapshot_full_component(railgun)
        snapshot_name = f'railgun_rapid_fire_{rate:.1f}'
        expected = load_snapshot(snapshot_name)

        if expected is None:
            fail_missing_baseline(snapshot_name, snapshot)

        diffs = compare_snapshots(snapshot, expected)
        assert not diffs, f"Regression detected:\n" + "\n".join(diffs)

    @pytest.mark.parametrize("mass_mult", [1.0, 2.0, 3.0, 5.0])
    def test_railgun_hardened_mount(self, setup_registries, mass_mult):
        """Railgun with hardened_mount at different mass multipliers."""
        railgun = create_component('railgun', registries=setup_registries)
        if mass_mult > 1.0:
            railgun.add_modifier('hardened_mount', mass_mult)
        railgun.recalculate_stats()

        snapshot = snapshot_full_component(railgun)
        snapshot_name = f'railgun_hardened_{mass_mult:.1f}'
        expected = load_snapshot(snapshot_name)

        if expected is None:
            fail_missing_baseline(snapshot_name, snapshot)

        diffs = compare_snapshots(snapshot, expected)
        assert not diffs, f"Regression detected:\n" + "\n".join(diffs)

    @pytest.mark.parametrize("arc", [0, 45, 90, 180])
    def test_railgun_turret_mount(self, setup_registries, arc):
        """Railgun with turret_mount at different arcs."""
        railgun = create_component('railgun', registries=setup_registries)
        if arc > 0:
            railgun.add_modifier('turret_mount', arc)
        railgun.recalculate_stats()

        snapshot = snapshot_full_component(railgun)
        snapshot_name = f'railgun_turret_{arc}'
        expected = load_snapshot(snapshot_name)

        if expected is None:
            fail_missing_baseline(snapshot_name, snapshot)

        diffs = compare_snapshots(snapshot, expected)
        assert not diffs, f"Regression detected:\n" + "\n".join(diffs)

    def test_railgun_combined_modifiers(self, setup_registries):
        """Railgun with multiple modifiers combined."""
        railgun = create_component('railgun', registries=setup_registries)
        railgun.add_modifier('range_mount', 2)
        railgun.add_modifier('rapid_fire', 2.0)
        railgun.add_modifier('hardened_mount', 2.0)
        railgun.recalculate_stats()

        snapshot = snapshot_full_component(railgun)
        expected = load_snapshot('railgun_combined')

        if expected is None:
            fail_missing_baseline('railgun_combined', snapshot)

        diffs = compare_snapshots(snapshot, expected)
        assert not diffs, f"Regression detected:\n" + "\n".join(diffs)


class TestLaserCannonModifierRegression:
    """Regression tests for beam weapon modifiers (laser_cannon)."""

    def test_laser_cannon_no_modifiers(self, setup_registries):
        """Baseline: Laser cannon with no modifiers."""
        laser = create_component('laser_cannon', registries=setup_registries)
        laser.recalculate_stats()

        snapshot = snapshot_full_component(laser)
        expected = load_snapshot('laser_cannon_no_modifiers')

        if expected is None:
            fail_missing_baseline('laser_cannon_no_modifiers', snapshot)

        diffs = compare_snapshots(snapshot, expected)
        assert not diffs, f"Regression detected:\n" + "\n".join(diffs)

    @pytest.mark.parametrize("level", [0, 1, 2, 3, 5])
    def test_laser_cannon_precision_mount(self, setup_registries, level):
        """Laser cannon with precision_mount at different levels."""
        laser = create_component('laser_cannon', registries=setup_registries)
        if level > 0:
            laser.add_modifier('precision_mount', level)
        laser.recalculate_stats()

        snapshot = snapshot_full_component(laser)
        snapshot_name = f'laser_cannon_precision_level_{level}'
        expected = load_snapshot(snapshot_name)

        if expected is None:
            fail_missing_baseline(snapshot_name, snapshot)

        diffs = compare_snapshots(snapshot, expected)
        assert not diffs, f"Regression detected:\n" + "\n".join(diffs)


class TestSeekerModifierRegression:
    """Regression tests for seeker/missile modifiers."""

    def test_capital_missile_no_modifiers(self, setup_registries):
        """Baseline: Capital missile with no modifiers."""
        missile = create_component('capital_missile', registries=setup_registries)
        missile.recalculate_stats()

        snapshot = snapshot_full_component(missile)
        expected = load_snapshot('capital_missile_no_modifiers')

        if expected is None:
            fail_missing_baseline('capital_missile_no_modifiers', snapshot)

        diffs = compare_snapshots(snapshot, expected)
        assert not diffs, f"Regression detected:\n" + "\n".join(diffs)

    @pytest.mark.parametrize("mult", [1.0, 2.0, 5.0, 10.0])
    def test_capital_missile_seeker_endurance(self, setup_registries, mult):
        """Capital missile with seeker_endurance at different multipliers."""
        missile = create_component('capital_missile', registries=setup_registries)
        if mult > 1.0:
            missile.add_modifier('seeker_endurance', mult)
        missile.recalculate_stats()

        snapshot = snapshot_full_component(missile)
        snapshot_name = f'capital_missile_endurance_{mult:.1f}'
        expected = load_snapshot(snapshot_name)

        if expected is None:
            fail_missing_baseline(snapshot_name, snapshot)

        diffs = compare_snapshots(snapshot, expected)
        assert not diffs, f"Regression detected:\n" + "\n".join(diffs)

    @pytest.mark.parametrize("mult", [1.0, 2.0, 10.0, 100.0])
    def test_capital_missile_seeker_damage(self, setup_registries, mult):
        """Capital missile with seeker_damage at different multipliers."""
        missile = create_component('capital_missile', registries=setup_registries)
        if mult > 1.0:
            missile.add_modifier('seeker_damage', mult)
        missile.recalculate_stats()

        snapshot = snapshot_full_component(missile)
        snapshot_name = f'capital_missile_damage_{mult:.1f}'
        expected = load_snapshot(snapshot_name)

        if expected is None:
            fail_missing_baseline(snapshot_name, snapshot)

        diffs = compare_snapshots(snapshot, expected)
        assert not diffs, f"Regression detected:\n" + "\n".join(diffs)

    @pytest.mark.parametrize("mult", [1.0, 2.0, 10.0, 100.0])
    def test_capital_missile_seeker_armored(self, setup_registries, mult):
        """Capital missile with seeker_armored at different multipliers."""
        missile = create_component('capital_missile', registries=setup_registries)
        if mult > 1.0:
            missile.add_modifier('seeker_armored', mult)
        missile.recalculate_stats()

        snapshot = snapshot_full_component(missile)
        snapshot_name = f'capital_missile_armored_{mult:.1f}'
        expected = load_snapshot(snapshot_name)

        if expected is None:
            fail_missing_baseline(snapshot_name, snapshot)

        diffs = compare_snapshots(snapshot, expected)
        assert not diffs, f"Regression detected:\n" + "\n".join(diffs)

    @pytest.mark.parametrize("level", [0, 1, 3, 5, 10])
    def test_capital_missile_seeker_stealth(self, setup_registries, level):
        """Capital missile with seeker_stealth at different levels."""
        missile = create_component('capital_missile', registries=setup_registries)
        if level > 0:
            missile.add_modifier('seeker_stealth', level)
        missile.recalculate_stats()

        snapshot = snapshot_full_component(missile)
        snapshot_name = f'capital_missile_stealth_{level}'
        expected = load_snapshot(snapshot_name)

        if expected is None:
            fail_missing_baseline(snapshot_name, snapshot)

        diffs = compare_snapshots(snapshot, expected)
        assert not diffs, f"Regression detected:\n" + "\n".join(diffs)
