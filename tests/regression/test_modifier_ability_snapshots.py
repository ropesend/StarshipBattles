"""
Regression tests for modifier-ability system.

These tests capture the current behavior of the modifier system BEFORE any refactoring.
They serve as a baseline to ensure the refactored system produces identical results.

Agent Instructions:
- Run these tests BEFORE making any changes to verify they pass
- Run these tests AFTER each phase to verify no regressions
- If a test fails after refactoring, the refactored code has a bug that must be fixed
"""
import pytest
import json
import os
import math
from typing import Dict, Any, List, Optional
from pathlib import Path

# Ensure proper imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from game.simulation.components.component import (
    Component, load_components, load_modifiers, create_component,
    reset_component_caches
)
from game.core.registry import RegistryManager


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def snapshot_component_stats(component: Component) -> Dict[str, Any]:
    """
    Capture all stats from a component for regression comparison.

    Returns a dictionary with:
    - Component-level stats (mass, hp, cost, etc.)
    - All modifier values applied
    - The stats dictionary
    """
    return {
        'id': component.id,
        'name': component.name,
        'mass': component.mass,
        'base_mass': component.base_mass,
        'max_hp': component.max_hp,
        'base_max_hp': component.base_max_hp,
        'cost': getattr(component, 'cost', 0),
        'type_str': component.type_str,
        'stats': dict(component.stats) if component.stats else {},
        'modifiers': [
            {'id': m.definition.id, 'value': m.value}
            for m in component.modifiers
        ],
    }


def snapshot_ability_stats(ability) -> Dict[str, Any]:
    """
    Capture all stats from an ability for regression comparison.

    Handles different ability types by capturing their specific attributes.
    """
    snapshot = {
        'class_name': ability.__class__.__name__,
        'tags': list(ability.tags) if hasattr(ability, 'tags') else [],
    }

    # Weapon abilities
    if hasattr(ability, 'damage'):
        snapshot['damage'] = ability.damage
    if hasattr(ability, '_base_damage'):
        snapshot['base_damage'] = ability._base_damage
    if hasattr(ability, 'range'):
        snapshot['range'] = ability.range
    if hasattr(ability, '_base_range'):
        snapshot['base_range'] = ability._base_range
    if hasattr(ability, 'reload_time'):
        snapshot['reload_time'] = ability.reload_time
    if hasattr(ability, '_base_reload'):
        snapshot['base_reload'] = ability._base_reload
    if hasattr(ability, 'firing_arc'):
        snapshot['firing_arc'] = ability.firing_arc
    if hasattr(ability, '_base_firing_arc'):
        snapshot['base_firing_arc'] = ability._base_firing_arc
    if hasattr(ability, 'base_accuracy'):
        snapshot['base_accuracy'] = ability.base_accuracy
    if hasattr(ability, '_base_accuracy'):
        snapshot['_base_accuracy'] = ability._base_accuracy

    # Seeker/Projectile abilities
    if hasattr(ability, 'projectile_damage'):
        snapshot['projectile_damage'] = ability.projectile_damage
    if hasattr(ability, 'projectile_hp'):
        snapshot['projectile_hp'] = ability.projectile_hp
    if hasattr(ability, 'endurance'):
        snapshot['endurance'] = ability.endurance
    if hasattr(ability, '_base_endurance'):
        snapshot['base_endurance'] = ability._base_endurance

    # Propulsion abilities
    if hasattr(ability, 'thrust_force'):
        snapshot['thrust_force'] = ability.thrust_force
    if hasattr(ability, 'base_thrust'):
        snapshot['base_thrust'] = ability.base_thrust
    if hasattr(ability, 'turn_rate'):
        snapshot['turn_rate'] = ability.turn_rate
    if hasattr(ability, 'base_turn_rate'):
        snapshot['base_turn_rate'] = ability.base_turn_rate
    if hasattr(ability, 'movement_points'):
        snapshot['movement_points'] = ability.movement_points
    if hasattr(ability, 'base_movement_points'):
        snapshot['base_movement_points'] = ability.base_movement_points

    # Defense abilities
    if hasattr(ability, 'capacity'):
        snapshot['capacity'] = ability.capacity
    if hasattr(ability, 'base_capacity'):
        snapshot['base_capacity'] = ability.base_capacity
    if hasattr(ability, 'rate'):
        snapshot['rate'] = ability.rate
    if hasattr(ability, 'base_rate'):
        snapshot['base_rate'] = ability.base_rate

    # Crew abilities
    if hasattr(ability, 'amount'):
        snapshot['amount'] = ability.amount
    if hasattr(ability, '_base_amount'):
        snapshot['base_amount'] = ability._base_amount

    # Resource abilities
    if hasattr(ability, 'max_amount'):
        snapshot['max_amount'] = ability.max_amount

    return snapshot


def snapshot_full_component(component: Component) -> Dict[str, Any]:
    """
    Capture complete snapshot of a component including all abilities.
    """
    return {
        'component': snapshot_component_stats(component),
        'abilities': [
            snapshot_ability_stats(ab) for ab in component.ability_instances
        ]
    }


def compare_snapshots(actual: Dict, expected: Dict, tolerance: float = 1e-6) -> List[str]:
    """
    Compare two snapshots and return list of differences.

    Returns empty list if snapshots match, otherwise returns list of difference descriptions.
    """
    differences = []

    def compare_values(path: str, actual_val, expected_val):
        if isinstance(expected_val, dict):
            if not isinstance(actual_val, dict):
                differences.append(f"{path}: expected dict, got {type(actual_val).__name__}")
                return
            for key in expected_val:
                if key not in actual_val:
                    differences.append(f"{path}.{key}: missing in actual")
                else:
                    compare_values(f"{path}.{key}", actual_val[key], expected_val[key])
        elif isinstance(expected_val, list):
            if not isinstance(actual_val, list):
                differences.append(f"{path}: expected list, got {type(actual_val).__name__}")
                return
            if len(actual_val) != len(expected_val):
                differences.append(f"{path}: length mismatch (actual={len(actual_val)}, expected={len(expected_val)})")
            for i, (a, e) in enumerate(zip(actual_val, expected_val)):
                compare_values(f"{path}[{i}]", a, e)
        elif isinstance(expected_val, float):
            if not isinstance(actual_val, (int, float)):
                differences.append(f"{path}: expected number, got {type(actual_val).__name__}")
            elif abs(actual_val - expected_val) > tolerance:
                differences.append(f"{path}: {actual_val} != {expected_val} (diff={actual_val - expected_val})")
        elif actual_val != expected_val:
            differences.append(f"{path}: {actual_val} != {expected_val}")

    compare_values("root", actual, expected)
    return differences


def load_snapshot(name: str) -> Optional[Dict]:
    """Load a snapshot from the snapshots directory."""
    snapshot_dir = Path(__file__).parent / "snapshots"
    snapshot_path = snapshot_dir / f"{name}.json"
    if snapshot_path.exists():
        with open(snapshot_path, 'r') as f:
            return json.load(f)
    return None


def save_snapshot(name: str, data: Dict):
    """Save a snapshot to the snapshots directory."""
    snapshot_dir = Path(__file__).parent / "snapshots"
    snapshot_dir.mkdir(exist_ok=True)
    snapshot_path = snapshot_dir / f"{name}.json"
    with open(snapshot_path, 'w') as f:
        json.dump(data, f, indent=2)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture(scope="module")
def setup_registries():
    """Load components and modifiers into registries."""
    reset_component_caches()
    load_modifiers("data/modifiers.json")
    load_components("data/components.json")
    yield
    reset_component_caches()


# =============================================================================
# REGRESSION TESTS - WEAPON MODIFIERS
# =============================================================================

class TestWeaponModifierRegression:
    """Regression tests for weapon-related modifiers."""

    def test_railgun_no_modifiers(self, setup_registries):
        """Baseline: Railgun with no modifiers."""
        railgun = create_component('railgun')
        railgun.recalculate_stats()

        snapshot = snapshot_full_component(railgun)
        expected = load_snapshot('railgun_no_modifiers')

        if expected is None:
            # First run - save baseline
            save_snapshot('railgun_no_modifiers', snapshot)
            pytest.skip("Baseline snapshot created - re-run test")

        diffs = compare_snapshots(snapshot, expected)
        assert not diffs, f"Regression detected:\n" + "\n".join(diffs)

    @pytest.mark.parametrize("level", [0, 1, 2, 3])
    def test_railgun_range_mount(self, setup_registries, level):
        """Railgun with range_mount at different levels."""
        railgun = create_component('railgun')
        if level > 0:
            railgun.add_modifier('range_mount', level)
        railgun.recalculate_stats()

        snapshot = snapshot_full_component(railgun)
        snapshot_name = f'railgun_range_mount_level_{level}'
        expected = load_snapshot(snapshot_name)

        if expected is None:
            save_snapshot(snapshot_name, snapshot)
            pytest.skip(f"Baseline snapshot '{snapshot_name}' created - re-run test")

        diffs = compare_snapshots(snapshot, expected)
        assert not diffs, f"Regression detected:\n" + "\n".join(diffs)

    @pytest.mark.parametrize("rate", [1.0, 1.5, 2.0, 3.0, 5.0])
    def test_railgun_rapid_fire(self, setup_registries, rate):
        """Railgun with rapid_fire at different rates."""
        railgun = create_component('railgun')
        if rate > 1.0:
            railgun.add_modifier('rapid_fire', rate)
        railgun.recalculate_stats()

        snapshot = snapshot_full_component(railgun)
        snapshot_name = f'railgun_rapid_fire_{rate:.1f}'
        expected = load_snapshot(snapshot_name)

        if expected is None:
            save_snapshot(snapshot_name, snapshot)
            pytest.skip(f"Baseline snapshot '{snapshot_name}' created - re-run test")

        diffs = compare_snapshots(snapshot, expected)
        assert not diffs, f"Regression detected:\n" + "\n".join(diffs)

    @pytest.mark.parametrize("mass_mult", [1.0, 2.0, 3.0, 5.0])
    def test_railgun_hardened_mount(self, setup_registries, mass_mult):
        """Railgun with hardened_mount at different mass multipliers."""
        railgun = create_component('railgun')
        if mass_mult > 1.0:
            railgun.add_modifier('hardened_mount', mass_mult)
        railgun.recalculate_stats()

        snapshot = snapshot_full_component(railgun)
        snapshot_name = f'railgun_hardened_{mass_mult:.1f}'
        expected = load_snapshot(snapshot_name)

        if expected is None:
            save_snapshot(snapshot_name, snapshot)
            pytest.skip(f"Baseline snapshot '{snapshot_name}' created - re-run test")

        diffs = compare_snapshots(snapshot, expected)
        assert not diffs, f"Regression detected:\n" + "\n".join(diffs)

    @pytest.mark.parametrize("arc", [0, 45, 90, 180])
    def test_railgun_turret_mount(self, setup_registries, arc):
        """Railgun with turret_mount at different arcs."""
        railgun = create_component('railgun')
        if arc > 0:
            railgun.add_modifier('turret_mount', arc)
        railgun.recalculate_stats()

        snapshot = snapshot_full_component(railgun)
        snapshot_name = f'railgun_turret_{arc}'
        expected = load_snapshot(snapshot_name)

        if expected is None:
            save_snapshot(snapshot_name, snapshot)
            pytest.skip(f"Baseline snapshot '{snapshot_name}' created - re-run test")

        diffs = compare_snapshots(snapshot, expected)
        assert not diffs, f"Regression detected:\n" + "\n".join(diffs)

    def test_railgun_combined_modifiers(self, setup_registries):
        """Railgun with multiple modifiers combined."""
        railgun = create_component('railgun')
        railgun.add_modifier('range_mount', 2)
        railgun.add_modifier('rapid_fire', 2.0)
        railgun.add_modifier('hardened_mount', 2.0)
        railgun.recalculate_stats()

        snapshot = snapshot_full_component(railgun)
        expected = load_snapshot('railgun_combined')

        if expected is None:
            save_snapshot('railgun_combined', snapshot)
            pytest.skip("Baseline snapshot created - re-run test")

        diffs = compare_snapshots(snapshot, expected)
        assert not diffs, f"Regression detected:\n" + "\n".join(diffs)


class TestLaserCannonModifierRegression:
    """Regression tests for beam weapon modifiers (laser_cannon)."""

    def test_laser_cannon_no_modifiers(self, setup_registries):
        """Baseline: Laser cannon with no modifiers."""
        laser = create_component('laser_cannon')
        laser.recalculate_stats()

        snapshot = snapshot_full_component(laser)
        expected = load_snapshot('laser_cannon_no_modifiers')

        if expected is None:
            save_snapshot('laser_cannon_no_modifiers', snapshot)
            pytest.skip("Baseline snapshot created - re-run test")

        diffs = compare_snapshots(snapshot, expected)
        assert not diffs, f"Regression detected:\n" + "\n".join(diffs)

    @pytest.mark.parametrize("level", [0, 1, 2, 3, 5])
    def test_laser_cannon_precision_mount(self, setup_registries, level):
        """Laser cannon with precision_mount at different levels."""
        laser = create_component('laser_cannon')
        if level > 0:
            laser.add_modifier('precision_mount', level)
        laser.recalculate_stats()

        snapshot = snapshot_full_component(laser)
        snapshot_name = f'laser_cannon_precision_level_{level}'
        expected = load_snapshot(snapshot_name)

        if expected is None:
            save_snapshot(snapshot_name, snapshot)
            pytest.skip(f"Baseline snapshot '{snapshot_name}' created - re-run test")

        diffs = compare_snapshots(snapshot, expected)
        assert not diffs, f"Regression detected:\n" + "\n".join(diffs)


class TestSeekerModifierRegression:
    """Regression tests for seeker/missile modifiers."""

    def test_capital_missile_no_modifiers(self, setup_registries):
        """Baseline: Capital missile with no modifiers."""
        missile = create_component('capital_missile')
        missile.recalculate_stats()

        snapshot = snapshot_full_component(missile)
        expected = load_snapshot('capital_missile_no_modifiers')

        if expected is None:
            save_snapshot('capital_missile_no_modifiers', snapshot)
            pytest.skip("Baseline snapshot created - re-run test")

        diffs = compare_snapshots(snapshot, expected)
        assert not diffs, f"Regression detected:\n" + "\n".join(diffs)

    @pytest.mark.parametrize("mult", [1.0, 2.0, 5.0, 10.0])
    def test_capital_missile_seeker_endurance(self, setup_registries, mult):
        """Capital missile with seeker_endurance at different multipliers."""
        missile = create_component('capital_missile')
        if mult > 1.0:
            missile.add_modifier('seeker_endurance', mult)
        missile.recalculate_stats()

        snapshot = snapshot_full_component(missile)
        snapshot_name = f'capital_missile_endurance_{mult:.1f}'
        expected = load_snapshot(snapshot_name)

        if expected is None:
            save_snapshot(snapshot_name, snapshot)
            pytest.skip(f"Baseline snapshot '{snapshot_name}' created - re-run test")

        diffs = compare_snapshots(snapshot, expected)
        assert not diffs, f"Regression detected:\n" + "\n".join(diffs)

    @pytest.mark.parametrize("mult", [1.0, 2.0, 10.0, 100.0])
    def test_capital_missile_seeker_damage(self, setup_registries, mult):
        """Capital missile with seeker_damage at different multipliers."""
        missile = create_component('capital_missile')
        if mult > 1.0:
            missile.add_modifier('seeker_damage', mult)
        missile.recalculate_stats()

        snapshot = snapshot_full_component(missile)
        snapshot_name = f'capital_missile_damage_{mult:.1f}'
        expected = load_snapshot(snapshot_name)

        if expected is None:
            save_snapshot(snapshot_name, snapshot)
            pytest.skip(f"Baseline snapshot '{snapshot_name}' created - re-run test")

        diffs = compare_snapshots(snapshot, expected)
        assert not diffs, f"Regression detected:\n" + "\n".join(diffs)

    @pytest.mark.parametrize("mult", [1.0, 2.0, 10.0, 100.0])
    def test_capital_missile_seeker_armored(self, setup_registries, mult):
        """Capital missile with seeker_armored at different multipliers."""
        missile = create_component('capital_missile')
        if mult > 1.0:
            missile.add_modifier('seeker_armored', mult)
        missile.recalculate_stats()

        snapshot = snapshot_full_component(missile)
        snapshot_name = f'capital_missile_armored_{mult:.1f}'
        expected = load_snapshot(snapshot_name)

        if expected is None:
            save_snapshot(snapshot_name, snapshot)
            pytest.skip(f"Baseline snapshot '{snapshot_name}' created - re-run test")

        diffs = compare_snapshots(snapshot, expected)
        assert not diffs, f"Regression detected:\n" + "\n".join(diffs)

    @pytest.mark.parametrize("level", [0, 1, 3, 5, 10])
    def test_capital_missile_seeker_stealth(self, setup_registries, level):
        """Capital missile with seeker_stealth at different levels."""
        missile = create_component('capital_missile')
        if level > 0:
            missile.add_modifier('seeker_stealth', level)
        missile.recalculate_stats()

        snapshot = snapshot_full_component(missile)
        snapshot_name = f'capital_missile_stealth_{level}'
        expected = load_snapshot(snapshot_name)

        if expected is None:
            save_snapshot(snapshot_name, snapshot)
            pytest.skip(f"Baseline snapshot '{snapshot_name}' created - re-run test")

        diffs = compare_snapshots(snapshot, expected)
        assert not diffs, f"Regression detected:\n" + "\n".join(diffs)


# =============================================================================
# REGRESSION TESTS - PROPULSION MODIFIERS
# =============================================================================

class TestPropulsionModifierRegression:
    """Regression tests for propulsion modifiers."""

    def test_standard_engine_no_modifiers(self, setup_registries):
        """Baseline: Standard engine with no modifiers."""
        engine = create_component('standard_engine')
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
        engine = create_component('standard_engine')
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
        thruster = create_component('thruster')
        thruster.recalculate_stats()

        snapshot = snapshot_full_component(thruster)
        expected = load_snapshot('thruster_no_modifiers')

        if expected is None:
            save_snapshot('thruster_no_modifiers', snapshot)
            pytest.skip("Baseline snapshot created - re-run test")

        diffs = compare_snapshots(snapshot, expected)
        assert not diffs, f"Regression detected:\n" + "\n".join(diffs)


# =============================================================================
# REGRESSION TESTS - UTILITY MODIFIERS
# =============================================================================

class TestFacingModifierRegression:
    """Regression tests for facing modifier."""

    def test_railgun_no_facing(self, setup_registries):
        """Baseline: Railgun with no facing modifier (default forward)."""
        railgun = create_component('railgun')
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
        railgun = create_component('railgun')
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
        laser = create_component('laser_cannon')
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
        quarters = create_component('crew_quarters')
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
        generator = create_component('generator')
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


# =============================================================================
# COMPREHENSIVE FORMULA VERIFICATION
# =============================================================================

class TestModifierFormulaVerification:
    """
    Direct verification of modifier formulas.
    These tests verify the mathematical correctness of each handler.
    """

    def test_hardened_mount_formula(self, setup_registries):
        """Verify hardened_mount: HP = mass^2"""
        railgun = create_component('railgun')
        base_mass = railgun.base_mass
        base_hp = railgun.base_max_hp

        for mass_mult in [1.0, 2.0, 3.0, 5.0]:
            railgun = create_component('railgun')
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
        railgun = create_component('railgun')
        base_mass = railgun.base_mass
        weapon = railgun.get_ability('ProjectileWeaponAbility')
        base_range = weapon._base_range if hasattr(weapon, '_base_range') else weapon.range

        for level in [0, 1, 2, 3]:
            railgun = create_component('railgun')
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
        railgun = create_component('railgun')
        base_mass = railgun.base_mass

        for arc in [0, 30, 45, 90, 180]:
            railgun = create_component('railgun')
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
        railgun = create_component('railgun')
        base_mass = railgun.base_mass
        weapon = railgun.get_ability('ProjectileWeaponAbility')
        base_reload = weapon._base_reload if hasattr(weapon, '_base_reload') else weapon.reload_time

        for rate in [1.0, 2.0, 3.0, 5.0]:
            railgun = create_component('railgun')
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


# =============================================================================
# UTILITY: Generate All Snapshots
# =============================================================================

def generate_all_snapshots():
    """
    Utility function to generate all baseline snapshots.
    Run this once before refactoring to capture current behavior.

    Usage: python -c "from tests.regression.test_modifier_ability_snapshots import generate_all_snapshots; generate_all_snapshots()"
    """
    reset_component_caches()
    load_modifiers("data/modifiers.json")
    load_components("data/components.json")

    print("Generating baseline snapshots...")

    # Railgun tests
    for level in [0, 1, 2, 3]:
        railgun = create_component('railgun')
        if level > 0:
            railgun.add_modifier('range_mount', level)
        railgun.recalculate_stats()
        save_snapshot(f'railgun_range_mount_level_{level}', snapshot_full_component(railgun))
        print(f"  Created: railgun_range_mount_level_{level}")

    for rate in [1.0, 1.5, 2.0, 3.0, 5.0]:
        railgun = create_component('railgun')
        if rate > 1.0:
            railgun.add_modifier('rapid_fire', rate)
        railgun.recalculate_stats()
        save_snapshot(f'railgun_rapid_fire_{rate:.1f}', snapshot_full_component(railgun))
        print(f"  Created: railgun_rapid_fire_{rate:.1f}")

    for mass_mult in [1.0, 2.0, 3.0, 5.0]:
        railgun = create_component('railgun')
        if mass_mult > 1.0:
            railgun.add_modifier('hardened_mount', mass_mult)
        railgun.recalculate_stats()
        save_snapshot(f'railgun_hardened_{mass_mult:.1f}', snapshot_full_component(railgun))
        print(f"  Created: railgun_hardened_{mass_mult:.1f}")

    for arc in [0, 45, 90, 180]:
        railgun = create_component('railgun')
        if arc > 0:
            railgun.add_modifier('turret_mount', arc)
        railgun.recalculate_stats()
        save_snapshot(f'railgun_turret_{arc}', snapshot_full_component(railgun))
        print(f"  Created: railgun_turret_{arc}")

    # Combined
    railgun = create_component('railgun')
    railgun.add_modifier('range_mount', 2)
    railgun.add_modifier('rapid_fire', 2.0)
    railgun.add_modifier('hardened_mount', 2.0)
    railgun.recalculate_stats()
    save_snapshot('railgun_combined', snapshot_full_component(railgun))
    print("  Created: railgun_combined")

    # No modifier baseline
    railgun = create_component('railgun')
    railgun.recalculate_stats()
    save_snapshot('railgun_no_modifiers', snapshot_full_component(railgun))
    print("  Created: railgun_no_modifiers")

    # Laser cannon
    laser = create_component('laser_cannon')
    laser.recalculate_stats()
    save_snapshot('laser_cannon_no_modifiers', snapshot_full_component(laser))
    print("  Created: laser_cannon_no_modifiers")

    for level in [0, 1, 2, 3, 5]:
        laser = create_component('laser_cannon')
        if level > 0:
            laser.add_modifier('precision_mount', level)
        laser.recalculate_stats()
        save_snapshot(f'laser_cannon_precision_level_{level}', snapshot_full_component(laser))
        print(f"  Created: laser_cannon_precision_level_{level}")

    # Capital missile
    missile = create_component('capital_missile')
    missile.recalculate_stats()
    save_snapshot('capital_missile_no_modifiers', snapshot_full_component(missile))
    print("  Created: capital_missile_no_modifiers")

    for mult in [1.0, 2.0, 5.0, 10.0]:
        missile = create_component('capital_missile')
        if mult > 1.0:
            missile.add_modifier('seeker_endurance', mult)
        missile.recalculate_stats()
        save_snapshot(f'capital_missile_endurance_{mult:.1f}', snapshot_full_component(missile))
        print(f"  Created: capital_missile_endurance_{mult:.1f}")

    for mult in [1.0, 2.0, 10.0, 100.0]:
        missile = create_component('capital_missile')
        if mult > 1.0:
            missile.add_modifier('seeker_damage', mult)
        missile.recalculate_stats()
        save_snapshot(f'capital_missile_damage_{mult:.1f}', snapshot_full_component(missile))
        print(f"  Created: capital_missile_damage_{mult:.1f}")

    for mult in [1.0, 2.0, 10.0, 100.0]:
        missile = create_component('capital_missile')
        if mult > 1.0:
            missile.add_modifier('seeker_armored', mult)
        missile.recalculate_stats()
        save_snapshot(f'capital_missile_armored_{mult:.1f}', snapshot_full_component(missile))
        print(f"  Created: capital_missile_armored_{mult:.1f}")

    for level in [0, 1, 3, 5, 10]:
        missile = create_component('capital_missile')
        if level > 0:
            missile.add_modifier('seeker_stealth', level)
        missile.recalculate_stats()
        save_snapshot(f'capital_missile_stealth_{level}', snapshot_full_component(missile))
        print(f"  Created: capital_missile_stealth_{level}")

    # Propulsion
    engine = create_component('standard_engine')
    engine.recalculate_stats()
    save_snapshot('standard_engine_no_modifiers', snapshot_full_component(engine))
    print("  Created: standard_engine_no_modifiers")

    for scale in [1, 2, 4, 8, 16]:
        engine = create_component('standard_engine')
        if scale > 1:
            engine.add_modifier('simple_size_mount', scale)
        engine.recalculate_stats()
        save_snapshot(f'standard_engine_size_{scale}', snapshot_full_component(engine))
        print(f"  Created: standard_engine_size_{scale}")

    thruster = create_component('thruster')
    thruster.recalculate_stats()
    save_snapshot('thruster_no_modifiers', snapshot_full_component(thruster))
    print("  Created: thruster_no_modifiers")

    # Utility
    for reduction in [0.0, 0.25, 0.5, 0.75, 0.99]:
        quarters = create_component('crew_quarters')
        if reduction > 0.0:
            quarters.add_modifier('automation', reduction)
        quarters.recalculate_stats()
        save_snapshot(f'crew_quarters_automation_{reduction:.2f}', snapshot_full_component(quarters))
        print(f"  Created: crew_quarters_automation_{reduction:.2f}")

    for resource_mult in [1.0, 0.5, 0.25, 0.1]:
        generator = create_component('generator')
        if resource_mult < 1.0:
            generator.add_modifier('efficiency_mount', resource_mult)
        generator.recalculate_stats()
        save_snapshot(f'generator_efficiency_{resource_mult:.2f}', snapshot_full_component(generator))
        print(f"  Created: generator_efficiency_{resource_mult:.2f}")

    # Facing modifier tests
    for angle in [0, 45, 90, 180, 270]:
        railgun = create_component('railgun')
        if angle > 0:
            railgun.add_modifier('facing', angle)
        railgun.recalculate_stats()
        save_snapshot(f'railgun_facing_{angle}', snapshot_full_component(railgun))
        print(f"  Created: railgun_facing_{angle}")

    laser = create_component('laser_cannon')
    laser.add_modifier('facing', 90)
    laser.recalculate_stats()
    save_snapshot('laser_cannon_facing_90', snapshot_full_component(laser))
    print("  Created: laser_cannon_facing_90")

    print(f"\nAll snapshots saved to: {Path(__file__).parent / 'snapshots'}")


if __name__ == "__main__":
    generate_all_snapshots()
