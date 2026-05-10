"""Contract test for StrategyRenderer public API surface (PROJ-309 sub-phase 3.2).

This test pins the public symbols and methods of game.ui.screens.strategy_renderer
that callers (strategy_screen.py and existing test files) rely on. It guards the
decomposition of strategy_renderer.py into the strategy_render/ subpackage —
the public API must remain stable across the split.
"""
from __future__ import annotations

import inspect


class TestStrategyRendererPublicApi:
    """Pin the public API of game.ui.screens.strategy_renderer."""

    def test_strategy_renderer_class_importable(self) -> None:
        """StrategyRenderer class is importable from the original module path."""
        from game.ui.screens.strategy_renderer import StrategyRenderer

        assert inspect.isclass(StrategyRenderer)

    def test_warp_point_rotation_speed_constant_importable(self) -> None:
        """WARP_POINT_ROTATION_SPEED constant remains importable from the module.

        test_strategy_renderer_animation.py imports this directly.
        """
        from game.ui.screens.strategy_renderer import WARP_POINT_ROTATION_SPEED

        assert isinstance(WARP_POINT_ROTATION_SPEED, (int, float))
        assert WARP_POINT_ROTATION_SPEED > 0

    def test_strategy_renderer_has_init_with_scene_param(self) -> None:
        """StrategyRenderer.__init__ accepts a single positional `scene` argument."""
        from game.ui.screens.strategy_renderer import StrategyRenderer

        sig = inspect.signature(StrategyRenderer.__init__)
        params = list(sig.parameters.values())
        # self + scene
        assert len(params) >= 2
        assert params[1].name == "scene"

    def test_strategy_renderer_has_update_method(self) -> None:
        """StrategyRenderer.update(dt) is the public animation tick API."""
        from game.ui.screens.strategy_renderer import StrategyRenderer

        assert hasattr(StrategyRenderer, "update")
        sig = inspect.signature(StrategyRenderer.update)
        params = list(sig.parameters.values())
        # self + dt
        assert len(params) >= 2
        assert params[1].name == "dt"

    def test_strategy_renderer_has_draw_method(self) -> None:
        """StrategyRenderer.draw(screen) is the public draw API."""
        from game.ui.screens.strategy_renderer import StrategyRenderer

        assert hasattr(StrategyRenderer, "draw")
        sig = inspect.signature(StrategyRenderer.draw)
        params = list(sig.parameters.values())
        assert len(params) >= 2
        assert params[1].name == "screen"

    def test_strategy_renderer_has_draw_processing_overlay_method(self) -> None:
        """StrategyRenderer.draw_processing_overlay(screen) is the public modal API."""
        from game.ui.screens.strategy_renderer import StrategyRenderer

        assert hasattr(StrategyRenderer, "draw_processing_overlay")
        sig = inspect.signature(StrategyRenderer.draw_processing_overlay)
        params = list(sig.parameters.values())
        assert len(params) >= 2
        assert params[1].name == "screen"

    def test_property_accessors_present(self) -> None:
        """The composer keeps property accessors that delegate to scene."""
        from game.ui.screens.strategy_renderer import StrategyRenderer

        for name in (
            "camera",
            "galaxy",
            "systems",
            "empires",
            "hex_size",
            "screen_width",
            "screen_height",
            "SIDEBAR_WIDTH",
            "TOP_BAR_HEIGHT",
            "empire_assets",
        ):
            attr = getattr(StrategyRenderer, name, None)
            assert isinstance(attr, property), (
                f"{name} should be a property on StrategyRenderer"
            )
