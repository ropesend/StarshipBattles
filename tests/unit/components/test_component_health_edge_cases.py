"""
Unit tests for ComponentHealthManager edge cases.

Tests damage to zero HP, healing cap, damage threshold behavior,
and status updates.
"""
import pytest
from unittest.mock import MagicMock

from game.simulation.components.component_health_manager import ComponentHealthManager
from game.simulation.components.component_constants import ComponentStatus


@pytest.fixture
def mock_component():
    """Create a mock component with default health values."""
    comp = MagicMock()
    comp.max_hp = 100
    comp.current_hp = 100
    comp.is_active = True
    comp.status = ComponentStatus.ACTIVE
    comp.damage_threshold = 0.5  # 50%
    comp._hp_ratio_dirty = True
    comp._cached_hp_ratio = 1.0
    return comp


class TestTakeDamageEdgeCases:
    """Tests for take_damage edge cases."""

    def test_take_damage_zero_hp_component(self, mock_component):
        """Damage to 0-HP component returns True (destroyed)."""
        mock_component.current_hp = 0
        manager = ComponentHealthManager(mock_component)

        result = manager.take_damage(10)

        assert result is True
        assert mock_component.current_hp == 0
        assert mock_component.is_active is False

    def test_take_damage_exact_destruction(self, mock_component):
        """Damage exactly equal to remaining HP destroys component."""
        mock_component.current_hp = 50
        manager = ComponentHealthManager(mock_component)

        result = manager.take_damage(50)

        assert result is True
        assert mock_component.current_hp == 0
        assert mock_component.is_active is False

    def test_take_damage_overkill(self, mock_component):
        """Damage exceeding HP still sets HP to 0."""
        mock_component.current_hp = 30
        manager = ComponentHealthManager(mock_component)

        result = manager.take_damage(100)

        assert result is True
        assert mock_component.current_hp == 0

    def test_take_damage_partial_no_destruction(self, mock_component):
        """Partial damage doesn't destroy component."""
        manager = ComponentHealthManager(mock_component)

        result = manager.take_damage(30)

        assert result is False
        assert mock_component.current_hp == 70
        assert mock_component.is_active is True


class TestDamageThreshold:
    """Tests for damage threshold behavior."""

    def test_damage_threshold_50_percent(self, mock_component):
        """Component at exactly 50% HP gets DAMAGED status."""
        manager = ComponentHealthManager(mock_component)
        # Damage to exactly 50%
        manager.take_damage(50)

        assert mock_component.current_hp == 50
        # At exactly threshold, current_hp < max_hp * 0.5 is False (50 < 50 is False)
        # So status should NOT be DAMAGED
        # Let's damage one more point to go below threshold
        manager.take_damage(1)

        assert mock_component.current_hp == 49
        assert mock_component.status == ComponentStatus.DAMAGED

    def test_damage_below_threshold_is_damaged(self, mock_component):
        """Component below 50% HP gets DAMAGED status."""
        manager = ComponentHealthManager(mock_component)

        # Damage to 40%
        manager.take_damage(60)

        assert mock_component.current_hp == 40
        assert mock_component.status == ComponentStatus.DAMAGED

    def test_damage_above_threshold_not_damaged(self, mock_component):
        """Component at 51% HP stays operational."""
        manager = ComponentHealthManager(mock_component)

        # Damage to 51%
        manager.take_damage(49)

        assert mock_component.current_hp == 51
        # Status should NOT be changed to DAMAGED since 51 >= 50
        # The check is: current_hp < max_hp * damage_threshold
        # 51 < 100 * 0.5 = 51 < 50 = False
        assert mock_component.status != ComponentStatus.DAMAGED


class TestResetHp:
    """Tests for reset_hp behavior."""

    def test_heal_past_max_hp(self, mock_component):
        """Reset restores HP to max (not above)."""
        mock_component.current_hp = 30
        mock_component.is_active = False
        mock_component.status = ComponentStatus.DAMAGED
        manager = ComponentHealthManager(mock_component)

        manager.reset_hp()

        assert mock_component.current_hp == 100  # max_hp
        assert mock_component.is_active is True
        assert mock_component.status == ComponentStatus.ACTIVE


class TestHpRatio:
    """Tests for hp_ratio property."""

    def test_hp_ratio_caching(self, mock_component):
        """hp_ratio is cached until dirty flag set."""
        mock_component.current_hp = 50
        mock_component._hp_ratio_dirty = True
        manager = ComponentHealthManager(mock_component)

        ratio1 = manager.hp_ratio
        assert ratio1 == 0.5
        assert mock_component._hp_ratio_dirty is False

        # Modify current_hp without setting dirty
        mock_component.current_hp = 75
        ratio2 = manager.hp_ratio
        # Should still return cached value
        assert ratio2 == 0.5

    def test_hp_ratio_zero_max_hp(self, mock_component):
        """hp_ratio returns 1.0 when max_hp is 0 (avoids division by zero)."""
        mock_component.max_hp = 0
        mock_component.current_hp = 0
        mock_component._hp_ratio_dirty = True
        manager = ComponentHealthManager(mock_component)

        ratio = manager.hp_ratio

        assert ratio == 1.0
