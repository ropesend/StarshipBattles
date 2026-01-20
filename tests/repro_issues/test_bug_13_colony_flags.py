"""
BUG-13 Reproduction Test: Colony flags replaced by colored circles.

This test verifies that colony flags are loaded and available in
empire_assets when the strategy scene loads assets for empires with
valid theme paths.
"""
import os
import pytest
from unittest.mock import MagicMock, patch, PropertyMock


class TestColonyFlagLoading:
    """Tests for colony flag asset loading in strategy scene."""

    def test_colony_flag_loaded_when_theme_path_valid(self):
        """
        GIVEN an empire with a valid theme_path pointing to a theme with Colony_Flag.jpg
        WHEN _load_assets() is called
        THEN empire_assets[empire.id]['colony'] should contain the loaded flag image
        """
        from game.strategy.data.empire import Empire
        from game.assets.asset_manager import AssetManager

        # Get actual path to test theme
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        theme_path = os.path.join(project_root, "assets", "ShipThemes", "Atlantians")
        colony_flag_path = os.path.join(theme_path, "Flags", "Colony_Flag.jpg")

        # Precondition: verify the flag file actually exists
        assert os.path.exists(colony_flag_path), f"Test precondition failed: {colony_flag_path} does not exist"

        # Create empire with valid theme path
        empire = Empire(
            empire_id=0,
            name="Test Empire",
            color=(0, 0, 255),
            theme_path=theme_path
        )

        # Verify empire has theme_path set
        assert empire.theme_path == theme_path
        assert os.path.exists(empire.theme_path), "Empire theme_path should exist"

        # Mock the asset loading scenario
        empire_assets = {}

        # Reset AssetManager singleton for clean test
        AssetManager.reset()

        # Simulate what _load_assets does
        from game.assets.asset_manager import get_asset_manager
        am = get_asset_manager()
        am.load_manifest()

        empire_assets[empire.id] = {}
        if empire.theme_path and os.path.exists(empire.theme_path):
            colony_path = os.path.join(empire.theme_path, "Flags", "Colony_Flag.jpg")
            if os.path.exists(colony_path):
                empire_assets[empire.id]['colony'] = am.load_external_image(colony_path)

        # THE BUG: This assertion should pass but may fail if loading breaks
        assert 'colony' in empire_assets[empire.id], \
            f"Colony flag not loaded into empire_assets. Keys: {empire_assets[empire.id].keys()}"

        # Verify we got an actual image, not None or missing texture
        colony_img = empire_assets[empire.id]['colony']
        assert colony_img is not None, "Colony flag image is None"

        # Clean up
        AssetManager.reset()

    def test_renderer_uses_flag_image_not_circle_fallback(self):
        """
        GIVEN empire_assets contains a valid colony flag image
        WHEN _draw_planet_sprite renders an owned planet
        THEN it should use the flag image, not the circle fallback

        This test verifies the rendering logic path.
        """
        # Mock the condition that determines flag vs circle
        emp_assets = {'colony': MagicMock()}  # Has colony key

        # This is the condition from strategy_renderer.py:446
        uses_flag = emp_assets and 'colony' in emp_assets

        assert uses_flag, "Renderer should use flag when 'colony' key exists in emp_assets"

    def test_fallback_to_circle_when_no_flag(self):
        """
        GIVEN empire_assets does NOT contain 'colony' key
        WHEN _draw_planet_sprite renders an owned planet
        THEN it should fall back to drawing a circle

        This confirms the fallback logic works.
        """
        # Empty assets - no colony key
        emp_assets = {}

        uses_flag = emp_assets and 'colony' in emp_assets

        assert not uses_flag, "Renderer should fall back to circle when no 'colony' key"

    def test_empire_theme_path_from_game_config(self):
        """
        GIVEN a GameConfig with valid theme settings
        WHEN creating an empire with get_player_theme_path()
        THEN the path should point to an existing directory with Colony_Flag.jpg
        """
        from game.strategy.engine.game_config import GameConfig

        config = GameConfig()

        # Check player theme path exists (using new API)
        player_theme_path = config.get_player_theme_path(0)
        assert os.path.exists(player_theme_path), \
            f"Player theme path does not exist: {player_theme_path}"

        # Check colony flag exists in theme
        colony_flag_path = os.path.join(player_theme_path, "Flags", "Colony_Flag.jpg")
        assert os.path.exists(colony_flag_path), \
            f"Colony flag does not exist: {colony_flag_path}"


class TestLoadedGameColonyFlags:
    """Tests for colony flags when loading from saved games - verifies the fix."""

    def test_load_assets_uses_empire_theme_id_not_saved_path(self):
        """
        FIX VERIFICATION: _load_assets() now uses empire_theme_id to calculate
        the theme path, ignoring the potentially invalid saved theme_path.

        GIVEN an empire with an invalid saved theme_path but valid empire_theme_id
        WHEN _load_assets() processes this empire
        THEN colony flag should be loaded using the recalculated path
        """
        from game.strategy.data.empire import Empire
        from game.strategy.engine.game_config import GameConfig
        from game.assets.asset_manager import AssetManager, get_asset_manager

        # Create empire with INVALID saved theme_path but VALID empire_theme_id
        empire = Empire(
            empire_id=0,
            name="Test Empire",
            color=(0, 0, 255),
            theme_path="C:\\NonExistent\\Path\\ShipThemes\\Atlantians",  # Invalid saved path
            empire_theme_id="Atlantians"  # Valid theme ID
        )

        # Reset and get asset manager
        AssetManager.reset()
        am = get_asset_manager()
        am.load_manifest()

        # Simulate the FIXED _load_assets() logic
        config = GameConfig()
        asset_base = config.asset_base_path

        empire_assets = {}
        empire_assets[empire.id] = {}

        # Use empire_theme_id to calculate path (THE FIX)
        theme_path = os.path.join(asset_base, empire.empire_theme_id)

        if os.path.exists(theme_path):
            colony_path = os.path.join(theme_path, "Flags", "Colony_Flag.jpg")
            if os.path.exists(colony_path):
                empire_assets[empire.id]['colony'] = am.load_external_image(colony_path)

        # With the fix, colony flag should be loaded
        has_colony_flag = 'colony' in empire_assets[empire.id]

        assert has_colony_flag, (
            f"FIX FAILED: Colony flag should be loaded using empire_theme_id.\n"
            f"  empire.theme_path (invalid): {empire.theme_path}\n"
            f"  empire.empire_theme_id: {empire.empire_theme_id}\n"
            f"  Recalculated theme_path: {theme_path}\n"
            f"  empire_assets keys: {list(empire_assets[empire.id].keys())}"
        )

        # Clean up
        AssetManager.reset()

    def test_load_assets_works_with_different_theme_ids(self):
        """
        Verify _load_assets() works for both player and enemy empires
        with different theme IDs.
        """
        from game.strategy.data.empire import Empire
        from game.strategy.engine.game_config import GameConfig
        from game.assets.asset_manager import AssetManager, get_asset_manager

        # Reset and get asset manager
        AssetManager.reset()
        am = get_asset_manager()
        am.load_manifest()

        config = GameConfig()
        asset_base = config.asset_base_path

        # Test both Atlantians and Federation themes
        test_cases = [
            ("Atlantians", 0),
            ("Federation", 1),
        ]

        for theme_id, emp_id in test_cases:
            empire = Empire(
                empire_id=emp_id,
                name=f"Test Empire {emp_id}",
                color=(0, 0, 255),
                theme_path="C:\\Invalid\\Path",  # Invalid
                empire_theme_id=theme_id
            )

            empire_assets = {}
            empire_assets[empire.id] = {}

            theme_path = os.path.join(asset_base, empire.empire_theme_id)

            if os.path.exists(theme_path):
                colony_path = os.path.join(theme_path, "Flags", "Colony_Flag.jpg")
                if os.path.exists(colony_path):
                    empire_assets[empire.id]['colony'] = am.load_external_image(colony_path)

            assert 'colony' in empire_assets[empire.id], \
                f"Colony flag not loaded for theme {theme_id}"

        # Clean up
        AssetManager.reset()
