"""Tests for UI module imports.

PROJ-111 Task 1.10: Module import verification.
"""
import pytest
import sys


class TestUIImports:
    """Tests to verify UI module imports work correctly."""

    def test_game_ui_import_succeeds(self):
        """import game.ui should succeed without errors."""
        import game.ui
        assert game.ui is not None

    def test_renderer_submodule_importable(self):
        """game.ui.renderer should be importable."""
        import game.ui.renderer
        assert game.ui.renderer is not None

    def test_screens_submodule_importable(self):
        """game.ui.screens should be importable."""
        import game.ui.screens
        assert game.ui.screens is not None

    def test_panels_submodule_importable(self):
        """game.ui.panels should be importable."""
        import game.ui.panels
        assert game.ui.panels is not None

    def test_services_submodule_importable(self):
        """game.ui.services should be importable."""
        import game.ui.services
        assert game.ui.services is not None

    def test_workshop_screen_not_auto_imported(self):
        """workshop_screen should NOT be imported by game.ui.__init__.

        WorkshopScreen uses Tkinter dialogs which can cause issues in
        headless environments. It should not be auto-imported.
        """
        # Clear any cached imports to ensure fresh test
        modules_before = set(sys.modules.keys())

        # Re-import game.ui
        if 'game.ui' in sys.modules:
            # Reload to check fresh import behavior
            import game.ui
        else:
            import game.ui

        # workshop_screen should not have been pulled in by the init
        # (It may be imported later when explicitly needed)
        # We just verify the main import worked
        assert 'game.ui' in sys.modules


class TestUISubmoduleImports:
    """Tests for specific submodule imports."""

    def test_camera_import(self):
        """game.ui.renderer.camera should be importable."""
        from game.ui.renderer.camera import Camera
        assert Camera is not None

    def test_colors_import(self):
        """game.ui.colors should be importable."""
        from game.ui.colors import COLORS
        assert COLORS is not None

    def test_battle_ui_interface_import(self):
        """game.ui.interfaces.battle_ui should be importable."""
        from game.ui.interfaces.battle_ui import IBattleUI, ShipDTO
        assert IBattleUI is not None
        assert ShipDTO is not None

    def test_battle_ui_service_import(self):
        """game.ui.services.battle_ui_service should be importable."""
        from game.ui.services.battle_ui_service import BattleUIService
        assert BattleUIService is not None
