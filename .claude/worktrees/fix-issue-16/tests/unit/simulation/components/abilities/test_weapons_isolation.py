"""
Isolation unit tests for weapon ability classes.

PROJ-118: Phase 2 - Foundation test coverage

These tests verify weapon ability behavior in isolation using mocks,
focusing on:
- Initialization with various data formats
- Damage calculation (static and formula-based)
- Cooldown handling
- Resource consumption
- Firing arc and range checks
- Stat modifier application
- Edge cases and boundary conditions
"""

import math
import pytest
from unittest.mock import Mock, patch, MagicMock
from pygame import Vector2

from game.simulation.components.abilities.weapons import (
    WeaponAbility,
    ProjectileWeaponAbility,
    BeamWeaponAbility,
    SeekerWeaponAbility,
)
from game.core.config import PhysicsConfig


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_component():
    """Create a mock component with default stats."""
    component = Mock()
    component.stats = {}
    component.ability_stats = {}
    component.data = {}
    component.consume_activation = Mock()
    return component


@pytest.fixture
def mock_component_with_stats():
    """Create a mock component with populated stats for modifier testing."""
    component = Mock()
    component.stats = {
        'damage_mult': 1.5,
        'range_mult': 1.2,
        'reload_mult': 0.8,
    }
    component.ability_stats = {}
    component.data = {}
    component.consume_activation = Mock()
    return component


@pytest.fixture
def basic_weapon_data():
    """Standard weapon data dict."""
    return {
        'damage': 100,
        'range': 1000,
        'reload': 2.0,
        'firing_arc': 90,
        'facing_angle': 0,
    }


@pytest.fixture
def formula_weapon_data():
    """Weapon data with formula-based damage."""
    return {
        'damage': '=50 + range_to_target * 0.1',
        'range': 2000,
        'reload': 1.5,
        'firing_arc': 360,
        'facing_angle': 0,
    }


# =============================================================================
# WeaponAbility Tests
# =============================================================================

class TestWeaponAbilityInitialization:
    """Test WeaponAbility initialization with various data formats."""

    def test_init_with_dict_data(self, mock_component, basic_weapon_data):
        """WeaponAbility initializes correctly with dict data."""
        ability = WeaponAbility(mock_component, basic_weapon_data)

        assert ability.damage == 100.0
        assert ability.range == 1000.0
        assert ability.reload_time == 2.0
        assert ability.firing_arc == 90.0
        assert ability.facing_angle == 0.0
        assert ability.cooldown_timer == 0.0

    def test_init_with_primitive_data_uses_component_data(self, mock_component):
        """WeaponAbility falls back to component.data when data is not a dict."""
        mock_component.data = {
            'damage': 50,
            'range': 500,
            'reload': 1.0,
            'firing_arc': 180,
            'facing_angle': 45,
        }

        ability = WeaponAbility(mock_component, True)

        assert ability.damage == 50.0
        assert ability.range == 500.0
        assert ability.reload_time == 1.0
        assert ability.firing_arc == 180.0
        assert ability.facing_angle == 45.0

    def test_init_with_base_stat_fallbacks(self, mock_component):
        """WeaponAbility uses base_damage/base_range when damage/range missing."""
        mock_component.data = {
            'base_damage': 75,
            'base_range': 750,
        }

        ability = WeaponAbility(mock_component, True)

        assert ability.damage == 75.0
        assert ability.range == 750.0

    def test_init_reload_fallback_to_base_reload(self, mock_component):
        """WeaponAbility uses base_reload when reload is explicitly 0."""
        mock_component.data = {
            'damage': 50,
            'range': 500,
            'reload': 0,  # Falsy value triggers fallback
            'base_reload': 1.5,
        }

        ability = WeaponAbility(mock_component, True)

        assert ability.reload_time == 1.5

    def test_init_defaults_when_no_data(self, mock_component):
        """WeaponAbility uses defaults when no data provided."""
        ability = WeaponAbility(mock_component, {})

        assert ability.damage == 0.0
        assert ability.range == 0.0
        assert ability.reload_time == 1.0  # Default reload is 1.0
        assert ability.firing_arc == 360.0  # Default is full arc
        assert ability.facing_angle == 0.0

    def test_init_stores_base_values(self, mock_component, basic_weapon_data):
        """WeaponAbility stores base values for modifier calculations."""
        ability = WeaponAbility(mock_component, basic_weapon_data)

        assert ability._base_damage == 100.0
        assert ability._base_range == 1000.0
        assert ability._base_reload == 2.0
        assert ability._base_firing_arc == 90.0

    def test_init_with_tags(self, mock_component):
        """WeaponAbility captures tags from data."""
        data = {
            'damage': 100,
            'range': 1000,
            'reload': 1.0,
            'tags': ['kinetic', 'heavy'],
        }

        ability = WeaponAbility(mock_component, data)

        assert 'kinetic' in ability.tags
        assert 'heavy' in ability.tags


class TestWeaponAbilityFormulaSupport:
    """Test formula-based damage/range/reload calculation."""

    def test_damage_formula_stored(self, mock_component, formula_weapon_data):
        """Damage formula is stored and base damage calculated at range 0."""
        ability = WeaponAbility(mock_component, formula_weapon_data)

        assert ability.damage_formula == '50 + range_to_target * 0.1'
        assert ability.damage == 50.0  # Evaluated at range 0

    def test_range_formula_evaluated(self, mock_component):
        """Range formula is evaluated during init."""
        data = {
            'damage': 100,
            'range': '=1000 + 500',
            'reload': 1.0,
        }

        ability = WeaponAbility(mock_component, data)

        assert ability.range == 1500.0

    def test_reload_formula_evaluated(self, mock_component):
        """Reload formula is evaluated during init."""
        data = {
            'damage': 100,
            'range': 1000,
            'reload': '=2.0 * 0.5',
        }

        ability = WeaponAbility(mock_component, data)

        assert ability.reload_time == 1.0

    def test_formula_negative_clamped_to_zero(self, mock_component):
        """Negative formula results are clamped to 0."""
        data = {
            'damage': '=-100',
            'range': '=-500',
            'reload': '=-1.0',
        }

        ability = WeaponAbility(mock_component, data)

        assert ability.damage == 0.0
        assert ability.range == 0.0
        assert ability.reload_time == 0.0


class TestWeaponAbilityCooldown:
    """Test cooldown timer behavior."""

    def test_can_fire_when_cooldown_zero(self, mock_component, basic_weapon_data):
        """Weapon can fire when cooldown timer is zero."""
        ability = WeaponAbility(mock_component, basic_weapon_data)

        assert ability.can_fire() is True

    def test_cannot_fire_when_on_cooldown(self, mock_component, basic_weapon_data):
        """Weapon cannot fire when cooldown timer is positive."""
        ability = WeaponAbility(mock_component, basic_weapon_data)
        ability.cooldown_timer = 1.0

        assert ability.can_fire() is False

    def test_update_decrements_cooldown(self, mock_component, basic_weapon_data):
        """Update method decrements cooldown by TICK_RATE."""
        ability = WeaponAbility(mock_component, basic_weapon_data)
        ability.cooldown_timer = 1.0

        ability.update()

        expected = 1.0 - PhysicsConfig.TICK_RATE
        assert ability.cooldown_timer == pytest.approx(expected, rel=1e-6)

    def test_update_does_not_decrement_below_zero(self, mock_component, basic_weapon_data):
        """Cooldown stops decrementing at or below zero."""
        ability = WeaponAbility(mock_component, basic_weapon_data)
        ability.cooldown_timer = 0.005  # Less than TICK_RATE

        ability.update()

        # Should go negative (no clamp in current impl)
        assert ability.cooldown_timer < 0

    def test_update_returns_true(self, mock_component, basic_weapon_data):
        """Update always returns True (operational)."""
        ability = WeaponAbility(mock_component, basic_weapon_data)

        assert ability.update() is True


class TestWeaponAbilityFire:
    """Test fire method behavior."""

    def test_fire_sets_cooldown(self, mock_component, basic_weapon_data):
        """Fire sets cooldown timer to reload_time."""
        ability = WeaponAbility(mock_component, basic_weapon_data)

        result = ability.fire(Mock())

        assert result is True
        assert ability.cooldown_timer == 2.0

    def test_fire_consumes_activation(self, mock_component, basic_weapon_data):
        """Fire calls component.consume_activation."""
        ability = WeaponAbility(mock_component, basic_weapon_data)

        ability.fire(Mock())

        mock_component.consume_activation.assert_called_once()

    def test_fire_fails_when_on_cooldown(self, mock_component, basic_weapon_data):
        """Fire returns False when weapon is on cooldown."""
        ability = WeaponAbility(mock_component, basic_weapon_data)
        ability.cooldown_timer = 1.0

        result = ability.fire(Mock())

        assert result is False
        mock_component.consume_activation.assert_not_called()

    def test_fire_without_component(self, basic_weapon_data):
        """Fire works even if component is None."""
        ability = WeaponAbility(None, basic_weapon_data)

        result = ability.fire(Mock())

        assert result is True
        assert ability.cooldown_timer == 2.0


class TestWeaponAbilityGetDamage:
    """Test get_damage method for static and formula-based damage."""

    def test_get_damage_static(self, mock_component, basic_weapon_data):
        """Static damage returns the damage value regardless of range."""
        ability = WeaponAbility(mock_component, basic_weapon_data)

        assert ability.get_damage(0) == 100.0
        assert ability.get_damage(500) == 100.0
        assert ability.get_damage(1000) == 100.0

    def test_get_damage_formula_varies_with_range(self, mock_component, formula_weapon_data):
        """Formula damage varies with range_to_target."""
        ability = WeaponAbility(mock_component, formula_weapon_data)

        # Formula: 50 + range_to_target * 0.1
        assert ability.get_damage(0) == 50.0
        assert ability.get_damage(100) == 60.0
        assert ability.get_damage(500) == 100.0

    def test_get_damage_formula_clamps_negative(self, mock_component):
        """Formula damage clamps negative results to 0."""
        data = {
            'damage': '=100 - range_to_target',
            'range': 1000,
            'reload': 1.0,
        }
        ability = WeaponAbility(mock_component, data)

        assert ability.get_damage(0) == 100.0
        assert ability.get_damage(100) == 0.0  # 100 - 100 = 0
        assert ability.get_damage(200) == 0.0  # 100 - 200 = -100 -> 0

    def test_get_damage_default_range_is_zero(self, mock_component, formula_weapon_data):
        """get_damage uses 0 as default range."""
        ability = WeaponAbility(mock_component, formula_weapon_data)

        assert ability.get_damage() == ability.get_damage(0)

    def test_get_damage_with_broken_formula_returns_zero(self, mock_component):
        """PROJ-246: Runtime get_damage() with broken formula returns 0, not crash.

        The runtime path uses safe_evaluate so combat doesn't crash mid-tick.
        A broken formula injected at runtime (e.g. corrupted by a mod) should
        degrade gracefully to 0, not crash the battle engine.
        """
        data = {
            'damage': '=range_to_target * 0.1',
            'range': 1000,
            'reload': 1.0,
        }
        ability = WeaponAbility(mock_component, data)

        # Simulate a broken formula being set at runtime
        ability.damage_formula = 'undefined_var + 10'

        # Runtime evaluation with broken formula should return 0 (safe fallback)
        result = ability.get_damage(500)
        assert result == 0.0


class TestWeaponAbilityRecalculate:
    """Test modifier application via recalculate."""

    def test_recalculate_applies_damage_mult(self, mock_component_with_stats, basic_weapon_data):
        """Recalculate applies damage_mult modifier."""
        ability = WeaponAbility(mock_component_with_stats, basic_weapon_data)

        ability.recalculate()

        assert ability.damage == pytest.approx(150.0, rel=1e-6)  # 100 * 1.5

    def test_recalculate_applies_range_mult(self, mock_component_with_stats, basic_weapon_data):
        """Recalculate applies range_mult modifier."""
        ability = WeaponAbility(mock_component_with_stats, basic_weapon_data)

        ability.recalculate()

        assert ability.range == pytest.approx(1200.0, rel=1e-6)  # 1000 * 1.2

    def test_recalculate_applies_reload_mult(self, mock_component_with_stats, basic_weapon_data):
        """Recalculate applies reload_mult modifier."""
        ability = WeaponAbility(mock_component_with_stats, basic_weapon_data)

        ability.recalculate()

        assert ability.reload_time == pytest.approx(1.6, rel=1e-6)  # 2.0 * 0.8

    def test_recalculate_arc_set_overrides(self, mock_component, basic_weapon_data):
        """arc_set stat overrides firing_arc completely."""
        mock_component.stats = {'arc_set': 45.0}
        ability = WeaponAbility(mock_component, basic_weapon_data)

        ability.recalculate()

        assert ability.firing_arc == 45.0

    def test_recalculate_arc_add_modifies(self, mock_component, basic_weapon_data):
        """arc_add stat adds to base firing_arc."""
        mock_component.stats = {'arc_add': 30.0}
        ability = WeaponAbility(mock_component, basic_weapon_data)

        ability.recalculate()

        assert ability.firing_arc == 120.0  # 90 + 30

    def test_recalculate_arc_set_takes_priority_over_add(self, mock_component, basic_weapon_data):
        """arc_set takes priority over arc_add."""
        mock_component.stats = {'arc_set': 45.0, 'arc_add': 30.0}
        ability = WeaponAbility(mock_component, basic_weapon_data)

        ability.recalculate()

        assert ability.firing_arc == 45.0

    def test_recalculate_uses_base_values(self, mock_component, basic_weapon_data):
        """Recalculate always uses base values, not current values."""
        mock_component.stats = {'damage_mult': 2.0}
        ability = WeaponAbility(mock_component, basic_weapon_data)

        ability.recalculate()  # damage = 200
        mock_component.stats = {'damage_mult': 1.5}
        ability.recalculate()  # Should be 150, not 300

        assert ability.damage == pytest.approx(150.0, rel=1e-6)


class TestWeaponAbilitySyncData:
    """Test sync_data method for updating ability state."""

    def test_sync_data_updates_firing_arc(self, mock_component, basic_weapon_data):
        """sync_data updates firing_arc from new data."""
        ability = WeaponAbility(mock_component, basic_weapon_data)

        ability.sync_data({'firing_arc': 180})

        assert ability.firing_arc == 180.0
        assert ability._base_firing_arc == 180.0

    def test_sync_data_updates_facing_angle(self, mock_component, basic_weapon_data):
        """sync_data updates facing_angle from new data."""
        ability = WeaponAbility(mock_component, basic_weapon_data)

        ability.sync_data({'facing_angle': 90})

        assert ability.facing_angle == 90.0

    def test_sync_data_updates_damage(self, mock_component, basic_weapon_data):
        """sync_data updates damage and _base_damage."""
        ability = WeaponAbility(mock_component, basic_weapon_data)

        ability.sync_data({'damage': 200})

        assert ability.damage == 200.0
        assert ability._base_damage == 200.0

    def test_sync_data_handles_formula(self, mock_component, basic_weapon_data):
        """sync_data handles formula strings in data."""
        ability = WeaponAbility(mock_component, basic_weapon_data)

        ability.sync_data({'damage': '=150'})

        assert ability._base_damage == 150.0
        assert ability.damage == 150.0

    def test_sync_data_ignores_non_dict(self, mock_component, basic_weapon_data):
        """sync_data does nothing for non-dict data."""
        ability = WeaponAbility(mock_component, basic_weapon_data)
        original_damage = ability.damage

        ability.sync_data(True)

        assert ability.damage == original_damage


class TestWeaponAbilityFiringSolution:
    """Test check_firing_solution geometry checks."""

    def test_firing_solution_in_range_and_arc(self, mock_component):
        """Target in range and arc returns True."""
        data = {
            'damage': 100,
            'range': 1000,
            'reload': 1.0,
            'firing_arc': 90,
            'facing_angle': 0,
        }
        ability = WeaponAbility(mock_component, data)

        ship_pos = Vector2(0, 0)
        ship_angle = 0  # Facing right
        target_pos = Vector2(500, 0)  # Directly ahead

        assert ability.check_firing_solution(ship_pos, ship_angle, target_pos) is True

    def test_firing_solution_out_of_range(self, mock_component):
        """Target out of range returns False."""
        data = {
            'damage': 100,
            'range': 500,
            'reload': 1.0,
            'firing_arc': 360,
            'facing_angle': 0,
        }
        ability = WeaponAbility(mock_component, data)

        ship_pos = Vector2(0, 0)
        ship_angle = 0
        target_pos = Vector2(600, 0)  # Beyond range

        assert ability.check_firing_solution(ship_pos, ship_angle, target_pos) is False

    def test_firing_solution_outside_arc(self, mock_component):
        """Target outside firing arc returns False."""
        data = {
            'damage': 100,
            'range': 1000,
            'reload': 1.0,
            'firing_arc': 90,  # 45 degrees each side
            'facing_angle': 0,
        }
        ability = WeaponAbility(mock_component, data)

        ship_pos = Vector2(0, 0)
        ship_angle = 0  # Facing right
        target_pos = Vector2(-500, 0)  # Behind the ship

        assert ability.check_firing_solution(ship_pos, ship_angle, target_pos) is False

    def test_firing_solution_full_arc(self, mock_component):
        """Full 360 arc allows targets in any direction."""
        data = {
            'damage': 100,
            'range': 1000,
            'reload': 1.0,
            'firing_arc': 360,
            'facing_angle': 0,
        }
        ability = WeaponAbility(mock_component, data)

        ship_pos = Vector2(0, 0)
        ship_angle = 0

        # Test all directions
        assert ability.check_firing_solution(ship_pos, ship_angle, Vector2(500, 0)) is True
        assert ability.check_firing_solution(ship_pos, ship_angle, Vector2(-500, 0)) is True
        assert ability.check_firing_solution(ship_pos, ship_angle, Vector2(0, 500)) is True
        assert ability.check_firing_solution(ship_pos, ship_angle, Vector2(0, -500)) is True

    def test_firing_solution_respects_facing_angle(self, mock_component):
        """Firing solution accounts for component facing angle."""
        data = {
            'damage': 100,
            'range': 1000,
            'reload': 1.0,
            'firing_arc': 90,
            'facing_angle': 90,  # Component faces 90 degrees from ship
        }
        ability = WeaponAbility(mock_component, data)

        ship_pos = Vector2(0, 0)
        ship_angle = 0  # Ship facing right, but weapon faces up

        # Target above ship (in weapon's arc)
        assert ability.check_firing_solution(ship_pos, ship_angle, Vector2(0, 500)) is True
        # Target to the right (outside weapon's arc)
        assert ability.check_firing_solution(ship_pos, ship_angle, Vector2(500, 0)) is False

    def test_firing_solution_arc_boundary(self, mock_component):
        """Targets at arc boundary are included (with epsilon)."""
        data = {
            'damage': 100,
            'range': 1000,
            'reload': 1.0,
            'firing_arc': 90,  # 45 degrees each side
            'facing_angle': 0,
        }
        ability = WeaponAbility(mock_component, data)

        ship_pos = Vector2(0, 0)
        ship_angle = 0

        # Target at exactly 45 degrees
        angle_rad = math.radians(45)
        target_pos = Vector2(math.cos(angle_rad) * 500, math.sin(angle_rad) * 500)

        assert ability.check_firing_solution(ship_pos, ship_angle, target_pos) is True


class TestWeaponAbilityUIRows:
    """Test UI display methods."""

    def test_get_ui_rows_returns_three_rows(self, mock_component, basic_weapon_data):
        """get_ui_rows returns damage, range, and reload rows."""
        ability = WeaponAbility(mock_component, basic_weapon_data)

        rows = ability.get_ui_rows()

        assert len(rows) == 3
        labels = [r['label'] for r in rows]
        assert 'Damage' in labels
        assert 'Range' in labels
        assert 'Reload' in labels

    def test_get_ui_rows_formatting(self, mock_component, basic_weapon_data):
        """UI rows have proper formatting."""
        ability = WeaponAbility(mock_component, basic_weapon_data)

        rows = ability.get_ui_rows()
        damage_row = next(r for r in rows if r['label'] == 'Damage')
        reload_row = next(r for r in rows if r['label'] == 'Reload')

        assert damage_row['value'] == '100'
        assert reload_row['value'] == '2.0s'

    def test_get_primary_value_returns_damage(self, mock_component, basic_weapon_data):
        """get_primary_value returns damage value."""
        ability = WeaponAbility(mock_component, basic_weapon_data)

        assert ability.get_primary_value() == 100.0


# =============================================================================
# ProjectileWeaponAbility Tests
# =============================================================================

class TestProjectileWeaponAbility:
    """Test ProjectileWeaponAbility-specific behavior."""

    def test_init_with_projectile_speed(self, mock_component):
        """ProjectileWeaponAbility captures projectile_speed from data."""
        data = {
            'damage': 100,
            'range': 1000,
            'reload': 1.0,
            'projectile_speed': 800,
        }

        ability = ProjectileWeaponAbility(mock_component, data)

        assert ability.projectile_speed == 800.0

    def test_init_default_projectile_speed(self, mock_component):
        """ProjectileWeaponAbility uses 500 as default speed."""
        data = {'damage': 100, 'range': 1000, 'reload': 1.0}

        ability = ProjectileWeaponAbility(mock_component, data)

        assert ability.projectile_speed == 500.0

    def test_init_non_dict_uses_component_attribute(self, mock_component):
        """ProjectileWeaponAbility reads from component for non-dict data."""
        mock_component.projectile_speed = 1000
        mock_component.data = {'damage': 50, 'range': 500, 'reload': 1.0}

        ability = ProjectileWeaponAbility(mock_component, True)

        assert ability.projectile_speed == 1000.0

    def test_get_ui_rows_includes_speed(self, mock_component):
        """UI rows include projectile speed."""
        data = {
            'damage': 100,
            'range': 1000,
            'reload': 1.0,
            'projectile_speed': 750,
        }
        ability = ProjectileWeaponAbility(mock_component, data)

        rows = ability.get_ui_rows()

        assert len(rows) == 4
        speed_row = next(r for r in rows if r['label'] == 'Speed')
        assert speed_row['value'] == '750'


# =============================================================================
# BeamWeaponAbility Tests
# =============================================================================

class TestBeamWeaponAbility:
    """Test BeamWeaponAbility-specific behavior."""

    def test_init_with_accuracy_stats(self, mock_component):
        """BeamWeaponAbility captures accuracy_falloff and base_accuracy."""
        data = {
            'damage': 100,
            'range': 2000,
            'reload': 0.5,
            'accuracy_falloff': 0.002,
            'base_accuracy': 0.95,
        }

        ability = BeamWeaponAbility(mock_component, data)

        assert ability.accuracy_falloff == 0.002
        assert ability.base_accuracy == 0.95
        assert ability._base_accuracy == 0.95

    def test_init_default_accuracy_values(self, mock_component):
        """BeamWeaponAbility uses default accuracy values."""
        data = {'damage': 100, 'range': 1000, 'reload': 1.0}

        ability = BeamWeaponAbility(mock_component, data)

        assert ability.accuracy_falloff == 0.001
        assert ability.base_accuracy == 1.0

    def test_get_ui_rows_includes_accuracy(self, mock_component):
        """UI rows include accuracy percentage."""
        data = {
            'damage': 100,
            'range': 1000,
            'reload': 1.0,
            'base_accuracy': 0.85,
        }
        ability = BeamWeaponAbility(mock_component, data)

        rows = ability.get_ui_rows()

        assert len(rows) == 4
        acc_row = next(r for r in rows if r['label'] == 'Accuracy')
        assert acc_row['value'] == '85%'

    def test_recalculate_applies_accuracy_add(self, mock_component):
        """Recalculate applies accuracy_add modifier."""
        mock_component.stats = {'accuracy_add': 0.1}
        data = {
            'damage': 100,
            'range': 1000,
            'reload': 1.0,
            'base_accuracy': 0.8,
        }
        ability = BeamWeaponAbility(mock_component, data)

        ability.recalculate()

        assert ability.base_accuracy == pytest.approx(0.9, rel=1e-6)


class TestBeamWeaponPDCValidTargets:
    """Test BeamWeaponAbility.pdc_valid_targets configuration."""

    def test_default_pdc_valid_targets(self, mock_component):
        """BeamWeaponAbility defaults pdc_valid_targets to ["MISSILE", "FIGHTER"]."""
        data = {'damage': 50, 'range': 500, 'reload': 0.5, 'tags': ['pdc']}
        ability = BeamWeaponAbility(mock_component, data)

        assert ability.pdc_valid_targets == ["MISSILE", "FIGHTER"]

    def test_custom_pdc_valid_targets_from_data(self, mock_component):
        """BeamWeaponAbility reads pdc_valid_targets from JSON data."""
        data = {
            'damage': 50,
            'range': 500,
            'reload': 0.5,
            'tags': ['pdc'],
            'pdc_valid_targets': ['MISSILE'],
        }
        ability = BeamWeaponAbility(mock_component, data)

        assert ability.pdc_valid_targets == ['MISSILE']

    def test_extended_pdc_valid_targets(self, mock_component):
        """BeamWeaponAbility supports extended target lists including DRONE."""
        data = {
            'damage': 50,
            'range': 500,
            'reload': 0.5,
            'tags': ['pdc'],
            'pdc_valid_targets': ['MISSILE', 'FIGHTER', 'DRONE'],
        }
        ability = BeamWeaponAbility(mock_component, data)

        assert ability.pdc_valid_targets == ['MISSILE', 'FIGHTER', 'DRONE']

    def test_non_pdc_beam_still_has_default_pdc_valid_targets(self, mock_component):
        """Non-PDC beam weapons still have pdc_valid_targets (unused but present)."""
        data = {'damage': 100, 'range': 1000, 'reload': 1.0}
        ability = BeamWeaponAbility(mock_component, data)

        assert ability.pdc_valid_targets == ["MISSILE", "FIGHTER"]

    def test_pdc_valid_targets_synced_on_data_change(self, mock_component):
        """pdc_valid_targets is updated when sync_data is called with new data."""
        data = {'damage': 50, 'range': 500, 'reload': 0.5, 'tags': ['pdc']}
        ability = BeamWeaponAbility(mock_component, data)

        assert ability.pdc_valid_targets == ["MISSILE", "FIGHTER"]

        new_data = {
            'damage': 50,
            'range': 500,
            'reload': 0.5,
            'tags': ['pdc'],
            'pdc_valid_targets': ['MISSILE', 'DRONE'],
        }
        ability.sync_data(new_data)

        assert ability.pdc_valid_targets == ['MISSILE', 'DRONE']


class TestBeamWeaponHitChance:
    """Test BeamWeaponAbility hit chance calculation."""

    @pytest.fixture
    def beam_ability(self, mock_component):
        """Create a beam ability for testing."""
        data = {
            'damage': 100,
            'range': 2000,
            'reload': 0.5,
            'accuracy_falloff': 0.001,
            'base_accuracy': 1.0,
        }
        return BeamWeaponAbility(mock_component, data)

    def test_hit_chance_close_range(self, beam_ability):
        """Hit chance at close range is high."""
        chance = beam_ability.calculate_hit_chance(0)

        # At distance 0 with base_accuracy 1.0: sigmoid(1.0) approx 0.73
        assert chance > 0.7

    def test_hit_chance_decreases_with_distance(self, beam_ability):
        """Hit chance decreases as distance increases."""
        close_chance = beam_ability.calculate_hit_chance(100)
        far_chance = beam_ability.calculate_hit_chance(1000)

        assert far_chance < close_chance

    def test_hit_chance_with_attack_bonus(self, beam_ability):
        """Attack score bonus increases hit chance."""
        base_chance = beam_ability.calculate_hit_chance(500)
        bonus_chance = beam_ability.calculate_hit_chance(500, attack_score_bonus=1.0)

        assert bonus_chance > base_chance

    def test_hit_chance_with_defense_penalty(self, beam_ability):
        """Defense score penalty decreases hit chance."""
        base_chance = beam_ability.calculate_hit_chance(500)
        penalty_chance = beam_ability.calculate_hit_chance(500, defense_score_penalty=1.0)

        assert penalty_chance < base_chance

    def test_hit_chance_bounds(self, beam_ability):
        """Hit chance is always between 0 and 1."""
        # Very high score
        high_chance = beam_ability.calculate_hit_chance(0, attack_score_bonus=100)
        assert 0.0 <= high_chance <= 1.0

        # Very low score
        low_chance = beam_ability.calculate_hit_chance(10000, defense_score_penalty=100)
        assert 0.0 <= low_chance <= 1.0

    def test_hit_chance_sigmoid_midpoint(self, mock_component):
        """Net score of 0 gives ~50% hit chance (sigmoid midpoint)."""
        data = {
            'damage': 100,
            'range': 2000,
            'reload': 0.5,
            'accuracy_falloff': 0.001,
            'base_accuracy': 0.0,  # Net score will be 0 at distance 0
        }
        ability = BeamWeaponAbility(mock_component, data)

        chance = ability.calculate_hit_chance(0)

        assert chance == pytest.approx(0.5, rel=0.01)

    def test_hit_chance_overflow_protection(self, beam_ability):
        """Hit chance handles extreme values without overflow."""
        # These extreme values could cause math.exp overflow
        high_chance = beam_ability.calculate_hit_chance(0, attack_score_bonus=50)
        low_chance = beam_ability.calculate_hit_chance(0, defense_score_penalty=50)

        # Should be clamped, not raise OverflowError
        assert high_chance > 0.99
        assert low_chance < 0.01


# =============================================================================
# SeekerWeaponAbility Tests
# =============================================================================

class TestSeekerWeaponAbility:
    """Test SeekerWeaponAbility-specific behavior."""

    @pytest.fixture
    def seeker_data(self):
        """Standard seeker weapon data."""
        return {
            'damage': 0,  # Seeker weapons have projectile_damage
            'reload': 3.0,
            'projectile_speed': 600,
            'endurance': 5.0,
            'turn_rate': 45.0,
            'to_hit_defense': 0.5,
            'projectile_damage': 150,
            'projectile_hp': 10,
            'projectile_stealth': 1.0,
        }

    def test_init_captures_seeker_stats(self, mock_component, seeker_data):
        """SeekerWeaponAbility captures seeker-specific stats."""
        ability = SeekerWeaponAbility(mock_component, seeker_data)

        assert ability.projectile_speed == 600.0
        assert ability.endurance == 5.0
        assert ability.turn_rate == 45.0
        assert ability.to_hit_defense == 0.5
        assert ability.projectile_damage == 150.0
        assert ability.projectile_hp == 10.0
        assert ability.projectile_stealth == 1.0

    def test_init_stores_base_values(self, mock_component, seeker_data):
        """SeekerWeaponAbility stores base values for modifiers."""
        ability = SeekerWeaponAbility(mock_component, seeker_data)

        assert ability._base_endurance == 5.0
        assert ability._base_projectile_damage == 150.0
        assert ability._base_projectile_hp == 10.0
        assert ability._base_projectile_stealth == 1.0

    def test_init_calculates_range_from_endurance(self, mock_component):
        """Range is calculated from speed * endurance * 0.8 if not set."""
        data = {
            'damage': 0,
            'range': 0,  # Not set
            'reload': 3.0,
            'projectile_speed': 1000,
            'endurance': 10.0,
            'projectile_damage': 100,
        }

        ability = SeekerWeaponAbility(mock_component, data)

        # Range = 1000 * 10.0 * 0.8 = 8000
        assert ability.range == 8000
        assert ability._base_range == 8000

    def test_init_explicit_range_not_overridden(self, mock_component):
        """Explicit range is not overridden by calculation."""
        data = {
            'damage': 0,
            'range': 5000,  # Explicitly set
            'reload': 3.0,
            'projectile_speed': 1000,
            'endurance': 10.0,
            'projectile_damage': 100,
        }

        ability = SeekerWeaponAbility(mock_component, data)

        assert ability.range == 5000

    def test_init_projectile_damage_fallback(self, mock_component):
        """projectile_damage falls back to damage if not specified."""
        data = {
            'damage': 200,
            'reload': 3.0,
            'projectile_speed': 500,
            'endurance': 3.0,
        }

        ability = SeekerWeaponAbility(mock_component, data)

        assert ability.projectile_damage == 200.0

    def test_check_firing_solution_ignores_arc(self, mock_component, seeker_data):
        """Seekers ignore firing arc (omni-directional)."""
        seeker_data['range'] = 1000
        seeker_data['firing_arc'] = 90  # Should be ignored
        ability = SeekerWeaponAbility(mock_component, seeker_data)

        ship_pos = Vector2(0, 0)
        ship_angle = 0

        # Target behind ship (would fail arc check for normal weapon)
        target_behind = Vector2(-500, 0)
        assert ability.check_firing_solution(ship_pos, ship_angle, target_behind) is True

        # Target to the side
        target_side = Vector2(0, 500)
        assert ability.check_firing_solution(ship_pos, ship_angle, target_side) is True

    def test_check_firing_solution_respects_range(self, mock_component, seeker_data):
        """Seekers still respect range limits."""
        seeker_data['range'] = 500
        ability = SeekerWeaponAbility(mock_component, seeker_data)

        ship_pos = Vector2(0, 0)
        ship_angle = 0

        # In range
        assert ability.check_firing_solution(ship_pos, ship_angle, Vector2(400, 0)) is True
        # Out of range
        assert ability.check_firing_solution(ship_pos, ship_angle, Vector2(600, 0)) is False

    def test_recalculate_applies_seeker_modifiers(self, mock_component, seeker_data):
        """Recalculate applies seeker-specific stat modifiers."""
        mock_component.stats = {
            'endurance_mult': 1.5,
            'projectile_damage_mult': 2.0,
            'projectile_hp_mult': 1.2,
            'projectile_stealth_level': 0.5,
        }
        ability = SeekerWeaponAbility(mock_component, seeker_data)

        ability.recalculate()

        assert ability.endurance == pytest.approx(7.5, rel=1e-6)  # 5.0 * 1.5
        assert ability.projectile_damage == pytest.approx(300.0, rel=1e-6)  # 150 * 2.0
        assert ability.projectile_hp == pytest.approx(12.0, rel=1e-6)  # 10 * 1.2
        assert ability.projectile_stealth == pytest.approx(1.5, rel=1e-6)  # 1.0 + 0.5


class TestSeekerWeaponStatBindings:
    """Test SeekerWeaponAbility STAT_BINDINGS configuration."""

    def test_stat_bindings_includes_parent(self):
        """SeekerWeaponAbility includes parent stat bindings."""
        from game.simulation.components.abilities.stat_keys import StatKey

        consumed = SeekerWeaponAbility.get_consumed_stats()

        # Parent bindings
        assert StatKey.DAMAGE_MULT in consumed
        assert StatKey.RANGE_MULT in consumed
        assert StatKey.RELOAD_MULT in consumed

    def test_stat_bindings_includes_seeker_specific(self):
        """SeekerWeaponAbility includes seeker-specific bindings."""
        from game.simulation.components.abilities.stat_keys import StatKey

        consumed = SeekerWeaponAbility.get_consumed_stats()

        # Seeker-specific bindings
        assert StatKey.ENDURANCE_MULT in consumed
        assert StatKey.PROJECTILE_DAMAGE_MULT in consumed
        assert StatKey.PROJECTILE_HP_MULT in consumed
        assert StatKey.PROJECTILE_STEALTH_LEVEL in consumed


# =============================================================================
# Edge Cases and Boundary Conditions
# =============================================================================

class TestWeaponAbilityEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_zero_damage(self, mock_component):
        """Weapon with zero damage works correctly."""
        data = {'damage': 0, 'range': 1000, 'reload': 1.0}
        ability = WeaponAbility(mock_component, data)

        assert ability.damage == 0.0
        assert ability.get_damage() == 0.0
        assert ability.get_primary_value() == 0.0

    def test_zero_range(self, mock_component):
        """Weapon with zero range blocks all firing solutions."""
        data = {'damage': 100, 'range': 0, 'reload': 1.0, 'firing_arc': 360}
        ability = WeaponAbility(mock_component, data)

        ship_pos = Vector2(0, 0)
        # Even adjacent target is out of range
        assert ability.check_firing_solution(ship_pos, 0, Vector2(0.1, 0)) is False

    def test_zero_reload_time(self, mock_component):
        """Weapon with zero reload time can fire repeatedly."""
        data = {'damage': 100, 'range': 1000, 'reload': 0}
        ability = WeaponAbility(mock_component, data)

        ability.fire(Mock())
        assert ability.cooldown_timer == 0.0
        assert ability.can_fire() is True

    def test_very_large_values(self, mock_component):
        """Weapon handles very large stat values."""
        data = {
            'damage': 1e10,
            'range': 1e10,
            'reload': 1e10,
        }
        ability = WeaponAbility(mock_component, data)

        assert ability.damage == 1e10
        assert ability.range == 1e10
        assert ability.reload_time == 1e10

    def test_fractional_values(self, mock_component):
        """Weapon handles fractional stat values."""
        data = {
            'damage': 0.5,
            'range': 0.1,
            'reload': 0.001,
        }
        ability = WeaponAbility(mock_component, data)

        assert ability.damage == 0.5
        assert ability.range == 0.1
        assert ability.reload_time == 0.001

    def test_narrow_firing_arc(self, mock_component):
        """Weapon with very narrow arc works correctly."""
        data = {
            'damage': 100,
            'range': 1000,
            'reload': 1.0,
            'firing_arc': 1,  # 0.5 degrees each side
            'facing_angle': 0,
        }
        ability = WeaponAbility(mock_component, data)

        ship_pos = Vector2(0, 0)
        ship_angle = 0

        # Target directly ahead - should hit
        assert ability.check_firing_solution(ship_pos, ship_angle, Vector2(100, 0)) is True
        # Target slightly off - should miss
        assert ability.check_firing_solution(ship_pos, ship_angle, Vector2(100, 10)) is False

    def test_ability_stats_override_component_stats(self, mock_component, basic_weapon_data):
        """Ability-specific stats take priority over component stats."""
        mock_component.stats = {'damage_mult': 1.5}
        mock_component.ability_stats = {'WeaponAbility': {'damage_mult': 2.0}}

        ability = WeaponAbility(mock_component, basic_weapon_data)
        ability.recalculate()

        # Should use ability-specific 2.0, not component 1.5
        assert ability.damage == pytest.approx(200.0, rel=1e-6)
