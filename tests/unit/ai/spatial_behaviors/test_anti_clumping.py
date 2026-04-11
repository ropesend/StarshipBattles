"""
Unit tests for anti-clumping and visual polish in spatial behaviors.

Phase 8: Ensures ships don't clump together and movements are smooth.
"""

from unittest.mock import MagicMock
from game.core.math import Vector2


def _make_ship(x=0, y=0):
    ship = MagicMock()
    ship.position = Vector2(x, y)
    ship.mass = 1000
    ship.instance_id = f"ship_{x}_{y}"
    return ship


class TestAntiClumping:
    """Tests for anti-clumping logic across spatial behaviors."""

    def test_apply_separation_pushes_close_ships_apart(self):
        """Ships closer than min_separation get pushed apart."""
        from game.ai.spatial_behaviors.base import apply_separation

        positions = [Vector2(100, 100), Vector2(110, 100)]  # 10 apart
        min_sep = 500

        adjusted = apply_separation(positions, min_separation=min_sep)

        dist = (adjusted[0] - adjusted[1]).length()
        assert dist > 10  # pushed further apart than original

    def test_apply_separation_no_change_when_far(self):
        """Ships already far apart are not moved."""
        from game.ai.spatial_behaviors.base import apply_separation

        positions = [Vector2(0, 0), Vector2(5000, 0)]
        min_sep = 500

        adjusted = apply_separation(positions, min_separation=min_sep)

        # Should be unchanged (within floating point)
        assert abs(adjusted[0].x - 0) < 1
        assert abs(adjusted[1].x - 5000) < 1

    def test_apply_separation_handles_single_ship(self):
        """Single ship is returned unchanged."""
        from game.ai.spatial_behaviors.base import apply_separation

        positions = [Vector2(100, 200)]
        adjusted = apply_separation(positions, min_separation=500)

        assert len(adjusted) == 1
        assert adjusted[0].x == 100
        assert adjusted[0].y == 200

    def test_apply_separation_handles_empty(self):
        """Empty list returns empty."""
        from game.ai.spatial_behaviors.base import apply_separation

        adjusted = apply_separation([], min_separation=500)
        assert adjusted == []

    def test_apply_separation_coincident_ships(self):
        """Ships at the exact same position are pushed apart."""
        from game.ai.spatial_behaviors.base import apply_separation

        positions = [Vector2(100, 100), Vector2(100, 100)]
        min_sep = 500

        adjusted = apply_separation(positions, min_separation=min_sep)

        dist = (adjusted[0] - adjusted[1]).length()
        assert dist > 0  # no longer coincident
