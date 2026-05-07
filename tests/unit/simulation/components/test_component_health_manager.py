"""
Unit tests for ComponentHealthManager.

Tests health tracking, damage application, repair methods, and edge cases
for the ComponentHealthManager class extracted from Component.

PROJ-118 Phase 2 Task 2.21
"""
import pytest
from unittest.mock import MagicMock

from game.simulation.components.component_health_manager import ComponentHealthManager
from game.simulation.components.component_constants import ComponentStatus
from game.simulation.components.component import create_component


@pytest.fixture
def mock_component():
    """Create a mock component with standard health values."""
    component = MagicMock()
    component.max_hp = 100
    component.current_hp = 100
    component.is_active = True
    component.status = ComponentStatus.ACTIVE
    component.damage_threshold = 0.5
    component._hp_ratio_dirty = True
    component._cached_hp_ratio = 1.0
    return component


@pytest.fixture
def health_manager(mock_component):
    """Create a ComponentHealthManager with a mock component."""
    return ComponentHealthManager(mock_component)


class TestComponentHealthManagerInit:
    """Tests for ComponentHealthManager initialization."""

    def test_init_stores_component_reference(self, mock_component):
        """Manager stores reference to component."""
        manager = ComponentHealthManager(mock_component)
        assert manager._component is mock_component

    def test_uses_slots_for_memory_efficiency(self):
        """Manager uses __slots__ to minimize memory footprint."""
        assert hasattr(ComponentHealthManager, '__slots__')
        assert '_component' in ComponentHealthManager.__slots__


class TestTakeDamage:
    """Tests for take_damage method."""

    def test_reduces_current_hp_by_damage_amount(self, health_manager, mock_component):
        """Damage reduces current_hp by the specified amount."""
        health_manager.take_damage(30)
        assert mock_component.current_hp == 70

    def test_returns_false_when_not_destroyed(self, health_manager):
        """Returns False when component survives damage."""
        result = health_manager.take_damage(30)
        assert result is False

    def test_returns_true_when_destroyed(self, health_manager, mock_component):
        """Returns True when damage destroys component (hp <= 0)."""
        result = health_manager.take_damage(100)
        assert result is True

    def test_marks_hp_ratio_dirty_after_damage(self, health_manager, mock_component):
        """Damage marks the hp_ratio cache as dirty."""
        mock_component._hp_ratio_dirty = False
        health_manager.take_damage(10)
        assert mock_component._hp_ratio_dirty is True

    def test_sets_inactive_when_destroyed(self, health_manager, mock_component):
        """Component becomes inactive when destroyed."""
        health_manager.take_damage(150)
        assert mock_component.is_active is False

    def test_clamps_hp_to_zero_on_destruction(self, health_manager, mock_component):
        """HP is clamped to 0 when destroyed (no negative HP)."""
        health_manager.take_damage(200)
        assert mock_component.current_hp == 0

    def test_sets_damaged_status_below_threshold(self, health_manager, mock_component):
        """Status becomes DAMAGED when HP drops below threshold."""
        # 60 damage leaves 40 HP, which is below 50% (50 HP)
        health_manager.take_damage(60)
        assert mock_component.status == ComponentStatus.DAMAGED

    def test_does_not_change_status_above_threshold(self, health_manager, mock_component):
        """Status unchanged when HP remains above threshold."""
        original_status = mock_component.status
        # 40 damage leaves 60 HP, still above 50%
        health_manager.take_damage(40)
        assert mock_component.status == original_status

    def test_raises_validation_exception_for_string_input(self, health_manager):
        """ValidationException raised for string damage amount."""
        from game.core.exceptions import ValidationException
        with pytest.raises(ValidationException, match="amount must be numeric"):
            health_manager.take_damage("50")

    def test_raises_validation_exception_for_none_input(self, health_manager):
        """ValidationException raised for None damage amount."""
        from game.core.exceptions import ValidationException
        with pytest.raises(ValidationException, match="amount must be numeric"):
            health_manager.take_damage(None)

    def test_raises_validation_exception_for_list_input(self, health_manager):
        """ValidationException raised for list damage amount."""
        from game.core.exceptions import ValidationException
        with pytest.raises(ValidationException, match="amount must be numeric"):
            health_manager.take_damage([10])

    def test_accepts_integer_damage(self, health_manager, mock_component):
        """Integer damage amounts are accepted."""
        result = health_manager.take_damage(25)
        assert mock_component.current_hp == 75
        assert result is False

    def test_accepts_float_damage(self, health_manager, mock_component):
        """Float damage amounts are accepted."""
        result = health_manager.take_damage(25.5)
        assert mock_component.current_hp == 74.5
        assert result is False

    def test_zero_damage_has_no_effect(self, health_manager, mock_component):
        """Zero damage does not change HP but marks ratio dirty."""
        mock_component._hp_ratio_dirty = False
        result = health_manager.take_damage(0)
        assert mock_component.current_hp == 100
        assert result is False
        assert mock_component._hp_ratio_dirty is True

    def test_negative_damage_heals(self, health_manager, mock_component):
        """Negative damage effectively heals (increases HP)."""
        mock_component.current_hp = 50
        health_manager.take_damage(-20)
        assert mock_component.current_hp == 70


class TestTakeDamageEdgeCases:
    """Edge case tests for take_damage."""

    def test_damage_exactly_equal_to_hp_destroys(self, health_manager, mock_component):
        """Damage exactly equal to remaining HP destroys component."""
        result = health_manager.take_damage(100)
        assert result is True
        assert mock_component.current_hp == 0
        assert mock_component.is_active is False

    def test_damage_to_already_zero_hp_component(self, health_manager, mock_component):
        """Damaging already-destroyed component still returns destroyed."""
        mock_component.current_hp = 0
        result = health_manager.take_damage(50)
        assert result is True
        assert mock_component.current_hp == 0

    def test_hp_exactly_at_threshold_not_damaged(self, health_manager, mock_component):
        """HP exactly at threshold (50%) is not marked DAMAGED."""
        # 50 HP is exactly 50% of 100 max HP
        # The condition is current_hp < max_hp * threshold
        # 50 < 50 is False, so status should NOT change
        original_status = mock_component.status
        health_manager.take_damage(50)
        assert mock_component.current_hp == 50
        assert mock_component.status == original_status

    def test_hp_one_below_threshold_is_damaged(self, health_manager, mock_component):
        """HP one point below threshold triggers DAMAGED status."""
        health_manager.take_damage(51)
        assert mock_component.current_hp == 49
        assert mock_component.status == ComponentStatus.DAMAGED

    def test_very_small_damage_amount(self, health_manager, mock_component):
        """Very small damage amounts are handled correctly."""
        health_manager.take_damage(0.001)
        assert mock_component.current_hp == 99.999

    def test_very_large_damage_amount(self, health_manager, mock_component):
        """Very large damage amounts clamp HP to zero."""
        result = health_manager.take_damage(1_000_000)
        assert result is True
        assert mock_component.current_hp == 0

    def test_custom_damage_threshold(self, mock_component):
        """Custom damage threshold is respected."""
        mock_component.damage_threshold = 0.75  # 75% threshold
        manager = ComponentHealthManager(mock_component)

        # 30 damage leaves 70 HP, which is below 75% (75 HP)
        manager.take_damage(30)

        assert mock_component.status == ComponentStatus.DAMAGED


class TestResetHp:
    """Tests for reset_hp method."""

    def test_restores_hp_to_max(self, health_manager, mock_component):
        """reset_hp restores current_hp to max_hp."""
        mock_component.current_hp = 30
        health_manager.reset_hp()
        assert mock_component.current_hp == 100

    def test_sets_active_true(self, health_manager, mock_component):
        """reset_hp sets is_active to True."""
        mock_component.is_active = False
        health_manager.reset_hp()
        assert mock_component.is_active is True

    def test_sets_status_to_active(self, health_manager, mock_component):
        """reset_hp sets status to ACTIVE."""
        mock_component.status = ComponentStatus.DAMAGED
        health_manager.reset_hp()
        assert mock_component.status == ComponentStatus.ACTIVE

    def test_marks_hp_ratio_dirty(self, health_manager, mock_component):
        """reset_hp marks hp_ratio cache as dirty."""
        mock_component._hp_ratio_dirty = False
        health_manager.reset_hp()
        assert mock_component._hp_ratio_dirty is True

    def test_reset_from_zero_hp(self, health_manager, mock_component):
        """reset_hp works on destroyed component (0 HP)."""
        mock_component.current_hp = 0
        mock_component.is_active = False
        health_manager.reset_hp()
        assert mock_component.current_hp == 100
        assert mock_component.is_active is True

    def test_reset_already_full_hp(self, health_manager, mock_component):
        """reset_hp on full HP component has no adverse effects."""
        health_manager.reset_hp()
        assert mock_component.current_hp == 100
        assert mock_component.is_active is True
        assert mock_component.status == ComponentStatus.ACTIVE


class TestHpRatio:
    """Tests for hp_ratio property."""

    def test_returns_cached_value_when_not_dirty(self, health_manager, mock_component):
        """hp_ratio returns cached value when cache is clean."""
        mock_component._hp_ratio_dirty = False
        mock_component._cached_hp_ratio = 0.75

        result = health_manager.hp_ratio

        assert result == 0.75

    def test_recalculates_when_dirty(self, health_manager, mock_component):
        """hp_ratio recalculates when cache is dirty."""
        mock_component.current_hp = 50
        mock_component.max_hp = 100
        mock_component._hp_ratio_dirty = True
        mock_component._cached_hp_ratio = 0.99  # Stale value

        result = health_manager.hp_ratio

        assert result == 0.5

    def test_updates_cached_value_on_recalculation(self, health_manager, mock_component):
        """hp_ratio updates _cached_hp_ratio after recalculation."""
        mock_component.current_hp = 75
        mock_component.max_hp = 100
        mock_component._hp_ratio_dirty = True

        health_manager.hp_ratio

        assert mock_component._cached_hp_ratio == 0.75

    def test_clears_dirty_flag_on_recalculation(self, health_manager, mock_component):
        """hp_ratio clears dirty flag after recalculation."""
        mock_component._hp_ratio_dirty = True

        health_manager.hp_ratio

        assert mock_component._hp_ratio_dirty is False

    def test_returns_one_when_max_hp_is_zero(self, health_manager, mock_component):
        """hp_ratio returns 1.0 when max_hp is 0 (avoids division by zero)."""
        mock_component.max_hp = 0
        mock_component.current_hp = 0
        mock_component._hp_ratio_dirty = True

        result = health_manager.hp_ratio

        assert result == 1.0

    def test_returns_zero_ratio_at_zero_hp(self, health_manager, mock_component):
        """hp_ratio returns 0.0 when current_hp is 0."""
        mock_component.current_hp = 0
        mock_component.max_hp = 100
        mock_component._hp_ratio_dirty = True

        result = health_manager.hp_ratio

        assert result == 0.0

    def test_ratio_with_fractional_hp(self, health_manager, mock_component):
        """hp_ratio correctly calculates fractional HP ratios."""
        mock_component.current_hp = 33.33
        mock_component.max_hp = 100
        mock_component._hp_ratio_dirty = True

        result = health_manager.hp_ratio

        assert result == pytest.approx(0.3333, rel=1e-3)

    def test_caching_prevents_redundant_calculation(self, health_manager, mock_component):
        """Accessing hp_ratio twice without damage uses cached value."""
        mock_component.current_hp = 80
        mock_component.max_hp = 100
        mock_component._hp_ratio_dirty = True

        # First access - calculates
        result1 = health_manager.hp_ratio

        # Manually change current_hp without setting dirty flag
        mock_component.current_hp = 50

        # Second access - should still use cached value
        result2 = health_manager.hp_ratio

        assert result1 == 0.8
        assert result2 == 0.8  # Cached, not 0.5


class TestIntegrationScenarios:
    """Integration-style tests for realistic usage scenarios."""

    def test_damage_then_reset_cycle(self, health_manager, mock_component):
        """Component can be damaged and then reset."""
        # Apply damage
        health_manager.take_damage(80)
        assert mock_component.current_hp == 20
        assert mock_component.status == ComponentStatus.DAMAGED

        # Reset
        health_manager.reset_hp()
        assert mock_component.current_hp == 100
        assert mock_component.status == ComponentStatus.ACTIVE

    def test_multiple_damage_instances(self, health_manager, mock_component):
        """Multiple damage applications accumulate correctly."""
        health_manager.take_damage(20)
        health_manager.take_damage(30)
        health_manager.take_damage(10)

        assert mock_component.current_hp == 40
        assert mock_component.status == ComponentStatus.DAMAGED

    def test_damage_to_destruction_then_reset(self, health_manager, mock_component):
        """Component can be destroyed and then reset."""
        # Destroy
        result = health_manager.take_damage(150)
        assert result is True
        assert mock_component.current_hp == 0
        assert mock_component.is_active is False

        # Reset
        health_manager.reset_hp()
        assert mock_component.current_hp == 100
        assert mock_component.is_active is True

    def test_hp_ratio_updates_after_damage(self, health_manager, mock_component):
        """hp_ratio reflects new value after damage."""
        # Initial ratio
        initial_ratio = health_manager.hp_ratio
        assert initial_ratio == 1.0

        # Apply damage
        health_manager.take_damage(40)

        # Check updated ratio
        new_ratio = health_manager.hp_ratio
        assert new_ratio == 0.6

    def test_hp_ratio_updates_after_reset(self, health_manager, mock_component):
        """hp_ratio returns to 1.0 after reset."""
        # Apply damage
        health_manager.take_damage(70)
        assert health_manager.hp_ratio == 0.3

        # Reset
        health_manager.reset_hp()
        assert health_manager.hp_ratio == 1.0


class TestComponentHealthFacade:
    """Tests for Component health-manager lazy facade methods."""

    def test_component_health_manager_is_lazily_initialized_and_cached(self, fresh_registries):
        railgun = create_component('railgun', registries=fresh_registries)

        assert railgun._health_mgr is None

        manager = railgun.health_manager

        assert isinstance(manager, ComponentHealthManager)
        assert railgun._health_mgr is manager
        assert railgun.health_manager is manager

    def test_component_reset_hp_lazily_initializes_manager(self, fresh_registries):
        railgun = create_component('railgun', registries=fresh_registries)
        railgun.current_hp = 0
        railgun.is_active = False
        railgun.status = ComponentStatus.DAMAGED
        railgun._hp_ratio_dirty = False

        assert railgun._health_mgr is None

        railgun.reset_hp()

        assert isinstance(railgun._health_mgr, ComponentHealthManager)
        assert railgun.current_hp == railgun.max_hp
        assert railgun.is_active is True
        assert railgun.status == ComponentStatus.ACTIVE
        assert railgun._hp_ratio_dirty is True
