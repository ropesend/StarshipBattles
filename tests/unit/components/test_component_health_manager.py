"""Tests for ComponentHealthManager."""
import pytest
from unittest.mock import MagicMock


class TestComponentHealthManager:
    """Tests for ComponentHealthManager extracted from Component."""

    @pytest.fixture
    def mock_component(self):
        """Create a mock component for testing."""
        component = MagicMock()
        component.current_hp = 100
        component.max_hp = 100
        component.is_active = True
        component.status = MagicMock()  # ComponentStatus.ACTIVE
        component.damage_threshold = 0.5
        component._hp_ratio_dirty = False
        component._cached_hp_ratio = 1.0
        return component

    # === take_damage tests ===

    def test_take_damage_reduces_current_hp(self, mock_component):
        """Test take_damage reduces current_hp correctly."""
        from game.simulation.components.component_health_manager import ComponentHealthManager

        mgr = ComponentHealthManager(mock_component)

        result = mgr.take_damage(30)

        assert mock_component.current_hp == 70
        assert mock_component._hp_ratio_dirty is True
        assert result is False  # Not destroyed

    def test_take_damage_returns_true_when_destroyed(self, mock_component):
        """Test take_damage returns True when component is destroyed (hp <= 0)."""
        from game.simulation.components.component_health_manager import ComponentHealthManager

        mgr = ComponentHealthManager(mock_component)

        result = mgr.take_damage(150)

        assert mock_component.current_hp == 0
        assert mock_component.is_active is False
        assert result is True  # Destroyed

    def test_take_damage_sets_status_to_damaged_below_threshold(self, mock_component):
        """Test take_damage sets status to DAMAGED below threshold."""
        from game.simulation.components.component_health_manager import ComponentHealthManager
        from game.simulation.components.component_constants import ComponentStatus

        mock_component.damage_threshold = 0.5  # 50% threshold
        mgr = ComponentHealthManager(mock_component)

        # Damage to below 50% but still alive
        mgr.take_damage(60)

        assert mock_component.current_hp == 40
        assert mock_component.status == ComponentStatus.DAMAGED

    def test_take_damage_raises_typeerror_for_non_numeric(self, mock_component):
        """Test take_damage raises TypeError for non-numeric input."""
        from game.simulation.components.component_health_manager import ComponentHealthManager

        mgr = ComponentHealthManager(mock_component)

        with pytest.raises(TypeError, match="amount must be numeric"):
            mgr.take_damage("invalid")

    def test_take_damage_exact_hp_to_zero(self, mock_component):
        """Test take_damage works correctly at exactly 0 HP."""
        from game.simulation.components.component_health_manager import ComponentHealthManager

        mgr = ComponentHealthManager(mock_component)

        result = mgr.take_damage(100)

        assert mock_component.current_hp == 0
        assert mock_component.is_active is False
        assert result is True

    # === reset_hp tests ===

    def test_reset_hp_restores_full_hp(self, mock_component):
        """Test reset_hp restores full HP."""
        from game.simulation.components.component_health_manager import ComponentHealthManager
        from game.simulation.components.component_constants import ComponentStatus

        mock_component.current_hp = 30
        mock_component.is_active = False
        mock_component.status = ComponentStatus.DAMAGED
        mgr = ComponentHealthManager(mock_component)

        mgr.reset_hp()

        assert mock_component.current_hp == 100
        assert mock_component.is_active is True
        assert mock_component.status == ComponentStatus.ACTIVE
        assert mock_component._hp_ratio_dirty is True

    # === hp_ratio tests ===

    def test_hp_ratio_returns_cached_ratio(self, mock_component):
        """Test hp_ratio returns cached ratio when not dirty."""
        from game.simulation.components.component_health_manager import ComponentHealthManager

        mock_component._hp_ratio_dirty = False
        mock_component._cached_hp_ratio = 0.75
        mgr = ComponentHealthManager(mock_component)

        result = mgr.hp_ratio

        assert result == 0.75

    def test_hp_ratio_recalculates_after_damage(self, mock_component):
        """Test hp_ratio recalculates after damage (dirty flag)."""
        from game.simulation.components.component_health_manager import ComponentHealthManager

        mock_component.current_hp = 50
        mock_component.max_hp = 100
        mock_component._hp_ratio_dirty = True
        mock_component._cached_hp_ratio = 1.0  # Stale value
        mgr = ComponentHealthManager(mock_component)

        result = mgr.hp_ratio

        assert result == 0.5
        assert mock_component._cached_hp_ratio == 0.5
        assert mock_component._hp_ratio_dirty is False

    def test_hp_ratio_handles_zero_max_hp(self, mock_component):
        """Test hp_ratio returns 1.0 when max_hp is 0."""
        from game.simulation.components.component_health_manager import ComponentHealthManager

        mock_component.current_hp = 0
        mock_component.max_hp = 0
        mock_component._hp_ratio_dirty = True
        mgr = ComponentHealthManager(mock_component)

        result = mgr.hp_ratio

        assert result == 1.0
