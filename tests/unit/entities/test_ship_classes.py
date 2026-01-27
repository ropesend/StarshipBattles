import pytest
from unittest.mock import patch
import pygame
import os
from game.simulation.entities.ship_loader import initialize_ship_data
from game.core.registry import RegistryManager
from game.ui.assets import ShipThemeManager
from tests.fixtures.paths import get_project_root


class TestShipClasses:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        # Initialize with project root
        project_root = str(get_project_root())
        initialize_ship_data(project_root)
        self.theme_manager = ShipThemeManager.instance()
        # Initialize theme manager with project root to load themes
        self.theme_manager.initialize(project_root)

        yield

        # CRITICAL: Clean up ALL mocks first (prevents mock object pollution)
        patch.stopall()

        RegistryManager.instance().clear()
        self.theme_manager.clear()
        if pygame.get_init():
            pygame.quit()

    def test_all_classes_exist(self):
        expected_classes = [
            "Escort", "Frigate", "Destroyer",
            "Light Cruiser", "Cruiser", "Heavy Cruiser",
            "Battle Cruiser", "Battleship", "Dreadnought",
            "Superdreadnaugh", "Monitor"
        ]

        classes = RegistryManager.instance().vehicle_classes
        assert len(classes) >= 11, f"Expected at least 11 classes, found {len(classes)}"

        for cls_name in ["Escort", "Frigate", "Destroyer", "Cruiser", "Battleship", "Dreadnought"]:
            assert cls_name in classes, f"Class '{cls_name}' missing from vehicle_classes"

        # Verify a selection of mass limits in vehicle_classes
        assert classes["Escort"]["max_mass"] == 1000
        assert classes["Frigate"]["max_mass"] == 2000
        assert classes["Monitor"]["max_mass"] == 1024000

    def test_theme_image_loading(self):
        themes = ["Federation", "Atlantians", "Klingons", "Romulans"]
        classes = [
            "Escort", "Frigate", "Destroyer",
            "Light Cruiser", "Cruiser", "Heavy Cruiser",
            "Battle Cruiser", "Battleship", "Dreadnought",
            "Superdreadnaugh", "Monitor"
        ]

        for theme in themes:
            for ship_class in classes:
                # Get image directly
                img = self.theme_manager.get_image(theme, ship_class)

                assert img is not None, f"Failed to load image for {theme} / {ship_class}"
                assert isinstance(img, pygame.Surface)
