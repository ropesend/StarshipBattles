"""
Tests for ResearchTreeScene dependency injection (PROJ-132).

Validates that ResearchTreeScene can receive a Camera via DI,
allowing flexibility in camera implementation.

PROJ-147: ResearchTreeScene moved from game/research/ui/ to game/ui/research/
to fix architecture layer violation. The module now correctly lives in the
UI layer and can import Camera directly.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import pygame

from game.core.protocols import ICamera


class TestResearchSceneCameraInjection:
    """Test camera dependency injection for ResearchTreeScene."""

    @pytest.fixture
    def mock_camera(self):
        """Create a mock camera that satisfies ICamera protocol."""
        camera = Mock(spec=['width', 'height', 'zoom', 'target_zoom', 'position',
                           'min_zoom', 'max_zoom', 'world_to_screen', 'screen_to_world',
                           'update', 'update_input'])
        camera.width = 1920
        camera.height = 1080
        camera.zoom = 1.0
        camera.target_zoom = 1.0
        camera.min_zoom = 0.1
        camera.max_zoom = 5.0
        camera.position = pygame.math.Vector2(0, 0)
        camera.world_to_screen = Mock(return_value=pygame.math.Vector2(0, 0))
        camera.screen_to_world = Mock(return_value=pygame.math.Vector2(0, 0))
        camera.update = Mock()
        camera.update_input = Mock()
        return camera

    def test_research_scene_accepts_camera_parameter(self, mock_camera):
        """ResearchTreeScene should accept an optional camera parameter."""
        # Patch pygame_gui to avoid initialization issues
        with patch('game.ui.research.research_scene.pygame_gui'):
            with patch('game.ui.research.research_scene.ResearchControlPanel'):
                with patch('game.ui.research.research_scene.ResearchRenderer'):
                    from game.ui.research.research_scene import ResearchTreeScene

                    # Should be able to create scene with injected camera
                    scene = ResearchTreeScene(
                        screen_width=1920,
                        screen_height=1080,
                        camera=mock_camera
                    )

                    # Scene should use the injected camera
                    assert scene.camera is mock_camera

    def test_research_scene_creates_camera_when_not_provided(self):
        """ResearchTreeScene should create its own camera if none provided."""
        with patch('game.ui.research.research_scene.pygame_gui'):
            with patch('game.ui.research.research_scene.ResearchControlPanel'):
                with patch('game.ui.research.research_scene.ResearchRenderer'):
                    from game.ui.research.research_scene import ResearchTreeScene

                    # When no camera provided, scene should create one
                    scene = ResearchTreeScene(
                        screen_width=1920,
                        screen_height=1080
                    )

                    # Camera should be created
                    assert scene.camera is not None
                    assert hasattr(scene.camera, 'width')
                    assert hasattr(scene.camera, 'height')


class TestResearchSceneModuleLocation:
    """Test that ResearchTreeScene is correctly located in the UI layer."""

    def test_module_in_ui_layer(self):
        """ResearchTreeScene should be in game.ui.research, not game.research.ui."""
        # This import should work
        from game.ui.research.research_scene import ResearchTreeScene

        # Verify the module path
        assert 'game.ui.research' in ResearchTreeScene.__module__

    def test_camera_import_is_direct(self):
        """ResearchTreeScene can now import Camera directly (PROJ-147 fix)."""
        import game.ui.research.research_scene as module

        # Read the source to verify Camera is imported directly
        source = open(module.__file__).read()

        # The module should have a direct import of Camera since it's in the UI layer
        assert 'from game.ui.renderer.camera import Camera' in source, \
            "Camera should be directly imported since module is in UI layer"
