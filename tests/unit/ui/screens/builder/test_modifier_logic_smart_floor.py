"""Tests for ModifierLogic.calculate_snap_value smart_floor behavior.

Moved from tests/unit/simulation/components/test_size_mount_sub_one.py
to respect layer boundaries: ModifierLogic is UI-layer code.
"""
import pytest
from game.ui.screens.builder.modifier_logic import ModifierLogic


class TestSmartFloorSubOne:
    """Test smart_floor logic allows values below 1.0."""

    def test_snap_down_from_1_to_0_9(self):
        """Decrementing from 1.0 by 0.1 should give 0.9, not clamp at 1.0."""
        result = ModifierLogic.calculate_snap_value(
            current=1.0, step=0.1, direction=-1,
            min_val=0.1, max_val=1024.0, smart_floor=True
        )
        assert result == pytest.approx(0.9, abs=0.01)

    def test_snap_down_from_0_2_to_0_1(self):
        """Decrementing from 0.2 by 0.1 should give 0.1."""
        result = ModifierLogic.calculate_snap_value(
            current=0.2, step=0.1, direction=-1,
            min_val=0.1, max_val=1024.0, smart_floor=True
        )
        assert result == pytest.approx(0.1, abs=0.01)

    def test_snap_down_from_0_1_clamps_at_min(self):
        """Decrementing from 0.1 should clamp at 0.1 (min_val)."""
        result = ModifierLogic.calculate_snap_value(
            current=0.1, step=0.1, direction=-1,
            min_val=0.1, max_val=1024.0, smart_floor=True
        )
        assert result == pytest.approx(0.1, abs=0.01)

    def test_snap_down_by_1_from_1_stays_at_min(self):
        """Decrementing from 1.0 by 1.0 step with smart_floor should clamp at 0.1."""
        result = ModifierLogic.calculate_snap_value(
            current=1.0, step=1.0, direction=-1,
            min_val=0.1, max_val=1024.0, smart_floor=True
        )
        # current (1.0) <= step (1.0) and direction < 0, so smart_floor activates
        assert result >= 0.1
