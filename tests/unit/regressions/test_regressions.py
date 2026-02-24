import pytest
import pygame
import os
from unittest.mock import patch
from game.simulation.entities import ship as ship
from game.simulation.entities.ship import Ship
from game.simulation.entities.ship_loader import load_vehicle_classes
from game.core.registry import RegistryManager
from game.ui.assets import ShipThemeManager


@pytest.fixture
def pygame_setup():
    """Set up and tear down pygame environment."""
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    pygame.init()
    # Ensure we have a display for image operations if needed (though mostly headless works for surfaces)
    # ship.py might depend on initialized pygame

    yield

    # CRITICAL: Clean up ALL mocks first (prevents mock object pollution)
    patch.stopall()

    pygame.quit()


class TestRegressions:
    def test_ship_classes_update_in_place(self, pygame_setup):
        """
        Regression Test for Builder Dropdown Bug:
        Verify that load_vehicle_classes updates the RegistryManager vehicle_classes dict in-place
        instead of replacing the reference.
        """
        # Store original reference
        original_ref = RegistryManager.instance().vehicle_classes
        original_id = id(original_ref)

        # Call loader (from ship_loader module)
        load_vehicle_classes()

        # Verify reference is identical
        assert id(RegistryManager.instance().vehicle_classes) == original_id, \
            "vehicle_classes reference changed! Imports in other modules will be stale."
        assert RegistryManager.instance().vehicle_classes is original_ref

        # Verify it has content
        assert len(RegistryManager.instance().vehicle_classes) > 0, "vehicle_classes should not be empty"

    def test_theme_fallback_image(self, pygame_setup):
        """
        Regression Test for Crash on Missing Image:
        Verify that getting an image for a non-existent theme or class returns a valid fallback surface.
        """
        manager = ShipThemeManager.instance()
        # Force reload to ensure clean state if needed, but singleton persists.
        # Just use it.

        # 1. Test invalid theme -> Should fallback to Default (Federation) if Escort exists
        img = manager.load_image("NonExistentTheme", "Escort")
        assert isinstance(img, pygame.Surface)
        # If Federation/Escort exists, it won't be 100x100.
        # But we know "NonExistentClass" shouldn't exist in any theme.

        # 2. Test valid theme, invalid class -> Should be fallback 100x100
        img2 = manager.load_image("Federation", "NonExistentClass")
        assert isinstance(img2, pygame.Surface)
        assert img2.get_width() == 100

        # 3. Test invalid theme AND invalid class -> Should be fallback 100x100
        img3 = manager.load_image("NonExistentTheme", "NonExistentClass")
        assert isinstance(img3, pygame.Surface)
        assert img3.get_width() == 100

    def test_ship_theme_persistence(self, pygame_setup, fresh_registries):
        """
        Regression Test for Theme Not Saving:
        Verify theme_id is saved and loaded correctly.
        """
        s = Ship("TestShip", 0, 0, (255, 0, 0), theme_id="Atlantians", registries=fresh_registries)

        data = s.to_dict()
        assert data.get('theme_id') == "Atlantians"

        s2 = Ship.from_dict(data, registries=fresh_registries)
        assert s2.theme_id == "Atlantians"

        # Test Default
        s_def = Ship("DefShip", 0, 0, (255, 0, 0), registries=fresh_registries)  # defaults to Federation
        data_def = s_def.to_dict()
        assert data_def.get('theme_id') == "Federation"
