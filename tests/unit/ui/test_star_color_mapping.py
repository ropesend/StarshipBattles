"""
Unit tests for star color mapping logic.

PROJ-37 Phase 5: Updated tests for manifest-based implementation.
These tests verify the star color classification logic now delegates to
AssetManager.get_star_color_key() which reads thresholds from the manifest.
"""

import pytest
from unittest.mock import MagicMock, patch


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def mock_asset_manager():
    """Create a mock AssetManager that returns identifiable surfaces."""
    am = MagicMock()

    def load_image_side_effect(category, key):
        """Return a mock surface tagged with the requested key."""
        surface = MagicMock()
        surface.star_color_key = key  # Tag the surface so we can verify which was returned
        return surface

    am.load_image.side_effect = load_image_side_effect

    # Map RGB tuples to expected color keys based on manifest thresholds
    def get_star_color_key_side_effect(color):
        """Simulate manifest-based color lookup."""
        r, g, b = color[0], color[1], color[2]
        # Red: r_min=200 (r > 200), g_max=100 (g < 100)
        if r > 200 and g < 100:
            return 'red'
        # Blue: r_max=100 (r < 100), b_min=200 (b > 200)
        if r < 100 and b > 200:
            return 'blue'
        # White: r_min=200, g_min=200, b_min=200 (all > 200)
        if r > 200 and g > 200 and b > 200:
            return 'white'
        # Orange: r_min=200 (r > 200), g_min=150 (g > 150)
        if r > 200 and g > 150:
            return 'orange'
        return 'yellow'

    am.get_star_color_key.side_effect = get_star_color_key_side_effect

    return am


@pytest.fixture
def star_factory():
    """Factory for creating mock star objects with specific colors."""
    def _create_star(r: int, g: int, b: int):
        """Create a mock star with the given RGB color."""
        star = MagicMock()
        star.color = (r, g, b)
        return star
    return _create_star


# =============================================================================
# Test: Star Color Mapping Logic
# =============================================================================

class TestStarColorMapping:
    """Tests for the star color mapping logic in strategy_scene._get_object_asset.

    The current logic in strategy_scene.py lines 510-520:
    - Default: yellow
    - Red: color[0] > 200 and color[1] < 100
    - Blue: color[2] > 200 and color[0] < 100
    - White: color[0] > 200 and color[1] > 200 and color[2] > 200
    - Orange: color[0] > 200 and color[1] > 150
    """

    def test_red_star_maps_correctly(self, mock_asset_manager, star_factory):
        """RGB (220, 50, 50) should classify as 'red' star."""
        from game.ui.screens.strategy_screen import StrategyScreen

        star = star_factory(220, 50, 50)

        with patch('game.assets.asset_manager.get_asset_manager', return_value=mock_asset_manager):
            with patch('game.ui.screens.strategy_screen.is_star', return_value=True):
                scene = MagicMock(spec=StrategyScreen)
                scene.empire_assets = {}

                # Call the actual method
                result = StrategyScreen._get_object_asset(scene, star)

        # Verify the asset manager was called with 'stars' and 'red'
        mock_asset_manager.load_image.assert_called_once_with('stars', 'red')
        assert result.star_color_key == 'red'

    def test_blue_star_maps_correctly(self, mock_asset_manager, star_factory):
        """RGB (50, 50, 220) should classify as 'blue' star."""
        from game.ui.screens.strategy_screen import StrategyScreen

        star = star_factory(50, 50, 220)

        with patch('game.assets.asset_manager.get_asset_manager', return_value=mock_asset_manager):
            with patch('game.ui.screens.strategy_screen.is_star', return_value=True):
                scene = MagicMock(spec=StrategyScreen)
                scene.empire_assets = {}

                result = StrategyScreen._get_object_asset(scene, star)

        mock_asset_manager.load_image.assert_called_once_with('stars', 'blue')
        assert result.star_color_key == 'blue'

    def test_white_star_maps_correctly(self, mock_asset_manager, star_factory):
        """RGB (220, 220, 220) should classify as 'white' star."""
        from game.ui.screens.strategy_screen import StrategyScreen

        star = star_factory(220, 220, 220)

        with patch('game.assets.asset_manager.get_asset_manager', return_value=mock_asset_manager):
            with patch('game.ui.screens.strategy_screen.is_star', return_value=True):
                scene = MagicMock(spec=StrategyScreen)
                scene.empire_assets = {}

                result = StrategyScreen._get_object_asset(scene, star)

        mock_asset_manager.load_image.assert_called_once_with('stars', 'white')
        assert result.star_color_key == 'white'

    def test_orange_star_maps_correctly(self, mock_asset_manager, star_factory):
        """RGB (220, 160, 50) should classify as 'orange' star."""
        from game.ui.screens.strategy_screen import StrategyScreen

        star = star_factory(220, 160, 50)

        with patch('game.assets.asset_manager.get_asset_manager', return_value=mock_asset_manager):
            with patch('game.ui.screens.strategy_screen.is_star', return_value=True):
                scene = MagicMock(spec=StrategyScreen)
                scene.empire_assets = {}

                result = StrategyScreen._get_object_asset(scene, star)

        mock_asset_manager.load_image.assert_called_once_with('stars', 'orange')
        assert result.star_color_key == 'orange'

    def test_yellow_default_for_unknown(self, mock_asset_manager, star_factory):
        """RGB (150, 150, 50) should fall back to 'yellow' (default)."""
        from game.ui.screens.strategy_screen import StrategyScreen

        # This color doesn't match any specific rule
        star = star_factory(150, 150, 50)

        with patch('game.assets.asset_manager.get_asset_manager', return_value=mock_asset_manager):
            with patch('game.ui.screens.strategy_screen.is_star', return_value=True):
                scene = MagicMock(spec=StrategyScreen)
                scene.empire_assets = {}

                result = StrategyScreen._get_object_asset(scene, star)

        mock_asset_manager.load_image.assert_called_once_with('stars', 'yellow')
        assert result.star_color_key == 'yellow'


class TestStarColorThresholdBoundaries:
    """Tests for edge cases at the threshold boundaries.

    Verifies behavior at and near the magic number thresholds (100, 150, 200).
    """

    def test_threshold_boundary_red_at_limit(self, mock_asset_manager, star_factory):
        """RGB (201, 99, 100) should classify as 'red' (just above/below threshold)."""
        from game.ui.screens.strategy_screen import StrategyScreen

        # Red condition: color[0] > 200 and color[1] < 100
        star = star_factory(201, 99, 100)

        with patch('game.assets.asset_manager.get_asset_manager', return_value=mock_asset_manager):
            with patch('game.ui.screens.strategy_screen.is_star', return_value=True):
                scene = MagicMock(spec=StrategyScreen)
                scene.empire_assets = {}

                result = StrategyScreen._get_object_asset(scene, star)

        mock_asset_manager.load_image.assert_called_once_with('stars', 'red')
        assert result.star_color_key == 'red'

    def test_threshold_boundary_red_fails_below(self, mock_asset_manager, star_factory):
        """RGB (200, 99, 100) should NOT classify as 'red' (at threshold, not above)."""
        from game.ui.screens.strategy_screen import StrategyScreen

        # Red condition: color[0] > 200 (must be greater, not equal)
        star = star_factory(200, 99, 100)

        with patch('game.assets.asset_manager.get_asset_manager', return_value=mock_asset_manager):
            with patch('game.ui.screens.strategy_screen.is_star', return_value=True):
                scene = MagicMock(spec=StrategyScreen)
                scene.empire_assets = {}

                result = StrategyScreen._get_object_asset(scene, star)

        # Should fall through to yellow (default)
        mock_asset_manager.load_image.assert_called_once_with('stars', 'yellow')
        assert result.star_color_key == 'yellow'

    def test_threshold_boundary_blue_at_limit(self, mock_asset_manager, star_factory):
        """RGB (99, 100, 201) should classify as 'blue' (just above/below threshold)."""
        from game.ui.screens.strategy_screen import StrategyScreen

        # Blue condition: color[2] > 200 and color[0] < 100
        star = star_factory(99, 100, 201)

        with patch('game.assets.asset_manager.get_asset_manager', return_value=mock_asset_manager):
            with patch('game.ui.screens.strategy_screen.is_star', return_value=True):
                scene = MagicMock(spec=StrategyScreen)
                scene.empire_assets = {}

                result = StrategyScreen._get_object_asset(scene, star)

        mock_asset_manager.load_image.assert_called_once_with('stars', 'blue')
        assert result.star_color_key == 'blue'

    def test_threshold_boundary_blue_fails_at_red_limit(self, mock_asset_manager, star_factory):
        """RGB (100, 100, 201) should NOT classify as 'blue' (red component at threshold)."""
        from game.ui.screens.strategy_screen import StrategyScreen

        # Blue condition: color[0] < 100 (must be less, not equal)
        star = star_factory(100, 100, 201)

        with patch('game.assets.asset_manager.get_asset_manager', return_value=mock_asset_manager):
            with patch('game.ui.screens.strategy_screen.is_star', return_value=True):
                scene = MagicMock(spec=StrategyScreen)
                scene.empire_assets = {}

                result = StrategyScreen._get_object_asset(scene, star)

        # Should fall through to yellow (default)
        mock_asset_manager.load_image.assert_called_once_with('stars', 'yellow')
        assert result.star_color_key == 'yellow'

    def test_threshold_boundary_orange_at_limit(self, mock_asset_manager, star_factory):
        """RGB (201, 151, 0) should classify as 'orange'."""
        from game.ui.screens.strategy_screen import StrategyScreen

        # Orange condition: color[0] > 200 and color[1] > 150
        star = star_factory(201, 151, 0)

        with patch('game.assets.asset_manager.get_asset_manager', return_value=mock_asset_manager):
            with patch('game.ui.screens.strategy_screen.is_star', return_value=True):
                scene = MagicMock(spec=StrategyScreen)
                scene.empire_assets = {}

                result = StrategyScreen._get_object_asset(scene, star)

        mock_asset_manager.load_image.assert_called_once_with('stars', 'orange')
        assert result.star_color_key == 'orange'

    def test_threshold_boundary_orange_fails_below_green(self, mock_asset_manager, star_factory):
        """RGB (201, 150, 0) should NOT classify as 'orange' (green at threshold)."""
        from game.ui.screens.strategy_screen import StrategyScreen

        # Orange condition: color[1] > 150 (must be greater, not equal)
        star = star_factory(201, 150, 0)

        with patch('game.assets.asset_manager.get_asset_manager', return_value=mock_asset_manager):
            with patch('game.ui.screens.strategy_screen.is_star', return_value=True):
                scene = MagicMock(spec=StrategyScreen)
                scene.empire_assets = {}

                result = StrategyScreen._get_object_asset(scene, star)

        # Should fall through to yellow (default)
        mock_asset_manager.load_image.assert_called_once_with('stars', 'yellow')
        assert result.star_color_key == 'yellow'


class TestStarColorPriorityOrder:
    """Tests verifying the priority/evaluation order of color conditions.

    The current logic checks in this order:
    1. Red (color[0] > 200 and color[1] < 100)
    2. Blue (color[2] > 200 and color[0] < 100)
    3. White (color[0] > 200 and color[1] > 200 and color[2] > 200)
    4. Orange (color[0] > 200 and color[1] > 150)
    5. Yellow (default)

    This means conditions that match multiple rules will use the FIRST match.
    """

    def test_white_not_confused_with_orange(self, mock_asset_manager, star_factory):
        """White star (220, 220, 220) should not be classified as orange.

        White meets orange condition (r>200, g>150) but white is checked first.
        """
        from game.ui.screens.strategy_screen import StrategyScreen

        star = star_factory(220, 220, 220)

        with patch('game.assets.asset_manager.get_asset_manager', return_value=mock_asset_manager):
            with patch('game.ui.screens.strategy_screen.is_star', return_value=True):
                scene = MagicMock(spec=StrategyScreen)
                scene.empire_assets = {}

                result = StrategyScreen._get_object_asset(scene, star)

        # White should be checked before orange
        mock_asset_manager.load_image.assert_called_once_with('stars', 'white')
        assert result.star_color_key == 'white'

    def test_cyan_classifies_as_blue(self, mock_asset_manager, star_factory):
        """Cyan star (50, 220, 220) should classify as blue.

        Blue check: b>200 and r<100. (50, 220, 220) -> b=220>200, r=50<100 -> BLUE
        """
        from game.ui.screens.strategy_screen import StrategyScreen

        # (50, 220, 220): color[2]=220 > 200, color[0]=50 < 100 -> should be BLUE
        star = star_factory(50, 220, 220)

        with patch('game.assets.asset_manager.get_asset_manager', return_value=mock_asset_manager):
            with patch('game.ui.screens.strategy_screen.is_star', return_value=True):
                scene = MagicMock(spec=StrategyScreen)
                scene.empire_assets = {}

                result = StrategyScreen._get_object_asset(scene, star)

        # This actually matches blue: b > 200 and r < 100
        mock_asset_manager.load_image.assert_called_once_with('stars', 'blue')
        assert result.star_color_key == 'blue'

    def test_magenta_classifies_as_red(self, mock_asset_manager, star_factory):
        """Magenta star (220, 50, 220) should classify as red.

        Red check: r>200 AND g<100. (220, 50, 220) -> r=220>200, g=50<100 -> RED
        """
        from game.ui.screens.strategy_screen import StrategyScreen

        # (220, 50, 220): color[0]=220 > 200, color[1]=50 < 100 -> RED
        star = star_factory(220, 50, 220)

        with patch('game.assets.asset_manager.get_asset_manager', return_value=mock_asset_manager):
            with patch('game.ui.screens.strategy_screen.is_star', return_value=True):
                scene = MagicMock(spec=StrategyScreen)
                scene.empire_assets = {}

                result = StrategyScreen._get_object_asset(scene, star)

        # Matches red: r > 200 and g < 100
        mock_asset_manager.load_image.assert_called_once_with('stars', 'red')
        assert result.star_color_key == 'red'

    def test_green_falls_to_yellow(self, mock_asset_manager, star_factory):
        """Pure green star (50, 220, 50) should fall back to yellow.

        - Not red: r=50 not > 200
        - Not blue: b=50 not > 200
        - Not white: not all > 200
        - Not orange: r=50 not > 200
        -> Yellow default
        """
        from game.ui.screens.strategy_screen import StrategyScreen

        star = star_factory(50, 220, 50)

        with patch('game.assets.asset_manager.get_asset_manager', return_value=mock_asset_manager):
            with patch('game.ui.screens.strategy_screen.is_star', return_value=True):
                scene = MagicMock(spec=StrategyScreen)
                scene.empire_assets = {}

                result = StrategyScreen._get_object_asset(scene, star)

        mock_asset_manager.load_image.assert_called_once_with('stars', 'yellow')
        assert result.star_color_key == 'yellow'
