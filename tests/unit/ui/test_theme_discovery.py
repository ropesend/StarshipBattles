import pytest
from unittest.mock import patch
import pygame
import os
from game.ui.assets import ShipThemeManager

from game.core.constants import ASSET_DIR


class TestNewThemes:

    @pytest.fixture(autouse=True)
    def setup(self):
        # Initialize manager with base path (cwd)
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        pygame.font.init()

        # Ensure display is initialized for convert_alpha
        if not pygame.display.get_surface():
             pygame.display.set_mode((1, 1), pygame.NOFRAME)

        ShipThemeManager.reset()
        manager = ShipThemeManager.instance()

        # Verify resources exist
        klingon_json = os.path.join(ASSET_DIR, "ShipThemes", "Klingons", "theme.json")
        romulan_json = os.path.join(ASSET_DIR, "ShipThemes", "Romulans", "theme.json")

        # Skip test if theme files are missing
        if not os.path.exists(klingon_json) or not os.path.exists(romulan_json):
            pytest.skip("Theme JSON files not found - skipping theme discovery tests")

        manager.initialize()

        # Re-initialize to ensure new files are picked up if manager was already loaded
        # (Though in a fresh process it shouldn't matter, but good for interactive testing)
        manager.themes = {}
        manager.loaded = False

        # Ensure display is initialized for convert_alpha
        if not pygame.display.get_surface():
            pygame.display.set_mode((1, 1), pygame.NOFRAME)

        manager.initialize()
        self.manager = manager

        yield

        # CRITICAL: Clean up ALL mocks first (prevents mock object pollution)
        patch.stopall()

        # Clean up singleton
        ShipThemeManager.reset()

        # NOTE: Do not call pygame.quit() or pygame.display.quit() here - the root
        # conftest manages pygame lifecycle at session scope. Calling quit() here
        # would break subsequent tests with "No video mode set" errors.
        from game.core.registry import RegistryManager
        RegistryManager.instance().clear()

    def test_theme_discovery(self):
        """Verify themes are discovered."""
        themes = self.manager.get_available_themes()
        assert len(themes) > 0, "No themes discovered!"
        assert "Klingons" in themes
        assert "Romulans" in themes

    def test_klingon_theme_loads(self):
        """Verify Klingon theme loads and has images."""
        # Note: JSON key is "Battle Cruiser" with space
        img = self.manager.load_image("Klingons", "Battle Cruiser")
        assert img is not None
        # Verify it's not the fallback (100x100)
        assert img.get_size() != (100, 100), "Should not be fallback image"

    def test_romulan_theme_loads(self):
        """Verify Romulan theme loads and has images."""
        # Note: JSON key is "Battle Cruiser" with space
        img = self.manager.load_image("Romulans", "Battle Cruiser")
        assert img is not None
        # Verify it's not the fallback (100x100)
        assert img.get_size() != (100, 100), "Should not be fallback image"
