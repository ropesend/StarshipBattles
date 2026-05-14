"""Tests for StrategyRenderer warp point rotation animation."""
import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def renderer():
    """Create a StrategyRenderer with mocked dependencies."""
    scene = MagicMock()
    with patch('game.assets.asset_manager.get_default_asset_manager'):
        from game.ui.screens.strategy_renderer import StrategyRenderer
        return StrategyRenderer(scene)


class TestRendererAnimationState:
    """Tests for animation state tracking in StrategyRenderer."""

    def test_update_handles_large_dt(self, renderer):
        """update should handle large delta time values."""
        renderer.update(1.0)
        assert renderer._elapsed_time == pytest.approx(1.0)

    def test_update_handles_zero_dt(self, renderer):
        """update should handle zero delta time."""
        renderer.update(0.0)
        assert renderer._elapsed_time == pytest.approx(0.0)


class TestWarpPointRotationAngle:
    """Tests for rotation angle calculation during rendering."""

    def test_different_warp_points_get_different_offsets(self):
        """Different warp points should produce a wide spread of rotation offsets.

        Production uses `hash(wp) % 360` for visual variety. The hash is
        randomized per process (PYTHONHASHSEED), so any specific pair *can*
        collide mod 360 by chance — testing one pair is fragile (PROJ-295
        hit such a collision on Python 3.13). Test statistically instead:
        across 100 distinct warp points, the offset distribution should be
        wide (not collapsed to a single value).
        """
        from game.strategy.data.star_system import WarpPoint
        from game.core.hex_math import HexCoord

        warp_points = [
            WarpPoint(f"sys{i}", HexCoord(i, 0)) for i in range(100)
        ]
        offsets = {hash(wp) % 360 for wp in warp_points}

        # 100 distinct inputs against 360 buckets: by birthday-paradox, we'd
        # expect ~50+ unique buckets even with a perfect random hash. Anything
        # less than 30 indicates the hash isn't producing variety.
        assert len(offsets) > 30, (
            f"Expected wide rotation-offset distribution across 100 warp "
            f"points; got only {len(offsets)} unique offsets out of 360 "
            f"buckets (offsets: {sorted(offsets)[:10]}...)"
        )

    def test_rotation_offset_is_deterministic(self):
        """Same warp point should always get the same rotation offset."""
        from game.strategy.data.star_system import WarpPoint
        from game.core.hex_math import HexCoord

        wp = WarpPoint("sys1", HexCoord(1, 0))
        offset1 = hash(wp) % 360
        offset2 = hash(wp) % 360
        assert offset1 == offset2

    def test_rotation_angle_increases_with_elapsed_time(self, renderer):
        """Rotation angle should increase as elapsed time increases."""
        from game.ui.screens.strategy_renderer import WARP_POINT_ROTATION_SPEED

        renderer.update(1.0)  # 1 second elapsed
        expected_rotation_component = 1.0 * WARP_POINT_ROTATION_SPEED
        assert expected_rotation_component == pytest.approx(12.0)

        renderer.update(1.0)  # 2 seconds total
        expected_rotation_component = 2.0 * WARP_POINT_ROTATION_SPEED
        assert expected_rotation_component == pytest.approx(24.0)
