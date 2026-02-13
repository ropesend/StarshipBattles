"""
Tests for ResearchTreeScene dependency injection (PROJ-132).

Validates that ResearchTreeScene can receive a Camera via DI,
eliminating the layer violation where research imports from game.ui.
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
        with patch('game.research.ui.research_scene.pygame_gui'):
            with patch('game.research.ui.research_scene.ResearchControlPanel'):
                with patch('game.research.ui.research_scene.ResearchRenderer'):
                    from game.research.ui.research_scene import ResearchTreeScene

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
        with patch('game.research.ui.research_scene.pygame_gui'):
            with patch('game.research.ui.research_scene.ResearchControlPanel'):
                with patch('game.research.ui.research_scene.ResearchRenderer'):
                    from game.research.ui.research_scene import ResearchTreeScene

                    # When no camera provided, scene should create one
                    scene = ResearchTreeScene(
                        screen_width=1920,
                        screen_height=1080
                    )

                    # Camera should be created
                    assert scene.camera is not None
                    assert hasattr(scene.camera, 'width')
                    assert hasattr(scene.camera, 'height')


class TestResearchSceneNoUIImport:
    """Test that research_scene doesn't import directly from game.ui."""

    def test_no_direct_camera_import(self):
        """ResearchTreeScene should not import Camera from game.ui.renderer."""
        import game.research.ui.research_scene as module

        # Check that Camera is not imported at module level from game.ui
        source = open(module.__file__).read()

        # The fix: Camera should be conditionally imported or not imported at all
        # For backward compatibility, a factory function in game.ui is acceptable
        # but direct "from game.ui.renderer.camera import Camera" is not
        assert 'from game.ui.renderer.camera import Camera' not in source or \
               'TYPE_CHECKING' in source, \
               "Direct Camera import from game.ui.renderer.camera should be removed or guarded by TYPE_CHECKING"
