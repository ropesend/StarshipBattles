from game.ui.screens.strategy_render.context import hex_radius_to_screen


class TestHexRadiusToScreen:
    def test_non_positive_radius_uses_minimum_visible_radius(self):
        assert hex_radius_to_screen(0, hex_size=10, zoom=1.0) == 3
        assert hex_radius_to_screen(-2, hex_size=10, zoom=1.0) == 3

    def test_tiny_positive_radius_is_clamped_to_minimum_visible_radius(self):
        assert hex_radius_to_screen(0.01, hex_size=10, zoom=1.0) == 3
